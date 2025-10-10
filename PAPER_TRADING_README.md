# Arbitra - Paper Trading Setup Complete ✅

## 🎉 What's Working

Your Arbitra paper trading backend is now **fully operational** with:

✅ **Backend Server Running** on `http://localhost:8000`
- FastAPI application with CORS enabled
- Real-time WebSocket support
- SSL certificate issue resolved (dev workaround)

✅ **Paper Trading Engine**
- Tracks virtual positions with $100,000 initial capital
- Calculates P&L in real-time
- Applies slippage (5 bps) and commission ($0.005/share)
- Supports market and limit orders

✅ **Alpaca Integration**
- Live market data from Alpaca Markets API
- Real-time quotes, historical bars, asset search
- Account info from your paper trading account

✅ **Swift macOS UI** (already completed)
- Full-featured trading interface
- WebSocket connectivity ready
- Account and position tracking

## 🚀 Quick Start

### Start the Backend
```bash
cd /Users/wscholl/arbitra
./start-server.sh
```

The server will start on `http://localhost:8000`

### Test the API
Open your browser to:
- Health Check: http://localhost:8000/health
- API Docs: http://localhost:8000/docs
- Account Info: http://localhost:8000/api/trading/account

### Run the Swift App
Open Xcode and run your `ArbitraApp` - it will automatically connect to the backend via WebSocket at `ws://localhost:8000/ws/market-data`

## 📡 API Endpoints

### Account & Positions
- `GET /api/trading/account` - Account balance, P&L, positions
- `GET /api/trading/positions` - All open positions
- `GET /api/trading/positions/{symbol}` - Specific position
- `GET /api/trading/trades` - Trade history

### Market Data
- `GET /api/trading/quote/{symbol}` - Latest quote (bid/ask)
- `GET /api/trading/bars/{symbol}` - Historical OHLCV bars
- `GET /api/trading/search?q=Apple` - Search for assets

### Orders
- `POST /api/trading/orders` - Submit buy/sell order
- `GET /api/trading/orders` - All orders
- `GET /api/trading/orders/{order_id}` - Specific order
- `DELETE /api/trading/orders/{order_id}` - Cancel order

### WebSocket
- `WS /ws/market-data` - Real-time market data stream

**WebSocket Messages:**
```json
// Subscribe to symbols
{"action": "subscribe", "symbols": ["AAPL", "GOOGL"]}

// Get account info
{"action": "get_account"}

// Get positions
{"action": "get_positions"}

// Ping/pong
{"action": "ping"}
```

## 📝 Example: Place a Trade

### Buy 10 shares of AAPL (market order)
```bash
curl -X POST http://localhost:8000/api/trading/orders \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "side": "buy",
    "quantity": 10,
    "order_type": "market"
  }'
```

### Sell 5 shares of GOOGL (limit order at $180)
```bash
curl -X POST http://localhost:8000/api/trading/orders \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "GOOGL",
    "side": "sell",
    "quantity": 5,
    "order_type": "limit",
    "limit_price": 180.00
  }'
```

## 📂 Project Structure

```
arbitra/
├── backend/
│   ├── main.py                       # FastAPI server ✅
│   ├── services/
│   │   └── alpaca_service.py        # Alpaca market data ✅
│   ├── trading/
│   │   └── paper_trading_engine.py  # Paper trading logic ✅
│   ├── database/
│   │   └── models.py                # SQLAlchemy models ✅
│   └── api/
│       └── routes/
│           ├── trading.py           # REST API ✅
│           └── websocket.py         # WebSocket handler ✅
├── ArbitraApp/                       # Swift macOS UI ✅
├── .env                              # API keys configured
├── start-server.sh                   # Quick start script
└── test_alpaca_connection.py        # Connection test
```

## 🔧 Configuration (.env)

```bash
# Alpaca API (Paper Trading)
ALPACA_API_KEY=PKZREONV...
ALPACA_SECRET_KEY=your_secret_key
ALPACA_BASE_URL=https://paper-api.alpaca.markets

# Paper Trading Settings
INITIAL_CAPITAL=100000.0
ENABLE_SLIPPAGE=true
SLIPPAGE_BPS=5.0
ENABLE_COMMISSION=true
COMMISSION_PER_SHARE=0.005

# Server
API_HOST=0.0.0.0
API_PORT=8000
```

## 🐛 SSL Certificate Issue (Fixed)

**Problem:** Corporate proxy/firewall blocking SSL verification to Alpaca API

**Solution:** `start-server.sh` disables SSL verification for development:
```bash
export REQUESTS_CA_BUNDLE=""
export PYTHONHTTPSVERIFY=0
```

⚠️ **Warning:** This is for development only. For production, install proper certificates.

## 🎯 Next Steps

### Immediate (Ready to Use)
1. ✅ Start backend: `./start-server.sh`
2. ✅ Run Swift app from Xcode
3. ✅ Subscribe to symbols via WebSocket
4. ✅ Place paper trades through UI
5. ✅ Watch real-time P&L updates

### Future Enhancements (Optional)
- [ ] **AI Signal Generator** - OpenRouter integration for trading signals
- [ ] **Database Persistence** - Save trades/positions to SQLite
- [ ] **Backtesting** - Test strategies on historical data
- [ ] **Multiple Strategies** - Run different trading algorithms
- [ ] **Risk Management** - Position limits, stop losses
- [ ] **Performance Analytics** - Sharpe ratio, max drawdown, etc.

## 📊 How It Works

```
┌─────────────────┐
│   Swift macOS   │
│   (ArbitraApp)  │
└────────┬────────┘
         │ WebSocket
         ↓
┌─────────────────────────────────────┐
│      FastAPI Backend Server         │
│  (http://localhost:8000)            │
│                                      │
│  ┌────────────────────────────┐   │
│  │  Paper Trading Engine      │   │
│  │  - Track virtual positions │   │
│  │  - Calculate P&L           │   │
│  │  - Apply slippage/commission│  │
│  └────────────────────────────┘   │
└────────┬────────────────────────────┘
         │ REST API calls
         ↓
┌─────────────────────────────────────┐
│       Alpaca Markets API             │
│  (Paper Trading Account)             │
│  - Real-time quotes                  │
│  - Historical bars                   │
│  - Account info                      │
└──────────────────────────────────────┘
```

**Data Flow:**
1. Alpaca provides real market data (quotes, bars)
2. Paper trading engine simulates trades locally
3. FastAPI serves REST API and WebSocket
4. Swift UI displays account, positions, P&L
5. Users place orders via UI → engine tracks virtually

## 🔍 Troubleshooting

### Server won't start
```bash
# Check if port 8000 is in use
lsof -i :8000

# Kill existing process
kill -9 <PID>

# Restart
./start-server.sh
```

### SSL certificate errors
Already handled by `start-server.sh` - it disables SSL verification

### Swift app can't connect
1. Ensure backend is running: `curl http://localhost:8000/health`
2. Check WebSocket URL in Swift: `ws://localhost:8000/ws/market-data`
3. Check console logs in Xcode for connection errors

### No market data
- Market hours: 9:30 AM - 4:00 PM ET Monday-Friday
- Alpaca paper API works 24/7 but data may be delayed outside market hours
- Test with `curl http://localhost:8000/api/trading/quote/AAPL`

## 📚 API Documentation

Interactive docs available at: http://localhost:8000/docs

## 🏆 Current Status

✅ **FULLY OPERATIONAL** for paper trading with live market data!

**Account:**
- Starting Capital: $100,000
- Slippage: 5 bps (0.05%)
- Commission: $0.005 per share

**Features Working:**
- Real-time market data from Alpaca
- Paper trading with P&L calculation
- WebSocket streaming to Swift UI
- Full REST API for trading operations
- Account and position tracking

**What You Can Do:**
- Subscribe to stock symbols
- View real-time quotes
- Place market and limit orders
- Track positions and P&L
- View trade history
- All through your native macOS app!

---

## 🎮 Let's Trade!

Your paper trading platform is ready. Open the Swift app, connect to the backend, and start trading with live market data! 🚀

**Quick Test:**
1. Start backend: `./start-server.sh`
2. Open Swift app in Xcode
3. Subscribe to AAPL
4. Watch the real-time quotes
5. Place a test order
6. See your position and P&L update

Happy trading! 📈
