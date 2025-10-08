"""Tests for position sizing module."""

import pytest
from decimal import Decimal
from hypothesis import given, strategies as st

from src.risk.position_sizing import (
    KellyCriterion,
    PositionSizer,
    PositionSizeParams,
    AssetTier,
    calculate_risk_reward_ratio,
    min_win_rate_for_profitability,
)


class TestKellyCriterion:
    """Tests for Kelly Criterion calculator."""
    
    def test_kelly_with_positive_edge(self):
        """Test Kelly with positive edge (should recommend position)."""
        win_rate = Decimal("0.60")  # 60% win rate
        avg_win = Decimal("100")
        avg_loss = Decimal("50")
        
        kelly = KellyCriterion.calculate(win_rate, avg_win, avg_loss)
        
        # Should recommend some position
        assert kelly > 0
        # Should be conservative (fractional Kelly)
        assert kelly <= Decimal("0.1")  # Less than or equal to 10%
    
    def test_kelly_with_negative_edge(self):
        """Test Kelly with negative edge (should not recommend position)."""
        win_rate = Decimal("0.40")  # 40% win rate (losing edge)
        avg_win = Decimal("50")
        avg_loss = Decimal("100")
        
        kelly = KellyCriterion.calculate(win_rate, avg_win, avg_loss)
        
        # Should recommend no position
        assert kelly == 0
    
    def test_kelly_minimum_win_rate(self):
        """Test that Kelly returns 0 below minimum win rate."""
        win_rate = Decimal("0.50")  # Exactly break-even
        avg_win = Decimal("100")
        avg_loss = Decimal("100")
        
        kelly = KellyCriterion.calculate(win_rate, avg_win, avg_loss)
        
        assert kelly == 0
    
    def test_kelly_zero_avg_loss(self):
        """Test Kelly with zero average loss (edge case)."""
        win_rate = Decimal("0.60")
        avg_win = Decimal("100")
        avg_loss = Decimal("0")
        
        kelly = KellyCriterion.calculate(win_rate, avg_win, avg_loss)
        
        assert kelly == 0
    
    def test_kelly_zero_avg_win(self):
        """Test Kelly criterion with zero average win."""
        win_rate = Decimal("0.60")
        avg_win = Decimal("0")
        avg_loss = Decimal("100")
        
        kelly = KellyCriterion.calculate(win_rate, avg_win, avg_loss)
        
        assert kelly == 0  # Can't calculate with zero avg_win
    
    def test_kelly_negative_avg_win(self):
        """Test Kelly criterion with negative average win."""
        win_rate = Decimal("0.60")
        avg_win = Decimal("-50")
        avg_loss = Decimal("100")
        
        kelly = KellyCriterion.calculate(win_rate, avg_win, avg_loss)
        
        assert kelly == 0  # Invalid scenario
    
    def test_kelly_custom_fraction(self):
        """Test Kelly with custom fractional value."""
        win_rate = Decimal("0.60")
        avg_win = Decimal("100")
        avg_loss = Decimal("50")
        
        kelly_25 = KellyCriterion.calculate(win_rate, avg_win, avg_loss, Decimal("0.25"))
        kelly_50 = KellyCriterion.calculate(win_rate, avg_win, avg_loss, Decimal("0.50"))
        
        # 50% Kelly should be exactly double 25% Kelly
        assert kelly_50 == kelly_25 * 2
    
    @given(
        win_rate=st.decimals(min_value=0.51, max_value=0.99, places=2),
        avg_win=st.decimals(min_value=1, max_value=1000, places=2),
        avg_loss=st.decimals(min_value=1, max_value=1000, places=2),
    )
    def test_kelly_never_exceeds_100_percent(self, win_rate, avg_win, avg_loss):
        """Property test: Kelly should never recommend >100% position."""
        kelly = KellyCriterion.calculate(win_rate, avg_win, avg_loss)
        assert 0 <= kelly <= 1


class TestPositionSizer:
    """Tests for position sizing calculator."""
    
    def test_foundation_position_sizing(
        self,
        sample_portfolio_value,
        sample_win_rate,
        sample_avg_win,
        sample_avg_loss,
        sample_confidence,
    ):
        """Test position sizing for foundation tier (BTC/ETH/SOL)."""
        params = PositionSizeParams(
            portfolio_value=sample_portfolio_value,
            win_rate=sample_win_rate,
            avg_win=sample_avg_win,
            avg_loss=sample_avg_loss,
            confidence=sample_confidence,
            asset_tier=AssetTier.FOUNDATION,
        )
        
        sizer = PositionSizer(params)
        position_size = sizer.calculate_position_size()
        
        # Should return a positive position
        assert position_size > 0
        
        # Should not exceed tier limit (5% for foundation)
        max_allowed = sample_portfolio_value * Decimal("0.05")
        assert position_size <= max_allowed
        
        # Should not exceed hard maximum (2%)
        hard_max = sample_portfolio_value * Decimal("0.02")
        assert position_size <= hard_max
    
    def test_opportunity_position_sizing(
        self,
        sample_portfolio_value,
        sample_win_rate,
        sample_avg_win,
        sample_avg_loss,
        sample_confidence,
    ):
        """Test position sizing for opportunity tier (memecoins)."""
        params = PositionSizeParams(
            portfolio_value=sample_portfolio_value,
            win_rate=sample_win_rate,
            avg_win=sample_avg_win,
            avg_loss=sample_avg_loss,
            confidence=sample_confidence,
            asset_tier=AssetTier.OPPORTUNITY,
        )
        
        sizer = PositionSizer(params)
        position_size = sizer.calculate_position_size()
        
        # Should be much smaller than foundation
        max_allowed = sample_portfolio_value * Decimal("0.01")  # 1% max for memecoins
        assert position_size <= max_allowed
    
    def test_confidence_affects_position_size(
        self,
        sample_portfolio_value,
        sample_win_rate,
        sample_avg_win,
        sample_avg_loss,
        high_confidence,
        low_confidence,
    ):
        """Test that higher confidence results in larger positions."""
        params_high = PositionSizeParams(
            portfolio_value=sample_portfolio_value,
            win_rate=sample_win_rate,
            avg_win=sample_avg_win,
            avg_loss=sample_avg_loss,
            confidence=high_confidence,
            asset_tier=AssetTier.FOUNDATION,
        )
        
        params_low = PositionSizeParams(
            portfolio_value=sample_portfolio_value,
            win_rate=sample_win_rate,
            avg_win=sample_avg_win,
            avg_loss=sample_avg_loss,
            confidence=low_confidence,
            asset_tier=AssetTier.FOUNDATION,
        )
        
        sizer_high = PositionSizer(params_high)
        sizer_low = PositionSizer(params_low)
        
        high_pos = sizer_high.calculate_position_size()
        low_pos = sizer_low.calculate_position_size()
        
        # Higher confidence should result in larger position
        assert high_pos > low_pos
    
    def test_invalid_parameters_raise_errors(self):
        """Test that invalid parameters raise appropriate errors."""
        # Negative portfolio value
        with pytest.raises(ValueError, match="Portfolio value must be positive"):
            params = PositionSizeParams(
                portfolio_value=Decimal("-1000"),
                win_rate=Decimal("0.6"),
                avg_win=Decimal("100"),
                avg_loss=Decimal("50"),
                confidence=Decimal("0.8"),
                asset_tier=AssetTier.FOUNDATION,
            )
            PositionSizer(params)
        
        # Invalid win rate
        with pytest.raises(ValueError, match="Win rate must be between 0 and 1"):
            params = PositionSizeParams(
                portfolio_value=Decimal("10000"),
                win_rate=Decimal("1.5"),  # >100%
                avg_win=Decimal("100"),
                avg_loss=Decimal("50"),
                confidence=Decimal("0.8"),
                asset_tier=AssetTier.FOUNDATION,
            )
            PositionSizer(params)
        
        # Invalid confidence
        with pytest.raises(ValueError, match="Confidence must be between 0 and 1"):
            params = PositionSizeParams(
                portfolio_value=Decimal("10000"),
                win_rate=Decimal("0.6"),
                avg_win=Decimal("100"),
                avg_loss=Decimal("50"),
                confidence=Decimal("1.5"),  # >100%
                asset_tier=AssetTier.FOUNDATION,
            )
            PositionSizer(params)
        
        # Invalid avg_win (zero)
        with pytest.raises(ValueError, match="Average win must be positive"):
            params = PositionSizeParams(
                portfolio_value=Decimal("10000"),
                win_rate=Decimal("0.6"),
                avg_win=Decimal("0"),
                avg_loss=Decimal("50"),
                confidence=Decimal("0.8"),
                asset_tier=AssetTier.FOUNDATION,
            )
            PositionSizer(params)
        
        # Invalid avg_loss (negative)
        with pytest.raises(ValueError, match="Average loss must be positive"):
            params = PositionSizeParams(
                portfolio_value=Decimal("10000"),
                win_rate=Decimal("0.6"),
                avg_win=Decimal("100"),
                avg_loss=Decimal("-50"),
                confidence=Decimal("0.8"),
                asset_tier=AssetTier.FOUNDATION,
            )
            PositionSizer(params)
    
    def test_stop_loss_calculation(
        self,
        sample_portfolio_value,
        sample_win_rate,
        sample_avg_win,
        sample_avg_loss,
        sample_confidence,
        sample_entry_price,
    ):
        """Test stop loss price calculation."""
        params = PositionSizeParams(
            portfolio_value=sample_portfolio_value,
            win_rate=sample_win_rate,
            avg_win=sample_avg_win,
            avg_loss=sample_avg_loss,
            confidence=sample_confidence,
            asset_tier=AssetTier.FOUNDATION,
        )
        
        sizer = PositionSizer(params)
        stop_loss = sizer.calculate_stop_loss(sample_entry_price, Decimal("5.0"))
        
        # Stop loss should be below entry
        assert stop_loss < sample_entry_price
        
        # Should be approximately 5% below entry
        expected = sample_entry_price * Decimal("0.95")
        assert abs(stop_loss - expected) < Decimal("0.01")
    
    def test_stop_loss_with_zero_risk(self):
        """Test stop loss calculation with zero risk percentage."""
        params = PositionSizeParams(
            portfolio_value=Decimal("10000"),
            win_rate=Decimal("0.6"),
            avg_win=Decimal("100"),
            avg_loss=Decimal("50"),
            confidence=Decimal("0.8"),
            asset_tier=AssetTier.FOUNDATION,
        )
        
        sizer = PositionSizer(params)
        entry_price = Decimal("100")
        
        # Zero or negative risk should raise error
        with pytest.raises(ValueError, match="Stop loss percentage must be positive"):
            sizer.calculate_stop_loss(entry_price, Decimal("0"))
        
        with pytest.raises(ValueError, match="Stop loss percentage must be positive"):
            sizer.calculate_stop_loss(entry_price, Decimal("-5"))
    
    def test_stop_loss_with_large_risk(self):
        """Test stop loss calculation with large risk percentage."""
        params = PositionSizeParams(
            portfolio_value=Decimal("10000"),
            win_rate=Decimal("0.6"),
            avg_win=Decimal("100"),
            avg_loss=Decimal("50"),
            confidence=Decimal("0.8"),
            asset_tier=AssetTier.FOUNDATION,
        )
        
        sizer = PositionSizer(params)
        entry_price = Decimal("100")
        
        # 50% risk
        stop_loss = sizer.calculate_stop_loss(entry_price, Decimal("50"))
        expected = entry_price * Decimal("0.5")
        assert stop_loss == expected
    
    def test_stop_loss_invalid_entry_price(self):
        """Test stop loss with invalid entry price."""
        params = PositionSizeParams(
            portfolio_value=Decimal("10000"),
            win_rate=Decimal("0.6"),
            avg_win=Decimal("100"),
            avg_loss=Decimal("50"),
            confidence=Decimal("0.8"),
            asset_tier=AssetTier.FOUNDATION,
        )
        
        sizer = PositionSizer(params)
        
        # Zero entry price - covers line 184
        with pytest.raises(ValueError, match="Entry price must be positive"):
            sizer.calculate_stop_loss(Decimal("0"), Decimal("5"))
        
        # Negative entry price
        with pytest.raises(ValueError, match="Entry price must be positive"):
            sizer.calculate_stop_loss(Decimal("-100"), Decimal("5"))
    
    def test_memecoin_tighter_stop_loss(
        self,
        sample_portfolio_value,
        sample_win_rate,
        sample_avg_win,
        sample_avg_loss,
        sample_confidence,
        sample_entry_price,
    ):
        """Test that memecoins get tighter stop losses."""
        params_foundation = PositionSizeParams(
            portfolio_value=sample_portfolio_value,
            win_rate=sample_win_rate,
            avg_win=sample_avg_win,
            avg_loss=sample_avg_loss,
            confidence=sample_confidence,
            asset_tier=AssetTier.FOUNDATION,
        )
        
        params_memecoin = PositionSizeParams(
            portfolio_value=sample_portfolio_value,
            win_rate=sample_win_rate,
            avg_win=sample_avg_win,
            avg_loss=sample_avg_loss,
            confidence=sample_confidence,
            asset_tier=AssetTier.OPPORTUNITY,
        )
        
        sizer_foundation = PositionSizer(params_foundation)
        sizer_memecoin = PositionSizer(params_memecoin)
        
        stop_foundation = sizer_foundation.calculate_stop_loss(sample_entry_price, Decimal("5.0"))
        stop_memecoin = sizer_memecoin.calculate_stop_loss(sample_entry_price, Decimal("5.0"))
        
        # Memecoin stop should be tighter (higher price)
        assert stop_memecoin > stop_foundation
    
    def test_position_quantity_calculation(
        self,
        sample_portfolio_value,
        sample_win_rate,
        sample_avg_win,
        sample_avg_loss,
        sample_confidence,
        sample_entry_price,
    ):
        """Test token quantity calculation."""
        params = PositionSizeParams(
            portfolio_value=sample_portfolio_value,
            win_rate=sample_win_rate,
            avg_win=sample_avg_win,
            avg_loss=sample_avg_loss,
            confidence=sample_confidence,
            asset_tier=AssetTier.FOUNDATION,
        )
        
        sizer = PositionSizer(params)
        quantity = sizer.calculate_position_quantity(sample_entry_price)
        
        # Quantity should be positive
        assert quantity > 0
        
        # Quantity * price should equal position size
        position_size = sizer.calculate_position_size()
        calculated_value = quantity * sample_entry_price
        
        # Allow small rounding error
        assert abs(calculated_value - position_size) < Decimal("0.01")
    
    def test_position_quantity_invalid_entry_price(self):
        """Test position quantity with invalid entry price."""
        params = PositionSizeParams(
            portfolio_value=Decimal("10000"),
            win_rate=Decimal("0.6"),
            avg_win=Decimal("100"),
            avg_loss=Decimal("50"),
            confidence=Decimal("0.8"),
            asset_tier=AssetTier.FOUNDATION,
        )
        
        sizer = PositionSizer(params)
        
        # Zero entry price
        with pytest.raises(ValueError, match="Entry price must be positive"):
            sizer.calculate_position_quantity(Decimal("0"))
        
        # Negative entry price
        with pytest.raises(ValueError, match="Entry price must be positive"):
            sizer.calculate_position_quantity(Decimal("-100"))
    
    def test_tier_allocation_validation(
        self,
        sample_portfolio_value,
        sample_win_rate,
        sample_avg_win,
        sample_avg_loss,
        sample_confidence,
    ):
        """Test tier allocation limit validation."""
        params = PositionSizeParams(
            portfolio_value=sample_portfolio_value,
            win_rate=sample_win_rate,
            avg_win=sample_avg_win,
            avg_loss=sample_avg_loss,
            confidence=sample_confidence,
            asset_tier=AssetTier.OPPORTUNITY,  # Max 20% for memecoins
        )
        
        sizer = PositionSizer(params)
        
        # Should allow position with low current exposure
        assert sizer.validate_tier_allocation(Decimal("5.0"))
        
        # Should reject position with high current exposure
        assert not sizer.validate_tier_allocation(Decimal("19.5"))
    
    @given(
        portfolio_value=st.decimals(min_value=1000, max_value=1000000, places=2),
        entry_price=st.decimals(min_value=0.01, max_value=10000, places=2),
    )
    def test_position_never_exceeds_portfolio(self, portfolio_value, entry_price):
        """Property test: Position size should never exceed portfolio value."""
        params = PositionSizeParams(
            portfolio_value=portfolio_value,
            win_rate=Decimal("0.7"),  # Good win rate
            avg_win=Decimal("100"),
            avg_loss=Decimal("50"),
            confidence=Decimal("0.9"),  # High confidence
            asset_tier=AssetTier.FOUNDATION,
        )
        
        sizer = PositionSizer(params)
        position_size = sizer.calculate_position_size()
        
        # Should never exceed portfolio
        assert position_size <= portfolio_value


class TestRiskRewardRatio:
    """Tests for risk-reward ratio calculations."""
    
    def test_basic_risk_reward_calculation(
        self, sample_entry_price, sample_take_profit, sample_stop_loss
    ):
        """Test basic risk-reward ratio calculation."""
        rr_ratio = calculate_risk_reward_ratio(
            sample_entry_price,
            sample_take_profit,
            sample_stop_loss
        )
        
        # With entry=100, tp=120, sl=95:
        # Reward = 20, Risk = 5, RR = 4.0
        assert rr_ratio == Decimal("4.0")
    
    def test_invalid_risk_reward_inputs(self, sample_entry_price):
        """Test that invalid inputs raise errors."""
        # Stop loss above entry
        with pytest.raises(ValueError, match="Stop loss must be below entry"):
            calculate_risk_reward_ratio(
                sample_entry_price,
                Decimal("120"),
                Decimal("105"),  # Above entry
            )
        
        # Take profit below entry
        with pytest.raises(ValueError, match="Take profit must be above entry"):
            calculate_risk_reward_ratio(
                sample_entry_price,
                Decimal("95"),  # Below entry
                Decimal("90"),
            )
        
        # Zero entry price - covers line 248
        with pytest.raises(ValueError, match="Entry price must be positive"):
            calculate_risk_reward_ratio(
                Decimal("0"),
                Decimal("120"),
                Decimal("90"),
            )
        
        # Negative entry price
        with pytest.raises(ValueError, match="Entry price must be positive"):
            calculate_risk_reward_ratio(
                Decimal("-100"),
                Decimal("120"),
                Decimal("90"),
            )
    
    def test_minimum_win_rate_calculation(self):
        """Test minimum win rate calculation for profitability."""
        # With 2:1 RR, need 33.3% win rate
        min_wr = min_win_rate_for_profitability(Decimal("2.0"))
        expected = Decimal("1") / Decimal("3")
        assert abs(min_wr - expected) < Decimal("0.001")
        
        # With 1:1 RR, need 50% win rate
        min_wr = min_win_rate_for_profitability(Decimal("1.0"))
        assert min_wr == Decimal("0.5")
        
        # With 3:1 RR, need 25% win rate
        min_wr = min_win_rate_for_profitability(Decimal("3.0"))
        assert min_wr == Decimal("0.25")
    
    @given(
        entry=st.decimals(min_value=1, max_value=1000, places=2),
        reward_pct=st.decimals(min_value=5, max_value=100, places=2),
        risk_pct=st.decimals(min_value=1, max_value=20, places=2),
    )
    def test_risk_reward_always_positive(self, entry, reward_pct, risk_pct):
        """Property test: RR ratio should always be positive."""
        tp = entry * (Decimal("1") + reward_pct / Decimal("100"))
        sl = entry * (Decimal("1") - risk_pct / Decimal("100"))
        
        rr = calculate_risk_reward_ratio(entry, tp, sl)
        assert rr > 0
    
    def test_zero_risk_reward_ratio(self):
        """Test risk-reward ratio with zero risk (edge case)."""
        entry = Decimal("100")
        tp = Decimal("120")
        sl = Decimal("100")  # No risk
        
        # Should raise error for zero risk
        with pytest.raises(ValueError, match="Stop loss must be below entry"):
            calculate_risk_reward_ratio(entry, tp, sl)
    
    def test_high_risk_reward_ratio(self):
        """Test very high risk-reward ratios."""
        entry = Decimal("100")
        tp = Decimal("200")  # 100% gain
        sl = Decimal("99")   # 1% loss
        
        rr = calculate_risk_reward_ratio(entry, tp, sl)
        assert rr == Decimal("100")  # 100:1 ratio
    
    def test_min_win_rate_zero_rr(self):
        """Test minimum win rate with zero RR (should handle edge case)."""
        # Zero RR means you need 100% win rate (impossible)
        min_wr = min_win_rate_for_profitability(Decimal("0"))
        assert min_wr == Decimal("1")  # 100%
