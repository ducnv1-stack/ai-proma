from src.prompts.components.fallbacks import get_fallbacks
from src.prompts.components.language import get_language
from src.prompts.components.user_custom_instruction import get_user_custom_instruction

def get_base_instruction():
    return f"""
{get_user_custom_instruction()}

====

{get_fallbacks()}

====

{get_language()}
"""