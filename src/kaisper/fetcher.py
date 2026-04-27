"""Fetcher implementation using Obscura."""

from typing import Dict, Optional
from loguru import logger

from kaisper.config import settings


class Fetcher:
    """Fetcher using Obscura."""
    
    def __init__(self):
        self.timeout = settings.fetcher.timeout
        self.max_retries = settings.fetcher.max_retries
        self.user_agent = settings.fetcher.user_agent
    
    async def fetch(
        self,
        url: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        cookies: Optional[Dict[str, str]] = None,
    ) -> Dict[str, any]:
        """Fetch a URL and return the response."""
        logger.info(f"Fetching {url}")
        
        # Prepare headers
        request_headers = {
            "User-Agent": self.user_agent,
            **(headers or {}),
        }
        
        # For now, return a mock response
        # In production, this would use Obscura or Playwright
        response = {
            "url": url,
            "status_code": 200,
            "headers": dict(request_headers),
            "content": f"<html><body><h1>Mock content for {url}</h1></body></html>",
            "cookies": cookies or {},
        }
        
        logger.info(f"Fetched {url} - Status: {response['status_code']}")
        
        return response
    
    async def fetch_with_retry(
        self,
        url: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        cookies: Optional[Dict[str, str]] = None,
    ) -> Dict[str, any]:
        """Fetch with retry logic."""
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                return await self.fetch(url, method, headers, cookies)
            except Exception as e:
                last_error = e
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
        
        # All retries failed
        raise Exception(f"Failed to fetch {url} after {self.max_retries} attempts: {last_error}")


# Global fetcher instance
fetcher = Fetcher()
