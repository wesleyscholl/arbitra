"""
Paper Trading Engine

Simulates trading with virtual positions while using real market data from Alpaca.
Tracks positions, calculates P&L, applies slippage and commission.
"""

from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class Position:
    """Represents a paper trading position."""

    symbol: str
    quantity: Decimal
    entry_price: Decimal
    entry_time: datetime
    side: str  # 'long' or 'short'
    current_price: Decimal = Decimal("0")
    realized_pl: Decimal = Decimal("0")

    @property
    def market_value(self) -> Decimal:
        """Current market value of position."""
        return self.quantity * self.current_price

    @property
    def cost_basis(self) -> Decimal:
        """Original cost of position."""
        return self.quantity * self.entry_price

    @property
    def unrealized_pl(self) -> Decimal:
        """Unrealized profit/loss."""
        if self.side == "long":
            return (self.current_price - self.entry_price) * self.quantity
        else:  # short
            return (self.entry_price - self.current_price) * self.quantity

    @property
    def unrealized_plpc(self) -> Decimal:
        """Unrealized P&L percentage."""
        if self.entry_price == 0:
            return Decimal("0")
        return (self.unrealized_pl / self.cost_basis) * 100

    def to_dict(self) -> Dict:
        """Convert to dict for API responses."""
        return {
            "symbol": self.symbol,
            "quantity": float(self.quantity),
            "side": self.side,
            "entry_price": float(self.entry_price),
            "entry_time": self.entry_time.isoformat(),
            "current_price": float(self.current_price),
            "market_value": float(self.market_value),
            "cost_basis": float(self.cost_basis),
            "unrealized_pl": float(self.unrealized_pl),
            "unrealized_plpc": float(self.unrealized_plpc),
            "realized_pl": float(self.realized_pl),
        }


@dataclass
class Trade:
    """Represents a completed trade."""

    symbol: str
    side: str  # 'buy' or 'sell'
    quantity: Decimal
    price: Decimal
    commission: Decimal
    timestamp: datetime
    order_id: str

    def to_dict(self) -> Dict:
        """Convert to dict for API responses."""
        return {
            "symbol": self.symbol,
            "side": self.side,
            "quantity": float(self.quantity),
            "price": float(self.price),
            "commission": float(self.commission),
            "timestamp": self.timestamp.isoformat(),
            "order_id": self.order_id,
        }


@dataclass
class Order:
    """Represents a pending order."""

    order_id: str
    symbol: str
    side: str  # 'buy' or 'sell'
    quantity: Decimal
    order_type: str  # 'market' or 'limit'
    limit_price: Optional[Decimal] = None
    status: str = "pending"  # pending, filled, cancelled
    submitted_at: datetime = field(default_factory=datetime.now)
    filled_at: Optional[datetime] = None
    filled_price: Optional[Decimal] = None

    def to_dict(self) -> Dict:
        """Convert to dict for API responses."""
        return {
            "order_id": self.order_id,
            "symbol": self.symbol,
            "side": self.side,
            "quantity": float(self.quantity),
            "order_type": self.order_type,
            "limit_price": float(self.limit_price) if self.limit_price else None,
            "status": self.status,
            "submitted_at": self.submitted_at.isoformat(),
            "filled_at": self.filled_at.isoformat() if self.filled_at else None,
            "filled_price": float(self.filled_price) if self.filled_price else None,
        }


class PaperTradingEngine:
    """
    Paper trading engine that tracks virtual positions using real market data.
    """

    def __init__(
        self,
        initial_capital: Decimal = Decimal("100000"),
        enable_slippage: bool = True,
        slippage_bps: Decimal = Decimal("5"),
        enable_commission: bool = True,
        commission_per_share: Decimal = Decimal("0.005"),
    ):
        """
        Initialize paper trading engine.

        Args:
            initial_capital: Starting cash balance
            enable_slippage: Whether to simulate slippage
            slippage_bps: Slippage in basis points (default: 5 = 0.05%)
            enable_commission: Whether to charge commission
            commission_per_share: Commission per share traded
        """
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions: Dict[str, Position] = {}
        self.trades: List[Trade] = []
        self.orders: Dict[str, Order] = {}

        # Settings
        self.enable_slippage = enable_slippage
        self.slippage_bps = slippage_bps
        self.enable_commission = enable_commission
        self.commission_per_share = commission_per_share

        # Tracking
        self.order_counter = 0

        logger.info(
            f"Paper trading engine initialized with ${initial_capital:,.2f}"
        )

    def _generate_order_id(self) -> str:
        """Generate unique order ID."""
        self.order_counter += 1
        return f"PAPER-{datetime.now().strftime('%Y%m%d')}-{self.order_counter:06d}"

    def _calculate_slippage(
        self, price: Decimal, side: str, quantity: Decimal
    ) -> Decimal:
        """
        Calculate slippage for an order.

        Args:
            price: Base price
            side: 'buy' or 'sell'
            quantity: Order quantity

        Returns:
            Adjusted price with slippage
        """
        if not self.enable_slippage:
            return price

        # Slippage increases with order size
        slippage_pct = self.slippage_bps / Decimal("10000")

        if side == "buy":
            # Buys slip up
            return price * (Decimal("1") + slippage_pct)
        else:
            # Sells slip down
            return price * (Decimal("1") - slippage_pct)

    def _calculate_commission(self, quantity: Decimal) -> Decimal:
        """Calculate commission for an order."""
        if not self.enable_commission:
            return Decimal("0")

        return quantity * self.commission_per_share

    def submit_order(
        self,
        symbol: str,
        side: str,
        quantity: Decimal,
        order_type: str = "market",
        limit_price: Optional[Decimal] = None,
    ) -> Dict:
        """
        Submit a paper trading order.

        Args:
            symbol: Stock symbol
            side: 'buy' or 'sell'
            quantity: Number of shares
            order_type: 'market' or 'limit'
            limit_price: Price for limit orders

        Returns:
            Order dict
        """
        order_id = self._generate_order_id()

        order = Order(
            order_id=order_id,
            symbol=symbol,
            side=side,
            quantity=quantity,
            order_type=order_type,
            limit_price=limit_price,
        )

        self.orders[order_id] = order

        logger.info(
            f"Order submitted: {side.upper()} {quantity} {symbol} @ {order_type}"
        )

        return order.to_dict()

    def fill_order(
        self, order_id: str, current_price: Decimal
    ) -> Optional[Dict]:
        """
        Fill a pending order at current price.

        Args:
            order_id: Order ID to fill
            current_price: Current market price

        Returns:
            Trade dict if filled, None if order not found or can't be filled
        """
        if order_id not in self.orders:
            logger.warning(f"Order {order_id} not found")
            return None

        order = self.orders[order_id]

        if order.status != "pending":
            logger.warning(f"Order {order_id} already {order.status}")
            return None

        # Check limit price for limit orders
        if order.order_type == "limit" and order.limit_price:
            if order.side == "buy" and current_price > order.limit_price:
                logger.info(
                    f"Order {order_id} not filled: price ${current_price:.2f} > limit ${order.limit_price:.2f}"
                )
                return None
            elif order.side == "sell" and current_price < order.limit_price:
                logger.info(
                    f"Order {order_id} not filled: price ${current_price:.2f} < limit ${order.limit_price:.2f}"
                )
                return None

        # Apply slippage
        fill_price = self._calculate_slippage(
            current_price, order.side, order.quantity
        )

        # Calculate commission
        commission = self._calculate_commission(order.quantity)

        # Calculate total cost/proceeds
        if order.side == "buy":
            total_cost = (fill_price * order.quantity) + commission

            if total_cost > self.cash:
                logger.warning(
                    f"Insufficient funds for order {order_id}: need ${total_cost:.2f}, have ${self.cash:.2f}"
                )
                order.status = "cancelled"
                return None

            # Deduct cash
            self.cash -= total_cost

            # Add or increase position
            if order.symbol in self.positions:
                pos = self.positions[order.symbol]
                # Update weighted average entry price
                total_quantity = pos.quantity + order.quantity
                pos.entry_price = (
                    (pos.entry_price * pos.quantity)
                    + (fill_price * order.quantity)
                ) / total_quantity
                pos.quantity = total_quantity
            else:
                # New position
                self.positions[order.symbol] = Position(
                    symbol=order.symbol,
                    quantity=order.quantity,
                    entry_price=fill_price,
                    entry_time=datetime.now(),
                    side="long",
                    current_price=current_price,
                )

        else:  # sell
            if order.symbol not in self.positions:
                logger.warning(
                    f"Cannot sell {order.symbol}: no position exists"
                )
                order.status = "cancelled"
                return None

            pos = self.positions[order.symbol]

            if order.quantity > pos.quantity:
                logger.warning(
                    f"Cannot sell {order.quantity} shares of {order.symbol}: only have {pos.quantity}"
                )
                order.status = "cancelled"
                return None

            # Calculate proceeds
            proceeds = (fill_price * order.quantity) - commission

            # Add cash
            self.cash += proceeds

            # Calculate realized P&L
            realized_pl = (fill_price - pos.entry_price) * order.quantity
            pos.realized_pl += realized_pl

            # Reduce or close position
            pos.quantity -= order.quantity

            if pos.quantity == 0:
                # Close position
                del self.positions[order.symbol]
                logger.info(
                    f"Position closed: {order.symbol} (Realized P&L: ${realized_pl:.2f})"
                )
            else:
                logger.info(
                    f"Position reduced: {order.symbol} ({pos.quantity} shares remaining)"
                )

        # Record trade
        trade = Trade(
            symbol=order.symbol,
            side=order.side,
            quantity=order.quantity,
            price=fill_price,
            commission=commission,
            timestamp=datetime.now(),
            order_id=order_id,
        )

        self.trades.append(trade)

        # Update order
        order.status = "filled"
        order.filled_at = datetime.now()
        order.filled_price = fill_price

        logger.info(
            f"Order filled: {order.side.upper()} {order.quantity} {order.symbol} @ ${fill_price:.2f}"
        )

        return trade.to_dict()

    def cancel_order(self, order_id: str) -> bool:
        """Cancel a pending order."""
        if order_id not in self.orders:
            return False

        order = self.orders[order_id]

        if order.status != "pending":
            return False

        order.status = "cancelled"
        logger.info(f"Order cancelled: {order_id}")

        return True

    def update_prices(self, prices: Dict[str, Decimal]):
        """
        Update current prices for all positions.

        Args:
            prices: Dict mapping symbol to current price
        """
        for symbol, position in self.positions.items():
            if symbol in prices:
                position.current_price = prices[symbol]

    def get_account_info(self) -> Dict:
        """Get current account information."""
        total_market_value = sum(
            pos.market_value for pos in self.positions.values()
        )

        equity = self.cash + total_market_value

        unrealized_pl = sum(pos.unrealized_pl for pos in self.positions.values())

        realized_pl = sum(pos.realized_pl for pos in self.positions.values())

        return {
            "cash": float(self.cash),
            "buying_power": float(self.cash),
            "equity": float(equity),
            "portfolio_value": float(equity),
            "initial_capital": float(self.initial_capital),
            "total_pl": float(realized_pl + unrealized_pl),
            "realized_pl": float(realized_pl),
            "unrealized_pl": float(unrealized_pl),
            "total_return": float(
                ((equity - self.initial_capital) / self.initial_capital) * 100
            )
            if self.initial_capital > 0
            else 0,
            "position_count": len(self.positions),
            "trade_count": len(self.trades),
        }

    def get_positions(self) -> List[Dict]:
        """Get all current positions."""
        return [pos.to_dict() for pos in self.positions.values()]

    def get_position(self, symbol: str) -> Optional[Dict]:
        """Get a specific position."""
        if symbol in self.positions:
            return self.positions[symbol].to_dict()
        return None

    def get_trades(self, limit: int = 100) -> List[Dict]:
        """Get recent trades."""
        return [trade.to_dict() for trade in self.trades[-limit:]]

    def get_order(self, order_id: str) -> Optional[Dict]:
        """Get order by ID."""
        if order_id in self.orders:
            return self.orders[order_id].to_dict()
        return None

    def get_all_orders(self, status: Optional[str] = None) -> List[Dict]:
        """
        Get all orders, optionally filtered by status.

        Args:
            status: Filter by status ('pending', 'filled', 'cancelled')
        """
        orders = self.orders.values()

        if status:
            orders = [o for o in orders if o.status == status]

        return [o.to_dict() for o in orders]

    def reset(self):
        """Reset the paper trading engine to initial state."""
        self.cash = self.initial_capital
        self.positions.clear()
        self.trades.clear()
        self.orders.clear()
        self.order_counter = 0

        logger.info("Paper trading engine reset")
