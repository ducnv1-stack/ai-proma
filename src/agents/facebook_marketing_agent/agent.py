from typing import Any, Dict, Optional
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from src.callbacks.tool_configs import before_tool_call, after_tool_call
from google.genai import types
from src.prompts.components.facebook_marketing.system_message import get_system_message
from src.tools.common.generate_image import generate_image_tool
from configs import get_ai_settings

ai_settings = get_ai_settings()

def search_tool(action_description: str, query: str, expected_outcome: str = "Search results") -> Dict[str, Any]:
    """Search for information on the internet
    Args:
        action_description: Clear description of what you intend to do
        query: The search query string
        expected_outcome: What you expect to achieve
    """
    print(f"\n[TOOL EXECUTED] search_tool with query: {query}")
    return {
        "status": "success",
        "result": f"Search results for: {query}",
        "data": f"Found relevant information about {query}"
    }

def calculator_tool(action_description: str, expression: str, expected_outcome: str = "Mathematical result") -> Dict[str, Any]:
    """Calculate mathematical expressions
    Args:
        action_description: Clear description of what you intend to do
        expression: The mathematical expression to calculate
        expected_outcome: What you expect to achieve
    """
    print(f"\n[TOOL EXECUTED] calculator_tool with expression: {expression}")
    try:
        result = eval(expression)
        return {
            "status": "success",
            "result": f"Result: {result}",
            "calculation": result
        }
    except Exception as e:
        return {
            "status": "error",
            "result": "Invalid expression",
            "error": str(e)
        }

def weather_tool(action_description: str, location: str, expected_outcome: str = "Weather information") -> Dict[str, Any]:
    """Get weather information for a location
    Args:
        action_description: Clear description of what you intend to do
        location: The location to get weather for
        expected_outcome: What you expect to achieve
    """
    print(f"\n[TOOL EXECUTED] weather_tool with location: {location}")
    return {
        "status": "success",
        "result": f"Weather in {location}: 25°C, sunny",
        "temperature": "25°C",
        "condition": "sunny"
    }

facebook_marketing_agent = LlmAgent(
    name="facebook_marketing_agent",
    description="Famarex – Nhân viên Marketing Facebook xuất sắc.",
    instruction=get_system_message(),
    tools=[generate_image_tool, search_tool, calculator_tool, weather_tool],
    model=LiteLlm(
        model=ai_settings.mkt_agent_model,
        api_key=ai_settings.openrouter_api_key,
        api_base=ai_settings.openrouter_base_url,
        supports_vision=True
    ),
    generate_content_config=types.GenerateContentConfig(
        temperature=ai_settings.temperature,
        max_output_tokens=ai_settings.max_output_tokens,
    ),
    before_tool_callback=before_tool_call,
    after_tool_callback=after_tool_call
    # planner=BuiltInPlanner(
    #     thinking_config=types.ThinkingConfig(
    #         include_thoughts=True,
    #         thinking_budget=1024,
    #     )
    # ),
)