# Configuration file for Proma AI
import os

# OpenRouter API Configuration
# Read from environment to avoid committing secrets
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

# Default AI Model
DEFAULT_AI_MODEL = "openai/gpt-4o-mini" #"anthropic/claude-3.5-sonnet"  # or "openai/gpt-4o"

# JWT Configuration
# Use env var; provide a non-secret dev default only if absent
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "proma-dev-secret-change-me")
JWT_ALGORITHM = "HS256"

# Database Configuration (from env)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres")
DATABASE_SCHEMA = "ai_proma"
DATABASE_TABLE = "users_proma"
