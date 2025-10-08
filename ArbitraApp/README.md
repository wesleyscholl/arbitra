# Arbitra macOS App

Native macOS application for monitoring and controlling the Arbitra algorithmic trading system.

## Features

- **Real-time Dashboard**: Portfolio overview with performance charts
- **Position Management**: View and manage open positions with stop-loss controls
- **Trade History**: Complete trade history with filtering and search
- **Performance Analytics**: Comprehensive metrics including Sharpe ratio, win rate, drawdown
- **Paper Trading**: Test strategies with simulated trading before risking capital
- **Native macOS UI**: Built with Swift and SwiftUI for optimal performance

## Requirements

- macOS 13.0 (Ventura) or later
- Xcode 15.0 or later (for development)
- Arbitra backend running on `localhost:8000`

## Building

### Option 1: Xcode (Recommended)

1. Open the project directory in Xcode:
   ```bash
   cd arbitra
   open .
   ```

2. In Xcode, select **File → New → Project**
3. Choose **macOS → App**
4. Set:
   - Product Name: `Arbitra`
   - Organization Identifier: `com.yourcompany`
   - Interface: SwiftUI
   - Language: Swift
   - Create the project in the `arbitra` directory

5. Add all files from `ArbitraApp/` to the project:
   - Drag the folders into Xcode's project navigator
   - Ensure "Copy items if needed" is checked
   - Add to target: Arbitra

6. Build and run: **⌘R**

### Option 2: Command Line (Swift Package Manager)

```bash
cd arbitra
swift build
swift run ArbitraApp
```

## Project Structure

```
ArbitraApp/
├── ArbitraApp.swift          # Main app entry point
├── Models/
│   ├── AppState.swift         # Global app state
│   ├── Portfolio.swift        # Data models
│   ├── PortfolioState.swift   # Portfolio management
│   └── ConnectionState.swift  # WebSocket connection
├── Services/
│   └── APIService.swift       # Backend API client
└── Views/
    ├── ContentView.swift      # Main navigation
    ├── DashboardView.swift    # Portfolio overview
    ├── PositionsView.swift    # Position management
    ├── HistoryView.swift      # Trade history
    ├── PerformanceView.swift  # Analytics
    └── SettingsView.swift     # Configuration
```

## Configuration

### Backend Connection

By default, the app connects to:
- **API**: `http://localhost:8000`
- **WebSocket**: `ws://localhost:8000/ws`

Change these in **Settings** or via `@AppStorage` defaults.

### Keyboard Shortcuts

- **⌘S**: Start trading
- **⌘⇧S**: Stop trading
- **⌘⌥E**: Emergency stop
- **⌘R**: Refresh data
- **⌘,**: Open settings

## Backend Setup

Ensure the Arbitra backend is running with the required endpoints:

### REST API Endpoints

```
GET  /api/portfolio              # Get current portfolio
GET  /api/trades/recent          # Get recent trades
GET  /api/performance/metrics    # Get performance metrics
POST /api/trading/start          # Start trading
POST /api/trading/stop           # Stop trading
POST /api/trading/emergency-stop # Emergency stop
POST /api/positions/{symbol}/close  # Close position
PUT  /api/positions/{symbol}/stop-loss  # Update stop loss
```

### WebSocket Endpoint

```
WS /ws  # Real-time updates
```

WebSocket message format:
```json
{
  "type": "position_update|trade_executed|alert",
  "data": { ... }
}
```

## Paper Trading

The app supports paper trading mode to test strategies without risking capital:

1. Toggle "Paper Trading" in the toolbar
2. All trades will be simulated
3. Performance metrics track paper vs. live results

See `src/execution/paper_trading.py` for the backend implementation.

## Development

### Adding New Views

1. Create new Swift file in `ArbitraApp/Views/`
2. Add to `AppView` enum in `Models/AppState.swift`
3. Add navigation link in `ContentView.swift` sidebar
4. Add case in `mainContentView` switch statement

### Styling

The app uses SwiftUI with native macOS styling:
- **Colors**: System colors with `.windowBackgroundColor`, `.controlBackgroundColor`
- **Typography**: System fonts with semantic sizes
- **Charts**: Swift Charts framework for performance visualization
- **Icons**: SF Symbols for consistent iconography

### State Management

- **AppState**: Global app state (trading status, navigation, alerts)
- **PortfolioState**: Portfolio data with auto-refresh
- **ConnectionState**: WebSocket connection management

All use `@MainActor` for thread-safe UI updates.

## Troubleshooting

### Connection Issues

- Verify backend is running: `curl http://localhost:8000/api/portfolio`
- Check API URL in Settings
- Review console logs for errors

### Build Issues

- Clean build folder: **⌘⇧K** in Xcode
- Reset package cache: `swift package reset`
- Verify macOS deployment target: 13.0+

### WebSocket Disconnects

- Check backend WebSocket implementation
- Review connection logs in app
- Ensure firewall allows local connections

## Contributing

See main Arbitra repository for contribution guidelines.

## License

[Your License Here]
