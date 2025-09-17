from pydantic import Field
from pydantic_settings import BaseSettings


class MemoryBankSettings(BaseSettings):
    # VertexAI Memory Bank settings
    vertex_project_id: str = Field(env="VERTEX_PROJECT_ID", description="Vertex project id")
    vertex_location: str = Field(default="us-central1", env="VERTEX_LOCATION", description="Vertex location region")
    vertex_agent_engine_id: str = Field(env="VERTEX_AGENT_ENGINE_ID", description="Vertex AI agent engine ID")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

vertexai_memorybank_settings = MemoryBankSettings()