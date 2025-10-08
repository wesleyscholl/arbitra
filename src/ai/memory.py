"""
Trade Memory System using Vector Database.

Stores and retrieves similar past trades for pattern recognition and learning.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional

import pinecone
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class TradePattern(BaseModel):
    """Pattern extracted from a historical trade."""
    
    trade_id: str = Field(description="Unique trade identifier")
    symbol: str = Field(description="Token symbol")
    entry_price: Decimal = Field(description="Entry price")
    exit_price: Optional[Decimal] = Field(default=None, description="Exit price if closed")
    profit_loss_pct: Optional[Decimal] = Field(default=None, description="P/L percentage")
    success: Optional[bool] = Field(default=None, description="Whether trade was successful")
    
    # Market conditions at entry
    rsi: Optional[Decimal] = Field(default=None, description="RSI at entry")
    volume_24h: Optional[Decimal] = Field(default=None, description="24h volume")
    market_cap: Optional[Decimal] = Field(default=None, description="Market cap")
    sentiment_score: Optional[Decimal] = Field(default=None, description="Sentiment score")
    
    # Trade details
    action: str = Field(description="BUY/SELL/HOLD")
    confidence: Decimal = Field(description="AI confidence score")
    reasoning: str = Field(description="Trade reasoning")
    timestamp: datetime = Field(description="When trade was made")
    
    # Outcome metadata
    max_drawdown: Optional[Decimal] = Field(default=None, description="Max drawdown %")
    holding_period_hours: Optional[int] = Field(default=None, description="How long held")


class TradeMemory:
    """
    Vector database for trade pattern storage and retrieval.
    
    Uses Pinecone to store trade embeddings and retrieve similar patterns.
    """
    
    def __init__(
        self,
        api_key: str,
        environment: str = "us-west-2-aws",
        index_name: str = "arbitra-trades"
    ):
        """
        Initialize trade memory system.
        
        Args:
            api_key: Pinecone API key
            environment: Pinecone environment
            index_name: Name of the Pinecone index
        """
        self.index_name = index_name
        
        # Initialize Pinecone
        pinecone.init(api_key=api_key, environment=environment)
        
        # Create index if it doesn't exist
        if index_name not in pinecone.list_indexes():
            logger.info(f"Creating Pinecone index: {index_name}")
            pinecone.create_index(
                name=index_name,
                dimension=384,  # Dimension for text embedding models
                metric="cosine"
            )
        
        self.index = pinecone.Index(index_name)
        logger.info(f"Connected to Pinecone index: {index_name}")
    
    def store_trade(
        self,
        pattern: TradePattern,
        embedding: List[float]
    ):
        """
        Store a trade pattern with its embedding.
        
        Args:
            pattern: Trade pattern to store
            embedding: Vector embedding of the trade (384-dim)
        """
        try:
            # Convert pattern to metadata
            metadata = pattern.model_dump()
            
            # Convert Decimal to float for Pinecone
            for key, value in metadata.items():
                if isinstance(value, Decimal):
                    metadata[key] = float(value)
                elif isinstance(value, datetime):
                    metadata[key] = value.isoformat()
            
            # Upsert to Pinecone
            self.index.upsert(
                vectors=[(pattern.trade_id, embedding, metadata)]
            )
            
            logger.info(f"Stored trade {pattern.trade_id} ({pattern.symbol})")
            
        except Exception as e:
            logger.error(f"Error storing trade: {e}", exc_info=True)
    
    def find_similar_trades(
        self,
        query_embedding: List[float],
        symbol: Optional[str] = None,
        min_confidence: Optional[Decimal] = None,
        limit: int = 10
    ) -> List[TradePattern]:
        """
        Find similar past trades based on embedding similarity.
        
        Args:
            query_embedding: Embedding of current market conditions
            symbol: Filter by symbol (optional)
            min_confidence: Minimum confidence threshold (optional)
            limit: Maximum number of results
            
        Returns:
            List of similar trade patterns
        """
        try:
            # Build filter
            filter_dict = {}
            if symbol:
                filter_dict["symbol"] = symbol
            if min_confidence:
                filter_dict["confidence"] = {"$gte": float(min_confidence)}
            
            # Query Pinecone
            results = self.index.query(
                vector=query_embedding,
                filter=filter_dict if filter_dict else None,
                top_k=limit,
                include_metadata=True
            )
            
            # Convert results to TradePattern objects
            patterns = []
            for match in results.matches:
                try:
                    metadata = match.metadata
                    
                    # Convert timestamp back to datetime
                    if "timestamp" in metadata:
                        metadata["timestamp"] = datetime.fromisoformat(metadata["timestamp"])
                    
                    # Convert numeric fields back to Decimal
                    decimal_fields = ["entry_price", "exit_price", "profit_loss_pct", 
                                     "rsi", "volume_24h", "market_cap", "sentiment_score", 
                                     "confidence", "max_drawdown"]
                    for field in decimal_fields:
                        if field in metadata and metadata[field] is not None:
                            metadata[field] = Decimal(str(metadata[field]))
                    
                    pattern = TradePattern(**metadata)
                    patterns.append(pattern)
                    
                except Exception as e:
                    logger.warning(f"Failed to parse trade pattern: {e}")
                    continue
            
            logger.info(f"Found {len(patterns)} similar trades")
            return patterns
            
        except Exception as e:
            logger.error(f"Error finding similar trades: {e}", exc_info=True)
            return []
    
    def get_success_rate_for_pattern(
        self,
        query_embedding: List[float],
        symbol: Optional[str] = None,
        limit: int = 20
    ) -> Optional[Decimal]:
        """
        Get historical success rate for similar patterns.
        
        Args:
            query_embedding: Embedding of current pattern
            symbol: Filter by symbol (optional)
            limit: Number of similar trades to analyze
            
        Returns:
            Success rate (0-1) or None if insufficient data
        """
        similar_trades = self.find_similar_trades(
            query_embedding=query_embedding,
            symbol=symbol,
            limit=limit
        )
        
        # Filter only closed trades with outcomes
        closed_trades = [t for t in similar_trades if t.success is not None]
        
        if len(closed_trades) < 5:
            logger.warning(f"Insufficient closed trades for pattern analysis: {len(closed_trades)}")
            return None
        
        success_count = sum(1 for t in closed_trades if t.success)
        success_rate = Decimal(success_count) / len(closed_trades)
        
        logger.info(f"Historical success rate for pattern: {success_rate:.2%} ({success_count}/{len(closed_trades)})")
        return success_rate
    
    def update_trade_outcome(
        self,
        trade_id: str,
        exit_price: Decimal,
        profit_loss_pct: Decimal,
        success: bool,
        max_drawdown: Decimal,
        holding_period_hours: int
    ):
        """
        Update a trade with its outcome after closing.
        
        Args:
            trade_id: Trade identifier
            exit_price: Exit price
            profit_loss_pct: Profit/loss percentage
            success: Whether trade was successful
            max_drawdown: Maximum drawdown experienced
            holding_period_hours: How long the trade was held
        """
        try:
            # Fetch the trade
            fetch_response = self.index.fetch(ids=[trade_id])
            
            if trade_id not in fetch_response.vectors:
                logger.error(f"Trade {trade_id} not found in memory")
                return
            
            # Get existing vector and metadata
            vector_data = fetch_response.vectors[trade_id]
            metadata = vector_data.metadata.copy()
            embedding = vector_data.values
            
            # Update with outcome
            metadata.update({
                "exit_price": float(exit_price),
                "profit_loss_pct": float(profit_loss_pct),
                "success": success,
                "max_drawdown": float(max_drawdown),
                "holding_period_hours": holding_period_hours
            })
            
            # Upsert with updated metadata
            self.index.upsert(
                vectors=[(trade_id, embedding, metadata)]
            )
            
            logger.info(f"Updated trade {trade_id} with outcome: {'SUCCESS' if success else 'FAIL'} ({profit_loss_pct:.2%})")
            
        except Exception as e:
            logger.error(f"Error updating trade outcome: {e}", exc_info=True)
    
    def get_stats(self) -> Dict:
        """
        Get statistics about the trade memory.
        
        Returns:
            Dictionary with memory statistics
        """
        try:
            stats = self.index.describe_index_stats()
            return {
                "total_trades": stats.total_vector_count,
                "index_name": self.index_name,
                "dimension": stats.dimension
            }
        except Exception as e:
            logger.error(f"Error getting memory stats: {e}")
            return {"error": str(e)}
    
    def clear_memory(self):
        """Clear all trades from memory (use with caution!)."""
        try:
            self.index.delete(delete_all=True)
            logger.warning("Cleared all trades from memory")
        except Exception as e:
            logger.error(f"Error clearing memory: {e}")


def create_embedding_from_conditions(
    symbol: str,
    rsi: Optional[Decimal] = None,
    volume_24h: Optional[Decimal] = None,
    market_cap: Optional[Decimal] = None,
    sentiment_score: Optional[Decimal] = None,
    reasoning: str = ""
) -> List[float]:
    """
    Create a simple embedding from market conditions.
    
    This is a placeholder - in production you would use a proper
    embedding model like sentence-transformers.
    
    Args:
        symbol: Token symbol
        rsi: RSI value
        volume_24h: 24h volume
        market_cap: Market cap
        sentiment_score: Sentiment score
        reasoning: Trade reasoning text
        
    Returns:
        384-dimensional embedding vector
    """
    # Placeholder: In production, use sentence-transformers or similar
    # For now, create a simple feature vector
    
    features = []
    
    # Normalize and add numeric features
    features.append(float(rsi / 100) if rsi else 0.5)
    features.append(min(float(volume_24h / 1000000), 1.0) if volume_24h else 0.5)
    features.append(min(float(market_cap / 10000000000), 1.0) if market_cap else 0.5)
    features.append(float(sentiment_score) if sentiment_score else 0.5)
    
    # Pad to 384 dimensions
    while len(features) < 384:
        features.append(0.0)
    
    return features[:384]
