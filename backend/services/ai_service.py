"""
Multi-Provider AI Service

Provides trading signal generation using:
1. Google Gemini (primary)
2. Hugging Face Inference API (secondary)
3. Ollama local instance (fallback)
"""

import os
import json
import logging
from typing import Dict, Optional, Any
import httpx

logger = logging.getLogger(__name__)


class AIService:
    """
    Multi-provider AI service with automatic fallback.
    
    Tries providers in order: Gemini -> HuggingFace -> Ollama
    """

    def __init__(
        self,
        gemini_api_key: Optional[str] = None,
        huggingface_api_key: Optional[str] = None,
        ollama_api_key: Optional[str] = None,
        ollama_base_url: str = "http://localhost:11434",
    ):
        """
        Initialize AI service with multiple provider keys.
        
        Args:
            gemini_api_key: Google Gemini API key
            huggingface_api_key: Hugging Face API token
            ollama_api_key: Ollama API key (for remote instances)
            ollama_base_url: Base URL for Ollama instance
        """
        self.gemini_api_key = gemini_api_key
        self.huggingface_api_key = huggingface_api_key
        self.ollama_api_key = ollama_api_key
        self.ollama_base_url = ollama_base_url
        
        # Track which providers are available
        self.gemini_available = bool(gemini_api_key)
        self.huggingface_available = bool(huggingface_api_key)
        self.ollama_available = True  # Assume available, will check on first call
        
        logger.info(
            f"AI Service initialized - Gemini: {self.gemini_available}, "
            f"HuggingFace: {self.huggingface_available}, "
            f"Ollama: {self.ollama_available}"
        )

    async def generate_trading_signal(
        self, prompt: str, timeout: float = 30.0
    ) -> Dict[str, Any]:
        """
        Generate a trading signal using available AI providers.
        
        Tries providers in order until one succeeds.
        
        Args:
            prompt: The trading analysis prompt
            timeout: Request timeout in seconds
            
        Returns:
            Dict with AI response and metadata
        """
        errors = []
        
        # Try Gemini first
        if self.gemini_available:
            try:
                result = await self._call_gemini(prompt, timeout)
                return {
                    "success": True,
                    "content": result,
                    "provider": "gemini",
                    "model": "gemini-2.5-flash"
                }
            except Exception as e:
                error_msg = f"Gemini failed: {str(e)}"
                logger.warning(error_msg)
                errors.append(error_msg)
        
        # Try HuggingFace second
        if self.huggingface_available:
            try:
                result = await self._call_huggingface(prompt, timeout)
                return {
                    "success": True,
                    "content": result,
                    "provider": "huggingface",
                    "model": "Qwen/Qwen2.5-Coder-32B-Instruct"
                }
            except Exception as e:
                error_msg = f"HuggingFace failed: {str(e)}"
                logger.warning(error_msg)
                errors.append(error_msg)
        
        # Try Ollama last
        if self.ollama_available:
            try:
                result = await self._call_ollama(prompt, timeout)
                return {
                    "success": True,
                    "content": result,
                    "provider": "ollama",
                    "model": "llama3.2"
                }
            except Exception as e:
                error_msg = f"Ollama failed: {str(e)}"
                logger.warning(error_msg)
                errors.append(error_msg)
        
        # All providers failed
        error_summary = " | ".join(errors) if errors else "No providers available"
        logger.error(f"All AI providers failed: {error_summary}")
        return {
            "success": False,
            "content": None,
            "provider": "none",
            "errors": errors
        }

    async def _call_gemini(self, prompt: str, timeout: float) -> str:
        """
        Call Google Gemini API.
        
        Args:
            prompt: The prompt to send
            timeout: Request timeout
            
        Returns:
            AI response text
        """
        # Use gemini-2.5-flash (latest stable model with free tier)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.gemini_api_key}"
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 500
            }
        }
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, json=payload)
            
            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}: {response.text}")
            
            result = response.json()
            
            # Extract content from Gemini response structure
            try:
                # Try different possible response structures
                if "candidates" not in result or len(result["candidates"]) == 0:
                    raise Exception(f"No candidates in response: {json.dumps(result)[:300]}")
                
                candidate = result["candidates"][0]
                
                # Check for content.parts structure (standard format)
                if "content" in candidate:
                    content = candidate["content"]
                    if isinstance(content, dict) and "parts" in content:
                        parts = content["parts"]
                        if isinstance(parts, list) and len(parts) > 0:
                            if "text" in parts[0]:
                                return parts[0]["text"]
                    elif isinstance(content, str):
                        return content
                
                # Check for direct text in candidate
                if "text" in candidate:
                    return candidate["text"]
                
                # Check for output in candidate
                if "output" in candidate:
                    return candidate["output"]
                
                # If nothing worked, log the actual structure and raise
                logger.error(f"Gemini response structure: {json.dumps(result, indent=2)[:1000]}")
                raise Exception(f"Could not extract text from response")
            except KeyError as e:
                logger.error(f"Gemini KeyError: {e}, Response: {json.dumps(result, indent=2)[:1000]}")
                raise Exception(f"Response parsing failed - missing key: {e}")
            except Exception as e:
                logger.error(f"Gemini parse error: {e}, Response: {json.dumps(result, indent=2)[:1000]}")
                raise Exception(f"Response parsing failed: {str(e)}")

    async def _call_huggingface(self, prompt: str, timeout: float) -> str:
        """
        Call Hugging Face Inference Providers API (new chat completions endpoint).
        
        Args:
            prompt: The prompt to send
            timeout: Request timeout
            
        Returns:
            AI response text
        """
        # Using new Inference Providers API with chat completions
        # Free tier models available via router
        url = "https://router.huggingface.co/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.huggingface_api_key}",
            "Content-Type": "application/json"
        }
        
        # Use a free tier model like Qwen
        payload = {
            "model": "Qwen/Qwen2.5-Coder-32B-Instruct",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 500,
            "stream": False
        }
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, headers=headers, json=payload)
            
            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}: {response.text}")
            
            result = response.json()
            
            # Extract content from OpenAI-compatible response format
            try:
                content = result["choices"][0]["message"]["content"]
                return content
            except (KeyError, IndexError) as e:
                raise Exception(f"Unexpected response format: {e}")

    async def _call_ollama(self, prompt: str, timeout: float) -> str:
        """
        Call local Ollama API using chat completions endpoint.
        
        Args:
            prompt: The prompt to send
            timeout: Request timeout
            
        Returns:
            AI response text
        """
        # Use chat API endpoint instead of generate
        url = f"{self.ollama_base_url}/api/chat"
        
        payload = {
            "model": "llama3.2",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "stream": False,
            "options": {
                "temperature": 0.3,
                "num_predict": 500
            },
            "format": "json"
        }
        
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                
                result = response.json()
                
                # Extract message content from chat response
                if "message" in result and "content" in result["message"]:
                    return result["message"]["content"]
                elif "error" in result:
                    raise Exception(f"Ollama error: {result['error']}")
                else:
                    raise Exception(f"Unexpected Ollama response format: {result}")
        except httpx.ConnectError:
            raise Exception("Cannot connect to Ollama - ensure it's running locally with: ollama serve")
        except httpx.TimeoutException:
            raise Exception(f"Ollama request timed out after {timeout}s")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise Exception("Ollama model 'llama3.2' not found - pull it with: ollama pull llama3.2")
            raise Exception(f"Ollama HTTP error {e.response.status_code}: {e.response.text}")
        except Exception as e:
            raise Exception(f"Ollama API error: {str(e)}")

    def get_status(self) -> Dict[str, Any]:
        """Get status of all AI providers."""
        return {
            "gemini": {
                "available": self.gemini_available,
                "configured": bool(self.gemini_api_key)
            },
            "huggingface": {
                "available": self.huggingface_available,
                "configured": bool(self.huggingface_api_key)
            },
            "ollama": {
                "available": self.ollama_available,
                "base_url": self.ollama_base_url,
                "configured": bool(self.ollama_api_key) or "local"
            }
        }
