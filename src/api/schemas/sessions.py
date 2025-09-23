from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

class CreateSessionRequest(BaseModel):
    """Request model for creating a new agent session"""
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Initial session metadata")

class CreateSessionResponse(BaseModel):
    """Response model for creating a new agent session"""
    session_id: str = Field(..., description="The created session ID")
    agent_id: str = Field(..., description="The ID of the agent the session is for")
    workspace_id: str = Field(..., description="The Id of workspace user created")
    created_at: str = Field(..., description="Timestamp when the session was created")

class GetSessionResponse(BaseModel):
    """Response model for getting session details"""
    id: Optional[str] = Field(None, description="Session ID")
    app_name: Optional[str] = Field(None, description="Application name")
    user_id: Optional[str] = Field(None, description="User ID")
    state: Dict[str, Any] = Field(default_factory=dict, description="Session state")
    create_time: Optional[str] = Field(None, description="Session creation timestamp")
    update_time: Optional[str] = Field(None, description="Session last update timestamp")

class EventResponse(BaseModel):
    """Response model for session events"""
    id: str = Field(..., description="Event ID")
    app_name: str = Field(..., description="Application name")
    user_id: str = Field(..., description="User ID")
    session_id: str = Field(..., description="Session ID")
    invocation_id: Optional[str] = Field(None, description="Invocation ID")
    author: str = Field(..., description="Event author")
    branch: Optional[str] = Field(None, description="Branch")
    timestamp: str = Field(..., description="Event timestamp")
    content: Optional[str] = Field(None, description="Event content")
    actions: Optional[List[Dict[str, Any]]] = Field(None, description="Event actions")
    long_running_tool_ids_json: Optional[str] = Field(None, description="Long running tool IDs")
    grounding_metadata: Optional[Dict[str, Any]] = Field(None, description="Grounding metadata")
    partial: Optional[bool] = Field(None, description="Is partial event")
    turn_complete: Optional[bool] = Field(None, description="Is turn complete")
    error_code: Optional[str] = Field(None, description="Error code")
    error_message: Optional[str] = Field(None, description="Error message")
    interrupted: Optional[bool] = Field(None, description="Is interrupted")
    custom_metadata: Optional[Dict[str, Any]] = Field(None, description="Custom metadata")

class GetEventsResponse(BaseModel):
    """Response model for getting session events"""
    session_id: str = Field(..., description="Session ID")
    events: List[EventResponse] = Field(..., description="List of events")
    total_count: int = Field(..., description="Total number of events")

class SessionSummary(BaseModel):
    """Summary of a session for listing"""
    id: Optional[str] = Field(None, description="Session ID")
    app_name: Optional[str] = Field(None, description="Application name")
    user_id: Optional[str] = Field(None, description="User ID")
    create_time: Optional[str] = Field(None, description="Session creation timestamp")
    update_time: Optional[str] = Field(None, description="Session last update timestamp")

class GetAgentSessionsResponse(BaseModel):
    """Response model for getting all sessions of an agent"""
    agent_id: str = Field(..., description="Agent ID")
    sessions: List[SessionSummary] = Field(..., description="List of sessions")
    total_count: int = Field(..., description="Total number of sessions")
