"""Ollama client for local LLM fallback."""

import json
from typing import Any, Dict, List, Optional
from loguru import logger

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False
    logger.warning("httpx not available, Ollama client will be disabled")


class OllamaClient:
    """Ollama client for local LLM fallback."""
    
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "gemma2:9b",
        timeout: int = 120,
    ):
        """Initialize Ollama client."""
        if not HTTPX_AVAILABLE:
            logger.warning("Ollama client not available (httpx not installed)")
            self.client = None
            return
        
        self.base_url = base_url
        self.model = model
        self.timeout = timeout
        
        try:
            self.client = httpx.Client(timeout=timeout)
            logger.info(f"Ollama client initialized with model {model}")
        except Exception as e:
            logger.error(f"Failed to initialize Ollama client: {e}")
            self.client = None
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 4000,
    ) -> Optional[str]:
        """Generate text using Ollama."""
        if not self.client:
            logger.warning("Ollama client not available")
            return None
        
        try:
            messages = []
            
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens,
                    },
                },
            )
            
            response.raise_for_status()
            data = response.json()
            
            if "message" in data and "content" in data["message"]:
                return data["message"]["content"]
            
            logger.warning("Unexpected response format from Ollama")
            return None
            
        except Exception as e:
            logger.error(f"Failed to generate text with Ollama: {e}")
            return None
    
    async def generate_template(
        self,
        html: str,
        url: str,
        content_type: str,
        system_prompt: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Generate extraction template using Ollama."""
        prompt = f"""Generate an extraction template for the following webpage.

URL: {url}
Content Type: {content_type}

HTML:
{html[:10000]}

Generate a JSON template with the following structure:
{{
  "extraction": {{
    "title": {{"method": "xpath|css|regex", "pattern": "selector pattern", "extract": "text|attribute"}},
    "description": {{...}},
    "price": {{...}}
  }},
  "validation": {{
    "required_fields": ["title", "description"],
    "field_validators": {{}}
  }}
}}

Return only the JSON, no other text.
"""
        
        response = await self.generate(
            prompt=prompt,
            system_prompt=system_prompt or "You are an expert web scraping assistant. Generate extraction templates from HTML.",
            temperature=0.1,
            max_tokens=4000,
        )
        
        if not response:
            return None
        
        try:
            template_data = json.loads(response)
            return template_data
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Ollama response as JSON: {e}")
            return None
    
    def check_model_available(self) -> bool:
        """Check if the model is available."""
        if not self.client:
            return False
        
        try:
            response = self.client.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            data = response.json()
            
            models = [model["name"] for model in data.get("models", [])]
            return self.model in models
            
        except Exception as e:
            logger.error(f"Failed to check model availability: {e}")
            return False
    
    def list_models(self) -> List[str]:
        """List available models."""
        if not self.client:
            return []
        
        try:
            response = self.client.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            data = response.json()
            
            models = [model["name"] for model in data.get("models", [])]
            return models
            
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return []


# Global Ollama client instance
ollama_client = OllamaClient()
