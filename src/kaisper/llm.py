"""LLM client for template generation."""

import json
from typing import Any, Dict, List, Optional
from loguru import logger

import httpx
from openai import AsyncOpenAI

from kaisper.config import settings
from kaisper.models import Template


class LLMClient:
    """LLM client for template generation."""
    
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.llm.api_key,
            base_url=settings.llm.base_url,
        )
        self.model = settings.llm.model
        self.temperature = settings.llm.temperature
        self.max_tokens = settings.llm.max_tokens
        self.timeout = settings.llm.timeout
    
    async def generate_template(
        self,
        html: str,
        url: str,
        content_type: str,
        few_shot_examples: Optional[List[Dict[str, Any]]] = None,
    ) -> Template:
        """Generate extraction template from HTML."""
        logger.info(f"Generating template for {url} (content_type: {content_type})")
        
        # Build prompt
        prompt = self._build_prompt(
            html=html,
            url=url,
            content_type=content_type,
            few_shot_examples=few_shot_examples or [],
        )
        
        # Call LLM
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert web scraping assistant. Generate extraction templates from HTML.",
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                timeout=self.timeout,
            )
            
            # Parse response
            content = response.choices[0].message.content
            template_data = json.loads(content)
            
            # Create template
            template = Template(
                template_id=f"{url.replace('://', '_').replace('/', '_')}",
                domain=url.split('/')[2],
                content_type=content_type,
                confidence=0.8,
                **template_data,
            )
            
            logger.info(f"Template generated for {url}")
            return template
            
        except Exception as e:
            logger.error(f"Failed to generate template for {url}: {e}")
            raise
    
    def _build_prompt(
        self,
        html: str,
        url: str,
        content_type: str,
        few_shot_examples: List[Dict[str, Any]],
    ) -> str:
        """Build prompt for template generation."""
        
        prompt = f"""Generate an extraction template for the following webpage.

URL: {url}
Content Type: {content_type}

HTML:
{html[:10000]}  # Truncate to avoid token limits

"""
        
        if few_shot_examples:
            prompt += "\nExamples:\n"
            for i, example in enumerate(few_shot_examples, 1):
                prompt += f"\nExample {i}:\n"
                prompt += f"Input: {example['input'][:5000]}\n"
                prompt += f"Output: {json.dumps(example['output'], indent=2)}\n"
        
        prompt += """
Generate a JSON template with the following structure:
{
  "extraction": {
    "title": {
      "method": "xpath|css|regex",
      "pattern": "selector pattern",
      "extract": "text|attribute",
      "attribute": "attribute name (if applicable)",
      "required": true,
      "post_process": []
    },
    "description": { ... },
    "price": { ... },
    "images": { ... }
  },
  "validation": {
    "required_fields": ["title", "description"],
    "field_validators": {}
  }
}

Return only the JSON, no other text.
"""
        
        return prompt
    
    async def validate_template(self, template: Template) -> bool:
        """Validate template structure."""
        logger.info(f"Validating template {template.template_id}")
        
        # Check required fields
        if not template.extraction:
            logger.warning(f"Template {template.template_id} has no extraction rules")
            return False
        
        # Check extraction rules
        for field_name, rule in template.extraction.items():
            if not rule.method or not rule.pattern:
                logger.warning(f"Field {field_name} has invalid extraction rule")
                return False
        
        logger.info(f"Template {template.template_id} is valid")
        return True
    
    async def improve_template(
        self,
        template: Template,
        feedback: str,
    ) -> Template:
        """Improve template based on feedback."""
        logger.info(f"Improving template {template.template_id}")
        
        prompt = f"""Improve the following extraction template based on feedback.

Current Template:
{json.dumps(template.model_dump(), indent=2)}

Feedback:
{feedback}

Generate an improved JSON template with the same structure.
Return only the JSON, no other text.
"""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert web scraping assistant. Improve extraction templates.",
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                timeout=self.timeout,
            )
            
            content = response.choices[0].message.content
            improved_data = json.loads(content)
            
            # Update template
            template.extraction = improved_data.get("extraction", template.extraction)
            template.validation = improved_data.get("validation", template.validation)
            template.confidence = min(template.confidence + 0.1, 1.0)
            
            logger.info(f"Template {template.template_id} improved")
            return template
            
        except Exception as e:
            logger.error(f"Failed to improve template {template.template_id}: {e}")
            raise


# Global LLM client instance
llm_client = LLMClient()
