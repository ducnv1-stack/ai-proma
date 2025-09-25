from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from datetime import datetime, timedelta
import jwt
from typing import Optional
import os
import hashlib
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "ai-proma-secret-key-2024")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "480"))  # 8 hours

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    claims: dict

@router.post("/token", response_model=TokenResponse)
async def create_token_from_any_json(request: dict):
    """
    Tạo JWT token từ bất kỳ JSON body nào
    Body JSON sẽ được chuyển trực tiếp thành JWT payload
    """
    try:
        # Thêm thông tin expiration vào payload
        payload = request.copy()
        payload.update({
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        })
        
        # Tạo JWT từ payload
        access_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            claims=request  # Trả về body gốc làm claims
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create token: {str(e)}"
        )

@router.post("/decode", response_model=dict)
async def decode_token(token: str):
    """
    Decode JWT token để xem thông tin bên trong
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
