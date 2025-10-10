"""
AI Trading Agent Service

Automated trading agent that generates signals and executes paper trades 24/7.
Uses OpenRouter API for signal generation based on market data.
"""

import asyncio
import os
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Optional
import json

import httpx
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()


class TradingAgent:
    """
    Autonomous trading agent that:
    1. Monitors market data
    2. Generates AI signals via OpenRouter
    3. Executes paper trades
    4. Manages positions
    """

    def __init__(
        self,
        alpaca_service,
        paper_engine,
        websocket_manager,
        openrouter_api_key: str,
        model: str = "anthropic/claude-3.5-sonnet",
    ):
        """
        Initialize trading agent.

        Args:
            alpaca_service: Alpaca market data service
            paper_engine: Paper trading engine
            websocket_manager: WebSocket manager for broadcasting
            openrouter_api_key: OpenRouter API key
            model: AI model to use for signal generation
        """
        self.alpaca = alpaca_service
        self.engine = paper_engine
        self.ws_manager = websocket_manager
        self.openrouter_api_key = openrouter_api_key
        self.model = model

        # Agent configuration
        self.watchlist = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]
        self.scan_interval = 300  # 5 minutes
        self.signal_threshold = 0.65  # Minimum confidence to act
        self.max_position_size = Decimal("10000")  # Max $10k per position
        self.max_positions = 5

        # State
        self.running = False
        self.last_scan_time = None
        self.signal_history: List[Dict] = []

        logger.info(f"Trading agent initialized with model: {model}")

    async def start(self):
        """Start the trading agent."""
        if self.running:
            logger.warning("Agent already running")
            return

        self.running = True
        logger.info("🤖 Trading agent started")

        # Broadcast status
        try:
            await self.ws_manager.broadcast(
                {
                    "type": "agent_status",
                    "data": {"status": "started", "timestamp": datetime.now().isoformat()},
                }
            )
        except:
            pass

        # Start main loop
        await self._main_loop()

    async def stop(self):
        """Stop the trading agent."""
        self.running = False
        logger.info("🛑 Trading agent stopped")

        # Broadcast status
        try:
            await self.ws_manager.broadcast(
                {
                    "type": "agent_status",
                    "data": {"status": "stopped", "timestamp": datetime.now().isoformat()},
                }
            )
        except:
            pass

    async def _main_loop(self):
        """Main agent loop - runs continuously."""
        while self.running:
            try:
                await self._scan_and_trade()
                await asyncio.sleep(self.scan_interval)

            except Exception as e:
                logger.error(f"Error in agent main loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error

    async def _scan_and_trade(self):
        """Scan watchlist and execute trades based on AI signals."""
        logger.info("📊 Scanning watchlist for trading opportunities...")

        self.last_scan_time = datetime.now()

        for symbol in self.watchlist:
            try:
                # Skip if we already have a position
                current_positions = self.engine.get_positions()
                if any(p["symbol"] == symbol for p in current_positions):
                    logger.debug(f"Skipping {symbol} - already have position")
                    continue

                # Skip if we're at max positions
                if len(current_positions) >= self.max_positions:
                    logger.info(f"At max positions ({self.max_positions}), skipping scan")
                    break

                # Get market data
                quote = await self.alpaca.get_latest_quote(symbol)
                bars = await self.alpaca.get_bars(
                    symbol, timeframe="1Day", limit=30
                )

                # Generate AI signal
                signal = await self._generate_signal(symbol, quote, bars)

                # Log signal
                self.signal_history.append(signal)

                # Broadcast signal
                try:
                    await self.ws_manager.broadcast(
                        {"type": "ai_signal", "data": signal}
                    )
                except:
                    pass

                # Act on signal if confidence is high enough
                if signal["confidence"] >= self.signal_threshold:
                    await self._execute_signal(signal, quote)

            except Exception as e:
                logger.error(f"Error scanning {symbol}: {e}")
                continue

    async def _generate_signal(
        self, symbol: str, quote: Dict, bars: List[Dict]
    ) -> Dict:
        """
        Generate trading signal using AI.

        Args:
            symbol: Stock symbol
            quote: Latest quote data
            bars: Historical bar data

        Returns:
            Signal dict with type, confidence, reasoning
        """
        try:
            # Calculate technical indicators
            prices = [bar["close"] for bar in bars]
            current_price = (quote["bid_price"] + quote["ask_price"]) / 2

            # Simple moving averages
            sma_5 = sum(prices[-5:]) / 5 if len(prices) >= 5 else current_price
            sma_20 = sum(prices[-20:]) / 20 if len(prices) >= 20 else current_price

            # Price change
            price_change_1d = (
                ((current_price - prices[-1]) / prices[-1] * 100)
                if len(prices) > 0
                else 0
            )
            price_change_5d = (
                ((current_price - prices[-5]) / prices[-5] * 100)
                if len(prices) >= 5
                else 0
            )

            # Create AI prompt
            prompt = f"""You are an expert trading algorithm. Analyze this market data and provide a trading signal.

Symbol: {symbol}
Current Price: ${current_price:.2f}
Bid/Ask: ${quote['bid_price']:.2f} / ${quote['ask_price']:.2f}

Technical Indicators:
- 5-day SMA: ${sma_5:.2f}
- 20-day SMA: ${sma_20:.2f}
- 1-day change: {price_change_1d:+.2f}%
- 5-day change: {price_change_5d:+.2f}%

Recent Price Action (last 10 days):
{json.dumps([{"close": bar["close"], "volume": bar["volume"], "timestamp": bar["timestamp"]} for bar in bars[-10:]], indent=2)}

Based on this data, should we BUY, SELL, or HOLD?

Respond in JSON format:
{{
  "signal": "BUY" | "SELL" | "HOLD",
  "confidence": 0.0-1.0,
  "reasoning": "Brief explanation of your decision",
  "target_size": "shares to trade (integer)"
}}

Consider:
- Trend direction (SMA crossovers)
- Momentum (recent price changes)
- Volume patterns
- Risk/reward ratio

Be conservative - only suggest BUY with high confidence."""

            # Call OpenRouter API
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.openrouter_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "user",
                                "content": prompt,
                            }
                        ],
                        "temperature": 0.3,  # Lower temperature for more consistent signals
                        "max_tokens": 500,
                    },
                )

            if response.status_code != 200:
                logger.error(f"OpenRouter API error: {response.status_code}")
                return self._fallback_signal(symbol, current_price)

            # Parse AI response
            result = response.json()
            ai_response = result["choices"][0]["message"]["content"]

            # Extract JSON from response
            try:
                # Try to find JSON in the response
                start = ai_response.find("{")
                end = ai_response.rfind("}") + 1
                ai_signal = json.loads(ai_response[start:end])

                return {
                    "symbol": symbol,
                    "signal_type": ai_signal["signal"].lower(),
                    "confidence": float(ai_signal["confidence"]),
                    "reasoning": ai_signal["reasoning"],
                    "target_size": int(ai_signal.get("target_size", 10)),
                    "current_price": current_price,
                    "timestamp": datetime.now().isoformat(),
                    "model": self.model,
                    "indicators": {
                        "sma_5": sma_5,
                        "sma_20": sma_20,
                        "price_change_1d": price_change_1d,
                        "price_change_5d": price_change_5d,
                    },
                }

            except (json.JSONDecodeError, KeyError) as e:
                logger.error(f"Error parsing AI response: {e}")
                logger.debug(f"AI Response: {ai_response}")
                return self._fallback_signal(symbol, current_price)

        except Exception as e:
            logger.error(f"Error generating AI signal: {e}")
            return self._fallback_signal(symbol, current_price)

    def _fallback_signal(self, symbol: str, price: float) -> Dict:
        """Generate a conservative fallback signal on AI failure."""
        return {
            "symbol": symbol,
            "signal_type": "hold",
            "confidence": 0.0,
            "reasoning": "AI signal generation failed - defaulting to HOLD",
            "target_size": 0,
            "current_price": price,
            "timestamp": datetime.now().isoformat(),
            "model": "fallback",
            "indicators": {},
        }

    async def _execute_signal(self, signal: Dict, quote: Dict):
        """
        Execute a trading signal.

        Args:
            signal: AI-generated signal
            quote: Current quote data
        """
        symbol = signal["symbol"]
        signal_type = signal["signal_type"]
        confidence = signal["confidence"]
        target_size = signal["target_size"]

        logger.info(
            f"🎯 Executing {signal_type.upper()} signal for {symbol} "
            f"(confidence: {confidence:.2%})"
        )

        try:
            if signal_type == "buy":
                # Calculate position size (don't exceed max)
                current_price = Decimal(str(signal["current_price"]))
                position_value = current_price * Decimal(str(target_size))

                if position_value > self.max_position_size:
                    target_size = int(self.max_position_size / current_price)

                # Check if we have enough cash
                account = self.engine.get_account_info()
                if Decimal(str(account["cash"])) < position_value:
                    logger.warning(f"Insufficient funds for {symbol} trade")
                    return

                # Submit buy order
                order = self.engine.submit_order(
                    symbol=symbol,
                    side="buy",
                    quantity=Decimal(str(target_size)),
                    order_type="market",
                )

                # Fill immediately (market order)
                mid_price = Decimal(
                    str((quote["bid_price"] + quote["ask_price"]) / 2)
                )
                trade = self.engine.fill_order(order["order_id"], mid_price)

                if trade:
                    logger.info(
                        f"✅ Bought {target_size} shares of {symbol} @ ${mid_price:.2f}"
                    )

                    # Broadcast trade
                    try:
                        await self.ws_manager.broadcast(
                            {"type": "trade_executed", "data": trade}
                        )
                    except:
                        pass

            elif signal_type == "sell":
                # Check if we have a position
                position = self.engine.get_position(symbol)
                if not position:
                    logger.debug(f"No position to sell for {symbol}")
                    return

                # Submit sell order for full position
                quantity = Decimal(str(position["quantity"]))
                order = self.engine.submit_order(
                    symbol=symbol,
                    side="sell",
                    quantity=quantity,
                    order_type="market",
                )

                # Fill immediately
                mid_price = Decimal(
                    str((quote["bid_price"] + quote["ask_price"]) / 2)
                )
                trade = self.engine.fill_order(order["order_id"], mid_price)

                if trade:
                    logger.info(
                        f"✅ Sold {quantity} shares of {symbol} @ ${mid_price:.2f}"
                    )

                    # Broadcast trade
                    try:
                        await self.ws_manager.broadcast(
                            {"type": "trade_executed", "data": trade}
                        )
                    except:
                        pass

        except Exception as e:
            logger.error(f"Error executing signal for {symbol}: {e}")

    def get_status(self) -> Dict:
        """Get agent status."""
        return {
            "running": self.running,
            "watchlist": self.watchlist,
            "scan_interval": self.scan_interval,
            "signal_threshold": self.signal_threshold,
            "max_positions": self.max_positions,
            "max_position_size": float(self.max_position_size),
            "last_scan_time": self.last_scan_time.isoformat()
            if self.last_scan_time
            else None,
            "total_signals": len(self.signal_history),
        }

    def get_recent_signals(self, limit: int = 10) -> List[Dict]:
        """Get recent signals."""
        return self.signal_history[-limit:]
