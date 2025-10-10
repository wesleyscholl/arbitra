"""
Test script to verify Alpaca API connection and market data service.

Run from project root: python test_alpaca_connection.py
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from backend.services.alpaca_service import AlpacaMarketDataService


async def test_connection():
    """Test Alpaca API connection and basic functionality."""

    print("🔌 Testing Alpaca API Connection...")
    print("=" * 60)

    # Get credentials from environment
    api_key = os.getenv("ALPACA_API_KEY")
    secret_key = os.getenv("ALPACA_SECRET_KEY")
    base_url = os.getenv("ALPACA_BASE_URL")

    if not api_key or not secret_key:
        print("❌ Error: ALPACA_API_KEY and ALPACA_SECRET_KEY must be set in .env")
        return

    print(f"📡 API Key: {api_key[:8]}...")
    print(f"🌐 Base URL: {base_url}")
    print()

    # Initialize service
    service = AlpacaMarketDataService(
        api_key=api_key, secret_key=secret_key, paper=True
    )

    try:
        # Test 1: Get account info
        print("📊 Test 1: Fetching account information...")
        account = await service.get_account_info()
        print(f"✅ Account ID: {account['account_number']}")
        print(f"   Status: {account['status']}")
        print(f"   Cash: ${account['cash']:,.2f}")
        print(f"   Buying Power: ${account['buying_power']:,.2f}")
        print(f"   Portfolio Value: ${account['portfolio_value']:,.2f}")
        print()

        # Test 2: Get positions
        print("💼 Test 2: Fetching current positions...")
        positions = await service.get_positions()
        if positions:
            print(f"✅ Found {len(positions)} positions:")
            for pos in positions:
                print(
                    f"   {pos['symbol']}: {pos['quantity']} shares @ ${pos['current_price']:.2f}"
                )
                print(
                    f"      Unrealized P&L: ${pos['unrealized_pl']:,.2f} ({pos['unrealized_plpc']:.2%})"
                )
        else:
            print("✅ No open positions")
        print()

        # Test 3: Get latest quote
        print("💹 Test 3: Fetching latest quote for AAPL...")
        quote = await service.get_latest_quote("AAPL")
        print(f"✅ AAPL Quote:")
        print(f"   Bid: ${quote['bid_price']:.2f} x {quote['bid_size']}")
        print(f"   Ask: ${quote['ask_price']:.2f} x {quote['ask_size']}")
        print(f"   Timestamp: {quote['timestamp']}")
        print()

        # Test 4: Get historical bars
        print("📈 Test 4: Fetching historical bars for AAPL (last 10 bars)...")
        bars = await service.get_bars("AAPL", timeframe="5Min", limit=10)
        print(f"✅ Fetched {len(bars)} bars:")
        for i, bar in enumerate(bars[-5:], 1):  # Show last 5
            print(
                f"   {i}. {bar['timestamp']} - O:{bar['open']:.2f} H:{bar['high']:.2f} L:{bar['low']:.2f} C:{bar['close']:.2f} V:{bar['volume']:,}"
            )
        print()

        # Test 5: Search assets
        print("🔍 Test 5: Searching for assets matching 'Apple'...")
        assets = await service.search_assets("Apple")
        print(f"✅ Found {len(assets)} assets:")
        for asset in assets[:5]:  # Show first 5
            print(
                f"   {asset['symbol']}: {asset['name']} ({asset['exchange']})"
            )
        print()

        print("=" * 60)
        print("✅ All tests passed! Alpaca connection working.")
        print()
        print("Next steps:")
        print("  1. Paper Trading Engine - Track virtual positions")
        print("  2. AI Signal Generation - OpenRouter integration")
        print("  3. FastAPI Endpoints - REST API for Swift UI")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()

    finally:
        await service.close()


if __name__ == "__main__":
    asyncio.run(test_connection())
