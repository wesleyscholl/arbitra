"""
Tests for trade memory and pattern matching.
"""

import pytest
from decimal import Decimal
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from src.ai.memory import TradeMemory, TradePattern


class TestTradePattern:
    """Tests for TradePattern model."""
    
    def test_create_valid_pattern(self):
        """Test creating a valid trade pattern."""
        pattern = TradePattern(
            trade_id="test_123",
            symbol="SOL",
            entry_price=Decimal("98.50"),
            action="BUY",
            confidence=Decimal("0.85"),
            reasoning="Test reasoning",
            timestamp=datetime.now()
        )
        
        assert pattern.trade_id == "test_123"
        assert pattern.symbol == "SOL"
        assert pattern.action == "BUY"
    
    def test_pattern_with_outcome(self):
        """Test pattern with trade outcome."""
        pattern = TradePattern(
            trade_id="test_123",
            symbol="BTC",
            entry_price=Decimal("50000.00"),
            exit_price=Decimal("52000.00"),
            profit_loss_pct=Decimal("0.04"),
            success=True,
            action="BUY",
            confidence=Decimal("0.80"),
            reasoning="Strong fundamentals",
            timestamp=datetime.now(),
            max_drawdown=Decimal("0.02"),
            holding_period_hours=48
        )
        
        assert pattern.success is True
        assert pattern.profit_loss_pct == Decimal("0.04")


class TestTradeMemory:
    """Tests for the TradeMemory class."""
    
    @pytest.fixture
    def mock_pinecone(self):
        """Mock Pinecone client."""
        with patch('src.ai.memory.pinecone') as mock:
            # Mock index
            mock_index = MagicMock()
            mock.Index.return_value = mock_index
            mock.list_indexes.return_value = []  # Index doesn't exist yet
            yield mock, mock_index
    
    @pytest.fixture
    def memory(self, mock_pinecone):
        """Create trade memory with mocked Pinecone."""
        mock_client, mock_index = mock_pinecone
        return TradeMemory(
            api_key="test_key",
            environment="test",
            index_name="test-index"
        )
    
    @pytest.fixture
    def sample_pattern(self):
        """Create a sample trade pattern."""
        return TradePattern(
            trade_id="trade_123",
            symbol="SOL",
            entry_price=Decimal("98.50"),
            action="BUY",
            confidence=Decimal("0.85"),
            reasoning="Strong momentum with bullish indicators",
            timestamp=datetime.now(),
            rsi=Decimal("62.5"),
            volume_24h=Decimal("1500000000"),
            market_cap=Decimal("45000000000")
        )
    
    @pytest.fixture
    def sample_embedding(self):
        """Create a sample embedding vector."""
        return [0.1] * 384
    
    def test_memory_initialization(self, memory, mock_pinecone):
        """Test memory initializes correctly."""
        mock_client, mock_index = mock_pinecone
        
        assert memory is not None
        assert memory.index_name == "test-index"
        mock_client.Index.assert_called_once_with("test-index")
        # Should create index if it doesn't exist
        mock_client.create_index.assert_called_once()
    
    def test_store_trade(self, memory, sample_pattern, sample_embedding, mock_pinecone):
        """Test storing a trade in memory."""
        mock_client, mock_index = mock_pinecone
        
        memory.store_trade(
            pattern=sample_pattern,
            embedding=sample_embedding
        )
        
        # Should have called upsert
        mock_index.upsert.assert_called_once()
        
        # Check upsert was called with correct structure
        call_args = mock_index.upsert.call_args
        vectors = call_args[1]["vectors"]
        assert len(vectors) == 1
        assert vectors[0][0] == "trade_123"  # trade_id
        assert len(vectors[0][1]) == 384  # embedding
        assert "symbol" in vectors[0][2]  # metadata
    
    def test_store_trade_converts_decimals(self, memory, sample_pattern, sample_embedding, mock_pinecone):
        """Test that Decimal values are converted to float for storage."""
        mock_client, mock_index = mock_pinecone
        
        memory.store_trade(
            pattern=sample_pattern,
            embedding=sample_embedding
        )
        
        call_args = mock_index.upsert.call_args
        metadata = call_args[1]["vectors"][0][2]
        
        # Decimal fields should be converted to float
        assert isinstance(metadata["entry_price"], float)
        assert isinstance(metadata["confidence"], float)
    
    def test_find_similar_trades(self, memory, sample_embedding, mock_pinecone):
        """Test finding similar trades."""
        mock_client, mock_index = mock_pinecone
        
        # Create mock match object
        mock_match = MagicMock()
        mock_match.metadata = {
            "trade_id": "trade_123",
            "symbol": "SOL",
            "entry_price": 98.50,
            "action": "BUY",
            "confidence": 0.85,
            "reasoning": "Test",
            "timestamp": datetime.now().isoformat()
        }
        
        # Mock query response
        mock_response = MagicMock()
        mock_response.matches = [mock_match]
        mock_index.query.return_value = mock_response
        
        similar = memory.find_similar_trades(
            query_embedding=sample_embedding,
            symbol="SOL",
            limit=5
        )
        
        # Should return list of patterns
        assert isinstance(similar, list)
        assert len(similar) == 1
        assert isinstance(similar[0], TradePattern)
        
        # Check query was called correctly
        mock_index.query.assert_called_once()
        call_args = mock_index.query.call_args[1]
        assert call_args["top_k"] == 5
        assert call_args["vector"] == sample_embedding
    
    def test_find_similar_trades_with_filters(self, memory, sample_embedding, mock_pinecone):
        """Test finding similar trades with filters."""
        mock_client, mock_index = mock_pinecone
        mock_response = MagicMock()
        mock_response.matches = []
        mock_index.query.return_value = mock_response
        
        # Find with symbol and confidence filter
        memory.find_similar_trades(
            query_embedding=sample_embedding,
            symbol="BTC",
            min_confidence=Decimal("0.75"),
            limit=10
        )
        
        # Check filter was applied
        call_args = mock_index.query.call_args[1]
        assert call_args["filter"]["symbol"] == "BTC"
        assert call_args["filter"]["confidence"]["$gte"] == 0.75
    
    def test_find_similar_trades_empty(self, memory, sample_embedding, mock_pinecone):
        """Test finding similar trades with no matches."""
        mock_client, mock_index = mock_pinecone
        mock_response = MagicMock()
        mock_response.matches = []
        mock_index.query.return_value = mock_response
        
        similar = memory.find_similar_trades(
            query_embedding=sample_embedding
        )
        
        assert similar == []
    
    def test_find_similar_trades_handles_errors(self, memory, sample_embedding, mock_pinecone):
        """Test that find_similar_trades handles errors gracefully."""
        mock_client, mock_index = mock_pinecone
        mock_index.query.side_effect = Exception("API Error")
        
        # Should return empty list instead of raising
        similar = memory.find_similar_trades(
            query_embedding=sample_embedding
        )
        
        assert similar == []
    
    def test_update_trade_outcome(self, memory, mock_pinecone):
        """Test updating trade outcome."""
        mock_client, mock_index = mock_pinecone
        
        # Mock fetch to return existing trade
        mock_vector = MagicMock()
        mock_vector.metadata = {"symbol": "SOL", "action": "BUY"}
        mock_vector.values = [0.1] * 384
        
        mock_response = MagicMock()
        mock_response.vectors = {"trade_123": mock_vector}
        mock_index.fetch.return_value = mock_response
        
        memory.update_trade_outcome(
            trade_id="trade_123",
            exit_price=Decimal("105.00"),
            profit_loss_pct=Decimal("0.066"),
            success=True,
            max_drawdown=Decimal("0.02"),
            holding_period_hours=48
        )
        
        # Should fetch the trade
        mock_index.fetch.assert_called_once_with(ids=["trade_123"])
        
        # Should upsert with updated metadata
        mock_index.upsert.assert_called_once()
        call_args = mock_index.upsert.call_args[1]
        updated_metadata = call_args["vectors"][0][2]
        assert updated_metadata["exit_price"] == 105.00
        assert updated_metadata["success"] is True
    
    def test_update_trade_outcome_not_found(self, memory, mock_pinecone):
        """Test updating outcome for non-existent trade."""
        mock_client, mock_index = mock_pinecone
        mock_response = MagicMock()
        mock_response.vectors = {}
        mock_index.fetch.return_value = mock_response
        
        # Should not raise error
        memory.update_trade_outcome(
            trade_id="nonexistent",
            exit_price=Decimal("100.00"),
            profit_loss_pct=Decimal("-0.02"),
            success=False,
            max_drawdown=Decimal("0.05"),
            holding_period_hours=24
        )
        
        # Should not call upsert
        mock_index.upsert.assert_not_called()
    
    def test_get_success_rate_for_pattern(self, memory, sample_embedding, mock_pinecone):
        """Test getting success rate for similar patterns (needs 5+ closed trades)."""
        mock_client, mock_index = mock_pinecone
        
        # Create mock matches with outcomes (need at least 5)
        matches = []
        outcomes = [(True, 0.05), (False, -0.02), (True, 0.03), (True, 0.04), (False, -0.01)]
        for i, (success, pnl) in enumerate(outcomes):
            mock_match = MagicMock()
            mock_match.metadata = {
                "trade_id": f"trade_{i}",
                "symbol": "SOL",
                "entry_price": 98.0,
                "action": "BUY",
                "confidence": 0.85,
                "reasoning": "Test",
                "timestamp": datetime.now().isoformat(),
                "success": success,
                "profit_loss_pct": pnl
            }
            matches.append(mock_match)
        
        mock_response = MagicMock()
        mock_response.matches = matches
        mock_index.query.return_value = mock_response
        
        success_rate = memory.get_success_rate_for_pattern(
            query_embedding=sample_embedding,
            symbol="SOL"
        )
        
        # Should calculate correct success rate (3 out of 5 = 60%)
        assert success_rate == pytest.approx(Decimal("0.60"), abs=0.01)
    
    def test_get_success_rate_insufficient_data(self, memory, sample_embedding, mock_pinecone):
        """Test success rate with insufficient completed trades (< 5)."""
        mock_client, mock_index = mock_pinecone
        
        # Create only 3 matches (less than minimum of 5)
        matches = []
        for i in range(3):
            mock_match = MagicMock()
            mock_match.metadata = {
                "trade_id": f"trade_{i}",
                "symbol": "SOL",
                "entry_price": 98.0,
                "action": "BUY",
                "confidence": 0.85,
                "reasoning": "Test",
                "timestamp": datetime.now().isoformat(),
                "success": True,
                "profit_loss_pct": 0.05
            }
            matches.append(mock_match)
        
        mock_response = MagicMock()
        mock_response.matches = matches
        mock_index.query.return_value = mock_response
        
        success_rate = memory.get_success_rate_for_pattern(
            query_embedding=sample_embedding
        )
        
        # Should return None when insufficient data
        assert success_rate is None
    
    def test_get_stats(self, memory, mock_pinecone):
        """Test getting memory statistics."""
        mock_client, mock_index = mock_pinecone
        
        # Mock index stats
        mock_stats = MagicMock()
        mock_stats.total_vector_count = 150
        mock_index.describe_index_stats.return_value = mock_stats
        
        stats = memory.get_stats()
        
        assert "total_trades" in stats
        assert stats["total_trades"] == 150
    
    def test_clear_memory(self, memory, mock_pinecone):
        """Test clearing all trades from memory."""
        mock_client, mock_index = mock_pinecone
        
        memory.clear_memory()
        
        # Should call delete with delete_all=True on the index
        mock_index.delete.assert_called_once_with(delete_all=True)
