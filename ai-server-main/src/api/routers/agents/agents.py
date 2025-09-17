from fastapi import APIRouter, HTTPException
from src.agents import AGENT_MAPPING
from src.api.schemas.agents import AgentListResponse, AgentDetailResponse, AgentSummary, AgentDetail
from src.api.logging.logger import get_logger
from typing import Dict, Any

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

@router.get("/", response_model=AgentListResponse)
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

@router.get("/{agent_id}", response_model=AgentDetailResponse)
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