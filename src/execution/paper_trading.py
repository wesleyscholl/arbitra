"""
Paper Trading Engine - Realistic simulation with performance tracking.

This module provides a complete paper trading system that simulates
real trading with realistic slippage, fees, and execution.
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class PaperPosition:
    """Simulated position."""
    symbol: str
    entry_price: Decimal
    quantity: Decimal
    entry_time: datetime
    stop_loss: Optional[Decimal] = None
    take_profit: Optional[Decimal] = None
    fees_paid: Decimal = Decimal("0")
    strategy: str = "unknown"
    confidence: Decimal = Decimal("0.5")
    
    @property
    def cost_basis(self) -> Decimal:
        """Total cost including fees."""
        return (self.entry_price * self.quantity) + self.fees_paid
    
    def current_value(self, current_price: Decimal) -> Decimal:
        """Current position value."""
        return current_price * self.quantity
    
    def unrealized_pnl(self, current_price: Decimal) -> Decimal:
        """Unrealized profit/loss."""
        return self.current_value(current_price) - self.cost_basis
    
    def unrealized_pnl_pct(self, current_price: Decimal) -> Decimal:
        """Unrealized P/L percentage."""
        if self.cost_basis == 0:
            return Decimal("0")
        return (self.unrealized_pnl(current_price) / self.cost_basis) * Decimal("100")


@dataclass
class PaperTrade:
    """Completed simulated trade."""
    symbol: str
    entry_price: Decimal
    exit_price: Decimal
    quantity: Decimal
    entry_time: datetime
    exit_time: datetime
    pnl: Decimal
    pnl_pct: Decimal
    fees_paid: Decimal
    exit_reason: str  # "take_profit", "stop_loss", "manual", "timeout"
    strategy: str
    confidence: Decimal
    holding_period_hours: float = field(init=False)
    
    def __post_init__(self):
        """Calculate holding period."""
        self.holding_period_hours = (self.exit_time - self.entry_time).total_seconds() / 3600


class PaperTradingEngine:
    """
    Full-featured paper trading engine with realistic simulation.
    
    Features:
    - Real market data
    - Realistic slippage simulation
    - Fee calculation
    - Stop-loss and take-profit execution
    - Performance tracking
    - Detailed analytics
    """
    
    def __init__(
        self,
        initial_capital: Decimal = Decimal("10000"),
        fee_rate: Decimal = Decimal("0.001"),  # 0.1% per trade
        slippage_rate: Decimal = Decimal("0.002")  # 0.2% slippage
    ):
        """Initialize paper trading engine."""
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.fee_rate = fee_rate
        self.slippage_rate = slippage_rate
        
        self.positions: Dict[str, PaperPosition] = {}
        self.closed_trades: List[PaperTrade] = []
        self.start_time = datetime.now()
        
        # Performance tracking
        self.peak_value = initial_capital
        self.daily_pnl: Dict[str, Decimal] = {}  # date -> pnl
        
        logger.info(f"Paper trading initialized with ${initial_capital:,.2f}")
    
    def execute_buy(
        self,
        symbol: str,
        quantity: Decimal,
        price: Decimal,
        stop_loss: Optional[Decimal] = None,
        take_profit: Optional[Decimal] = None,
        strategy: str = "unknown",
        confidence: Decimal = Decimal("0.5")
    ) -> bool:
        """
        Execute simulated buy order.
        
        Args:
            symbol: Token symbol
            quantity: Number of tokens to buy
            price: Current market price
            stop_loss: Stop loss price
            take_profit: Take profit price
            strategy: Strategy name
            confidence: AI confidence score
            
        Returns:
            True if order executed successfully
        """
        # Validate inputs
        if quantity <= 0:
            logger.error(f"Invalid quantity: {quantity}")
            return False
        
        if price <= 0:
            logger.error(f"Invalid price: {price}")
            return False
        
        # Simulate slippage (buy at slightly higher price)
        execution_price = price * (Decimal("1") + self.slippage_rate)
        
        # Calculate costs
        cost = execution_price * quantity
        fees = cost * self.fee_rate
        total_cost = cost + fees
        
        # Check if we have enough cash
        if total_cost > self.cash:
            logger.warning(
                f"Insufficient cash for {symbol}: "
                f"need ${total_cost:.2f}, have ${self.cash:.2f}"
            )
            return False
        
        # Check if we already have a position
        if symbol in self.positions:
            logger.warning(f"Already have position in {symbol}")
            return False
        
        # Validate stop loss and take profit
        if stop_loss and stop_loss >= execution_price:
            logger.error(f"Stop loss {stop_loss} must be below entry {execution_price}")
            return False
        
        if take_profit and take_profit <= execution_price:
            logger.error(f"Take profit {take_profit} must be above entry {execution_price}")
            return False
        
        # Execute order
        self.cash -= total_cost
        self.positions[symbol] = PaperPosition(
            symbol=symbol,
            entry_price=execution_price,
            quantity=quantity,
            entry_time=datetime.now(),
            stop_loss=stop_loss,
            take_profit=take_profit,
            fees_paid=fees,
            strategy=strategy,
            confidence=confidence
        )
        
        logger.info(
            f"BUY {quantity} {symbol} @ ${execution_price:.4f} "
            f"(slippage: {self.slippage_rate:.2%}, fees: ${fees:.2f})"
        )
        return True
    
    def execute_sell(
        self,
        symbol: str,
        current_price: Decimal,
        exit_reason: str = "manual"
    ) -> Optional[PaperTrade]:
        """
        Execute simulated sell order.
        
        Args:
            symbol: Token symbol
            current_price: Current market price
            exit_reason: Reason for exit
            
        Returns:
            Completed trade record
        """
        if symbol not in self.positions:
            logger.warning(f"No position in {symbol} to sell")
            return None
        
        position = self.positions[symbol]
        
        # Simulate slippage (sell at slightly lower price)
        execution_price = current_price * (Decimal("1") - self.slippage_rate)
        
        # Calculate proceeds
        proceeds = execution_price * position.quantity
        fees = proceeds * self.fee_rate
        net_proceeds = proceeds - fees
        
        # Calculate P/L
        pnl = net_proceeds - position.cost_basis
        pnl_pct = (pnl / position.cost_basis) * Decimal("100") if position.cost_basis > 0 else Decimal("0")
        
        # Update cash
        self.cash += net_proceeds
        
        # Record trade
        trade = PaperTrade(
            symbol=symbol,
            entry_price=position.entry_price,
            exit_price=execution_price,
            quantity=position.quantity,
            entry_time=position.entry_time,
            exit_time=datetime.now(),
            pnl=pnl,
            pnl_pct=pnl_pct,
            fees_paid=position.fees_paid + fees,
            exit_reason=exit_reason,
            strategy=position.strategy,
            confidence=position.confidence
        )
        
        self.closed_trades.append(trade)
        
        # Update daily P/L
        today = datetime.now().date().isoformat()
        if today not in self.daily_pnl:
            self.daily_pnl[today] = Decimal("0")
        self.daily_pnl[today] += pnl
        
        # Remove position
        del self.positions[symbol]
        
        logger.info(
            f"SELL {position.quantity} {symbol} @ ${execution_price:.4f} | "
            f"P/L: ${pnl:.2f} ({pnl_pct:+.2f}%) | Reason: {exit_reason}"
        )
        
        return trade
    
    def check_stop_loss_take_profit(
        self,
        symbol: str,
        current_price: Decimal
    ) -> Optional[str]:
        """
        Check if stop-loss or take-profit triggered.
        
        Returns:
            Exit reason if triggered, None otherwise
        """
        if symbol not in self.positions:
            return None
        
        position = self.positions[symbol]
        
        # Check stop loss
        if position.stop_loss and current_price <= position.stop_loss:
            return "stop_loss"
        
        # Check take profit
        if position.take_profit and current_price >= position.take_profit:
            return "take_profit"
        
        return None
    
    def update_positions(
        self,
        market_prices: Dict[str, Decimal]
    ) -> List[PaperTrade]:
        """
        Update all positions with current prices and check for exits.
        
        Args:
            market_prices: Dict of symbol -> current price
            
        Returns:
            List of trades that were closed
        """
        closed_trades = []
        
        for symbol, position in list(self.positions.items()):
            if symbol not in market_prices:
                logger.warning(f"No price data for {symbol}")
                continue
            
            current_price = market_prices[symbol]
            exit_reason = self.check_stop_loss_take_profit(symbol, current_price)
            
            if exit_reason:
                trade = self.execute_sell(symbol, current_price, exit_reason=exit_reason)
                if trade:
                    closed_trades.append(trade)
        
        # Update peak value
        current_value = self.portfolio_value(market_prices)
        self.peak_value = max(self.peak_value, current_value)
        
        return closed_trades
    
    def portfolio_value(self, market_prices: Dict[str, Decimal]) -> Decimal:
        """Calculate total portfolio value (cash + positions)."""
        position_value = sum(
            pos.current_value(market_prices.get(symbol, Decimal("0")))
            for symbol, pos in self.positions.items()
        )
        return self.cash + position_value
    
    @property
    def total_pnl(self) -> Decimal:
        """Calculate total realized P/L."""
        return sum(trade.pnl for trade in self.closed_trades)
    
    @property
    def total_pnl_pct(self) -> Decimal:
        """Calculate total P/L percentage."""
        if self.initial_capital == 0:
            return Decimal("0")
        return (self.total_pnl / self.initial_capital) * Decimal("100")
    
    def get_performance_metrics(self) -> Dict:
        """
        Calculate comprehensive performance metrics.
        
        Returns:
            Dictionary with performance statistics
        """
        if not self.closed_trades:
            return {
                "error": "No completed trades",
                "cash": float(self.cash),
                "open_positions": len(self.positions)
            }
        
        # Basic metrics
        total_trades = len(self.closed_trades)
        winning_trades = [t for t in self.closed_trades if t.pnl > 0]
        losing_trades = [t for t in self.closed_trades if t.pnl <= 0]
        
        win_rate = len(winning_trades) / total_trades if total_trades > 0 else 0
        
        avg_win = (
            sum(t.pnl for t in winning_trades) / len(winning_trades)
            if winning_trades else Decimal("0")
        )
        avg_loss = (
            sum(abs(t.pnl) for t in losing_trades) / len(losing_trades)
            if losing_trades else Decimal("0")
        )
        
        gross_profit = sum(t.pnl for t in winning_trades)
        gross_loss = sum(abs(t.pnl) for t in losing_trades)
        profit_factor = (
            gross_profit / gross_loss
            if gross_loss > 0 else Decimal("999")
        )
        
        # Time metrics
        runtime_days = (datetime.now() - self.start_time).total_seconds() / 86400
        
        # Max drawdown
        max_drawdown = self._calculate_max_drawdown()
        
        # Sharpe ratio (simplified - assumes daily returns)
        sharpe = self._calculate_sharpe_ratio()
        
        # Average holding period
        avg_holding_hours = (
            sum(t.holding_period_hours for t in self.closed_trades) / total_trades
        )
        
        return {
            "initial_capital": float(self.initial_capital),
            "cash": float(self.cash),
            "total_pnl": float(self.total_pnl),
            "total_pnl_pct": float(self.total_pnl_pct),
            "total_trades": total_trades,
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "win_rate": win_rate,
            "avg_win": float(avg_win),
            "avg_loss": float(avg_loss),
            "profit_factor": float(profit_factor),
            "max_drawdown_pct": float(max_drawdown),
            "sharpe_ratio": sharpe,
            "runtime_days": runtime_days,
            "trades_per_day": total_trades / runtime_days if runtime_days > 0 else 0,
            "avg_holding_hours": avg_holding_hours,
            "open_positions": len(self.positions),
            "total_fees_paid": float(sum(t.fees_paid for t in self.closed_trades))
        }
    
    def _calculate_max_drawdown(self) -> Decimal:
        """Calculate maximum drawdown from peak."""
        peak = self.initial_capital
        max_dd = Decimal("0")
        
        running_value = self.initial_capital
        for trade in self.closed_trades:
            running_value += trade.pnl
            peak = max(peak, running_value)
            
            if peak > 0:
                drawdown = ((peak - running_value) / peak) * Decimal("100")
                max_dd = max(max_dd, drawdown)
        
        return max_dd
    
    def _calculate_sharpe_ratio(self) -> float:
        """Calculate Sharpe ratio from trade returns."""
        if len(self.closed_trades) < 2:
            return 0.0
        
        returns = [float(t.pnl_pct) for t in self.closed_trades]
        avg_return = sum(returns) / len(returns)
        
        variance = sum((r - avg_return) ** 2 for r in returns) / len(returns)
        std_return = variance ** 0.5
        
        sharpe = avg_return / std_return if std_return > 0 else 0.0
        return sharpe
    
    def generate_report(self) -> str:
        """Generate human-readable performance report."""
        metrics = self.get_performance_metrics()
        
        if "error" in metrics:
            return f"No trades to report. Cash: ${metrics['cash']:,.2f}"
        
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║           PAPER TRADING PERFORMANCE REPORT                   ║
╚══════════════════════════════════════════════════════════════╝

📊 CAPITAL
  Initial:           ${metrics['initial_capital']:>12,.2f}
  Current Cash:      ${metrics['cash']:>12,.2f}
  
💰 PROFIT & LOSS
  Total P/L:         ${metrics['total_pnl']:>12,.2f}
  Total Return:       {metrics['total_pnl_pct']:>12,.2f}%
  Max Drawdown:       {metrics['max_drawdown_pct']:>12,.2f}%
  
📈 TRADING STATISTICS
  Total Trades:       {metrics['total_trades']:>12}
  Winners:            {metrics['winning_trades']:>12}
  Losers:             {metrics['losing_trades']:>12}
  Win Rate:           {metrics['win_rate']*100:>12,.1f}%
  
  Average Win:       ${metrics['avg_win']:>12,.2f}
  Average Loss:      ${metrics['avg_loss']:>12,.2f}
  Profit Factor:      {metrics['profit_factor']:>12,.2f}
  
📊 RISK METRICS
  Sharpe Ratio:       {metrics['sharpe_ratio']:>12,.2f}
  
⏱️  TIME METRICS
  Runtime:            {metrics['runtime_days']:>12,.1f} days
  Trades/Day:         {metrics['trades_per_day']:>12,.1f}
  Avg Hold Time:      {metrics['avg_holding_hours']:>12,.1f} hours
  
💸 COSTS
  Total Fees:        ${metrics['total_fees_paid']:>12,.2f}
  
📍 CURRENT STATUS
  Open Positions:     {metrics['open_positions']:>12}

╚══════════════════════════════════════════════════════════════╝
"""
        return report
    
    def get_trade_history(self, limit: int = 10) -> List[Dict]:
        """Get recent trade history."""
        recent_trades = sorted(
            self.closed_trades,
            key=lambda t: t.exit_time,
            reverse=True
        )[:limit]
        
        return [
            {
                "symbol": t.symbol,
                "entry_price": float(t.entry_price),
                "exit_price": float(t.exit_price),
                "quantity": float(t.quantity),
                "pnl": float(t.pnl),
                "pnl_pct": float(t.pnl_pct),
                "exit_reason": t.exit_reason,
                "strategy": t.strategy,
                "confidence": float(t.confidence),
                "holding_hours": t.holding_period_hours
            }
            for t in recent_trades
        ]
