from google.adk import Agent
from google.adk.models.lite_llm import LiteLlm
from google.genai import types
from src.prompts.components.facebook_marketing.system_message import get_system_message
from src.tools.common.generate_image import generate_image_tool
from configs import get_ai_settings

ai_settings = get_ai_settings()

project_manager_agent = Agent(
    name="project_manager_agent",
    description="Proma – Chuyên gia quản lý dự án xuất sắc.",
    instruction=get_system_message(),
    tools=[generate_image_tool],
    model=LiteLlm(
        model=ai_settings.mkt_agent_model,
        api_key=ai_settings.openrouter_api_key,
        api_base=ai_settings.openrouter_base_url
    ),
    generate_content_config=types.GenerateContentConfig(
        temperature=ai_settings.temperature,
        max_output_tokens=ai_settings.max_output_tokens,
    )
)