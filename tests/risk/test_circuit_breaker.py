"""Tests for circuit breaker system."""

import pytest
from decimal import Decimal
from datetime import datetime, timedelta

from src.risk.circuit_breaker import (
    CircuitBreaker,
    BreakerType,
    BreakerState,
    BreakerConfig,
)


class TestCircuitBreaker:
    """Tests for circuit breaker system."""
    
    @pytest.fixture
    def breaker(self):
        """Create a circuit breaker with default config."""
        return CircuitBreaker()
    
    @pytest.fixture
    def custom_breaker(self):
        """Create a circuit breaker with custom (loose) config for testing."""
        configs = {
            BreakerType.DAILY_LOSS: BreakerConfig(
                breaker_type=BreakerType.DAILY_LOSS,
                threshold=Decimal("10.0"),  # 10% (looser than default)
                cooling_period_minutes=1,  # Very short for testing
            ),
            BreakerType.CONSECUTIVE_LOSSES: BreakerConfig(
                breaker_type=BreakerType.CONSECUTIVE_LOSSES,
                threshold=Decimal("3"),  # 3 losses
                cooling_period_minutes=1,
            ),
        }
        return CircuitBreaker(configs)
    
    def test_initial_state(self, breaker):
        """Test that breaker starts in closed state."""
        assert breaker.is_trading_allowed()
        assert len(breaker.get_active_breakers()) == 0
    
    def test_daily_loss_breaker_trips(self, breaker):
        """Test daily loss breaker trips when threshold exceeded."""
        start_value = Decimal("10000")
        # 6% loss (exceeds 5% threshold)
        current_value = Decimal("9400")
        
        result = breaker.check_daily_loss(current_value, start_value)
        
        assert result is True
        assert not breaker.is_trading_allowed()
        assert BreakerType.DAILY_LOSS in breaker.get_active_breakers()
    
    def test_daily_loss_breaker_does_not_trip(self, breaker):
        """Test daily loss breaker doesn't trip below threshold."""
        start_value = Decimal("10000")
        # 4% loss (below 5% threshold)
        current_value = Decimal("9600")
        
        result = breaker.check_daily_loss(current_value, start_value)
        
        assert result is False
        assert breaker.is_trading_allowed()
    
    def test_weekly_loss_breaker(self, breaker):
        """Test weekly loss breaker."""
        start_value = Decimal("10000")
        # 11% loss (exceeds 10% threshold)
        current_value = Decimal("8900")
        
        result = breaker.check_weekly_loss(current_value, start_value)
        
        assert result is True
        assert not breaker.is_trading_allowed()
        assert BreakerType.WEEKLY_LOSS in breaker.get_active_breakers()
    
    def test_drawdown_breaker(self, breaker):
        """Test drawdown breaker."""
        peak_value = Decimal("10000")
        # 16% drawdown (exceeds 15% threshold)
        current_value = Decimal("8400")
        
        result = breaker.check_drawdown(current_value, peak_value)
        
        assert result is True
        assert not breaker.is_trading_allowed()
        assert BreakerType.DRAWDOWN in breaker.get_active_breakers()
    
    def test_volatility_breaker(self, breaker):
        """Test volatility breaker."""
        # Volatility index of 150 (exceeds 100 threshold)
        result = breaker.check_volatility(Decimal("150"))
        
        assert result is True
        assert not breaker.is_trading_allowed()
        assert BreakerType.VOLATILITY in breaker.get_active_breakers()
    
    def test_liquidity_breaker(self, breaker):
        """Test liquidity breaker."""
        # $30k liquidity (below $50k threshold)
        result = breaker.check_liquidity(Decimal("30000"))
        
        assert result is True
        assert not breaker.is_trading_allowed()
        assert BreakerType.LIQUIDITY in breaker.get_active_breakers()
    
    def test_consecutive_losses_breaker(self, breaker):
        """Test consecutive losses breaker."""
        # Record 4 losses (below threshold)
        for _ in range(4):
            result = breaker.record_trade_result(is_win=False)
            assert result is False  # Should not trip yet
        
        # 5th loss should trip
        result = breaker.record_trade_result(is_win=False)
        assert result is True
        assert not breaker.is_trading_allowed()
        assert BreakerType.CONSECUTIVE_LOSSES in breaker.get_active_breakers()
    
    def test_winning_trade_resets_loss_counter(self, breaker):
        """Test that winning trade resets consecutive loss counter."""
        # Record 3 losses
        for _ in range(3):
            breaker.record_trade_result(is_win=False)
        
        # Win resets counter
        breaker.record_trade_result(is_win=True)
        
        # Should be able to lose 5 more times before breaker trips
        for _ in range(4):
            result = breaker.record_trade_result(is_win=False)
            assert result is False
        
        # 5th loss trips
        result = breaker.record_trade_result(is_win=False)
        assert result is True
    
    def test_api_failure_breaker(self, breaker):
        """Test API failure breaker."""
        # Record 2 failures (below threshold)
        for _ in range(2):
            result = breaker.record_api_failure()
            assert result is False
        
        # 3rd failure should trip
        result = breaker.record_api_failure()
        assert result is True
        assert not breaker.is_trading_allowed()
        assert BreakerType.API_FAILURE in breaker.get_active_breakers()
    
    def test_api_success_resets_failure_counter(self, breaker):
        """Test that successful API call resets failure counter."""
        # Record 2 failures
        for _ in range(2):
            breaker.record_api_failure()
        
        # Success resets counter
        breaker.record_api_success()
        
        # Should be able to fail 3 more times
        for _ in range(2):
            result = breaker.record_api_failure()
            assert result is False
        
        result = breaker.record_api_failure()
        assert result is True
    
    def test_multiple_breakers_can_trip(self, breaker):
        """Test that multiple breakers can be active simultaneously."""
        # Trip daily loss breaker
        breaker.check_daily_loss(Decimal("9400"), Decimal("10000"))
        
        # Trip volatility breaker
        breaker.check_volatility(Decimal("150"))
        
        active = breaker.get_active_breakers()
        assert len(active) == 2
        assert BreakerType.DAILY_LOSS in active
        assert BreakerType.VOLATILITY in active
    
    def test_cooling_period_short(self, custom_breaker):
        """Test that breaker resets after cooling period."""
        import time
        
        # Trip breaker
        custom_breaker.check_daily_loss(Decimal("9000"), Decimal("10000"))
        assert not custom_breaker.is_trading_allowed()
        
        # Wait for cooling period (1 minute in config, but we can't wait that long)
        # So we manually adjust the trip time
        past_time = datetime.now() - timedelta(minutes=2)
        custom_breaker.trip_times[BreakerType.DAILY_LOSS] = past_time
        
        # Should be reset now
        assert custom_breaker.is_trading_allowed()
        assert len(custom_breaker.get_active_breakers()) == 0
    
    def test_manual_reset(self, breaker):
        """Test manual reset of breaker."""
        # Trip breaker
        breaker.check_daily_loss(Decimal("9400"), Decimal("10000"))
        assert not breaker.is_trading_allowed()
        
        # Manual reset
        breaker.manual_reset(BreakerType.DAILY_LOSS)
        
        # Should be allowed now
        assert breaker.is_trading_allowed()
        assert BreakerType.DAILY_LOSS not in breaker.get_active_breakers()
    
    def test_reset_all(self, breaker):
        """Test reset all breakers."""
        # Trip multiple breakers
        breaker.check_daily_loss(Decimal("9400"), Decimal("10000"))
        breaker.check_volatility(Decimal("150"))
        breaker.record_trade_result(is_win=False)  # Start loss counter
        
        assert not breaker.is_trading_allowed()
        
        # Reset all
        breaker.reset_all()
        
        # Everything should be clear
        assert breaker.is_trading_allowed()
        assert len(breaker.get_active_breakers()) == 0
        assert breaker.consecutive_losses == 0
        assert len(breaker.events) == 0
    
    def test_get_recent_events(self, breaker):
        """Test retrieving recent breaker events."""
        # Trip some breakers
        breaker.check_daily_loss(Decimal("9400"), Decimal("10000"))
        breaker.check_volatility(Decimal("150"))
        
        events = breaker.get_recent_events(minutes=60)
        
        assert len(events) == 2
        assert all(e.timestamp >= datetime.now() - timedelta(minutes=60) for e in events)
    
    def test_disabled_breaker_does_not_trip(self):
        """Test that disabled breakers don't trip."""
        configs = {
            BreakerType.DAILY_LOSS: BreakerConfig(
                breaker_type=BreakerType.DAILY_LOSS,
                threshold=Decimal("5.0"),
                enabled=False,  # Disabled
            ),
        }
        breaker = CircuitBreaker(configs)
        
        # Try to trip disabled breaker
        result = breaker.check_daily_loss(Decimal("9400"), Decimal("10000"))
        
        # Should not trip
        assert result is False
        assert breaker.is_trading_allowed()
    
    def test_breaker_event_details(self, breaker):
        """Test that breaker events contain correct details."""
        start_value = Decimal("10000")
        current_value = Decimal("9400")
        
        breaker.check_daily_loss(current_value, start_value)
        
        events = breaker.events
        assert len(events) == 1
        
        event = events[0]
        assert event.breaker_type == BreakerType.DAILY_LOSS
        assert event.threshold == Decimal("5.0")
        assert event.actual_value == Decimal("6.0")  # 6% loss
        assert "threshold" in event.message.lower()
    
    def test_zero_values_dont_crash(self, breaker):
        """Test that zero/invalid values don't crash the system."""
        # Zero start value should not crash
        result = breaker.check_daily_loss(Decimal("9000"), Decimal("0"))
        assert result is False
        
        result = breaker.check_weekly_loss(Decimal("9000"), Decimal("0"))
        assert result is False
        
        result = breaker.check_drawdown(Decimal("9000"), Decimal("0"))
        assert result is False
    
    def test_edge_case_exact_threshold(self, breaker):
        """Test behavior at exact threshold value."""
        start_value = Decimal("10000")
        # Exactly 5% loss (at threshold)
        current_value = Decimal("9500")
        
        # Should NOT trip (must exceed threshold)
        result = breaker.check_daily_loss(current_value, start_value)
        assert result is False
        
        # 5.01% should trip
        current_value = Decimal("9499")
        result = breaker.check_daily_loss(current_value, start_value)
        assert result is True


class TestBreakerIntegration:
    """Integration tests for circuit breaker system."""
    
    def test_trading_flow_with_breakers(self):
        """Test typical trading flow with circuit breakers."""
        breaker = CircuitBreaker()
        portfolio_value = Decimal("10000")
        
        # Start of day
        assert breaker.is_trading_allowed()
        
        # Make some trades
        breaker.record_trade_result(is_win=True)
        breaker.record_trade_result(is_win=True)
        
        # Still allowed
        assert breaker.is_trading_allowed()
        
        # Market turns bad
        breaker.record_trade_result(is_win=False)
        breaker.record_trade_result(is_win=False)
        breaker.record_trade_result(is_win=False)
        
        # Still allowed (only 3 losses)
        assert breaker.is_trading_allowed()
        
        # More losses
        breaker.record_trade_result(is_win=False)
        breaker.record_trade_result(is_win=False)
        
        # Should trip now (5 consecutive losses)
        assert not breaker.is_trading_allowed()
    
    def test_multiple_safety_nets(self):
        """Test that multiple safety mechanisms work together."""
        breaker = CircuitBreaker()
        
        # High volatility
        breaker.check_volatility(Decimal("150"))
        
        # AND low liquidity
        breaker.check_liquidity(Decimal("30000"))
        
        # AND losing streak
        for _ in range(5):
            breaker.record_trade_result(is_win=False)
        
        # All three should be active
        active = breaker.get_active_breakers()
        assert len(active) == 3
        assert not breaker.is_trading_allowed()
    
    def test_graceful_recovery(self):
        """Test system can recover gracefully after breaker trips."""
        configs = {
            BreakerType.CONSECUTIVE_LOSSES: BreakerConfig(
                breaker_type=BreakerType.CONSECUTIVE_LOSSES,
                threshold=Decimal("3"),
                cooling_period_minutes=1,
            ),
        }
        breaker = CircuitBreaker(configs)
        
        # Trip breaker
        for _ in range(3):
            breaker.record_trade_result(is_win=False)
        
        assert not breaker.is_trading_allowed()
        
        # Manual reset (simulating cooling period)
        breaker.manual_reset(BreakerType.CONSECUTIVE_LOSSES)
        
        # Should be able to trade again
        assert breaker.is_trading_allowed()
        
        # Win streak rebuilds confidence
        breaker.record_trade_result(is_win=True)
        breaker.record_trade_result(is_win=True)
        
        # Loss counter should be reset
        assert breaker.consecutive_losses == 0
