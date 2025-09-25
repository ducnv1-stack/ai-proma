from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class CreateMemberRequest(BaseModel):
    """Schema cho request tạo member mới"""
    member_name: str = Field(..., description="Tên thành viên (bắt buộc)")
    team: Optional[str] = Field(None, description="Tên team (tùy chọn)")
    email: Optional[str] = Field(None, description="Email thành viên (tùy chọn)")

    class Config:
        json_schema_extra = {
            "example": {
                "member_name": "Nguyen Van A",
                "team": "Development",
                "email": "nguyenvana@example.com"
            }
        }

class CreateMemberResponse(BaseModel):
    """Schema cho response sau khi tạo member thành công"""
    workspace_id: str
    user_id: str
    member_id: str
    member_name: str
    team: Optional[str]
    email: Optional[str]
    created_at: str
    updated_at: Optional[str]

    class Config:
        json_schema_extra = {
            "example": {
                "workspace_id": "default_workspace",
                "user_id": "user_865417",
                "member_id": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
                "member_name": "Nguyen Van A",
                "team": "Development",
                "email": "nguyenvana@example.com",
                "created_at": "24/09/2024 13:45:30",
                "updated_at": None
            }
        }

class MemberInfo(BaseModel):
    """Schema cho thông tin member"""
    workspace_id: str
    user_id: str
    member_id: str
    member_name: str
    team: Optional[str]
    email: Optional[str]
    created_at: str

class ListMembersResponse(BaseModel):
    """Schema cho response danh sách members"""
    members: List[MemberInfo]
    total: int
    workspace_id: str
    user_id: str

    class Config:
        json_schema_extra = {
            "example": {
                "members": [
                    {
                        "workspace_id": "default_workspace",
                        "user_id": "user_865417",
                        "member_id": "01",
                        "member_name": "Duc Nguyen",
                        "team": "Dev",
                        "email": "ducnguyen@example.com",
                        "created_at": "24/09/2024 02:39:32"
                    }
                ],
                "total": 1,
                "workspace_id": "default_workspace",
                "user_id": "user_865417"
            }
        }

class UpdateMemberRequest(BaseModel):
    """Schema cho request update member"""
    member_name: Optional[str] = Field(None, description="Tên thành viên mới (tùy chọn)")
    team: Optional[str] = Field(None, description="Tên team mới (tùy chọn)")
    email: Optional[str] = Field(None, description="Email mới (tùy chọn)")

    class Config:
        json_schema_extra = {
            "example": {
                "member_name": "Nguyen Van B Updated",
                "team": "Marketing",
                "email": "nguyenvanb.updated@example.com"
            }
        }

class UpdateMemberResponse(BaseModel):
    """Schema cho response sau khi update member thành công"""
    workspace_id: str
    user_id: str
    member_id: str
    member_name: str
    team: Optional[str]
    email: Optional[str]
    created_at: str
    updated_at: str

    class Config:
        json_schema_extra = {
            "example": {
                "workspace_id": "default_workspace",
                "user_id": "user_865417",
                "member_id": "01",
                "member_name": "Nguyen Van B Updated",
                "team": "Marketing",
                "email": "nguyenvanb.updated@example.com",
                "created_at": "24/09/2024 13:45:30",
                "updated_at": "24/09/2024 15:20:15"
            }
        }
