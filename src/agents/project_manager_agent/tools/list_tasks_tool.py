"""
List Tasks Tool for Project Manager Agent
Get tasks by type, time, or assignee
"""

from typing import Dict, Any, Optional, List
import logging
from datetime import datetime, timedelta
from src.api.services.epic_service import EpicService
from src.api.logging.logger import get_logger

logger = get_logger(__name__)

def list_tasks_tool(
    action_description: str,
    task_type: str = "All",  # "Epic", "Task", "Sub_task", "All"
    time_filter: Optional[str] = None,  # "today", "this_week", "this_month", "overdue"
    assignee_name: Optional[str] = None,
    expected_outcome: str = "Tasks retrieved successfully"
) -> Dict[str, Any]:
    """
    List tasks with various filters
    
    Args:
        action_description: Clear description of what you intend to do
        task_type: Type of tasks to retrieve ("Epic", "Task", "Sub_task", "All")
        time_filter: Time-based filter ("today", "this_week", "this_month", "overdue")
        assignee_name: Filter by assignee name
        expected_outcome: What you expect to achieve
    
    Returns:
        Dict containing list of tasks
    """
    
    logger.info(f"[TOOL EXECUTED] list_tasks_tool: {action_description}")
    logger.info(f"Listing {task_type} tasks with filters: time={time_filter}, assignee={assignee_name}")
    
    try:
        # Initialize epic service
        epic_service = EpicService()
        
        # Prepare filter description
        filters = []
        if task_type != "All":
            filters.append(f"type: {task_type}")
        if time_filter:
            filters.append(f"time: {time_filter}")
        if assignee_name:
            filters.append(f"assignee: {assignee_name}")
        
        filter_description = ", ".join(filters) if filters else "no filters"
        
        # Calculate time range for time_filter
        time_range = None
        if time_filter:
            now = datetime.now()
            if time_filter == "today":
                time_range = {
                    "start": now.strftime("%d/%m/%Y"),
                    "end": now.strftime("%d/%m/%Y")
                }
            elif time_filter == "this_week":
                start_of_week = now - timedelta(days=now.weekday())
                end_of_week = start_of_week + timedelta(days=6)
                time_range = {
                    "start": start_of_week.strftime("%d/%m/%Y"),
                    "end": end_of_week.strftime("%d/%m/%Y")
                }
            elif time_filter == "this_month":
                start_of_month = now.replace(day=1)
                if now.month == 12:
                    end_of_month = now.replace(year=now.year + 1, month=1, day=1) - timedelta(days=1)
                else:
                    end_of_month = now.replace(month=now.month + 1, day=1) - timedelta(days=1)
                time_range = {
                    "start": start_of_month.strftime("%d/%m/%Y"),
                    "end": end_of_month.strftime("%d/%m/%Y")
                }
            elif time_filter == "overdue":
                time_range = {
                    "end": (now - timedelta(days=1)).strftime("%d/%m/%Y"),
                    "type": "overdue"
                }
        
        # Note: This tool requires context (workspace_id, user_id)
        # In actual implementation, these would be injected from the agent's context
        
        result = {
            "status": "success",
            "message": f"Tasks retrieved with filters: {filter_description}",
            "task_type": task_type,
            "filters": {
                "time_filter": time_filter,
                "time_range": time_range,
                "assignee_name": assignee_name
            },
            "action_description": action_description,
            "expected_outcome": expected_outcome,
            "note": "This tool requires integration with agent context for actual data retrieval",
            "sample_response": {
                "total_count": 0,
                "tasks": []
            }
        }
        
        logger.info(f"Task list prepared with filters: {filter_description}")
        return result
        
    except Exception as e:
        logger.error(f"Error in list_tasks_tool: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to list tasks: {str(e)}",
            "action_description": action_description
        }
