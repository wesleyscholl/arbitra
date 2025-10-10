# 🤖 AI Trading Agent - 24/7 Automated Paper Trading

## Overview

The AI Trading Agent uses **OpenRouter API** (Claude 3.5 Sonnet) to:
1. Monitor a watchlist of stocks every 5 minutes
2. Analyze market data and generate trading signals
3. Execute paper trades automatically based on AI confidence
4. Manage positions and risk

## 🔑 Setup

### Step 1: Get OpenRouter API Key

1. Go to https://openrouter.ai/
2. Sign up for an account
3. Add credits to your account ($5-10 is plenty for testing)
4. Generate an API key

### Step 2: Add API Key to `.env`

```bash
# Edit your .env file
nano .env
```

Add this line:
```bash
OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

### Step 3: Restart Backend

```bash
# Stop the current server (Ctrl+C)
# Then restart
./start-server.sh
```

You should see:
```
✅ Trading agent initialized
```

## 🚀 Starting the Agent

### Option 1: Via API

```bash
# Start the agent
curl -X POST http://localhost:8000/api/agent/start

# Check status
curl http://localhost:8000/api/agent/status

# Stop the agent
curl -X POST http://localhost:8000/api/agent/stop
```

### Option 2: Via Swift App

1. Open the Arbitra app
2. Go to Dashboard
3. Click "Start Trading" button
4. Agent will start scanning automatically

## 📊 How It Works

### Agent Loop (Every 5 Minutes)

1. **Scan Watchlist**
   - Default: AAPL, GOOGL, MSFT, AMZN, TSLA
   - Get latest quotes and historical data

2. **Generate AI Signal**
   - Send market data to Claude AI
   - Get trading recommendation: BUY, SELL, or HOLD
   - Receive confidence score (0-1)

3. **Execute Trades**
   - If confidence ≥ 0.65 (65%), execute trade
   - BUY: Opens new position (max $10k per position)
   - SELL: Closes existing position
   - HOLD: Do nothing

4. **Broadcast Updates**
   - WebSocket pushes signals and trades to Swift app
   - Real-time notifications

### Signal Format

```json
{
  "symbol": "AAPL",
  "signal_type": "buy",
  "confidence": 0.78,
  "reasoning": "Strong upward momentum with SMA crossover...",
  "target_size": 15,
  "current_price": 121.31,
  "timestamp": "2025-10-10T16:00:00",
  "model": "anthropic/claude-3.5-sonnet",
  "indicators": {
    "sma_5": 120.5,
    "sma_20": 118.2,
    "price_change_1d": 1.2,
    "price_change_5d": 3.5
  }
}
```

## ⚙️ Configuration

### Default Settings

```python
watchlist = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]
scan_interval = 300  # 5 minutes
signal_threshold = 0.65  # 65% confidence required
max_positions = 5  # Maximum open positions
max_position_size = $10,000  # Max per position
```

### Update Configuration

```bash
curl -X POST http://localhost:8000/api/agent/config \
  -H "Content-Type: application/json" \
  -d '{
    "watchlist": ["AAPL", "TSLA", "NVDA"],
    "scan_interval": 600,
    "signal_threshold": 0.70,
    "max_positions": 3,
    "max_position_size": 5000.0
  }'
```

### Get Current Configuration

```bash
curl http://localhost:8000/api/agent/config
```

## 📈 Monitoring

### Check Agent Status

```bash
curl http://localhost:8000/api/agent/status
```

Response:
```json
{
  "running": true,
  "watchlist": ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"],
  "scan_interval": 300,
  "signal_threshold": 0.65,
  "max_positions": 5,
  "max_position_size": 10000.0,
  "last_scan_time": "2025-10-10T16:05:00",
  "total_signals": 42
}
```

### View Recent Signals

```bash
curl http://localhost:8000/api/agent/signals
```

### Watch Backend Logs

The backend logs show all agent activity:

```
📊 Scanning watchlist for trading opportunities...
🎯 Executing BUY signal for AAPL (confidence: 78.00%)
✅ Bought 15 shares of AAPL @ $121.31
```

## 🎯 Example Session

### 1. Start the backend
```bash
./start-server.sh
```

### 2. Start the agent
```bash
curl -X POST http://localhost:8000/api/agent/start
```

### 3. Watch it trade
```bash
# Check status every minute
watch -n 60 'curl -s http://localhost:8000/api/agent/status | jq'

# Or watch account balance
watch -n 60 'curl -s http://localhost:8000/api/trading/account | jq'
```

### 4. View results in Swift app
- Open Arbitra app
- Dashboard shows real-time P&L
- Positions tab shows all holdings
- History shows all trades with AI reasoning

## 🔒 Risk Management

The agent includes built-in protections:

1. **Position Limits**
   - Max 5 positions at once
   - Max $10k per position

2. **Confidence Threshold**
   - Only trades when AI is ≥65% confident
   - Conservative signals only

3. **Paper Trading Only**
   - No real money at risk
   - Test strategies safely

4. **Slippage & Commission**
   - Realistic simulation
   - 5 bps slippage
   - $0.005/share commission

## 💰 Cost Estimate

**OpenRouter Pricing (Claude 3.5 Sonnet):**
- ~$0.003 per signal generation
- 5 stocks × 12 scans/hour = 60 signals/hour
- **~$0.18/hour = $4.32/day = $129.60/month**

**Recommendations:**
- Start with shorter intervals (5 min) for testing
- Increase to 15-30 min for production
- Monitor costs in OpenRouter dashboard

## 🐛 Troubleshooting

### Agent won't start

**Check API key:**
```bash
grep OPENROUTER_API_KEY .env
```

**Check logs:**
```bash
# Look for "Trading agent initialized"
```

### No trades being executed

**Check confidence threshold:**
```bash
curl http://localhost:8000/api/agent/signals | jq
```

Most signals probably have <65% confidence. Lower threshold:
```bash
curl -X POST http://localhost:8000/api/agent/config \
  -H "Content-Type: application/json" \
  -d '{"signal_threshold": 0.50}'
```

### Agent stopped unexpectedly

Check backend logs for errors. Common issues:
- OpenRouter API key invalid
- Rate limiting (too many requests)
- Alpaca SSL errors (already fixed)

## 📝 API Endpoints

### Agent Control
- `POST /api/agent/start` - Start agent
- `POST /api/agent/stop` - Stop agent
- `GET /api/agent/status` - Get status
- `GET /api/agent/signals?limit=20` - Recent signals

### Configuration
- `GET /api/agent/config` - Get config
- `POST /api/agent/config` - Update config

### Trading
- `GET /api/trading/account` - Account info
- `GET /api/trading/positions` - Current positions
- `GET /api/trading/trades` - Trade history

## 🎉 Success Indicators

When working correctly, you'll see:

**Backend Logs:**
```
📊 Scanning watchlist for trading opportunities...
🎯 Executing BUY signal for AAPL (confidence: 78.00%)
✅ Bought 15 shares of AAPL @ $121.31
```

**Swift App:**
- Real-time position updates
- Trade notifications
- P&L tracking
- Signal history with AI reasoning

**Account Growth:**
- Positions accumulating
- Trades being executed
- P&L changing (could be positive or negative!)

## 🚦 Running 24/7

### Option 1: Keep Terminal Open
```bash
# Start backend in background
nohup ./start-server.sh > server.log 2>&1 &

# Start agent via API
curl -X POST http://localhost:8000/api/agent/start

# Agent runs until stopped
```

### Option 2: Use tmux/screen
```bash
# Start tmux session
tmux new -s arbitra

# Start backend
./start-server.sh

# Detach: Ctrl+B, then D
# Reattach: tmux attach -t arbitra
```

### Option 3: systemd Service (Production)
Create `/etc/systemd/system/arbitra.service`:
```ini
[Unit]
Description=Arbitra Trading Agent
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/arbitra
ExecStart=/path/to/arbitra/venv/bin/python -m backend.main
Restart=always

[Install]
WantedBy=multi-user.target
```

---

**🎊 Your AI trading agent is ready to trade 24/7!**

Start with conservative settings, monitor closely, and adjust based on performance. Remember: This is paper trading, so experiment freely! 📈🤖

