"""
Project Manager Agent - PROMA
Expert AI agent for project and task management
"""

from typing import Any, Dict, Optional
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from src.callbacks.tool_configs import before_tool_call, after_tool_call
from google.genai import types
from src.prompts.components.project_manager.system_message import get_system_message
from configs import get_ai_settings

# Import Project Manager tools
from src.agents.project_manager_agent.tools.context_aware_create_task import context_aware_create_task_tool
# from src.agents.project_manager_agent.tools.list_tasks_tool import list_tasks_tool
from src.agents.project_manager_agent.tools.list_tasks_tool import smart_list_tasks_tool
from src.agents.project_manager_agent.tools.update_task_tool import update_task_tool
from src.agents.project_manager_agent.tools.delete_task_tool import delete_task_by_name_tool
from src.agents.project_manager_agent.tools.generate_report_tool import generate_report_tool

# Get AI settings for model configuration
ai_settings = get_ai_settings()

# Additional utility tools for project management
def get_team_members_tool(
    action_description: str, 
    workspace_filter: Optional[str] = None,
    expected_outcome: str = "Team members retrieved"
) -> Dict[str, Any]:
    """Get list of team members for assignment purposes
    
    Args:
        action_description: Clear description of what you intend to do
        workspace_filter: Optional workspace filter
        expected_outcome: What you expect to achieve
    """
    print(f"\n[TOOL EXECUTED] get_team_members_tool: {action_description}")
    
    # Simulate team members data (in real implementation, this would query member_service)
    return {
        "status": "success",
        "message": "Team members retrieved successfully",
        "team_members": [
            {"member_id": "member-001", "name": "John Doe", "team": "Development", "email": "john@example.com"},
            {"member_id": "member-002", "name": "Jane Smith", "team": "Design", "email": "jane@example.com"},
            {"member_id": "member-003", "name": "Mike Johnson", "team": "QA", "email": "mike@example.com"},
            {"member_id": "member-004", "name": "Sarah Wilson", "team": "Marketing", "email": "sarah@example.com"}
        ],
        "total_count": 4,
        "action_description": action_description,
        "note": "This tool requires integration with member_service for actual data"
    }

def analyze_workload_tool(
    action_description: str,
    time_period: str = "this_week",  # "today", "this_week", "this_month"
    team_member: Optional[str] = None,
    expected_outcome: str = "Workload analysis completed"
) -> Dict[str, Any]:
    """Analyze team workload and capacity
    
    Args:
        action_description: Clear description of what you intend to do
        time_period: Time period for analysis ("today", "this_week", "this_month")
        team_member: Specific team member to analyze (optional)
        expected_outcome: What you expect to achieve
    """
    print(f"\n[TOOL EXECUTED] analyze_workload_tool: {action_description}")
    
    # Simulate workload analysis (in real implementation, this would analyze task assignments)
    return {
        "status": "success",
        "message": f"Workload analysis completed for {time_period}",
        "time_period": time_period,
        "analysis": {
            "total_tasks": 15,
            "completed_tasks": 8,
            "in_progress_tasks": 5,
            "pending_tasks": 2,
            "overdue_tasks": 1,
            "team_utilization": "75%",
            "bottlenecks": ["Design team overloaded", "QA capacity available"]
        },
        "recommendations": [
            "Consider redistributing design tasks",
            "Utilize available QA capacity for early testing",
            "Review overdue task priorities"
        ],
        "action_description": action_description,
        "note": "This tool requires integration with task and member services for actual analysis"
    }

def project_timeline_tool(
    action_description: str,
    epic_name: Optional[str] = None,
    include_dependencies: bool = True,
    expected_outcome: str = "Project timeline generated"
) -> Dict[str, Any]:
    """Generate project timeline and milestone tracking
    
    Args:
        action_description: Clear description of what you intend to do
        epic_name: Specific epic to analyze (optional, if None analyzes all active epics)
        include_dependencies: Whether to include task dependencies in timeline
        expected_outcome: What you expect to achieve
    """
    print(f"\n[TOOL EXECUTED] project_timeline_tool: {action_description}")
    
    # Simulate timeline generation (in real implementation, this would analyze task dates and dependencies)
    return {
        "status": "success",
        "message": "Project timeline generated successfully",
        "epic_name": epic_name or "All Active Epics",
        "timeline": {
            "start_date": "01/10/2024",
            "end_date": "30/11/2024", 
            "duration_days": 60,
            "milestones": [
                {"name": "Design Phase Complete", "date": "15/10/2024", "status": "on_track"},
                {"name": "Development Phase Start", "date": "16/10/2024", "status": "on_track"},
                {"name": "Testing Phase Start", "date": "01/11/2024", "status": "at_risk"},
                {"name": "Launch Preparation", "date": "20/11/2024", "status": "planned"}
            ],
            "critical_path": ["Epic Planning", "Design", "Core Development", "Integration Testing", "Launch"],
            "risks": ["Design approval delays", "Resource availability in November"]
        },
        "include_dependencies": include_dependencies,
        "action_description": action_description,
        "note": "This tool requires integration with task service for actual timeline calculation"
    }

# Create the Project Manager Agent
project_manager_agent = LlmAgent(
    name="project_manager_agent",
    description="PROMA - Expert Project Manager AI specializing in Epic, Task, and Sub_task management with intelligent memory and team coordination.",
    instruction=get_system_message(),
    tools=[
        # Core task management tools
        context_aware_create_task_tool,
        # list_tasks_tool, 
        smart_list_tasks_tool,
        update_task_tool,
        delete_task_by_name_tool,
        
        # Reporting and analysis tools
        generate_report_tool,
        
        # Team and project analysis tools
        get_team_members_tool,
        analyze_workload_tool,
        project_timeline_tool
    ],
    model=LiteLlm(
        model=ai_settings.proma_agent_model,  # Uses PROMA_AGENT_MODEL from .env
        api_key=ai_settings.openrouter_api_key,
        api_base=ai_settings.openrouter_base_url,
        supports_vision=True  # Enable vision capabilities for processing charts/diagrams
    ),
    generate_content_config=types.GenerateContentConfig(
        temperature=ai_settings.temperature,  # Use same temperature as other agents
        max_output_tokens=ai_settings.max_output_tokens,  # Use same token limit
    ),
    before_tool_callback=before_tool_call,
    after_tool_callback=after_tool_call
    # Memory integration will be added when memory system is implemented
    # planner=BuiltInPlanner(
    #     thinking_config=types.ThinkingConfig(
    #         include_thoughts=True,
    #         thinking_budget=1024,
    #     )
    # ),
)
