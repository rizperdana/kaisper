"""Template generation orchestrator."""

from typing import Dict, List, Optional
from loguru import logger

from kaisper.fetcher import fetcher
from kaisper.llm import llm_client
from kaisper.template_storage import template_storage
from kaisper.models import Template


class TemplateGenerator:
    """Template generation orchestrator."""
    
    async def generate(
        self,
        url: str,
        content_type: Optional[str] = None,
        few_shot_examples: Optional[List[Dict]] = None,
        force_regenerate: bool = False,
    ) -> Template:
        """Generate or retrieve template for URL."""
        logger.info(f"Generating template for {url}")
        
        # Check if template already exists
        domain = url.split('/')[2]
        existing_templates = await template_storage.find_by_domain(domain, content_type)
        
        if existing_templates and not force_regenerate:
            logger.info(f"Using existing template for {domain}")
            return existing_templates[0]
        
        # Fetch page
        response = await fetcher.fetch_with_retry(url)
        html = response.get("content", "")
        
        # Detect content type if not provided
        if not content_type:
            content_type = self._detect_content_type(html, url)
        
        # Generate template
        template = await llm_client.generate_template(
            html=html,
            url=url,
            content_type=content_type,
            few_shot_examples=few_shot_examples,
        )
        
        # Validate template
        is_valid = await llm_client.validate_template(template)
        if not is_valid:
            logger.warning(f"Template validation failed for {url}")
            # Try to improve template
            template = await llm_client.improve_template(
                template,
                feedback="Template validation failed. Fix extraction rules.",
            )
        
        # Save template
        await template_storage.save(template)
        
        logger.info(f"Template generated and saved for {url}")
        return template
    
    def _detect_content_type(self, html: str, url: str) -> str:
        """Detect content type from HTML."""
        # Simple heuristic detection
        html_lower = html.lower()
        
        # Check for product indicators
        if any(keyword in html_lower for keyword in ["price", "add to cart", "buy now"]):
            return "product"
        
        # Check for article indicators
        if any(keyword in html_lower for keyword in ["article", "blog", "post"]):
            return "article"
        
        # Check for video indicators
        if any(keyword in html_lower for keyword in ["video", "watch", "play"]):
            return "video"
        
        # Default to generic
        return "generic"
    
    async def batch_generate(
        self,
        urls: List[str],
        content_type: Optional[str] = None,
    ) -> List[Template]:
        """Generate templates for multiple URLs."""
        logger.info(f"Batch generating templates for {len(urls)} URLs")
        
        templates = []
        for url in urls:
            try:
                template = await self.generate(url, content_type)
                templates.append(template)
            except Exception as e:
                logger.error(f"Failed to generate template for {url}: {e}")
        
        logger.info(f"Generated {len(templates)} templates")
        return templates
    
    async def improve_template(
        self,
        template_id: str,
        feedback: str,
    ) -> Optional[Template]:
        """Improve existing template."""
        logger.info(f"Improving template {template_id}")
        
        # Get template
        template = await template_storage.get(template_id)
        if not template:
            logger.warning(f"Template {template_id} not found")
            return None
        
        # Improve template
        improved_template = await llm_client.improve_template(template, feedback)
        
        # Increment version
        improved_template.version += 1
        improved_template.created_at = datetime.utcnow()
        
        # Save improved template
        await template_storage.save(improved_template)
        
        logger.info(f"Template {template_id} improved and saved")
        return improved_template


# Global template generator instance
template_generator = TemplateGenerator()
