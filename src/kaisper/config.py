"""Configuration management for Kaisper."""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings as Settings


class DatabaseSettings(Settings):
    """Database configuration."""
    
    host: str = Field(default="localhost", description="PostgreSQL host")
    port: int = Field(default=5432, description="PostgreSQL port")
    database: str = Field(default="kaisper", description="Database name")
    user: str = Field(default="postgres", description="Database user")
    password: str = Field(default="", description="Database password")
    pool_size: int = Field(default=10, description="Connection pool size")
    
    class Config:
        env_prefix = "KAISPER_DB_"


class LLMSettings(Settings):
    """LLM API configuration."""

    provider: str = Field(default="cliproxyapi", description="LLM provider (openai, ollama, cliproxyapi)")
    api_key: str = Field(default="sk-dIMp6qoD0oWyMvswe", description="API key")
    base_url: str = Field(default="http://localhost:83117/v1", description="API base URL")
    model: str = Field(default="kilo-auto/free", description="Model name")
    temperature: float = Field(default=0.1, description="Temperature for generation")
    max_tokens: int = Field(default=4000, description="Max tokens per request")
    timeout: int = Field(default=120, description="Request timeout in seconds")

    class Config:
        env_prefix = "KAISPER_LLM_"


class S3Settings(Settings):
    """S3 storage configuration."""
    
    endpoint_url: str = Field(default="", description="S3 endpoint URL")
    access_key: str = Field(default="", description="S3 access key")
    secret_key: str = Field(default="", description="S3 secret key")
    bucket: str = Field(default="kaisper", description="S3 bucket name")
    region: str = Field(default="us-east-1", description="S3 region")
    
    class Config:
        env_prefix = "KAISPER_S3_"


class FetcherSettings(Settings):
    """Fetcher configuration."""
    
    timeout: int = Field(default=30, description="Request timeout in seconds")
    max_retries: int = Field(default=3, description="Max retry attempts")
    user_agent: str = Field(
        default="Kaisper/0.1.0",
        description="User agent string"
    )
    headless: bool = Field(default=True, description="Run browser in headless mode")
    
    class Config:
        env_prefix = "KAISPER_FETCHER_"


class Settings(Settings):
    """Main application settings."""
    
    # Database
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    
    # LLM
    llm: LLMSettings = Field(default_factory=LLMSettings)
    
    # S3
    s3: S3Settings = Field(default_factory=S3Settings)
    
    # Fetcher
    fetcher: FetcherSettings = Field(default_factory=FetcherSettings)
    
    # General
    debug: bool = Field(default=False, description="Debug mode")
    log_level: str = Field(default="INFO", description="Log level")
    
    class Config:
        env_prefix = "KAISPER_"


# Global settings instance
settings = Settings()
