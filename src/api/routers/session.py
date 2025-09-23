import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Path
from src.api.schemas.sessions import (
    CreateSessionRequest, 
    CreateSessionResponse, 
    GetEventsResponse,
    EventResponse,
)
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

@router.get("/sessions/{session_id}/events", response_model=GetEventsResponse)
async def get_session_events(
    session_id: str = Path(..., description="Session ID to get events for"),
    current_user: dict = Depends(get_current_active_user)
):
    """Get all events for a session with user authorization check"""
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

    try:
        # Import database config and create connection inside function
        from src.database.postgres import DATABASE_URL
        import asyncpg
        
        # Use direct DB query to select top 50 events that not need to use session service
        # First check if session exists for this user
        conn = await asyncpg.connect(DATABASE_URL)
        try:
            # Check if session exists for this user
            check_session_query = """
                SELECT 1 FROM sessions 
                WHERE id = $1 
                AND user_id = $2 
                AND app_name = $3
                AND state->>'user_id' = $4
                AND state->>'workspace_id' = $5
                AND state->>'agent_id' = $6
                LIMIT 1
            """
            session_exists = await conn.fetchval(check_session_query, session_id, user_id, agent_id, user_id, workspace_id, agent_id)
            
            if not session_exists:
                logger.warning(f"Session '{session_id}' not found for user '{user_id}' and agent '{agent_id}'")
                raise HTTPException(status_code=404, detail="Session not found")
            
            # Get top 50 events for this session
            events_query = """
                SELECT id, app_name, user_id, session_id, invocation_id, author, branch, 
                       timestamp, content, actions, long_running_tool_ids_json, 
                       grounding_metadata, partial, turn_complete, error_code, 
                       error_message, interrupted, custom_metadata
                FROM events 
                WHERE session_id = $1 AND user_id = $2 AND app_name = $3
                ORDER BY timestamp DESC
                LIMIT 50
            """
            events = await conn.fetch(events_query, session_id, user_id, agent_id)
        finally:
            await conn.close()
        
        event_responses = []
        for event in events:
            # Handle timestamp conversion
            timestamp_str = None
            if event["timestamp"]:
                timestamp_obj = event["timestamp"]
                if hasattr(timestamp_obj, 'isoformat'):
                    timestamp_str = timestamp_obj.isoformat()
                else:
                    timestamp_str = str(timestamp_obj)
            
            # Handle actions deserialization (from bytes to list of dicts)
            actions_list = None
            if event["actions"]:
                try:
                    import pickle
                    actions_bytes = event["actions"]
                    if isinstance(actions_bytes, bytes):
                        pickled_actions = pickle.loads(actions_bytes)
                        # Convert tuples to dictionaries
                        if isinstance(pickled_actions, list):
                            actions_list = []
                            for action in pickled_actions:
                                if isinstance(action, tuple) and len(action) == 2:
                                    actions_list.append({
                                        "action_type": action[0],
                                        "value": action[1]
                                    })
                                elif isinstance(action, dict):
                                    actions_list.append(action)
                                else:
                                    # Convert other types to string representation
                                    actions_list.append({"action": str(action)})
                        else:
                            actions_list = [{"action": str(pickled_actions)}]
                    elif isinstance(actions_bytes, str):
                        actions_list = eval(actions_bytes) if actions_bytes != 'null' else None
                except Exception:
                    actions_list = None


            # Handle custom_metadata conversion (from string to dict)
            custom_metadata_dict = None
            if event["custom_metadata"]:
                try:
                    custom_str = event["custom_metadata"]
                    if custom_str and custom_str != 'null':
                        import json
                        custom_metadata_dict = json.loads(custom_str)
                except Exception:
                    custom_metadata_dict = None
            
            event_responses.append(EventResponse(
                id=event["id"],
                app_name=event["app_name"],
                user_id=event["user_id"],
                session_id=event["session_id"],
                author=event["author"],
                branch=event["branch"],
                timestamp=timestamp_str,
                content=event["content"],
                actions=actions_list,
                long_running_tool_ids_json=event["long_running_tool_ids_json"],
                turn_complete=event["turn_complete"],
                error_code=event["error_code"],
                error_message=event["error_message"],
                interrupted=event["interrupted"],
                custom_metadata=custom_metadata_dict
            ))
        
        logger.info(f"Successfully retrieved {len(event_responses)} events for session '{session_id}'")
        
        return GetEventsResponse(
            session_id=session_id,
            events=event_responses,
            total_count=len(event_responses)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve events for session '{session_id}': {e}")
        raise HTTPException(
            status_code=500, 
            detail="Failed to retrieve events from database"
        )
