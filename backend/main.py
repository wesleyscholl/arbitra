"""
Arbitra FastAPI Backend

Paper trading backend with real-time market data from Alpaca.
"""

import os
import logging
from contextlib import asynccontextmanager
from decimal import Decimal
from typing import Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from backend.services.alpaca_service import AlpacaMarketDataService
from backend.services.ai_service import AIService
from backend.services.trading_agent import TradingAgent
from backend.trading.paper_trading_engine import PaperTradingEngine
from backend.api.routes import trading, websocket as ws_routes, agent as agent_routes

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

# Global state
alpaca_service: AlpacaMarketDataService = None
paper_engine: PaperTradingEngine = None
websocket_manager = None
trading_agent: TradingAgent = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown logic."""
    global alpaca_service, paper_engine, websocket_manager, trading_agent

    # Startup
    logger.info("Starting Arbitra backend...")

    # Initialize Alpaca service
    api_key = os.getenv("ALPACA_API_KEY")
    secret_key = os.getenv("ALPACA_SECRET_KEY")

    if not api_key or not secret_key:
        raise ValueError("ALPACA_API_KEY and ALPACA_SECRET_KEY must be set")

    alpaca_service = AlpacaMarketDataService(
        api_key=api_key, secret_key=secret_key, paper=True
    )

    logger.info("Alpaca service initialized")

    # Initialize paper trading engine
    initial_capital = Decimal(os.getenv("INITIAL_CAPITAL", "100000"))
    enable_slippage = os.getenv("ENABLE_SLIPPAGE", "true").lower() == "true"
    slippage_bps = Decimal(os.getenv("SLIPPAGE_BPS", "5"))
    enable_commission = os.getenv("ENABLE_COMMISSION", "true").lower() == "true"
    commission_per_share = Decimal(os.getenv("COMMISSION_PER_SHARE", "0.005"))

    paper_engine = PaperTradingEngine(
        initial_capital=initial_capital,
        enable_slippage=enable_slippage,
        slippage_bps=slippage_bps,
        enable_commission=enable_commission,
        commission_per_share=commission_per_share,
    )

    logger.info("Paper trading engine initialized")

    # Initialize WebSocket manager
    websocket_manager = ws_routes.ConnectionManager()

    # Initialize AI service with multiple providers
    gemini_key = os.getenv("GEMINI_API_KEY")
    huggingface_key = os.getenv("HUGGINGFACE_API_KEY")
    ollama_key = os.getenv("OLLAMA_API_KEY")
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    ai_service = AIService(
        gemini_api_key=gemini_key,
        huggingface_api_key=huggingface_key,
        ollama_api_key=ollama_key,
        ollama_base_url=ollama_url,
    )
    logger.info("AI service initialized with multi-provider support")
    
    # Initialize trading agent
    if gemini_key or huggingface_key or ollama_url:
        trading_agent = TradingAgent(
            alpaca_service=alpaca_service,
            paper_engine=paper_engine,
            websocket_manager=websocket_manager,
            ai_service=ai_service,
        )
        logger.info("Trading agent initialized with multi-provider AI")
    else:
        logger.warning("No AI providers configured - agent will not be available")

    logger.info("Arbitra backend started successfully")

    yield

    # Shutdown
    logger.info("Shutting down Arbitra backend...")

    if trading_agent and trading_agent.running:
        await trading_agent.stop()

    if alpaca_service:
        await alpaca_service.close()

    logger.info("Arbitra backend shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Arbitra Trading Bot",
    description="Paper trading backend with real-time market data",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "alpaca_connected": alpaca_service is not None,
        "paper_engine_running": paper_engine is not None,
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Arbitra Trading Bot",
        "version": "1.0.0",
        "status": "running",
    }


# Include routers
app.include_router(trading.router, prefix="/api/trading", tags=["trading"])
app.include_router(ws_routes.router, prefix="/ws", tags=["websocket"])
app.include_router(agent_routes.router, prefix="/api/agent", tags=["agent"])


# Helper functions to access global state
def get_alpaca_service() -> AlpacaMarketDataService:
    """Get the Alpaca service instance."""
    if not alpaca_service:
        raise RuntimeError("Alpaca service not initialized")
    return alpaca_service


def get_paper_engine() -> PaperTradingEngine:
    """Get the paper trading engine instance."""
    if not paper_engine:
        raise RuntimeError("Paper trading engine not initialized")
    return paper_engine


def get_websocket_manager():
    """Get the WebSocket connection manager."""
    if not websocket_manager:
        raise RuntimeError("WebSocket manager not initialized")
    return websocket_manager


def get_trading_agent():
    """Get the trading agent instance."""
    if not trading_agent:
        raise RuntimeError("Trading agent not initialized")
    return trading_agent


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))

    logger.info(f"Starting server on {host}:{port}")

    uvicorn.run(
        "backend.main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info",
    )
