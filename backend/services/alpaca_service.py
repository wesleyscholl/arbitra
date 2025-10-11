"""
Alpaca Market Data Service

Provides real-time and historical market data from Alpaca Markets API.
Uses configured API keys from environment for paper trading.
"""

import asyncio
import ssl
import os
from decimal import Decimal
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import logging

# Disable SSL verification for development (corporate proxy)
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Monkey patch SSL to disable verification
import ssl
_create_unverified_https_context = ssl._create_unverified_context
ssl._create_default_https_context = _create_unverified_https_context

# Also disable for requests library
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import create_urllib3_context

class SSLAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        context = create_urllib3_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        kwargs['ssl_context'] = context
        return super().init_poolmanager(*args, **kwargs)

# Patch requests session globally
original_session_init = requests.Session.__init__
def patched_session_init(self, *args, **kwargs):
    original_session_init(self, *args, **kwargs)
    self.mount('https://', SSLAdapter())
    self.verify = False

requests.Session.__init__ = patched_session_init

from alpaca.data.historical import StockHistoricalDataClient, CryptoHistoricalDataClient
from alpaca.data.live import StockDataStream, CryptoDataStream
from alpaca.data.requests import (
    StockLatestQuoteRequest,
    StockBarsRequest,
    CryptoLatestQuoteRequest,
    CryptoBarsRequest,
)
from alpaca.data.timeframe import TimeFrame
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetAssetsRequest
from alpaca.trading.enums import AssetClass

logger = logging.getLogger(__name__)


def is_crypto_symbol(symbol: str) -> bool:
    """
    Determine if a symbol is cryptocurrency based on format.
    
    Args:
        symbol: Symbol to check (e.g., 'BTC/USD', 'AAPL')
    
    Returns:
        True if crypto, False if stock
    """
    # Crypto symbols typically contain a slash (BTC/USD, ETH/USD)
    return '/' in symbol


class AlpacaMarketDataService:
    """Service for fetching market data (stocks & crypto) from Alpaca."""

    def __init__(self, api_key: str, secret_key: str, paper: bool = True):
        """
        Initialize Alpaca market data service for both stocks and crypto.

        Args:
            api_key: Alpaca API key
            secret_key: Alpaca secret key
            paper: Use paper trading endpoint (default: True)
        """
        self.api_key = api_key
        self.secret_key = secret_key
        self.paper = paper

        # Stock historical data client
        self.stock_data_client = StockHistoricalDataClient(api_key, secret_key)
        
        # Crypto historical data client
        self.crypto_data_client = CryptoHistoricalDataClient(api_key, secret_key)

        # Trading client for account info
        self.trading_client = TradingClient(
            api_key, secret_key, paper=paper
        )

        # Live data streams (stocks and crypto separate)
        self.stock_stream: Optional[StockDataStream] = None
        self.crypto_stream: Optional[CryptoDataStream] = None
        self._stream_handlers: Dict[str, List] = {}

        logger.info(f"AlpacaMarketDataService initialized for STOCKS & CRYPTO (paper={paper})")

    async def get_latest_quote(self, symbol: str) -> Dict[str, Any]:
        """
        Get the latest quote for a symbol (stock or crypto).

        Args:
            symbol: Stock symbol (e.g., 'AAPL') or crypto pair (e.g., 'BTC/USD')

        Returns:
            Dict with bid/ask prices and sizes
        """
        try:
            if is_crypto_symbol(symbol):
                # Crypto quote
                request = CryptoLatestQuoteRequest(symbol_or_symbols=symbol)
                quotes = self.crypto_data_client.get_crypto_latest_quote(request)
                quote = quotes[symbol]
                
                return {
                    "symbol": symbol,
                    "bid_price": float(quote.bid_price),
                    "bid_size": float(quote.bid_size),  # Crypto can have fractional sizes
                    "ask_price": float(quote.ask_price),
                    "ask_size": float(quote.ask_size),  # Crypto can have fractional sizes
                    "timestamp": quote.timestamp.isoformat(),
                    "asset_type": "crypto"
                }
            else:
                # Stock quote
                request = StockLatestQuoteRequest(symbol_or_symbols=symbol)
                quotes = self.stock_data_client.get_stock_latest_quote(request)
                quote = quotes[symbol]
                
                return {
                    "symbol": symbol,
                    "bid_price": float(quote.bid_price),
                    "bid_size": int(quote.bid_size),
                    "ask_price": float(quote.ask_price),
                    "ask_size": int(quote.ask_size),
                    "timestamp": quote.timestamp.isoformat(),
                    "asset_type": "stock"
                }

        except Exception as e:
            logger.error(f"Error fetching quote for {symbol}: {e}")
            raise

    async def get_bars(
        self,
        symbol: str,
        timeframe: str = "1Min",
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Get historical bars for a symbol (stock or crypto).

        Args:
            symbol: Stock symbol (e.g., 'AAPL') or crypto pair (e.g., 'BTC/USD')
            timeframe: Bar timeframe (1Min, 5Min, 15Min, 1Hour, 1Day)
            start: Start datetime (default: 24 hours ago)
            end: End datetime (default: now)
            limit: Max number of bars (default: 100)

        Returns:
            List of bar data dicts
        """
        try:
            # Convert timeframe string to TimeFrame enum
            timeframe_map = {
                "1Min": TimeFrame.Minute,
                "5Min": TimeFrame(5, "Min"),
                "15Min": TimeFrame(15, "Min"),
                "1Hour": TimeFrame.Hour,
                "1Day": TimeFrame.Day,
            }

            tf = timeframe_map.get(timeframe, TimeFrame.Minute)

            # Default time range
            if not start:
                start = datetime.now() - timedelta(days=1)
            if not end:
                end = datetime.now()

            result = []
            
            if is_crypto_symbol(symbol):
                # Crypto bars
                request = CryptoBarsRequest(
                    symbol_or_symbols=symbol,
                    timeframe=tf,
                    start=start,
                    end=end,
                    limit=limit,
                )
                bars = self.crypto_data_client.get_crypto_bars(request)
                
                for bar in bars[symbol]:
                    result.append(
                        {
                            "timestamp": bar.timestamp.isoformat(),
                            "open": float(bar.open),
                            "high": float(bar.high),
                            "low": float(bar.low),
                            "close": float(bar.close),
                            "volume": float(bar.volume),  # Crypto can have fractional volume
                            "vwap": float(bar.vwap) if bar.vwap else None,
                            "trade_count": bar.trade_count,
                            "asset_type": "crypto"
                        }
                    )
            else:
                # Stock bars
                request = StockBarsRequest(
                    symbol_or_symbols=symbol,
                    timeframe=tf,
                    start=start,
                    end=end,
                    limit=limit,
                )
                bars = self.stock_data_client.get_stock_bars(request)
                
                for bar in bars[symbol]:
                    result.append(
                        {
                            "timestamp": bar.timestamp.isoformat(),
                            "open": float(bar.open),
                            "high": float(bar.high),
                            "low": float(bar.low),
                            "close": float(bar.close),
                            "volume": int(bar.volume),
                            "vwap": float(bar.vwap) if bar.vwap else None,
                            "trade_count": bar.trade_count,
                            "asset_type": "stock"
                        }
                    )

            logger.info(f"Fetched {len(result)} bars for {symbol}")
            return result

        except Exception as e:
            logger.error(f"Error fetching bars for {symbol}: {e}")
            raise

    async def get_account_info(self) -> Dict[str, Any]:
        """
        Get account information.

        Returns:
            Dict with account balance, buying power, etc.
        """
        try:
            account = self.trading_client.get_account()

            return {
                "id": account.id,
                "account_number": account.account_number,
                "status": account.status.value,
                "currency": account.currency,
                "cash": float(account.cash),
                "buying_power": float(account.buying_power),
                "portfolio_value": float(account.portfolio_value),
                "equity": float(account.equity),
                "last_equity": float(account.last_equity),
                "long_market_value": float(account.long_market_value),
                "short_market_value": float(account.short_market_value),
                "initial_margin": float(account.initial_margin),
                "maintenance_margin": float(account.maintenance_margin),
                "daytrade_count": account.daytrade_count,
                "daytrading_buying_power": float(account.daytrading_buying_power),
                "pattern_day_trader": account.pattern_day_trader,
            }

        except Exception as e:
            logger.error(f"Error fetching account info: {e}")
            raise

    async def get_positions(self) -> List[Dict[str, Any]]:
        """
        Get current positions from Alpaca account.

        Returns:
            List of position dicts
        """
        try:
            positions = self.trading_client.get_all_positions()

            result = []
            for pos in positions:
                result.append(
                    {
                        "symbol": pos.symbol,
                        "quantity": float(pos.qty),
                        "side": pos.side.value,
                        "entry_price": float(pos.avg_entry_price),
                        "current_price": float(pos.current_price),
                        "market_value": float(pos.market_value),
                        "cost_basis": float(pos.cost_basis),
                        "unrealized_pl": float(pos.unrealized_pl),
                        "unrealized_plpc": float(pos.unrealized_plpc),
                        "unrealized_intraday_pl": float(pos.unrealized_intraday_pl),
                        "unrealized_intraday_plpc": float(
                            pos.unrealized_intraday_plpc
                        ),
                    }
                )

            logger.info(f"Fetched {len(result)} positions")
            return result

        except Exception as e:
            logger.error(f"Error fetching positions: {e}")
            raise

    async def search_assets(
        self, query: str, asset_class: str = "us_equity"
    ) -> List[Dict[str, Any]]:
        """
        Search for tradeable assets.

        Args:
            query: Search query (symbol or name)
            asset_class: Asset class filter (default: us_equity)

        Returns:
            List of asset dicts
        """
        try:
            # Map string to enum
            class_map = {
                "us_equity": AssetClass.US_EQUITY,
                "crypto": AssetClass.CRYPTO,
            }

            request = GetAssetsRequest(
                asset_class=class_map.get(asset_class, AssetClass.US_EQUITY)
            )

            assets = self.trading_client.get_all_assets(request)

            # Filter by query
            query_upper = query.upper()
            result = []

            for asset in assets:
                if (
                    query_upper in asset.symbol.upper()
                    or query_upper in asset.name.upper()
                ):
                    if asset.tradable:  # Only tradeable assets
                        result.append(
                            {
                                "symbol": asset.symbol,
                                "name": asset.name,
                                "exchange": asset.exchange.value,
                                "asset_class": asset.asset_class.value,
                                "tradable": asset.tradable,
                                "marginable": asset.marginable,
                                "shortable": asset.shortable,
                                "easy_to_borrow": asset.easy_to_borrow,
                                "fractionable": asset.fractionable,
                            }
                        )

            logger.info(f"Found {len(result)} assets matching '{query}'")
            return result[:50]  # Limit results

        except Exception as e:
            logger.error(f"Error searching assets: {e}")
            raise

    async def start_stream(self, symbols: List[str]):
        """
        Start streaming real-time data for symbols.

        Args:
            symbols: List of symbols to stream
        """
        if self.stream:
            logger.warning("Stream already running")
            return

        self.stream = StockDataStream(self.api_key, self.secret_key)

        # Subscribe to trades
        async def handle_trade(data):
            handlers = self._stream_handlers.get("trade", [])
            for handler in handlers:
                await handler(
                    {
                        "type": "trade",
                        "symbol": data.symbol,
                        "price": float(data.price),
                        "size": int(data.size),
                        "timestamp": data.timestamp.isoformat(),
                    }
                )

        # Subscribe to quotes
        async def handle_quote(data):
            handlers = self._stream_handlers.get("quote", [])
            for handler in handlers:
                await handler(
                    {
                        "type": "quote",
                        "symbol": data.symbol,
                        "bid_price": float(data.bid_price),
                        "bid_size": int(data.bid_size),
                        "ask_price": float(data.ask_price),
                        "ask_size": int(data.ask_size),
                        "timestamp": data.timestamp.isoformat(),
                    }
                )

        for symbol in symbols:
            self.stream.subscribe_trades(handle_trade, symbol)
            self.stream.subscribe_quotes(handle_quote, symbol)

        logger.info(f"Starting stream for {len(symbols)} symbols")

        # Run stream in background
        asyncio.create_task(self.stream._run_forever())

    async def stop_stream(self):
        """Stop the real-time data stream."""
        if self.stream:
            await self.stream.close()
            self.stream = None
            logger.info("Stream stopped")

    def add_stream_handler(self, event_type: str, handler):
        """
        Add a handler for stream events.

        Args:
            event_type: 'trade' or 'quote'
            handler: Async function to call with event data
        """
        if event_type not in self._stream_handlers:
            self._stream_handlers[event_type] = []

        self._stream_handlers[event_type].append(handler)
        logger.info(f"Added handler for {event_type} events")

    def remove_stream_handler(self, event_type: str, handler):
        """Remove a stream event handler."""
        if event_type in self._stream_handlers:
            try:
                self._stream_handlers[event_type].remove(handler)
                logger.info(f"Removed handler for {event_type} events")
            except ValueError:
                pass

    async def close(self):
        """Clean up resources."""
        await self.stop_stream()
        logger.info("AlpacaMarketDataService closed")
