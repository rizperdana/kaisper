"""Tests for Kaisper foundation components."""

import pytest
from kaisper.config import settings
from kaisper.models import Template, ExtractionResult, UniversalContent


def test_settings():
    """Test settings configuration."""
    assert settings.database.host == "localhost"
    assert settings.database.port == 5432
    assert settings.llm.model == "kilo-auto/free"
    assert settings.llm.provider == "cliproxyapi"
    assert settings.fetcher.timeout == 30


def test_template_model():
    """Test Template model."""
    template = Template(
        template_id="test-template",
        domain="example.com",
        content_type="product",
        confidence=0.9,
    )
    
    assert template.template_id == "test-template"
    assert template.domain == "example.com"
    assert template.content_type == "product"
    assert template.confidence == 0.9
    assert template.version == 1


def test_extraction_result_model():
    """Test ExtractionResult model."""
    result = ExtractionResult(
        url="https://example.com/product/1",
        content_type="product",
        source_domain="example.com",
        title="Test Product",
        detected_content_type="product",
        detection_confidence=0.95,
        detection_method="schema_org",
        template_id="test-template",
        template_version=1,
        template_confidence=0.9,
    )
    
    assert result.url == "https://example.com/product/1"
    assert result.content_type == "product"
    assert result.title == "Test Product"
    assert result.detected_content_type == "product"
    assert result.detection_confidence == 0.95


def test_universal_content_model():
    """Test UniversalContent model."""
    content = UniversalContent(
        url="https://example.com/product/1",
        content_type="product",
        source_domain="example.com",
        title="Test Product",
    )
    
    assert content.url == "https://example.com/product/1"
    assert content.content_type == "product"
    assert content.title == "Test Product"
    assert content.scraped_at is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
