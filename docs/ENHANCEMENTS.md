# Arbitra Enhancement Plan

> Comprehensive enhancements for risk management, AI decision-making, paper trading, and native macOS UI

**Last Updated**: October 8, 2025

---

## 🎯 Overview

This document outlines production-grade enhancements to make Arbitra more robust, safer, and user-friendly:

1. **Risk Module Enhancements** - 15+ new safety features
2. **AI Agent Enhancements** - 12+ intelligence improvements
3. **Paper Trading System** - Full simulation with performance tracking
4. **Native macOS UI** - Swift-based desktop application

---

## 🛡️ Risk Module Enhancements

### 1. Portfolio Rebalancing Logic

**Purpose**: Automatically rebalance when allocations drift from targets

```python
# New file: src/risk/rebalancer.py

class PortfolioRebalancer:
    """Automatic portfolio rebalancing."""
    
    REBALANCE_THRESHOLD = 5.0  # Rebalance if tier drifts >5%
    REBALANCE_COOLDOWN_HOURS = 24  # Min time between rebalances
    
    def check_rebalancing_needed(
        self,
        current_allocations: Dict[AssetTier, Decimal],
        target_allocations: Dict[AssetTier, Decimal]
    ) -> bool:
        """Check if portfolio needs rebalancing."""
        
    def generate_rebalancing_trades(self) -> List[TradeRecommendation]:
        """Generate trades to rebalance portfolio."""
```

**Benefits**:
- Maintains target risk profile
- Prevents allocation drift
- Automatic risk adjustment

---

### 2. Correlation-Based Position Limits

**Purpose**: Prevent highly correlated positions that amplify risk

```python
# Add to src/risk/validators.py

class CorrelationValidator:
    """Validate positions based on correlation."""
    
    MAX_CORRELATION = 0.7  # Don't add positions with >0.7 correlation
    MAX_CORRELATED_EXPOSURE = 15.0  # Max % in correlated assets
    
    def calculate_portfolio_correlation(self) -> Decimal:
        """Calculate weighted portfolio correlation."""
        
    def validate_correlation_risk(
        self,
        new_asset: str,
        existing_positions: List[Position]
    ) -> ValidationResult:
        """Check if new position increases correlation risk."""
```

**Benefits**:
- Reduces systemic risk
- Better diversification
- Prevents "all eggs in one basket"

---

### 3. Time-Based Trading Restrictions

**Purpose**: Avoid trading during low liquidity or maintenance windows

```python
# Add to src/risk/circuit_breaker.py

class TimeBasedRestrictions:
    """Time-based trading rules."""
    
    # UTC times
    RESTRICTED_HOURS = [
        (0, 4),   # 12am-4am UTC (low liquidity)
        (12, 13), # Noon UTC (maintenance window)
    ]
    
    WEEKEND_TRADING_ENABLED = False  # Disable on weekends
    
    def is_trading_allowed_now(self) -> bool:
        """Check if trading is allowed at current time."""
        
    def get_next_trading_window(self) -> datetime:
        """Get next time trading will be allowed."""
```

**Benefits**:
- Avoids low liquidity periods
- Prevents slippage
- Respects maintenance windows

---

### 4. Gradual Position Scaling (DCA Entry)

**Purpose**: Scale into positions over time to reduce timing risk

```python
# New file: src/risk/position_scaler.py

class PositionScaler:
    """Scale into positions gradually."""
    
    DEFAULT_TRANCHES = 3  # Split position into 3 entries
    MIN_TRANCHE_INTERVAL_MINUTES = 15
    
    def create_scaling_plan(
        self,
        total_position_size: Decimal,
        entry_price: Decimal,
        num_tranches: int = 3
    ) -> List[Tranche]:
        """Create plan to scale into position."""
        
    def execute_next_tranche(self, plan: ScalingPlan) -> Optional[Trade]:
        """Execute next tranche if conditions met."""
```

**Benefits**:
- Reduces timing risk
- Better average entry price
- Lower emotional stress

---

### 5. Dynamic Trailing Stops

**Purpose**: Lock in profits while letting winners run

```python
# Add to src/risk/position_sizing.py

class TrailingStopManager:
    """Dynamic trailing stop-loss management."""
    
    def calculate_trailing_stop(
        self,
        entry_price: Decimal,
        current_price: Decimal,
        initial_stop_pct: Decimal = Decimal("5.0"),
        trailing_pct: Decimal = Decimal("3.0")
    ) -> Decimal:
        """Calculate dynamic trailing stop."""
        
    def update_stops_for_portfolio(
        self,
        positions: List[Position]
    ) -> Dict[str, Decimal]:
        """Update trailing stops for all positions."""
```

**Benefits**:
- Locks in profits automatically
- Lets winners run
- Reduces regret from early exits

---

### 6. Maximum Concurrent Positions Limit

**Purpose**: Prevent over-diversification and maintain focus

```python
# Add to src/risk/validators.py

class PositionLimitValidator:
    """Validate position count limits."""
    
    MAX_POSITIONS_TOTAL = 10
    MAX_POSITIONS_PER_TIER = {
        AssetTier.FOUNDATION: 3,
        AssetTier.GROWTH: 5,
        AssetTier.OPPORTUNITY: 5
    }
    
    def can_open_new_position(
        self,
        tier: AssetTier,
        current_positions: List[Position]
    ) -> bool:
        """Check if new position is allowed."""
```

**Benefits**:
- Maintains focus
- Reduces monitoring complexity
- Better position management

---

### 7. Sector Concentration Limits

**Purpose**: Prevent over-allocation to single narrative/sector

```python
# New file: src/risk/sector_limits.py

class SectorLimitManager:
    """Manage sector/narrative concentration."""
    
    MAX_SECTOR_ALLOCATION = 25.0  # Max 25% per sector
    
    SECTORS = [
        "DeFi", "Gaming", "AI", "Memes", "Infrastructure",
        "Privacy", "DePIN", "Social", "NFT", "Layer1"
    ]
    
    def get_sector_exposure(self, sector: str) -> Decimal:
        """Calculate current exposure to sector."""
        
    def validate_sector_limits(
        self,
        new_trade_sector: str,
        new_trade_size: Decimal
    ) -> ValidationResult:
        """Check if trade exceeds sector limits."""
```

**Benefits**:
- True diversification
- Reduces narrative risk
- Better risk-adjusted returns

---

### 8. Slippage Protection

**Purpose**: Cancel trades if expected slippage too high

```python
# New file: src/risk/slippage_guard.py

class SlippageGuard:
    """Protect against excessive slippage."""
    
    MAX_SLIPPAGE_PCT = {
        AssetTier.FOUNDATION: Decimal("0.5"),
        AssetTier.GROWTH: Decimal("1.0"),
        AssetTier.OPPORTUNITY: Decimal("2.0")
    }
    
    def estimate_slippage(
        self,
        token: str,
        trade_size_usd: Decimal,
        order_book: OrderBook
    ) -> Decimal:
        """Estimate slippage for trade."""
        
    def should_cancel_trade(
        self,
        estimated_slippage: Decimal,
        tier: AssetTier
    ) -> bool:
        """Check if slippage exceeds threshold."""
```

**Benefits**:
- Prevents expensive trades
- Ensures execution quality
- Protects from manipulation

---

### 9. Win Rate Floor

**Purpose**: Don't trade strategies below minimum performance

```python
# Add to src/risk/validators.py

class StrategyPerformanceValidator:
    """Validate strategy performance thresholds."""
    
    MIN_WIN_RATE = Decimal("0.45")  # 45% minimum
    MIN_TRADES_FOR_VALIDATION = 20
    MIN_PROFIT_FACTOR = Decimal("1.2")  # Gross profit / gross loss
    
    def validate_strategy_performance(
        self,
        strategy: Strategy,
        lookback_days: int = 30
    ) -> ValidationResult:
        """Check if strategy meets minimum standards."""
```

**Benefits**:
- Prevents trading bad strategies
- Forces strategy improvement
- Better long-term returns

---

### 10. Recovery Mode After Losses

**Purpose**: Reduce position sizing after losses to preserve capital

```python
# New file: src/risk/recovery_mode.py

class RecoveryMode:
    """Reduce risk after losses."""
    
    RECOVERY_TRIGGER_LOSS = Decimal("3.0")  # Enter recovery at 3% loss
    POSITION_SIZE_REDUCTION = Decimal("0.5")  # Reduce to 50% size
    RECOVERY_EXIT_PROFIT = Decimal("1.0")  # Exit recovery at 1% profit
    
    def check_recovery_mode_trigger(
        self,
        daily_pnl_pct: Decimal
    ) -> bool:
        """Check if should enter recovery mode."""
        
    def get_recovery_mode_multiplier(self) -> Decimal:
        """Get position size multiplier for recovery mode."""
```

**Benefits**:
- Preserves capital after losses
- Reduces psychological stress
- Prevents revenge trading

---

## 🤖 AI Agent Enhancements

### 1. Multi-Model Consensus

**Purpose**: Require agreement between models for high-confidence trades

```python
# Add to src/ai/agent.py

class ConsensusAnalyzer:
    """Require multi-model agreement."""
    
    MIN_AGREEMENT_FOR_HIGH_CONFIDENCE = 2  # Both models agree
    CONSENSUS_CONFIDENCE_BONUS = Decimal("0.1")
    
    async def get_consensus_analysis(
        self,
        request: AnalysisRequest
    ) -> ConsensusResult:
        """Get analysis from multiple models and compare."""
        
        # Run both flash and pro models
        flash_result = await self.analyze_trade(request, use_deep_analysis=False)
        pro_result = await self.analyze_trade(request, use_deep_analysis=True)
        
        # Check agreement
        agreement_score = self._calculate_agreement(flash_result, pro_result)
        
        # Return consensus or conflict
        return self._build_consensus(flash_result, pro_result, agreement_score)
```

**Benefits**:
- Higher quality decisions
- Catches AI errors
- More reliable recommendations

---

### 2. Confidence Decay (Time-Based)

**Purpose**: Lower confidence for stale analysis

```python
# Add to src/ai/confidence.py

class ConfidenceDecay:
    """Reduce confidence over time."""
    
    DECAY_HALF_LIFE_MINUTES = 30  # Confidence halves every 30 min
    MIN_CONFIDENCE_FLOOR = Decimal("0.3")
    
    def apply_time_decay(
        self,
        original_confidence: Decimal,
        analysis_timestamp: datetime
    ) -> Decimal:
        """Apply exponential decay to confidence."""
        
        age_minutes = (datetime.now() - analysis_timestamp).total_seconds() / 60
        decay_factor = Decimal(2) ** (-Decimal(age_minutes) / self.DECAY_HALF_LIFE_MINUTES)
        
        decayed = original_confidence * decay_factor
        return max(decayed, self.MIN_CONFIDENCE_FLOOR)
```

**Benefits**:
- Prevents trading on stale data
- Encourages fresh analysis
- Reduces timing risk

---

### 3. Hallucination Detection

**Purpose**: Validate AI outputs for logical consistency

```python
# New file: src/ai/validators.py

class AIOutputValidator:
    """Detect and reject AI hallucinations."""
    
    def validate_analysis(self, analysis: AnalysisResponse) -> ValidationResult:
        """Check for logical inconsistencies."""
        
        errors = []
        
        # Check 1: Stop loss must be below entry
        if analysis.stop_loss and analysis.entry_price:
            if analysis.stop_loss >= analysis.entry_price:
                errors.append("Stop loss above entry price")
        
        # Check 2: Take profit must be above entry
        if analysis.take_profit and analysis.entry_price:
            if analysis.take_profit <= analysis.entry_price:
                errors.append("Take profit below entry price")
        
        # Check 3: Risk/reward ratio must be reasonable
        if analysis.entry_price and analysis.stop_loss and analysis.take_profit:
            rr = self._calculate_risk_reward(...)
            if rr < Decimal("1.0") or rr > Decimal("20.0"):
                errors.append(f"Unrealistic risk/reward: {rr}")
        
        # Check 4: Confidence must match reasoning
        sentiment_in_reasoning = self._analyze_sentiment(analysis.reasoning)
        if analysis.action == TradeAction.BUY and sentiment_in_reasoning < 0:
            errors.append("Reasoning contradicts BUY action")
        
        return ValidationResult(is_valid=len(errors) == 0, errors=errors)
```

**Benefits**:
- Catches AI errors
- Prevents bad trades
- Improves reliability

---

### 4. Market Regime Detection

**Purpose**: Adjust strategies based on market conditions

```python
# New file: src/ai/market_regime.py

class MarketRegimeDetector:
    """Detect bull/bear/sideways markets."""
    
    class Regime(Enum):
        BULL = "bull"
        BEAR = "bear"
        SIDEWAYS = "sideways"
        VOLATILE = "volatile"
    
    def detect_regime(
        self,
        price_history: List[Decimal],
        volume_history: List[Decimal]
    ) -> Regime:
        """Detect current market regime."""
        
    def adjust_strategy_for_regime(
        self,
        base_analysis: AnalysisResponse,
        regime: Regime
    ) -> AnalysisResponse:
        """Modify analysis based on market regime."""
        
        # Example: Reduce confidence in bear markets
        if regime == Regime.BEAR:
            base_analysis.confidence *= Decimal("0.8")
        elif regime == Regime.VOLATILE:
            base_analysis.confidence *= Decimal("0.7")
```

**Benefits**:
- Adapts to market conditions
- Better risk adjustment
- Higher win rate

---

### 5. Event Awareness System

**Purpose**: Factor in upcoming events, unlocks, announcements

```python
# New file: src/ai/event_tracker.py

class EventTracker:
    """Track and factor in upcoming events."""
    
    @dataclass
    class Event:
        token: str
        event_type: str  # "unlock", "upgrade", "partnership", etc.
        impact: str  # "positive", "negative", "neutral"
        timestamp: datetime
        confidence: Decimal
    
    def get_upcoming_events(self, token: str, days_ahead: int = 7) -> List[Event]:
        """Get upcoming events for token."""
        
    def adjust_confidence_for_events(
        self,
        base_confidence: Decimal,
        events: List[Event]
    ) -> Decimal:
        """Adjust confidence based on upcoming events."""
        
        # Example: Reduce confidence before major unlock
        for event in events:
            if event.event_type == "unlock" and event.impact == "negative":
                base_confidence *= Decimal("0.7")
        
        return base_confidence
```

**Benefits**:
- Avoids trading before negative events
- Captures positive catalysts
- Better timing

---

### 6. Liquidity-Adjusted Targets

**Purpose**: Scale targets based on available liquidity

```python
# Add to src/ai/agent.py

def adjust_targets_for_liquidity(
    self,
    analysis: AnalysisResponse,
    available_liquidity: Decimal,
    position_size: Decimal
) -> AnalysisResponse:
    """Adjust take-profit based on liquidity."""
    
    # If position is large relative to liquidity, reduce targets
    position_to_liquidity_ratio = position_size / available_liquidity
    
    if position_to_liquidity_ratio > Decimal("0.05"):  # >5% of liquidity
        # Scale down take-profit to ensure we can exit
        reduction_factor = Decimal("1.0") - (position_to_liquidity_ratio * Decimal("0.5"))
        
        if analysis.take_profit and analysis.entry_price:
            profit_range = analysis.take_profit - analysis.entry_price
            adjusted_profit_range = profit_range * reduction_factor
            analysis.take_profit = analysis.entry_price + adjusted_profit_range
    
    return analysis
```

**Benefits**:
- Ensures we can exit positions
- Prevents unrealistic targets
- Better execution

---

### 7. Performance-Based Model Selection

**Purpose**: Choose model based on recent accuracy

```python
# Add to src/ai/agent.py

class AdaptiveModelSelector:
    """Choose model based on recent performance."""
    
    def __init__(self):
        self.flash_recent_accuracy = Decimal("0.7")
        self.pro_recent_accuracy = Decimal("0.7")
        self.lookback_trades = 20
    
    def select_optimal_model(
        self,
        request: AnalysisRequest
    ) -> str:
        """Choose flash or pro based on recent accuracy."""
        
        # Update accuracies
        self._update_model_accuracies()
        
        # For high-stakes trades, use more accurate model
        if request.tier == AssetTier.FOUNDATION:
            return "pro" if self.pro_recent_accuracy > self.flash_recent_accuracy else "flash"
        
        # For opportunity trades, speed matters more
        elif request.tier == AssetTier.OPPORTUNITY:
            # Use flash unless pro is significantly better
            if self.pro_recent_accuracy > self.flash_recent_accuracy + Decimal("0.1"):
                return "pro"
            return "flash"
        
        # Default: use flash for speed
        return "flash"
```

**Benefits**:
- Optimizes for accuracy
- Adapts to model performance
- Better resource usage

---

### 8. Sanity Check Layer

**Purpose**: Catch obviously bad recommendations

```python
# Add to src/ai/validators.py

class SanityChecker:
    """Catch obviously bad AI recommendations."""
    
    MAX_REASONABLE_GAIN_MULTIPLIER = Decimal("3.0")  # 3x max
    MIN_REASONABLE_STOP_LOSS = Decimal("2.0")  # 2% min
    
    def check_recommendation_sanity(
        self,
        analysis: AnalysisResponse
    ) -> ValidationResult:
        """Check for obviously unrealistic recommendations."""
        
        warnings = []
        
        # Check for unrealistic targets (e.g., 1000x)
        if analysis.take_profit and analysis.entry_price:
            gain_multiplier = analysis.take_profit / analysis.entry_price
            if gain_multiplier > self.MAX_REASONABLE_GAIN_MULTIPLIER:
                warnings.append(f"Unrealistic {gain_multiplier:.1f}x target")
        
        # Check for too-tight stop loss
        if analysis.stop_loss and analysis.entry_price:
            stop_pct = ((analysis.entry_price - analysis.stop_loss) / analysis.entry_price) * 100
            if stop_pct < self.MIN_REASONABLE_STOP_LOSS:
                warnings.append(f"Stop loss too tight: {stop_pct:.1f}%")
        
        # Check for contradictory risk factors
        if analysis.action == TradeAction.BUY:
            negative_words = sum(1 for factor in analysis.risk_factors if factor.lower() in ["scam", "rug", "honeypot"])
            if negative_words > 0:
                warnings.append("BUY action despite severe risk factors")
        
        return ValidationResult(
            is_valid=len(warnings) == 0,
            warnings=warnings
        )
```

**Benefits**:
- Last line of defense
- Prevents catastrophic errors
- Protects capital

---

## 📊 Paper Trading System

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                Paper Trading System                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐         ┌──────────────┐             │
│  │  Real Market │────────>│   Simulated  │             │
│  │     Data     │         │   Execution  │             │
│  └──────────────┘         └──────────────┘             │
│         │                        │                     │
│         │                        ↓                     │
│         │                 ┌──────────────┐             │
│         └────────────────>│  Portfolio   │             │
│                          │   Simulator   │             │
│                          └──────────────┘             │
│                                 │                     │
│                                 ↓                     │
│                          ┌──────────────┐             │
│                          │ Performance  │             │
│                          │   Tracking   │             │
│                          └──────────────┘             │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Implementation

```python
# New file: src/execution/paper_trading.py

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
        # Simulate slippage (buy at slightly higher price)
        execution_price = price * (Decimal("1") + self.slippage_rate)
        
        # Calculate costs
        cost = execution_price * quantity
        fees = cost * self.fee_rate
        total_cost = cost + fees
        
        # Check if we have enough cash
        if total_cost > self.cash:
            logger.warning(f"Insufficient cash for {symbol}: need ${total_cost:.2f}, have ${self.cash:.2f}")
            return False
        
        # Check if we already have a position
        if symbol in self.positions:
            logger.warning(f"Already have position in {symbol}")
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
            fees_paid=fees
        )
        
        logger.info(f"BUY {quantity} {symbol} @ ${execution_price:.4f} (slippage: {self.slippage_rate:.2%}, fees: ${fees:.2f})")
        return True
    
    def execute_sell(
        self,
        symbol: str,
        current_price: Decimal,
        exit_reason: str = "manual",
        strategy: str = "unknown",
        confidence: Decimal = Decimal("0.5")
    ) -> Optional[PaperTrade]:
        """
        Execute simulated sell order.
        
        Args:
            symbol: Token symbol
            current_price: Current market price
            exit_reason: Reason for exit
            strategy: Strategy name
            confidence: AI confidence score
            
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
        pnl_pct = (pnl / position.cost_basis) * Decimal("100")
        
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
            strategy=strategy,
            confidence=confidence
        )
        
        self.closed_trades.append(trade)
        del self.positions[symbol]
        
        logger.info(f"SELL {position.quantity} {symbol} @ ${execution_price:.4f} | P/L: ${pnl:.2f} ({pnl_pct:+.2f}%) | Reason: {exit_reason}")
        return trade
    
    def check_stop_loss_take_profit(self, symbol: str, current_price: Decimal) -> Optional[str]:
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
    
    def update_positions(self, market_prices: Dict[str, Decimal]) -> List[PaperTrade]:
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
                continue
            
            current_price = market_prices[symbol]
            exit_reason = self.check_stop_loss_take_profit(symbol, current_price)
            
            if exit_reason:
                trade = self.execute_sell(symbol, current_price, exit_reason=exit_reason)
                if trade:
                    closed_trades.append(trade)
        
        return closed_trades
    
    @property
    def portfolio_value(self) -> Decimal:
        """Calculate total portfolio value (cash + positions)."""
        return self.cash + sum(
            pos.current_value(Decimal("0"))  # Would use real prices
            for pos in self.positions.values()
        )
    
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
                "portfolio_value": float(self.portfolio_value),
                "cash": float(self.cash),
                "open_positions": len(self.positions)
            }
        
        # Basic metrics
        total_trades = len(self.closed_trades)
        winning_trades = [t for t in self.closed_trades if t.pnl > 0]
        losing_trades = [t for t in self.closed_trades if t.pnl <= 0]
        
        win_rate = len(winning_trades) / total_trades if total_trades > 0 else 0
        
        avg_win = sum(t.pnl for t in winning_trades) / len(winning_trades) if winning_trades else Decimal("0")
        avg_loss = sum(abs(t.pnl) for t in losing_trades) / len(losing_trades) if losing_trades else Decimal("0")
        
        profit_factor = sum(t.pnl for t in winning_trades) / sum(abs(t.pnl) for t in losing_trades) if losing_trades else Decimal("999")
        
        # Time metrics
        runtime_days = (datetime.now() - self.start_time).total_seconds() / 86400
        
        # Return metrics
        total_return_pct = self.total_pnl_pct
        
        # Max drawdown
        peak = self.initial_capital
        max_drawdown = Decimal("0")
        
        running_value = self.initial_capital
        for trade in self.closed_trades:
            running_value += trade.pnl
            peak = max(peak, running_value)
            drawdown = ((peak - running_value) / peak) * Decimal("100")
            max_drawdown = max(max_drawdown, drawdown)
        
        # Sharpe ratio (simplified)
        if self.closed_trades:
            returns = [float(t.pnl_pct) for t in self.closed_trades]
            avg_return = sum(returns) / len(returns)
            std_return = (sum((r - avg_return) ** 2 for r in returns) / len(returns)) ** 0.5
            sharpe = avg_return / std_return if std_return > 0 else 0
        else:
            sharpe = 0
        
        return {
            "portfolio_value": float(self.portfolio_value),
            "initial_capital": float(self.initial_capital),
            "cash": float(self.cash),
            "total_pnl": float(self.total_pnl),
            "total_pnl_pct": float(total_return_pct),
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
            "open_positions": len(self.positions),
            "total_fees_paid": float(sum(t.fees_paid for t in self.closed_trades))
        }
    
    def generate_report(self) -> str:
        """Generate human-readable performance report."""
        metrics = self.get_performance_metrics()
        
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║           PAPER TRADING PERFORMANCE REPORT                   ║
╚══════════════════════════════════════════════════════════════╝

📊 PORTFOLIO SUMMARY
  Initial Capital:    ${metrics['initial_capital']:>12,.2f}
  Current Value:      ${metrics['portfolio_value']:>12,.2f}
  Cash:              ${metrics['cash']:>12,.2f}
  Open Positions:     {metrics['open_positions']:>12}
  
💰 PROFIT & LOSS
  Total P/L:         ${metrics['total_pnl']:>12,.2f}
  Total Return:       {metrics['total_pnl_pct']:>12,.2f}%
  Max Drawdown:       {metrics['max_drawdown_pct']:>12,.2f}%
  
📈 TRADING STATISTICS
  Total Trades:       {metrics['total_trades']:>12}
  Winning Trades:     {metrics['winning_trades']:>12}
  Losing Trades:      {metrics['losing_trades']:>12}
  Win Rate:           {metrics['win_rate']*100:>12,.1f}%
  
  Average Win:       ${metrics['avg_win']:>12,.2f}
  Average Loss:      ${metrics['avg_loss']:>12,.2f}
  Profit Factor:      {metrics['profit_factor']:>12,.2f}
  
📊 RISK METRICS
  Sharpe Ratio:       {metrics['sharpe_ratio']:>12,.2f}
  
⏱️  TIME METRICS
  Runtime:            {metrics['runtime_days']:>12,.1f} days
  Trades/Day:         {metrics['trades_per_day']:>12,.1f}
  
💸 FEES
  Total Fees:        ${metrics['total_fees_paid']:>12,.2f}

╚══════════════════════════════════════════════════════════════╝
"""
        return report
```

---

## 🖥️ macOS Swift UI Application

### Architecture

```
ArbitraApp/
├── ArbitraApp.swift                 # App entry point
├── Models/
│   ├── Trade.swift                  # Trade data model
│   ├── Position.swift               # Position data model
│   └── Portfolio.swift              # Portfolio state
├── ViewModels/
│   ├── DashboardViewModel.swift     # Dashboard logic
│   ├── PositionsViewModel.swift     # Positions management
│   └── PerformanceViewModel.swift   # Analytics
├── Views/
│   ├── DashboardView.swift          # Main dashboard
│   ├── PositionsView.swift          # Active positions
│   ├── HistoryView.swift            # Trade history
│   ├── SettingsView.swift           # Configuration
│   └── Components/
│       ├── PortfolioCard.swift      # Portfolio summary
│       ├── PositionRow.swift        # Position item
│       └── PerformanceChart.swift   # Charts
├── Services/
│   ├── APIService.swift             # Backend API
│   ├── WebSocketService.swift      # Real-time updates
│   └── NotificationService.swift   # Alerts
└── Utils/
    ├── Formatters.swift             # Number/date formatting
    └── Constants.swift              # App constants
```

### Sample Implementation

```swift
// ArbitraApp.swift
import SwiftUI

@main
struct ArbitraApp: App {
    @StateObject private var portfolioState = PortfolioState()
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(portfolioState)
                .frame(minWidth: 1200, minHeight: 800)
        }
        .commands {
            CommandGroup(replacing: .appInfo) {
                Button("About Arbitra") {
                    NSApplication.shared.orderFrontStandardAboutPanel()
                }
            }
        }
    }
}

// Models/Portfolio.swift
import Foundation

struct Portfolio: Codable {
    let totalValue: Decimal
    let cash: Decimal
    let positions: [Position]
    let dailyPnL: Decimal
    let dailyPnLPct: Decimal
    let totalPnL: Decimal
    let totalPnLPct: Decimal
}

struct Position: Codable, Identifiable {
    let id: String
    let symbol: String
    let quantity: Decimal
    let entryPrice: Decimal
    let currentPrice: Decimal
    let unrealizedPnL: Decimal
    let unrealizedPnLPct: Decimal
    let stopLoss: Decimal?
    let takeProfit: Decimal?
    let tier: String
}

// Views/DashboardView.swift
import SwiftUI
import Charts

struct DashboardView: View {
    @EnvironmentObject var portfolioState: PortfolioState
    @StateObject private var viewModel = DashboardViewModel()
    
    var body: some View {
        NavigationSplitView {
            // Sidebar
            List {
                NavigationLink("Dashboard", destination: DashboardContent())
                NavigationLink("Positions", destination: PositionsView())
                NavigationLink("History", destination: HistoryView())
                NavigationLink("Performance", destination: PerformanceView())
                NavigationLink("Settings", destination: SettingsView())
            }
            .navigationTitle("Arbitra")
        } detail: {
            DashboardContent()
        }
    }
}

struct DashboardContent: View {
    @EnvironmentObject var portfolioState: PortfolioState
    
    var body: some View {
        ScrollView {
            VStack(spacing: 20) {
                // Portfolio Summary
                HStack(spacing: 20) {
                    PortfolioCard(
                        title: "Total Value",
                        value: portfolioState.portfolio?.totalValue ?? 0,
                        format: .currency
                    )
                    
                    PortfolioCard(
                        title: "Daily P/L",
                        value: portfolioState.portfolio?.dailyPnL ?? 0,
                        format: .currency,
                        changePercent: portfolioState.portfolio?.dailyPnLPct
                    )
                    
                    PortfolioCard(
                        title: "Total P/L",
                        value: portfolioState.portfolio?.totalPnL ?? 0,
                        format: .currency,
                        changePercent: portfolioState.portfolio?.totalPnLPct
                    )
                }
                
                // Chart
                PerformanceChart(data: portfolioState.performanceHistory)
                    .frame(height: 300)
                
                // Active Positions
                PositionsList(positions: portfolioState.portfolio?.positions ?? [])
                
                // Recent Trades
                RecentTradesList(trades: portfolioState.recentTrades)
            }
            .padding()
        }
        .navigationTitle("Dashboard")
        .toolbar {
            ToolbarItem {
                Button(action: viewModel.refreshData) {
                    Image(systemName: "arrow.clockwise")
                }
            }
            
            ToolbarItem {
                HStack {
                    Circle()
                        .fill(viewModel.isConnected ? Color.green : Color.red)
                        .frame(width: 8, height: 8)
                    Text(viewModel.isConnected ? "Connected" : "Disconnected")
                        .font(.caption)
                }
            }
        }
    }
}

// Components/PortfolioCard.swift
struct PortfolioCard: View {
    let title: String
    let value: Decimal
    let format: ValueFormat
    var changePercent: Decimal?
    
    enum ValueFormat {
        case currency
        case percent
        case number
    }
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(title)
                .font(.caption)
                .foregroundColor(.secondary)
            
            HStack(alignment: .firstTextBaseline) {
                Text(formattedValue)
                    .font(.title)
                    .fontWeight(.bold)
                
                if let change = changePercent {
                    Text(String(format: "%+.2f%%", Double(truncating: change as NSNumber)))
                        .font(.subheadline)
                        .foregroundColor(change >= 0 ? .green : .red)
                }
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background(Color(.windowBackgroundColor))
        .cornerRadius(12)
    }
    
    private var formattedValue: String {
        switch format {
        case .currency:
            return String(format: "$%.2f", Double(truncating: value as NSNumber))
        case .percent:
            return String(format: "%.2f%%", Double(truncating: value as NSNumber))
        case .number:
            return String(format: "%.2f", Double(truncating: value as NSNumber))
        }
    }
}

// Services/APIService.swift
import Foundation

class APIService {
    static let shared = APIService()
    
    private let baseURL = "http://localhost:8000/api"
    
    func fetchPortfolio() async throws -> Portfolio {
        let url = URL(string: "\(baseURL)/portfolio")!
        let (data, _) = try await URLSession.shared.data(from: url)
        return try JSONDecoder().decode(Portfolio.self, from: data)
    }
    
    func executeTrade(symbol: String, action: String, quantity: Decimal) async throws {
        let url = URL(string: "\(baseURL)/trades")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let body = [
            "symbol": symbol,
            "action": action,
            "quantity": String(describing: quantity)
        ]
        request.httpBody = try JSONEncoder().encode(body)
        
        let (_, response) = try await URLSession.shared.data(for: request)
        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 200 else {
            throw APIError.requestFailed
        }
    }
}

enum APIError: Error {
    case requestFailed
    case invalidResponse
    case decodingError
}
```

### Key Features

1. **Real-Time Updates**: WebSocket connection for live portfolio updates
2. **Interactive Charts**: SwiftUI Charts for performance visualization
3. **Native macOS Design**: Follows Apple Human Interface Guidelines
4. **Keyboard Shortcuts**: Quick actions for power users
5. **Notifications**: System notifications for important events
6. **Dark Mode Support**: Full dark mode implementation
7. **Performance**: Optimized for smooth 60fps experience

---

## 📋 Implementation Priority

### Phase 1: Critical Safety (Week 1)
1. ✅ Correlation-based limits
2. ✅ Sanity checks
3. ✅ Hallucination detection
4. ✅ Recovery mode

### Phase 2: Paper Trading (Week 2)
1. ✅ Paper trading engine
2. ✅ Performance tracking
3. ✅ Validation against live data
4. ✅ Report generation

### Phase 3: Advanced Risk (Week 3)
1. Portfolio rebalancing
2. Trailing stops
3. Time restrictions
4. Sector limits

### Phase 4: AI Improvements (Week 4)
1. Multi-model consensus
2. Market regime detection
3. Event awareness
4. Confidence decay

### Phase 5: macOS UI (Week 5-6)
1. Basic UI skeleton
2. Real-time data integration
3. Charts and visualizations
4. Settings and configuration

---

## 🎯 Success Metrics

### Paper Trading Validation
- **Minimum Runtime**: 2 weeks continuous operation
- **Target Win Rate**: >55%
- **Max Drawdown**: <10%
- **Sharpe Ratio**: >1.2
- **System Uptime**: >99%

### UI Usability
- **Response Time**: <100ms for all interactions
- **Crash Rate**: <0.1%
- **User Satisfaction**: 4.5+ / 5.0

---

## 📚 Next Steps

1. **Review this plan** - Prioritize features
2. **Start with Critical Safety** - Implement high-priority risk features
3. **Build Paper Trading** - Validate strategies before live trading
4. **Develop UI** - Create great user experience
5. **Iterate** - Continuously improve based on results

---

**Remember**: The goal is not to trade perfectly, but to survive long enough to improve. These enhancements prioritize capital preservation above all else.
