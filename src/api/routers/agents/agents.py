from fastapi import APIRouter, HTTPException, Depends, Path
from src.agents import AGENT_MAPPING
from src.api.authentication.dependencies import get_current_active_user
from src.api.schemas.agents import AgentListResponse, AgentDetailResponse, AgentSummary, AgentDetail
from src.api.logging.logger import get_logger
from typing import Dict, Any

from src.api.schemas.sessions import GetAgentSessionsResponse, SessionSummary

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/agents", tags=["Agents"])

def extract_agent_info(agent_id: str, agent_obj) -> Dict[str, Any]:
    """Extract agent information from agent object"""
    try:
        agent_info = {
            "id": agent_id,
            "name": getattr(agent_obj, 'name', agent_id),
            "description": getattr(agent_obj, 'description', 'No description available'),
            "instruction": getattr(agent_obj, 'instruction', None),
            "tools": [tool.name if hasattr(tool, 'name') else str(tool) for tool in getattr(agent_obj, 'tools', [])],
            "model_config": {}
        }
        
        if hasattr(agent_obj, 'model'):
            model = agent_obj.model
            agent_info["model_config"] = {
                "model_type": type(model).__name__,
                "model_name": getattr(model, 'model', 'unknown')
            }
            
        # Extract generation config if available
        if hasattr(agent_obj, 'generate_content_config'):
            config = agent_obj.generate_content_config
            agent_info["model_config"].update({
                "temperature": getattr(config, 'temperature', None),
                "max_output_tokens": getattr(config, 'max_output_tokens', None)
            })
            
        return agent_info
    except Exception as e:
        logger.error(f"Error extracting info for agent {agent_id}: {str(e)}")
        return {
            "id": agent_id,
            "name": agent_id,
            "description": "Error loading agent information",
            "instruction": None,
            "tools": [],
            "model_config": {}
        }

@router.get("/alls", response_model=AgentListResponse)
async def get_agents():
    """
    Get list of all available agents
    
    Returns:
        AgentListResponse: List of available agents with summary information
    """
    try:
        logger.info("Fetching list of available agents")
        
        agents = []
        for agent_id, agent_obj in AGENT_MAPPING.items():
            agent_info = extract_agent_info(agent_id, agent_obj)
            agents.append(AgentSummary(
                id=agent_info["id"],
                name=agent_info["name"],
                description=agent_info["description"]
            ))
            
        logger.info(f"Successfully retrieved {len(agents)} agents")
        return AgentListResponse(
            agents=agents,
            total_count=len(agents)
        )
        
    except Exception as e:
        logger.error(f"Error fetching agents: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while fetching agents")

@router.get("/detail/{agent_id}", response_model=AgentDetailResponse)
async def get_agent_detail(agent_id: str):
    """
    Get detailed information about a specific agent
    
    Args:
        agent_id: The ID of the agent to retrieve
        
    Returns:
        AgentDetailResponse: Detailed information about the agent
    """
    try:
        logger.info(f"Fetching details for agent: {agent_id}")
        
        if agent_id not in AGENT_MAPPING:
            logger.warning(f"Agent not found: {agent_id}")
            raise HTTPException(status_code=404, detail=f"Agent with ID '{agent_id}' not found")
            
        agent_obj = AGENT_MAPPING[agent_id]
        agent_info = extract_agent_info(agent_id, agent_obj)
        
        agent_detail = AgentDetail(
            id=agent_info["id"],
            name=agent_info["name"],
            description=agent_info["description"],
            instruction=agent_info["instruction"],
            tools=agent_info["tools"],
            model_config=agent_info["model_config"]
        )
        
        logger.info(f"Successfully retrieved details for agent: {agent_id}")
        return AgentDetailResponse(agent=agent_detail)
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error fetching agent details for {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while fetching agent details") 
    


@router.get("/{agent_id}/sessions", response_model=GetAgentSessionsResponse)
async def get_agent_sessions(
    agent_id: str = Path(..., description="Agent ID to get sessions for"),
    current_user: dict = Depends(get_current_active_user)
):
    token_data = current_user.get("token_data", {})
    user_data = current_user.get("user", {})
    
    user_id = token_data.get("user_id") or user_data.get("id") or user_data.get("user_id")
    if not user_id:
        logger.error("User ID not found in token")
        raise HTTPException(status_code=401, detail="User ID not found in token")
    
    workspace_id = token_data.get("workspace_id")
    if not workspace_id:
        logger.error("Workspace ID not found in token")
        raise HTTPException(status_code=401, detail="Workspace ID not found in token")

    if agent_id not in AGENT_MAPPING:
        logger.error(f"Agent {agent_id} not found in AGENT_MAPPING")
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")

    try:
        # Import database config and create connection inside function
        from src.database.postgres import DATABASE_URL
        import asyncpg
        
        # Use direct DB query to get sessions for this agent
        conn = await asyncpg.connect(DATABASE_URL)
        try:
            # Get sessions with state filter
            sessions_query = """
                SELECT id, app_name, user_id, create_time, update_time, state
                FROM sessions 
                WHERE app_name = $1 
                AND user_id = $2
                AND state->>'user_id' = $3
                AND state->>'workspace_id' = $4
                AND state->>'agent_id' = $5
                ORDER BY create_time DESC
            """
            sessions = await conn.fetch(sessions_query, agent_id, user_id, user_id, workspace_id, agent_id)
        finally:
            await conn.close()
        
        session_summaries = []
        for session in sessions:
            # Handle create_time and update_time conversion
            create_time_str = None
            if session["create_time"]:
                create_time_obj = session["create_time"]
                if hasattr(create_time_obj, 'isoformat'):
                    create_time_str = create_time_obj.isoformat()
                else:
                    create_time_str = str(create_time_obj)
            
            update_time_str = None
            if session["update_time"]:
                update_time_obj = session["update_time"]
                if hasattr(update_time_obj, 'isoformat'):
                    update_time_str = update_time_obj.isoformat()
                else:
                    update_time_str = str(update_time_obj)
            
            session_summaries.append(SessionSummary(
                id=session["id"],
                app_name=session["app_name"],
                user_id=session["user_id"],
                create_time=create_time_str,
                update_time=update_time_str
            ))
        
        logger.info(f"Successfully retrieved {len(session_summaries)} sessions for agent '{agent_id}', user '{user_id}' and workspace '{workspace_id}'")
        
        return GetAgentSessionsResponse(
            agent_id=agent_id,
            sessions=session_summaries,
            total_count=len(session_summaries)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve sessions for agent '{agent_id}': {e}")
        raise HTTPException(
            status_code=500, 
            detail="Failed to retrieve sessions from database"
        )
