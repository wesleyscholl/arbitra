# 🤖 AI Trading Agent - 24/7 Automated Paper Trading

## 🎯 Overview

The AI Trading Agent uses OpenRouter (with models like Claude, GPT-4, etc.) to analyze market data and make automated trading decisions 24/7.

## 📋 Prerequisites

1. ✅ Backend server running (`./start-server.sh`)
2. ✅ Alpaca API keys configured (for market data)
3. 🔑 OpenRouter API key (get from https://openrouter.ai)

## 🔧 Setup

### Step 1: Get OpenRouter API Key

1. Go to https://openrouter.ai
2. Sign up for an account
3. Go to Settings → API Keys
4. Create a new API key
5. Copy the key (starts with `sk-or-...`)

### Step 2: Configure Environment

Add to your `.env` file:

```bash
# OpenRouter API for AI Trading
OPENROUTER_API_KEY=sk-or-v1-your-key-here
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet  # Or any model you prefer

# AI Agent Settings
AI_ENABLED=true
AI_UPDATE_INTERVAL=300  # Analyze every 5 minutes
AI_CONFIDENCE_THRESHOLD=0.7  # Only trade on 70%+ confidence
AI_MAX_POSITION_SIZE=1000  # Max $1000 per position
AI_MAX_POSITIONS=5  # Max 5 concurrent positions
AI_RISK_PER_TRADE=0.02  # Risk 2% per trade
```

### Step 3: Restart Backend

```bash
# Stop the current server (Ctrl+C in the terminal running it)
./start-server.sh
```

You should see:
```
✅ AI service initialized
✅ Trading agent initialized
✅ Agent monitoring started
```

## 🚀 Start Automated Trading

### Option 1: Via Swift App (Recommended)

1. Open the Arbitra app
2. Click "AI Trading" in the sidebar (brain icon)
3. Click the green "Start Agent" button
4. Monitor signals and activity in real-time

The AI Trading view shows:
- ✅ Agent status (running/stopped)
- 📊 Statistics (signals generated, scan interval, etc.)
- 🎯 Recent trading signals with confidence scores
- 🔧 Watchlist configuration (add/remove symbols)

### Option 2: Via API

```bash
# Start the agent
curl -X POST http://localhost:8000/api/agent/start

# Check status
curl http://localhost:8000/api/agent/status

# Stop the agent
curl -X POST http://localhost:8000/api/agent/stop
```

### Option 3: Auto-start on Backend Launch

Set in `.env`:
```bash
AI_ENABLED=true  # Agent starts automatically with backend
```

Then restart backend:
```bash
./start-server.sh
```

## 📊 How It Works

### The Trading Loop (Every 5 Minutes)

```
1. Fetch Market Data
   ↓
2. AI Analyzes Data
   - Technical indicators
   - Price patterns
   - Market sentiment
   ↓
3. Generate Trading Signals
   - BUY / SELL / HOLD
   - Confidence score (0-1)
   ↓
4. Risk Management
   - Check position limits
   - Calculate position size
   - Apply stop losses
   ↓
5. Execute Trades (if confidence > threshold)
   ↓
6. Update Portfolio
   ↓
7. Wait 5 minutes → Repeat
```

### AI Prompt Structure

The agent sends market data to the AI with this context:

```
You are an expert day trader analyzing stocks for paper trading.

Current Portfolio:
- Cash: $X
- Positions: [list]
- P&L: $X

Market Data for [SYMBOL]:
- Current Price: $X
- 5-min bars: [OHLCV data]
- Volume: X
- Trends: [analysis]

Task: Should we BUY, SELL, or HOLD this stock?
Provide:
1. Action (BUY/SELL/HOLD)
2. Confidence (0.0-1.0)
3. Reasoning (brief)
4. Position size (shares)
```

## 🛡️ Risk Management

### Built-in Safeguards

1. **Position Limits**
   - Max positions: 5 concurrent
   - Max per position: $1,000

2. **Confidence Threshold**
   - Only trades with 70%+ confidence
   - Lower confidence → smaller position size

3. **Stop Losses**
   - Automatic 5% stop loss on all positions
   - Prevents large losses

4. **Circuit Breaker**
   - Stops trading if losses exceed 10% in a day
   - Requires manual restart

5. **Paper Trading Only**
   - All trades are simulated
   - No real money at risk

## 📈 Monitoring

### Watch Backend Logs

The agent activity is logged in the backend terminal:

```bash
# You'll see logs like:
INFO - AI Agent analyzing AAPL...
INFO - Signal: BUY AAPL (confidence: 0.82)
INFO - Placing order: BUY 8 shares AAPL @ $121.50
INFO - Order filled: PAPER-20251010-000002
INFO - Position opened: AAPL (+8 shares)
```

### Check Portfolio Status

```bash
# View current account status
curl http://localhost:8000/api/trading/account

# View open positions
curl http://localhost:8000/api/trading/positions

# View recent trades
curl http://localhost:8000/api/trading/trades?limit=20
```

### Backend Logs

The backend terminal will show:
```
INFO - AI Agent analyzing AAPL...
INFO - Signal: BUY AAPL (confidence: 0.82)
INFO - Placing order: BUY 8 shares AAPL @ $121.50
INFO - Order filled: PAPER-20251010-000002
INFO - Position opened: AAPL (+8 shares)
```

### Swift App Dashboard

The app will show:
- Real-time positions updating
- New trades appearing in history
- P&L updating as prices change

## 🔧 Configuration Options

### Adjust Trading Frequency

In `.env`:
```bash
AI_UPDATE_INTERVAL=60   # Analyze every 1 minute (aggressive)
AI_UPDATE_INTERVAL=300  # Every 5 minutes (default)
AI_UPDATE_INTERVAL=900  # Every 15 minutes (conservative)
```

### Change AI Model

Different models have different strengths:

```bash
# Best reasoning (recommended)
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet

# Fast and cheap
OPENROUTER_MODEL=anthropic/claude-3-haiku

# Most capable
OPENROUTER_MODEL=openai/gpt-4-turbo

# Free (limited)
OPENROUTER_MODEL=meta-llama/llama-3.1-8b-instruct:free
```

### Adjust Risk Levels

**Conservative:**
```bash
AI_CONFIDENCE_THRESHOLD=0.8  # Only very confident trades
AI_MAX_POSITION_SIZE=500     # Smaller positions
AI_RISK_PER_TRADE=0.01       # Risk 1% per trade
```

**Aggressive:**
```bash
AI_CONFIDENCE_THRESHOLD=0.6  # Trade more often
AI_MAX_POSITION_SIZE=2000    # Larger positions
AI_RISK_PER_TRADE=0.05       # Risk 5% per trade
```

## 🐛 Troubleshooting

### Agent not starting

**Check backend logs:**
Look in the terminal running the backend for:
```
✅ AI service initialized
✅ Trading agent initialized  
✅ Agent monitoring started
```

**Common issues:**
- Missing OpenRouter API key → Add to `.env`
- Invalid API key → Check at https://openrouter.ai
- `AI_ENABLED=false` → Change to `true` in `.env`
- Network connectivity issues → Check internet connection

**Verify configuration:**
```bash
# Check .env file
cat .env | grep -E "OPENROUTER|AI_ENABLED"

# Should show:
# OPENROUTER_API_KEY=sk-or-v1-...
# AI_ENABLED=true
```

### No trades being placed

**Check confidence threshold:**
Edit `.env` and lower the threshold temporarily:
```bash
AI_CONFIDENCE_THRESHOLD=0.5  # Default is 0.7
```

**Check position limits:**
Edit `.env` to increase limits:
```bash
AI_MAX_POSITIONS=10          # Default is 5
AI_MAX_POSITION_SIZE=2000    # Default is 1000
```

**Monitor the analysis:**
Watch backend terminal for "AI Agent analyzing..." messages.
If you don't see any, the agent might not be running.

### Trades not appearing in app

**Restart the app:**
```bash
# Kill current instance
pkill -f ArbitraApp

# Restart
./run-app.sh
```

**Check WebSocket connection:**
- Look for "WebSocket connected" in app logs
- Should see real-time updates

## 📊 Performance Tracking

### View All Signals

```bash
# Last 50 signals
curl http://localhost:8000/api/agent/signals?limit=50
```

### Calculate Win Rate

Check the signals table in database:
```python
# In Python shell
from backend.database.models import Signal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///arbitra.db')
Session = sessionmaker(bind=engine)
session = Session()

# Get statistics
total = session.query(Signal).filter(Signal.acted_on == True).count()
buy_signals = session.query(Signal).filter(Signal.signal_type == 'buy').count()
sell_signals = session.query(Signal).filter(Signal.signal_type == 'sell').count()

print(f"Total signals: {total}")
print(f"Buy: {buy_signals}")
print(f"Sell: {sell_signals}")
```

### Export Trading History

```bash
# Get all trades as JSON
curl http://localhost:8000/api/trading/trades?limit=1000 > trades.json
```

## 🚀 Running 24/7

### Option 1: Keep Terminal Open

Just leave the backend running:
```bash
./start-server.sh
# Don't close terminal
# Agent runs continuously
```

### Option 2: Background Process (tmux)

```bash
# Install tmux
brew install tmux

# Start session
tmux new -s arbitra

# Run backend
./start-server.sh

# Detach: Press Ctrl+B, then D
# Reattach: tmux attach -t arbitra
```

### Option 3: System Service (macOS)

Create a LaunchAgent to run on startup:

```bash
# Create service file
cat > ~/Library/LaunchAgents/com.arbitra.backend.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.arbitra.backend</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/wscholl/arbitra/start-server.sh</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/wscholl/arbitra</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/Users/wscholl/arbitra/logs/backend.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/wscholl/arbitra/logs/backend.error.log</string>
</dict>
</plist>
EOF

# Create logs directory
mkdir -p ~/arbitra/logs

# Load service
launchctl load ~/Library/LaunchAgents/com.arbitra.backend.plist

# Check status
launchctl list | grep arbitra

# Stop service
launchctl unload ~/Library/LaunchAgents/com.arbitra.backend.plist
```

## ⚙️ Advanced Configuration

### Custom Trading Symbols

Edit the agent to trade specific stocks:

In `backend/services/trading_agent.py`:
```python
# Add your watchlist
self.watchlist = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'NVDA']
```

### Custom Trading Strategy

Modify the AI prompt in `backend/services/ai_service.py`:
```python
prompt = f"""
You are a momentum trader focusing on breakouts.

[Your custom strategy instructions here]
"""
```

### Webhooks for Notifications

Get notified of trades via Discord/Slack:

```python
# Add to trading agent
import requests

def notify_trade(trade):
    webhook_url = "YOUR_WEBHOOK_URL"
    requests.post(webhook_url, json={
        "text": f"Trade: {trade['side']} {trade['quantity']} {trade['symbol']} @ ${trade['price']}"
    })
```

## 📝 Summary

Your AI trading agent is now configured for 24/7 automated paper trading!

**What happens now:**
1. ✅ Agent analyzes market every 5 minutes
2. ✅ AI generates BUY/SELL/HOLD signals
3. ✅ High-confidence signals → automatic trades
4. ✅ Risk management enforced on all positions
5. ✅ Real-time updates to Swift app
6. ✅ All trades logged to database

**Monitor it:**
- Swift app dashboard (live)
- Backend terminal logs (detailed)
- API endpoints (programmatic)

**Control it:**
- Adjust thresholds in `.env`
- Start/stop via API
- Emergency stop via circuit breaker

**Stay safe:**
- It's paper trading (no real money)
- Position limits enforced
- Stop losses on all positions
- Circuit breaker for large losses

🎉 **Happy automated trading!** 📈🤖
