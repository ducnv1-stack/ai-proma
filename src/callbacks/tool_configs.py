import logging
from typing import Optional, Dict, Any
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.base_tool import BaseTool

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

def before_tool_call(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext
) -> Optional[Dict]:
    """Log befor call ."""
    tool_name = getattr(tool, "name", "unknown")
    action_description = args.get("action_description", f"Executing {tool_name}")
    expected_outcome = args.get("expected_outcome", "Tool execution result")


    logger.info(
        f"[BEFORE] Tool: {tool_name} | "
        f"Action: {action_description} | "
        f"Expected: {expected_outcome} | "
        f"Agent: {tool_context.agent_name}"
    )

    return None


def after_tool_call(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext, tool_response: Dict[str, Any]
) -> Optional[Dict]:
    """Log after call"""
    tool_name = getattr(tool, "name", "unknown")
    success = not ("error" in str(tool_response).lower())
    logger.info(
        f"[AFTER] status: {success} Tool: {tool_name} | "
        f"Response: {tool_response} | "
        f"Agent: {tool_context.agent_name}"
    )

    return None
