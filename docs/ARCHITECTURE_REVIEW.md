---
title: Kaisper Architecture Review
version: 0.1.0
status: complete
last_updated: 2026-04-26
---

# Kaisper Architecture Review

## Executive Summary

The current architecture is **solid but incomplete**. It correctly identifies the core components and data flow, but lacks critical details for universal scraping, content type detection, and LLM integration patterns identified in research.

**Overall Assessment**: Good foundation, needs refinement in 5 key areas.

---

## Critical Findings

### 1. Missing Content Type Detection Layer

**Issue**: Architecture lacks explicit content type detection component, which is critical for universal scraping.

**Impact**: HIGH - Without content type detection, the system cannot automatically determine which template to use or how to normalize data.

**Research Finding**: Automatic schema detection requires combining multiple signals (Schema.org, Open Graph, ML classifier) to reliably identify page types and infer data models.

**Recommendation**: Add dedicated `ContentDetector` component in Template Generation Layer:

```
┌─────────────────────────────────────────────────────────────────┐
│                    Template Generation Layer                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Fetcher     │  │  Content     │  │  LLM Client  │         │
│  │  (Obscura)   │  │  Detector    │  │  (OpenAI)    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                       ↓                                           │
│              ┌──────────────┐                                  │
│              │  Template    │                                  │
│              │  Generator   │                                  │
│              └──────────────┘                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Implementation**:
```python
class ContentDetector:
    def detect_content_type(self, url: str, html: str) -> str:
        # 1. Check for Schema.org
        schema_type = self._extract_schema_org_type(html)
        if schema_type:
            return self._map_schema_to_content_type(schema_type)
        
        # 2. Check for Open Graph
        og_type = self._extract_open_graph_type(html)
        if og_type:
            return self._map_og_to_content_type(og_type)
        
        # 3. Use ML classifier
        features = self._extract_features(url, html)
        predicted_type = self._classifier.predict(features)
        
        return predicted_type
```

### 2. LLM Integration Not Detailed

**Issue**: Architecture mentions LLM Client but doesn't specify schema-guided extraction, few-shot learning, or validation patterns.

**Impact**: HIGH - Without proper LLM integration patterns, template generation will be unreliable and inconsistent.

**Research Finding**: Schema-guided extraction with few-shot examples stabilizes extraction for complex schemas and eliminates brittle text parsing.

**Recommendation**: Expand LLM Client component with:

```python
class LLMClient:
    def generate_template(
        self,
        html: str,
        network_requests: List[Request],
        content_type: str,
        few_shot_examples: List[Example]
    ) -> Template:
        # 1. Build prompt with few-shot examples
        prompt = self._build_prompt(
            html=html,
            network_requests=network_requests,
            content_type=content_type,
            examples=few_shot_examples
        )
        
        # 2. Call LLM with schema validation
        response = await self._llm.generate(
            prompt=prompt,
            response_format=TemplateSchema,
            temperature=0.1  # Low temperature for consistency
        )
        
        # 3. Validate against schema
        template = Template.parse_obj(response)
        self._validate_template(template)
        
        return template
```

### 3. Missing Schema.org Integration

**Issue**: Universal data model doesn't explicitly include Schema.org mapping, which is critical for interoperability.

**Impact**: MEDIUM - Without Schema.org integration, the system cannot leverage existing structured data or normalize to industry standards.

**Research Finding**: Schema.org is the de facto standard with 800+ types. JSON-LD is the recommended format for embedding structured data.

**Recommendation**: Add Schema.org parser and mapper:

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

### 4. Vision Scraping Not Integrated

**Issue**: Fallback chain mentions vision scraper but architecture doesn't show how it integrates with the main flow.

**Impact**: MEDIUM - Without proper integration, vision scraping won't be used effectively as a fallback.

**Research Finding**: Vision models can extract data from screenshots when HTML parsing fails, especially for dynamic or obfuscated content.

**Recommendation**: Add Vision Scraper component with clear integration point:

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

### 5. Missing Template Versioning Strategy

**Issue**: Architecture mentions template versioning but doesn't specify how to handle template evolution and rollback.

**Impact**: MEDIUM - Without proper versioning, template updates could break existing scrapers.

**Recommendation**: Add template versioning strategy:

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
```

---

## Architectural Improvements

### 1. Enhanced Data Flow

**Current**: Template generation → Extraction → Storage

**Improved**: Content detection → Template generation → Validation → Extraction → Storage

```
1. User provides URL
   ↓
2. Fetcher fetches page (Obscura/Playwright)
   ↓
3. ContentDetector identifies content type
   ↓
4. Check template cache
   ↓
5a. Template found → Use cached template
5b. Template not found → Generate new template
   ↓
6. LLM generates template (with few-shot examples)
   ↓
7. TemplateValidator validates template
   ↓
8. TemplateStore saves template
   ↓
9. Extractor applies template selectors
   ↓
10. Post-process extracted data
   ↓
11. ResultValidator validates results
   ↓
12a. Validation passes → Store results
12b. Validation fails → Try fallback chain
   ↓
13. Return results to user
```

### 2. Enhanced Component Breakdown

**Add to Template Generation Layer**:
- `ContentDetector` - Detect content type from Schema.org, Open Graph, ML
- `SchemaOrgParser` - Parse Schema.org JSON-LD and Microdata
- `SchemaOrgMapper` - Map Schema.org to universal data model
- `FewShotExampleStore` - Store and retrieve few-shot examples

**Add to Execution Engine Layer**:
- `VisionScraper` - Screenshot-based extraction
- `SchemaNormalizer` - Normalize extracted data to Schema.org
- `PostProcessor` - Apply content-type-specific post-processing

**Add to Storage Layer**:
- `TemplateVersionManager` - Manage template versions
- `SchemaOrgCache` - Cache Schema.org data
- `ContentClassifier` - ML model for content type detection

### 3. Enhanced Universal Data Model

**Add to ExtractionResult**:
```python
class ExtractionResult(BaseModel):
    # ... existing fields ...
    
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
```

### 4. Enhanced Template Schema

**Add to Template**:
```python
class Template(BaseModel):
    # ... existing fields ...
    
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

---

## Scalability Concerns

### 1. Template Cache Size

**Issue**: SQLite template cache may not scale to millions of templates.

**Recommendation**: Consider Redis or PostgreSQL for template cache at scale.

### 2. LLM API Rate Limits

**Issue**: OpenAI API has rate limits that could bottleneck template generation.

**Recommendation**: Implement request queuing, rate limiting, and fallback to Ollama.

### 3. Browser Pool Size

**Issue**: Browser pool size not specified; could be bottleneck for concurrent scraping.

**Recommendation**: Make pool size configurable and implement connection pooling.

---

## Security Concerns

### 1. Template Injection

**Issue**: LLM-generated templates could contain malicious selectors or JS steps.

**Recommendation**: Implement template sanitization and validation before execution.

### 2. XSS in Extracted Data

**Issue**: Extracted HTML could contain malicious JavaScript.

**Recommendation**: Sanitize all HTML output and validate file paths.

### 3. Rate Limiting Evasion

**Issue**: Aggressive scraping could trigger anti-bot measures.

**Recommendation**: Implement per-domain rate limiting and request shaping.

---

## Performance Considerations

### 1. Template Generation Latency

**Issue**: LLM calls add 1-2s latency per template generation.

**Recommendation**: Cache aggressively and use batch generation for multiple URLs.

### 2. Extraction Speed

**Issue**: Selector execution could be slow for complex templates.

**Recommendation**: Implement parallel selector execution and caching.

### 3. Database Query Performance

**Issue**: JSONB queries could be slow without proper indexing.

**Recommendation**: Use GIN indexes and optimize query patterns.

---

## Missing Components

### 1. Monitoring & Observability

**Missing**: Metrics collection, health checks, alerting

**Recommendation**: Add Prometheus metrics endpoint and structured logging.

### 2. Error Handling & Retry Logic

**Missing**: Comprehensive error handling and retry strategies

**Recommendation**: Implement exponential backoff and circuit breakers.

### 3. Configuration Management

**Missing**: Dynamic configuration and hot-reloading

**Recommendation**: Implement Pydantic Settings with hot-reload support.

### 4. Testing Strategy

**Missing**: Test suite design and coverage targets

**Recommendation**: Define test strategy with unit, integration, and E2E tests.

---

## Recommendations Summary

### High Priority (Must Fix)

1. **Add Content Type Detection** - Critical for universal scraping
2. **Detail LLM Integration** - Schema-guided extraction with few-shot learning
3. **Add Schema.org Integration** - For interoperability and normalization
4. **Integrate Vision Scraping** - As fallback in extraction flow
5. **Define Template Versioning** - For template evolution and rollback

### Medium Priority (Should Fix)

6. **Enhance Data Flow** - Add content detection and validation steps
7. **Add Missing Components** - Monitoring, error handling, configuration
8. **Address Scalability** - Template cache, rate limits, browser pooling
9. **Improve Security** - Template sanitization, XSS prevention, rate limiting
10. **Optimize Performance** - Caching, parallel execution, query optimization

### Low Priority (Nice to Have)

11. **Add Distributed Scraping** - For horizontal scaling
12. **Implement Real-time Updates** - Webhook notifications
13. **Build Community Templates** - Public template marketplace
14. **Add ML Classification** - Auto-detect content types
15. **Create Template Editor** - Visual template editing tool

---

## Conclusion

The current architecture is **good but incomplete**. It correctly identifies the core components and data flow, but lacks critical details for universal scraping, content type detection, and LLM integration patterns.

**Key Gaps**:
- Missing content type detection layer
- LLM integration not detailed
- Schema.org integration missing
- Vision scraping not integrated
- Template versioning not specified

**Next Steps**:
1. Add content type detection component
2. Detail LLM integration with schema-guided extraction
3. Add Schema.org parser and mapper
4. Integrate vision scraping into fallback chain
5. Define template versioning strategy

**Overall Assessment**: 7/10 - Good foundation, needs refinement in 5 key areas before implementation.

**Status**: Ready for implementation after addressing high-priority recommendations.
