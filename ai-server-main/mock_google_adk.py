# Mock Google ADK classes để có thể chạy server
from typing import List, Dict, Any, Optional, AsyncGenerator
from enum import Enum
import asyncio
import json
from datetime import datetime

class StreamingMode(Enum):
    SSE = "sse"
    WEBSOCKET = "websocket"

class Part:
    def __init__(self, text: str = None, uri: str = None, mime_type: str = None):
        self.text = text
        self.uri = uri
        self.mime_type = mime_type
    
    @classmethod
    def from_text(cls, text: str):
        return cls(text=text)
    
    @classmethod
    def from_uri(cls, uri: str, mime_type: str):
        return cls(uri=uri, mime_type=mime_type)

class Content:
    def __init__(self, role: str, parts: List[Part]):
        self.role = role
        self.parts = parts

class GenerateContentConfig:
    def __init__(self, temperature: float = 0.1, max_output_tokens: int = 64000):
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens

class LiteLlm:
    def __init__(self, model: str, api_key: str, api_base: str):
        self.model = model
        self.api_key = api_key
        self.api_base = api_base

class FunctionTool:
    def __init__(self, func):
        self.func = func
        self.name = func.__name__

class Agent:
    def __init__(self, name: str, description: str, instruction: str, tools: List, model, generate_content_config):
        self.name = name
        self.description = description
        self.instruction = instruction
        self.tools = tools
        self.model = model
        self.generate_content_config = generate_content_config

class RunConfig:
    def __init__(self, streaming_mode: StreamingMode, max_llm_calls: int = 150):
        self.streaming_mode = streaming_mode
        self.max_llm_calls = max_llm_calls

class Event:
    def __init__(self, content: Content):
        self.content = content

class Session:
    def __init__(self, session_id: str, user_id: str, app_name: str, state: Dict):
        self.session_id = session_id
        self.user_id = user_id
        self.app_name = app_name
        self.state = state

class DatabaseSessionService:
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.sessions = {}  # Mock storage
    
    async def create_session(self, app_name: str, user_id: str, session_id: str, state: Dict) -> Session:
        session = Session(session_id, user_id, app_name, state)
        self.sessions[session_id] = session
        return session
    
    async def get_session(self, app_name: str, user_id: str, session_id: str) -> Optional[Session]:
        return self.sessions.get(session_id)

class InMemoryMemoryService:
    def __init__(self):
        self.memories = []

class VertexAiMemoryBankService:
    def __init__(self, project: str, location: str, agent_engine_id: str):
        self.project = project
        self.location = location
        self.agent_engine_id = agent_engine_id

class Runner:
    def __init__(self, app_name: str, agent: Agent, session_service: DatabaseSessionService, memory_service):
        self.app_name = app_name
        self.agent = agent
        self.session_service = session_service
        self.memory_service = memory_service
    
    async def run_async(self, user_id: str, session_id: str, new_message: Content, run_config: RunConfig) -> AsyncGenerator[Event, None]:
        # Mock response - tạo phản hồi demo
        mock_responses = [
            "Xin chào! Tôi là FARAMEX Marketing Agent.",
            " Tôi có thể giúp bạn với các chiến lược marketing Facebook,",
            " tạo nội dung quảng cáo, và phân tích hiệu suất campaign.",
            " Bạn cần hỗ trợ gì hôm nay?"
        ]
        
        for response_part in mock_responses:
            await asyncio.sleep(0.1)  # Simulate streaming delay
            content = Content(role="assistant", parts=[Part.from_text(response_part)])
            yield Event(content)

# Mock modules structure
class MockGoogleAdk:
    class agents:
        class run_config:
            StreamingMode = StreamingMode
        
        Agent = Agent
        RunConfig = RunConfig
    
    class sessions:
        DatabaseSessionService = DatabaseSessionService
    
    class memory:
        InMemoryMemoryService = InMemoryMemoryService
        VertexAiMemoryBankService = VertexAiMemoryBankService
    
    class runners:
        Runner = Runner
    
    class tools:
        FunctionTool = FunctionTool
    
    class models:
        class lite_llm:
            LiteLlm = LiteLlm

class MockGoogleGenai:
    class types:
        Part = Part
        Content = Content
        GenerateContentConfig = GenerateContentConfig

# Inject mock modules
import sys
from types import ModuleType

# Only mock ADK and genai modules, not the main google module
google_adk_module = ModuleType('google.adk')
google_adk_agents_module = ModuleType('google.adk.agents')
google_adk_agents_run_config_module = ModuleType('google.adk.agents.run_config')
google_adk_sessions_module = ModuleType('google.adk.sessions')
google_adk_memory_module = ModuleType('google.adk.memory')
google_adk_runners_module = ModuleType('google.adk.runners')
google_adk_tools_module = ModuleType('google.adk.tools')
google_adk_models_module = ModuleType('google.adk.models')
google_adk_models_lite_llm_module = ModuleType('google.adk.models.lite_llm')
google_genai_module = ModuleType('google.genai')
google_genai_types_module = ModuleType('google.genai.types')

# Add classes to modules
google_adk_module.Agent = Agent
google_adk_agents_run_config_module.StreamingMode = StreamingMode
google_adk_agents_module.RunConfig = RunConfig
google_adk_sessions_module.DatabaseSessionService = DatabaseSessionService
google_adk_memory_module.InMemoryMemoryService = InMemoryMemoryService
google_adk_memory_module.VertexAiMemoryBankService = VertexAiMemoryBankService
google_adk_runners_module.Runner = Runner
google_adk_tools_module.FunctionTool = FunctionTool
google_adk_models_lite_llm_module.LiteLlm = LiteLlm
google_genai_types_module.Part = Part
google_genai_types_module.Content = Content
google_genai_types_module.GenerateContentConfig = GenerateContentConfig

# Register only ADK and genai modules
sys.modules['google.adk'] = google_adk_module
sys.modules['google.adk.agents'] = google_adk_agents_module
sys.modules['google.adk.agents.run_config'] = google_adk_agents_run_config_module
sys.modules['google.adk.sessions'] = google_adk_sessions_module
sys.modules['google.adk.memory'] = google_adk_memory_module
sys.modules['google.adk.runners'] = google_adk_runners_module
sys.modules['google.adk.tools'] = google_adk_tools_module
sys.modules['google.adk.models'] = google_adk_models_module
sys.modules['google.adk.models.lite_llm'] = google_adk_models_lite_llm_module
sys.modules['google.genai'] = google_genai_module
sys.modules['google.genai.types'] = google_genai_types_module
