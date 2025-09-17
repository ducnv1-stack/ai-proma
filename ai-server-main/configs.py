from pydantic import Field
from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables from config.env file
load_dotenv("config.env")


class DatabaseSettings(BaseSettings):
    """Database configuration settings"""
    
    # Database URL (takes precedence over individual settings)
    database_url: Optional[str] = Field(
        default=os.getenv("DATABASE_URL"),
        env="DATABASE_URL",
        description="Complete database URL connection string"
    )
    
    # Individual database components
    postgres_user: Optional[str] = Field(
        default=None,
        env="POSTGRES_USER",
        description="PostgreSQL username"
    )
    
    postgres_password: Optional[str] = Field(
        default=None,
        env="POSTGRES_PASSWORD",
        description="PostgreSQL password"
    )
    
    postgres_host: str = Field(
        default="localhost",
        env="POSTGRES_HOST",
        description="PostgreSQL host address"
    )
    
    postgres_port: int = Field(
        default=5432,
        env="POSTGRES_PORT",
        description="PostgreSQL port number"
    )
    
    postgres_dbname: str = Field(
        default="faramex",
        env="POSTGRES_DBNAME",
        description="PostgreSQL database name"
    )
    
    class Config:
        env_file_encoding = "utf-8"
        extra = "forbid"


class AISettings(BaseSettings):
    """AI model and API configuration settings"""
    
    # Marketing agent model
    mkt_agent_model: str = Field(
        default=os.getenv("MKT_AGENT_MODEL"),
        env="MKT_AGENT_MODEL",
        description="AI model for marketing agent"
    )
    
    # OpenRouter API configuration
    openrouter_api_key: str = Field(
        default=os.getenv("OPENROUTER_API_KEY"),
        env="OPENROUTER_API_KEY",
        description="OpenRouter API key"
    )
    
    openrouter_base_url: str = Field(
        default=os.getenv("OPENROUTER_BASE_URL"),
        env="OPENROUTER_BASE_URL",
        description="OpenRouter API base URL"
    )
    
    # AI generation settings
    temperature: float = Field(
        default=0.1,
        env="AI_TEMPERATURE",
        description="AI model temperature (0.0 to 1.0)"
    )
    
    max_output_tokens: int = Field(
        default=64000,
        env="AI_MAX_OUTPUT_TOKENS",
        description="Maximum AI output tokens"
    )
    
    class Config:
        env_file_encoding = "utf-8"
        extra = "forbid"


class SecuritySettings(BaseSettings):
    """Security and authentication configuration settings"""
    
    # Password hashing
    bcrypt_rounds: int = Field(
        default=12,
        env="BCRYPT_ROUNDS",
        description="BCrypt password hashing rounds"
    )
    
    # API key settings
    api_key_length: int = Field(
        default=64,
        env="API_KEY_LENGTH",
        description="Length of generated API keys"
    )
    
    # JWT settings (if needed in the future)
    jwt_secret_key: Optional[str] = Field(
        default=None,
        env="JWT_SECRET_KEY",
        description="JWT secret key for authentication"
    )
    
    jwt_algorithm: str = Field(
        default="HS256",
        env="JWT_ALGORITHM",
        description="JWT algorithm"
    )
    
    jwt_access_token_expire_minutes: int = Field(
        default=30,
        env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES",
        description="JWT access token expiration time in minutes"
    )
    
    class Config:
        env_file_encoding = "utf-8"
        extra = "forbid"


class ServerSettings(BaseSettings):
    """Server and application configuration settings"""
    
    # Application info
    app_name: str = Field(
        default="FARAMEX",
        env="APP_NAME",
        description="Application name"
    )
    
    app_description: str = Field(
        default="FARAMEX MULTI AGENT SYSTEM",
        env="APP_DESCRIPTION",
        description="Application description"
    )
    
    app_version: str = Field(
        default="0.0.1-dev",
        env="APP_VERSION",
        description="Application version"
    )
    
    # Server settings
    host: str = Field(
        default="0.0.0.0",
        env="HOST",
        description="Server host address"
    )
    
    port: int = Field(
        default=8000,
        env="PORT",
        description="Server port number"
    )
    
    reload: bool = Field(
        default=True,
        env="RELOAD",
        description="Enable auto-reload for development"
    )
    
    workers: int = Field(
        default=1,
        env="WORKERS",
        description="Number of worker processes"
    )
    
    timeout_keep_alive: int = Field(
        default=300,
        env="TIMEOUT_KEEP_ALIVE",
        description="Keep alive timeout in seconds"
    )
    
    # CORS settings
    cors_origins: list[str] = Field(
        default=["*"],
        env="CORS_ORIGINS",
        description="CORS allowed origins"
    )
    
    # API documentation
    docs_url: str = Field(
        default="/docs",
        env="DOCS_URL",
        description="Swagger documentation URL"
    )
    
    redoc_url: str = Field(
        default="/redoc",
        env="REDOC_URL",
        description="ReDoc documentation URL"
    )
    
    class Config:
        env_file_encoding = "utf-8"
        extra = "forbid"


class LoggingSettings(BaseSettings):
    """Logging configuration settings"""
    
    log_level: str = Field(
        default="INFO",
        env="LOG_LEVEL",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT",
        description="Log message format"
    )
    
    # File logging
    log_file: Optional[str] = Field(
        default=None,
        env="LOG_FILE",
        description="Log file path (if None, logs to console only)"
    )
    
    max_log_file_size: int = Field(
        default=10 * 1024 * 1024,  # 10MB
        env="MAX_LOG_FILE_SIZE",
        description="Maximum log file size in bytes"
    )
    
    backup_log_count: int = Field(
        default=5,
        env="BACKUP_LOG_COUNT",
        description="Number of backup log files to keep"
    )
    
    class Config:
        env_file_encoding = "utf-8"
        extra = "forbid"


class Settings(BaseSettings):
    """Main application settings that combines all configuration sections"""
    
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    ai: AISettings = Field(default_factory=AISettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    server: ServerSettings = Field(default_factory=ServerSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    
    class Config:
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "forbid"


# Global settings instance
settings = Settings()

def get_database_url() -> str:
    """
    Get database URL with proper handling of different authentication scenarios.
    This function replicates the logic from postgres.py but uses the centralized configuration.
    """
    from urllib.parse import quote_plus
    
    # Check if DATABASE_URL is set directly
    if settings.database.database_url:
        return settings.database.database_url
    
    # Get individual components from settings
    postgres_user = settings.database.postgres_user
    postgres_password = settings.database.postgres_password
    postgres_host = settings.database.postgres_host
    postgres_port = settings.database.postgres_port
    postgres_dbname = settings.database.postgres_dbname
    
    # Build URL based on whether auth is needed
    if postgres_user and postgres_password:
        # With authentication
        encoded_password = quote_plus(postgres_password)
        url = f"postgresql://{postgres_user}:{encoded_password}@{postgres_host}:{postgres_port}/{postgres_dbname}"
    elif postgres_user:
        # With username only
        url = f"postgresql://{postgres_user}@{postgres_host}:{postgres_port}/{postgres_dbname}"
    else:
        # No authentication (peer/trust authentication)
        url = f"postgresql://{postgres_host}:{postgres_port}/{postgres_dbname}"
    
    print(f"✅ Using constructed database URL: {url}")
    return url


def get_settings() -> Settings:
    """Get the global settings instance"""
    return settings


# Convenience functions for accessing specific settings sections
def get_database_settings() -> DatabaseSettings:
    """Get database settings"""
    return settings.database


def get_ai_settings() -> AISettings:
    """Get AI settings"""
    return settings.ai


def get_security_settings() -> SecuritySettings:
    """Get security settings"""
    return settings.security


def get_server_settings() -> ServerSettings:
    """Get server settings"""
    return settings.server


def get_logging_settings() -> LoggingSettings:
    """Get logging settings"""
    return settings.logging
