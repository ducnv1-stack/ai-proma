from fastapi import APIRouter, Depends, HTTPException, status
from src.api.authentication.dependencies import get_current_active_user, get_epic_context
from src.api.schemas.epics import CreateEpicRequest, CreateEpicResponse, CreateTaskRequest, CreateTaskResponse, ListEpicsResponse
from src.api.services.epic_service import epic_service
from src.api.logging.logger import get_logger
import logging

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/epics", tags=["Epic Management"])

@router.post("/create", response_model=CreateEpicResponse)
async def create_epic(
    request: CreateEpicRequest,
    epic_context: dict = Depends(get_epic_context)
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
    
    JWT token chỉ cần chứa: workspace_id, user_id, user_name
    """
    try:
        # Lấy thông tin từ JWT context (chỉ workspace_id, user_id, user_name)
        workspace_id = epic_context["workspace_id"]
        user_id = epic_context["user_id"]
        user_name = epic_context["user_name"]
        
        logger.info(f"Creating epic '{request.epic_name}' for user {user_name} ({user_id}) in workspace {workspace_id}")
        
        # Gọi service để tạo epic với thông tin đơn giản
        epic = await epic_service.create_epic_simple(
            request=request,
            workspace_id=workspace_id,
            user_id=user_id,
            user_name=user_name
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

@router.post("/create-task", response_model=CreateTaskResponse)
async def create_task_unified(
    request: CreateTaskRequest,
    epic_context: dict = Depends(get_epic_context)
):
    """
    API thống nhất để tạo Epic, Task, hoặc Sub_task
    
    **Type Epic:**
    - epic_name: Tên epic (bắt buộc)
    - description, category, priority, status, assignee_name, start_date, due_date (tùy chọn)
    
    **Type Task:**
    - epic_id: ID của epic (bắt buộc)
    - epic_name: Tên epic (bắt buộc) 
    - task_name: Tên task (bắt buộc)
    - description, category, priority, status, assignee_name, start_date, due_date (tùy chọn)
    
    **Type Sub_task:**
    - epic_id: ID của epic (bắt buộc)
    - epic_name: Tên epic (bắt buộc)
    - parent_id: ID của task cha (bắt buộc)
    - sub_task_name: Tên sub task (bắt buộc)
    - description, category, priority, status, assignee_name, start_date, due_date (tùy chọn)
    
    JWT token chỉ cần chứa: workspace_id, user_id, user_name
    """
    try:
        # Lấy thông tin từ JWT context
        workspace_id = epic_context["workspace_id"]
        user_id = epic_context["user_id"]
        user_name = epic_context["user_name"]
        
        logger.info(f"Creating {request.type.value} for user {user_name} ({user_id}) in workspace {workspace_id}")
        
        # Gọi service để tạo task thống nhất
        task = await epic_service.create_task_unified(
            request=request,
            workspace_id=workspace_id,
            user_id=user_id,
            user_name=user_name
        )
        
        logger.info(f"{request.type.value} created successfully: {task.epic_id}")
        
        return CreateTaskResponse(
            status="success",
            message=f"{request.type.value} created successfully",
            task=task
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating {request.type.value}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create {request.type.value}: {str(e)}"
        )

@router.get("/list", response_model=ListEpicsResponse)
async def list_epics(
    epic_context: dict = Depends(get_epic_context),
    type: str = None
):
    """
    Lấy danh sách epics/tasks/subtasks theo workspace_id, user_id từ JWT token
    
    Query Parameters:
    - type: Epic, Task, Sub_task, hoặc All (mặc định: Epic)
    """
    try:
        # Lấy thông tin từ JWT context
        workspace_id = epic_context["workspace_id"]
        user_id = epic_context["user_id"]
        user_name = epic_context["user_name"]
        
        # Xử lý type parameter
        if type is None:
            type = "Epic"  # Mặc định là Epic để backward compatible
        
        # Validate type
        valid_types = ["Epic", "Task", "Sub_task", "All"]
        if type not in valid_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid type. Must be one of: {', '.join(valid_types)}"
            )
        
        logger.info(f"Listing {type} for user {user_name} ({user_id}) in workspace {workspace_id}")
        
        # Gọi service với type filter
        items = await epic_service.list_tasks_by_type(
            workspace_id=workspace_id,
            user_id=user_id,
            type_filter=type
        )
        
        logger.info(f"Service returned {len(items)} {type.lower()}s")
        
        # Tạo message phù hợp
        type_display = type.lower() + "s" if type != "All" else "items"
        
        return ListEpicsResponse(
            status="success",
            message=f"Found {len(items)} {type_display} for user {user_name} in workspace {workspace_id}",
            total_count=len(items),
            workspace_id=workspace_id,
            epics=items  # Vẫn dùng field "epics" để backward compatible
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing {type}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list {type}: {str(e)}"
        )
