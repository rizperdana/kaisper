"""Prompt templates for different content types."""

from typing import Dict, List, Optional


class PromptTemplates:
    """Prompt templates for different content types."""
    
    # System prompts
    SYSTEM_PROMPTS = {
        "default": "You are an expert web scraping assistant. Generate extraction templates from HTML.",
        "product": "You are an expert e-commerce scraping assistant. Generate extraction templates for product pages.",
        "article": "You are an expert content scraping assistant. Generate extraction templates for articles and blog posts.",
        "video": "You are an expert video scraping assistant. Generate extraction templates for video pages.",
        "generic": "You are an expert web scraping assistant. Generate extraction templates for generic web pages.",
    }
    
    # Few-shot examples
    FEW_SHOT_EXAMPLES = {
        "product": [
            {
                "input": '<div class="product"><h1 class="title">iPhone 15 Pro</h1><div class="price">$999.00</div><p class="description">The most powerful iPhone ever.</p></div>',
                "output": {
                    "extraction": {
                        "title": {
                            "method": "css",
                            "pattern": ".title",
                            "extract": "text",
                            "required": True,
                        },
                        "price": {
                            "method": "css",
                            "pattern": ".price",
                            "extract": "text",
                            "required": True,
                            "post_process": ["remove_currency", "to_float"],
                        },
                        "description": {
                            "method": "css",
                            "pattern": ".description",
                            "extract": "text",
                            "required": True,
                        },
                    },
                    "validation": {
                        "required_fields": ["title", "price", "description"],
                        "field_validators": {
                            "price": "must_be_positive_number",
                        },
                    },
                },
            },
        ],
        "article": [
            {
                "input": '<article><h1 class="headline">Breaking News</h1><div class="author">John Doe</div><div class="content">This is the article content.</div><div class="date">2024-01-01</div></article>',
                "output": {
                    "extraction": {
                        "title": {
                            "method": "css",
                            "pattern": ".headline",
                            "extract": "text",
                            "required": True,
                        },
                        "author": {
                            "method": "css",
                            "pattern": ".author",
                            "extract": "text",
                            "required": False,
                        },
                        "content": {
                            "method": "css",
                            "pattern": ".content",
                            "extract": "text",
                            "required": True,
                        },
                        "date": {
                            "method": "css",
                            "pattern": ".date",
                            "extract": "text",
                            "required": False,
                            "post_process": ["parse_date"],
                        },
                    },
                    "validation": {
                        "required_fields": ["title", "content"],
                        "field_validators": {},
                    },
                },
            },
        ],
        "video": [
            {
                "input": '<div class="video"><h1 class="title">Amazing Video</h1><div class="duration">10:30</div><div class="views">1M views</div><div class="author">Video Creator</div></div>',
                "output": {
                    "extraction": {
                        "title": {
                            "method": "css",
                            "pattern": ".title",
                            "extract": "text",
                            "required": True,
                        },
                        "duration": {
                            "method": "css",
                            "pattern": ".duration",
                            "extract": "text",
                            "required": True,
                            "post_process": ["parse_duration"],
                        },
                        "views": {
                            "method": "css",
                            "pattern": ".views",
                            "extract": "text",
                            "required": False,
                            "post_process": ["parse_views"],
                        },
                        "author": {
                            "method": "css",
                            "pattern": ".author",
                            "extract": "text",
                            "required": False,
                        },
                    },
                    "validation": {
                        "required_fields": ["title", "duration"],
                        "field_validators": {},
                    },
                },
            },
        ],
    }
    
    # Extraction instructions
    EXTRACTION_INSTRUCTIONS = {
        "product": """Extract product information including:
- Title (product name)
- Price (numeric value)
- Description (product details)
- Images (product images)
- Availability (in stock, out of stock)
- Rating (if available)
- Reviews (if available)""",
        "article": """Extract article information including:
- Title (headline)
- Author (author name)
- Content (article body)
- Date (publication date)
- Tags (if available)
- Category (if available)""",
        "video": """Extract video information including:
- Title (video title)
- Duration (video length)
- Views (view count)
- Author (channel/creator)
- Upload date (if available)
- Description (video description)""",
        "generic": """Extract the main content from the page including:
- Title (page title)
- Description (page description)
- Main content (body text)
- Images (if available)
- Links (if relevant)""",
    }
    
    @classmethod
    def get_system_prompt(cls, content_type: str) -> str:
        """Get system prompt for content type."""
        return cls.SYSTEM_PROMPTS.get(content_type, cls.SYSTEM_PROMPTS["default"])
    
    @classmethod
    def get_few_shot_examples(cls, content_type: str) -> List[Dict]:
        """Get few-shot examples for content type."""
        return cls.FEW_SHOT_EXAMPLES.get(content_type, [])
    
    @classmethod
    def get_extraction_instructions(cls, content_type: str) -> str:
        """Get extraction instructions for content type."""
        return cls.EXTRACTION_INSTRUCTIONS.get(content_type, cls.EXTRACTION_INSTRUCTIONS["generic"])
    
    @classmethod
    def build_prompt(
        cls,
        html: str,
        url: str,
        content_type: str,
        few_shot_examples: Optional[List[Dict]] = None,
    ) -> str:
        """Build prompt for template generation."""
        
        system_prompt = cls.get_system_prompt(content_type)
        extraction_instructions = cls.get_extraction_instructions(content_type)
        examples = few_shot_examples or cls.get_few_shot_examples(content_type)
        
        prompt = f"""Generate an extraction template for the following webpage.

URL: {url}
Content Type: {content_type}

HTML:
{html[:10000]}

"""
        
        if examples:
            prompt += "Examples:\n"
            for i, example in enumerate(examples, 1):
                prompt += f"\nExample {i}:\n"
                prompt += f"Input: {example['input'][:5000]}\n"
                prompt += f"Output: {json.dumps(example['output'], indent=2)}\n"
        
        prompt += f"""
Extraction Instructions:
{extraction_instructions}

Generate a JSON template with the following structure:
{{
  "extraction": {{
    "field_name": {{
      "method": "xpath|css|regex",
      "pattern": "selector pattern",
      "extract": "text|attribute",
      "attribute": "attribute name (if applicable)",
      "required": true,
      "post_process": []
    }}
  }},
  "validation": {{
    "required_fields": ["field1", "field2"],
    "field_validators": {{}}
  }}
}}

Return only the JSON, no other text.
"""
        
        return prompt
