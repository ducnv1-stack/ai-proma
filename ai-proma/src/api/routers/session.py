import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from src.api.schemas.sessions import CreateSessionRequest, CreateSessionResponse
from src.api.authentication.dependencies import get_current_active_user
from src.agents import AGENT_MAPPING
from google.adk.sessions import DatabaseSessionService
from configs import get_database_url
from src.api.logging.logger import get_logger

router = APIRouter(prefix="/api/v1", tags=["Session Management"])
logger = get_logger(__name__)
DB_URL = get_database_url()
session_service = DatabaseSessionService(db_url=DB_URL)

@router.post("/session/create", response_model=CreateSessionResponse)
async def create_new_session(
    data: CreateSessionRequest,
    current_user: dict = Depends(get_current_active_user)
):
    token_data = current_user.get("token_data", {})
    user_data = current_user.get("user", {})
    
    user_id = token_data.get("user_id") or user_data.get("id") or user_data.get("user_id")
    if not user_id:
        logger.error("User ID not found in token")
        raise HTTPException(status_code=401, detail="User ID not found in token")
    
    workspace_id = token_data.get("workspace_id")
    agent_id = token_data.get("agent_id")
    
    if not workspace_id:
        logger.error("Workspace ID not found in token")
        raise HTTPException(status_code=401, detail="Workspace ID not found in token")
        
    if not agent_id:
        logger.error("Agent ID not found in token")
        raise HTTPException(status_code=401, detail="Agent ID not found in token")

    if agent_id not in AGENT_MAPPING:
        logger.error(f"Agent {agent_id} not found in AGENT_MAPPING")
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    
    agent = AGENT_MAPPING[agent_id]
    
    session_id = str(uuid.uuid4())
    
    try:
        created_session = await session_service.create_session(
            app_name=agent.name,
            user_id=user_id,
            session_id=session_id,
            state={
                "user:workspace_id": workspace_id,
                "user_id": user_id,
                "workspace_id": workspace_id,
                "agent_id": agent_id,
                "session_id": session_id,
                **data.metadata  
            }
        )
        
        logger.info(f"Successfully created new session '{session_id}' for user '{user_id}' with agent '{agent_id}' in workspace {workspace_id}")
        
        return CreateSessionResponse(
            session_id=session_id,
            agent_id=agent_id,
            workspace_id=workspace_id,
            created_at=datetime.utcnow().isoformat()
        )
    except Exception as e:
        logger.error(f"Failed to create session for user '{user_id}' with agent '{agent_id}': {e}")
        raise HTTPException(
            status_code=500, 
            detail="Failed to create session in database"
        )
