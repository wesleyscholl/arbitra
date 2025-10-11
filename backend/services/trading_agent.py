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
import re

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

        # Agent configuration - mixed watchlist of stocks and crypto
        self.watchlist = [
            # Stocks
            # "AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "NVDA", "META", "NFLX", "INTC", "AMD", "PYPL", "ADBE", "CSCO", "CRM", "ORCL", "IBM", "QCOM", "TXN", "AVGO", "AMAT", "NOW", "INTU", "LRCX", "FISV", "ADP", "MU", "BKNG", "ZM", "DOCU", "SNOW", "SPOT", "TWTR", "UBER", "LYFT", "PINS", "SQ", "WORK", "TEAM", "FSLY", "CRWD", "OKTA", "ZS", "DDOG", "NET", "PLTR", "ROKU", "ETSY", "BIDU",
            # Crypto
            "BTC/USD", "ETH/USD", "SOL/USD", "DOGE/USD", "LTC/USD", "ADA/USD", "AVAX/USD", "MATIC/USD", "SHIB/USD", "BNB/USD", "LINK/USD"
        ]

        # Read from env or use defaults
        self.scan_interval = int(os.getenv("AI_SCAN_INTERVAL", 120))  # 2 minutes
        self.signal_threshold = float(os.getenv("AI_SIGNAL_THRESHOLD", 0.7))  # Minimum confidence to act
        self.max_position_size = Decimal(os.getenv("AI_MAX_POSITION_SIZE", "10000"))  # Max $10k per position
        self.max_positions = int(os.getenv("AI_MAX_POSITIONS", 10))  # Max 10 concurrent positions

        # State
        self.running = False
        self.last_scan_time = None
        self.signal_history: List[Dict] = []

        logger.info(f"Trading agent initialized with model: {model} (stocks & crypto)")

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

        # Start main loop in background task (don't await it)
        asyncio.create_task(self._main_loop())

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

            # Determine asset type for context
            asset_type = quote.get('asset_type', 'stock')
            asset_label = "Cryptocurrency" if asset_type == 'crypto' else "Stock"
            unit_label = "coins" if asset_type == 'crypto' else "shares"
            
            # Create AI prompt with asset-aware context
            prompt = f"""You are an expert trading algorithm. Analyze this {asset_label.lower()} market data and provide a trading signal.

{asset_label}: {symbol}
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
  "target_size": "{unit_label} to trade (integer or decimal)"
}}

Consider:
- Trend direction (SMA crossovers)
- Momentum (recent price changes)
- Volume patterns
- Risk/reward ratio
{"- High volatility typical of crypto markets" if asset_type == 'crypto' else "- Market hours and traditional trading patterns"}
{"- 24/7 trading availability" if asset_type == 'crypto' else ""}

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
            # Check response status and log body on error
            if response.status_code != 200:
                # Log response body for debugging
                try:
                    text = response.text
                except Exception:
                    text = "(unable to read response body)"

                logger.error(
                    f"OpenRouter API error: {response.status_code} - response body: {text}"
                )
                return self._fallback_signal(symbol, current_price)

            # Parse AI response
            result = response.json()
            # Expecting chat-like structure; be defensive
            try:
                ai_response = result["choices"][0]["message"]["content"]
            except Exception:
                # Fallback: stringify full result
                ai_response = json.dumps(result)

            # Extract JSON from response robustly and map common key names
            try:
                # First attempt: naive bracket matching
                start = ai_response.find("{")
                end = ai_response.rfind("}") + 1
                json_text = ai_response[start:end] if start != -1 and end != -1 else None

                ai_signal = None
                if json_text:
                    try:
                        ai_signal = json.loads(json_text)
                    except json.JSONDecodeError:
                        ai_signal = None

                # If naive parse failed, try regex extraction (DOTALL)
                if ai_signal is None:
                    m = re.search(r"\{.*\}", ai_response, re.DOTALL)
                    if m:
                        try:
                            ai_signal = json.loads(m.group(0))
                        except json.JSONDecodeError:
                            ai_signal = None

                if not ai_signal:
                    raise ValueError("Could not extract JSON from AI response")

                # Flexible key mapping to tolerate different model outputs
                signal_raw = ai_signal.get("signal") or ai_signal.get("signal_type") or ai_signal.get("action")
                confidence_raw = ai_signal.get("confidence") or ai_signal.get("score") or ai_signal.get("confidence_score")
                reasoning_raw = ai_signal.get("reasoning") or ai_signal.get("explanation") or ai_signal.get("reason") or ""
                target_size_raw = ai_signal.get("target_size") or ai_signal.get("size") or ai_signal.get("quantity") or 0

                # Normalize values
                signal_type_norm = str(signal_raw).lower() if signal_raw else "hold"
                try:
                    confidence_norm = float(confidence_raw)
                except Exception:
                    confidence_norm = 0.0

                try:
                    # Allow decimals for crypto "coins" sizes
                    if isinstance(target_size_raw, (int, float)):
                        target_size_norm = float(target_size_raw)
                    else:
                        target_size_norm = float(str(target_size_raw))
                except Exception:
                    target_size_norm = 0

                return {
                    "symbol": symbol,
                    "signal_type": signal_type_norm,
                    "confidence": confidence_norm,
                    "reasoning": reasoning_raw,
                    "target_size": target_size_norm,
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

            except Exception as e:
                logger.error(f"Error parsing AI response: {e}")
                # Log the full AI response for debugging
                logger.debug(f"AI Response raw: {ai_response}")
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
