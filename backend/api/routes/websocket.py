"""
WebSocket Routes

Real-time data streaming via WebSocket for market data and account updates.
"""

import asyncio
import json
import logging
from typing import Dict, List, Set
from decimal import Decimal

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState

logger = logging.getLogger(__name__)

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections and broadcasting."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.subscriptions: Dict[WebSocket, Set[str]] = {}

    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        self.subscriptions[websocket] = set()
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.subscriptions:
            del self.subscriptions[websocket]
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific client."""
        try:
            if websocket.client_state == WebSocketState.CONNECTED:
                await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")

    async def broadcast(self, message: dict):
        """Broadcast a message to all connected clients."""
        disconnected = []

        for connection in self.active_connections:
            try:
                if connection.client_state == WebSocketState.CONNECTED:
                    await connection.send_json(message)
                else:
                    disconnected.append(connection)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")
                disconnected.append(connection)

        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection)

    async def broadcast_to_subscribers(self, symbol: str, message: dict):
        """Broadcast a message to clients subscribed to a specific symbol."""
        disconnected = []

        for connection in self.active_connections:
            try:
                if (
                    symbol in self.subscriptions.get(connection, set())
                    and connection.client_state == WebSocketState.CONNECTED
                ):
                    await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to subscriber: {e}")
                disconnected.append(connection)

        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection)

    def subscribe(self, websocket: WebSocket, symbol: str):
        """Subscribe a client to updates for a specific symbol."""
        if websocket not in self.subscriptions:
            self.subscriptions[websocket] = set()

        self.subscriptions[websocket].add(symbol.upper())
        logger.info(f"Client subscribed to {symbol}")

    def unsubscribe(self, websocket: WebSocket, symbol: str):
        """Unsubscribe a client from updates for a specific symbol."""
        if websocket in self.subscriptions:
            self.subscriptions[websocket].discard(symbol.upper())
            logger.info(f"Client unsubscribed from {symbol}")

    def get_subscriptions(self, websocket: WebSocket) -> Set[str]:
        """Get all symbols a client is subscribed to."""
        return self.subscriptions.get(websocket, set())


# Connection manager instance (will be initialized in main.py)
manager = ConnectionManager()


@router.websocket("/market-data")
async def websocket_market_data(websocket: WebSocket):
    """
    WebSocket endpoint for real-time market data streaming.

    Messages from client:
    - {"action": "subscribe", "symbols": ["AAPL", "GOOGL"]}
    - {"action": "unsubscribe", "symbols": ["AAPL"]}
    - {"action": "ping"}

    Messages to client:
    - {"type": "quote", "symbol": "AAPL", "data": {...}}
    - {"type": "trade", "symbol": "AAPL", "data": {...}}
    - {"type": "account", "data": {...}}
    - {"type": "position", "data": {...}}
    - {"type": "order_filled", "data": {...}}
    - {"type": "pong"}
    - {"type": "error", "message": "..."}
    """
    await manager.connect(websocket)

    try:
        # Import here to avoid circular dependency
        import backend.main as main_module

        # Send initial account state
        try:
            engine = main_module.get_paper_engine()
            account = engine.get_account_info()
            await manager.send_personal_message(
                {"type": "account", "data": account}, websocket
            )
        except Exception as e:
            logger.error(f"Error sending initial account state: {e}")

        # Handle incoming messages
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_json()

                action = data.get("action")

                if action == "subscribe":
                    symbols = data.get("symbols", [])
                    for symbol in symbols:
                        manager.subscribe(websocket, symbol)

                    await manager.send_personal_message(
                        {
                            "type": "subscribed",
                            "symbols": [s.upper() for s in symbols],
                        },
                        websocket,
                    )

                    # Send initial quotes for subscribed symbols
                    try:
                        alpaca = main_module.get_alpaca_service()
                        for symbol in symbols:
                            try:
                                quote = await alpaca.get_latest_quote(symbol.upper())
                                await manager.send_personal_message(
                                    {"type": "quote", "symbol": symbol.upper(), "data": quote},
                                    websocket,
                                )
                            except Exception as e:
                                logger.error(f"Error fetching quote for {symbol}: {e}")
                    except Exception as e:
                        logger.error(f"Error getting alpaca service: {e}")

                elif action == "unsubscribe":
                    symbols = data.get("symbols", [])
                    for symbol in symbols:
                        manager.unsubscribe(websocket, symbol)

                    await manager.send_personal_message(
                        {
                            "type": "unsubscribed",
                            "symbols": [s.upper() for s in symbols],
                        },
                        websocket,
                    )

                elif action == "ping":
                    await manager.send_personal_message({"type": "pong"}, websocket)

                elif action == "get_account":
                    try:
                        engine = main_module.get_paper_engine()
                        account = engine.get_account_info()
                        await manager.send_personal_message(
                            {"type": "account", "data": account}, websocket
                        )
                    except Exception as e:
                        await manager.send_personal_message(
                            {"type": "error", "message": str(e)}, websocket
                        )

                elif action == "get_positions":
                    try:
                        engine = main_module.get_paper_engine()
                        positions = engine.get_positions()
                        await manager.send_personal_message(
                            {"type": "positions", "data": positions}, websocket
                        )
                    except Exception as e:
                        await manager.send_personal_message(
                            {"type": "error", "message": str(e)}, websocket
                        )

                else:
                    await manager.send_personal_message(
                        {"type": "error", "message": f"Unknown action: {action}"},
                        websocket,
                    )

            except json.JSONDecodeError:
                await manager.send_personal_message(
                    {"type": "error", "message": "Invalid JSON"}, websocket
                )

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Client disconnected")

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


# Background task to stream real-time updates
async def stream_market_updates():
    """
    Background task to periodically update market data for subscribed symbols.
    This should be started when the app starts.
    """
    import backend.main as main_module

    logger.info("Market data streaming task started")

    while True:
        try:
            # Get all unique subscribed symbols
            all_symbols = set()
            for subscriptions in manager.subscriptions.values():
                all_symbols.update(subscriptions)

            if all_symbols:
                # Fetch quotes for all subscribed symbols
                alpaca = main_module.get_alpaca_service()
                engine = main_module.get_paper_engine()

                for symbol in all_symbols:
                    try:
                        # Get latest quote
                        quote = await alpaca.get_latest_quote(symbol)

                        # Update paper engine prices
                        mid_price = Decimal(
                            str((quote["bid_price"] + quote["ask_price"]) / 2)
                        )
                        engine.update_prices({symbol: mid_price})

                        # Broadcast quote to subscribers
                        await manager.broadcast_to_subscribers(
                            symbol, {"type": "quote", "symbol": symbol, "data": quote}
                        )

                    except Exception as e:
                        logger.error(f"Error updating {symbol}: {e}")

                # Broadcast account updates to all clients
                try:
                    account = engine.get_account_info()
                    await manager.broadcast({"type": "account", "data": account})
                except Exception as e:
                    logger.error(f"Error broadcasting account update: {e}")

            # Wait before next update (5 seconds)
            await asyncio.sleep(5)

        except Exception as e:
            logger.error(f"Error in market data streaming: {e}")
            await asyncio.sleep(5)
