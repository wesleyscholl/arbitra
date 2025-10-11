# 🚀 Arbitra Quick Reference

## Start Everything

```bash
# 1. Start Backend
cd /Users/wscholl/arbitra
./start-server.sh

# 2. Run Swift App
./run-app.sh

# 3. Bring app to front
# Press Cmd+Tab and select ArbitraApp
```

## Test a Trade

```bash
curl -X POST http://localhost:8000/api/trading/orders \
  -H "Content-Type: application/json" \
  -d '{"symbol":"AAPL","side":"buy","quantity":10,"order_type":"market"}'
```

## Start AI Agent (24/7 Trading)

```bash
# 1. Add to .env file:
OPENROUTER_API_KEY=sk-or-v1-your-key-here

# 2. Restart backend (Ctrl+C, then ./start-server.sh)

# 3. Start agent:
curl -X POST http://localhost:8000/api/agent/start

# 4. Check status:
curl http://localhost:8000/api/agent/status
```

## Key URLs

- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **WebSocket:** ws://localhost:8000/ws/market-data

## Troubleshooting

### Swift App not connecting?
1. Open app Settings
2. Click "Reset to Defaults"
3. Restart app

### Backend not responding?
```bash
# Check if running:
curl http://localhost:8000/health

# Restart:
pkill -f uvicorn
./start-server.sh
```

### View logs
Backend terminal shows all activity:
- API requests
- WebSocket connections  
- Trade executions
- AI agent signals

## Documentation

- **`PROJECT_SUMMARY.md`** - Complete overview
- **`AI_AGENT_24_7_GUIDE.md`** - AI agent setup
- **`PAPER_TRADING_README.md`** - Backend details
- **`docs/RUNNING.md`** - App usage guide

## Current Status

✅ Backend running at http://localhost:8000
✅ Swift app connected via WebSocket
✅ Paper trading with $100,000 capital
✅ Live Alpaca market data
✅ AI agent ready (needs API key)

**Everything is working! Start trading!** 📈
