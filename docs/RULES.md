---
title: Kaisper Coding Rules
version: 0.1.0
status: active
last_updated: 2026-04-26
---

# Kaisper Coding Rules

## Directory Structure

```
kaisper/
├── src/kaisper/
│   ├── __init__.py
│   ├── cli.py              # Typer CLI app (entry point)
│   ├── config.py           # Pydantic settings
│   ├── fetcher/            # Browser abstraction layer
│   │   ├── __init__.py
│   │   ├── base.py         # Abstract base class
│   │   ├── obscura.py      # Obscura implementation
│   │   ├── playwright.py   # Playwright fallback
│   │   └── pool.py         # Browser connection pool
│   ├── template/           # Template management
│   │   ├── __init__.py
│   │   ├── generator.py    # LLM template generation
│   │   ├── schema.py       # Pydantic models
│   │   ├── store.py        # SQLite storage
│   │   └── validator.py    # Template validation
│   ├── engine/             # Execution engine
│   │   ├── __init__.py
│   │   ├── extractor.py    # Selector execution
│   │   ├── js_runtime.py   # JS step execution
│   │   └── validator.py    # Result validation
│   ├── storage/            # Data storage layer
│   │   ├── __init__.py
│   │   ├── postgres.py     # PostgreSQL client
│   │   ├── s3.py           # S3-compatible storage
│   │   └── models.py       # SQLAlchemy models
│   ├── cache/              # Caching layer
│   │   ├── __init__.py
│   │   ├── template.py     # Template cache
│   │   └── result.py       # Result cache
│   └── utils/
│       ├── __init__.py
│       ├── logging.py      # Structured logging
│       ├── retry.py        # Retry policies
│       └── errors.py       # Custom exceptions
├── tests/                  # Test suite
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── scripts/                # Utility scripts
├── docs/                   # Documentation
├── templates/              # Example/custom templates
├── pyproject.toml
└── README.md
```

## Code Style

### Python Version
- Target Python 3.10+
- Use type hints for all public functions
- Use `asyncio` for I/O operations

### Formatting
- Use `black` for code formatting (line length: 100)
- Use `ruff` for linting
- Use `mypy` for type checking (strict mode)

### Naming Conventions
- Classes: `PascalCase`
- Functions/variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private members: `_leading_underscore`
- Async functions: `async def` prefix

### Import Order
1. Standard library
2. Third-party imports
3. Local imports
4. Separate each group with blank line

## Async Patterns

### Always Use Async
```python
# Good
async def fetch_page(url: str) -> FetchResult:
    browser = await pool.acquire()
    try:
        return await browser.fetch(url)
    finally:
        await pool.release(browser)

# Bad
def fetch_page(url: str) -> FetchResult:
    browser = pool.acquire()  # Blocking!
    return browser.fetch(url)
```

### Use Context Managers
```python
# Good
async with browser_pool.acquire() as browser:
    result = await browser.fetch(url)

# Bad
browser = await browser_pool.acquire()
result = await browser.fetch(url)
await browser_pool.release(browser)
```

### Handle Timeouts
```python
try:
    result = await asyncio.wait_for(fetch_page(url), timeout=30.0)
except asyncio.TimeoutError:
    raise FetchTimeoutError(f"Timeout fetching {url}")
```

## Error Handling

### Custom Exceptions
```python
class KaisperError(Exception):
    """Base exception for Kaisper."""
    pass

class TemplateGenerationError(KaisperError):
    """Failed to generate template."""
    pass

class ExtractionError(KaisperError):
    """Failed to extract data."""
    pass
```

### Always Log Errors
```python
import structlog

logger = structlog.get_logger()

try:
    result = await extract(template, url)
except ExtractionError as e:
    logger.error(
        "extraction_failed",
        url=url,
        template_id=template.template_id,
        error=str(e),
    )
    raise
```

### Never Swallow Exceptions
```python
# Bad
try:
    result = await extract(template, url)
except Exception:
    pass  # Silent failure!

# Good
try:
    result = await extract(template, url)
except ExtractionError as e:
    logger.error("extraction_failed", error=str(e))
    raise
```

## Database Patterns

### Use Connection Pooling
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
)

async with AsyncSession(engine) as session:
    result = await session.execute(query)
```

### Always Use Transactions
```python
async with session.begin():
    item = Item(url=url, content_type=type)
    session.add(item)
    # Automatically commits or rolls back
```

### Use JSONB for Flexible Data
```python
# Good
item = Item(
    url=url,
    content_type="product",
    content={
        "price": 99.99,
        "currency": "USD",
        "availability": "in_stock",
    },
)

# Bad
item = Item(
    url=url,
    content_type="product",
    price=99.99,  # Too rigid!
    currency="USD",
    availability="in_stock",
)
```

## Template Patterns

### Use Pydantic for Validation
```python
from pydantic import BaseModel, Field, validator

class Template(BaseModel):
    template_id: str
    domain: str
    extraction: Dict[str, ExtractionRule]
    
    @validator('domain')
    def domain_must_be_valid(cls, v):
        if not v or '.' not in v:
            raise ValueError('Invalid domain')
        return v
```

### Never Trust User Input
```python
# Good
template = Template.parse_raw(user_input)  # Validates!

# Bad
template = json.loads(user_input)  # No validation!
```

### Sanitize Selectors
```python
def sanitize_selector(selector: str) -> str:
    """Remove dangerous patterns from selectors."""
    # Remove JavaScript
    selector = re.sub(r'<script.*?>.*?</script>', '', selector, flags=re.DOTALL)
    # Remove event handlers
    selector = re.sub(r'on\w+\s*=', '', selector)
    return selector
```

## Logging

### Use Structured Logging
```python
import structlog

logger = structlog.get_logger()

logger.info(
    "template_generated",
    domain=domain,
    template_id=template_id,
    confidence=confidence,
    duration_ms=duration_ms,
)
```

### Log at Appropriate Levels
- `DEBUG`: Detailed diagnostic information
- `INFO`: General informational messages
- `WARNING`: Unexpected but recoverable issues
- `ERROR`: Errors that prevent operation
- `CRITICAL`: System-level failures

### Never Log Sensitive Data
```python
# Bad
logger.info("user_login", password="secret123")

# Good
logger.info("user_login", user_id=user.id)
```

## Testing

### Use pytest-asyncio
```python
import pytest

@pytest.mark.asyncio
async def test_template_generation():
    template = await generate_template(url)
    assert template.domain == "example.com"
```

### Mock External Dependencies
```python
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_fetch_with_mock():
    mock_browser = AsyncMock()
    mock_browser.fetch.return_value = FetchResult(html="<html></html>")
    
    result = await fetch_page("https://example.com", browser=mock_browser)
    assert result.html == "<html></html>"
```

### Test Error Cases
```python
@pytest.mark.asyncio
async def test_extraction_failure():
    with pytest.raises(ExtractionError):
        await extract(invalid_template, url)
```

## Security

### Never Execute Untrusted Code
```python
# Bad
eval(user_input)  # DANGEROUS!

# Good
# Use sandboxed execution or whitelist allowed operations
```

### Validate All Inputs
```python
def validate_url(url: str) -> str:
    """Validate and normalize URL."""
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError(f"Invalid URL: {url}")
    return url
```

### Use Prepared Statements
```python
# Good
await session.execute(
    "SELECT * FROM items WHERE url = :url",
    {"url": url}
)

# Bad
await session.execute(
    f"SELECT * FROM items WHERE url = '{url}'"  # SQL injection risk!
)
```

## Performance

### Use Connection Pooling
```python
# Browser pool
browser_pool = BrowserPool(size=10)

# Database pool
engine = create_async_engine(DATABASE_URL, pool_size=10)
```

### Cache Aggressively
```python
@lru_cache(maxsize=1000)
def parse_selector(selector: str) -> Selector:
    """Parse and cache selectors."""
    return Selector.parse(selector)
```

### Batch Operations
```python
# Good
await session.execute(
    INSERT(Item).values([
        {"url": url1, "content": content1},
        {"url": url2, "content": content2},
    ])
)

# Bad
for url, content in items:
    await session.execute(INSERT(Item).values({"url": url, "content": content}))
```

## Documentation

### Docstrings for All Public Functions
```python
async def extract(template: Template, url: str) -> ExtractionResult:
    """
    Extract data from a URL using a template.
    
    Args:
        template: The extraction template to use.
        url: The URL to extract data from.
        
    Returns:
        ExtractionResult containing the extracted data.
        
    Raises:
        ExtractionError: If extraction fails.
        FetchTimeoutError: If fetching times out.
    """
    ...
```

### Type Hints for All Functions
```python
def process_result(result: ExtractionResult) -> Dict[str, Any]:
    """Process extraction result."""
    ...
```

### Examples in Docstrings
```python
def generate_template(url: str) -> Template:
    """
    Generate a template for a URL.
    
    Example:
        >>> template = generate_template("https://example.com/video/123")
        >>> template.domain
        'example.com'
    """
    ...
```

## Anti-Hallucination Rules

When using subagents, always include:
```
YOU MUST FOLLOW THE ANTI-HALLUCINATION RULES DESCRIBED IN THE SUBAGENT-[TYPE] SKILL.
```

Use subagent-validator to review critical outputs before accepting them.

## Notes

- These rules are mandatory for all code contributions
- Update this file as new patterns emerge
- Use pre-commit hooks to enforce formatting and linting
- All code must pass type checking before merging
