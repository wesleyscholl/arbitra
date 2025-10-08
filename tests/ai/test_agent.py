"""
Tests for AI Trading Agent with Google Gemini.
"""

import pytest
from decimal import Decimal
from unittest.mock import Mock, patch

from src.ai import TradingAgent, AnalysisRequest, TradeAction, AssetTier


class TestTradingAgent:
    """Tests for the TradingAgent class."""
    
    @pytest.fixture
    def mock_genai(self):
        """Mock Google Generative AI."""
        with patch('src.ai.agent.genai') as mock:
            yield mock
    
    @pytest.fixture
    def agent(self, mock_genai):
        """Create a trading agent with mocked API."""
        return TradingAgent(api_key="test_key")
    
    @pytest.fixture
    def sample_request(self):
        """Create a sample analysis request."""
        return AnalysisRequest(
            symbol="SOL",
            current_price=Decimal("98.50"),
            market_data={
                "volume_24h": 1500000000,
                "market_cap": 45000000000
            },
            technical_indicators={
                "rsi": 62,
                "macd": 0.45
            },
            tier=AssetTier.FOUNDATION
        )
    
    def test_agent_initialization(self, agent, mock_genai):
        """Test that agent initializes correctly."""
        assert agent is not None
        assert agent.config is not None
        mock_genai.configure.assert_called_once()
    
    def test_build_analysis_prompt(self, agent, sample_request):
        """Test prompt building."""
        prompt = agent._build_analysis_prompt(sample_request)
        
        assert "SOL" in prompt
        assert "98.50" in prompt
        assert "FOUNDATION" in prompt
        assert "JSON" in prompt
    
    def test_parse_valid_response(self, agent):
        """Test parsing a valid JSON response."""
        response_text = """```json
        {
            "action": "BUY",
            "confidence": 0.85,
            "entry_price": 98.50,
            "take_profit": 106.00,
            "stop_loss": 95.00,
            "reasoning": "Strong momentum indicators",
            "risk_factors": ["Market volatility"],
            "opportunity_factors": ["Strong fundamentals"],
            "time_horizon": "medium"
        }
        ```"""
        
        analysis = agent._parse_response(response_text)
        
        assert analysis.action == TradeAction.BUY
        assert analysis.confidence == Decimal("0.85")
        assert analysis.entry_price == Decimal("98.50")
        assert "Strong momentum" in analysis.reasoning
    
    def test_parse_invalid_response_returns_hold(self, agent):
        """Test that invalid response defaults to HOLD."""
        response_text = "Invalid JSON response"
        
        analysis = agent._parse_response(response_text)
        
        assert analysis.action == TradeAction.HOLD
        assert analysis.confidence == Decimal("0.0")
        assert "Failed to parse" in analysis.reasoning
    
    def test_analyze_trade_with_mock(self, agent, sample_request, mock_genai):
        """Test trade analysis with mocked API."""
        # Mock the generate_content response
        mock_response = Mock()
        mock_response.text = """```json
        {
            "action": "BUY",
            "confidence": 0.75,
            "entry_price": 98.50,
            "take_profit": 105.00,
            "stop_loss": 96.00,
            "reasoning": "Test reasoning",
            "risk_factors": ["Test risk"],
            "opportunity_factors": ["Test opportunity"],
            "time_horizon": "short"
        }
        ```"""
        
        agent.flash_model.generate_content = Mock(return_value=mock_response)
        
        # Analyze trade
        analysis = agent.analyze_trade(sample_request)
        
        assert analysis.action == TradeAction.BUY
        assert analysis.confidence == Decimal("0.75")
        agent.flash_model.generate_content.assert_called_once()
    
    def test_analyze_trade_with_deep_analysis(self, agent, sample_request, mock_genai):
        """Test that deep analysis uses pro model."""
        mock_response = Mock()
        mock_response.text = """{"action": "HOLD", "confidence": 0.5, "reasoning": "Test", "risk_factors": [], "opportunity_factors": [], "time_horizon": "medium"}"""
        
        agent.pro_model.generate_content = Mock(return_value=mock_response)
        
        # Analyze with deep analysis
        analysis = agent.analyze_trade(sample_request, use_deep_analysis=True)
        
        # Verify pro model was used
        agent.pro_model.generate_content.assert_called_once()
    
    def test_analyze_trade_error_handling(self, agent, sample_request, mock_genai):
        """Test error handling in trade analysis."""
        # Mock an error
        agent.flash_model.generate_content = Mock(side_effect=Exception("API Error"))
        
        # Should return safe default (HOLD)
        analysis = agent.analyze_trade(sample_request)
        
        assert analysis.action == TradeAction.HOLD
        assert analysis.confidence == Decimal("0.0")
        assert "error" in analysis.reasoning.lower()
    
    def test_batch_analyze(self, agent, sample_request, mock_genai):
        """Test batch analysis."""
        mock_response = Mock()
        mock_response.text = """{"action": "HOLD", "confidence": 0.5, "reasoning": "Test", "risk_factors": [], "opportunity_factors": [], "time_horizon": "medium"}"""
        agent.flash_model.generate_content = Mock(return_value=mock_response)
        
        # Create multiple requests
        requests = [sample_request, sample_request, sample_request]
        
        # Batch analyze
        results = agent.batch_analyze(requests)
        
        assert len(results) == 3
        assert all(r.action == TradeAction.HOLD for r in results)
