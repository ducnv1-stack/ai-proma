from src.prompts.components import get_base_instruction
from src.prompts.components.facebook_marketing.behaviour import get_behaviour
from src.prompts.components.facebook_marketing.missions import get_missions
from src.prompts.components.facebook_marketing.rules import get_rules
from src.prompts.components.facebook_marketing.instruct_tool_use import get_instruct_tool_use
from src.prompts.components.roles import RoleManager, RoleType

role_manager = RoleManager()

def get_system_message():
    return f"""
{role_manager.get_role(RoleType.FACEBOOK_MARKETING)}

====

{get_missions()}

====

{get_instruct_tool_use()}

====

{get_behaviour()}

====

{get_rules()}

====

{get_base_instruction()}
"""