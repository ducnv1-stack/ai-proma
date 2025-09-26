"""
Context-aware wrapper for create_task_tool
Automatically injects workspace_id, user_id, user_name from agent context
"""

from typing import Dict, Any, Optional
from src.agents.project_manager_agent.tools.create_task_tool import create_task_tool
from src.api.logging.logger import get_logger

logger = get_logger(__name__)

def context_aware_create_task_tool(
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
    expected_outcome: str = "Task created successfully"
) -> Dict[str, Any]:
    """
    Context-aware wrapper for create_task_tool that automatically injects context
    
    This tool will attempt to get context from the current execution environment.
    If context is not available, it will fall back to simulation mode.
    
    Args:
        action_description: Clear description of what you intend to do
        task_type: Type of task to create ("Epic", "Task", "Sub_task")
        task_name: Name of the task
        epic_id: Epic ID (required for Task and Sub_task)
        parent_id: Parent task ID (required for Sub_task)
        description: Task description (optional)
        priority: Task priority (default: "Medium")
        status: Task status (default: "To do")
        assignee_name: Name of assignee (optional)
        start_date: Start date in dd/MM/yyyy format (optional)
        due_date: Due date in dd/MM/yyyy format (optional)
        expected_outcome: What you expect to achieve
    
    Returns:
        Dict containing task creation result
    """
    
    logger.info(f"[CONTEXT-AWARE TOOL] context_aware_create_task_tool: {action_description}")
    
    # Try to get context from various sources
    workspace_id = None
    user_id = None
    user_name = None
    
    # Method 1: Try to get from thread-local storage or global context
    # This would be set by the agent runner when executing tools
    try:
        import threading
        context = getattr(threading.current_thread(), 'agent_context', None)
        if context:
            workspace_id = context.get('workspace_id')
            user_id = context.get('user_id')
            user_name = context.get('user_name')
            logger.info(f"Got context from thread: workspace_id={workspace_id}, user_id={user_id}")
    except Exception as e:
        logger.debug(f"Could not get context from thread: {e}")
    
    # Method 2: Try to get from environment variables (fallback for testing)
    if not workspace_id or not user_id or not user_name:
        import os
        workspace_id = workspace_id or os.getenv('AGENT_WORKSPACE_ID', 'test_workspace')
        user_id = user_id or os.getenv('AGENT_USER_ID', 'test_user')
        user_name = user_name or os.getenv('AGENT_USER_NAME', 'Test User')
        logger.info(f"Using fallback context: workspace_id={workspace_id}, user_id={user_id}")
    
    # Call the actual create_task_tool with context
    return create_task_tool(
        action_description=action_description,
        task_type=task_type,
        task_name=task_name,
        epic_id=epic_id,
        parent_id=parent_id,
        description=description,
        priority=priority,
        status=status,
        assignee_name=assignee_name,
        start_date=start_date,
        due_date=due_date,
        workspace_id=workspace_id,
        user_id=user_id,
        user_name=user_name,
        expected_outcome=expected_outcome
    )
