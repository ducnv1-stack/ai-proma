from fastapi import APIRouter, Request, Depends, FastAPI, HTTPException, File, UploadFile, Form, Path
from fastapi.responses import StreamingResponse
from google.adk.agents.run_config import StreamingMode
from src.api.routers.generator import send_message
from google.adk.sessions import DatabaseSessionService
from google.adk.agents import RunConfig
from google.adk.runners import Runner
from src.agents import AGENT_MAPPING
from google.genai import types
from src.api.schemas.chats import MessageInput, UnifiedChatRequest, UnifiedChatResponse
from src.api.logging.logger import get_logger
from configs import get_database_url
from src.memory.memory_bank import vertexai_memorybank_settings
from src.api.authentication.dependencies import get_current_active_user
from google.adk.memory import InMemoryMemoryService
from src.api.schemas.sessions import CreateSessionRequest

import requests
import uuid
import datetime
import threading
logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1", tags=["Superb AI Service Chat"])

DB_URL = get_database_url()
session_service = DatabaseSessionService(db_url=DB_URL)

# Helper functions for unified chat endpoint
async def create_new_session_internal(agent_id: str, user_id: str, workspace_id: str) -> dict:
    """Create a new session internally"""
    try:
        session_id = str(uuid.uuid4())
        
        # Create session using session service
        session = await session_service.create_session(
            app_name=agent_id,
            user_id=user_id,
            session_id=session_id,
            state={
                "user:workspace_id": workspace_id,
                "agent_id": agent_id,
                "user_id": user_id
            }
        )
        
        logger.info(f"Created new session: {session_id} for agent: {agent_id}")
        return {
            "session_id": session_id,
            "agent_id": agent_id,
            "workspace_id": workspace_id,
            "created_at": None,
            #import datetime

            # Trong function create_new_session_internal
            "created_at": datetime.datetime.now().isoformat()
            # "created_at": session.create_time.isoformat() if session.create_time else None
        }
    except Exception as e:
        logger.error(f"Failed to create session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")

async def validate_session_internal(session_id: str, agent_id: str, workspace_id: str, user_id: str) -> dict:
    """Validate existing session internally"""
    try:
        # Check empty session_id early to avoid DB call
        if not session_id or (isinstance(session_id, str) and session_id.strip() == ""):
            raise HTTPException(
                status_code=400,
                detail="Session ID cannot be empty"
            )
        current_session = await session_service.get_session(
            app_name=agent_id,
            user_id=user_id,
            session_id=session_id,
        )

        if current_session is None:
            logger.error(f"Session {session_id} not found")
            raise HTTPException(
                status_code=404,
                detail=f"Session {session_id} not found. Please create a new session first."
            )

        # Validate workspace
        session_workspace_id = current_session.state.get("user:workspace_id")
        if session_workspace_id != workspace_id:
            logger.error(f"Workspace mismatch for session {session_id}")
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. Session belongs to different workspace."
            )

        # Validate agent
        session_agent_id = current_session.state.get("agent_id")
        if session_agent_id != agent_id:
            logger.error(f"Agent mismatch for session {session_id}")
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. Session belongs to different agent."
            )

        logger.info(f"Session validation successful for session {session_id}")
        return {
            "session_id": session_id,
            "agent_id": agent_id,
            "workspace_id": workspace_id,
            "validated": True
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to validate session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to validate session: {str(e)}")

@router.post("/chat/{session_id}")
async def chat(
        data: MessageInput,
        session_id: str = Path(..., description="Session ID to get events for"),
        current_user: dict = Depends(get_current_active_user)
):
    token_data = current_user.get("token_data", {})
    user_data = current_user.get("user", {})

    user_id = token_data.get("user_id") or user_data.get("id") or user_data.get("user_id")
    if not user_id:
        logger.error("User ID not found in token or user data")
        raise HTTPException(status_code=401, detail="User ID not found in token or user data")

    workspace_id = token_data.get("workspace_id")
    agent_name = token_data.get("agent_id")

    if not session_id:
        logger.error("Session ID not found")
        raise HTTPException(status_code=401, detail="Session ID not found")

    if not workspace_id:
        logger.error("Workspace ID not found in token")
        raise HTTPException(status_code=401, detail="Workspace ID not found in token")

    if not agent_name:
        logger.error("Agent ID not found in token")
        raise HTTPException(status_code=401, detail="Agent ID not found in token")

    logger.info(
        f"Processing request with token data: user_id={user_id}, session_id={session_id}, workspace_id={workspace_id}, agent_id={agent_name}")

    if agent_name not in AGENT_MAPPING:
        logger.error(f"Agent {agent_name} not found in AGENT_MAPPING")
        raise HTTPException(status_code=404, detail=f"Agent {agent_name} not found")

    logger.info(
        f"User {user_id} starts chatting with Agent {agent_name}, workspace {workspace_id}, session {session_id}")

    agent = AGENT_MAPPING[agent_name]

    current_session = None
    try:
        current_session = await session_service.get_session(
            app_name=agent.name,
            user_id=user_id,
            session_id=session_id,
        )

        if current_session is None:
            logger.error(f"Session {session_id} not found in database for user {user_id}")
            raise HTTPException(
                status_code=404,
                detail=f"Session {session_id} not found. Please create a new session first."
            )

        session_workspace_id = current_session.state.get("user:workspace_id")
        if session_workspace_id != workspace_id:
            logger.error(
                f"Workspace mismatch for session {session_id}. "
                f"Expected: {workspace_id}, Found: {session_workspace_id}"
            )
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. Session belongs to different workspace."
            )

        session_agent_id = current_session.state.get("agent_id")
        if session_agent_id != agent_name:
            logger.error(
                f"Agent mismatch for session {session_id}. "
                f"Expected: {agent_name}, Found: {session_agent_id}"
            )
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. Session belongs to different agent."
            )

        logger.info(f"Session validation successful for session {session_id}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve session for session_id='{session_id}' "
                     f"and user_id='{user_id}': {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to validate session. Please try again."
        )
    image_part = types.Part()

    if data.images and len(data.images) > 0:
        for image_url in data.images:
            if image_url:
                try:
                    res = requests.get(image_url)
                    res.raise_for_status()

                    image_bytes = res.content
                    mime_type = res.headers.get('Content-Type', 'image/png')
                    image_part = types.Part.from_bytes(
                        data=image_bytes,
                        mime_type=mime_type
                    )
                except Exception as e:
                    logger.error(f"Failed to process image {image_url}: {e}")

    text_part = types.Part.from_text(text=data.message)
    print(text_part, image_part)
    user_message = types.Content(role="user", parts=[text_part, image_part])
    print(user_message)

    # Use VertexAI Memory Bank if available, otherwise use InMemory
    if (vertexai_memorybank_settings.vertex_project_id and 
        vertexai_memorybank_settings.vertex_agent_engine_id):
        try:
            memory_service = VertexAiMemoryBankService(
                project=vertexai_memorybank_settings.vertex_project_id,
                location=vertexai_memorybank_settings.vertex_location,
                agent_engine_id=vertexai_memorybank_settings.vertex_agent_engine_id
            )
        except Exception as e:
            logger.warning(f"Failed to initialize VertexAI Memory Bank: {e}")
            memory_service = InMemoryMemoryService()
    else:
        logger.info("Using InMemory Memory Service (VertexAI not configured)")
        memory_service = InMemoryMemoryService()

    from src.custom.db_artifact_service import CustomDatabaseArtifactService
    artifact_service = CustomDatabaseArtifactService(
        db_url=DB_URL,
        user_id=user_id,
        workspace_id=workspace_id,
        agent_id=agent_name,
        session_id=session_id
    )

    # Set context for tools (thread-local storage) - for old endpoint too
    context = {
        'workspace_id': workspace_id,
        'user_id': user_id,
        'user_name': user_data.get('user_name') or f"User_{user_id}",
        'session_id': session_id,
        'agent_id': agent_name
    }
    threading.current_thread().agent_context = context
    logger.info(f"Set agent context (old endpoint): {context}")

    runner = Runner(
        app_name=agent.name,
        agent=agent,
        session_service=session_service,
        memory_service=memory_service,
        artifact_service=artifact_service,
    )

    run_config = RunConfig(
        streaming_mode=StreamingMode.SSE,
        max_llm_calls=50,
        save_input_blobs_as_artifacts=True
    )

    events = runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=user_message,
        run_config=run_config
    )

    async def async_generator():
        async for content in send_message(events=events):
            yield content

    return StreamingResponse(async_generator(), media_type="text/event-stream")


@router.post("/chat")
async def unified_chat(
    data: UnifiedChatRequest,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Unified chat endpoint with automatic session management
    - If session_id is None: creates new session
    - If session_id is provided: validates and uses existing session
    """
    token_data = current_user.get("token_data", {})
    user_data = current_user.get("user", {})

    # Extract user info from JWT
    user_id = token_data.get("user_id") or user_data.get("id") or user_data.get("user_id")
    if not user_id:
        logger.error("User ID not found in token")
        raise HTTPException(status_code=401, detail="User ID not found in token")

    workspace_id = token_data.get("workspace_id")
    if not workspace_id:
        logger.error("Workspace ID not found in token")
        raise HTTPException(status_code=401, detail="Workspace ID not found in token")
    # Extract user_name from token or user_data  
    user_name = token_data.get("user_name") or user_data.get("user_name") or user_data.get("name") or f"User_{user_id}"
    # Validate agent exists
    if data.agent_id not in AGENT_MAPPING:
        logger.error(f"Agent {data.agent_id} not found in AGENT_MAPPING")
        raise HTTPException(status_code=404, detail=f"Agent {data.agent_id} not found")

    logger.info(f"Processing unified chat request: user_id={user_id}, agent_id={data.agent_id}, session_id={data.session_id}")

    created_session = False
    session_id = data.session_id

    # Handle session logic
    if not session_id or (isinstance(session_id, str) and session_id.strip() == ""):
        # Create new session
        logger.info(f"Creating new session for agent: {data.agent_id}")
        session_info = await create_new_session_internal(
            agent_id=data.agent_id,
            user_id=user_id,
            workspace_id=workspace_id
        )
        session_id = session_info["session_id"]
        created_session = True
        logger.info(f"New session created: {session_id}")
    else:
        # Validate existing session
        logger.info(f"Validating existing session: {session_id}")
        await validate_session_internal(session_id, data.agent_id, workspace_id, user_id)
        logger.info(f"Session validation successful: {session_id}")

    # Get agent
    agent = AGENT_MAPPING[data.agent_id]

    # Prepare message parts (reuse existing logic)
    image_part = types.Part()
    if data.images and len(data.images) > 0:
        for image_url in data.images:
            if image_url:
                try:
                    res = requests.get(image_url)
                    res.raise_for_status()
                    image_part = types.Part.from_bytes(
                        data=res.content,
                        mime_type=res.headers.get("content-type", "image/jpeg")
                    )
                    break
                except Exception as e:
                    logger.warning(f"Failed to load image from {image_url}: {e}")

    text_part = types.Part.from_text(text=data.message)
    user_message = types.Content(role="user", parts=[text_part, image_part])

    # Use InMemory Memory Service (simple and reliable)
    logger.info("Using InMemory Memory Service")
    memory_service = InMemoryMemoryService()

    # Setup artifact service
    from src.custom.db_artifact_service import CustomDatabaseArtifactService
    artifact_service = CustomDatabaseArtifactService(
        db_url=DB_URL,
        user_id=user_id,
        workspace_id=workspace_id,
        agent_id=data.agent_id,
        session_id=session_id
    )

    # Set context for tools (thread-local storage)
    context = {
        'workspace_id': workspace_id,
        'user_id': user_id,
        'user_name': user_name or f"User_{user_id}",
        'session_id': session_id,
        'agent_id': data.agent_id
    }
    threading.current_thread().agent_context = context
    logger.info(f"Set agent context: {context}")

    # Setup runner
    runner = Runner(
        app_name=agent.name,
        agent=agent,
        session_service=session_service,
        memory_service=memory_service,
        artifact_service=artifact_service,
    )

    run_config = RunConfig(
        streaming_mode=StreamingMode.SSE,
        max_llm_calls=50,
        save_input_blobs_as_artifacts=True
    )

    # Run the agent
    events = runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=user_message,
        run_config=run_config
    )

    # Return streaming response with session info in headers
    async def async_generator():
        # First, yield session info as SSE event
        session_info = {
            "session_id": session_id,
            "agent_id": data.agent_id,
            "created_session": created_session,
            "message": data.message
        }
        yield f"data: {{'type': 'session_info', 'data': {session_info}}}\n\n"
        
        # Then yield agent responses
        async for content in send_message(events=events):
            yield content

    response = StreamingResponse(async_generator(), media_type="text/event-stream")
    
    # Add session info to response headers
    response.headers["X-Session-ID"] = session_id
    response.headers["X-Agent-ID"] = data.agent_id
    response.headers["X-Created-Session"] = str(created_session)
    
    return response