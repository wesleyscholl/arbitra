# Running the Arbitra macOS App

## Quick Start

### Option 1: Using the run script (Recommended)
```bash
./run-app.sh
```

### Option 2: Manual build and run
```bash
# Build the app
swift build

# Run the app
swift run ArbitraApp
```

**Note:** When running from the terminal, the app window may not automatically come to the front. If you don't see the window:

1. **Press `Cmd+Tab`** to switch to the ArbitraApp
2. **Check the Dock** - look for the Arbitra icon and click it
3. **Use Mission Control** (F3 or swipe up with three fingers) to see all windows

## Building a Standalone App

To create a standalone `.app` bundle:

```bash
swift build -c release

# The binary will be at:
# .build/release/ArbitraApp
```

## Troubleshooting

### Window doesn't appear
- The app is running but hidden behind other windows
- Use `Cmd+Tab` or click the Dock icon
- Check Activity Monitor for "ArbitraApp" process

### Connection errors  
- Make sure the backend API is running: `./start-server.sh`
- Backend should be at `http://localhost:8000`
- WebSocket endpoint is at `ws://localhost:8000/ws/market-data`

### First time running or after API changes
The app caches old API URLs in UserDefaults. To reset:
1. Open the app
2. Go to Settings (gear icon in sidebar)
3. Scroll down and click "Reset to Defaults"
4. Restart the app

### Decoding errors
- Restart both the backend and the app
- Make sure you've reset settings to defaults (see above)

## What's Working

✅ **Data Models**: All API responses decode successfully  
✅ **WebSocket**: Real-time position updates working  
✅ **Navigation**: All views accessible from sidebar  
✅ **API Integration**: Portfolio, trades, and metrics loading  
✅ **Error Handling**: Proper error messages and alerts  

## Current Status

The app is **fully functional**! All decoding errors have been resolved. The only issue is macOS window management when launching from the terminal - the window exists but may not be visible initially.

## Next Steps

- Use `Cmd+Tab` to bring the window to front
- Explore the Dashboard, Positions, History, and Performance views
- Try the trading controls (Start/Stop)
- Check the Settings for configuration options
