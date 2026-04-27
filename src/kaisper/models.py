"""Universal data models for Kaisper."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ValidationCheck(BaseModel):
    """Validation check result."""
    
    field: str
    passed: bool
    message: Optional[str] = None


class RequestConfig(BaseModel):
    """Request configuration."""
    
    method: str = "GET"
    headers: Dict[str, str] = Field(default_factory=dict)
    cookies: Dict[str, str] = Field(default_factory=dict)
    timeout: int = 30
    follow_redirects: bool = True


class ExtractionRule(BaseModel):
    """Rule for extracting a single field."""
    
    method: str = Field(description="Extraction method (xpath, css, regex)")
    pattern: str = Field(description="Selector pattern")
    extract: str = Field(description="What to extract (text, attribute, all)")
    attribute: Optional[str] = Field(default=None, description="Attribute name")
    required: bool = Field(default=False, description="Whether field is required")
    post_process: List[str] = Field(default_factory=list, description="Post-processing steps")


class PaginationConfig(BaseModel):
    """Pagination configuration."""
    
    enabled: bool = False
    method: str = "next_page"  # next_page, scroll, infinite_scroll
    selector: Optional[str] = None
    max_pages: int = 10


class JSStep(BaseModel):
    """JavaScript execution step."""
    
    code: str = Field(description="JavaScript code to execute")
    wait_for: Optional[str] = Field(default=None, description="Wait for selector before proceeding")


class ValidationConfig(BaseModel):
    """Validation configuration."""
    
    required_fields: List[str] = Field(default_factory=list)
    field_validators: Dict[str, str] = Field(default_factory=dict)


class FewShotExample(BaseModel):
    """Few-shot learning example."""
    
    input: str = Field(description="Example input (HTML, etc.)")
    output: Dict[str, Any] = Field(description="Example output")


class DetectionRule(BaseModel):
    """Content type detection rule."""
    
    selector: str = Field(description="CSS selector")
    attribute: str = Field(description="Attribute to check")
    pattern: str = Field(description="Pattern to match")
    content_type: str = Field(description="Detected content type")


class PostProcessingStep(BaseModel):
    """Post-processing step."""
    
    type: str = Field(description="Step type (clean, normalize, transform)")
    field: str = Field(description="Field to process")
    params: Dict[str, Any] = Field(default_factory=dict)


class Template(BaseModel):
    """Universal extraction template."""
    
    # Metadata
    template_id: str = Field(description="Unique template ID")
    domain: str = Field(description="Domain this template applies to")
    content_type: str = Field(description="Content type (video, product, article, etc.)")
    version: int = Field(default=1, description="Template version")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Template confidence score")
    
    # Extraction rules
    extraction: Dict[str, ExtractionRule] = Field(default_factory=dict)
    
    # Request configuration
    request: RequestConfig = Field(default_factory=RequestConfig)
    
    # Pagination
    pagination: Optional[PaginationConfig] = None
    
    # JavaScript steps
    js_steps: List[JSStep] = Field(default_factory=list)
    
    # Validation
    validation: ValidationConfig = Field(default_factory=ValidationConfig)
    
    # Fallback selectors
    fallback_selectors: List[Dict[str, ExtractionRule]] = Field(default_factory=list)
    
    # Schema.org mapping
    schema_org_type: Optional[str] = None
    schema_org_mapping: Optional[Dict[str, str]] = None
    
    # Few-shot examples
    few_shot_examples: List[FewShotExample] = Field(default_factory=list)
    
    # Content type detection
    content_type_detection_rules: List[DetectionRule] = Field(default_factory=list)
    
    # Post-processing
    post_processing_steps: List[PostProcessingStep] = Field(default_factory=list)


class UniversalContent(BaseModel):
    """Universal content model for any content type."""
    
    # Common fields
    url: str = Field(description="Content URL")
    content_type: str = Field(description="Content type")
    source_domain: str = Field(description="Source domain")
    title: Optional[str] = None
    description: Optional[str] = None
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Flexible content storage
    content: Dict[str, Any] = Field(default_factory=dict)
    
    # Binary references
    binary_storage_path: Optional[str] = None
    binary_size: Optional[int] = None
    binary_mime_type: Optional[str] = None
    
    # Schema.org integration
    schema_org_type: Optional[str] = None
    schema_org_data: Optional[Dict[str, Any]] = None
    open_graph_data: Optional[Dict[str, Any]] = None
    
    # Metadata
    checksum: Optional[str] = None
    language: Optional[str] = None
    author: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class ExtractionResult(BaseModel):
    """Universal extraction result."""
    
    # Common fields
    url: str = Field(description="Content URL")
    content_type: str = Field(description="Content type")
    source_domain: str = Field(description="Source domain")
    title: Optional[str] = None
    description: Optional[str] = None
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Flexible content storage
    content: Dict[str, Any] = Field(default_factory=dict)
    
    # Binary references
    binary_storage_path: Optional[str] = None
    binary_size: Optional[int] = None
    binary_mime_type: Optional[str] = None
    
    # Schema.org integration
    schema_org_type: Optional[str] = None
    schema_org_data: Optional[Dict[str, Any]] = None
    open_graph_data: Optional[Dict[str, Any]] = None
    
    # Content detection
    detected_content_type: str = Field(description="Detected content type")
    detection_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    detection_method: str = Field(description="Detection method")
    
    # Template metadata
    template_id: str = Field(description="Template ID used")
    template_version: int = Field(default=1, description="Template version used")
    template_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    
    # Metadata
    checksum: Optional[str] = None
    language: Optional[str] = None
    author: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    
    # Validation
    validation_score: float = Field(default=0.0, ge=0.0, le=1.0)
    validation_checks: List[ValidationCheck] = Field(default_factory=list)
