from fastapi import APIRouter, Request, Depends, FastAPI, HTTPException, File, UploadFile, Form, Path
from fastapi.responses import StreamingResponse
from google.adk.agents.run_config import StreamingMode
from src.api.routers.generator import send_message
from google.adk.sessions import DatabaseSessionService
from google.adk.agents import RunConfig
from google.adk.runners import Runner
from src.agents import AGENT_MAPPING
from google.genai import types
from src.api.schemas.chats import MessageInput
from src.api.logging.logger import get_logger
from configs import get_database_url
from src.memory.memory_bank import vertexai_memorybank_settings
from src.api.authentication.dependencies import get_current_active_user

import requests
logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1", tags=["Superb AI Service Chat"])

DB_URL = get_database_url()
session_service = DatabaseSessionService(db_url=DB_URL)

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


    runner = Runner(
        app_name=agent.name,
        agent=agent,
        session_service=session_service,
        memory_service=memory_service,
        artifact_service=artifact_service,
    )

    run_config = RunConfig(
        streaming_mode=StreamingMode.SSE,
        max_llm_calls=150,
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