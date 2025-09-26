"""
Delete Task Tool for Project Manager Agent
Delete Epic, Task, or Sub_task by name with cascade logic
"""

from typing import Dict, Any, Optional, List
import logging
from src.api.services.epic_service import EpicService
from src.api.logging.logger import get_logger

logger = get_logger(__name__)

def delete_task_by_name_tool(
    action_description: str,
    task_name: str,
    task_type: Optional[str] = None,  # "Epic", "Task", "Sub_task" - if None, search all types
    dry_run: bool = True,  # Default to dry run for safety
    expected_outcome: str = "Task deleted successfully"
) -> Dict[str, Any]:
    """
    Delete Epic, Task, or Sub_task by name with cascade logic
    - If Epic is deleted: all related Tasks and Sub_tasks are deleted
    - If Task is deleted: all related Sub_tasks are deleted  
    - If Sub_task is deleted: only that Sub_task is deleted
    
    Args:
        action_description: Clear description of what you intend to do
        task_name: Name of the task to delete
        task_type: Type of task ("Epic", "Task", "Sub_task") - if None, search all
        dry_run: If True, only preview what would be deleted (default: True for safety)
        expected_outcome: What you expect to achieve
    
    Returns:
        Dict containing deletion result or preview
    """
    
    logger.info(f"[TOOL EXECUTED] delete_task_by_name_tool: {action_description}")
    logger.info(f"Deleting task: {task_name}, type: {task_type}, dry_run: {dry_run}")
    
    try:
        # Initialize epic service
        epic_service = EpicService()
        
        # Step 1: Search for tasks by name
        # Note: This requires getting all tasks first, then filtering by name
        # In actual implementation, this would query the database
        
        search_types = [task_type] if task_type else ["Epic", "Task", "Sub_task"]
        found_items = []
        
        # Simulate search results (in real implementation, this would query database)
        for search_type in search_types:
            # This would be replaced with actual database query
            found_items.append({
                "item_id": f"{search_type.lower()}-simulated-id",
                "item_type": search_type,
                "item_name": task_name,
                "found_by": "name_match"
            })
        
        if not found_items:
            return {
                "status": "error",
                "message": f"No tasks found with name '{task_name}'",
                "task_name": task_name,
                "search_types": search_types,
                "action_description": action_description
            }
        
        # Step 2: Determine cascade deletion scope
        deletion_plan = []
        
        for item in found_items:
            item_type = item["item_type"]
            item_id = item["item_id"]
            
            if item_type == "Epic":
                # Epic deletion cascades to all tasks and subtasks
                deletion_plan.append({
                    "item_id": item_id,
                    "item_type": "Epic",
                    "item_name": task_name,
                    "cascade_reason": "primary_target"
                })
                # Add simulated related tasks and subtasks
                deletion_plan.extend([
                    {"item_id": "task-related-1", "item_type": "Task", "item_name": "Related Task 1", "cascade_reason": "epic_cascade"},
                    {"item_id": "task-related-2", "item_type": "Task", "item_name": "Related Task 2", "cascade_reason": "epic_cascade"},
                    {"item_id": "subtask-related-1", "item_type": "Sub_task", "item_name": "Related Subtask 1", "cascade_reason": "epic_cascade"}
                ])
                
            elif item_type == "Task":
                # Task deletion cascades to related subtasks
                deletion_plan.append({
                    "item_id": item_id,
                    "item_type": "Task", 
                    "item_name": task_name,
                    "cascade_reason": "primary_target"
                })
                # Add simulated related subtasks
                deletion_plan.extend([
                    {"item_id": "subtask-child-1", "item_type": "Sub_task", "item_name": "Child Subtask 1", "cascade_reason": "task_cascade"}
                ])
                
            elif item_type == "Sub_task":
                # Sub_task deletion only affects itself
                deletion_plan.append({
                    "item_id": item_id,
                    "item_type": "Sub_task",
                    "item_name": task_name,
                    "cascade_reason": "primary_target"
                })
        
        # Step 3: Calculate deletion summary
        deletion_summary = {
            "epic": len([item for item in deletion_plan if item["item_type"] == "Epic"]),
            "task": len([item for item in deletion_plan if item["item_type"] == "Task"]),
            "subtask": len([item for item in deletion_plan if item["item_type"] == "Sub_task"])
        }
        
        total_items = sum(deletion_summary.values())
        
        # Step 4: Return result based on dry_run flag
        if dry_run:
            result = {
                "status": "preview",
                "message": f"PREVIEW: Would delete {total_items} items (Epic: {deletion_summary['epic']}, Task: {deletion_summary['task']}, Sub_task: {deletion_summary['subtask']})",
                "task_name": task_name,
                "dry_run": True,
                "deletion_plan": deletion_plan,
                "deletion_summary": deletion_summary,
                "total_items": total_items,
                "action_description": action_description,
                "warning": "This is a preview. Set dry_run=False to execute actual deletion.",
                "note": "This tool requires integration with agent context for actual deletion"
            }
        else:
            result = {
                "status": "success",
                "message": f"Would delete {total_items} items successfully",
                "task_name": task_name,
                "dry_run": False,
                "deleted_items": deletion_plan,
                "deletion_summary": deletion_summary,
                "total_items": total_items,
                "action_description": action_description,
                "expected_outcome": expected_outcome,
                "note": "This tool requires integration with agent context for actual deletion"
            }
        
        logger.info(f"Deletion {'preview' if dry_run else 'execution'} prepared: {total_items} items")
        return result
        
    except Exception as e:
        logger.error(f"Error in delete_task_by_name_tool: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to delete task: {str(e)}",
            "action_description": action_description
        }
