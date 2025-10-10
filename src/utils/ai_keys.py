"""
Utilities for locating AI provider API keys from environment.

Priority:
 1. OPEN_ROUTER_API_KEY
 2. GEMINI_API_KEY (legacy fallback)

This keeps runtime behavior compatible while preferring OpenRouter-style keys.
"""
from typing import Optional
import os


def get_ai_api_key() -> Optional[str]:
    """Return the API key to use for AI providers.

    Checks OPEN_ROUTER_API_KEY first, then falls back to GEMINI_API_KEY.
    """
    return os.environ.get("OPEN_ROUTER_API_KEY") or os.environ.get("GEMINI_API_KEY")
