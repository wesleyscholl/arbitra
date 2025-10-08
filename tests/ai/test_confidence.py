"""
Tests for confidence scoring and calibration.
"""

import pytest
from decimal import Decimal
from datetime import datetime, timedelta

from src.ai import (
    ConfidenceScorer,
    ConfidenceFactors,
    TradeOutcome
)


class TestConfidenceFactors:
    """Tests for ConfidenceFactors model."""
    
    def test_create_valid_factors(self):
        """Test creating valid confidence factors."""
        factors = ConfidenceFactors(
            technical_score=Decimal("0.80"),
            sentiment_score=Decimal("0.70"),
            liquidity_score=Decimal("0.85"),
            risk_reward_score=Decimal("0.75"),
            historical_accuracy=Decimal("0.65")
        )
        
        assert factors.technical_score == Decimal("0.80")
        assert factors.sentiment_score == Decimal("0.70")
    
    def test_weighted_confidence(self):
        """Test weighted confidence calculation."""
        factors = ConfidenceFactors(
            technical_score=Decimal("0.80"),
            sentiment_score=Decimal("0.70"),
            liquidity_score=Decimal("0.85"),
            risk_reward_score=Decimal("0.75"),
            historical_accuracy=Decimal("0.65")
        )
        
        confidence = factors.weighted_confidence
        
        assert Decimal("0") <= confidence <= Decimal("1")
        assert isinstance(confidence, Decimal)


class TestConfidenceScorer:
    """Tests for the ConfidenceScorer class."""
    
    @pytest.fixture
    def scorer(self):
        """Create a confidence scorer."""
        return ConfidenceScorer()
    
    @pytest.fixture
    def base_factors(self):
        """Create base confidence factors."""
        return ConfidenceFactors(
            technical_score=Decimal("0.80"),
            sentiment_score=Decimal("0.70"),
            liquidity_score=Decimal("0.85"),
            risk_reward_score=Decimal("0.75"),
            historical_accuracy=Decimal("0.70")
        )
    
    def test_scorer_initialization(self, scorer):
        """Test scorer initializes correctly."""
        assert scorer is not None
        assert len(scorer.trade_history) == 0
        assert scorer.calibration_bins == 10
    
    def test_calculate_confidence_basic(self, scorer, base_factors):
        """Test basic confidence calculation."""
        confidence = scorer.calculate_confidence(base_factors, "FOUNDATION")
        
        # Should be a valid confidence score
        assert Decimal("0") <= confidence <= Decimal("1")
        assert isinstance(confidence, Decimal)
    
    def test_calculate_confidence_tier_foundation(self, scorer, base_factors):
        """Test confidence for foundation assets."""
        confidence = scorer.calculate_confidence(base_factors, "FOUNDATION")
        
        # Foundation has no discount
        assert confidence > Decimal("0")
    
    def test_calculate_confidence_tier_growth(self, scorer, base_factors):
        """Test confidence for growth assets."""
        foundation_conf = scorer.calculate_confidence(base_factors, "FOUNDATION")
        growth_conf = scorer.calculate_confidence(base_factors, "GROWTH")
        
        # Growth should be slightly discounted
        assert growth_conf < foundation_conf
    
    def test_calculate_confidence_tier_opportunity(self, scorer, base_factors):
        """Test confidence for opportunity assets."""
        growth_conf = scorer.calculate_confidence(base_factors, "GROWTH")
        opp_conf = scorer.calculate_confidence(base_factors, "OPPORTUNITY")
        
        # Opportunity should be heavily discounted
        assert opp_conf < growth_conf
    
    def test_record_outcome(self, scorer):
        """Test recording trade outcomes."""
        outcome = TradeOutcome(
            predicted_confidence=Decimal("0.80"),
            actual_success=True,
            profit_loss_pct=Decimal("0.05"),
            timestamp=datetime.now()
        )
        
        scorer.record_outcome(outcome.predicted_confidence, outcome.actual_success, outcome.profit_loss_pct)
        
        assert len(scorer.trade_history) == 1
    
    def test_get_calibration_metrics_empty(self, scorer):
        """Test calibration metrics with no history."""
        metrics = scorer.get_calibration_metrics()
        
        # Should return error when insufficient data
        assert "error" in metrics
    
    def test_get_calibration_metrics_with_data(self, scorer):
        """Test calibration metrics with historical data."""
        # Need at least 10 outcomes for metrics
        for i in range(15):
            success = i % 2 == 0
            scorer.record_outcome(
                Decimal("0.80"),
                success,
                Decimal("0.05") if success else Decimal("-0.02")
            )
        
        metrics = scorer.get_calibration_metrics()
        
        assert metrics["total_trades"] == 15
        assert "overall_success_rate" in metrics
        assert "brier_score" in metrics
    
    def test_brier_score_calculation(self, scorer):
        """Test Brier score calculation."""
        # Add enough outcomes (need 10+)
        for i in range(12):
            scorer.record_outcome(
                Decimal("0.8"),
                i % 3 != 0,  # 66% success
                Decimal("0.05") if i % 3 != 0 else Decimal("-0.02")
            )
        
        metrics = scorer.get_calibration_metrics()
        
        # Should have a Brier score
        assert "brier_score" in metrics
        assert 0 <= metrics["brier_score"] <= 1
    
    def test_get_recent_accuracy(self, scorer):
        """Test getting recent accuracy."""
        # Add some recent outcomes
        for i in range(5):
            scorer.record_outcome(Decimal("0.80"), i < 4, Decimal("0.02"))
        
        accuracy = scorer.get_recent_accuracy(days=7)
        
        # Should have 80% accuracy (4 out of 5)
        assert accuracy is not None
        assert accuracy == pytest.approx(Decimal("0.80"), abs=0.01)
    
    def test_get_recent_accuracy_no_history(self, scorer):
        """Test recent accuracy with no history."""
        accuracy = scorer.get_recent_accuracy(days=7)
        
        assert accuracy is None
    
    def test_calibration_with_many_outcomes(self, scorer, base_factors):
        """Test calibration improves with more data."""
        # Record many outcomes
        for i in range(50):
            # Simulate 80% success rate
            success = i % 5 != 0
            scorer.record_outcome(Decimal("0.80"), success, Decimal("0.02") if success else Decimal("-0.01"))
        
        # Calculate confidence should still work
        confidence = scorer.calculate_confidence(base_factors, "FOUNDATION")
        
        assert Decimal("0") <= confidence <= Decimal("1")
        
        # Metrics should show history
        metrics = scorer.get_calibration_metrics()
        assert metrics["total_trades"] == 50
        assert "bins" in metrics
        assert len(metrics["bins"]) > 0
