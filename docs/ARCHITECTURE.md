---
title: Kaisper Architecture
version: 0.1.0
status: complete
last_updated: 2026-04-26
---

# Kaisper Architecture

## System Overview

Kaisper is a universal AI-driven scraping system that can extract ANY type of content from ANY website using LLM-generated templates and a single deterministic execution engine.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLI Interface                            │
│                    (Typer-based commands)                        │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Orchestration Layer                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Task Queue  │  │  Scheduler   │  │  Coordinator │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Template Generation Layer                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Fetcher     │  │  Content     │  │  Schema Org  │         │
│  │  (Obscura)   │  │  Detector    │  │  Parser      │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                       ↓                   ↓                       │
│              ┌──────────────┐  ┌──────────────┐               │
│              │  LLM Client  │  │  Few Shot    │               │
│              │  (OpenAI)    │  │  Examples    │               │
│              └──────────────┘  └──────────────┘               │
│                       ↓                                           │
│              ┌──────────────┐                                  │
│              │  Template    │                                  │
│              │  Generator   │                                  │
│              └──────────────┘                                  │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Execution Engine Layer                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Extractor   │  │  Validator   │  │  Schema      │         │
│  │  (Parsel)    │  │  (Pydantic)  │  │  Normalizer  │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                       ↓                                           │
│              ┌──────────────┐  ┌──────────────┐               │
│              │  Post        │  │  Vision      │               │
│              │  Processor   │  │  Scraper     │               │
│              └──────────────┘  └──────────────┘               │
│                       ↓                                           │
│              ┌──────────────┐                                  │
│              │  Fallback    │                                  │
│              │  Chain       │                                  │
│              └──────────────┘                                  │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Storage Layer                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  PostgreSQL  │  │  S3 Storage  │  │  Template    │         │
│  │  (JSONB)     │  │  (Binaries)  │  │  Cache       │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Template    │  │  Schema Org  │  │  Content     │         │
│  │  Versioning  │  │  Cache       │  │  Classifier  │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

## Component Breakdown

### 1. CLI Interface

**Purpose**: User-facing command-line interface

**Components**:
- `cli.py` - Main Typer app
- Command handlers for: scrape, batch, template, config, status

**Responsibilities**:
- Parse user commands
- Validate inputs
- Invoke appropriate services
- Format and display results

### 2. Orchestration Layer

**Purpose**: Coordinate scraping tasks and manage workflow

**Components**:
- `TaskQueue` - Queue of URLs to scrape
- `Scheduler` - Schedule tasks with priorities
- `Coordinator` - Coordinate between layers

**Responsibilities**:
- Manage task lifecycle
- Handle retries and failures
- Enforce rate limiting
- Track progress

### 3. Template Generation Layer

**Purpose**: Generate extraction templates using LLM

**Components**:
- `Fetcher` - Fetch and analyze web pages
- `ContentDetector` - Detect content type from Schema.org, Open Graph, ML
- `SchemaOrgParser` - Parse Schema.org JSON-LD and Microdata
- `LLMClient` - Interface to LLM APIs with schema-guided extraction
- `FewShotExampleStore` - Store and retrieve few-shot examples
- `TemplateGenerator` - Generate templates from analysis

**Responsibilities**:
- Fetch page content (HTML, network requests)
- Detect content type using multiple signals
- Parse Schema.org and Open Graph data
- Generate extraction rules with few-shot learning
- Validate and sanitize templates

### 4. Execution Engine Layer

**Purpose**: Execute templates deterministically

**Components**:
- `Extractor` - Apply selectors and extract data
- `Validator` - Validate extracted results
- `SchemaNormalizer` - Normalize extracted data to Schema.org
- `PostProcessor` - Apply content-type-specific post-processing
- `VisionScraper` - Screenshot-based extraction (fallback)
- `FallbackChain` - Chain of fallback scrapers

**Responsibilities**:
- Execute extraction rules
- Apply post-processing
- Normalize to Schema.org
- Validate results
- Handle failures gracefully
- Use vision scraping as last resort

### 5. Storage Layer

**Purpose**: Store templates, results, and binary content

**Components**:
- `PostgreSQLClient` - Store structured data
- `S3Client` - Store binary content
- `TemplateCache` - Cache templates
- `TemplateVersionManager` - Manage template versions
- `SchemaOrgCache` - Cache Schema.org data
- `ContentClassifier` - ML model for content type detection

**Responsibilities**:
- Store extraction results
- Cache templates
- Manage binary content
- Provide query interfaces
- Track template versions
- Cache Schema.org data

## Data Flow

### Template Generation Flow

```
1. User provides URL
   ↓
2. Fetcher fetches page (Obscura/Playwright)
   ↓
3. Capture DOM and network requests
   ↓
4. ContentDetector identifies content type
   ↓
5. SchemaOrgParser parses Schema.org data
   ↓
6. FewShotExampleStore retrieves examples
   ↓
7. LLM analyzes structure with few-shot examples
   ↓
8. TemplateGenerator creates template
   ↓
9. TemplateValidator validates template
   ↓
10. TemplateVersionManager creates version
   ↓
11. TemplateStore saves template
   ↓
12. Return template to user
```

### Extraction Flow

```
1. User provides URL (and optional template_id)
   ↓
2. Check template cache
   ↓
3a. Template found → Use cached template
3b. Template not found → Generate new template
   ↓
4. Fetcher fetches page
   ↓
5. ContentDetector identifies content type
   ↓
6. Extractor applies template selectors
   ↓
7. SchemaNormalizer normalizes to Schema.org
   ↓
8. PostProcessor applies content-type-specific processing
   ↓
9. Validator validates results
   ↓
10a. Validation passes → Store results
10b. Validation fails → Try fallback chain
   ↓
11. FallbackChain: AI → Scrapy → Regex → Vision
   ↓
12. Return results to user
```

## Universal Data Model

### Content Type Abstraction

Kaisper uses a **content-type-agnostic** approach where the engine doesn't need to know about specific content types. All content is represented using a unified schema:

```python
class ExtractionResult(BaseModel):
    """Universal extraction result for any content type."""
    
    # Common fields (all content types)
    url: str
    content_type: str  # 'video', 'image', 'product', 'article', 'raw_html', etc.
    source_domain: str
    title: Optional[str]
    description: Optional[str]
    scraped_at: datetime
    
    # Flexible content storage
    content: Dict[str, Any]  # Type-specific data
    
    # Binary references
    binary_storage_path: Optional[str]
    binary_size: Optional[int]
    binary_mime_type: Optional[str]
    
    # Schema.org integration
    schema_org_type: Optional[str]
    schema_org_data: Optional[Dict[str, Any]]
    open_graph_data: Optional[Dict[str, Any]]
    
    # Content detection
    detected_content_type: str
    detection_confidence: float
    detection_method: str  # 'schema_org', 'open_graph', 'ml_classifier'
    
    # Template metadata
    template_id: str
    template_version: int
    template_confidence: float
    
    # Metadata
    checksum: Optional[str]
    language: Optional[str]
    author: Optional[str]
    tags: List[str]
    
    # Validation
    validation_score: float
    validation_checks: List[ValidationCheck]
```

### Content Type Examples

**Video Content**:
```json
{
  "content_type": "video",
  "content": {
    "video_url": "https://example.com/video.mp4",
    "duration_seconds": 300,
    "resolution": "1920x1080",
    "format": "mp4",
    "thumbnail": "https://example.com/thumb.jpg",
    "transcript_available": true,
    "views": 10000,
    "likes": 500
  }
}
```

**Product Content**:
```json
{
  "content_type": "product",
  "content": {
    "price": 99.99,
    "currency": "USD",
    "availability": "in_stock",
    "sku": "PROD-12345",
    "brand": "ExampleBrand",
    "categories": ["electronics", "smartphones"],
    "specifications": {
      "screen_size": "6.5 inch",
      "storage": "128GB",
      "ram": "8GB"
    },
    "images": ["https://example.com/img1.jpg"]
  }
}
```

**Article Content**:
```json
{
  "content_type": "article",
  "content": {
    "author": "John Doe",
    "publish_date": "2024-01-15",
    "word_count": 1500,
    "reading_time_minutes": 7,
    "categories": ["technology", "AI"],
    "featured_image": "https://example.com/featured.jpg",
    "related_links": ["https://example.com/related1"]
  }
}
```

## Universal Template Schema

### Template Structure

Templates are designed to work for ANY content type without modification:

```python
class Template(BaseModel):
    """Universal extraction template."""
    
    # Metadata
    template_id: str
    domain: str
    content_type: str  # 'video', 'product', 'article', etc.
    version: int
    created_at: datetime
    confidence: float
    
    # Extraction rules (content-type-agnostic)
    extraction: Dict[str, ExtractionRule]
    
    # Request configuration
    request: RequestConfig
    
    # Pagination (optional)
    pagination: Optional[PaginationConfig]
    
    # JavaScript steps (optional)
    js_steps: List[JSStep]
    
    # Validation rules
    validation: ValidationConfig
    
    # Fallback selectors
    fallback_selectors: List[Dict[str, ExtractionRule]]
    
    # Schema.org mapping
    schema_org_type: Optional[str]
    schema_org_mapping: Optional[Dict[str, str]]
    
    # Few-shot examples
    few_shot_examples: List[FewShotExample]
    
    # Content type detection
    content_type_detection_rules: List[DetectionRule]
    
    # Post-processing
    post_processing_steps: List[PostProcessingStep]
```

### Extraction Rule

```python
class ExtractionRule(BaseModel):
    """Rule for extracting a single field."""
    
    method: str  # 'xpath', 'css', 'regex'
    pattern: str
    extract: str  # 'text', 'attribute', 'all'
    attribute: Optional[str]  # For attribute extraction
    required: bool
    post_process: List[str]  # Post-processing steps
```

## Content Type Detection

### Multi-Signal Detection

Kaisper uses a multi-signal approach to detect content types:

1. **Schema.org** - Check for JSON-LD or Microdata
2. **Open Graph** - Check for og:type meta tags
3. **ML Classifier** - Use trained model as fallback

### Implementation

```python
class ContentDetector:
    def detect_content_type(self, url: str, html: str) -> ContentDetectionResult:
        # 1. Check for Schema.org
        schema_type = self._extract_schema_org_type(html)
        if schema_type:
            return ContentDetectionResult(
                content_type=self._map_schema_to_content_type(schema_type),
                confidence=0.95,
                method='schema_org'
            )
        
        # 2. Check for Open Graph
        og_type = self._extract_open_graph_type(html)
        if og_type:
            return ContentDetectionResult(
                content_type=self._map_og_to_content_type(og_type),
                confidence=0.90,
                method='open_graph'
            )
        
        # 3. Use ML classifier
        features = self._extract_features(url, html)
        predicted_type, confidence = self._classifier.predict(features)
        
        return ContentDetectionResult(
            content_type=predicted_type,
            confidence=confidence,
            method='ml_classifier'
        )
    
    def _extract_schema_org_type(self, html: str) -> Optional[str]:
        # Extract @type from JSON-LD
        # Extract itemtype from Microdata
        pass
    
    def _extract_open_graph_type(self, html: str) -> Optional[str]:
        # Extract og:type from meta tags
        pass
```

### Schema.org Integration

```python
class SchemaOrgParser:
    def parse(self, html: str) -> Optional[SchemaOrgData]:
        # Extract JSON-LD
        json_ld = self._extract_json_ld(html)
        if json_ld:
            return SchemaOrgData.parse_obj(json_ld)
        
        # Extract Microdata
        microdata = self._extract_microdata(html)
        if microdata:
            return SchemaOrgData.parse_obj(microdata)
        
        return None

class SchemaOrgMapper:
    def map_to_universal(self, schema_data: SchemaOrgData) -> UniversalContent:
        # Map Schema.org types to internal content types
        content_type = self._map_type(schema_data['@type'])
        
        # Extract common fields
        return UniversalContent(
            content_type=content_type,
            title=schema_data.get('name'),
            description=schema_data.get('description'),
            content=schema_data,
            schema_org_type=schema_data['@type'],
            schema_org_data=schema_data
        )
```

## Vision Scraping

### Screenshot-Based Extraction

Vision scraping is used as a fallback when HTML parsing fails:

```python
class VisionScraper:
    def scrape_with_vision(self, url: str) -> Dict[str, Any]:
        # 1. Capture screenshot
        screenshot = self._capture_screenshot(url)
        
        # 2. Encode to base64
        image_base64 = base64.b64encode(screenshot).decode('utf-8')
        
        # 3. Send to vision model
        response = self.vision_client.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "system",
                "content": [{
                    "type": "text",
                    "text": "Extract structured data from this screenshot"
                }, {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_base64}"
                    }
                }]
            }]
        )
        
        # 4. Parse and validate
        return json.loads(response.choices[0].message.content)
```

### Integration with Fallback Chain

Vision scraping is the last resort in the fallback chain:

1. AI Scraper (primary)
2. Scrapy Spider (secondary)
3. Regex Scraper (tertiary)
4. Vision Scraper (quaternary - last resort)

## Template Versioning

### Version Management

Templates are versioned to support evolution and rollback:

```python
class TemplateVersionManager:
    def create_version(self, template: Template) -> TemplateVersion:
        # Increment version
        version = self._get_next_version(template.domain, template.content_type)
        
        # Store version
        template_version = TemplateVersion(
            template_id=template.template_id,
            domain=template.domain,
            content_type=template.content_type,
            version=version,
            template_json=template.json(),
            created_at=datetime.utcnow(),
            confidence=template.confidence
        )
        
        self._store(template_version)
        return template_version
    
    def rollback(self, template_id: str, target_version: int) -> Template:
        # Retrieve specific version
        template_version = self._get_version(template_id, target_version)
        
        # Restore
        return Template.parse_obj(template_version.template_json)
    
    def get_latest_version(self, template_id: str) -> Template:
        # Retrieve latest version
        template_version = self._get_latest_version(template_id)
        
        return Template.parse_obj(template_version.template_json)
```

### Version Storage

Template versions are stored in PostgreSQL:

```sql
CREATE TABLE template_versions (
    id BIGSERIAL PRIMARY KEY,
    template_id TEXT NOT NULL,
    domain TEXT NOT NULL,
    content_type TEXT NOT NULL,
    version INTEGER NOT NULL,
    template_json JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    confidence FLOAT NOT NULL,
    UNIQUE (template_id, version)
);

CREATE INDEX idx_template_versions_template_id ON template_versions(template_id);
CREATE INDEX idx_template_versions_domain_content_type ON template_versions(domain, content_type);
```

## Storage Architecture

### PostgreSQL Schema

**Primary Tables**:
- `items` - Universal storage for all content types (JSONB)
- `tags` - Tag definitions
- `item_tags` - Many-to-many relationship
- `crawl_queue` - Task queue
- `templates` - Template storage

**Key Design Decisions**:
- Use JSONB for flexible content storage
- Partition by time for efficient deletion
- GIN indexes for JSONB queries
- Full-text search on title/description
- Trigram indexes for LIKE queries

### S3 Storage

**Binary Content**:
- `images/` - Image files
- `videos/` - Video files
- `raw_html/` - Raw HTML dumps

**Lifecycle**:
- Hot storage (0-30 days): S3 Standard
- Warm storage (30-90 days): S3 Infrequent Access
- Cold storage (90+ days): S3 Glacier

## Caching Strategy

### Template Cache

**Storage**: SQLite

**Key**: `(domain, content_type, template_hash)`

**TTL**: 30 days

**Invalidation**: On validation failure

### Result Cache

**Storage**: Redis (optional) or in-memory

**Key**: `(url, template_id)`

**TTL**: 1 hour

**Invalidation**: Manual or time-based

## Fallback Chain

### Chain Order

1. **AI Scraper** - Use AI-generated template
2. **Scrapy Spider** - Use hand-written spider (if available)
3. **Regex Scraper** - Generic regex extraction
4. **Vision Scraper** - Screenshot analysis (last resort)

### Fallback Triggers

- Template validation fails
- Extraction error occurs
- Success rate drops below threshold
- Circuit breaker activated

## Security Considerations

### Input Validation

- Validate all URLs
- Sanitize all selectors
- Never execute untrusted code
- Use prepared statements for SQL

### Output Sanitization

- Remove JavaScript from extracted content
- Sanitize HTML
- Validate file paths
- Check for XSS vectors

### Rate Limiting

- Per-domain rate limits
- Global rate limits
- Request shaping
- Exponential backoff

## Performance Considerations

### Concurrency

- Browser connection pooling
- Database connection pooling
- Async I/O throughout
- Configurable concurrency limits

### Optimization

- Template caching
- Result caching
- Batch operations
- Index optimization

### Monitoring

- Structured logging
- Metrics collection
- Health checks
- Alerting

## Extensibility

### Adding New Content Types

To add support for a new content type:

1. Define content type string (e.g., 'podcast')
2. Create example template
3. Add validation rules
4. Update documentation

**No engine modification required!**

### Adding New Fetchers

To add a new fetcher:

1. Implement `Fetcher` interface
2. Add to fetcher pool
3. Update configuration
4. Add tests

### Adding New LLM Backends

To add a new LLM backend:

1. Implement `LLMClient` interface
2. Add to LLM client pool
3. Update configuration
4. Add tests

## Known Limitations

1. **LLM Reliability**: Template generation depends on LLM quality
2. **Cost**: OpenAI API costs for template generation
3. **Latency**: Template generation can be slow (1-2s)
4. **Complex JS**: Some sites may require custom JS steps
5. **Legal**: Must respect robots.txt and ToS

## Future Enhancements

1. **Multi-modal LLMs**: Use vision models for better template generation
2. **Distributed Scraping**: Scale horizontally with multiple workers
3. **Real-time Updates**: Webhook notifications for new content
4. **ML Classification**: Auto-detect content types
5. **Community Templates**: Public template marketplace

## Notes

This architecture is designed to be:
- **Universal**: Handle any content type without engine modification
- **Deterministic**: No LLM calls during extraction
- **Extensible**: Easy to add new features
- **Performant**: Optimized for high-volume scraping
- **Maintainable**: Clear separation of concerns

**Status**: Complete - All high-priority issues from architecture review have been addressed:
- ✅ Content Type Detection layer added
- ✅ LLM integration detailed with schema-guided extraction
- ✅ Schema.org integration added
- ✅ Vision scraping integrated into fallback chain
- ✅ Template versioning strategy defined
