"""
Trading Agent API Routes

Endpoints for controlling the AI trading agent.
"""

from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from decimal import Decimal

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
async def update_agent_config(config: dict = Body(...)):
    """Update agent configuration.

    Accepts a flexible payload where `watchlist` may be a list of symbols or a
    comma-separated string. Symbols will be deduplicated (order-preserving,
    case-insensitive). Numeric fields are coerced to the expected types.
    """
    try:
        agent = get_agent()

        # Parse and normalize watchlist
        raw_watchlist = config.get("watchlist", agent.watchlist)
        if isinstance(raw_watchlist, str):
            symbols = [s.strip() for s in raw_watchlist.split(",") if s.strip()]
        elif isinstance(raw_watchlist, list):
            symbols = [str(s).strip() for s in raw_watchlist if str(s).strip()]
        else:
            raise HTTPException(status_code=400, detail="watchlist must be a list or comma-separated string")

        # Order-preserving, case-insensitive dedupe
        seen = set()
        deduped = []
        for s in symbols:
            k = s.upper()
            if k in seen:
                continue
            seen.add(k)
            deduped.append(s)

        agent.watchlist = deduped

        # Coerce other numeric/config fields if present
        if "scan_interval" in config:
            agent.scan_interval = int(config["scan_interval"])

        if "signal_threshold" in config:
            agent.signal_threshold = float(config["signal_threshold"])

        if "max_positions" in config:
            agent.max_positions = int(config["max_positions"])

        if "max_position_size" in config:
            # Keep max_position_size as Decimal internally to avoid float/Decimal
            # comparison issues elsewhere in the agent.
            try:
                agent.max_position_size = Decimal(str(config["max_position_size"]))
            except Exception:
                raise HTTPException(status_code=400, detail="max_position_size must be numeric")

        return {
            "message": "Agent configuration updated",
            "config": {
                "watchlist": agent.watchlist,
                "scan_interval": agent.scan_interval,
                "signal_threshold": agent.signal_threshold,
                "max_positions": agent.max_positions,
                "max_position_size": float(agent.max_position_size),
            },
        }

    except HTTPException:
        raise
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
async def update_watchlist(body=Body(...)):
    """Update agent watchlist.

    Accepts these body shapes:
    - JSON list: ["AAPL", "GOOGL"]
    - JSON string: "AAPL, GOOGL"
    - JSON object: {"symbols": [...]} 
    """
    try:
        agent = get_agent()

        # Normalize input into a list of symbol strings
        items = []
        if isinstance(body, dict):
            # Support { "symbols": [...] } or { "watchlist": [...] }
            if "symbols" in body:
                raw = body["symbols"]
            elif "watchlist" in body:
                raw = body["watchlist"]
            else:
                # Might be a single-key payload where the key is the symbol
                raw = body

            if isinstance(raw, str):
                items = [s.strip() for s in raw.split(",") if s.strip()]
            elif isinstance(raw, list):
                items = [str(s).strip() for s in raw if str(s).strip()]
            else:
                # Fallback: try to coerce all dict values to strings
                items = [str(v).strip() for v in raw.values()] if isinstance(raw, dict) else []

        elif isinstance(body, str):
            items = [s.strip() for s in body.split(",") if s.strip()]
        elif isinstance(body, list):
            items = [str(s).strip() for s in body if str(s).strip()]
        else:
            raise HTTPException(status_code=400, detail="Unsupported payload for watchlist")

        # Deduplicate (order-preserving, case-insensitive)
        seen = set()
        deduped = []
        for s in items:
            k = s.upper()
            if k in seen:
                continue
            seen.add(k)
            deduped.append(s)

        agent.watchlist = deduped

        return {
            "message": "Watchlist updated",
            "symbols": agent.watchlist,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
