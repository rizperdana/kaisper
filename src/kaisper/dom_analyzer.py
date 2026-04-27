"""DOM analysis for template generation."""

from typing import Any, Dict, List, Optional
from loguru import logger

try:
    from parsel import Selector
    PARSEL_AVAILABLE = True
except ImportError:
    PARSEL_AVAILABLE = False
    logger.warning("parsel not available, DOM analysis will be limited")


class DOMAnalyzer:
    """DOM analyzer for template generation."""
    
    def __init__(self):
        """Initialize DOM analyzer."""
        if not PARSEL_AVAILABLE:
            logger.warning("DOM analyzer not available (parsel not installed)")
    
    def analyze_html(
        self,
        html: str,
        url: str,
    ) -> Dict[str, Any]:
        """Analyze HTML structure."""
        if not PARSEL_AVAILABLE:
            return {}
        
        try:
            selector = Selector(html)
            
            analysis = {
                "url": url,
                "title": self._extract_title(selector),
                "headings": self._extract_headings(selector),
                "links": self._extract_links(selector),
                "images": self._extract_images(selector),
                "forms": self._extract_forms(selector),
                "tables": self._extract_tables(selector),
                "meta_tags": self._extract_meta_tags(selector),
                "structured_data": self._extract_structured_data(selector),
                "content_type": self._detect_content_type(selector),
            }
            
            logger.info(f"DOM analysis completed for {url}")
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze HTML: {e}")
            return {}
    
    def _extract_title(self, selector: Selector) -> Optional[str]:
        """Extract page title."""
        title = selector.css("title::text").get()
        if title:
            return title.strip()
        return None
    
    def _extract_headings(self, selector: Selector) -> List[Dict[str, Any]]:
        """Extract headings."""
        headings = []
        
        for level in range(1, 7):
            for heading in selector.css(f"h{level}"):
                text = heading.css("::text").get()
                if text:
                    headings.append({
                        "level": level,
                        "text": text.strip(),
                    })
        
        return headings
    
    def _extract_links(self, selector: Selector) -> List[Dict[str, Any]]:
        """Extract links."""
        links = []
        
        for link in selector.css("a"):
            href = link.css("::attr(href)").get()
            text = link.css("::text").get()
            
            if href:
                links.append({
                    "href": href,
                    "text": text.strip() if text else "",
                })
        
        return links
    
    def _extract_images(self, selector: Selector) -> List[Dict[str, Any]]:
        """Extract images."""
        images = []
        
        for img in selector.css("img"):
            src = img.css("::attr(src)").get()
            alt = img.css("::attr(alt)").get()
            
            if src:
                images.append({
                    "src": src,
                    "alt": alt or "",
                })
        
        return images
    
    def _extract_forms(self, selector: Selector) -> List[Dict[str, Any]]:
        """Extract forms."""
        forms = []
        
        for form in selector.css("form"):
            action = form.css("::attr(action)").get()
            method = form.css("::attr(method)").get()
            
            inputs = []
            for input_field in form.css("input"):
                input_type = input_field.css("::attr(type)").get()
                input_name = input_field.css("::attr(name)").get()
                
                inputs.append({
                    "type": input_type or "text",
                    "name": input_name or "",
                })
            
            forms.append({
                "action": action or "",
                "method": method or "GET",
                "inputs": inputs,
            })
        
        return forms
    
    def _extract_tables(self, selector: Selector) -> List[Dict[str, Any]]:
        """Extract tables."""
        tables = []
        
        for table in selector.css("table"):
            rows = []
            
            for row in table.css("tr"):
                cells = []
                
                for cell in row.css("td, th"):
                    text = cell.css("::text").get()
                    cells.append(text.strip() if text else "")
                
                if cells:
                    rows.append(cells)
            
            if rows:
                tables.append({
                    "rows": rows,
                })
        
        return tables
    
    def _extract_meta_tags(self, selector: Selector) -> Dict[str, str]:
        """Extract meta tags."""
        meta_tags = {}
        
        for meta in selector.css("meta"):
            name = meta.css("::attr(name)").get()
            property = meta.css("::attr(property)").get()
            content = meta.css("::attr(content)").get()
            
            if content:
                if name:
                    meta_tags[name] = content
                elif property:
                    meta_tags[property] = content
        
        return meta_tags
    
    def _extract_structured_data(self, selector: Selector) -> List[Dict[str, Any]]:
        """Extract structured data (JSON-LD, microdata)."""
        structured_data = []
        
        # JSON-LD
        for script in selector.css('script[type="application/ld+json"]'):
            content = script.css("::text").get()
            if content:
                try:
                    data = json.loads(content)
                    structured_data.append({
                        "type": "json-ld",
                        "data": data,
                    })
                except json.JSONDecodeError:
                    pass
        
        return structured_data
    
    def _detect_content_type(self, selector: Selector) -> str:
        """Detect content type from DOM."""
        html_text = selector.get().lower()
        
        # Check for product indicators
        if any(keyword in html_text for keyword in ["price", "add to cart", "buy now", "product"]):
            return "product"
        
        # Check for article indicators
        if any(keyword in html_text for keyword in ["article", "blog", "post", "author"]):
            return "article"
        
        # Check for video indicators
        if any(keyword in html_text for keyword in ["video", "watch", "play", "duration"]):
            return "video"
        
        # Default to generic
        return "generic"
    
    def suggest_selectors(
        self,
        html: str,
        field_name: str,
    ) -> List[str]:
        """Suggest CSS selectors for a field."""
        if not PARSEL_AVAILABLE:
            return []
        
        selector = Selector(html)
        suggestions = []
        
        # Common selectors for common fields
        field_selectors = {
            "title": ["h1", "h1.title", ".title", "#title", "[property='og:title']"],
            "description": ["p.description", ".description", "#description", "[property='og:description']"],
            "price": [".price", "#price", "[itemprop='price']", ".product-price"],
            "author": [".author", "#author", "[itemprop='author']", ".byline"],
            "date": [".date", "#date", "[itemprop='datePublished']", ".published"],
            "image": ["img", ".image", "#image", "[property='og:image']"],
        }
        
        if field_name in field_selectors:
            suggestions = field_selectors[field_name]
        
        # Check which selectors actually match
        valid_suggestions = []
        for sel in suggestions:
            if selector.css(sel):
                valid_suggestions.append(sel)
        
        return valid_suggestions


# Global DOM analyzer instance
dom_analyzer = DOMAnalyzer()
