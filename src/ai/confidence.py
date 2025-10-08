"""
Confidence Scoring System for Trade Recommendations.

Calibrates and tracks the accuracy of AI confidence scores over time.
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ConfidenceFactors(BaseModel):
    """Factors contributing to confidence score."""
    
    technical_score: Decimal = Field(ge=0, le=1, description="Technical indicator alignment")
    sentiment_score: Decimal = Field(ge=0, le=1, description="Market sentiment strength")
    liquidity_score: Decimal = Field(ge=0, le=1, description="Liquidity adequacy")
    risk_reward_score: Decimal = Field(ge=0, le=1, description="Risk/reward ratio quality")
    historical_accuracy: Decimal = Field(ge=0, le=1, description="Past accuracy for similar trades")
    
    @property
    def weighted_confidence(self) -> Decimal:
        """Calculate weighted confidence from factors."""
        weights = {
            "technical": Decimal("0.25"),
            "sentiment": Decimal("0.15"),
            "liquidity": Decimal("0.20"),
            "risk_reward": Decimal("0.25"),
            "historical": Decimal("0.15"),
        }
        
        confidence = (
            self.technical_score * weights["technical"] +
            self.sentiment_score * weights["sentiment"] +
            self.liquidity_score * weights["liquidity"] +
            self.risk_reward_score * weights["risk_reward"] +
            self.historical_accuracy * weights["historical"]
        )
        
        return min(confidence, Decimal("1.0"))


@dataclass
class TradeOutcome:
    """Outcome of a trade for confidence calibration."""
    predicted_confidence: Decimal
    actual_success: bool
    profit_loss_pct: Decimal
    timestamp: datetime


class ConfidenceScorer:
    """
    Confidence scoring and calibration system.
    
    Tracks the accuracy of confidence scores over time and adjusts
    scoring based on historical performance.
    """
    
    def __init__(self):
        """Initialize confidence scorer."""
        self.trade_history: List[TradeOutcome] = []
        self.calibration_bins = 10  # Divide confidence into 10 bins
        self.min_samples_for_calibration = 20
        
    def calculate_confidence(
        self,
        factors: ConfidenceFactors,
        asset_tier: str
    ) -> Decimal:
        """
        Calculate calibrated confidence score.
        
        Args:
            factors: Contributing confidence factors
            asset_tier: Asset tier (FOUNDATION/GROWTH/OPPORTUNITY)
            
        Returns:
            Calibrated confidence score
        """
        # Get base confidence from factors
        base_confidence = factors.weighted_confidence
        
        # Apply tier-specific adjustments
        tier_adjustment = self._get_tier_adjustment(asset_tier)
        adjusted_confidence = base_confidence * tier_adjustment
        
        # Apply calibration based on historical accuracy
        calibrated_confidence = self._apply_calibration(adjusted_confidence)
        
        # Ensure within bounds
        return max(Decimal("0.0"), min(calibrated_confidence, Decimal("1.0")))
    
    def _get_tier_adjustment(self, asset_tier: str) -> Decimal:
        """
        Get confidence adjustment based on asset tier.
        
        Higher risk tiers get lower confidence adjustments.
        """
        adjustments = {
            "FOUNDATION": Decimal("1.0"),    # No adjustment for BTC/ETH/SOL
            "GROWTH": Decimal("0.9"),        # Slight discount for altcoins
            "OPPORTUNITY": Decimal("0.8"),   # Larger discount for memecoins
        }
        return adjustments.get(asset_tier, Decimal("0.8"))
    
    def _apply_calibration(self, raw_confidence: Decimal) -> Decimal:
        """
        Apply calibration based on historical accuracy.
        
        Adjusts confidence scores to match actual success rates.
        """
        if len(self.trade_history) < self.min_samples_for_calibration:
            # Not enough data for calibration, return raw confidence
            return raw_confidence
        
        # Find which bin this confidence falls into
        bin_index = min(int(raw_confidence * self.calibration_bins), self.calibration_bins - 1)
        bin_min = Decimal(bin_index) / self.calibration_bins
        bin_max = Decimal(bin_index + 1) / self.calibration_bins
        
        # Get trades in this confidence bin
        trades_in_bin = [
            t for t in self.trade_history
            if bin_min <= t.predicted_confidence < bin_max
        ]
        
        if len(trades_in_bin) < 5:
            # Not enough data in this bin
            return raw_confidence
        
        # Calculate actual success rate in this bin
        success_rate = sum(1 for t in trades_in_bin if t.actual_success) / len(trades_in_bin)
        calibrated_confidence = Decimal(str(success_rate))
        
        # Blend with raw confidence (50/50) to avoid over-fitting
        return (raw_confidence + calibrated_confidence) / 2
    
    def record_outcome(
        self,
        predicted_confidence: Decimal,
        actual_success: bool,
        profit_loss_pct: Decimal
    ):
        """
        Record trade outcome for calibration.
        
        Args:
            predicted_confidence: Confidence score that was predicted
            actual_success: Whether the trade was successful
            profit_loss_pct: Profit/loss percentage
        """
        outcome = TradeOutcome(
            predicted_confidence=predicted_confidence,
            actual_success=actual_success,
            profit_loss_pct=profit_loss_pct,
            timestamp=datetime.now()
        )
        
        self.trade_history.append(outcome)
        
        # Keep only last 1000 trades for calibration
        if len(self.trade_history) > 1000:
            self.trade_history = self.trade_history[-1000:]
        
        logger.info(f"Recorded outcome: confidence={predicted_confidence:.2%}, success={actual_success}, P/L={profit_loss_pct:.2%}")
    
    def get_calibration_metrics(self) -> Dict:
        """
        Get calibration metrics for analysis.
        
        Returns:
            Dictionary with calibration statistics
        """
        if len(self.trade_history) < 10:
            return {"error": "Insufficient data for metrics"}
        
        # Calculate metrics by confidence bin
        bin_metrics = []
        for bin_idx in range(self.calibration_bins):
            bin_min = Decimal(bin_idx) / self.calibration_bins
            bin_max = Decimal(bin_idx + 1) / self.calibration_bins
            
            trades_in_bin = [
                t for t in self.trade_history
                if bin_min <= t.predicted_confidence < bin_max
            ]
            
            if trades_in_bin:
                success_rate = sum(1 for t in trades_in_bin if t.actual_success) / len(trades_in_bin)
                avg_pnl = sum(t.profit_loss_pct for t in trades_in_bin) / len(trades_in_bin)
                
                bin_metrics.append({
                    "bin": f"{float(bin_min):.1f}-{float(bin_max):.1f}",
                    "predicted_confidence": float((bin_min + bin_max) / 2),
                    "actual_success_rate": float(success_rate),
                    "avg_pnl_pct": float(avg_pnl),
                    "count": len(trades_in_bin)
                })
        
        # Calculate overall metrics
        total_success = sum(1 for t in self.trade_history if t.actual_success)
        overall_success_rate = total_success / len(self.trade_history)
        
        avg_confidence = sum(t.predicted_confidence for t in self.trade_history) / len(self.trade_history)
        
        # Calculate calibration error (Brier score)
        brier_score = sum(
            (t.predicted_confidence - (1 if t.actual_success else 0)) ** 2
            for t in self.trade_history
        ) / len(self.trade_history)
        
        return {
            "total_trades": len(self.trade_history),
            "overall_success_rate": float(overall_success_rate),
            "average_confidence": float(avg_confidence),
            "brier_score": float(brier_score),  # Lower is better (0 = perfect)
            "bins": bin_metrics,
            "is_well_calibrated": float(brier_score) < 0.2  # Threshold for good calibration
        }
    
    def get_recent_accuracy(self, days: int = 7) -> Optional[Decimal]:
        """
        Get recent accuracy over the last N days.
        
        Args:
            days: Number of days to look back
            
        Returns:
            Success rate over the period, or None if insufficient data
        """
        cutoff = datetime.now() - timedelta(days=days)
        recent_trades = [t for t in self.trade_history if t.timestamp > cutoff]
        
        if len(recent_trades) < 5:
            return None
        
        success_count = sum(1 for t in recent_trades if t.actual_success)
        return Decimal(success_count) / len(recent_trades)
