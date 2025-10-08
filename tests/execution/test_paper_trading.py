"""Tests for paper trading engine."""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal

from src.execution.paper_trading import (
    PaperTradingEngine,
    PaperPosition,
    PaperTrade
)


class TestPaperPosition:
    """Test PaperPosition model."""
    
    def test_cost_basis(self):
        """Test cost basis calculation."""
        position = PaperPosition(
            symbol="SOL",
            entry_price=Decimal("100"),
            quantity=Decimal("10"),
            entry_time=datetime.now(),
            fees_paid=Decimal("5")
        )
        
        assert position.cost_basis == Decimal("1005")  # 100 * 10 + 5
    
    def test_unrealized_pnl(self):
        """Test unrealized P/L calculation."""
        position = PaperPosition(
            symbol="SOL",
            entry_price=Decimal("100"),
            quantity=Decimal("10"),
            entry_time=datetime.now(),
            fees_paid=Decimal("5")
        )
        
        # Price up 10%
        current_price = Decimal("110")
        pnl = position.unrealized_pnl(current_price)
        assert pnl == Decimal("95")  # 1100 - 1005
        
        # Price down 5%
        current_price = Decimal("95")
        pnl = position.unrealized_pnl(current_price)
        assert pnl == Decimal("-55")  # 950 - 1005
    
    def test_unrealized_pnl_pct(self):
        """Test unrealized P/L percentage."""
        position = PaperPosition(
            symbol="SOL",
            entry_price=Decimal("100"),
            quantity=Decimal("10"),
            entry_time=datetime.now(),
            fees_paid=Decimal("5")
        )
        
        # Price up 10%
        current_price = Decimal("110")
        pnl_pct = position.unrealized_pnl_pct(current_price)
        assert abs(pnl_pct - Decimal("9.45")) < Decimal("0.01")  # ~9.45%


class TestPaperTradingEngine:
    """Test paper trading engine."""
    
    @pytest.fixture
    def engine(self):
        """Create engine for testing."""
        return PaperTradingEngine(
            initial_capital=Decimal("10000"),
            fee_rate=Decimal("0.001"),
            slippage_rate=Decimal("0.002")
        )
    
    def test_initialization(self, engine):
        """Test engine initialization."""
        assert engine.initial_capital == Decimal("10000")
        assert engine.cash == Decimal("10000")
        assert len(engine.positions) == 0
        assert len(engine.closed_trades) == 0
    
    def test_execute_buy_success(self, engine):
        """Test successful buy execution."""
        success = engine.execute_buy(
            symbol="SOL",
            quantity=Decimal("10"),
            price=Decimal("100"),
            stop_loss=Decimal("95"),
            take_profit=Decimal("110")
        )
        
        assert success is True
        assert "SOL" in engine.positions
        
        position = engine.positions["SOL"]
        assert position.symbol == "SOL"
        assert position.quantity == Decimal("10")
        
        # Check slippage applied (buy at 100.2)
        assert position.entry_price == Decimal("100.2")
        
        # Check cash deducted (100.2 * 10 * 1.001 = 1003.002)
        expected_cash = Decimal("10000") - Decimal("1003.002")
        assert abs(engine.cash - expected_cash) < Decimal("0.01")
    
    def test_execute_buy_insufficient_cash(self, engine):
        """Test buy with insufficient cash."""
        success = engine.execute_buy(
            symbol="SOL",
            quantity=Decimal("1000"),  # Way too much
            price=Decimal("100")
        )
        
        assert success is False
        assert len(engine.positions) == 0
        assert engine.cash == Decimal("10000")  # Unchanged
    
    def test_execute_buy_duplicate_position(self, engine):
        """Test buying same symbol twice."""
        # First buy
        engine.execute_buy(
            symbol="SOL",
            quantity=Decimal("10"),
            price=Decimal("100")
        )
        
        # Second buy (should fail)
        success = engine.execute_buy(
            symbol="SOL",
            quantity=Decimal("5"),
            price=Decimal("100")
        )
        
        assert success is False
        assert len(engine.positions) == 1
    
    def test_execute_buy_invalid_stop_loss(self, engine):
        """Test buy with invalid stop loss (above entry)."""
        success = engine.execute_buy(
            symbol="SOL",
            quantity=Decimal("10"),
            price=Decimal("100"),
            stop_loss=Decimal("105")  # Above entry!
        )
        
        assert success is False
        assert len(engine.positions) == 0
    
    def test_execute_buy_invalid_take_profit(self, engine):
        """Test buy with invalid take profit (below entry)."""
        success = engine.execute_buy(
            symbol="SOL",
            quantity=Decimal("10"),
            price=Decimal("100"),
            take_profit=Decimal("95")  # Below entry!
        )
        
        assert success is False
        assert len(engine.positions) == 0
    
    def test_execute_sell_success(self, engine):
        """Test successful sell execution."""
        # First buy
        engine.execute_buy(
            symbol="SOL",
            quantity=Decimal("10"),
            price=Decimal("100")
        )
        
        initial_cash = engine.cash
        
        # Then sell at profit
        trade = engine.execute_sell(
            symbol="SOL",
            current_price=Decimal("110"),
            exit_reason="manual"
        )
        
        assert trade is not None
        assert trade.symbol == "SOL"
        assert trade.pnl > 0  # Profit
        assert "SOL" not in engine.positions
        assert len(engine.closed_trades) == 1
        assert engine.cash > initial_cash  # More cash than after buy
    
    def test_execute_sell_no_position(self, engine):
        """Test sell without position."""
        trade = engine.execute_sell(
            symbol="SOL",
            current_price=Decimal("110")
        )
        
        assert trade is None
        assert len(engine.closed_trades) == 0
    
    def test_stop_loss_trigger(self, engine):
        """Test stop loss triggering."""
        # Buy with stop loss
        engine.execute_buy(
            symbol="SOL",
            quantity=Decimal("10"),
            price=Decimal("100"),
            stop_loss=Decimal("95")
        )
        
        # Price drops to stop loss
        exit_reason = engine.check_stop_loss_take_profit("SOL", Decimal("95"))
        assert exit_reason == "stop_loss"
        
        # Update positions (should trigger stop)
        market_prices = {"SOL": Decimal("95")}
        closed_trades = engine.update_positions(market_prices)
        
        assert len(closed_trades) == 1
        assert closed_trades[0].exit_reason == "stop_loss"
        assert closed_trades[0].pnl < 0  # Loss
    
    def test_take_profit_trigger(self, engine):
        """Test take profit triggering."""
        # Buy with take profit
        engine.execute_buy(
            symbol="SOL",
            quantity=Decimal("10"),
            price=Decimal("100"),
            take_profit=Decimal("110")
        )
        
        # Price rises to take profit
        exit_reason = engine.check_stop_loss_take_profit("SOL", Decimal("110"))
        assert exit_reason == "take_profit"
        
        # Update positions (should trigger TP)
        market_prices = {"SOL": Decimal("110")}
        closed_trades = engine.update_positions(market_prices)
        
        assert len(closed_trades) == 1
        assert closed_trades[0].exit_reason == "take_profit"
        assert closed_trades[0].pnl > 0  # Profit
    
    def test_performance_metrics_no_trades(self, engine):
        """Test metrics with no trades."""
        metrics = engine.get_performance_metrics()
        
        assert "error" in metrics
        assert metrics["cash"] == 10000.0
        assert metrics["open_positions"] == 0
    
    def test_performance_metrics_with_trades(self, engine):
        """Test metrics with completed trades."""
        # Execute some trades
        # Trade 1: Winner
        engine.execute_buy("SOL", Decimal("10"), Decimal("100"))
        engine.execute_sell("SOL", Decimal("110"))
        
        # Trade 2: Loser
        engine.execute_buy("ETH", Decimal("5"), Decimal("200"))
        engine.execute_sell("ETH", Decimal("190"))
        
        metrics = engine.get_performance_metrics()
        
        assert metrics["total_trades"] == 2
        assert metrics["winning_trades"] == 1
        assert metrics["losing_trades"] == 1
        assert 0 < metrics["win_rate"] < 1
        assert metrics["avg_win"] > 0
        assert metrics["avg_loss"] > 0
        assert metrics["profit_factor"] > 0
    
    def test_max_drawdown_calculation(self, engine):
        """Test maximum drawdown calculation."""
        # Series of losing trades
        engine.execute_buy("SOL", Decimal("10"), Decimal("100"))
        engine.execute_sell("SOL", Decimal("95"))  # -5%
        
        engine.execute_buy("ETH", Decimal("5"), Decimal("200"))
        engine.execute_sell("ETH", Decimal("190"))  # -5%
        
        metrics = engine.get_performance_metrics()
        assert metrics["max_drawdown_pct"] > 0
    
    def test_generate_report(self, engine):
        """Test report generation."""
        # Execute a trade
        engine.execute_buy("SOL", Decimal("10"), Decimal("100"))
        engine.execute_sell("SOL", Decimal("110"))
        
        report = engine.generate_report()
        
        assert "PAPER TRADING PERFORMANCE REPORT" in report
        assert "CAPITAL" in report
        assert "PROFIT & LOSS" in report
        assert "TRADING STATISTICS" in report
        assert "Total Trades" in report
    
    def test_trade_history(self, engine):
        """Test trade history retrieval."""
        # Execute multiple trades
        for i in range(5):
            symbol = f"TOKEN{i}"
            engine.execute_buy(symbol, Decimal("10"), Decimal("100"))
            engine.execute_sell(symbol, Decimal("105"))
        
        history = engine.get_trade_history(limit=3)
        
        assert len(history) == 3
        assert all("symbol" in trade for trade in history)
        assert all("pnl" in trade for trade in history)
    
    def test_multiple_positions(self, engine):
        """Test managing multiple positions."""
        # Open multiple positions
        engine.execute_buy("SOL", Decimal("10"), Decimal("100"))
        engine.execute_buy("ETH", Decimal("5"), Decimal("200"))
        engine.execute_buy("BTC", Decimal("1"), Decimal("50000"))
        
        assert len(engine.positions) == 3
        
        # Update with new prices
        market_prices = {
            "SOL": Decimal("105"),
            "ETH": Decimal("210"),
            "BTC": Decimal("52000")
        }
        
        portfolio_value = engine.portfolio_value(market_prices)
        assert portfolio_value > engine.initial_capital
    
    def test_slippage_simulation(self, engine):
        """Test that slippage is correctly applied."""
        # Buy with 0.2% slippage
        engine.execute_buy("SOL", Decimal("10"), Decimal("100"))
        
        position = engine.positions["SOL"]
        # Buy price should be 100 * 1.002 = 100.2
        assert position.entry_price == Decimal("100.2")
        
        # Sell with 0.2% slippage
        trade = engine.execute_sell("SOL", Decimal("110"))
        
        # Sell price should be 110 * 0.998 = 109.78
        assert trade.exit_price == Decimal("109.78")
    
    def test_fee_calculation(self, engine):
        """Test that fees are correctly calculated."""
        initial_cash = engine.cash
        
        # Buy $1000 worth (10 * 100)
        engine.execute_buy("SOL", Decimal("10"), Decimal("100"))
        
        position = engine.positions["SOL"]
        
        # Fees should be ~1% of cost (0.1% fee rate)
        expected_fees = Decimal("100.2") * Decimal("10") * Decimal("0.001")
        assert abs(position.fees_paid - expected_fees) < Decimal("0.01")
        
        # Total cost should be slippage + fees
        # 100.2 * 10 * 1.001 = 1003.002
        expected_cost = Decimal("1003.002")
        cash_spent = initial_cash - engine.cash
        assert abs(cash_spent - expected_cost) < Decimal("0.01")
    
    def test_daily_pnl_tracking(self, engine):
        """Test daily P/L tracking."""
        # Execute trade today
        engine.execute_buy("SOL", Decimal("10"), Decimal("100"))
        engine.execute_sell("SOL", Decimal("110"))
        
        today = datetime.now().date().isoformat()
        assert today in engine.daily_pnl
        assert engine.daily_pnl[today] > 0  # Profit today


class TestPaperTrade:
    """Test PaperTrade model."""
    
    def test_holding_period_calculation(self):
        """Test holding period calculation."""
        entry_time = datetime.now()
        exit_time = entry_time + timedelta(hours=5)
        
        trade = PaperTrade(
            symbol="SOL",
            entry_price=Decimal("100"),
            exit_price=Decimal("110"),
            quantity=Decimal("10"),
            entry_time=entry_time,
            exit_time=exit_time,
            pnl=Decimal("100"),
            pnl_pct=Decimal("10"),
            fees_paid=Decimal("2"),
            exit_reason="take_profit",
            strategy="test",
            confidence=Decimal("0.8")
        )
        
        assert abs(trade.holding_period_hours - 5.0) < 0.01


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_zero_quantity_buy(self):
        """Test buy with zero quantity."""
        engine = PaperTradingEngine()
        success = engine.execute_buy(
            symbol="SOL",
            quantity=Decimal("0"),
            price=Decimal("100")
        )
        assert success is False
    
    def test_negative_price(self):
        """Test buy with negative price."""
        engine = PaperTradingEngine()
        success = engine.execute_buy(
            symbol="SOL",
            quantity=Decimal("10"),
            price=Decimal("-100")
        )
        assert success is False
    
    def test_zero_initial_capital(self):
        """Test engine with zero initial capital."""
        engine = PaperTradingEngine(initial_capital=Decimal("0"))
        success = engine.execute_buy(
            symbol="SOL",
            quantity=Decimal("1"),
            price=Decimal("100")
        )
        assert success is False
    
    def test_portfolio_value_with_missing_prices(self):
        """Test portfolio value with missing price data."""
        engine = PaperTradingEngine()
        engine.execute_buy("SOL", Decimal("10"), Decimal("100"))
        
        # Provide empty price dict
        value = engine.portfolio_value({})
        
        # Should just return cash (positions valued at 0)
        assert value == engine.cash
