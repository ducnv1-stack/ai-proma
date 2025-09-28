"""
Smart List Tasks Tool for Project Manager Agent
Enhanced version with real database integration and hierarchy support
"""

from typing import Dict, Any, Optional, List
import logging
import threading
import asyncio
import concurrent.futures
from datetime import datetime, timedelta
from src.api.services.epic_service import EpicService
from src.api.logging.logger import get_logger

logger = get_logger(__name__)

def smart_list_tasks_tool(
    action_description: str,
    scope: str = "all",  # "all", "epic", "task", "subtask"
    include_hierarchy: bool = True,
    time_filter: Optional[str] = None,  # "today", "this_week", "this_month", "overdue"
    assignee_name: Optional[str] = None,
    expected_outcome: str = "Tasks retrieved successfully"
) -> Dict[str, Any]:
    """
    Smart tool to list all work items with hierarchy support
    
    Args:
        action_description: Clear description of what you intend to do
        scope: Scope of items to retrieve ("all", "epic", "task", "subtask")
        include_hierarchy: Whether to return hierarchical structure
        time_filter: Time-based filter ("today", "this_week", "this_month", "overdue")
        assignee_name: Filter by assignee name
        expected_outcome: What you expect to achieve
    
    Returns:
        Dict containing hierarchical list of work items
    """
    
    logger.info(f"[SMART TOOL] smart_list_tasks_tool: {action_description}")
    logger.info(f"Parameters: scope={scope}, hierarchy={include_hierarchy}, time_filter={time_filter}")

    # Lightweight natural-language mapping when time_filter is not set
    if not time_filter and isinstance(action_description, str):
        text = action_description.lower().strip()
        if any(k in text for k in ["sắp đến hạn", "sap den han", "due soon", "upcoming", "gan den han"]):
            time_filter = "due_soon"
        elif any(k in text for k in ["tháng sau", "thang sau", "next month"]):
            time_filter = "next_month"
        elif any(k in text for k in ["hôm nay", "hom nay", "today"]):
            time_filter = "today"
        elif any(k in text for k in ["tuần này", "tuan nay", "this week", "this_week"]):
            time_filter = "this_week"
        elif any(k in text for k in ["tháng này", "thang nay", "this month", "this_month"]):
            time_filter = "this_month"
        elif any(k in text for k in ["quá hạn", "qua han", "overdue"]):
            time_filter = "overdue"
    
    try:
        # 1. Get context from thread-local storage
        context = None
        workspace_id = None
        user_id = None
        user_name = None
        
        try:
            context = getattr(threading.current_thread(), 'agent_context', None)
            if context:
                workspace_id = context.get('workspace_id')
                user_id = context.get('user_id')
                user_name = context.get('user_name')
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
            user_name = user_name or os.getenv('AGENT_USER_NAME', 'Default User')
            logger.info(f"Using fallback context: workspace_id={workspace_id}, user_id={user_id}")
        
        # 3. Initialize epic service
        epic_service = EpicService()
        
        # 4. Determine what to fetch based on scope
        items_to_fetch = []
        if scope == "all":
            items_to_fetch = ["Epic", "Task", "Sub_task"]
        elif scope == "epic":
            items_to_fetch = ["Epic"]
        elif scope == "task":
            items_to_fetch = ["Task"]
        elif scope == "subtask":
            items_to_fetch = ["Sub_task"]
        else:
            items_to_fetch = ["Epic", "Task", "Sub_task"]  # Default to all
        
        # 5. Fetch data from database using async wrapper
        all_items = []
        epics = []
        tasks = []
        subtasks = []
        
        async def fetch_data():
            nonlocal all_items, epics, tasks, subtasks
            # Prefer DB-side time filtering if requested
            if time_filter:
                try:
                    items = await epic_service.list_tasks_by_time_period(
                        workspace_id=workspace_id,
                        user_id=user_id,
                        time_period=time_filter,
                        scope=("all" if scope == "all" else scope.title()),
                        assignee_name=assignee_name
                    )
                    all_items.extend(items)
                    # When time filter is used, we return flat items; hierarchy will be built if requested
                    epics = [i for i in items if (hasattr(i.type, 'value') and i.type.value == 'Epic') or str(i.type) == 'Epic']
                    tasks = [i for i in items if (hasattr(i.type, 'value') and i.type.value == 'Task') or str(i.type) == 'Task']
                    subtasks = [i for i in items if (hasattr(i.type, 'value') and i.type.value == 'Sub_task') or str(i.type) == 'Sub_task']
                    logger.info(f"Fetched {len(items)} items by time period: {time_filter}")
                    return
                except Exception as e:
                    logger.warning(f"DB time filter failed, falling back to type-based fetch: {e}")
            # Fallback: fetch by type then apply in-memory filters
            for item_type in items_to_fetch:
                try:
                    items = await epic_service.list_tasks_by_type(
                        workspace_id=workspace_id,
                        user_id=user_id,
                        type_filter=item_type
                    )
                    all_items.extend(items)
                    if item_type == "Epic":
                        epics = items
                    elif item_type == "Task":
                        tasks = items
                    elif item_type == "Sub_task":
                        subtasks = items
                    logger.info(f"Fetched {len(items)} {item_type.lower()}s")
                except Exception as e:
                    logger.error(f"Error fetching {item_type}: {e}")
                    continue
        
        # Run async function in new thread to avoid event loop conflicts
        def run_async_in_thread():
            return asyncio.run(fetch_data())
        
        try:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(run_async_in_thread)
                future.result(timeout=30)  # 30 second timeout
        except Exception as e:
            logger.error(f"Error running async fetch: {e}")
            return {
                "status": "error",
                "message": f"Failed to fetch data: {str(e)}",
                "total_items": 0,
                "action_description": action_description
            }
        
        # 6. Apply filters
        filtered_items = apply_filters(all_items, time_filter, assignee_name)
        
        # 7. Build response
        if include_hierarchy and scope == "all":
            # Build hierarchical structure
            hierarchy = build_hierarchy(epics, tasks, subtasks)
            response = {
                "status": "success",
                "message": f"Found {len(filtered_items)} work items across {len(epics)} epics",
                "total_items": len(filtered_items),
                "workspace_id": workspace_id,
                "user_id": user_id,
                "user_name": user_name,
                "scope": scope,
                "filters_applied": {
                    "time_filter": time_filter,
                    "assignee_name": assignee_name
                },
                "hierarchy": hierarchy,
                "summary": {
                    "epics": len(epics),
                    "tasks": len(tasks),
                    "subtasks": len(subtasks),
                    "total": len(filtered_items),
                    "completed": count_by_status(filtered_items, "Done"),
                    "in_progress": count_by_status(filtered_items, "Inprogress"),
                    "todo": count_by_status(filtered_items, "To do")
                },
                "action_description": action_description,
                "expected_outcome": expected_outcome
            }
        else:
            # Flat list structure
            response = {
                "status": "success",
                "message": f"Found {len(filtered_items)} {scope} items",
                "total_items": len(filtered_items),
                "workspace_id": workspace_id,
                "user_id": user_id,
                "user_name": user_name,
                "scope": scope,
                "items": [item_to_dict(item) for item in filtered_items],
                "action_description": action_description,
                "expected_outcome": expected_outcome
            }
        
        logger.info(f"Successfully retrieved {len(filtered_items)} items")
        return response
        
    except Exception as e:
        logger.error(f"Error in smart_list_tasks_tool: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to retrieve tasks: {str(e)}",
            "total_items": 0,
            "action_description": action_description,
            "error_details": str(e)
        }

def build_hierarchy(epics: List, tasks: List, subtasks: List) -> List[Dict]:
    """Build hierarchical structure Epic -> Task -> Sub_task"""
    hierarchy = []
    
    for epic in epics:
        epic_dict = item_to_dict(epic)
        epic_tasks = []
        
        # Find tasks belonging to this epic
        for task in tasks:
            if task.epic_id == epic.epic_id:
                task_dict = item_to_dict(task)
                task_subtasks = []
                
                # Find subtasks belonging to this task
                for subtask in subtasks:
                    if subtask.task_id == task.task_id:
                        task_subtasks.append(item_to_dict(subtask))
                
                task_dict["subtasks"] = task_subtasks
                epic_tasks.append(task_dict)
        
        epic_dict["tasks"] = epic_tasks
        hierarchy.append({"epic": epic_dict})
    
    return hierarchy

def item_to_dict(item) -> Dict:
    """Convert EpicResponse object to dictionary"""
    return {
        "id": item.epic_id or item.task_id or item.sub_task_id,
        "name": item.epic_name or item.task_name or item.sub_task_name,
        "type": item.type.value if hasattr(item.type, 'value') else str(item.type),
        "description": item.description,
        "priority": item.priority.value if hasattr(item.priority, 'value') else str(item.priority),
        "status": item.status.value if hasattr(item.status, 'value') else str(item.status),
        "assignee_name": item.assignee_name,
        "start_date": item.start_date,
        "due_date": item.due_date,
        "create_at": item.create_at,
        "update_at": item.update_at
    }

def apply_filters(items: List, time_filter: Optional[str], assignee_name: Optional[str]) -> List:
    """Apply time and assignee filters to items"""
    filtered = items
    
    # Apply assignee filter
    if assignee_name:
        filtered = [item for item in filtered if item.assignee_name and assignee_name.lower() in item.assignee_name.lower()]
    
    # Apply time filter (simplified implementation)
    if time_filter:
        # This would need more sophisticated date parsing
        # For now, return all items
        pass
    
    return filtered

def count_by_status(items: List, status: str) -> int:
    """Count items by status"""
    return len([item for item in items if (hasattr(item.status, 'value') and item.status.value == status) or str(item.status) == status])

# Keep the original function name for backward compatibility
def list_tasks_tool(
    action_description: str,
    task_type: str = "All",
    time_filter: Optional[str] = None,
    assignee_name: Optional[str] = None,
    expected_outcome: str = "Tasks retrieved successfully"
) -> Dict[str, Any]:
    """
    Backward compatibility wrapper for the original list_tasks_tool
    """
    scope_mapping = {
        "All": "all",
        "Epic": "epic", 
        "Task": "task",
        "Sub_task": "subtask"
    }
    
    return smart_list_tasks_tool(
        action_description=action_description,
        scope=scope_mapping.get(task_type, "all"),
        include_hierarchy=True,
        time_filter=time_filter,
        assignee_name=assignee_name,
        expected_outcome=expected_outcome
    )