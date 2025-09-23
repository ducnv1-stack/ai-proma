from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import jwt
import logging

from configs import get_security_settings

logger = logging.getLogger(__name__)

security_settings = get_security_settings()

SECRET_KEY = security_settings.jwt_secret_key or "your-secret-key-change-this-in-production"
ALGORITHM = security_settings.jwt_algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = security_settings.jwt_access_token_expire_minutes

security = HTTPBearer()

def decode_token_jwt(token: str) -> dict:
    """Verify and decode a JWT token.
    
    When using JWT tokens without database authentication, the token should contain
    all necessary user information including:
    - sub: username or user identifier
    - user_id: the user's unique ID
    - email: user's email
    - role: user's role (optional, default 'user')
    - session_id: current session ID
    - workspace_id: current workspace ID
    - agent_id: current agent ID
    
    Returns:
        dict: The decoded JWT payload
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
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
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get the current authenticated user from JWT token.
    
    This function decodes the JWT token and extracts all user information.
    No database lookup is performed - all user data comes from the token.
    """
    token = credentials.credentials
    
    # Decode JWT token
    token_data = decode_token_jwt(token)
    
    # Extract basic user information from token
    user = {
        "id": token_data.get("user_id"),
        "username": token_data.get("sub"),
        "email": token_data.get("email"),
        "role": token_data.get("role", "user"),
        "is_active": True,
        "is_admin": token_data.get("role") == "admin"
    }
    
    # Log successful authentication
    logger.info(f"User authenticated: {user['username']}")
    
    return {
        "user": user,
        "token_data": token_data
    }

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