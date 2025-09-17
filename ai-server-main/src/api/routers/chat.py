from fastapi import APIRouter, Request, Depends, FastAPI, HTTPException, File, UploadFile, Form
from fastapi.responses import StreamingResponse
from google.adk.agents.run_config import StreamingMode
from src.api.routers.generator import send_message
from google.adk.sessions import DatabaseSessionService
from google.adk.agents import RunConfig
from google.adk.memory import InMemoryMemoryService, VertexAiMemoryBankService
from google.adk.runners import Runner
from src.agents import AGENT_MAPPING
from google.genai import types
import os
import uuid
from datetime import datetime
from src.api.schemas.chats import MessageInput
from src.api.logging.logger import get_logger
from configs import get_database_url
from src.memory.memory_bank import vertexai_memorybank_settings
from src.api.authentication.dependencies import get_current_active_user

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1", tags=["Superb AI Service Chat"])

DB_URL = get_database_url()
session_service = DatabaseSessionService(db_url=DB_URL)


@router.post("/chat")
async def chat(
        data: MessageInput,
        current_user: dict = Depends(get_current_active_user)
):
    token_data = current_user.get("token_data", {})
    user_data = current_user.get("user", {})

    user_id = token_data.get("user_id") or user_data.get("id") or user_data.get("user_id")
    if not user_id:
        logger.error("User ID not found in token or user data")
        raise HTTPException(status_code=401, detail="User ID not found in token or user data")

    session_id = token_data.get("session_id")
    workspace_id = token_data.get("workspace_id")
    agent_name = token_data.get("agent_id")

    if not session_id:
        logger.error("Session ID not found in token")
        raise HTTPException(status_code=401, detail="Session ID not found in token")

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

    # Process message parts
    parts = [types.Part.from_text(text=data.message)]

    if data.images and len(data.images) > 0:
        for image_url in data.images:
            if image_url and image_url != "string":
                try:
                    image_part = types.Part.from_uri(uri=image_url, mime_type="image/jpeg")
                    parts.append(image_part)
                except Exception as e:
                    logger.error(f"Failed to process image {image_url}: {e}")

    user_message = types.Content(role="user", parts=parts)

    memory_service = VertexAiMemoryBankService(
        project=vertexai_memorybank_settings.vertex_project_id,
        location=vertexai_memorybank_settings.vertex_location,
        agent_engine_id=vertexai_memorybank_settings.vertex_agent_engine_id
    )

    runner = Runner(
        app_name=agent.name,
        agent=agent,
        session_service=session_service,
        memory_service=memory_service
    )

    run_config = RunConfig(
        streaming_mode=StreamingMode.SSE,
        max_llm_calls=150
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