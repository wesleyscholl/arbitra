"""
Trading API Routes

REST API endpoints for trading operations, account info, market data.
"""

from decimal import Decimal
from typing import Optional, List
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field

router = APIRouter()


# Dependency injection functions (to avoid circular import)
def get_alpaca_service():
    """Get Alpaca service from app state."""
    from backend.main import get_alpaca_service as _get_alpaca

    return _get_alpaca()


def get_paper_engine():
    """Get paper trading engine from app state."""
    from backend.main import get_paper_engine as _get_engine

    return _get_engine()


def get_websocket_manager():
    """Get WebSocket manager from app state."""
    from backend.main import get_websocket_manager as _get_manager

    return _get_manager()


# Request/Response Models
class OrderRequest(BaseModel):
    """Request model for submitting orders."""

    symbol: str = Field(..., description="Stock symbol")
    side: str = Field(..., description="'buy' or 'sell'")
    quantity: float = Field(..., gt=0, description="Number of shares")
    order_type: str = Field(default="market", description="'market' or 'limit'")
    limit_price: Optional[float] = Field(None, description="Price for limit orders")


class OrderResponse(BaseModel):
    """Response model for orders."""

    order_id: str
    symbol: str
    side: str
    quantity: float
    order_type: str
    limit_price: Optional[float]
    status: str
    submitted_at: str
    filled_at: Optional[str]
    filled_price: Optional[float]


class AccountResponse(BaseModel):
    """Response model for account information."""

    cash: float
    buying_power: float
    equity: float
    portfolio_value: float
    initial_capital: float
    total_pl: float
    realized_pl: float
    unrealized_pl: float
    total_return: float
    position_count: int
    trade_count: int


# Account Endpoints
@router.get("/account", response_model=AccountResponse)
async def get_account():
    """Get current account information."""
    try:
        engine = get_paper_engine()
        account = engine.get_account_info()
        return account
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/account/history")
async def get_account_history(
    days: int = Query(default=7, ge=1, le=365, description="Number of days of history")
):
    """Get account balance history."""
    # TODO: Implement database query for historical snapshots
    return {
        "message": "Account history endpoint - coming soon",
        "days": days,
    }


# Position Endpoints
@router.get("/positions")
async def get_positions():
    """Get all current positions."""
    try:
        engine = get_paper_engine()
        positions = engine.get_positions()
        return {"positions": positions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/positions/{symbol}")
async def get_position(symbol: str):
    """Get a specific position."""
    try:
        engine = get_paper_engine()
        position = engine.get_position(symbol.upper())

        if not position:
            raise HTTPException(status_code=404, detail=f"No position for {symbol}")

        return position
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Market Data Endpoints
@router.get("/quote/{symbol:path}")
async def get_quote(symbol: str):
    """
    Get the latest quote for a symbol (stock or crypto).
    
    For crypto, use format: BTC/USD, ETH/USD, etc.
    For stocks, use format: AAPL, GOOGL, etc.
    """
    try:
        alpaca = get_alpaca_service()
        # Don't uppercase crypto symbols (they contain /)
        quote_symbol = symbol if '/' in symbol else symbol.upper()
        quote = await alpaca.get_latest_quote(quote_symbol)
        return quote
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bars/{symbol:path}")
async def get_bars(
    symbol: str,
    timeframe: str = Query(default="5Min", description="Bar timeframe"),
    limit: int = Query(default=100, ge=1, le=1000, description="Number of bars"),
):
    """
    Get historical bars for a symbol (stock or crypto).
    
    For crypto, use format: BTC/USD, ETH/USD, etc.
    For stocks, use format: AAPL, GOOGL, etc.
    """
    try:
        alpaca = get_alpaca_service()

        # Default to last 24 hours
        end = datetime.now()
        start = end - timedelta(days=1)

        # Don't uppercase crypto symbols (they contain /)
        bar_symbol = symbol if '/' in symbol else symbol.upper()

        bars = await alpaca.get_bars(
            symbol=bar_symbol,
            timeframe=timeframe,
            start=start,
            end=end,
            limit=limit,
        )

        return {"symbol": bar_symbol, "timeframe": timeframe, "bars": bars}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search")
async def search_assets(
    q: str = Query(..., min_length=1, description="Search query"),
    asset_class: str = Query(default="us_equity", description="Asset class"),
):
    """Search for tradeable assets."""
    try:
        alpaca = get_alpaca_service()
        assets = await alpaca.search_assets(query=q, asset_class=asset_class)
        return {"query": q, "results": assets}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Order Endpoints
@router.post("/orders", response_model=OrderResponse)
async def submit_order(order: OrderRequest):
    """Submit a new order."""
    try:
        engine = get_paper_engine()

        # Validate side
        if order.side.lower() not in ["buy", "sell"]:
            raise HTTPException(
                status_code=400, detail="Side must be 'buy' or 'sell'"
            )

        # Validate order type
        if order.order_type.lower() not in ["market", "limit"]:
            raise HTTPException(
                status_code=400, detail="Order type must be 'market' or 'limit'"
            )

        # Validate limit price for limit orders
        if order.order_type.lower() == "limit" and not order.limit_price:
            raise HTTPException(
                status_code=400, detail="Limit price required for limit orders"
            )

        # Submit order
        submitted_order = engine.submit_order(
            symbol=order.symbol.upper(),
            side=order.side.lower(),
            quantity=Decimal(str(order.quantity)),
            order_type=order.order_type.lower(),
            limit_price=Decimal(str(order.limit_price)) if order.limit_price else None,
        )

        # For market orders, fill immediately
        if order.order_type.lower() == "market":
            # Get current price
            alpaca = get_alpaca_service()
            quote = await alpaca.get_latest_quote(order.symbol.upper())

            # Use mid price
            current_price = Decimal(str((quote["bid_price"] + quote["ask_price"]) / 2))

            # Fill order
            engine.fill_order(submitted_order["order_id"], current_price)

            # Get updated order
            filled_order = engine.get_order(submitted_order["order_id"])

            # Broadcast update via WebSocket
            try:
                manager = get_websocket_manager()
                await manager.broadcast(
                    {
                        "type": "order_filled",
                        "data": filled_order,
                    }
                )
            except:
                pass  # Don't fail if WebSocket broadcast fails

            return filled_order

        return submitted_order

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orders")
async def get_orders(
    status: Optional[str] = Query(
        None, description="Filter by status (pending, filled, cancelled)"
    )
):
    """Get all orders, optionally filtered by status."""
    try:
        engine = get_paper_engine()
        orders = engine.get_all_orders(status=status)
        return {"orders": orders}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orders/{order_id}")
async def get_order(order_id: str):
    """Get a specific order by ID."""
    try:
        engine = get_paper_engine()
        order = engine.get_order(order_id)

        if not order:
            raise HTTPException(status_code=404, detail=f"Order {order_id} not found")

        return order
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/orders/{order_id}")
async def cancel_order(order_id: str):
    """Cancel a pending order."""
    try:
        engine = get_paper_engine()
        success = engine.cancel_order(order_id)

        if not success:
            raise HTTPException(
                status_code=404, detail=f"Order {order_id} not found or cannot be cancelled"
            )

        return {"message": "Order cancelled", "order_id": order_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Trade History Endpoints
@router.get("/trades")
async def get_trades(
    limit: int = Query(default=100, ge=1, le=1000, description="Number of trades")
):
    """Get recent trades."""
    try:
        engine = get_paper_engine()
        trades = engine.get_trades(limit=limit)
        return {"trades": trades}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Reset Endpoint (for testing)
@router.post("/reset")
async def reset_engine():
    """Reset the paper trading engine to initial state."""
    try:
        engine = get_paper_engine()
        engine.reset()
        return {"message": "Paper trading engine reset successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
