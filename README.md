# Arbitra - AI Crypto Trading Agent

> A capital-preserving AI trading agent focused on steady, consistent returns through multi-tier asset allocation and robust risk management.

## 🎯 Project Goals

- **Capital Preservation First**: Never risk more than 2% per trade
- **Steady Returns**: Target 8-15% monthly returns through diversified strategies
- **AI-Driven Decisions**: Use LLMs for market analysis with confidence scoring
- **Bulletproof Risk Management**: Hard limits, circuit breakers, and real-time monitoring

## 📊 Trading Philosophy

### Multi-Tier Asset Allocation

1. **Foundation Layer (50%)**: BTC, ETH, SOL - Low risk, steady growth
2. **Growth Layer (30%)**: Top 20-100 altcoins - Medium risk, higher returns
3. **Opportunity Layer (20%)**: High-quality memecoins - High risk, asymmetric upside

See `strategy.jsx` and `architecture.jsx` for detailed strategy documentation.

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Arbitra Trading System                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ Data Feeds   │  │  AI Engine   │  │ Risk Manager │       │
│  │              │  │              │  │              │       │
│  │ • Helius     │→ │ • Gemini AI  │→ │ • Position   │       │
│  │ • Birdeye    │  │ • Analysis   │  │   Sizing     │       │
│  │ • DexScreener│  │ • Confidence │  │ • Stop Loss  │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│         ↓                  ↓                  ↓             │
│  ┌──────────────────────────────────────────────────┐       │
│  │            Execution Engine                      │       │
│  │  • Jupiter Aggregator                            │       │
│  │  • Wallet Management                             │       │
│  │  • Transaction Monitoring                        │       │
│  └──────────────────────────────────────────────────┘       │
│         ↓                                                   │
│  ┌──────────────────────────────────────────────────┐       │
│  │            Monitoring & Logging                  │       │
│  │  • PostgreSQL (trades, metrics)                  │       │
│  │  • Redis (state management)                      │       │
│  │  • Prometheus/Grafana                            │       │
│  └──────────────────────────────────────────────────┘       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Technology Stack

### Core
- **Language**: Python 3.11+
- **Framework**: FastAPI (async trading operations)
- **AI Models**: Google Gemini (gemini-2.0-flash-exp, gemini-1.5-pro)
- **Blockchain**: Solana Web3.py

### Data & Storage
- **Database**: PostgreSQL 15+ (trade logs, analytics)
- **Cache**: Redis 7+ (real-time state)
- **Vector DB**: Pinecone (trade memory)

### External APIs
- **Blockchain Data**: Helius, QuickNode
- **Market Data**: Birdeye, DexScreener, CoinGecko
- **DEX Aggregator**: Jupiter API
- **Token Analysis**: RugCheck, Token Sniffer

### DevOps
- **Containerization**: Podman + Podman Compose (Docker-free alternative)
- **Monitoring**: Prometheus, Grafana
- **Logging**: Structlog
- **Testing**: Pytest, Hypothesis (property testing)

## 📦 Project Structure

```
arbitra/
├── README.md                    # This file
├── architecture.jsx             # System design reference
├── strategy.jsx                 # Trading strategy reference
├── podman-compose.yml           # Infrastructure setup (Podman)
├── requirements.txt             # Python dependencies
├── pyproject.toml              # Project config
│
├── src/
│   ├── __init__.py
│   │
│   ├── risk/                   # 🔴 CRITICAL: Risk management
│   │   ├── __init__.py
│   │   ├── manager.py          # Main risk manager
│   │   ├── position_sizing.py # Kelly criterion, position limits
│   │   ├── circuit_breaker.py # Emergency stop mechanisms
│   │   ├── portfolio.py        # Portfolio-level risk
│   │   └── validators.py       # Pre-trade validation
│   │
│   ├── ai/                     # AI decision engine
│   │   ├── __init__.py
│   │   ├── agent.py            # Main AI agent
│   │   ├── prompts.py          # LLM prompt templates
│   │   ├── confidence.py       # Confidence scoring
│   │   └── memory.py           # Trade memory/learning
│   │
│   ├── data/                   # Data collection
│   │   ├── __init__.py
│   │   ├── feeds.py            # Data feed aggregator
│   │   ├── solana.py           # Solana blockchain data
│   │   ├── market.py           # Market data (prices, volume)
│   │   └── social.py           # Social sentiment
│   │
│   ├── execution/              # Trade execution
│   │   ├── __init__.py
│   │   ├── engine.py           # Main execution engine
│   │   ├── jupiter.py          # Jupiter DEX integration
│   │   ├── wallet.py           # Wallet management
│   │   └── monitor.py          # Transaction monitoring
│   │
│   ├── strategies/             # Trading strategies
│   │   ├── __init__.py
│   │   ├── base.py             # Base strategy class
│   │   ├── foundation.py       # BTC/ETH/SOL strategies
│   │   ├── growth.py           # Altcoin strategies
│   │   └── opportunity.py      # Memecoin strategies
│   │
│   ├── models/                 # Data models
│   │   ├── __init__.py
│   │   ├── trade.py
│   │   ├── asset.py
│   │   └── portfolio.py
│   │
│   ├── database/               # Database layer
│   │   ├── __init__.py
│   │   ├── postgres.py
│   │   ├── redis.py
│   │   └── migrations/
│   │
│   └── utils/                  # Utilities
│       ├── __init__.py
│       ├── logging.py
│       ├── metrics.py
│       └── config.py
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Pytest fixtures
│   │
│   ├── risk/                   # Risk module tests
│   │   ├── test_manager.py
│   │   ├── test_position_sizing.py
│   │   ├── test_circuit_breaker.py
│   │   ├── test_portfolio.py
│   │   └── test_validators.py
│   │
│   ├── ai/
│   ├── data/
│   ├── execution/
│   └── strategies/
│
├── scripts/                    # Utility scripts
│   ├── backtest.py            # Backtesting framework
│   ├── paper_trade.py         # Paper trading mode
│   └── deploy.sh              # Deployment script
│
├── config/                    # Configuration files
│   ├── config.yaml            # Main config
│   ├── strategies.yaml        # Strategy parameters
│   └── risk.yaml              # Risk limits
│
└── docs/                      # Documentation
    ├── setup.md
    ├── strategies.md
    ├── risk-management.md
    └── api.md
```

## 🚀 Implementation Phases

### Phase 1: Foundation (Week 1-2) ✅ CURRENT PHASE

**Objective**: Build bulletproof risk management and core infrastructure

#### Components:
1. **Risk Management Module** 🔴 CRITICAL
   - Position sizing (Kelly criterion)
   - Stop-loss automation
   - Portfolio-level limits
   - Circuit breakers
   - Pre-trade validation
   - **Status**: In Progress

2. **Database Setup**
   - PostgreSQL schema
   - Redis configuration
   - Database migrations

3. **Basic Data Feeds**
   - Market data integration
   - Price feeds
   - Basic on-chain data

#### Success Criteria:
- ✅ Risk module passes 100% of tests
- ✅ Circuit breakers trigger correctly
- ✅ Position sizing calculations verified
- ✅ Database can handle 1000+ trades/day
- ✅ Data feeds maintain <1s latency

### Phase 2: AI Engine (Week 3-4) 🔄 IN PROGRESS

**Objective**: Implement AI decision-making with confidence scoring using Google Gemini

#### Components:
1. **AI Agent Core**
   - Google Gemini API integration (gemini-2.0-flash-exp for speed, gemini-1.5-pro for complex analysis)
   - Prompt engineering for trading analysis
   - Structured JSON output parsing
   - Retry logic and error handling

2. **Confidence Scoring**
   - Multi-factor confidence calculation (technical indicators, sentiment, risk factors)
   - Historical accuracy tracking
   - Confidence calibration against actual outcomes
   - Dynamic confidence adjustment

3. **Trade Memory**
   - Vector database setup (Pinecone)
   - Similar trade retrieval using embeddings
   - Learning from past trades
   - Pattern recognition

#### Success Criteria:
- AI generates valid trade recommendations with >90% structural accuracy
- Confidence scores correlate with outcomes (R² > 0.6)
- Memory system retrieves relevant trades (<500ms)
- Avg response time <2s for flash model, <5s for pro model

### Phase 3: Foundation Strategies (Week 5-6)

**Objective**: Implement low-risk BTC/ETH/SOL strategies

#### Components:
1. **Mean Reversion**
   - Support/resistance detection
   - RSI-based entries
   - Take-profit automation

2. **DCA & Accumulation**
   - Time-based buying
   - Dip buying logic
   - Cost averaging

3. **Staking Integration**
   - Staking rewards tracking
   - Auto-compounding

#### Success Criteria:
- Strategies tested on 6+ months historical data
- Win rate >60%
- Max drawdown <8%
- Sharpe ratio >1.5

### Phase 4: Execution Engine (Week 7-8)

**Objective**: Build reliable trade execution

#### Components:
1. **Jupiter Integration**
   - Route optimization
   - Slippage control
   - Transaction retry logic

2. **Wallet Management**
   - Secure key storage
   - Multi-wallet support
   - Balance tracking

3. **Transaction Monitoring**
   - Confirmation tracking
   - Failed transaction handling
   - Gas optimization

#### Success Criteria:
- 99%+ transaction success rate
- <5s avg execution time
- Slippage <0.5% of target

### Phase 5: Growth Strategies (Week 9-10)

**Objective**: Add medium-risk altcoin strategies

#### Components:
1. **Momentum Trading**
   - Breakout detection
   - Volume analysis
   - Trend following

2. **Sector Rotation**
   - Narrative tracking
   - Sector strength analysis
   - Rotation signals

3. **Event-Driven**
   - Protocol launch tracking
   - Partnership announcements
   - Token unlock monitoring

#### Success Criteria:
- Strategy mix provides 10-20% monthly returns
- Correlation with BTC <0.7
- Individual strategy win rate >55%

### Phase 6: Opportunity Layer (Week 11-12)

**Objective**: Add high-risk memecoin strategies (ONLY if Phase 5 successful)

#### Components:
1. **Token Safety Scanner**
   - Contract analysis
   - Honeypot detection
   - Liquidity verification
   - Ownership analysis

2. **Viral Momentum Detection**
   - Social signal processing
   - Engagement velocity
   - Influencer tracking

3. **Quick Execution**
   - <500ms execution
   - Aggressive take-profits
   - 24-72hr max hold time

#### Success Criteria:
- Token scanner catches 95%+ scams
- Social signals predict pumps with >40% accuracy
- Even with 50% loss rate, net positive returns
- HARD RULE: Never hold >72 hours

### Phase 7: Monitoring & Optimization (Ongoing)

**Objective**: Continuous improvement and monitoring

#### Components:
1. **Dashboard**
   - Real-time P&L
   - Strategy performance
   - Risk metrics
   - AI confidence tracking

2. **Backtesting Framework**
   - Historical replay
   - Strategy optimization
   - Walk-forward analysis

3. **Alerting**
   - Circuit breaker triggers
   - Large losses
   - System errors
   - Performance degradation

## 🛡️ Risk Management Rules

### Hard Limits (NEVER OVERRIDE)

```yaml
# Per-Trade Limits
max_position_size_pct: 2.0          # % of portfolio per trade
max_portfolio_risk_pct: 10.0        # % of portfolio at risk
stop_loss_pct: 5.0                  # Stop loss from entry

# Portfolio Limits
max_daily_loss_pct: 5.0             # Daily loss limit
max_weekly_loss_pct: 10.0           # Weekly loss limit
max_drawdown_pct: 15.0              # Max drawdown before pause

# Asset-Specific Limits
foundation_max_pct: 60.0            # Max in BTC/ETH/SOL
growth_max_pct: 40.0                # Max in altcoins
opportunity_max_pct: 20.0           # Max in memecoins

# Memecoin-Specific
memecoin_max_hold_hours: 72         # NEVER exceed
memecoin_min_liquidity: 100000      # Min $100k liquidity
memecoin_max_position: 1.0          # Max 1% per memecoin
```

### Circuit Breakers

1. **Daily Loss Breaker**: Stop trading if daily loss >5%
2. **Drawdown Breaker**: Pause if drawdown >15%
3. **Volatility Breaker**: Reduce size if VIX equivalent >100
4. **Liquidity Breaker**: No trades if liquidity <$50k
5. **API Failure Breaker**: Stop if data feeds fail

## 📈 Performance Targets

### Phase 1-3 (Foundation Only)
- **Target Return**: 5-8% monthly
- **Max Drawdown**: <8%
- **Win Rate**: >60%
- **Sharpe Ratio**: >1.5

### Phase 4-5 (Foundation + Growth)
- **Target Return**: 10-15% monthly
- **Max Drawdown**: <12%
- **Win Rate**: >55%
- **Sharpe Ratio**: >1.3

### Phase 6+ (Full System)
- **Target Return**: 15-25% monthly
- **Max Drawdown**: <15%
- **Win Rate**: >50%
- **Sharpe Ratio**: >1.2

## 🧪 Testing Strategy

### Unit Tests
- 100% coverage for risk module
- Property-based testing (Hypothesis)
- Edge case validation

### Integration Tests
- End-to-end trade flow
- API integration tests
- Database transaction tests

### Backtests
- 12+ months historical data
- Multiple market conditions
- Walk-forward validation

### Paper Trading
- Minimum 2 weeks before live
- Real-time execution testing
- Risk validation

## 🔒 Security

- Encrypted wallet keys (KMS)
- API key rotation
- Rate limiting
- Audit logging
- No secrets in code
- Regular security audits

## 📊 Monitoring Metrics

### Trading Metrics
- Daily/Weekly/Monthly P&L
- Win rate by strategy
- Average win/loss
- Sharpe ratio
- Max drawdown
- Recovery time

### Risk Metrics
- Position sizes
- Portfolio exposure
- Correlation matrix
- VaR (Value at Risk)
- Circuit breaker triggers

### System Metrics
- API latency
- Transaction success rate
- Data feed uptime
- Error rates
- Memory/CPU usage

## 🚦 Getting Started

### Prerequisites
```bash
# Required
- Python 3.11+
- Podman & Podman Compose (Docker-free alternative)
  OR native PostgreSQL 15+ and Redis 7+ installed locally

# Optional
- Solana CLI (for testing)
- Prometheus/Grafana (monitoring)
```

**Note**: This project uses Podman instead of Docker. Podman is daemonless, rootless, and doesn't require elevated privileges. If you can't use containers at all, see the "Local Installation" section below.

### Installation

```bash
# 1. Clone repository
git clone <repo-url>
cd arbitra

# 2. Set up Python environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
pip install -e .  # Install in editable mode

# 4. Set up infrastructure (choose one option)

## Option A: Using Podman (recommended)
podman-compose up -d

## Option B: Local installation (no containers)
# Install PostgreSQL
brew install postgresql@15  # macOS
brew services start postgresql@15

# Install Redis
brew install redis
brew services start redis

# 5. Run database migrations (skip if using Option B initially)
# python scripts/migrate.py

# 6. Configure environment
cp config/config.example.yaml config/config.yaml
# Edit config.yaml with your API keys and database connection strings

# 7. Run tests (no infrastructure needed for unit tests)
pytest tests/risk/ -v --cov=src/risk
```

### Quick Start

```bash
# Run in paper trading mode
python scripts/paper_trade.py

# Run backtests
python scripts/backtest.py --start 2024-01-01 --end 2024-12-31

# Start live trading (after paper trading success)
python main.py --mode live
```

## 📚 Documentation

- **[Installation Guide](INSTALLATION.md)** - Detailed setup options (Podman, local, or no infrastructure)
- **[Quick Start](QUICKSTART.md)** - Get up and running fast
- **[AI Engine](docs/AI_ENGINE.md)** - Google Gemini integration guide
- **[Phase 2 Testing](docs/PHASE2_TESTING.md)** - Complete test results and coverage report
- [Trading Strategies](docs/strategies.md)
- [Risk Management](docs/risk-management.md)
- [API Documentation](docs/api.md)

## ⚠️ Disclaimers

- **No Financial Advice**: This is experimental software. Use at your own risk.
- **Capital Loss Risk**: Crypto trading involves significant risk of capital loss.
- **No Guarantees**: Past performance doesn't guarantee future results.
- **Beta Software**: This system is under active development.

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE)

---

## 🎯 Current Status

**Phase**: 2 (AI Engine) ✅ **COMPLETE**  
**Test Coverage**: 95% overall (99 tests, 100% passing)  
**Completed**:
- ✅ Phase 1 - Risk Management Module (100% test coverage, 62 tests)
- ✅ Phase 2 - AI Engine with Google Gemini (95% coverage, 37 tests)
  - Trading agent with dual-model approach (Flash/Pro)
  - Confidence scoring with Brier calibration
  - Vector memory with Pinecone for pattern matching
  
**Next Milestone**: Phase 3 - Trading Strategies (Foundation layer: BTC/ETH/SOL)

**Last Updated**: October 8, 2025
