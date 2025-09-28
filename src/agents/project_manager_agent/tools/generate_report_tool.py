"""
Generate Report Tool for Project Manager Agent
Comprehensive reporting with time-based filtering, assignee breakdowns, and alerts
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

def generate_report_tool(
    action_description: str,
    time_period: str = "this_week",  # "today", "this_week", "this_month", "all", "due_soon", "next_month"
    scope: str = "all",  # "all", "epic", "task", "subtask"
    include_assignee_breakdown: bool = True,
    include_alerts: bool = True,
    expected_outcome: str = "Report generated successfully"
) -> Dict[str, Any]:
    """
    Generate comprehensive project reports with time-based filtering and detailed breakdowns
    
    Args:
        action_description: Clear description of what you intend to do
        time_period: Time period for report ("today", "this_week", "this_month", "all", "due_soon", "next_month")
        scope: Scope of items to include ("all", "epic", "task", "subtask")
        include_assignee_breakdown: Whether to include assignee breakdown
        include_alerts: Whether to include due soon and overdue alerts
        expected_outcome: What you expect to achieve
    
    Returns:
        Dict containing comprehensive report with summary, breakdowns, and alerts
    """
    
    logger.info(f"[REPORT TOOL] generate_report_tool: {action_description}")
    logger.info(f"Parameters: time_period={time_period}, scope={scope}, assignee_breakdown={include_assignee_breakdown}")
    
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
        
        # 4. Fetch data from database using async wrapper
        all_items = []
        
        async def fetch_data():
            nonlocal all_items
            try:
                if time_period == "all":
                    # Fetch all items by type
                    items_to_fetch = []
                    if scope == "all":
                        items_to_fetch = ["Epic", "Task", "Sub_task"]
                    elif scope == "epic":
                        items_to_fetch = ["Epic"]
                    elif scope == "task":
                        items_to_fetch = ["Task"]
                    elif scope == "subtask":
                        items_to_fetch = ["Sub_task"]
                    
                    for item_type in items_to_fetch:
                        items = await epic_service.list_tasks_by_type(
                            workspace_id=workspace_id,
                            user_id=user_id,
                            type_filter=item_type
                        )
                        all_items.extend(items)
                else:
                    # Use time-based filtering
                    items = await epic_service.list_tasks_by_time_period(
                        workspace_id=workspace_id,
                        user_id=user_id,
                        time_period=time_period,
                        scope=("all" if scope == "all" else scope.title())
                    )
                    all_items.extend(items)
                
                logger.info(f"Fetched {len(all_items)} items for report")
            except Exception as e:
                logger.error(f"Error fetching data for report: {e}")
                raise
        
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
                "message": f"Failed to fetch data for report: {str(e)}",
                "action_description": action_description
            }
        
        # 5. Generate comprehensive report
        report = generate_comprehensive_report(
            all_items, 
            time_period, 
            scope, 
            include_assignee_breakdown, 
            include_alerts
        )
        
        # 6. Build response
        response = {
            "status": "success",
            "message": f"Report generated for {time_period} ({len(all_items)} items)",
            "workspace_id": workspace_id,
            "user_id": user_id,
            "user_name": user_name,
            "time_period": time_period,
            "scope": scope,
            "report": report,
            "action_description": action_description,
            "expected_outcome": expected_outcome
        }
        
        logger.info(f"Successfully generated report with {len(all_items)} items")
        return response
        
    except Exception as e:
        logger.error(f"Error in generate_report_tool: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to generate report: {str(e)}",
            "action_description": action_description,
            "error_details": str(e)
        }

def generate_comprehensive_report(
    items: List, 
    time_period: str, 
    scope: str, 
    include_assignee_breakdown: bool, 
    include_alerts: bool
) -> Dict[str, Any]:
    """Generate comprehensive report structure"""
    
    # 1. Summary statistics
    summary = {
        "total_items": len(items),
        "by_type": {
            "epics": count_by_type(items, "Epic"),
            "tasks": count_by_type(items, "Task"),
            "subtasks": count_by_type(items, "Sub_task")
        },
        "by_status": {
            "todo": count_by_status(items, "To do"),
            "in_progress": count_by_status(items, "Inprogress"),
            "done": count_by_status(items, "Done")
        },
        "by_priority": {
            "high": count_by_priority(items, "High"),
            "medium": count_by_priority(items, "Medium"),
            "low": count_by_priority(items, "Low")
        }
    }
    
    # 2. Time-based analysis
    time_analysis = {
        "due_soon": count_due_soon(items),
        "overdue": count_overdue(items),
        "completed_this_period": count_completed_this_period(items, time_period)
    }
    
    # 3. Assignee breakdown (if requested)
    assignee_breakdown = {}
    if include_assignee_breakdown:
        assignee_breakdown = group_by_assignee(items)
    
    # 4. Alerts (if requested)
    alerts = {}
    if include_alerts:
        alerts = {
            "due_soon": get_due_soon_tasks(items),
            "overdue": get_overdue_tasks(items),
            "high_priority_todo": get_high_priority_todo(items)
        }
    
    # 5. Recent activity
    recent_activity = get_recent_activity(items)
    
    return {
        "summary": summary,
        "time_analysis": time_analysis,
        "assignee_breakdown": assignee_breakdown,
        "alerts": alerts,
        "recent_activity": recent_activity,
        "generated_at": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "time_period": time_period,
        "scope": scope
    }

def count_by_type(items: List, item_type: str) -> int:
    """Count items by type"""
    return len([item for item in items if (hasattr(item.type, 'value') and item.type.value == item_type) or str(item.type) == item_type])

def count_by_status(items: List, status: str) -> int:
    """Count items by status"""
    return len([item for item in items if (hasattr(item.status, 'value') and item.status.value == status) or str(item.status) == status])

def count_by_priority(items: List, priority: str) -> int:
    """Count items by priority"""
    return len([item for item in items if (hasattr(item.priority, 'value') and item.priority.value == priority) or str(item.priority) == priority])

def count_due_soon(items: List) -> int:
    """Count tasks due within 3 days"""
    today = datetime.now().date()
    due_soon_count = 0
    
    for item in items:
        due_date_str = item.due_date or item.start_date
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, '%d/%m/%Y').date()
                if today <= due_date <= today + timedelta(days=3):
                    due_soon_count += 1
            except:
                continue
    
    return due_soon_count

def count_overdue(items: List) -> int:
    """Count overdue tasks"""
    today = datetime.now().date()
    overdue_count = 0
    
    for item in items:
        due_date_str = item.due_date or item.start_date
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, '%d/%m/%Y').date()
                if due_date < today and (hasattr(item.status, 'value') and item.status.value != "Done") or str(item.status) != "Done":
                    overdue_count += 1
            except:
                continue
    
    return overdue_count

def count_completed_this_period(items: List, time_period: str) -> int:
    """Count completed items in the current period"""
    completed_count = 0
    today = datetime.now().date()
    
    for item in items:
        if (hasattr(item.status, 'value') and item.status.value == "Done") or str(item.status) == "Done":
            # Check if completed within the period
            update_date_str = item.update_at
            if update_date_str:
                try:
                    update_date = datetime.strptime(update_date_str, '%d/%m/%Y %H:%M:%S').date()
                    if is_within_period(update_date, today, time_period):
                        completed_count += 1
                except:
                    continue
    
    return completed_count

def is_within_period(date: datetime.date, today: datetime.date, period: str) -> bool:
    """Check if date is within the specified period"""
    if period == "today":
        return date == today
    elif period == "this_week":
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        return week_start <= date <= week_end
    elif period == "this_month":
        return date.year == today.year and date.month == today.month
    else:
        return True  # For "all" or other periods

def group_by_assignee(items: List) -> Dict[str, Any]:
    """Group items by assignee"""
    assignee_groups = {}
    
    for item in items:
        assignee = item.assignee_name or "Unassigned"
        
        if assignee not in assignee_groups:
            assignee_groups[assignee] = {
                "total_tasks": 0,
                "by_status": {"To do": 0, "Inprogress": 0, "Done": 0},
                "by_priority": {"High": 0, "Medium": 0, "Low": 0},
                "tasks": []
            }
        
        assignee_groups[assignee]["total_tasks"] += 1
        
        # Count by status
        status = item.status.value if hasattr(item.status, 'value') else str(item.status)
        if status in assignee_groups[assignee]["by_status"]:
            assignee_groups[assignee]["by_status"][status] += 1
        
        # Count by priority
        priority = item.priority.value if hasattr(item.priority, 'value') else str(item.priority)
        if priority in assignee_groups[assignee]["by_priority"]:
            assignee_groups[assignee]["by_priority"][priority] += 1
        
        # Add task details
        task_info = {
            "id": item.epic_id or item.task_id or item.sub_task_id,
            "name": item.epic_name or item.task_name or item.sub_task_name,
            "type": item.type.value if hasattr(item.type, 'value') else str(item.type),
            "status": status,
            "priority": priority,
            "due_date": item.due_date,
            "start_date": item.start_date
        }
        assignee_groups[assignee]["tasks"].append(task_info)
    
    return assignee_groups

def get_due_soon_tasks(items: List) -> List[Dict]:
    """Get tasks due within 3 days"""
    today = datetime.now().date()
    due_soon_tasks = []
    
    for item in items:
        due_date_str = item.due_date or item.start_date
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, '%d/%m/%Y').date()
                if today <= due_date <= today + timedelta(days=3):
                    due_soon_tasks.append({
                        "id": item.epic_id or item.task_id or item.sub_task_id,
                        "name": item.epic_name or item.task_name or item.sub_task_name,
                        "type": item.type.value if hasattr(item.type, 'value') else str(item.type),
                        "assignee": item.assignee_name or "Unassigned",
                        "due_date": due_date_str,
                        "priority": item.priority.value if hasattr(item.priority, 'value') else str(item.priority),
                        "status": item.status.value if hasattr(item.status, 'value') else str(item.status)
                    })
            except:
                continue
    
    return due_soon_tasks

def get_overdue_tasks(items: List) -> List[Dict]:
    """Get overdue tasks"""
    today = datetime.now().date()
    overdue_tasks = []
    
    for item in items:
        due_date_str = item.due_date or item.start_date
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, '%d/%m/%Y').date()
                status = item.status.value if hasattr(item.status, 'value') else str(item.status)
                if due_date < today and status != "Done":
                    overdue_tasks.append({
                        "id": item.epic_id or item.task_id or item.sub_task_id,
                        "name": item.epic_name or item.task_name or item.sub_task_name,
                        "type": item.type.value if hasattr(item.type, 'value') else str(item.type),
                        "assignee": item.assignee_name or "Unassigned",
                        "due_date": due_date_str,
                        "priority": item.priority.value if hasattr(item.priority, 'value') else str(item.priority),
                        "status": status,
                        "days_overdue": (today - due_date).days
                    })
            except:
                continue
    
    return overdue_tasks

def get_high_priority_todo(items: List) -> List[Dict]:
    """Get high priority todo tasks"""
    high_priority_todos = []
    
    for item in items:
        priority = item.priority.value if hasattr(item.priority, 'value') else str(item.priority)
        status = item.status.value if hasattr(item.status, 'value') else str(item.status)
        
        if priority == "High" and status == "To do":
            high_priority_todos.append({
                "id": item.epic_id or item.task_id or item.sub_task_id,
                "name": item.epic_name or item.task_name or item.sub_task_name,
                "type": item.type.value if hasattr(item.type, 'value') else str(item.type),
                "assignee": item.assignee_name or "Unassigned",
                "due_date": item.due_date,
                "start_date": item.start_date
            })
    
    return high_priority_todos

def get_recent_activity(items: List) -> List[Dict]:
    """Get recent activity (last 10 updated items)"""
    recent_items = []
    
    # Sort by update_at (most recent first)
    sorted_items = sorted(items, key=lambda x: x.update_at or "01/01/2024 00:00:00", reverse=True)
    
    for item in sorted_items[:10]:  # Last 10 items
        recent_items.append({
            "id": item.epic_id or item.task_id or item.sub_task_id,
            "name": item.epic_name or item.task_name or item.sub_task_name,
            "type": item.type.value if hasattr(item.type, 'value') else str(item.type),
            "status": item.status.value if hasattr(item.status, 'value') else str(item.status),
            "assignee": item.assignee_name or "Unassigned",
            "updated_at": item.update_at
        })
    
    return recent_items
