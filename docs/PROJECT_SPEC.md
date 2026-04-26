---
title: Kaisper Project Specification
version: 0.1.0
status: complete
last_updated: 2026-04-26
---

# Kaisper — Universal AI‑Driven Scraper

## Project Overview

**Goal**: Build a standalone Python library that can automatically generate extraction templates for ANY type of content (video, images, products, articles, HTML, etc.) from any website, then deterministically scrape data using a single reusable engine.

**Philosophy**: Separate concerns — an LLM (or rule‑based fallback) reasons about page structure and emits a structured **template**; a lightweight **engine** reads that template and performs the actual extraction without further AI calls. Templates are cached per domain and reused.

**Scope**: Universal scraping system that can handle any content type. Can be used as a library or CLI. Independent of SuperCrapper but may later integrate with it.

## Non-Negotiable Constraints

1. **Universal Content Support**: Must handle ANY type of content (video, images, products, articles, HTML, etc.) without content-type-specific code in the core engine
2. **Deterministic Extraction**: No LLM calls during extraction — only during template generation
3. **Template Reusability**: Templates must be cached and reused across multiple URLs from the same domain
4. **CLI-First**: Primary interface must be a command-line tool
5. **Modular Architecture**: Core engine must be extensible without modification for new content types
6. **Unified Storage**: Must use a single database solution for all content types
7. **Anti-Hallucination**: All subagent work must follow strict anti-hallucination rules with source citations

## Tech Stack Requirements

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **Fetcher** | Obscura (primary) + Playwright (fallback) | Obscura is ultra‑lightweight, fast, stealthy; Playwright as fallback for complex JS |
| **LLM Backend** | OpenAI GPT‑4o (primary) + Ollama (fallback) | OpenAI reliable; Ollama free but slower/less accurate |
| **Template Store** | SQLite (local) + JSON export | Simple, no external deps; supports versioning |
| **Data Storage** | PostgreSQL with JSONB (primary) + MongoDB (optional) | PostgreSQL JSONB for structured queries; MongoDB for flexible schema |
| **Engine** | Parsel (XPath/CSS) + `re` | Battle‑tested, fast, familiar from Scrapy |
| **Async Runtime** | asyncio | Already used in Obscura/Playwright; integrates with Scrapy‑style pipelines |
| **Config** | Pydantic Settings | Validation, env‑var support |
| **CLI** | Typer | Modern, auto‑help, subcommands |
| **Logging** | structlog + JSON logs | Structured logs for monitoring |
| **Testing** | pytest + pytest‑asyncio | Industry standard |

## Success Metrics

- **Coverage**: ≥80 % of tested sites yield a working template on first try
- **Reliability**: ≥95 % extraction success rate on cached templates
- **Cost**: < $0.01 per generated template (OpenAI); < $0.001 per extraction (engine only)
- **Latency**: < 2 s per page for template generation; < 500 ms per extraction
- **Maintainability**: < 200 lines of core engine code; templates editable by hand
- **Universal Support**: Must support at least 5 different content types (video, image, product, article, HTML) without engine modification

## Open Questions

1. **LLM model choice**: GPT‑4o vs Claude Sonnet vs local Llama 3.2? Start with OpenAI, add Ollama fallback.
2. **Template complexity**: How to represent multi‑step JS interactions (login, click‑to‑play)? Use a small DSL (action/selector pairs).
3. **Sharing templates**: Public repository of community templates? Consider later.
4. **Legal guardrails**: Should the library refuse certain domains? Opt‑in blocklist.
5. **Universal data model**: How to represent different content types in a unified way? Research Schema.org, JSON-LD, Open Graph.

## Key Features

- **Universal Content Support**: Handle ANY type of content without content-type-specific code
- **AI-Powered Templates**: LLM generates extraction rules automatically
- **Deterministic Extraction**: No LLM calls during scraping
- **Template Caching**: Reuse templates across multiple URLs
- **CLI-First**: Primary interface is a command-line tool
- **Unified Storage**: Single database solution for all content types
- **Fallback Chain**: Multiple scraping strategies for reliability

## Research-Based Design Decisions

### Universal Data Model

**Approach**: Use Schema.org as the foundation, normalize to internal model

**Rationale**: Schema.org is the de facto standard with 800+ types (CreativeWork, Product, Organization, Person, Event, Review, etc.). JSON-LD is the recommended format for embedding structured data.

**Implementation**:
```python
class UniversalContent(BaseModel):
    # Common fields (all content types)
    url: str
    content_type: str  # 'video', 'image', 'product', 'article', 'raw_html', etc.
    source_domain: str
    title: Optional[str]
    description: Optional[str]
    scraped_at: datetime
    
    # Flexible content storage
    content: Dict[str, Any]  # Type-specific data
    
    # Schema.org mapping
    schema_org_type: Optional[str]
    schema_org_data: Optional[Dict[str, Any]]
    
    # Open Graph data
    open_graph_data: Optional[Dict[str, Any]]
    
    # Binary references
    binary_storage_path: Optional[str]
    binary_size: Optional[int]
    binary_mime_type: Optional[str]
```

**Sources**: Schema.org Documentation, JSON-LD Specification, Open Graph Protocol

### Database Solution

**Approach**: PostgreSQL with JSONB as primary storage, S3 for binary content

**Rationale**: PostgreSQL JSONB provides the best balance of flexibility and structure for hybrid workloads. Supports full SQL, ACID compliance, advanced GIN indexing, and mature ecosystem.

**Implementation**:
- Primary table: `items` with JSONB `content` field
- Partition by `scraped_at` for efficient deletion
- GIN indexes for JSONB containment queries
- Full-text search on title/description
- S3 for images, videos, raw HTML

**Sources**: MongoDB vs PostgreSQL JSONB (Medium, 2025), PostgreSQL JSONB Documentation

### LLM Extraction Patterns

**Approach**: Schema-guided extraction with few-shot learning

**Rationale**: Enforcing JSON schemas with few-shot examples stabilizes extraction for complex schemas and eliminates brittle text parsing.

**Implementation**:
- Use Pydantic models for schema validation
- Provide few-shot examples in prompts
- Implement retry logic for validation failures
- Use chain-of-thought for complex extractions
- Leverage vision models as fallback

**Sources**: Structured Outputs with LLMs (ByAI Team, 2025), Schema-Guided Reasoning (Slava Dubrov, 2025)

### Template System

**Approach**: Reusable, parameterized templates with fallbacks

**Rationale**: Apify actors and Scrapy pipelines demonstrate the value of reusable extraction components. Templates should be versioned and shareable.

**Implementation**:
- Content-type-agnostic template format
- Parameterized selectors and patterns
- Version tracking and validation
- Fallback selectors for robustness
- JSON export/import for sharing

**Sources**: Apify Actors Documentation, Scrapy Item Pipelines

### Content Type Detection

**Approach**: Multi-signal detection (Schema.org, Open Graph, ML classifier)

**Rationale**: Automatic schema detection requires combining multiple signals to reliably identify page types and infer data models.

**Implementation**:
1. Check for Schema.org JSON-LD first
2. Check for Open Graph meta tags
3. Use ML classifier as fallback
4. Handle dynamic content with JavaScript rendering
5. Adapt to layout changes continuously

**Sources**: Automatic Schema Detection (ScrapingAnt, 2025), Web Page Classification (Analytics Vidhya, 2023)

### Vision-Based Scraping

**Approach**: Multi-modal LLMs as fallback for visual content

**Rationale**: Vision models can extract data from screenshots when HTML parsing fails, especially for dynamic or obfuscated content.

**Implementation**:
- Capture full-page screenshot
- Encode to base64
- Send to GPT-4o or Llama Vision
- Parse structured response
- Use as last resort in fallback chain

**Sources**: Visual-based Web Scraping (Medium, 2025), Visual Web Scraping with GPT Vision (Scrapeless, 2025)

### Critical Success Factors

1. **Template Caching** - Reuse templates across domains to minimize LLM costs
2. **Deterministic Extraction** - No LLM calls during scraping for performance
3. **Fallback Chain** - Multiple strategies (AI → Scrapy → Regex → Vision) for reliability
4. **Content Type Detection** - Automatic schema inference for universal support
5. **Unified Storage** - Single database solution for all content types

### Known Unknowns

1. **LLM Cost Optimization** - How to minimize template generation costs at scale
2. **Template Versioning** - How to manage template evolution over time
3. **Community Templates** - How to build and maintain a template marketplace
4. **Legal Compliance** - How to ensure compliance with robots.txt and ToS
5. **Performance at Scale** - How to handle 1M+ items/day

### Implementation Phases

**Phase 1: Foundation (Week 1-2)**
- Set up PostgreSQL with JSONB support
- Implement universal data model
- Create template schema
- Set up S3-compatible storage
- Implement basic fetcher (Obscura)

**Phase 2: Template Generation (Week 2-3)**
- Implement LLM client (OpenAI + Ollama)
- Design prompt templates
- Implement few-shot learning
- Add schema validation
- Create template storage

**Phase 3: Execution Engine (Week 3-4)**
- Implement extractor (Parsel)
- Add post-processing pipeline
- Implement validation
- Create fallback chain
- Add caching layer

**Phase 4: Content Type Detection (Week 4)**
- Implement Schema.org parser
- Implement Open Graph parser
- Train ML classifier
- Add vision scraping fallback
- Integrate with template generation

**Phase 5: CLI & Integration (Week 5)**
- Implement CLI commands
- Add output formats
- Integrate with SuperCrapper
- Create documentation
- Write tests

**Sources**: All research findings documented in docs/RESEARCH.md

## Current Status

### Completed
- [x] Create modular documentation structure
- [x] Define project requirements and constraints
- [x] Research database solution (PostgreSQL + JSONB)
- [x] Design storage schema with partitioning
- [x] Define indexing strategy
- [x] Create data lifecycle management plan
- [x] Design universal data model
- [x] Design universal template schema
- [x] Define coding rules and conventions
- [x] Create AGENTS.md with project-specific directives
- [x] Complete universal research (all 5 areas + vision-based scraping)
- [x] Compile research findings into RESEARCH.md

### In Progress
- [ ] Validate project specification (subagent running)
- [ ] Finalize architecture design based on review findings
- [ ] Begin implementation (Phase 1: Foundation)

### Next Steps
1. Complete plan validation and finalize design
2. Address high-priority architecture review findings
3. Begin implementation (Phase 1: Foundation)
4. Follow phased approach outlined in PROJECT_SPEC.md

## Documentation Structure

```
kaisper/
├── docs/
│   ├── PROJECT_SPEC.md    # This file - Requirements, tech stack, constraints
│   ├── TASKS.md           # Active work items, progress tracking
│   ├── RULES.md           # Coding patterns, conventions
│   └── ARCHITECTURE.md    # Technical architecture, data flow
├── AGENTS.md             # Agent directives for Kaisper project
├── pyproject.toml        # Project configuration
└── README.md             # User-facing documentation
```

## References

- **RESEARCH.md** - Comprehensive research findings (universal data models, database solutions, LLM extraction patterns, template systems, content type detection, vision-based scraping)
- **ARCHITECTURE.md** - Technical architecture, data flow, and component breakdown
- **TASKS.md** - Active work items and progress tracking
- **RULES.md** - Coding patterns, directory structure, and conventions
- **AGENTS.md** - Agent directives for Kaisper project

## Notes

This project follows a modular documentation approach as recommended for long-term nanobot/openclaw projects. Each document serves a specific purpose and is machine-readable for easy parsing and retrieval.

For detailed information on any aspect of the project, refer to the appropriate document in the `docs/` folder.
