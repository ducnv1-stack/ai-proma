from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
import jwt
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-super-secret-jwt-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Pydantic models
class TokenRequest(BaseModel):
    username: str
    email: Optional[str] = None
    role: str = "user"
    workspace_id: str = "default_workspace"
    agent_id: str = "facebook_marketing_agent"

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_info: dict

class LoginRequest(BaseModel):
    username: str
    password: str
    workspace_id: Optional[str] = "default_workspace"
    agent_id: Optional[str] = "facebook_marketing_agent"

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Tạo JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/token", response_model=TokenResponse)
async def create_token(request: TokenRequest):
    """
    Tạo JWT token cho testing và development
    Không cần password - chỉ dành cho development
    """
    try:
        # Tạo payload cho JWT
        token_data = {
            "sub": request.username,
            "user_id": f"user_{hash(request.username) % 1000000}",  # Generate simple user_id
            "email": request.email or f"{request.username}@example.com",
            "role": request.role,
            "workspace_id": request.workspace_id,
            "agent_id": request.agent_id
        }
        
        # Tạo token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data=token_data, 
            expires_delta=access_token_expires
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Convert to seconds
            user_info={
                "username": request.username,
                "email": token_data["email"],
                "role": request.role,
                "workspace_id": request.workspace_id,
                "agent_id": request.agent_id,
                "user_id": token_data["user_id"]
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create token: {str(e)}"
        )

@router.post("/login", response_model=TokenResponse)
async def login_for_access_token(request: LoginRequest):
    """
    Đăng nhập đơn giản để lấy token
    Chỉ dành cho development - không có database validation
    """
    # Simple validation - accept any username/password for development
    if not request.username or len(request.username) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username must be at least 3 characters"
        )
    
    if not request.password or len(request.password) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 3 characters"
        )
    
    # Create token (same as /token endpoint)
    token_request = TokenRequest(
        username=request.username,
        email=f"{request.username}@example.com",
        role="user",
        workspace_id=request.workspace_id,
        agent_id=request.agent_id
    )
    
    return await create_token(token_request)

@router.get("/verify")
async def verify_token(token: str):
    """
    Verify JWT token
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {
            "valid": True,
            "payload": payload,
            "expires_at": datetime.fromtimestamp(payload.get("exp", 0)).isoformat()
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

@router.get("/agents")
async def get_available_agents():
    """
    Lấy danh sách agents có sẵn để chọn khi tạo token
    """
    return {
        "agents": [
            {
                "id": "facebook_marketing_agent",
                "name": "Facebook Marketing Agent",
                "description": "Chuyên gia marketing Facebook"
            },
            {
                "id": "project_manager_agent", 
                "name": "Project Manager Agent",
                "description": "Chuyên gia quản lý dự án"
            }
        ]
    }
