"""Tests for Kaisper Phase 2: Template Generation."""

import pytest
from kaisper.config import settings
from kaisper.models import Template, ExtractionResult, UniversalContent
from kaisper.llm import llm_client
from kaisper.template_storage import template_storage


def test_llm_settings():
    """Test LLM settings configuration."""
    assert settings.llm.provider == "cliproxyapi"
    assert settings.llm.api_key == "sk-dIMp6qoD0oWyMvswe"
    assert settings.llm.base_url == "http://localhost:83117/v1"
    assert settings.llm.model == "kilo-auto/free"
    assert settings.llm.temperature == 0.1


def test_template_storage():
    """Test template storage."""
    template = Template(
        template_id="test-template-storage",
        domain="example.com",
        content_type="product",
        confidence=0.9,
    )
    
    # Test save (would need database connection)
    # await template_storage.save(template)
    
    # Test get (would need database connection)
    # retrieved = await template_storage.get("test-template-storage")
    # assert retrieved is not None
    # assert retrieved.template_id == "test-template-storage"
    
    assert template.template_id == "test-template-storage"


def test_llm_client():
    """Test LLM client initialization."""
    assert llm_client is not None
    assert llm_client.model == "kilo-auto/free"
    assert llm_client.temperature == 0.1


def test_template_generator():
    """Test template generator initialization."""
    from kaisper.template_generator import template_generator
    
    assert template_generator is not None


def test_content_type_detection():
    """Test content type detection."""
    from kaisper.template_generator import TemplateGenerator
    
    generator = TemplateGenerator()
    
    # Product detection
    html_product = "<html><body><div class='price'>$99.99</div><button>Add to Cart</button></body></html>"
    content_type = generator._detect_content_type(html_product, "https://example.com/product")
    assert content_type == "product"
    
    # Article detection
    html_article = "<html><body><article><h1>Blog Post</h1><p>Content here</p></article></body></html>"
    content_type = generator._detect_content_type(html_article, "https://example.com/blog")
    assert content_type == "article"
    
    # Video detection
    html_video = "<html><body><video src='video.mp4'></video><button>Play</button></body></html>"
    content_type = generator._detect_content_type(html_video, "https://example.com/video")
    assert content_type == "video"
    
    # Generic detection
    html_generic = "<html><body><div>Generic content</div></body></html>"
    content_type = generator._detect_content_type(html_generic, "https://example.com")
    assert content_type == "generic"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
