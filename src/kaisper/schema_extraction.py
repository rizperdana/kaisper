"""Schema-guided extraction for Kaisper."""

import json
from typing import Any, Dict, List, Optional
from loguru import logger

from kaisper.models import Template, ExtractionResult


class SchemaGuidedExtraction:
    """Schema-guided extraction using JSON Schema."""
    
    def __init__(self):
        """Initialize schema-guided extraction."""
        self.schemas = {}
    
    def register_schema(
        self,
        content_type: str,
        schema: Dict[str, Any],
    ) -> None:
        """Register a schema for a content type."""
        self.schemas[content_type] = schema
        logger.info(f"Registered schema for content type: {content_type}")
    
    def get_schema(self, content_type: str) -> Optional[Dict[str, Any]]:
        """Get schema for a content type."""
        return self.schemas.get(content_type)
    
    def validate_against_schema(
        self,
        data: Dict[str, Any],
        schema: Dict[str, Any],
    ) -> bool:
        """Validate data against schema."""
        try:
            # Check required fields
            required_fields = schema.get("required", [])
            for field in required_fields:
                if field not in data or data[field] is None:
                    logger.warning(f"Required field missing: {field}")
                    return False
            
            # Check field types
            properties = schema.get("properties", {})
            for field, field_schema in properties.items():
                if field in data and data[field] is not None:
                    expected_type = field_schema.get("type")
                    actual_value = data[field]
                    
                    if expected_type == "string" and not isinstance(actual_value, str):
                        logger.warning(f"Field {field} should be string, got {type(actual_value)}")
                        return False
                    
                    if expected_type == "number" and not isinstance(actual_value, (int, float)):
                        logger.warning(f"Field {field} should be number, got {type(actual_value)}")
                        return False
                    
                    if expected_type == "array" and not isinstance(actual_value, list):
                        logger.warning(f"Field {field} should be array, got {type(actual_value)}")
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Schema validation failed: {e}")
            return False
    
    def extract_with_schema(
        self,
        html: str,
        template: Template,
        schema: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Extract data using template and validate against schema."""
        
        # Use template's schema if not provided
        if schema is None and template.schema_org_type:
            schema = self.get_schema(template.schema_org_type)
        
        # Extract data using template
        extracted_data = {}
        
        for field_name, rule in template.extraction.items():
            try:
                # Apply extraction rule
                value = self._apply_extraction_rule(html, rule)
                
                # Apply post-processing
                if rule.post_process:
                    value = self._apply_post_processing(value, rule.post_process)
                
                extracted_data[field_name] = value
                
            except Exception as e:
                logger.error(f"Failed to extract field {field_name}: {e}")
                if rule.required:
                    extracted_data[field_name] = None
        
        # Validate against schema
        if schema:
            is_valid = self.validate_against_schema(extracted_data, schema)
            if not is_valid:
                logger.warning("Extracted data does not match schema")
        
        return extracted_data
    
    def _apply_extraction_rule(
        self,
        html: str,
        rule: Any,
    ) -> Any:
        """Apply extraction rule to HTML."""
        # This would use Parsel or similar library
        # For now, return placeholder
        return "extracted_value"
    
    def _apply_post_processing(
        self,
        value: Any,
        post_process: List[str],
    ) -> Any:
        """Apply post-processing steps."""
        for step in post_process:
            if step == "remove_currency":
                if isinstance(value, str):
                    value = value.replace("$", "").replace("€", "").replace("£", "").strip()
            elif step == "to_float":
                if isinstance(value, str):
                    value = float(value)
            elif step == "to_int":
                if isinstance(value, str):
                    value = int(value)
            elif step == "strip":
                if isinstance(value, str):
                    value = value.strip()
            elif step == "lower":
                if isinstance(value, str):
                    value = value.lower()
            elif step == "upper":
                if isinstance(value, str):
                    value = value.upper()
        
        return value
    
    def generate_schema_from_template(
        self,
        template: Template,
    ) -> Dict[str, Any]:
        """Generate JSON Schema from template."""
        
        properties = {}
        required = []
        
        for field_name, rule in template.extraction.items():
            field_schema = {
                "type": "string",
                "description": f"Extracted using {rule.method}",
            }
            
            if rule.required:
                required.append(field_name)
            
            properties[field_name] = field_schema
        
        schema = {
            "type": "object",
            "properties": properties,
            "required": required,
        }
        
        return schema


# Global schema-guided extraction instance
schema_guided_extraction = SchemaGuidedExtraction()
