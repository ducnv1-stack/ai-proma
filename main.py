from fastapi import FastAPI
import uvicorn
from src.api.routers.chat import router as chat_router
from src.api.routers.agents import agents_router
from src.api.routers.session import router as session_router
from src.api.routers.auth import router as auth_router
from src.api.routers.epics import router as epics_router
from src.api.routers.members import router as members_router
# Removed database import since we're using direct connections

from contextlib import asynccontextmanager
from configs import get_settings, get_server_settings
import logging

settings = get_settings()
server_settings = get_server_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"Starting {server_settings.app_name}...")
    print("Using direct database connections (no pool)")
    yield
    
    print(f"Shutting down {server_settings.app_name}...")
    print("No database pool to disconnect")

app = FastAPI(
    title=server_settings.app_name,
    description=server_settings.app_description,
    version=server_settings.app_version,
    docs_url=server_settings.docs_url,
    redoc_url=server_settings.redoc_url,
    root_path="",
    lifespan=lifespan
)

try:
    origins = server_settings.cors_origins
    app.include_router(auth_router, tags=['Authentication'])
    app.include_router(chat_router, tags=['Main Router'])
    app.include_router(agents_router, tags=['Agents'])
    app.include_router(session_router, tags=['Session'])
    app.include_router(epics_router, tags=['Epic Management'])
    app.include_router(members_router, tags=['Members'])
except Exception as e:
    print(e)

if __name__ == "__main__":

    uvicorn.run(
        "main:app",
        host=server_settings.host,
        port=server_settings.port,
        reload=server_settings.reload,
        reload_dirs=["./"],
        timeout_keep_alive=server_settings.timeout_keep_alive,
        workers=server_settings.workers
    )
