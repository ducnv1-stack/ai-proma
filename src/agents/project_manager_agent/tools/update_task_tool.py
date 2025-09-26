"""
Update Task Tool for Project Manager Agent
Update Epic, Task, or Sub_task by ID
"""

from typing import Dict, Any, Optional
import logging
from src.api.services.epic_service import EpicService
from src.api.logging.logger import get_logger

logger = get_logger(__name__)

async def update_task_tool(
    action_description: str,
    item_id: str,  # ID of the item to update (epic-xxx, task-xxx, subtask-xxx)
    task_name: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[str] = None,  # "Highest", "High", "Medium", "Low", "Lowest"
    status: Optional[str] = None,  # "To do", "Inprogress", "Done"
    assignee_name: Optional[str] = None,
    start_date: Optional[str] = None,  # dd/MM/yyyy format
    due_date: Optional[str] = None,  # dd/MM/yyyy format
    deadline_extend: Optional[str] = None,  # dd/MM/yyyy format
    expected_outcome: str = "Task updated successfully"
) -> Dict[str, Any]:
    """
    Update an existing Epic, Task, or Sub_task
    
    Args:
        action_description: Clear description of what you intend to do
        item_id: ID of the item to update (epic-xxx, task-xxx, subtask-xxx)
        task_name: New task name
        description: New description
        priority: New priority level
        status: New status
        assignee_name: New assignee name
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
        # Determine item type from ID
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
        
        # Initialize epic service
        epic_service = EpicService()
        
        # Prepare update data (only include non-None values)
        update_data = {}
        
        if task_name is not None:
            if item_type == "Epic":
                update_data["epic_name"] = task_name
            elif item_type == "Task":
                update_data["task_name"] = task_name
            elif item_type == "Sub_task":
                update_data["sub_task_name"] = task_name
        
        if description is not None:
            update_data["description"] = description
        if priority is not None:
            update_data["priority"] = priority
        if status is not None:
            update_data["status"] = status
        if assignee_name is not None:
            update_data["assignee_name"] = assignee_name
        if start_date is not None:
            update_data["start_date"] = start_date
        if due_date is not None:
            update_data["due_date"] = due_date
        if deadline_extend is not None:
            update_data["deadline_extend"] = deadline_extend
        
        if not update_data:
            return {
                "status": "error",
                "message": "No update data provided. At least one field must be specified for update.",
                "action_description": action_description
            }
        
        # Note: This tool requires context (workspace_id, user_id)
        # In actual implementation, these would be injected from the agent's context
        
        result = {
            "status": "success",
            "message": f"{item_type} '{item_id}' would be updated successfully",
            "item_id": item_id,
            "item_type": item_type,
            "update_data": update_data,
            "action_description": action_description,
            "expected_outcome": expected_outcome,
            "note": "This tool requires integration with agent context for actual update"
        }
        
        logger.info(f"Task update prepared: {item_type} - {item_id}")
        return result
        
    except Exception as e:
        logger.error(f"Error in update_task_tool: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to update task: {str(e)}",
            "action_description": action_description
        }
