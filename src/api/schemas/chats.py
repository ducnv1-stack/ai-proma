from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class MessageInput(BaseModel):
    """Input model for sending a message to an agent"""
    message: str = Field(..., description="The message content to send to the agent")
    images: List[str] = Field(default=[], description="Image URLs as string")
    files: List[str] = Field(default=[], description="File URLs as string")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata for the message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Help me analyze this data",
                "images": [],
                "files": [],
                "metadata": {}
            }
        }


class UnifiedChatRequest(BaseModel):
    """Unified chat request model with optional session management"""
    message: str = Field(..., description="Message content to send to the agent")
    agent_id: str = Field(..., description="Agent ID to chat with")
    session_id: Optional[str] = Field(None, description="Session ID (optional - creates new if None)")
    images: List[str] = Field(default=[], description="Image URLs as string")
    files: List[str] = Field(default=[], description="File URLs as string")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata for the message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Xin chào PROMA! Tôi cần giúp về quản lý dự án",
                "agent_id": "project_manager_agent",
                "session_id": None,
                "images": [],
                "files": [],
                "metadata": {}
            }
        }


class UnifiedChatResponse(BaseModel):
    """Unified chat response model"""
    session_id: str = Field(..., description="Session ID used or created")
    agent_id: str = Field(..., description="Agent ID that processed the message")
    created_session: bool = Field(False, description="Whether a new session was created")
    message: str = Field(..., description="User message that was sent")
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "abc123-def456-ghi789",
                "agent_id": "project_manager_agent", 
                "created_session": True,
                "message": "Xin chào PROMA! Tôi cần giúp về quản lý dự án"
            }
        }