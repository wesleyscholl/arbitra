# ✅ Swift App Updated for Paper Trading Backend

## 🔧 Changes Made

### 1. **WebSocket URL Fixed**
- Changed from `ws://localhost:8000/ws` → `ws://localhost:8000/ws/market-data`
- Updated in 3 files:
  - `ConnectionState.swift`
  - `SettingsView.swift` (default value)
  - `SettingsView.swift` (reset function)

### 2. **API Endpoints Updated**
- Created new response models in `APIResponseModels.swift` to match backend API
- Updated `APIService.swift` to use correct endpoints:
  - `/api/trading/account` (was `/api/portfolio`)
  - `/api/trading/positions` (new)
  - `/api/trading/trades` (was `/api/trades/recent`)

### 3. **Model Conversions**
- Added conversion methods to map backend responses to Swift models:
  - `AccountResponse` → `Portfolio`
  - `PositionResponse` → `Position`
  - `TradeResponse` → `Trade`

## 🚀 How to Run (After Updates)

### Step 1: Start the Backend
```bash
cd /Users/wscholl/arbitra
./start-server.sh
```

You should see:
```
✅ Alpaca service initialized
✅ Paper trading engine initialized
✅ Arbitra backend started successfully
```

### Step 2: Run the Swift App
```bash
./run-app.sh
```

### Step 3: **IMPORTANT** - Reset Settings (First Time)
The app cached the old WebSocket URL (`/ws`) in UserDefaults. You need to reset:

1. Open the Arbitra app (use Cmd+Tab if window is hidden)
2. Click the **⚙️ Settings** icon in the sidebar
3. Scroll to the bottom
4. Click **"Reset to Defaults"** button
5. **Quit and restart the app**

This will update:
- API Base URL: `http://localhost:8000`
- WebSocket URL: `ws://localhost:8000/ws/market-data` ✅

### Step 4: Verify Connection
After resetting and restarting, check the terminal running the backend. You should see:
```
INFO:     127.0.0.1:XXXXX - "GET /api/trading/account HTTP/1.1" 200 OK
INFO:     127.0.0.1:XXXXX - "GET /api/trading/positions HTTP/1.1" 200 OK
INFO:     WebSocket connection accepted
```

**No more 404 or 403 errors!**

## 🐛 Troubleshooting

### Still seeing WebSocket errors?
```
Error: "Could not connect to server" at /ws
```

**Solution:** You didn't reset settings. Go to Settings → Reset to Defaults → Restart app.

### Seeing 404 errors?
```
GET /api/portfolio HTTP/1.1" 404 Not Found
```

**Solution:** Old cached endpoints. Reset settings in the app.

### Seeing 403 Forbidden on WebSocket?
```
WebSocket /ws" 403 Forbidden
```

**Solution:** Wrong WebSocket path. Should be `/ws/market-data` not `/ws`. Reset settings.

## ✅ What Should Work Now

Once you reset settings and restart:

1. ✅ **WebSocket Connection** - Real-time updates from backend
2. ✅ **Account Info** - Portfolio value, cash, P&L displayed
3. ✅ **Positions** - All paper trading positions shown
4. ✅ **Trades** - Trade history from paper trading engine
5. ✅ **Real-time Updates** - Price updates via WebSocket

## 📊 Testing the Integration

### Test 1: Check Account Info
The Dashboard should show:
- **Total Value:** $100,000.00 (initial capital)
- **Cash:** $100,000.00
- **Positions:** 0

### Test 2: Place a Paper Trade (via API)
Open a new terminal and run:
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

The Swift app should immediately show:
- Position in AAPL (10 shares)
- Updated cash balance
- Trade in history

### Test 3: WebSocket Real-time Updates
1. In the Swift app, subscribe to a symbol (if there's a subscribe feature)
2. Watch the console - you should see quote updates every 5 seconds
3. Positions should update with current prices

## 📝 Summary

**Before:**
- ❌ WebSocket: `http://localhost:8000/ws` (wrong protocol, wrong path)
- ❌ API: `/api/portfolio` (doesn't exist)
- ❌ API: `/api/trades/recent` (doesn't exist)

**After:**
- ✅ WebSocket: `ws://localhost:8000/ws/market-data`
- ✅ API: `/api/trading/account`
- ✅ API: `/api/trading/positions`
- ✅ API: `/api/trading/trades`

**Action Required:**
1. Start backend: `./start-server.sh`
2. Start app: `./run-app.sh`
3. **Open Settings → Reset to Defaults → Restart**
4. Enjoy paper trading with live data!

---

**Current Status:** Backend running ✅ | Swift app updated ✅ | Settings reset needed ⚠️
