"""
Update Task Tool for Project Manager Agent
Update Epic, Task, or Sub_task by ID
"""

from typing import Dict, Any, Optional
import logging
from src.api.services.epic_service import EpicService
import threading
import asyncio
import concurrent.futures
from src.api.logging.logger import get_logger

logger = get_logger(__name__)

async def update_task_tool(
    action_description: str,
    item_id: str,  # ID of the item to update (epic-xxx, task-xxx, subtask-xxx)
    task_name: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[str] = None,  # "High", "Medium", "Low"
    status: Optional[str] = None,  # "To do", "Inprogress", "Done"
    assignee_name: Optional[str] = None,
    assignee_id: Optional[str] = None,
    start_date: Optional[str] = None,  # dd/MM/yyyy format
    due_date: Optional[str] = None,  # dd/MM/yyyy format
    deadline_extend: Optional[str] = None,  # dd/MM/yyyy format
    expected_outcome: str = "Task updated successfully"
) -> Dict[str, Any]:
    """
    Universal update tool cho Epic, Task, và Sub_task
    
    Args:
        action_description: Clear description of what you intend to do
        item_id: ID of the item to update (epic-xxx, task-xxx, subtask-xxx)
        task_name: New name (epic_name, task_name, or sub_task_name)
        description: New description
        priority: New priority level ("High", "Medium", "Low")
        status: New status ("To do", "Inprogress", "Done")
        assignee_name: New assignee name
        assignee_id: New assignee ID
        start_date: New start date (dd/MM/yyyy)
        due_date: New due date (dd/MM/yyyy)
        deadline_extend: Extended deadline (dd/MM/yyyy)
        expected_outcome: What you expect to achieve
    
    Returns:
        Dict containing update result
    """
    
    logger.info(f"[TOOL EXECUTED] update_task_tool: {action_description}")
    logger.info(f"Updating item: {item_id}")
    
    try:
        # 1. Get context from thread-local storage
        import threading
        context = None
        workspace_id = None
        user_id = None
        
        try:
            context = getattr(threading.current_thread(), 'agent_context', None)
            if context:
                workspace_id = context.get('workspace_id')
                user_id = context.get('user_id')
                logger.info(f"Got context: workspace_id={workspace_id}, user_id={user_id}")
            else:
                logger.warning("No agent context found in thread")
        except Exception as e:
            logger.error(f"Error getting context: {e}")
        
        # 2. Fallback to environment if no context
        if not workspace_id or not user_id:
            import os
            workspace_id = workspace_id or os.getenv('AGENT_WORKSPACE_ID', 'default_workspace')
            user_id = user_id or os.getenv('AGENT_USER_ID', 'default_user')
            logger.info(f"Using fallback context: workspace_id={workspace_id}, user_id={user_id}")
        
        # 3. Determine item type from ID
        item_type = None
        if item_id.startswith("epic-"):
            item_type = "Epic"
        elif item_id.startswith("task-"):
            item_type = "Task"
        elif item_id.startswith("subtask-"):
            item_type = "Sub_task"
        else:
            return {
                "status": "error",
                "message": f"Invalid item ID format: {item_id}. Must start with epic-, task-, or subtask-",
                "action_description": action_description
            }
        
        # 4. Initialize epic service
        epic_service = EpicService()
        
        # 5. Prepare update data (only include non-None values)
        updates = {}
        
        # Handle name field based on item type
        if task_name is not None:
            if item_type == "Epic":
                updates["epic_name"] = task_name
            elif item_type == "Task":
                updates["task_name"] = task_name
            elif item_type == "Sub_task":
                updates["sub_task_name"] = task_name
        
        # Handle common fields
        if description is not None:
            updates["description"] = description
        if priority is not None:
            updates["priority"] = priority
        if status is not None:
            updates["status"] = status
        if assignee_name is not None:
            updates["assignee_name"] = assignee_name
        if assignee_id is not None:
            updates["assignee_id"] = assignee_id
        if start_date is not None:
            updates["start_date"] = start_date
        if due_date is not None:
            updates["due_date"] = due_date
        if deadline_extend is not None:
            updates["deadline_extend"] = deadline_extend
        
        if not updates:
            return {
                "status": "error",
                "message": "No update data provided. At least one field must be specified for update.",
                "action_description": action_description
            }
        
        # 6. ✅ REAL DATABASE UPDATE
        result = await epic_service.update_task_universal(
            workspace_id=workspace_id,
            user_id=user_id,
            target_id=item_id,
            updates=updates
        )
        
        # 7. Add metadata to response
        result["action_description"] = action_description
        result["expected_outcome"] = expected_outcome
        
        logger.info(f"Task update completed: {item_type} - {item_id}")
        return result
        
    except Exception as e:
        logger.error(f"Error in update_task_tool: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to update task: {str(e)}",
            "action_description": action_description,
            "error_details": str(e)
        }
