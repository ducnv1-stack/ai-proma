# Import mock Google ADK first
import mock_google_adk

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
from src.api.routers.chat import router as chat_router
from src.api.routers.agents import agents_router
from src.api.routers.session import router as session_router
from src.database.postgres import database

from contextlib import asynccontextmanager
from configs import get_settings, get_server_settings
import logging

# Load configuration
settings = get_settings()
server_settings = get_server_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup - Connect to database
    print(f"Starting {server_settings.app_name}...")
    await database.connect()
    print("Database connected")
    yield
    
    # Shutdown - Disconnect from database
    print(f"Shutting down {server_settings.app_name}...")
    await database.disconnect()
    print("✅ Database disconnected")

app = FastAPI(
    title=server_settings.app_name,
    description=server_settings.app_description,
    version=server_settings.app_version,
    docs_url=server_settings.docs_url,
    redoc_url=server_settings.redoc_url,
    root_path="",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=server_settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for frontend
try:
    app.mount("/static", StaticFiles(directory="frontend"), name="static")
except Exception as e:
    print(f"Could not mount static files: {e}")

try:
    origins = server_settings.cors_origins
    app.include_router(chat_router, tags=['Main Router'])
    app.include_router(agents_router, tags=['Agents'])
    app.include_router(session_router, tags=['Session'])
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
