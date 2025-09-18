# Import mock Google ADK first
import mock_google_adk

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Boolean, DateTime, text
from pydantic import BaseModel
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
import jwt
import uuid
import os
import httpx
import json
from database import connect_db, disconnect_db, create_tables, get_db_health, get_db_session
from sqlalchemy.ext.asyncio import AsyncSession
import config

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not installed, skip loading .env file
    pass

# JWT Configuration
JWT_SECRET_KEY = config.JWT_SECRET_KEY
JWT_ALGORITHM = config.JWT_ALGORITHM
JWT_EXPIRATION_TIME = timedelta(hours=24)

# Security
security = HTTPBearer()

# OpenRouter configuration will be handled in the chat endpoint

# Lifespan manager with database
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting Proma...")
    try:
        # Connect to database
        await connect_db()
        # Create tables if they don't exist
        await create_tables()
        print("✅ Database connected and tables created")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        # Continue without database for demo mode
    
    yield
    
    print("Shutting down Proma...")
    try:
        await disconnect_db()
        print("✅ Database disconnected")
    except Exception as e:
        print(f"❌ Database disconnect failed: {e}")

# Create FastAPI app
app = FastAPI(
    title="Proma AI Server",
    description="AI Multi-Agent System with Chat Interface",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Debug middleware
@app.middleware("http")
async def debug_requests(request, call_next):
    if request.url.path.startswith("/api/"):
        print(f"🌐 {request.method} {request.url.path}")
        if request.method == "POST":
            body = await request.body()
            print(f"📦 Body: {body.decode()}")
    response = await call_next(request)
    return response

# Mount static files for frontend
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

# Simple chat endpoint for demo
from fastapi import HTTPException
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
import asyncio
import json

# Pydantic Models
class ChatMessage(BaseModel):
    message: str
    session_id: str = "demo-session"

class UserRegister(BaseModel):
    user_name: str
    user_pass: str
    confirm_password: str

class UserLogin(BaseModel):
    user_name: str
    user_pass: str

class UserResponse(BaseModel):
    user_id: str
    user_name: str
    workspace_id: str
    is_active: bool
    created_at: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"
    workspace_id: str = "default"
    agent_id: str = "project_manager_agent"

class ChatResponse(BaseModel):
    response: str
    session_id: str
    timestamp: str

# JWT Helper Functions
def create_access_token(data: dict):
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + JWT_EXPIRATION_TIME
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token"""
    print(f"🔐 Verifying token...")
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        print(f"✅ Token valid for user: {payload.get('user_name', 'unknown')}")
        return payload
    except jwt.ExpiredSignatureError:
        print("❌ Token expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.JWTError as e:
        print(f"❌ JWT Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

async def get_current_user(user_id: str = Depends(verify_token), db: AsyncSession = Depends(get_db_session)):
    """Get current authenticated user"""
    from models import User
    from sqlalchemy import select
    
    try:
        print(f"Getting user with ID: {user_id}")  # Debug log
        result = await db.execute(select(User).where(User.user_id == user_id))
        user = result.scalar_one_or_none()
        if user is None:
            print(f"User not found with ID: {user_id}")  # Debug log
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
    except Exception as e:
        print(f"Error getting current user: {str(e)}")  # Debug log
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@app.post("/api/v1/chat-stream")
async def chat_demo(data: ChatMessage):
    """Demo chat endpoint with mock streaming response"""
    
    async def generate_response():
        try:
            # Check if OpenRouter API key is configured
            if not os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENROUTER_API_KEY") == "your_openrouter_api_key_here":
                # Fallback to mock response if API key not configured
                responses = [
                    "⚠️ OpenRouter API key chưa được cấu hình.",
                    " Vui lòng cập nhật OPENROUTER_API_KEY trong file .env",
                    " để sử dụng model Gemini 2.5 Flash.",
                    f" Tin nhắn của bạn: '{data.message}'"
                ]
                
                for i, response_part in enumerate(responses):
                    await asyncio.sleep(0.5)  # Faster mock response
                    event_data = {
                        "content": response_part,
                        "session_id": data.session_id,
                        "message_id": f"msg_{i}",
                        "timestamp": "2024-01-01T00:00:00Z"
                    }
                    yield f"data: {json.dumps(event_data)}\n\n"
                
                yield f"data: [DONE]\n\n"
                return

            # Create OpenAI chat completion with streaming
            system_message = """Bạn là Proma Project Manager Agent - chuyên gia quản lý dự án thông minh và chuyên nghiệp. 
            Bạn có thể giúp khách hàng với:
            - Lên kế hoạch và quản lý dự án hiệu quả
            - Tạo và phân công các task công việc
            - Theo dõi tiến độ và quản lý thời gian
            - Tư vấn về phương pháp quản lý dự án
            - Đưa ra giải pháp tối ưu quy trình làm việc
            
            Hãy trả lời bằng tiếng Việt một cách thân thiện và chuyên nghiệp."""

            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": data.message}
            ]

            # Stream response from OpenRouter with optimized settings
            stream = await openai_client.chat.completions.create(
                model=os.getenv("MKT_AGENT_MODEL", "openrouter/google/gemini-2.5-flash"),
                messages=messages,
                stream=True,
                temperature=0.3,  # Lower temperature for faster, more focused responses
                max_tokens=1500,  # Increased for more complete responses
                top_p=0.9,       # Nucleus sampling for better quality
                frequency_penalty=0.1,  # Reduce repetition
                presence_penalty=0.1    # Encourage diverse responses
            )

            message_id = 0
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    
                    event_data = {
                        "content": content,
                        "session_id": data.session_id,
                        "message_id": f"msg_{message_id}",
                        "timestamp": "2024-01-01T00:00:00Z"
                    }
                    
                    yield f"data: {json.dumps(event_data)}\n\n"
                    message_id += 1

            # End of stream
            yield f"data: [DONE]\n\n"

        except Exception as e:
            # Error handling
            error_message = f"Lỗi khi gọi OpenRouter API: {str(e)}"
            event_data = {
                "content": error_message,
                "session_id": data.session_id,
                "message_id": "error",
                "timestamp": "2024-01-01T00:00:00Z"
            }
            yield f"data: {json.dumps(event_data)}\n\n"
            yield f"data: [DONE]\n\n"
    
    return StreamingResponse(
        generate_response(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "*"
        }
    )

@app.get("/api/v1/agents")
async def get_agents():
    """Demo agents endpoint"""
    return {
        "agents": [
            {
                "id": "project_manager_agent",
                "name": "Project manager Agent",
                "description": "Chuyên gia quản lý dự án, có thể tạo các task, giao việc cho các agent khác",
                "status": "active"
            }
        ]
    }

@app.post("/api/v1/session/create")
async def create_session():
    """Demo session creation endpoint"""
    return {
        "session_id": "demo-session-123",
        "status": "created",
        "agent_id": "project_manager_agent"
    }

@app.get("/")
async def root():
    """Root endpoint redirect to dashboard"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/frontend/dashboard.html")

@app.get("/demo")
async def demo():
    """Demo page endpoint"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/frontend/demo.html")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    db_health = await get_db_health()
    return {
        "status": "healthy", 
        "message": "Proma AI Server is running",
        "database": db_health
    }

@app.get("/api/v1/database/status")
async def database_status():
    """Database status endpoint"""
    return await get_db_health()

@app.get("/api/v1/test/users")
async def test_users(db: AsyncSession = Depends(get_db_session)):
    """Test endpoint to check users in database"""
    from sqlalchemy import text
    
    try:
        # Test basic query
        result = await db.execute(text("SELECT 1"))
        basic_test = result.scalar()
        
        # Check if schema exists
        schema_check = await db.execute(text("SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'ai_proma'"))
        schema_exists = schema_check.fetchone()
        
        # Check if table exists - table name is "users_proma"
        table_check = await db.execute(text("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'ai_proma' AND table_name = 'users_proma'
        """))
        table_exists = table_check.fetchone()
        
        users = []
        users_error = None
        
        # Try to access the users_proma table
        if schema_exists and table_exists:
            try:
                # Access users_proma table
                result = await db.execute(text('SELECT user_id, user_name FROM "ai_proma"."users_proma" LIMIT 5'))
                users = result.fetchall()
            except Exception as e1:
                users_error = f"Failed to access users_proma table: {str(e1)}"
        
        return {
            "basic_query": basic_test,
            "schema_exists": schema_exists is not None,
            "table_exists": table_exists is not None,
            "users_count": len(users),
            "users": [{"user_name": row[1], "user_id": row[0]} for row in users] if users else [],
            "error": users_error
        }
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}

@app.get("/api/v1/debug/schema-info")
async def get_schema_info(db: AsyncSession = Depends(get_db_session)):
    """Debug endpoint to check schema and tables"""
    from sqlalchemy import text
    
    try:
        # List all tables in ai_proma schema
        tables_result = await db.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'ai_proma'
            ORDER BY table_name
        """))
        tables = [row[0] for row in tables_result.fetchall()]
        
        # List all schemas
        schemas_result = await db.execute(text("""
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
            ORDER BY schema_name
        """))
        schemas = [row[0] for row in schemas_result.fetchall()]
        
        # Check specifically for users_proma table
        users_proma_check = await db.execute(text("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'ai_proma' AND table_name = 'users_proma'
        """))
        users_proma_exists = users_proma_check.fetchone()
        
        return {
            "schemas": schemas,
            "tables_in_ai_proma": tables,
            "ai_proma_exists": "ai_proma" in schemas,
            "users_proma_exists": users_proma_exists is not None
        }
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}

@app.get("/api/v1/debug/all-tables")
async def get_all_tables(db: AsyncSession = Depends(get_db_session)):
    """Debug endpoint to check all tables in database"""
    from sqlalchemy import text
    
    try:
        # List all tables in all schemas
        all_tables_result = await db.execute(text("""
            SELECT table_schema, table_name 
            FROM information_schema.tables 
            WHERE table_schema NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
            ORDER BY table_schema, table_name
        """))
        all_tables = [{"schema": row[0], "table": row[1]} for row in all_tables_result.fetchall()]
        
        # Check specifically for users table
        users_tables_result = await db.execute(text("""
            SELECT table_schema, table_name 
            FROM information_schema.tables 
            WHERE table_name LIKE '%user%'
            ORDER BY table_schema, table_name
        """))
        users_tables = [{"schema": row[0], "table": row[1]} for row in users_tables_result.fetchall()]
        
        return {
            "all_tables": all_tables,
            "users_related_tables": users_tables,
            "total_tables": len(all_tables)
        }
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}

@app.post("/api/v1/setup/create-tables")
async def create_tables_endpoint():
    """Manually create database tables"""
    try:
        await create_tables()
        return {"message": "Tables created successfully"}
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}

@app.get("/api/v1/setup/create-tables")
async def create_tables_get():
    """Manually create database tables (GET version)"""
    try:
        from database import create_tables
        await create_tables()
        return {"message": "Tables created successfully", "status": "ok"}
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__, "status": "error"}

@app.get("/api/v1/setup/create-user-table")
async def create_user_table_direct(db: AsyncSession = Depends(get_db_session)):
    """Create user table directly with SQL"""
    try:
        from sqlalchemy import text
        
        # First create schema if not exists
        await db.execute(text('CREATE SCHEMA IF NOT EXISTS "ai_proma"'))
        
        # Create users table directly (matching existing schema)
        create_sql = """
        CREATE TABLE IF NOT EXISTS "ai_proma"."user" (
            user_id VARCHAR PRIMARY KEY DEFAULT gen_random_uuid()::text,
            user_name VARCHAR(50) UNIQUE NOT NULL,
            user_pass VARCHAR(255) NOT NULL
        );
        
        CREATE INDEX IF NOT EXISTS idx_users_name ON "ai_proma"."users"(user_name);
        
        -- Insert test user duc with password 123456 (hashed)
        INSERT INTO "ai_proma"."users" (user_id, user_name, user_pass) 
        VALUES (gen_random_uuid()::text, 'duc', 'e10adc3949ba59abbe56e057f20f883e') 
        ON CONFLICT (user_name) DO NOTHING;
        """
        
        await db.execute(text(create_sql))
        await db.commit()
        
        return {"message": "User table and test data created successfully", "status": "ok"}
    except Exception as e:
        await db.rollback()
        return {"error": str(e), "type": type(e).__name__, "status": "error"}

@app.get("/api/v1/users")
async def get_users(db: AsyncSession = Depends(get_db_session)):
    """Get all users (demo endpoint)"""
    from models import User
    from sqlalchemy import select
    
    try:
        result = await db.execute(select(User))
        users = result.scalars().all()
        return {
            "users": [
                {
                    "user_id": str(user.user_id),
                    "user_name": user.user_name,
                    "workspace_id": user.workspace_id,
                    "is_active": user.is_active,
                    "created_at": user.created_at.isoformat() if user.created_at else None
                }
                for user in users
            ],
            "count": len(users)
        }
    except Exception as e:
        return {"error": str(e), "users": [], "count": 0}

@app.post("/api/v1/auth/register", response_model=LoginResponse)
async def register_user(user_data: UserRegister, db: AsyncSession = Depends(get_db_session)):
    """Register a new user"""
    from models import User
    from sqlalchemy import select
    
    # Validate password confirmation
    if user_data.user_pass != user_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mật khẩu xác nhận không khớp"
        )
    
    # Check if username already exists
    try:
        print(f"Register attempt for user: {user_data.user_name}")  # Debug log
        
        from sqlalchemy import text
        import uuid
        
        # Check if user exists in ai_proma.users_proma table
        print(f"Checking if user exists: {user_data.user_name}")  # Debug log
        result = await db.execute(
            text('SELECT user_name FROM "ai_proma"."users_proma" WHERE user_name = :username'),
            {"username": user_data.user_name}
        )
        print("User existence check completed")  # Debug log
        existing_user = result.fetchone()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tên đăng nhập đã tồn tại"
            )
        
        # Create new user - store password directly (no hashing for simplicity)
        new_user_id = str(uuid.uuid4())
        
        await db.execute(
            text('INSERT INTO "ai_proma"."users_proma" (user_id, user_name, user_pass) VALUES (:user_id, :user_name, :user_pass)'),
            {
                "user_id": new_user_id,
                "user_name": user_data.user_name,
                "user_pass": user_data.user_pass  # Store password directly
            }
        )
        await db.commit()
        
        # Create access token
        access_token = create_access_token(data={"sub": new_user_id})
        
        # Return response
        from datetime import datetime
        user_response = UserResponse(
            user_id=new_user_id,
            user_name=user_data.user_name,
            workspace_id='default',
            is_active=True,
            created_at=datetime.now().isoformat()
        )
        
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user=user_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi tạo tài khoản: {str(e)}"
        )

@app.post("/api/v1/auth/login", response_model=LoginResponse)
async def login_user(user_data: UserLogin, db: AsyncSession = Depends(get_db_session)):
    """Login user"""
    print(f"🔐 Login attempt: {user_data.user_name}")
    print(f"📝 Request data: {user_data}")
    from models import User
    from sqlalchemy import select
    
    try:
        
        # Find user by username in ai_proma.users_proma table
        from sqlalchemy import text
        result = await db.execute(
            text('SELECT user_id, user_name, user_pass FROM "ai_proma"."users_proma" WHERE user_name = :username'),
            {"username": user_data.user_name}
        )
        user_row = result.fetchone()
        
        print(f"User found: {user_row is not None}")  # Debug log
        
        if not user_row:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tên đăng nhập không tồn tại"
            )
            
        user_id, user_name, stored_password = user_row
        
        # Check password - compare directly with stored password
        print(f"Stored password: '{stored_password}'")  # Debug log
        print(f"Input password: '{user_data.user_pass}'")  # Debug log
        print(f"Password lengths - Stored: {len(stored_password)}, Input: {len(user_data.user_pass)}")  # Debug log
        print(f"Stored password repr: {repr(stored_password)}")  # Debug log
        print(f"Input password repr: {repr(user_data.user_pass)}")  # Debug log
        
        # Convert both to string and strip
        stored_pass_clean = str(stored_password).strip()
        input_pass_clean = str(user_data.user_pass).strip()
        
        print(f"After cleaning - Stored: '{stored_pass_clean}', Input: '{input_pass_clean}'")
        print(f"Are they equal? {stored_pass_clean == input_pass_clean}")
        
        # Simple password check - compare input password with stored password (strip whitespace)
        if input_pass_clean != stored_pass_clean:
            print(f"Password mismatch: '{input_pass_clean}' != '{stored_pass_clean}'")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Mật khẩu không đúng"
            )
        
        print("Password match successful!")
        
        # Create access token
        access_token = create_access_token(data={"sub": str(user_row[0])})
        
        # Return response
        from datetime import datetime
        user_response = UserResponse(
            user_id=str(user_row[0]),
            user_name=user_row[1],
            workspace_id='default',
            is_active=True,
            created_at=datetime.now().isoformat()
        )
        
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user=user_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {str(e)}")  # Debug log
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi đăng nhập: {str(e)}"
        )

@app.get("/api/v1/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(
        user_id=str(current_user.user_id),
        user_name=current_user.user_name,
        workspace_id=current_user.workspace_id,
        is_active=current_user.is_active,
        created_at=current_user.created_at.isoformat() if current_user.created_at else None
    )

@app.post("/api/v1/auth/logout")
async def logout_user(current_user: dict = Depends(verify_token)):
    """Logout user - invalidate token on client side"""
    print(f"🚪 Logout request from user: {current_user.get('user_name', 'unknown')}")
    
    # Since we're using JWT tokens, we can't invalidate them server-side without a blacklist
    # The client will handle removing the token from localStorage
    # In a production system, you might want to implement a token blacklist
    
    return {
        "message": "Đăng xuất thành công",
        "status": "success",
        "user_name": current_user.get("user_name", "unknown")
    }

@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat_with_ai(
    chat_request: ChatRequest,
    current_user: dict = Depends(verify_token)
):
    """Chat with AI using OpenRouter API"""
    print(f"🚀 CHAT ENDPOINT CALLED!")
    print(f"💬 Chat request received from user: {current_user.get('user_name', 'unknown')}")
    print(f"📝 Message: {chat_request.message}")
    print(f"🔍 Request details: {chat_request}")
    
    try:
        # OpenRouter API configuration
        openrouter_api_key = get_openrouter_api_key()
        print(f"🔑 API Key available: {openrouter_api_key is not None}")
        
        # If no API key, return mock response for demo
        if not openrouter_api_key:
            print("⚠️ No API key found, using mock response")
            return get_mock_ai_response(chat_request)
        
        openrouter_url = "https://openrouter.ai/api/v1/chat/completions"
        
        # Prepare the prompt based on agent type
        system_prompt = get_agent_prompt(chat_request.agent_id)
        
        # Call OpenRouter API
        print(f"🚀 Calling OpenRouter API with model: {config.DEFAULT_AI_MODEL}")
        print(f"📝 User message: {chat_request.message}")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                openrouter_url,
                headers={
                    "Authorization": f"Bearer {openrouter_api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://localhost:8004",
                    "X-Title": "Proma AI Assistant"
                },
                json={
                    "model": config.DEFAULT_AI_MODEL,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": chat_request.message}
                    ],
                    "max_tokens": 1000,
                    "temperature": 0.7
                },
                timeout=30.0
            )
            
        print(f"📡 OpenRouter response status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ OpenRouter API error: {response.status_code} - {response.text}")
            return get_mock_ai_response(chat_request)
            
        ai_response = response.json()
        ai_message = ai_response["choices"][0]["message"]["content"]
        
        print(f"✅ OpenRouter response received: {ai_message[:100]}...")
        
        return ChatResponse(
            response=ai_message,
            session_id=chat_request.session_id,
            timestamp=datetime.now().isoformat()
        )
        
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="AI service timeout. Please try again."
        )
    except Exception as e:
        print(f"💥 Chat error: {str(e)}")
        print(f"💥 Exception type: {type(e)}")
        import traceback
        print(f"💥 Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during chat processing"
        )

def get_openrouter_api_key() -> str:
    """Get OpenRouter API key from environment or config"""
    # Try environment variable first
    api_key = os.getenv("OPENROUTER_API_KEY")
    if api_key and api_key != "sk-or-v1-your-openrouter-api-key-here":
        return api_key
    
    # Try config file
    if hasattr(config, 'OPENROUTER_API_KEY') and config.OPENROUTER_API_KEY != "sk-or-v1-your-openrouter-api-key-here":
        return config.OPENROUTER_API_KEY
    
    # For demo purposes, return a mock response instead of calling real API
    return None

def get_mock_ai_response(chat_request: ChatRequest) -> ChatResponse:
    """Generate mock AI response for demo purposes"""
    import random
    
    print("🎭 Using MOCK response (not OpenRouter)")
    
    # Mock responses based on message content
    message = chat_request.message.lower()
    
    if "xin chào" in message or "hello" in message or "hi" in message:
        responses = [
            "Xin chào! Tôi là Proma, AI Project Manager Agent của bạn. Tôi có thể giúp bạn quản lý dự án, tạo tasks và theo dõi tiến độ. Bạn cần hỗ trợ gì hôm nay?",
            "Chào bạn! Rất vui được gặp bạn. Tôi là Proma, chuyên gia quản lý dự án AI. Hãy cho tôi biết bạn đang làm việc trên dự án gì nhé!",
            "Hello! Tôi là Proma Project Manager Agent. Tôi sẵn sàng hỗ trợ bạn trong việc quản lý dự án, phân công công việc và tối ưu hóa quy trình làm việc."
        ]
    elif "dự án" in message or "project" in message:
        responses = [
            "Tuyệt vời! Để quản lý dự án hiệu quả, chúng ta cần xác định rõ mục tiêu, timeline và phân công nhiệm vụ. Bạn có thể chia sẻ thêm về dự án bạn đang làm không?",
            "Quản lý dự án là thế mạnh của tôi! Tôi có thể giúp bạn lập kế hoạch, theo dõi tiến độ và đảm bảo dự án hoàn thành đúng hạn. Dự án của bạn thuộc lĩnh vực gì?",
            "Để hỗ trợ bạn tốt nhất, tôi cần hiểu rõ về dự án. Bạn có thể cho tôi biết về scope, timeline và team size không?"
        ]
    elif "task" in message or "công việc" in message or "nhiệm vụ" in message:
        responses = [
            "Tôi có thể giúp bạn tạo và quản lý tasks một cách có hệ thống. Chúng ta có thể chia nhỏ công việc, set priority và deadline. Bạn muốn tạo task nào trước?",
            "Quản lý tasks hiệu quả là chìa khóa thành công! Tôi có thể giúp bạn prioritize, assign và track progress. Hãy mô tả công việc bạn cần làm nhé!",
            "Tuyệt! Tôi sẽ giúp bạn organize các tasks. Chúng ta có thể sử dụng methodology như Agile hoặc Kanban. Bạn prefer phương pháp nào?"
        ]
    elif "team" in message or "nhóm" in message:
        responses = [
            "Team management là một phần quan trọng! Tôi có thể giúp bạn phân công công việc phù hợp với skill của từng thành viên và theo dõi performance. Team bạn có bao nhiêu người?",
            "Để quản lý team hiệu quả, chúng ta cần clear communication và proper task distribution. Bạn có thể chia sẻ về structure và roles trong team không?",
            "Great! Tôi có thể hỗ trợ bạn trong việc coordinate team activities, set up meetings và ensure everyone stays on track. Team bạn đang face challenges gì?"
        ]
    else:
        responses = [
            "Cảm ơn bạn đã chia sẻ! Là một Project Manager Agent, tôi có thể hỗ trợ bạn trong nhiều khía cạnh của quản lý dự án. Bạn có muốn tôi giúp phân tích vấn đề này không?",
            "Thật thú vị! Tôi sẽ cố gắng hỗ trợ bạn tốt nhất có thể. Với kinh nghiệm quản lý dự án, tôi nghĩ chúng ta có thể approach vấn đề này một cách có hệ thống.",
            "Tôi hiểu rồi! Hãy để tôi suy nghĩ về cách tốt nhất để giải quyết vấn đề này. Với background về project management, tôi có thể đưa ra một số suggestions hữu ích.",
            "Đây là một câu hỏi hay! Dựa trên kinh nghiệm quản lý dự án, tôi có thể chia sẻ một số best practices và methodologies phù hợp với tình huống của bạn."
        ]
    
    return ChatResponse(
        response=random.choice(responses),
        session_id=chat_request.session_id,
        timestamp=datetime.now().isoformat()
    )

def get_agent_prompt(agent_id: str) -> str:
    """Get system prompt based on agent type"""
    prompts = {
        "project_manager_agent": """Bạn là Proma, một AI Project Manager Agent chuyên nghiệp. 
        Nhiệm vụ của bạn là:
        - Hỗ trợ quản lý dự án
        - Tạo và phân công tasks
        - Theo dõi tiến độ công việc
        - Đưa ra lời khuyên về quy trình làm việc
        - Giúp tối ưu hóa hiệu suất team
        
        Hãy trả lời một cách chuyên nghiệp, hữu ích và thân thiện. Sử dụng tiếng Việt.""",
        
        "default": """Bạn là một AI assistant thông minh và hữu ích. 
        Hãy trả lời câu hỏi một cách chính xác và thân thiện bằng tiếng Việt."""
    }
    
    return prompts.get(agent_id, prompts["default"])

if __name__ == "__main__":
    print("Starting Proma AI Server (Demo Mode)")
    print("Frontend: http://localhost:8002/frontend/")
    print("Demo Page: http://localhost:8002/frontend/demo.html")
    print("Chat Interface: http://localhost:8002/frontend/index.html")
    
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0",
        port=8002,
        log_level="info"
    )
