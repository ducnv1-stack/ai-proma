from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from enum import Enum

class PriorityEnum(str, Enum):
    HIGHEST = "Highest"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    LOWEST = "Lowest"

class StatusEnum(str, Enum):
    TODO = "To do"
    INPROGRESS = "Inprogress"
    DONE = "Done"

class TypeEnum(str, Enum):
    EPIC = "Epic"
    TASK = "Task"
    SUBTASK = "Sub_task"

class CreateTaskRequest(BaseModel):
    type: TypeEnum = Field(..., description="Loại task: Epic, Task, hoặc Sub_task")
    
    # Fields cho Epic
    epic_name: Optional[str] = Field(None, min_length=1, max_length=255, description="Tên epic (bắt buộc cho Epic)")
    
    # Fields cho Task
    epic_id: Optional[str] = Field(None, description="ID của epic (bắt buộc cho Task và Sub_task)")
    task_name: Optional[str] = Field(None, min_length=1, max_length=255, description="Tên task (bắt buộc cho Task)")
    
    # Fields cho Sub_task
    parent_id: Optional[str] = Field(None, description="ID của task cha (bắt buộc cho Sub_task)")
    sub_task_name: Optional[str] = Field(None, min_length=1, max_length=255, description="Tên sub task (bắt buộc cho Sub_task)")
    
    # Common fields
    description: Optional[str] = Field(None, max_length=1000, description="Mô tả")
    category: Optional[str] = Field(None, max_length=100, description="Danh mục")
    priority: Optional[PriorityEnum] = Field(PriorityEnum.MEDIUM, description="Độ ưu tiên (mặc định: Medium)")
    status: Optional[StatusEnum] = Field(StatusEnum.TODO, description="Trạng thái (mặc định: To do)")
    assignee_name: Optional[str] = Field(None, max_length=100, description="Tên người được giao việc")
    start_date: Optional[str] = Field(None, description="Ngày bắt đầu (dd/MM/yyyy hh:mm:ss)")
    due_date: Optional[str] = Field(None, description="Ngày kết thúc (dd/MM/yyyy hh:mm:ss)")

    @validator('start_date', 'due_date')
    def validate_date_format(cls, v):
        if v is not None:
            try:
                datetime.strptime(v, '%d/%m/%Y %H:%M:%S')
            except ValueError:
                raise ValueError('Date must be in format dd/MM/yyyy hh:mm:ss')
        return v
    
    @validator('epic_name')
    def validate_epic_name(cls, v, values):
        if values.get('type') == TypeEnum.EPIC and not v:
            raise ValueError('epic_name is required for Epic type')
        return v
    
    @validator('epic_id')
    def validate_epic_id(cls, v, values):
        if values.get('type') in [TypeEnum.TASK, TypeEnum.SUBTASK] and not v:
            raise ValueError('epic_id is required for Task and Sub_task types')
        return v
    
    @validator('task_name')
    def validate_task_name(cls, v, values):
        if values.get('type') == TypeEnum.TASK and not v:
            raise ValueError('task_name is required for Task type')
        return v
    
    @validator('parent_id')
    def validate_parent_id(cls, v, values):
        if values.get('type') == TypeEnum.SUBTASK and not v:
            raise ValueError('parent_id is required for Sub_task type')
        return v
    
    @validator('sub_task_name')
    def validate_sub_task_name(cls, v, values):
        if values.get('type') == TypeEnum.SUBTASK and not v:
            raise ValueError('sub_task_name is required for Sub_task type')
        return v

# Giữ lại cho backward compatibility
class CreateEpicRequest(BaseModel):
    epic_name: str = Field(..., min_length=1, max_length=255, description="Tên epic (bắt buộc)")
    description: Optional[str] = Field(None, max_length=1000, description="Mô tả epic")
    category: Optional[str] = Field(None, max_length=100, description="Danh mục epic")
    priority: Optional[PriorityEnum] = Field(PriorityEnum.MEDIUM, description="Độ ưu tiên (mặc định: Medium)")
    status: Optional[StatusEnum] = Field(StatusEnum.TODO, description="Trạng thái (mặc định: To do)")
    assignee_name: Optional[str] = Field(None, max_length=100, description="Tên người được giao việc")
    start_date: Optional[str] = Field(None, description="Ngày bắt đầu (dd/MM/yyyy hh:mm:ss)")
    due_date: Optional[str] = Field(None, description="Ngày kết thúc (dd/MM/yyyy hh:mm:ss)")

    @validator('start_date', 'due_date')
    def validate_date_format(cls, v):
        if v is not None:
            try:
                datetime.strptime(v, '%d/%m/%Y %H:%M:%S')
            except ValueError:
                raise ValueError('Date must be in format dd/MM/yyyy hh:mm:ss')
        return v

class EpicResponse(BaseModel):
    workspace_id: str
    user_id: str
    epic_id: str
    epic_name: str
    task_id: Optional[str] = None
    task_name: Optional[str] = None
    sub_task_id: Optional[str] = None
    sub_task_name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    priority: PriorityEnum
    status: StatusEnum
    assignee_id: Optional[str] = None
    assignee_name: Optional[str] = None
    start_date: str
    due_date: str
    deadline_extend: Optional[str] = None
    type: TypeEnum
    create_at: str
    update_at: str

class CreateTaskResponse(BaseModel):
    status: str
    message: str
    task: EpicResponse  # Sử dụng EpicResponse vì cấu trúc giống nhau

class CreateEpicResponse(BaseModel):
    status: str
    message: str
    epic: EpicResponse

class ListEpicsResponse(BaseModel):
    status: str
    message: str
    total_count: int
    workspace_id: str
    epics: list[EpicResponse]
