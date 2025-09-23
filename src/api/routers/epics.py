from fastapi import APIRouter, Depends, HTTPException, status
from src.api.authentication.dependencies import get_current_active_user
from src.api.schemas.epics import CreateEpicRequest, CreateEpicResponse, ListEpicsResponse
from src.api.services.epic_service import epic_service
from src.api.logging.logger import get_logger
import logging

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/epics", tags=["Epic Management"])

@router.post("/create", response_model=CreateEpicResponse)
async def create_epic(
    request: CreateEpicRequest,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Tạo epic mới trong hệ thống
    
    - **epic_name**: Tên epic (bắt buộc)
    - **description**: Mô tả epic (tùy chọn)
    - **category**: Danh mục epic (tùy chọn)
    - **priority**: Độ ưu tiên (mặc định: Medium)
    - **status**: Trạng thái (mặc định: To do)
    - **assignee_name**: Tên người được giao việc (tùy chọn, mặc định là người tạo)
    - **start_date**: Ngày bắt đầu (tùy chọn, mặc định là hôm nay)
    - **due_date**: Ngày kết thúc (tùy chọn, mặc định là start_date + 7 ngày)
    
    JWT token sẽ tự động cung cấp: workspace_id, user_id, agent_id, username
    """
    try:
        # Lấy thông tin từ JWT token đã được parse
        token_data = current_user.get("token_data", {})
        user_data = current_user.get("user", {})
        
        # Extract thông tin cần thiết từ JWT
        user_id = token_data.get("user_id") or user_data.get("id")
        username = token_data.get("sub") or user_data.get("username")
        workspace_id = token_data.get("workspace_id")
        agent_id = token_data.get("agent_id")
        
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
        
        if not agent_id:
            logger.error("Agent ID not found in JWT token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Agent ID not found in token"
            )
        
        logger.info(f"Creating epic '{request.epic_name}' for user {user_id} in workspace {workspace_id}")
        
        # Gọi service để tạo epic
        epic = await epic_service.create_epic(
            request=request,
            user_id=user_id,
            username=username or "Unknown User",
            workspace_id=workspace_id,
            agent_id=agent_id
        )
        
        logger.info(f"Epic created successfully: {epic.epic_id}")
        
        return CreateEpicResponse(
            status="success",
            message=f"Epic '{request.epic_name}' created successfully",
            epic=epic
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error creating epic: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create epic: {str(e)}"
        )

@router.get("/list", response_model=ListEpicsResponse)
async def list_epics(
    current_user: dict = Depends(get_current_active_user)
):
    """
    Lấy danh sách epics của user trong workspace hiện tại
    Lấy tất cả epics có type = "Epic" (không phân biệt hoa thường)
    """
    try:
        token_data = current_user.get("token_data", {})
        user_data = current_user.get("user", {})
        
        # Extract thông tin từ JWT
        workspace_id = token_data.get("workspace_id")
        user_id = token_data.get("user_id") or user_data.get("id")
        
        if not workspace_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Workspace ID not found in token"
            )
        
        logger.info(f"Listing epics for workspace: {workspace_id}, user: {user_id}")
        
        # Gọi service để lấy danh sách epics
        # Không filter theo user_id để lấy tất cả epics trong workspace
        epics = await epic_service.list_epics(workspace_id=workspace_id)
        
        logger.info(f"Retrieved {len(epics)} epics successfully")
        
        return {
            "status": "success",
            "message": f"Found {len(epics)} epics in workspace",
            "total_count": len(epics),
            "workspace_id": workspace_id,
            "epics": [epic.dict() for epic in epics]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing epics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list epics: {str(e)}"
        )
