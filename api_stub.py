"""
FastAPI backend stub for Arbitra macOS app testing.

This provides minimal API endpoints to test the Swift UI without a full backend.
Run with: uvicorn api_stub:app --reload
"""

from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from decimal import Decimal
from datetime import datetime
import asyncio
import json

app = FastAPI(title="Arbitra API Stub")

# CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock data
MOCK_PORTFOLIO = {
    "total_value": 52350.75,
    "cash": 12500.00,
    "total_pnl": 2350.75,
    "total_pnl_pct": 4.69,
    "daily_pnl": 450.25,
    "daily_pnl_pct": 0.87,
    "positions": [
        {
            "id": "1",
            "symbol": "AAPL",
            "quantity": 50.0,
            "entry_price": 175.50,
            "current_price": 182.30,
            "current_value": 9115.00,
            "unrealized_pnl": 340.00,
            "unrealized_pnl_pct": 3.87,
            "tier": "foundation",
            "stop_loss": 170.00,
            "take_profit": 190.00,
            "entry_time": "2024-01-15T10:30:00Z"
        },
        {
            "id": "2",
            "symbol": "MSFT",
            "quantity": 30.0,
            "entry_price": 380.25,
            "current_price": 392.50,
            "current_value": 11775.00,
            "unrealized_pnl": 367.50,
            "unrealized_pnl_pct": 3.22,
            "tier": "foundation",
            "stop_loss": 365.00,
            "take_profit": None,
            "entry_time": "2024-01-14T14:20:00Z"
        },
        {
            "id": "3",
            "symbol": "NVDA",
            "quantity": 25.0,
            "entry_price": 485.00,
            "current_price": 520.50,
            "current_value": 13012.50,
            "unrealized_pnl": 887.50,
            "unrealized_pnl_pct": 7.32,
            "tier": "growth",
            "stop_loss": 470.00,
            "take_profit": 550.00,
            "entry_time": "2024-01-13T09:15:00Z"
        }
    ]
}

MOCK_TRADES = [
    {
        "id": "1",
        "symbol": "TSLA",
        "action": "buy",
        "quantity": 20.0,
        "entry_price": 242.50,
        "exit_price": 255.80,
        "entry_time": "2024-01-12T10:00:00Z",
        "exit_time": "2024-01-12T15:30:00Z",
        "pnl": 266.00,
        "pnl_pct": 5.49,
        "fees": 2.00,
        "slippage": 1.50
    },
    {
        "id": "2",
        "symbol": "GOOGL",
        "action": "buy",
        "quantity": 15.0,
        "entry_price": 142.30,
        "exit_price": 138.90,
        "entry_time": "2024-01-11T11:20:00Z",
        "exit_time": "2024-01-11T16:45:00Z",
        "pnl": -51.00,
        "pnl_pct": -2.39,
        "fees": 1.50,
        "slippage": 0.80
    }
]

MOCK_METRICS = {
    "total_trades": 47,
    "winning_trades": 32,
    "losing_trades": 15,
    "win_rate": 68.09,
    "avg_win": 425.30,
    "avg_loss": -185.60,
    "largest_win": 1250.75,
    "largest_loss": -520.30,
    "sharpe_ratio": 1.85,
    "max_drawdown": 8.3,
    "profit_factor": 2.29,
    "risk_reward_ratio": 2.29
}

# Request models
class TradingRequest(BaseModel):
    paper_mode: bool = True

class StopLossUpdate(BaseModel):
    stop_loss_price: float

# Endpoints
@app.get("/")
async def root():
    return {"status": "Arbitra API Stub", "version": "1.0.0"}

@app.get("/api/portfolio")
async def get_portfolio():
    """Get current portfolio state."""
    return MOCK_PORTFOLIO

@app.get("/api/trades/recent")
async def get_recent_trades():
    """Get recent trade history."""
    return MOCK_TRADES

@app.get("/api/performance/metrics")
async def get_performance_metrics():
    """Get performance metrics."""
    return MOCK_METRICS

@app.post("/api/trading/start")
async def start_trading(request: TradingRequest):
    """Start trading."""
    return {
        "status": "started",
        "paper_mode": request.paper_mode,
        "message": f"Trading started in {'paper' if request.paper_mode else 'live'} mode"
    }

@app.post("/api/trading/stop")
async def stop_trading():
    """Stop trading."""
    return {"status": "stopped", "message": "Trading stopped"}

@app.post("/api/trading/emergency-stop")
async def emergency_stop():
    """Emergency stop - close all positions."""
    return {
        "status": "emergency_stopped",
        "message": "All positions closed, trading stopped",
        "positions_closed": len(MOCK_PORTFOLIO["positions"])
    }

@app.post("/api/positions/{symbol}/close")
async def close_position(symbol: str):
    """Close a specific position."""
    position = next((p for p in MOCK_PORTFOLIO["positions"] if p["symbol"] == symbol), None)
    if not position:
        raise HTTPException(status_code=404, detail=f"Position {symbol} not found")
    
    return {
        "success": True,
        "message": f"Position {symbol} closed",
        "realized_pnl": position["unrealized_pnl"]
    }

@app.put("/api/positions/{symbol}/stop-loss")
async def update_stop_loss(symbol: str, update: StopLossUpdate):
    """Update stop loss for a position."""
    position = next((p for p in MOCK_PORTFOLIO["positions"] if p["symbol"] == symbol), None)
    if not position:
        raise HTTPException(status_code=404, detail=f"Position {symbol} not found")
    
    position["stop_loss"] = update.stop_loss_price
    
    return {
        "success": True,
        "message": f"Stop loss updated for {symbol}",
        "new_stop_loss": update.stop_loss_price
    }

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time updates."""
    await websocket.accept()
    
    try:
        # Send initial connection message
        await websocket.send_json({
            "type": "connected",
            "message": "WebSocket connected",
            "timestamp": datetime.now().isoformat()
        })
        
        # Simulate real-time updates
        while True:
            await asyncio.sleep(5)
            
            # Send mock position update
            await websocket.send_json({
                "type": "position_update",
                "data": {
                    "symbol": "AAPL",
                    "current_price": 182.30 + (asyncio.get_event_loop().time() % 10 - 5) * 0.5,
                    "timestamp": datetime.now().isoformat()
                }
            })
            
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Arbitra API Stub...")
    print("📡 API: http://localhost:8000")
    print("🔌 WebSocket: ws://localhost:8000/ws")
    print("📚 Docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
