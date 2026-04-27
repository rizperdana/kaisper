"""Template storage and management."""

import json
from typing import Dict, List, Optional
from datetime import datetime
from loguru import logger

from kaisper.database import db
from kaisper.models import Template


class TemplateStorage:
    """Template storage manager."""
    
    async def save(self, template: Template) -> None:
        """Save template to database."""
        logger.info(f"Saving template {template.template_id}")
        
        await db.execute(
            """
            INSERT INTO template_versions 
            (template_id, domain, content_type, version, template_json, created_at, confidence)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            ON CONFLICT (template_id, version) DO UPDATE SET
                template_json = EXCLUDED.template_json,
                confidence = EXCLUDED.confidence
            """,
            template.template_id,
            template.domain,
            template.content_type,
            template.version,
            json.dumps(template.model_dump()),
            template.created_at,
            template.confidence,
        )
        
        logger.info(f"Template {template.template_id} saved")
    
    async def get(
        self,
        template_id: str,
        version: Optional[int] = None,
    ) -> Optional[Template]:
        """Get template from database."""
        logger.info(f"Getting template {template_id}")
        
        if version:
            row = await db.fetchrow(
                """
                SELECT template_json FROM template_versions
                WHERE template_id = $1 AND version = $2
                """,
                template_id,
                version,
            )
        else:
            # Get latest version
            row = await db.fetchrow(
                """
                SELECT template_json FROM template_versions
                WHERE template_id = $1
                ORDER BY version DESC
                LIMIT 1
                """,
                template_id,
            )
        
        if not row:
            logger.warning(f"Template {template_id} not found")
            return None
        
        template_data = json.loads(row["template_json"])
        template = Template(**template_data)
        
        logger.info(f"Template {template_id} retrieved")
        return template
    
    async def find_by_domain(
        self,
        domain: str,
        content_type: Optional[str] = None,
    ) -> List[Template]:
        """Find templates by domain."""
        logger.info(f"Finding templates for domain {domain}")
        
        if content_type:
            rows = await db.fetch(
                """
                SELECT template_json FROM template_versions
                WHERE domain = $1 AND content_type = $2
                ORDER BY version DESC
                """,
                domain,
                content_type,
            )
        else:
            rows = await db.fetch(
                """
                SELECT template_json FROM template_versions
                WHERE domain = $1
                ORDER BY version DESC
                """,
                domain,
            )
        
        templates = []
        for row in rows:
            template_data = json.loads(row["template_json"])
            templates.append(Template(**template_data))
        
        logger.info(f"Found {len(templates)} templates for domain {domain}")
        return templates
    
    async def list_all(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Template]:
        """List all templates."""
        logger.info("Listing all templates")
        
        rows = await db.fetch(
            """
            SELECT template_json FROM template_versions
            ORDER BY created_at DESC
            LIMIT $1 OFFSET $2
            """,
            limit,
            offset,
        )
        
        templates = []
        for row in rows:
            template_data = json.loads(row["template_json"])
            templates.append(Template(**template_data))
        
        logger.info(f"Listed {len(templates)} templates")
        return templates
    
    async def delete(self, template_id: str) -> bool:
        """Delete template from database."""
        logger.info(f"Deleting template {template_id}")
        
        result = await db.execute(
            """
            DELETE FROM template_versions
            WHERE template_id = $1
            """,
            template_id,
        )
        
        deleted = "DELETE 1" in result
        logger.info(f"Template {template_id} deleted: {deleted}")
        return deleted
    
    async def get_versions(self, template_id: str) -> List[int]:
        """Get all versions of a template."""
        logger.info(f"Getting versions for template {template_id}")
        
        rows = await db.fetch(
            """
            SELECT version FROM template_versions
            WHERE template_id = $1
            ORDER BY version DESC
            """,
            template_id,
        )
        
        versions = [row["version"] for row in rows]
        logger.info(f"Found {len(versions)} versions for template {template_id}")
        return versions


# Global template storage instance
template_storage = TemplateStorage()
