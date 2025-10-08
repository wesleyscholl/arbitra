"""Circuit breakers to halt trading during adverse conditions."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional


class BreakerType(Enum):
    """Types of circuit breakers."""
    DAILY_LOSS = "daily_loss"
    WEEKLY_LOSS = "weekly_loss"
    DRAWDOWN = "drawdown"
    VOLATILITY = "volatility"
    LIQUIDITY = "liquidity"
    API_FAILURE = "api_failure"
    CONSECUTIVE_LOSSES = "consecutive_losses"


class BreakerState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Trading halted
    COOLING = "cooling"  # Waiting to reset


@dataclass
class BreakerConfig:
    """Configuration for a circuit breaker."""
    breaker_type: BreakerType
    threshold: Decimal
    cooling_period_minutes: int = 60
    enabled: bool = True


@dataclass
class BreakerEvent:
    """Event when a circuit breaker trips."""
    breaker_type: BreakerType
    timestamp: datetime
    threshold: Decimal
    actual_value: Decimal
    message: str


class CircuitBreaker:
    """
    Circuit breaker system to halt trading during adverse conditions.
    
    This is a CRITICAL safety mechanism. When triggered, all trading stops
    immediately until conditions improve or manual override occurs.
    """
    
    # Default configurations
    DEFAULT_CONFIGS = {
        BreakerType.DAILY_LOSS: BreakerConfig(
            breaker_type=BreakerType.DAILY_LOSS,
            threshold=Decimal("5.0"),  # 5% daily loss
            cooling_period_minutes=120,  # 2 hours
        ),
        BreakerType.WEEKLY_LOSS: BreakerConfig(
            breaker_type=BreakerType.WEEKLY_LOSS,
            threshold=Decimal("10.0"),  # 10% weekly loss
            cooling_period_minutes=1440,  # 24 hours
        ),
        BreakerType.DRAWDOWN: BreakerConfig(
            breaker_type=BreakerType.DRAWDOWN,
            threshold=Decimal("15.0"),  # 15% drawdown from peak
            cooling_period_minutes=2880,  # 48 hours
        ),
        BreakerType.VOLATILITY: BreakerConfig(
            breaker_type=BreakerType.VOLATILITY,
            threshold=Decimal("100.0"),  # VIX equivalent >100
            cooling_period_minutes=60,
        ),
        BreakerType.LIQUIDITY: BreakerConfig(
            breaker_type=BreakerType.LIQUIDITY,
            threshold=Decimal("50000"),  # Min $50k liquidity
            cooling_period_minutes=30,
        ),
        BreakerType.API_FAILURE: BreakerConfig(
            breaker_type=BreakerType.API_FAILURE,
            threshold=Decimal("3"),  # 3 consecutive API failures
            cooling_period_minutes=15,
        ),
        BreakerType.CONSECUTIVE_LOSSES: BreakerConfig(
            breaker_type=BreakerType.CONSECUTIVE_LOSSES,
            threshold=Decimal("5"),  # 5 consecutive losing trades
            cooling_period_minutes=240,  # 4 hours
        ),
    }
    
    def __init__(self, configs: Optional[Dict[BreakerType, BreakerConfig]] = None):
        """
        Initialize circuit breaker system.
        
        Args:
            configs: Custom breaker configurations (uses defaults if None)
        """
        self.configs = configs or self.DEFAULT_CONFIGS.copy()
        self.states: Dict[BreakerType, BreakerState] = {
            bt: BreakerState.CLOSED for bt in BreakerType
        }
        self.trip_times: Dict[BreakerType, Optional[datetime]] = {
            bt: None for bt in BreakerType
        }
        self.events: List[BreakerEvent] = []
        
        # Tracking for various breaker types
        self.consecutive_losses = 0
        self.consecutive_api_failures = 0
        self.daily_start_value: Optional[Decimal] = None
        self.weekly_start_value: Optional[Decimal] = None
        self.peak_value: Optional[Decimal] = None
    
    def check_daily_loss(self, current_value: Decimal, start_of_day_value: Decimal) -> bool:
        """
        Check if daily loss threshold exceeded.
        
        Args:
            current_value: Current portfolio value
            start_of_day_value: Portfolio value at start of day
            
        Returns:
            True if breaker should trip
        """
        if not self.configs[BreakerType.DAILY_LOSS].enabled:
            return False
        
        if start_of_day_value <= 0:
            return False
        
        loss_pct = ((start_of_day_value - current_value) / start_of_day_value) * Decimal("100")
        threshold = self.configs[BreakerType.DAILY_LOSS].threshold
        
        if loss_pct > threshold:
            self._trip_breaker(
                BreakerType.DAILY_LOSS,
                threshold,
                loss_pct,
                f"Daily loss of {loss_pct:.2f}% exceeds threshold of {threshold}%"
            )
            return True
        
        return False
    
    def check_weekly_loss(self, current_value: Decimal, start_of_week_value: Decimal) -> bool:
        """Check if weekly loss threshold exceeded."""
        if not self.configs[BreakerType.WEEKLY_LOSS].enabled:
            return False
        
        if start_of_week_value <= 0:
            return False
        
        loss_pct = ((start_of_week_value - current_value) / start_of_week_value) * Decimal("100")
        threshold = self.configs[BreakerType.WEEKLY_LOSS].threshold
        
        if loss_pct > threshold:
            self._trip_breaker(
                BreakerType.WEEKLY_LOSS,
                threshold,
                loss_pct,
                f"Weekly loss of {loss_pct:.2f}% exceeds threshold of {threshold}%"
            )
            return True
        
        return False
    
    def check_drawdown(self, current_value: Decimal, peak_value: Decimal) -> bool:
        """Check if drawdown from peak exceeded."""
        if not self.configs[BreakerType.DRAWDOWN].enabled:
            return False
        
        if peak_value <= 0:
            return False
        
        drawdown_pct = ((peak_value - current_value) / peak_value) * Decimal("100")
        threshold = self.configs[BreakerType.DRAWDOWN].threshold
        
        if drawdown_pct > threshold:
            self._trip_breaker(
                BreakerType.DRAWDOWN,
                threshold,
                drawdown_pct,
                f"Drawdown of {drawdown_pct:.2f}% exceeds threshold of {threshold}%"
            )
            return True
        
        return False
    
    def check_volatility(self, volatility_index: Decimal) -> bool:
        """Check if market volatility too high."""
        if not self.configs[BreakerType.VOLATILITY].enabled:
            return False
        
        threshold = self.configs[BreakerType.VOLATILITY].threshold
        
        if volatility_index > threshold:
            self._trip_breaker(
                BreakerType.VOLATILITY,
                threshold,
                volatility_index,
                f"Volatility index {volatility_index:.2f} exceeds threshold of {threshold}"
            )
            return True
        
        return False
    
    def check_liquidity(self, liquidity: Decimal) -> bool:
        """Check if liquidity below minimum threshold."""
        if not self.configs[BreakerType.LIQUIDITY].enabled:
            return False
        
        threshold = self.configs[BreakerType.LIQUIDITY].threshold
        
        if liquidity < threshold:
            self._trip_breaker(
                BreakerType.LIQUIDITY,
                threshold,
                liquidity,
                f"Liquidity ${liquidity:,.0f} below threshold of ${threshold:,.0f}"
            )
            return True
        
        return False
    
    def record_trade_result(self, is_win: bool) -> bool:
        """
        Record trade result and check consecutive losses.
        
        Args:
            is_win: True if trade was profitable
            
        Returns:
            True if breaker should trip
        """
        if is_win:
            self.consecutive_losses = 0
            return False
        
        self.consecutive_losses += 1
        
        if not self.configs[BreakerType.CONSECUTIVE_LOSSES].enabled:
            return False
        
        threshold = int(self.configs[BreakerType.CONSECUTIVE_LOSSES].threshold)
        
        if self.consecutive_losses >= threshold:
            self._trip_breaker(
                BreakerType.CONSECUTIVE_LOSSES,
                Decimal(threshold),
                Decimal(self.consecutive_losses),
                f"{self.consecutive_losses} consecutive losses exceeds threshold of {threshold}"
            )
            return True
        
        return False
    
    def record_api_failure(self) -> bool:
        """
        Record API failure and check threshold.
        
        Returns:
            True if breaker should trip
        """
        self.consecutive_api_failures += 1
        
        if not self.configs[BreakerType.API_FAILURE].enabled:
            return False
        
        threshold = int(self.configs[BreakerType.API_FAILURE].threshold)
        
        if self.consecutive_api_failures >= threshold:
            self._trip_breaker(
                BreakerType.API_FAILURE,
                Decimal(threshold),
                Decimal(self.consecutive_api_failures),
                f"{self.consecutive_api_failures} consecutive API failures exceeds threshold"
            )
            return True
        
        return False
    
    def record_api_success(self) -> None:
        """Record successful API call (resets failure counter)."""
        self.consecutive_api_failures = 0
    
    def _trip_breaker(
        self,
        breaker_type: BreakerType,
        threshold: Decimal,
        actual_value: Decimal,
        message: str
    ) -> None:
        """Internal method to trip a breaker."""
        self.states[breaker_type] = BreakerState.OPEN
        self.trip_times[breaker_type] = datetime.now()
        
        event = BreakerEvent(
            breaker_type=breaker_type,
            timestamp=datetime.now(),
            threshold=threshold,
            actual_value=actual_value,
            message=message
        )
        self.events.append(event)
    
    def is_trading_allowed(self) -> bool:
        """
        Check if trading is allowed (no breakers tripped).
        
        Returns:
            True if trading is allowed, False if any breaker is open
        """
        # Check if any critical breakers are open
        for breaker_type, state in self.states.items():
            if state == BreakerState.OPEN:
                # Check if cooling period expired
                if self._is_cooling_period_expired(breaker_type):
                    self.states[breaker_type] = BreakerState.CLOSED
                    self.trip_times[breaker_type] = None
                else:
                    return False  # Breaker still open
        
        return True
    
    def _is_cooling_period_expired(self, breaker_type: BreakerType) -> bool:
        """Check if cooling period for breaker has expired."""
        trip_time = self.trip_times[breaker_type]
        if trip_time is None:
            return True
        
        config = self.configs[breaker_type]
        cooling_period = timedelta(minutes=config.cooling_period_minutes)
        
        return datetime.now() - trip_time >= cooling_period
    
    def get_active_breakers(self) -> List[BreakerType]:
        """Get list of currently active (open) breakers."""
        return [
            bt for bt, state in self.states.items()
            if state == BreakerState.OPEN
        ]
    
    def get_recent_events(self, minutes: int = 60) -> List[BreakerEvent]:
        """Get breaker events from last N minutes."""
        cutoff = datetime.now() - timedelta(minutes=minutes)
        return [e for e in self.events if e.timestamp >= cutoff]
    
    def manual_reset(self, breaker_type: BreakerType) -> None:
        """
        Manually reset a breaker (use with caution).
        
        Args:
            breaker_type: Type of breaker to reset
        """
        self.states[breaker_type] = BreakerState.CLOSED
        self.trip_times[breaker_type] = None
        
        if breaker_type == BreakerType.CONSECUTIVE_LOSSES:
            self.consecutive_losses = 0
        elif breaker_type == BreakerType.API_FAILURE:
            self.consecutive_api_failures = 0
    
    def reset_all(self) -> None:
        """Reset all breakers (DANGEROUS - use only for testing/emergencies)."""
        for breaker_type in BreakerType:
            self.manual_reset(breaker_type)
        self.events.clear()
