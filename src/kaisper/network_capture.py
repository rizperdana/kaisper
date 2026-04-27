"""Network request capture for template generation."""

from typing import Any, Dict, List, Optional
from loguru import logger

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logger.warning("playwright not available, network capture will be disabled")


class NetworkRequestCapture:
    """Network request capture for template generation."""
    
    def __init__(self):
        """Initialize network request capture."""
        if not PLAYWRIGHT_AVAILABLE:
            logger.warning("Network request capture not available (playwright not installed)")
    
    def capture_requests(
        self,
        url: str,
        timeout: int = 30000,
    ) -> Dict[str, Any]:
        """Capture network requests for a URL."""
        if not PLAYWRIGHT_AVAILABLE:
            return {}
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                requests = []
                
                def handle_request(request):
                    requests.append({
                        "url": request.url,
                        "method": request.method,
                        "resource_type": request.resource_type,
                        "headers": dict(request.headers),
                    })
                
                page.on("request", handle_request)
                
                page.goto(url, timeout=timeout)
                
                browser.close()
                
                analysis = {
                    "url": url,
                    "total_requests": len(requests),
                    "requests": requests,
                    "api_requests": self._filter_api_requests(requests),
                    "static_requests": self._filter_static_requests(requests),
                }
                
                logger.info(f"Captured {len(requests)} network requests for {url}")
                return analysis
                
        except Exception as e:
            logger.error(f"Failed to capture network requests: {e}")
            return {}
    
    def _filter_api_requests(self, requests: List[Dict]) -> List[Dict]:
        """Filter API requests."""
        api_requests = []
        
        for request in requests:
            url = request["url"].lower()
            resource_type = request["resource_type"]
            
            # Check for API indicators
            if (
                "/api/" in url
                or ".json" in url
                or resource_type in ["xhr", "fetch"]
            ):
                api_requests.append(request)
        
        return api_requests
    
    def _filter_static_requests(self, requests: List[Dict]) -> List[Dict]:
        """Filter static requests."""
        static_requests = []
        
        for request in requests:
            url = request["url"].lower()
            resource_type = request["resource_type"]
            
            # Check for static resource indicators
            if (
                any(ext in url for ext in [".css", ".js", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".woff", ".woff2"])
                or resource_type in ["stylesheet", "script", "image", "font"]
            ):
                static_requests.append(request)
        
        return static_requests
    
    def suggest_api_endpoints(
        self,
        url: str,
    ) -> List[str]:
        """Suggest API endpoints for data extraction."""
        analysis = self.capture_requests(url)
        
        if not analysis:
            return []
        
        api_requests = analysis.get("api_requests", [])
        endpoints = []
        
        for request in api_requests:
            request_url = request["url"]
            
            # Extract endpoint path
            if "://" in request_url:
                path = request_url.split("/", 3)[-1] if len(request_url.split("/")) > 3 else ""
            else:
                path = request_url
            
            if path:
                endpoints.append(path)
        
        return list(set(endpoints))


# Global network request capture instance
network_capture = NetworkRequestCapture()
