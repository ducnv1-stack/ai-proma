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