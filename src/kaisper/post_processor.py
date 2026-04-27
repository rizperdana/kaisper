"""Template post-processing for Kaisper."""

import re
from typing import Any, Dict, List, Optional
from datetime import datetime
from loguru import logger

from kaisper.models import Template, ExtractionResult


class TemplatePostProcessor:
    """Template post-processor for improving extraction results."""
    
    def __init__(self):
        """Initialize template post-processor."""
        self.processors = {
            "clean_text": self._clean_text,
            "normalize_whitespace": self._normalize_whitespace,
            "remove_html": self._remove_html,
            "extract_urls": self._extract_urls,
            "extract_emails": self._extract_emails,
            "extract_phone_numbers": self._extract_phone_numbers,
            "parse_date": self._parse_date,
            "parse_datetime": self._parse_datetime,
            "parse_number": self._parse_number,
            "parse_currency": self._parse_currency,
            "parse_duration": self._parse_duration,
            "parse_views": self._parse_views,
            "remove_currency": self._remove_currency,
            "to_float": self._to_float,
            "to_int": self._to_int,
            "to_bool": self._to_bool,
            "strip": self._strip,
            "lower": self._lower,
            "upper": self._upper,
            "title_case": self._title_case,
            "truncate": self._truncate,
        }
    
    def process(
        self,
        data: Dict[str, Any],
        template: Template,
    ) -> Dict[str, Any]:
        """Process extraction results using template post-processing rules."""
        
        processed_data = {}
        
        for field_name, rule in template.extraction.items():
            if field_name in data:
                value = data[field_name]
                
                # Apply post-processing steps
                if rule.post_process:
                    for step in rule.post_process:
                        if step in self.processors:
                            try:
                                value = self.processors[step](value)
                            except Exception as e:
                                logger.error(f"Failed to apply post-processing {step} to {field_name}: {e}")
                
                processed_data[field_name] = value
        
        return processed_data
    
    def _clean_text(self, text: str) -> str:
        """Clean text by removing special characters."""
        if not isinstance(text, str):
            return text
        
        # Remove special characters but keep basic punctuation
        cleaned = re.sub(r'[^\w\s\.\,\!\?\-\:\;]', '', text)
        return cleaned.strip()
    
    def _normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace."""
        if not isinstance(text, str):
            return text
        
        # Replace multiple spaces with single space
        normalized = re.sub(r'\s+', ' ', text)
        return normalized.strip()
    
    def _remove_html(self, text: str) -> str:
        """Remove HTML tags."""
        if not isinstance(text, str):
            return text
        
        # Remove HTML tags
        cleaned = re.sub(r'<[^>]+>', '', text)
        return cleaned.strip()
    
    def _extract_urls(self, text: str) -> List[str]:
        """Extract URLs from text."""
        if not isinstance(text, str):
            return []
        
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, text)
        return urls
    
    def _extract_emails(self, text: str) -> List[str]:
        """Extract email addresses from text."""
        if not isinstance(text, str):
            return []
        
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, text)
        return emails
    
    def _extract_phone_numbers(self, text: str) -> List[str]:
        """Extract phone numbers from text."""
        if not isinstance(text, str):
            return []
        
        phone_pattern = r'\+?[\d\s\-\(\)]{10,}'
        phones = re.findall(phone_pattern, text)
        return phones
    
    def _parse_date(self, text: str) -> Optional[str]:
        """Parse date string."""
        if not isinstance(text, str):
            return text
        
        # Try common date formats
        date_formats = [
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%d-%m-%Y",
            "%d/%m/%Y",
            "%B %d, %Y",
            "%b %d, %Y",
        ]
        
        for fmt in date_formats:
            try:
                date_obj = datetime.strptime(text, fmt)
                return date_obj.strftime("%Y-%m-%d")
            except ValueError:
                continue
        
        return text
    
    def _parse_datetime(self, text: str) -> Optional[str]:
        """Parse datetime string."""
        if not isinstance(text, str):
            return text
        
        # Try common datetime formats
        datetime_formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y/%m/%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M",
        ]
        
        for fmt in datetime_formats:
            try:
                datetime_obj = datetime.strptime(text, fmt)
                return datetime_obj.isoformat()
            except ValueError:
                continue
        
        return text
    
    def _parse_number(self, text: str) -> Optional[float]:
        """Parse number from text."""
        if not isinstance(text, str):
            return text
        
        # Remove non-numeric characters except decimal point
        cleaned = re.sub(r'[^\d\.]', '', text)
        
        if not cleaned:
            return None
        
        try:
            return float(cleaned)
        except ValueError:
            return None
    
    def _parse_currency(self, text: str) -> Optional[float]:
        """Parse currency value."""
        if not isinstance(text, str):
            return text
        
        # Remove currency symbols and commas
        cleaned = re.sub(r'[^\d\.]', '', text)
        
        if not cleaned:
            return None
        
        try:
            return float(cleaned)
        except ValueError:
            return None
    
    def _parse_duration(self, text: str) -> Optional[int]:
        """Parse duration (e.g., "10:30" -> 630 seconds)."""
        if not isinstance(text, str):
            return text
        
        # Try to parse MM:SS format
        if ":" in text:
            parts = text.split(":")
            if len(parts) == 2:
                try:
                    minutes = int(parts[0])
                    seconds = int(parts[1])
                    return minutes * 60 + seconds
                except ValueError:
                    pass
        
        return text
    
    def _parse_views(self, text: str) -> Optional[int]:
        """Parse view count (e.g., "1M" -> 1000000)."""
        if not isinstance(text, str):
            return text
        
        # Remove non-numeric characters
        cleaned = re.sub(r'[^\d\.MK]', '', text, flags=re.IGNORECASE)
        
        if not cleaned:
            return None
        
        try:
            # Handle multipliers
            multiplier = 1
            if "M" in text.upper():
                multiplier = 1000000
            elif "K" in text.upper():
                multiplier = 1000
            
            value = float(cleaned)
            return int(value * multiplier)
        except ValueError:
            return None
    
    def _remove_currency(self, text: str) -> str:
        """Remove currency symbols."""
        if not isinstance(text, str):
            return text
        
        # Remove currency symbols
        cleaned = re.sub(r'[$€£¥]', '', text)
        return cleaned.strip()
    
    def _to_float(self, value: Any) -> Optional[float]:
        """Convert to float."""
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                return None
        return None
    
    def _to_int(self, value: Any) -> Optional[int]:
        """Convert to int."""
        if isinstance(value, (int, float)):
            return int(value)
        if isinstance(value, str):
            try:
                return int(float(value))
            except ValueError:
                return None
        return None
    
    def _to_bool(self, value: Any) -> bool:
        """Convert to bool."""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ["true", "yes", "1", "on"]
        if isinstance(value, (int, float)):
            return bool(value)
        return False
    
    def _strip(self, text: str) -> str:
        """Strip whitespace."""
        if isinstance(text, str):
            return text.strip()
        return text
    
    def _lower(self, text: str) -> str:
        """Convert to lowercase."""
        if isinstance(text, str):
            return text.lower()
        return text
    
    def _upper(self, text: str) -> str:
        """Convert to uppercase."""
        if isinstance(text, str):
            return text.upper()
        return text
    
    def _title_case(self, text: str) -> str:
        """Convert to title case."""
        if isinstance(text, str):
            return text.title()
        return text
    
    def _truncate(self, text: str, max_length: int = 100) -> str:
        """Truncate text to max length."""
        if isinstance(text, str) and len(text) > max_length:
            return text[:max_length] + "..."
        return text


# Global template post-processor instance
template_post_processor = TemplatePostProcessor()
