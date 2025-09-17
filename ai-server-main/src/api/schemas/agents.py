from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class AgentSummary(BaseModel):
    id: str
    name: str
    description: str
    
class AgentDetail(BaseModel):
    id: str
    name: str
    description: str
    instruction: Optional[str] = None
    tools: Optional[List[str]] = []
    model_config: Optional[Dict[str, Any]] = {}
    
class AgentListResponse(BaseModel):
    agents: List[AgentSummary]
    total_count: int
    
class AgentDetailResponse(BaseModel):
    agent: AgentDetail 