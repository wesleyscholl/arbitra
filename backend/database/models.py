"""
Database Models for Arbitra

SQLAlchemy models for storing trades, positions, signals, and account history.
"""

from datetime import datetime
from decimal import Decimal
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Boolean,
    Text,
    ForeignKey,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class AccountSnapshot(Base):
    """Historical snapshots of account state."""

    __tablename__ = "account_snapshots"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.now, index=True)
    cash = Column(Float, nullable=False)
    equity = Column(Float, nullable=False)
    portfolio_value = Column(Float, nullable=False)
    buying_power = Column(Float, nullable=False)
    realized_pl = Column(Float, default=0.0)
    unrealized_pl = Column(Float, default=0.0)
    total_pl = Column(Float, default=0.0)
    position_count = Column(Integer, default=0)
    trade_count = Column(Integer, default=0)

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "cash": self.cash,
            "equity": self.equity,
            "portfolio_value": self.portfolio_value,
            "buying_power": self.buying_power,
            "realized_pl": self.realized_pl,
            "unrealized_pl": self.unrealized_pl,
            "total_pl": self.total_pl,
            "position_count": self.position_count,
            "trade_count": self.trade_count,
        }


class Trade(Base):
    """Historical trades."""

    __tablename__ = "trades"

    id = Column(Integer, primary_key=True)
    order_id = Column(String(100), unique=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    side = Column(String(10), nullable=False)  # 'buy' or 'sell'
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    commission = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=datetime.now, index=True)
    
    # Optional: Link to position
    position_id = Column(Integer, ForeignKey("positions.id"), nullable=True)
    position = relationship("Position", back_populates="trades")

    # Optional: Link to signal that triggered this trade
    signal_id = Column(Integer, ForeignKey("signals.id"), nullable=True)
    signal = relationship("Signal", back_populates="trade")

    def to_dict(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "symbol": self.symbol,
            "side": self.side,
            "quantity": self.quantity,
            "price": self.price,
            "commission": self.commission,
            "timestamp": self.timestamp.isoformat(),
            "position_id": self.position_id,
            "signal_id": self.signal_id,
        }


class Position(Base):
    """Historical position records."""

    __tablename__ = "positions"

    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False, index=True)
    quantity = Column(Float, nullable=False)
    side = Column(String(10), nullable=False)  # 'long' or 'short'
    entry_price = Column(Float, nullable=False)
    entry_time = Column(DateTime, nullable=False)
    exit_price = Column(Float, nullable=True)
    exit_time = Column(DateTime, nullable=True)
    realized_pl = Column(Float, default=0.0)
    status = Column(String(20), default="open")  # 'open' or 'closed'

    # Related trades
    trades = relationship("Trade", back_populates="position")

    def to_dict(self):
        return {
            "id": self.id,
            "symbol": self.symbol,
            "quantity": self.quantity,
            "side": self.side,
            "entry_price": self.entry_price,
            "entry_time": self.entry_time.isoformat(),
            "exit_price": self.exit_price,
            "exit_time": self.exit_time.isoformat() if self.exit_time else None,
            "realized_pl": self.realized_pl,
            "status": self.status,
        }


class Signal(Base):
    """AI-generated trading signals."""

    __tablename__ = "signals"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.now, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    signal_type = Column(String(10), nullable=False)  # 'buy', 'sell', 'hold'
    confidence = Column(Float, nullable=False)  # 0.0 to 1.0
    strength = Column(Float, nullable=False)  # Signal strength
    
    # Market data at signal time
    price = Column(Float, nullable=False)
    
    # AI model information
    model_name = Column(String(100), nullable=True)
    model_version = Column(String(50), nullable=True)
    
    # Features used for prediction
    features = Column(Text, nullable=True)  # JSON string of features
    
    # Reasoning/explanation
    reasoning = Column(Text, nullable=True)
    
    # Did we act on this signal?
    acted_on = Column(Boolean, default=False)
    action_taken = Column(String(50), nullable=True)  # 'order_placed', 'ignored', etc.
    
    # Related trade (if signal resulted in trade)
    trade = relationship("Signal", back_populates="signal", uselist=False)

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "symbol": self.symbol,
            "signal_type": self.signal_type,
            "confidence": self.confidence,
            "strength": self.strength,
            "price": self.price,
            "model_name": self.model_name,
            "model_version": self.model_version,
            "features": self.features,
            "reasoning": self.reasoning,
            "acted_on": self.acted_on,
            "action_taken": self.action_taken,
        }


class Order(Base):
    """Order history."""

    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    order_id = Column(String(100), unique=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    side = Column(String(10), nullable=False)  # 'buy' or 'sell'
    quantity = Column(Float, nullable=False)
    order_type = Column(String(20), nullable=False)  # 'market' or 'limit'
    limit_price = Column(Float, nullable=True)
    status = Column(String(20), default="pending")  # pending, filled, cancelled
    submitted_at = Column(DateTime, default=datetime.now, index=True)
    filled_at = Column(DateTime, nullable=True)
    filled_price = Column(Float, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    cancellation_reason = Column(Text, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "symbol": self.symbol,
            "side": self.side,
            "quantity": self.quantity,
            "order_type": self.order_type,
            "limit_price": self.limit_price,
            "status": self.status,
            "submitted_at": self.submitted_at.isoformat(),
            "filled_at": self.filled_at.isoformat() if self.filled_at else None,
            "filled_price": self.filled_price,
            "cancelled_at": self.cancelled_at.isoformat()
            if self.cancelled_at
            else None,
            "cancellation_reason": self.cancellation_reason,
        }


class MarketDataSnapshot(Base):
    """Periodic market data snapshots for backtesting/analysis."""

    __tablename__ = "market_data_snapshots"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.now, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    price = Column(Float, nullable=False)
    bid = Column(Float, nullable=True)
    ask = Column(Float, nullable=True)
    volume = Column(Float, nullable=True)
    source = Column(String(50), default="alpaca")  # Data source

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "symbol": self.symbol,
            "price": self.price,
            "bid": self.bid,
            "ask": self.ask,
            "volume": self.volume,
            "source": self.source,
        }


class StrategyPerformance(Base):
    """Track performance of different trading strategies."""

    __tablename__ = "strategy_performance"

    id = Column(Integer, primary_key=True)
    strategy_name = Column(String(100), nullable=False, index=True)
    date = Column(DateTime, default=datetime.now, index=True)
    
    # Performance metrics
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    win_rate = Column(Float, default=0.0)
    
    total_pl = Column(Float, default=0.0)
    avg_win = Column(Float, default=0.0)
    avg_loss = Column(Float, default=0.0)
    profit_factor = Column(Float, default=0.0)
    
    # Risk metrics
    max_drawdown = Column(Float, default=0.0)
    sharpe_ratio = Column(Float, nullable=True)
    
    # Current state
    active = Column(Boolean, default=True)

    def to_dict(self):
        return {
            "id": self.id,
            "strategy_name": self.strategy_name,
            "date": self.date.isoformat(),
            "total_trades": self.total_trades,
            "winning_trades": self.winning_trades,
            "losing_trades": self.losing_trades,
            "win_rate": self.win_rate,
            "total_pl": self.total_pl,
            "avg_win": self.avg_win,
            "avg_loss": self.avg_loss,
            "profit_factor": self.profit_factor,
            "max_drawdown": self.max_drawdown,
            "sharpe_ratio": self.sharpe_ratio,
            "active": self.active,
        }
