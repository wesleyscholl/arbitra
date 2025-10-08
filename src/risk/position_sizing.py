"""Position sizing calculations using Kelly Criterion and risk-based methods."""

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Optional


class AssetTier(Enum):
    """Asset classification for risk management."""
    FOUNDATION = "foundation"  # BTC, ETH, SOL - 50% max
    GROWTH = "growth"          # Top 20-100 altcoins - 30% max
    OPPORTUNITY = "opportunity"  # Memecoins - 20% max


@dataclass
class PositionSizeParams:
    """Parameters for position sizing calculation."""
    portfolio_value: Decimal
    win_rate: Decimal  # 0.0 to 1.0
    avg_win: Decimal  # Average win amount
    avg_loss: Decimal  # Average loss amount (positive number)
    confidence: Decimal  # AI confidence score 0.0 to 1.0
    asset_tier: AssetTier
    max_position_pct: Decimal = Decimal("2.0")  # Max 2% per trade
    max_risk_pct: Decimal = Decimal("10.0")  # Max 10% portfolio at risk


class KellyCriterion:
    """
    Kelly Criterion for optimal position sizing.
    
    Formula: f* = (p * b - q) / b
    Where:
        f* = fraction of bankroll to bet
        p = probability of winning (win rate)
        q = probability of losing (1 - p)
        b = ratio of avg win to avg loss
    
    We use fractional Kelly (0.25 - 0.5) to reduce volatility.
    """
    
    KELLY_FRACTION = Decimal("0.25")  # Use 25% of full Kelly (conservative)
    MIN_WIN_RATE = Decimal("0.51")  # Below this, don't trade
    MIN_TRADES = 20  # Minimum trades needed for Kelly to be reliable
    
    @staticmethod
    def calculate(
        win_rate: Decimal,
        avg_win: Decimal,
        avg_loss: Decimal,
        fractional: Optional[Decimal] = None
    ) -> Decimal:
        """
        Calculate Kelly Criterion position size.
        
        Args:
            win_rate: Historical win rate (0.0 to 1.0)
            avg_win: Average winning trade amount
            avg_loss: Average losing trade amount (positive)
            fractional: Kelly fraction to use (default: 0.25)
            
        Returns:
            Recommended position size as fraction of portfolio (0.0 to 1.0)
        """
        if fractional is None:
            fractional = KellyCriterion.KELLY_FRACTION
            
        # Validation
        if win_rate < KellyCriterion.MIN_WIN_RATE:
            return Decimal("0")  # Edge is negative, don't trade
            
        if avg_loss == 0:
            return Decimal("0")  # Can't calculate
            
        if avg_win <= 0:
            return Decimal("0")  # No positive expectation
            
        # Kelly formula
        loss_rate = Decimal("1") - win_rate
        win_loss_ratio = avg_win / avg_loss
        
        kelly = (win_rate * win_loss_ratio - loss_rate) / win_loss_ratio
        
        # Apply fractional Kelly for safety
        fractional_kelly = kelly * fractional
        
        # Never go negative or above 100%
        return max(Decimal("0"), min(fractional_kelly, Decimal("1")))


class PositionSizer:
    """
    Main position sizing engine combining multiple risk methods.
    """
    
    # Tier-specific limits
    TIER_LIMITS = {
        AssetTier.FOUNDATION: Decimal("5.0"),     # Max 5% per position
        AssetTier.GROWTH: Decimal("3.0"),         # Max 3% per position
        AssetTier.OPPORTUNITY: Decimal("1.0"),    # Max 1% per position (memecoins)
    }
    
    # Portfolio allocation limits
    TIER_PORTFOLIO_LIMITS = {
        AssetTier.FOUNDATION: Decimal("60.0"),    # Max 60% in BTC/ETH/SOL
        AssetTier.GROWTH: Decimal("40.0"),        # Max 40% in altcoins
        AssetTier.OPPORTUNITY: Decimal("20.0"),   # Max 20% in memecoins
    }
    
    def __init__(self, params: PositionSizeParams):
        """Initialize position sizer with parameters."""
        self.params = params
        self._validate_params()
    
    def _validate_params(self) -> None:
        """Validate input parameters."""
        if self.params.portfolio_value <= 0:
            raise ValueError("Portfolio value must be positive")
        
        if not 0 <= self.params.win_rate <= 1:
            raise ValueError("Win rate must be between 0 and 1")
        
        if not 0 <= self.params.confidence <= 1:
            raise ValueError("Confidence must be between 0 and 1")
        
        if self.params.avg_win <= 0:
            raise ValueError("Average win must be positive")
        
        if self.params.avg_loss <= 0:
            raise ValueError("Average loss must be positive")
    
    def calculate_position_size(self) -> Decimal:
        """
        Calculate final position size using multiple methods.
        
        Returns the minimum of:
        1. Kelly Criterion (fractional)
        2. Fixed percentage based on confidence
        3. Tier-specific limits
        4. Hard maximum per trade
        
        Returns:
            Position size in dollars (not percentage)
        """
        # Method 1: Kelly Criterion
        kelly_fraction = KellyCriterion.calculate(
            self.params.win_rate,
            self.params.avg_win,
            self.params.avg_loss
        )
        
        # Method 2: Confidence-based sizing
        # Low confidence = smaller size
        confidence_multiplier = self.params.confidence * Decimal("0.5") + Decimal("0.5")
        confidence_size = self.params.max_position_pct * confidence_multiplier / Decimal("100")
        
        # Method 3: Tier limit
        tier_limit = self.TIER_LIMITS[self.params.asset_tier] / Decimal("100")
        
        # Method 4: Hard maximum
        hard_max = self.params.max_position_pct / Decimal("100")
        
        # Take the most conservative (minimum)
        position_fraction = min(kelly_fraction, confidence_size, tier_limit, hard_max)
        
        # Convert to dollar amount
        position_size = position_fraction * self.params.portfolio_value
        
        return position_size
    
    def calculate_stop_loss(self, entry_price: Decimal, stop_loss_pct: Decimal = Decimal("5.0")) -> Decimal:
        """
        Calculate stop-loss price.
        
        Args:
            entry_price: Entry price of the position
            stop_loss_pct: Stop loss percentage (default 5%)
            
        Returns:
            Stop-loss price
        """
        if entry_price <= 0:
            raise ValueError("Entry price must be positive")
        
        if stop_loss_pct <= 0:
            raise ValueError("Stop loss percentage must be positive")
        
        # Tighter stops for higher-risk tiers
        if self.params.asset_tier == AssetTier.OPPORTUNITY:
            stop_loss_pct = min(stop_loss_pct, Decimal("3.0"))  # Max 3% for memecoins
        
        stop_price = entry_price * (Decimal("1") - stop_loss_pct / Decimal("100"))
        return stop_price
    
    def calculate_position_quantity(self, entry_price: Decimal) -> Decimal:
        """
        Calculate position quantity (number of tokens).
        
        Args:
            entry_price: Price per token
            
        Returns:
            Quantity of tokens to buy
        """
        if entry_price <= 0:
            raise ValueError("Entry price must be positive")
        
        position_size = self.calculate_position_size()
        quantity = position_size / entry_price
        
        return quantity
    
    def validate_tier_allocation(self, current_tier_exposure: Decimal) -> bool:
        """
        Check if adding this position would exceed tier allocation limits.
        
        Args:
            current_tier_exposure: Current portfolio % allocated to this tier
            
        Returns:
            True if position is allowed, False otherwise
        """
        tier_limit = self.TIER_PORTFOLIO_LIMITS[self.params.asset_tier]
        position_pct = (self.calculate_position_size() / self.params.portfolio_value) * Decimal("100")
        new_exposure = current_tier_exposure + position_pct
        
        return new_exposure <= tier_limit


def calculate_risk_reward_ratio(
    entry_price: Decimal,
    take_profit_price: Decimal,
    stop_loss_price: Decimal
) -> Decimal:
    """
    Calculate risk-reward ratio for a trade.
    
    Args:
        entry_price: Entry price
        take_profit_price: Target profit price
        stop_loss_price: Stop loss price
        
    Returns:
        Risk-reward ratio (e.g., 3.0 means 3:1 reward:risk)
    """
    if entry_price <= 0:
        raise ValueError("Entry price must be positive")
    
    if stop_loss_price >= entry_price:
        raise ValueError("Stop loss must be below entry price")
    
    if take_profit_price <= entry_price:
        raise ValueError("Take profit must be above entry price")
    
    potential_profit = take_profit_price - entry_price
    potential_loss = entry_price - stop_loss_price
    
    # potential_loss is guaranteed to be > 0 due to validation above
    return potential_profit / potential_loss


def min_win_rate_for_profitability(risk_reward_ratio: Decimal) -> Decimal:
    """
    Calculate minimum win rate needed for profitability given risk-reward ratio.
    
    Formula: min_win_rate = 1 / (1 + risk_reward_ratio)
    
    Args:
        risk_reward_ratio: Risk-reward ratio (e.g., 2.0 for 2:1)
        
    Returns:
        Minimum win rate as decimal (e.g., 0.33 for 33%)
    """
    if risk_reward_ratio <= 0:
        return Decimal("1")  # Need 100% win rate (impossible)
    
    min_wr = Decimal("1") / (Decimal("1") + risk_reward_ratio)
    return min_wr
