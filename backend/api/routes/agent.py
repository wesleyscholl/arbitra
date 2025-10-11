"""
Trading Agent API Routes

Endpoints for controlling the AI trading agent.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class AgentConfig(BaseModel):
    """Agent configuration model."""

    watchlist: list[str] = [
        "AAPL", "GOOGL", "MSFT", "AMZN", "TSLA",  # Stocks
        "BTC/USD", "ETH/USD", "SOL/USD", "DOGE/USD"  # Crypto
    ]
    scan_interval: int = 300  # seconds
    signal_threshold: float = 0.65
    max_positions: int = 5
    max_position_size: float = 10000.0


# Helper to get agent from app state
def get_agent():
    """Get trading agent from app state."""
    from backend.main import get_trading_agent

    return get_trading_agent()


@router.post("/start")
async def start_agent():
    """Start the AI trading agent."""
    try:
        agent = get_agent()

        if agent.running:
            return {"message": "Agent already running", "status": "running"}

        # Start agent (it will handle background task internally)
        await agent.start()

        return {
            "message": "Trading agent started",
            "status": "running",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop")
async def stop_agent():
    """Stop the AI trading agent."""
    try:
        agent = get_agent()

        if not agent.running:
            return {"message": "Agent not running", "status": "stopped"}

        await agent.stop()

        return {
            "message": "Trading agent stopped",
            "status": "stopped",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_agent_status():
    """Get agent status."""
    try:
        agent = get_agent()
        return agent.get_status()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/signals")
async def get_recent_signals(limit: int = 20):
    """Get recent AI signals."""
    try:
        agent = get_agent()
        signals = agent.get_recent_signals(limit=limit)
        return {"signals": signals}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/config")
async def update_agent_config(config: AgentConfig):
    """Update agent configuration."""
    try:
        agent = get_agent()

        # Update configuration
        agent.watchlist = config.watchlist
        agent.scan_interval = config.scan_interval
        agent.signal_threshold = config.signal_threshold
        agent.max_positions = config.max_positions
        agent.max_position_size = config.max_position_size

        return {
            "message": "Agent configuration updated",
            "config": config.dict(),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config")
async def get_agent_config():
    """Get current agent configuration."""
    try:
        agent = get_agent()

        return {
            "watchlist": agent.watchlist,
            "scan_interval": agent.scan_interval,
            "signal_threshold": agent.signal_threshold,
            "max_positions": agent.max_positions,
            "max_position_size": float(agent.max_position_size),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/watchlist")
async def get_watchlist():
    """Get agent watchlist."""
    try:
        agent = get_agent()
        return {"symbols": agent.watchlist}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/watchlist")
async def update_watchlist(symbols: list[str]):
    """Update agent watchlist."""
    try:
        agent = get_agent()
        agent.watchlist = symbols

        return {
            "message": "Watchlist updated",
            "symbols": agent.watchlist,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
