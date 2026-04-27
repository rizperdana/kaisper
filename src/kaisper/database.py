"""Database connection and management for Kaisper."""

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

import asyncpg
from loguru import logger

from kaisper.config import settings


class Database:
    """Database connection manager."""
    
    def __init__(self):
        self._pool: Optional[asyncpg.Pool] = None
    
    async def connect(self) -> None:
        """Create connection pool."""
        if self._pool is not None:
            return
        
        logger.info(f"Connecting to PostgreSQL at {settings.database.host}:{settings.database.port}")
        
        self._pool = await asyncpg.create_pool(
            host=settings.database.host,
            port=settings.database.port,
            database=settings.database.database,
            user=settings.database.user,
            password=settings.database.password,
            min_size=1,
            max_size=settings.database.pool_size,
        )
        
        logger.info("Database connection pool created")
    
    async def disconnect(self) -> None:
        """Close connection pool."""
        if self._pool is not None:
            await self._pool.close()
            self._pool = None
            logger.info("Database connection pool closed")
    
    @asynccontextmanager
    async def connection(self) -> AsyncGenerator[asyncpg.Connection, None]:
        """Get a connection from the pool."""
        if self._pool is None:
            await self.connect()
        
        async with self._pool.acquire() as conn:
            yield conn
    
    async def execute(self, query: str, *args) -> str:
        """Execute a query."""
        async with self.connection() as conn:
            return await conn.execute(query, *args)
    
    async def fetch(self, query: str, *args) -> list:
        """Fetch rows from a query."""
        async with self.connection() as conn:
            return await conn.fetch(query, *args)
    
    async def fetchrow(self, query: str, *args) -> Optional[asyncpg.Record]:
        """Fetch a single row from a query."""
        async with self.connection() as conn:
            return await conn.fetchrow(query, *args)
    
    async def fetchval(self, query: str, *args) -> Any:
        """Fetch a single value from a query."""
        async with self.connection() as conn:
            return await conn.fetchval(query, *args)
    
    async def initialize_schema(self) -> None:
        """Initialize database schema."""
        logger.info("Initializing database schema")
        
        # Create items table
        await self.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id BIGSERIAL PRIMARY KEY,
                url TEXT NOT NULL,
                content_type VARCHAR(50) NOT NULL,
                source_domain TEXT NOT NULL,
                title TEXT,
                description TEXT,
                scraped_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                status VARCHAR(20) NOT NULL DEFAULT 'active',
                content JSONB NOT NULL,
                raw_content TEXT,
                binary_storage_path TEXT,
                binary_size BIGINT,
                binary_mime_type TEXT,
                schema_org_type TEXT,
                schema_org_data JSONB,
                open_graph_data JSONB,
                checksum TEXT,
                language TEXT,
                author TEXT,
                tags TEXT[],
                detected_content_type TEXT,
                detection_confidence FLOAT,
                detection_method TEXT,
                template_id TEXT,
                template_version INTEGER,
                template_confidence FLOAT,
                validation_score FLOAT,
                validation_checks JSONB,
                CONSTRAINT unique_url UNIQUE (url)
            ) PARTITION BY RANGE (scraped_at);
        """)
        
        # Create template_versions table
        await self.execute("""
            CREATE TABLE IF NOT EXISTS template_versions (
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
        """)
        
        # Create indexes
        await self.execute("""
            CREATE INDEX IF NOT EXISTS idx_items_content_gin ON items USING GIN (content);
        """)
        
        await self.execute("""
            CREATE INDEX IF NOT EXISTS idx_items_title_fts ON items 
                USING GIN (to_tsvector('english', title || ' ' || COALESCE(description, '')));
        """)
        
        await self.execute("""
            CREATE INDEX IF NOT EXISTS idx_items_type_status_scraped ON items(content_type, status, scraped_at);
        """)
        
        await self.execute("""
            CREATE INDEX IF NOT EXISTS idx_template_versions_template_id ON template_versions(template_id);
        """)
        
        await self.execute("""
            CREATE INDEX IF NOT EXISTS idx_template_versions_domain_content_type ON template_versions(domain, content_type);
        """)
        
        logger.info("Database schema initialized")


# Global database instance
db = Database()
