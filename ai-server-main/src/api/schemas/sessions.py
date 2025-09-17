from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class CreateSessionRequest(BaseModel):
    """Request model for creating a new agent session"""
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Initial session metadata")

class CreateSessionResponse(BaseModel):
    """Response model for creating a new agent session"""
    session_id: str = Field(..., description="The created session ID")
    agent_id: str = Field(..., description="The ID of the agent the session is for")
    workspace_id: str = Field(..., description="The Id of workspace user created")
    created_at: str = Field(..., description="Timestamp when the session was created")
