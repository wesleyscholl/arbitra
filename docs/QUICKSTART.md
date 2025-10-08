# Arbitra Quick Start Guide

## Installation

### 1. Prerequisites

Ensure you have:
- Python 3.11 or higher
- pip and virtualenv
- **Option A**: Podman and podman-compose (recommended)
- **Option B**: Native PostgreSQL 15+ and Redis 7+ (if you can't use containers)

### 2. Clone and Setup

#### Option A: Automatic Install (Recommended)
```bash
# Navigate to project
cd arbitra

# Run the install script (creates venv, installs everything)
./install.sh
```

#### Option B: Manual Install
```bash
# Navigate to project
cd arbitra

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Install project in editable mode (IMPORTANT!)
pip install -e .
```

**Important**: The `pip install -e .` step is crucial - it makes the `src` package importable.

### 3. Infrastructure Setup (Optional for Phase 1)

**Note**: For Phase 1 (Risk Module), you don't need any infrastructure. Unit tests run without databases.

#### Option A: Using Podman (when you need databases later)

```bash
# Install podman and podman-compose
# macOS:
brew install podman podman-compose

# Linux:
# See https://podman.io/getting-started/installation

# Initialize podman machine (macOS only)
podman machine init
podman machine start

# Start services
podman-compose up -d

# Verify services are running
podman-compose ps
```

#### Option B: Local Installation (no containers)

```bash
# macOS with Homebrew
brew install postgresql@15 redis
brew services start postgresql@15
brew services start redis

# Create database
createdb arbitra

# Verify services
psql -d arbitra -c "SELECT version();"
redis-cli ping
```

### 4. Run Tests (No Infrastructure Needed)

```bash
# Run all tests with coverage
pytest tests/ -v --cov=src/risk --cov-report=term-missing

# Run only risk module tests
pytest tests/risk/ -v

# Run with hypothesis property tests
pytest tests/risk/test_position_sizing.py -v --hypothesis-show-statistics

# Generate HTML coverage report
pytest tests/ --cov=src --cov-report=html
# Open htmlcov/index.html in browser
```

### 4. Verify Risk Module

The risk module should have 100% test coverage. Check:

```bash
# Run coverage check
pytest tests/risk/ --cov=src/risk --cov-report=term --cov-fail-under=95

# If coverage is below 95%, tests will fail
```

## Current Status

### ✅ Completed (Phase 1)

- [x] Project structure
- [x] Risk management module
  - [x] Position sizing (Kelly Criterion)
  - [x] Circuit breakers
  - [x] Tier-based allocation
- [x] Comprehensive test suite
  - [x] Unit tests
  - [x] Property-based tests (Hypothesis)
  - [x] Integration tests
- [x] Configuration system

### 🚧 In Progress

- [ ] Portfolio risk manager
- [ ] Trade validators
- [ ] Risk manager orchestrator

### 📋 Next Steps (Phase 2)

1. Complete remaining risk module components
2. Set up database infrastructure
3. Implement data feeds
4. Build AI agent core
5. Add foundation strategies

## Testing Philosophy

Our testing approach ensures the risk module is **bulletproof**:

### 1. Unit Tests
Every function tested independently with known inputs/outputs.

### 2. Property-Based Tests
Using Hypothesis to test with random inputs across ranges:
- Position size never exceeds portfolio
- Kelly criterion always returns 0-1
- Risk-reward ratios always positive

### 3. Edge Case Tests
- Zero values
- Negative values
- Exact threshold boundaries
- Extreme market conditions

### 4. Integration Tests
- Multiple breakers working together
- Complete trading flows
- Recovery scenarios

## Risk Module Usage Examples

### Position Sizing

```python
from decimal import Decimal
from src.risk.position_sizing import PositionSizer, PositionSizeParams, AssetTier

# Create parameters
params = PositionSizeParams(
    portfolio_value=Decimal("10000"),
    win_rate=Decimal("0.60"),       # 60% historical win rate
    avg_win=Decimal("100"),         # Avg $100 wins
    avg_loss=Decimal("50"),         # Avg $50 losses
    confidence=Decimal("0.80"),     # AI 80% confident
    asset_tier=AssetTier.FOUNDATION # BTC/ETH/SOL
)

# Calculate position size
sizer = PositionSizer(params)
position_size = sizer.calculate_position_size()
print(f"Position size: ${position_size:,.2f}")

# Calculate stop loss
entry_price = Decimal("100.00")
stop_loss = sizer.calculate_stop_loss(entry_price)
print(f"Stop loss: ${stop_loss:.2f}")

# Calculate quantity
quantity = sizer.calculate_position_quantity(entry_price)
print(f"Buy {quantity:.4f} tokens")
```

### Circuit Breakers

```python
from decimal import Decimal
from src.risk.circuit_breaker import CircuitBreaker

# Initialize breaker
breaker = CircuitBreaker()

# Check if trading is allowed
if not breaker.is_trading_allowed():
    print("Trading halted by circuit breaker!")
    active = breaker.get_active_breakers()
    print(f"Active breakers: {active}")
    exit()

# Check daily loss
current_portfolio = Decimal("9400")  # Down from $10,000
start_of_day = Decimal("10000")

if breaker.check_daily_loss(current_portfolio, start_of_day):
    print("Daily loss breaker triggered!")
    # Trading will be halted

# Record trade results
breaker.record_trade_result(is_win=False)

# Check API health
try:
    # ... make API call ...
    breaker.record_api_success()
except Exception:
    if breaker.record_api_failure():
        print("Too many API failures - halting trades")
```

### Risk-Reward Analysis

```python
from decimal import Decimal
from src.risk.position_sizing import (
    calculate_risk_reward_ratio,
    min_win_rate_for_profitability
)

entry = Decimal("100")
take_profit = Decimal("120")  # 20% gain
stop_loss = Decimal("95")     # 5% loss

# Calculate RR ratio
rr = calculate_risk_reward_ratio(entry, take_profit, stop_loss)
print(f"Risk-Reward Ratio: {rr}:1")

# Calculate minimum win rate needed
min_wr = min_win_rate_for_profitability(rr)
print(f"Min win rate needed: {min_wr*100:.1f}%")
```

## Common Issues

### Import Errors

If you get import errors, ensure:
1. Virtual environment is activated
2. Project installed in editable mode: `pip install -e .`
3. You're running from project root directory

### Test Failures

If tests fail:
1. Check Python version: `python --version` (must be 3.11+)
2. Reinstall dependencies: `pip install -r requirements.txt`
3. Clear pytest cache: `pytest --cache-clear`

### Decimal Precision

We use Python's `Decimal` type for financial calculations to avoid floating-point errors:

```python
# ❌ Don't use float
price = 0.1 + 0.2  # May not equal 0.3

# ✅ Use Decimal
from decimal import Decimal
price = Decimal("0.1") + Decimal("0.2")  # Exactly 0.3
```

## Configuration

Risk limits are configured in `config/risk.yaml`:

```yaml
position_limits:
  max_position_pct: 2.0  # Never risk >2% per trade
  
circuit_breakers:
  daily_loss:
    threshold_pct: 5.0   # Stop if >5% daily loss
```

Modify these values carefully - they are your safety net.

## Next Phase Checklist

Before moving to Phase 2 (AI Engine), ensure:

- [ ] All risk tests passing (100% coverage)
- [ ] No critical TODOs in risk module
- [ ] Risk configuration validated
- [ ] Edge cases documented
- [ ] Performance benchmarks run

Run verification:
```bash
./scripts/verify_phase1.sh
```

## Getting Help

- Check `docs/risk-management.md` for detailed risk explanations
- Review test files for usage examples
- See `architecture.jsx` for system design

## Safety First

Remember: **The risk module is your lifeline.** Don't compromise on these protections to chase higher returns. Better to miss profits than lose capital.
