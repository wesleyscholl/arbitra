# Arbitra macOS App - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies

```bash
# Install Python dependencies for backend stub
pip install fastapi uvicorn websockets pydantic
```

### Step 2: Start the Backend API Stub

```bash
cd arbitra
python api_stub.py
```

You should see:
```
🚀 Starting Arbitra API Stub...
📡 API: http://localhost:8000
🔌 WebSocket: ws://localhost:8000/ws
📚 Docs: http://localhost:8000/docs
```

### Step 3: Build the macOS App

**Option A: Xcode (Recommended)**

```bash
# Run setup script
./setup-xcode.sh

# Open Xcode
open .
```

Then in Xcode:
1. File → New → Project
2. macOS → App
3. Name: Arbitra, Interface: SwiftUI, Language: Swift
4. Drag ArbitraApp folder into project
5. Press ⌘R to build and run

**Option B: Command Line**

```bash
# Build
swift build

# Run
swift run ArbitraApp
```

### Step 4: Use the App

1. App should open with Dashboard view
2. Toggle "Paper Trading" mode (recommended for testing)
3. Click "Start Trading" or press ⌘S
4. Explore:
   - **Dashboard**: Portfolio overview and recent activity
   - **Positions**: View and manage open positions
   - **History**: Browse trade history with filters
   - **Performance**: Analyze metrics and charts
   - **Settings**: Configure API, notifications, and risk limits

### Keyboard Shortcuts

- **⌘S**: Start trading
- **⌘⇧S**: Stop trading
- **⌘⌥E**: Emergency stop (close all positions)
- **⌘R**: Refresh data
- **⌘,**: Open settings
- **⌘W**: Close window
- **⌘Q**: Quit app

## 📊 What You'll See

### Dashboard
- Portfolio summary cards (Total Value, Daily P/L, Total P/L, Cash)
- Performance chart showing portfolio value over time
- Asset allocation breakdown (Foundation, Growth, Opportunity tiers)
- Active positions list
- Recent trades

### Positions
- Search and filter positions
- Sort by Symbol, Value, P/L, or P/L %
- Click any position to:
  - View detailed information
  - Update stop loss
  - Close position

### History
- Complete trade history
- Filter by action (Buy/Sell) or date range
- Sort by date or P/L
- View detailed trade information including fees and slippage

### Performance
- Toggle timeframes (1D, 1W, 1M, 3M, 1Y, All)
- View metrics: Win Rate, Sharpe Ratio, Max Drawdown
- Interactive charts with multiple metric types
- Trade statistics and risk metrics
- Asset tier performance breakdown

### Settings
- Configure API endpoints
- Set refresh interval
- Enable/disable notifications
- Set risk limits (max position size, max daily loss, etc.)
- Customize display preferences

## 🧪 Testing with Mock Data

The `api_stub.py` provides realistic mock data:

- **Portfolio**: $52,350 total value with 3 positions (AAPL, MSFT, NVDA)
- **Trade History**: 2 recent closed trades (TSLA win, GOOGL loss)
- **Performance**: 47 total trades, 68% win rate, 1.85 Sharpe ratio
- **WebSocket**: Live price updates every 5 seconds

## 🔧 Troubleshooting

### "Cannot connect to API"
- Ensure backend is running: `python api_stub.py`
- Check API URL in Settings (should be `http://localhost:8000`)
- Test connection: Settings → Test Connection

### "Build failed" in Xcode
- Ensure macOS deployment target is 13.0+
- Clean build folder: ⌘⇧K
- Verify all files are added to target

### "WebSocket disconnected"
- Backend must be running
- Check WebSocket URL in Settings
- Look for errors in Xcode console

### Swift build errors
```bash
# Reset package cache
swift package reset

# Clean build
rm -rf .build
swift build
```

## 📝 Next Steps

1. **Integrate Real Backend**: Replace `api_stub.py` with actual Arbitra backend
2. **Customize UI**: Modify views to match your preferences
3. **Add Features**: Implement export, advanced charts, etc.
4. **Deploy**: Build release version for distribution

## 🔗 Resources

- **API Documentation**: http://localhost:8000/docs (when stub is running)
- **SwiftUI Documentation**: https://developer.apple.com/swiftui/
- **Swift Charts**: https://developer.apple.com/documentation/charts
- **Implementation Details**: See `ArbitraApp/IMPLEMENTATION.md`

## 💡 Tips

- Always test in Paper Trading mode first
- Use keyboard shortcuts for efficiency
- Monitor WebSocket connection status in toolbar
- Export trade history regularly for analysis
- Set conservative risk limits initially

---

**Ready to trade!** 🎉 Start the backend stub, build the app, and begin monitoring your portfolio with a native macOS experience.
