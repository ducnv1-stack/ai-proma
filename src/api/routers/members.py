from fastapi import APIRouter, Depends, HTTPException, status
from src.api.schemas.members import CreateMemberRequest, CreateMemberResponse, ListMembersResponse, UpdateMemberRequest, UpdateMemberResponse
from src.api.services.member_service import member_service
from src.api.authentication.dependencies import get_current_active_user
from src.api.logging.logger import get_logger
import logging

router = APIRouter(prefix="/api/v1/members", tags=["Member Management"])
logger = get_logger(__name__)

@router.post("/create", response_model=CreateMemberResponse)
async def create_member(
    request: CreateMemberRequest,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Tạo member mới trong hệ thống
    
    - **member_name**: Tên thành viên (bắt buộc)
    - **team**: Tên team (tùy chọn)
    - **email**: Email thành viên (tùy chọn)
    
    JWT token sẽ tự động cung cấp: workspace_id, user_id
    """
    try:
        # Lấy thông tin từ JWT token đã được parse
        token_data = current_user.get("token_data", {})
        user_data = current_user.get("user", {})
        
        # Extract thông tin cần thiết từ JWT
        user_id = token_data.get("user_id") or user_data.get("id")
        workspace_id = token_data.get("workspace_id")
        
        logger.info(f"DEBUG - JWT Token data: {token_data}")
        logger.info(f"DEBUG - Extracted - workspace_id: '{workspace_id}', user_id: '{user_id}'")
        
        # Validation các thông tin bắt buộc từ JWT
        if not user_id:
            logger.error("User ID not found in JWT token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User ID not found in token"
            )
        
        if not workspace_id:
            logger.error("Workspace ID not found in JWT token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Workspace ID not found in token"
            )
        
        # Validation request data
        if not request.member_name or request.member_name.strip() == "":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Member name is required"
            )
        
        # Gọi service để tạo member
        logger.info(f"Creating member: {request.member_name}")
        member = await member_service.create_member(
            request=request,
            user_id=user_id,
            workspace_id=workspace_id
        )
        
        logger.info(f"Member created successfully: {member.member_id}")
        return member
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating member: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create member: {str(e)}"
        )

@router.get("/list", response_model=ListMembersResponse)
async def list_members(
    current_user: dict = Depends(get_current_active_user)
):
    """
    Lấy danh sách members theo workspace_id và user_id từ JWT token
    
    JWT token sẽ tự động cung cấp: workspace_id, user_id
    """
    try:
        # Lấy thông tin từ JWT token đã được parse
        token_data = current_user.get("token_data", {})
        user_data = current_user.get("user", {})
        
        # Extract thông tin cần thiết từ JWT
        user_id = token_data.get("user_id") or user_data.get("id")
        workspace_id = token_data.get("workspace_id")
        
        logger.info(f"DEBUG - JWT Token data: {token_data}")
        logger.info(f"DEBUG - Extracted - workspace_id: '{workspace_id}', user_id: '{user_id}'")
        
        # Validation các thông tin bắt buộc từ JWT
        if not user_id:
            logger.error("User ID not found in JWT token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User ID not found in token"
            )
        
        if not workspace_id:
            logger.error("Workspace ID not found in JWT token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Workspace ID not found in token"
            )
        
        # Gọi service để lấy danh sách members
        logger.info(f"Listing members for workspace: {workspace_id}, user: {user_id}")
        members_response = await member_service.list_members(
            workspace_id=workspace_id,
            user_id=user_id
        )
        
        logger.info(f"Found {members_response.total} members")
        return members_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error listing members: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list members: {str(e)}"
        )

@router.put("/update/{member_id}", response_model=UpdateMemberResponse)
async def update_member(
    member_id: str,
    request: UpdateMemberRequest,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Update member theo workspace_id, user_id, member_id
    
    - **member_id**: ID của member cần update (từ URL path)
    - **member_name**: Tên thành viên mới (tùy chọn)
    - **team**: Tên team mới (tùy chọn) 
    - **email**: Email mới (tùy chọn)
    
    JWT token sẽ tự động cung cấp: workspace_id, user_id
    """
    try:
        # Lấy thông tin từ JWT token đã được parse
        token_data = current_user.get("token_data", {})
        user_data = current_user.get("user", {})
        
        # Extract thông tin cần thiết từ JWT
        user_id = token_data.get("user_id") or user_data.get("id")
        workspace_id = token_data.get("workspace_id")
        
        logger.info(f"DEBUG - JWT Token data: {token_data}")
        logger.info(f"DEBUG - Extracted - workspace_id: '{workspace_id}', user_id: '{user_id}', member_id: '{member_id}'")
        
        # Validation các thông tin bắt buộc từ JWT
        if not user_id:
            logger.error("User ID not found in JWT token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User ID not found in token"
            )
        
        if not workspace_id:
            logger.error("Workspace ID not found in JWT token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Workspace ID not found in token"
            )
        
        # Validation member_id
        if not member_id or member_id.strip() == "":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Member ID is required"
            )
        
        # Validation request data - ít nhất 1 field phải có giá trị
        if not any([request.member_name, request.team, request.email]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one field (member_name, team, email) must be provided for update"
            )
        
        # Gọi service để update member
        logger.info(f"Updating member: {member_id}")
        updated_member = await member_service.update_member(
            member_id=member_id,
            request=request,
            workspace_id=workspace_id,
            user_id=user_id
        )
        
        logger.info(f"Member updated successfully: {member_id}")
        return updated_member
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error updating member: {e}")
        if "Member not found" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Member not found: {member_id}"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update member: {str(e)}"
        )
