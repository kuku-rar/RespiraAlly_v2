"""
Application Configuration
Using Pydantic Settings for environment variable management
"""
from typing import List

from pydantic import Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Application
    ENVIRONMENT: str = Field(default="development", description="Application environment")
    DEBUG: bool = Field(default=True, description="Debug mode")
    APP_NAME: str = Field(default="RespiraAlly V2.0", description="Application name")

    # Database (PostgreSQL + pgvector)
    DATABASE_URL: str = Field(
        ..., description="PostgreSQL connection string with asyncpg driver"
    )
    DB_POOL_SIZE: int = Field(default=10, description="Database connection pool size")
    DB_MAX_OVERFLOW: int = Field(default=20, description="Max overflow connections")
    DB_ECHO: bool = Field(default=False, description="SQLAlchemy echo SQL queries")

    # Redis
    REDIS_HOST: str = Field(default="localhost", description="Redis host")
    REDIS_PORT: int = Field(default=6379, description="Redis port")
    REDIS_DB: int = Field(default=0, description="Redis database number")
    REDIS_PASSWORD: str | None = Field(default=None, description="Redis password")

    # RabbitMQ (Phase 2)
    RABBITMQ_HOST: str = Field(default="localhost", description="RabbitMQ host")
    RABBITMQ_PORT: int = Field(default=5672, description="RabbitMQ port")
    RABBITMQ_USER: str = Field(default="guest", description="RabbitMQ username")
    RABBITMQ_PASSWORD: str = Field(default="guest", description="RabbitMQ password")

    # JWT Authentication
    JWT_SECRET_KEY: str = Field(..., description="JWT secret key for signing tokens")
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT signing algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=60, description="Access token expiration in minutes"
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=7, description="Refresh token expiration in days"
    )

    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        description="Allowed CORS origins",
    )

    # LINE Platform
    LINE_CHANNEL_ACCESS_TOKEN: str = Field(..., description="LINE Messaging API access token")
    LINE_CHANNEL_SECRET: str = Field(..., description="LINE Messaging API channel secret")
    LINE_LIFF_ID: str = Field(..., description="LINE LIFF app ID")

    # OpenAI (GPT-4 for RAG)
    OPENAI_API_KEY: str = Field(..., description="OpenAI API key for GPT-4")
    OPENAI_MODEL: str = Field(default="gpt-4-turbo-preview", description="OpenAI model name")
    OPENAI_TEMPERATURE: float = Field(default=0.7, description="OpenAI temperature")
    OPENAI_MAX_TOKENS: int = Field(default=1000, description="OpenAI max tokens")

    # LangChain (RAG Context)
    LANGCHAIN_TRACING_V2: bool = Field(default=False, description="Enable LangSmith tracing")
    LANGCHAIN_API_KEY: str | None = Field(default=None, description="LangSmith API key")

    # Vector Search (pgvector)
    VECTOR_DIMENSION: int = Field(default=1536, description="Embedding vector dimension")
    SIMILARITY_THRESHOLD: float = Field(
        default=0.7, description="Vector similarity threshold"
    )

    # Logging
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FORMAT: str = Field(default="json", description="Log format: json or console")


settings = Settings()
