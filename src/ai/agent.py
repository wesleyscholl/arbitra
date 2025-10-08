"""
Trading Agent powered by Google Gemini AI.

This module implements the core AI agent for trading analysis using
Google's Gemini API for market analysis and trade recommendations.
"""

import json
import logging
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional

import google.generativeai as genai
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class TradeAction(str, Enum):
    """Possible trade actions."""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class AssetTier(str, Enum):
    """Asset classification tiers."""
    FOUNDATION = "FOUNDATION"  # BTC, ETH, SOL
    GROWTH = "GROWTH"          # Top 20-100 altcoins
    OPPORTUNITY = "OPPORTUNITY" # High-quality memecoins


class AnalysisRequest(BaseModel):
    """Request for AI trading analysis."""
    
    symbol: str = Field(description="Token symbol (e.g., SOL, BTC)")
    current_price: Decimal = Field(description="Current market price")
    market_data: Dict = Field(description="Market data (volume, mcap, etc.)")
    technical_indicators: Optional[Dict] = Field(default=None, description="RSI, MACD, etc.")
    sentiment_data: Optional[Dict] = Field(default=None, description="Social sentiment scores")
    on_chain_data: Optional[Dict] = Field(default=None, description="Blockchain metrics")
    portfolio_context: Optional[Dict] = Field(default=None, description="Current portfolio state")
    tier: AssetTier = Field(default=AssetTier.FOUNDATION, description="Asset tier")


class AnalysisResponse(BaseModel):
    """AI analysis response with trade recommendation."""
    
    action: TradeAction = Field(description="Recommended action")
    confidence: Decimal = Field(ge=0, le=1, description="Confidence score (0-1)")
    entry_price: Optional[Decimal] = Field(default=None, description="Suggested entry price")
    take_profit: Optional[Decimal] = Field(default=None, description="Take profit target")
    stop_loss: Optional[Decimal] = Field(default=None, description="Stop loss level")
    reasoning: str = Field(description="Detailed analysis reasoning")
    risk_factors: List[str] = Field(default_factory=list, description="Identified risks")
    opportunity_factors: List[str] = Field(default_factory=list, description="Opportunity factors")
    time_horizon: str = Field(description="Expected holding period (short/medium/long)")
    

@dataclass
class ModelConfig:
    """Configuration for Gemini models."""
    flash_model: str = "gemini-2.0-flash-exp"  # Fast analysis
    pro_model: str = "gemini-1.5-pro"          # Deep analysis
    temperature: float = 0.3  # Lower temperature for consistent trading decisions
    max_tokens: int = 2048


class TradingAgent:
    """
    AI Trading Agent using Google Gemini.
    
    Uses two models:
    - gemini-2.0-flash-exp: Fast analysis for quick decisions
    - gemini-1.5-pro: Deep analysis for complex market conditions
    """
    
    def __init__(self, api_key: str, config: Optional[ModelConfig] = None):
        """
        Initialize the trading agent.
        
        Args:
            api_key: Google AI API key
            config: Model configuration
        """
        self.config = config or ModelConfig()
        genai.configure(api_key=api_key)
        
        # Initialize models
        self.flash_model = genai.GenerativeModel(self.config.flash_model)
        self.pro_model = genai.GenerativeModel(self.config.pro_model)
        
        logger.info(f"Trading agent initialized with models: {self.config.flash_model}, {self.config.pro_model}")
    
    def analyze_trade(
        self,
        request: AnalysisRequest,
        use_deep_analysis: bool = False
    ) -> AnalysisResponse:
        """
        Analyze market conditions and generate trade recommendation.
        
        Args:
            request: Analysis request with market data
            use_deep_analysis: Use pro model for deeper analysis
            
        Returns:
            Analysis response with recommendation
        """
        try:
            # Build prompt
            prompt = self._build_analysis_prompt(request)
            
            # Choose model based on complexity
            model = self.pro_model if use_deep_analysis else self.flash_model
            
            logger.info(f"Analyzing {request.symbol} with {'pro' if use_deep_analysis else 'flash'} model")
            
            # Generate analysis
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.config.temperature,
                    max_output_tokens=self.config.max_tokens,
                )
            )
            
            # Parse response
            analysis = self._parse_response(response.text)
            
            logger.info(f"Analysis complete: {analysis.action} with {analysis.confidence:.2%} confidence")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing trade: {e}", exc_info=True)
            # Return safe default: HOLD with low confidence
            return AnalysisResponse(
                action=TradeAction.HOLD,
                confidence=Decimal("0.0"),
                reasoning=f"Analysis error: {str(e)}. Defaulting to HOLD for safety.",
                risk_factors=["Analysis failed - insufficient data"],
                opportunity_factors=[],
                time_horizon="unknown"
            )
    
    def _build_analysis_prompt(self, request: AnalysisRequest) -> str:
        """Build the analysis prompt for Gemini."""
        
        prompt = f"""You are an expert crypto trading analyst. Analyze the following market data and provide a trading recommendation.

**Asset:** {request.symbol} ({request.tier.value} tier)
**Current Price:** ${request.current_price}

**Market Data:**
{json.dumps(request.market_data, indent=2)}

**Technical Indicators:**
{json.dumps(request.technical_indicators or {}, indent=2)}

**Sentiment Data:**
{json.dumps(request.sentiment_data or {}, indent=2)}

**On-Chain Data:**
{json.dumps(request.on_chain_data or {}, indent=2)}

**Portfolio Context:**
{json.dumps(request.portfolio_context or {}, indent=2)}

**Risk Management Rules:**
- Foundation tier (BTC/ETH/SOL): Max 5% position, lower risk tolerance
- Growth tier: Max 3% position, medium risk tolerance
- Opportunity tier: Max 1% position, higher risk tolerance but strict safety checks

Provide your analysis in the following JSON format:
{{
    "action": "BUY|SELL|HOLD",
    "confidence": 0.85,
    "entry_price": 100.50,
    "take_profit": 120.00,
    "stop_loss": 95.00,
    "reasoning": "Detailed analysis of why this trade makes sense...",
    "risk_factors": ["Factor 1", "Factor 2"],
    "opportunity_factors": ["Factor 1", "Factor 2"],
    "time_horizon": "short|medium|long"
}}

Consider:
1. Technical indicators and chart patterns
2. Market sentiment and social signals
3. On-chain metrics (volume, liquidity, holder distribution)
4. Risk/reward ratio
5. Current market regime (bull/bear/sideways)
6. Portfolio diversification needs

Be conservative with confidence scores. Only recommend BUY with high confidence when:
- Multiple indicators align
- Risk/reward ratio > 2:1
- Adequate liquidity and volume
- No major red flags in on-chain data

Return ONLY the JSON, no other text.
"""
        return prompt
    
    def _parse_response(self, response_text: str) -> AnalysisResponse:
        """
        Parse Gemini response into structured format.
        
        Args:
            response_text: Raw response from Gemini
            
        Returns:
            Parsed analysis response
        """
        try:
            # Extract JSON from response (handle markdown code blocks)
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            # Parse JSON
            data = json.loads(response_text)
            
            # Convert to AnalysisResponse
            return AnalysisResponse(
                action=TradeAction(data["action"]),
                confidence=Decimal(str(data["confidence"])),
                entry_price=Decimal(str(data.get("entry_price"))) if data.get("entry_price") else None,
                take_profit=Decimal(str(data.get("take_profit"))) if data.get("take_profit") else None,
                stop_loss=Decimal(str(data.get("stop_loss"))) if data.get("stop_loss") else None,
                reasoning=data["reasoning"],
                risk_factors=data.get("risk_factors", []),
                opportunity_factors=data.get("opportunity_factors", []),
                time_horizon=data["time_horizon"]
            )
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error(f"Failed to parse AI response: {e}")
            logger.debug(f"Raw response: {response_text}")
            
            # Return safe default
            return AnalysisResponse(
                action=TradeAction.HOLD,
                confidence=Decimal("0.0"),
                reasoning="Failed to parse AI response. Defaulting to HOLD for safety.",
                risk_factors=["Response parsing failed"],
                opportunity_factors=[],
                time_horizon="unknown"
            )
    
    def batch_analyze(
        self,
        requests: List[AnalysisRequest],
        use_deep_analysis: bool = False
    ) -> List[AnalysisResponse]:
        """
        Analyze multiple assets in batch.
        
        Args:
            requests: List of analysis requests
            use_deep_analysis: Use pro model for all analyses
            
        Returns:
            List of analysis responses
        """
        results = []
        for request in requests:
            try:
                result = self.analyze_trade(request, use_deep_analysis)
                results.append(result)
            except Exception as e:
                logger.error(f"Error analyzing {request.symbol}: {e}")
                # Add safe default for failed analysis
                results.append(AnalysisResponse(
                    action=TradeAction.HOLD,
                    confidence=Decimal("0.0"),
                    reasoning=f"Batch analysis error: {str(e)}",
                    risk_factors=["Analysis failed"],
                    opportunity_factors=[],
                    time_horizon="unknown"
                ))
        
        return results
