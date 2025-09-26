"""
Create Task Tool for Project Manager Agent
Supports creating Epic, Task, and Sub_task
"""

from typing import Dict, Any, Optional
import logging
import asyncio
import concurrent.futures
from src.api.services.epic_service import EpicService
from src.api.logging.logger import get_logger
from src.api.schemas.epics import CreateTaskRequest, TypeEnum, PriorityEnum, StatusEnum

logger = get_logger(__name__)

def create_task_tool(
    action_description: str,
    task_type: str,  # "Epic", "Task", "Sub_task"
    task_name: str,
    epic_id: Optional[str] = None,
    parent_id: Optional[str] = None,
    description: Optional[str] = None,
    priority: str = "Medium",
    status: str = "To do",
    assignee_name: Optional[str] = None,
    start_date: Optional[str] = None,
    due_date: Optional[str] = None,
    workspace_id: Optional[str] = None,  # Required for actual DB save
    user_id: Optional[str] = None,       # Required for actual DB save
    user_name: Optional[str] = None,     # Required for actual DB save
    expected_outcome: str = "Task created successfully"
) -> Dict[str, Any]:
    """
    Create Epic, Task, or Sub_task using the existing epic service
    
    Args:
        action_description: Clear description of what you intend to do
        task_type: Type of task to create ("Epic", "Task", "Sub_task")
        task_name: Name of the task
        epic_id: Epic ID (required for Task and Sub_task)
        parent_id: Parent task ID (required for Sub_task)
        description: Task description
        priority: Task priority (Highest, High, Medium, Low, Lowest)
        status: Task status (To do, Inprogress, Done)
        assignee_name: Name of person assigned to task
        start_date: Start date (dd/MM/yyyy format)
        due_date: Due date (dd/MM/yyyy format)
        expected_outcome: What you expect to achieve
    
    Returns:
        Dict containing task creation result
    """
    
    logger.info(f"[TOOL EXECUTED] create_task_tool: {action_description}")
    logger.info(f"Creating {task_type}: {task_name}")
    
    try:
        # Initialize epic service
        epic_service = EpicService()
        
        # Validate required context for actual DB save
        if not workspace_id or not user_id or not user_name:
            logger.warning("Missing context (workspace_id, user_id, user_name) - returning simulation")
            return {
                "status": "simulation",
                "message": f"{task_type} '{task_name}' would be created (missing context for actual save)",
                "task_type": task_type,
                "task_name": task_name,
                "action_description": action_description,
                "note": "Provide workspace_id, user_id, user_name for actual database save"
            }
        
        # Validate task type and required fields
        if task_type == "Epic":
            if not task_name:
                return {
                    "status": "error",
                    "message": "epic_name is required for Epic type",
                    "action_description": action_description
                }
        elif task_type == "Task":
            if not epic_id or not task_name:
                return {
                    "status": "error",
                    "message": "epic_id and task_name are required for Task type",
                    "action_description": action_description
                }
        elif task_type == "Sub_task":
            if not epic_id or not parent_id or not task_name:
                return {
                    "status": "error",
                    "message": "epic_id, parent_id and sub_task_name are required for Sub_task type",
                    "action_description": action_description
                }
        else:
            return {
                "status": "error",
                "message": f"Invalid task_type: {task_type}. Must be Epic, Task, or Sub_task",
                "action_description": action_description
            }
        
        # Map string values to enums
        try:
            type_enum = TypeEnum(task_type)
            priority_enum = PriorityEnum(priority) if priority else PriorityEnum.MEDIUM
            status_enum = StatusEnum(status) if status else StatusEnum.TODO
        except ValueError as e:
            return {
                "status": "error",
                "message": f"Invalid enum value: {str(e)}",
                "action_description": action_description
            }
        
        # Create request object based on task type
        request_data = {
            "type": type_enum,
            "description": description,
            "priority": priority_enum,
            "status": status_enum,
            "assignee_name": assignee_name,
            "start_date": start_date,
            "due_date": due_date
        }
        
        if task_type == "Epic":
            request_data["epic_name"] = task_name
        elif task_type == "Task":
            request_data["epic_id"] = epic_id
            request_data["task_name"] = task_name
        elif task_type == "Sub_task":
            request_data["epic_id"] = epic_id
            request_data["parent_id"] = parent_id
            request_data["sub_task_name"] = task_name
        
        # Create request object
        create_request = CreateTaskRequest(**request_data)
        
        # Actually create in database using EpicService
        logger.info(f"Calling EpicService.create_task_unified for {task_type}: {task_name}")
        
        # Handle async call in sync tool using separate thread
        try:
            def run_async_in_thread():
                """Run async function in a new thread with its own event loop"""
                return asyncio.run(
                    epic_service.create_task_unified(
                        request=create_request,
                        workspace_id=workspace_id,
                        user_id=user_id,
                        user_name=user_name
                    )
                )
            
            # Execute async function in a separate thread
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(run_async_in_thread)
                task_result = future.result(timeout=30)  # 30s timeout
            
            # Extract information from the actual result
            result = {
                "status": "success",
                "message": f"{task_type} '{task_name}' created successfully in database",
                "task_type": task_type,
                "task_name": task_name,
                # "generated_id": task_result.epic_id,  # This contains the actual generated ID
                "generated_id": (
                    task_result.epic_id if task_type == "Epic" 
                    else task_result.task_id if task_type == "Task"
                    else task_result.sub_task_id
                ),
                "workspace_id": workspace_id,
                "user_id": user_id,
                "user_name": user_name,
                "task_result": {
                    # Core IDs
                    "workspace_id": task_result.workspace_id,
                    "user_id": task_result.user_id,
                    "epic_id": task_result.epic_id,
                    "epic_name": task_result.epic_name,
                    "task_id": task_result.task_id,
                    "task_name": task_result.task_name,
                    "sub_task_id": task_result.sub_task_id,
                    "sub_task_name": task_result.sub_task_name,
                    
                    # Content & Classification
                    "description": task_result.description,
                    "category": task_result.category,
                    "type": task_result.type,
                    
                    # Status & Priority
                    "priority": task_result.priority,
                    "status": task_result.status,
                    
                    # Assignment
                    "assignee_id": task_result.assignee_id,
                    "assignee_name": task_result.assignee_name,
                    
                    # Dates
                    "start_date": task_result.start_date,
                    "due_date": task_result.due_date,
                    "deadline_extend": task_result.deadline_extend,
                    "created_at": task_result.create_at,
                    "updated_at": task_result.update_at
                },
                "action_description": action_description,
                "expected_outcome": expected_outcome,
                "note": "Task created successfully in ai_proma.task_info table"
            }
            
        except concurrent.futures.TimeoutError:
            logger.error("Database operation timed out after 30 seconds")
            # Generate ID for fallback
            if task_type == "Epic":
                generated_id = epic_service.generate_epic_id()
            elif task_type == "Task":
                generated_id = epic_service.generate_task_id()
            else:  # Sub_task
                generated_id = epic_service.generate_subtask_id()
            
            result = {
                "status": "error_timeout",
                "message": f"{task_type} '{task_name}' creation timed out",
                "task_type": task_type,
                "task_name": task_name,
                "generated_id": generated_id,
                "workspace_id": workspace_id,
                "user_id": user_id,
                "user_name": user_name,
                "error": "Database operation timed out after 30 seconds",
                "action_description": action_description,
                "expected_outcome": expected_outcome,
                "note": "Database save timed out - please try again"
            }
            
        except Exception as db_error:
            logger.error(f"Database error: {str(db_error)}")
            # Fallback to simulation if DB call fails
            if task_type == "Epic":
                generated_id = epic_service.generate_epic_id()
            elif task_type == "Task":
                generated_id = epic_service.generate_task_id()
            else:  # Sub_task
                generated_id = epic_service.generate_subtask_id()
            
            result = {
                "status": "error_fallback",
                "message": f"{task_type} '{task_name}' creation failed, generated ID for reference",
                "task_type": task_type,
                "task_name": task_name,
                "generated_id": generated_id,
                "workspace_id": workspace_id,
                "user_id": user_id,
                "user_name": user_name,
                "error": str(db_error),
                "action_description": action_description,
                "expected_outcome": expected_outcome,
                "note": f"Database save failed: {str(db_error)}"
            }
        
        logger.info(f"Task operation completed: {task_type} - {task_name}")
        return result
        
    except Exception as e:
        logger.error(f"Error in create_task_tool: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to create {task_type}: {str(e)}",
            "action_description": action_description
        }
