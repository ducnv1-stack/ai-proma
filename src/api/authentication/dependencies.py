from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import jwt
import logging
import os

logger = logging.getLogger(__name__)

# Sử dụng cùng secret key với auth router
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "ai-proma-secret-key-2024")
ALGORITHM = "HS256"

security = HTTPBearer()

def decode_simple_jwt(token: str) -> dict:
    """Decode JWT token đơn giản chỉ lấy thông tin cần thiết
    
    JWT chứa:
    - sub: username
    - user_id: user ID
    - agent_id: agent ID  
    - workspace_id: workspace ID
    - role: user role
    
    Returns:
        dict: The decoded JWT payload
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Kiểm tra các field bắt buộc
        required_fields = ["sub", "user_id", "agent_id", "workspace_id"]
        for field in required_fields:
            if field not in payload:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Missing required field: {field}",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Decode JWT token và trả về thông tin user đơn giản"""
    token = credentials.credentials
    
    # Decode JWT token đơn giản
    token_data = decode_simple_jwt(token)
    
    # Extract thông tin cơ bản từ token
    user = {
        "id": token_data.get("user_id"),
        "username": token_data.get("username") or token_data.get("sub"),
        "role": token_data.get("role", "user"),
        "is_active": True,
        "is_admin": token_data.get("role") == "admin"
    }
    
    # Log authentication
    logger.info(f"User authenticated: {user['username']}")
    
    return {
        "user": user,
        "token_data": token_data
    }

async def get_epic_context(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Decode JWT và chỉ lấy thông tin cần thiết cho epic: workspace_id, user_id, user_name"""
    token = credentials.credentials
    
    try:
        # Decode JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Chỉ lấy thông tin cần thiết, bỏ qua thông tin thừa
        epic_context = {
            "workspace_id": payload.get("workspace_id"),
            "user_id": payload.get("user_id"), 
            "user_name": payload.get("username") or payload.get("sub")
        }
        
        # Validation các field bắt buộc
        if not epic_context["workspace_id"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="workspace_id not found in token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not epic_context["user_id"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="user_id not found in token", 
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not epic_context["user_name"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="user_name not found in token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.info(f"Epic context extracted: workspace_id={epic_context['workspace_id']}, user_id={epic_context['user_id']}, user_name={epic_context['user_name']}")
        
        return epic_context
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_active_user(current_user: dict = Depends(get_current_user)):
    """Get current active user.
    
    Since we're using JWT-only authentication, all users with valid tokens
    are considered active by default.
    """
    return current_user

async def get_admin_user(current_user: dict = Depends(get_current_active_user)):
    """Get current user if they are an admin."""
    # Check token data for admin role
    token_data = current_user.get("token_data", {})
    if token_data.get("role") != "admin" and not current_user["user"].get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user