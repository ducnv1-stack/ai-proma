from pydantic import Field
from pydantic_settings import BaseSettings
from typing import Optional


class MemoryBankSettings(BaseSettings):
    # VertexAI Memory Bank settings - Optional for development
    vertex_project_id: Optional[str] = Field(
        default=None, 
        env="VERTEX_PROJECT_ID", 
        description="Vertex project id (optional for development)"
    )
    vertex_location: str = Field(
        default="us-central1", 
        env="VERTEX_LOCATION", 
        description="Vertex location region"
    )
    vertex_agent_engine_id: Optional[str] = Field(
        default=None, 
        env="VERTEX_AGENT_ENGINE_ID", 
        description="Vertex AI agent engine ID (optional for development)"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

# Create settings instance with error handling
try:
    vertexai_memorybank_settings = MemoryBankSettings()
except Exception as e:
    print(f"Warning: VertexAI Memory Bank configuration not found: {e}")
    # Create minimal settings for development
    vertexai_memorybank_settings = MemoryBankSettings(
        vertex_project_id="dev-project",
        vertex_agent_engine_id="dev-engine"
    )