from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import uuid
import pytz
from src.database.postgres import database
from src.api.schemas.epics import CreateEpicRequest, EpicResponse, PriorityEnum, StatusEnum, TypeEnum
import logging

logger = logging.getLogger(__name__)

class EpicService:
    def __init__(self):
        self.vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')  # UTC+7
    
    def generate_epic_id(self) -> str:
        """Tạo epic ID theo format: epic-[chuỗi ngẫu nhiên]"""
        random_string = str(uuid.uuid4()).replace('-', '')[:8]
        return f"epic-{random_string}"
    
    def get_vietnam_datetime(self) -> str:
        """Lấy thời gian hiện tại theo múi giờ UTC+7"""
        now = datetime.now(self.vietnam_tz)
        return now.strftime('%d/%m/%Y %H:%M:%S')
    
    def calculate_due_date(self, start_date_str: str) -> str:
        """Tính due_date = start_date + 7 ngày"""
        try:
            # Debug log để xem input
            logger.info(f"Parsing start_date: '{start_date_str}' (type: {type(start_date_str)})")
            
            # Parse với format dd/MM/yyyy HH:mm:ss
            start_date = datetime.strptime(start_date_str, '%d/%m/%Y %H:%M:%S')
            due_date = start_date + timedelta(days=7)
            result = due_date.strftime('%d/%m/%Y %H:%M:%S')
            
            logger.info(f"Calculated due_date: '{result}'")
            return result
            
        except ValueError as e:
            logger.error(f"Date parsing error: {e}, input: '{start_date_str}'")
            # Fallback: return current time + 7 days
            fallback_date = datetime.now(self.vietnam_tz) + timedelta(days=7)
            return fallback_date.strftime('%d/%m/%Y %H:%M:%S')
        except Exception as e:
            logger.error(f"Unexpected error in calculate_due_date: {e}")
            # Fallback: return current time + 7 days  
            fallback_date = datetime.now(self.vietnam_tz) + timedelta(days=7)
            return fallback_date.strftime('%d/%m/%Y %H:%M:%S')
    
    async def get_assignee_info(self, assignee_name: str) -> Optional[Dict[str, str]]:
        """Lấy thông tin assignee từ bảng team_info"""
        try:
            query = """
                SELECT user_id, user_name 
                FROM ai_proma.team_info 
                WHERE LOWER(user_name) = LOWER(:assignee_name)
                LIMIT 1
            """
            result = await database.fetch_one(query, {"assignee_name": assignee_name})
            
            if result:
                return {
                    "assignee_id": result["user_id"],
                    "assignee_name": result["user_name"]
                }
            return None
        except Exception as e:
            logger.error(f"Error getting assignee info: {e}")
            return None
    
    async def create_epic(
        self, 
        request: CreateEpicRequest, 
        user_id: str, 
        username: str,
        workspace_id: str, 
        agent_id: str
    ) -> EpicResponse:
        """Tạo epic mới trong database"""
        
        # 1. Tạo epic_id
        epic_id = self.generate_epic_id()
        
        # 2. Xử lý start_date
        start_date = request.start_date or self.get_vietnam_datetime()
        
        # 3. Xử lý due_date
        due_date = request.due_date or self.calculate_due_date(start_date)
        
        # 4. Xử lý assignee
        assignee_id = user_id  # Mặc định là user tạo
        assignee_name = username  # Mặc định là user tạo
        
        if request.assignee_name and request.assignee_name.strip():
            assignee_info = await self.get_assignee_info(request.assignee_name)
            if assignee_info:
                assignee_id = assignee_info["assignee_id"]
                assignee_name = assignee_info["assignee_name"]
            else:
                logger.warning(f"Assignee '{request.assignee_name}' not found in team_info, using creator as assignee")
        
        # 5. Tạo timestamps
        current_time = self.get_vietnam_datetime()
        
        # 6. Chuẩn bị data để insert
        epic_data = {
            "workspace_id": workspace_id,
            "user_id": user_id,
            "agent_id": agent_id,
            "epic_id": epic_id,
            "epic_name": request.epic_name,
            "task_id": None,
            "task_name": None,
            "sub_task_id": None,
            "sub_task_name": None,
            "description": request.description,
            "category": request.category,
            "priority": request.priority.value if request.priority else PriorityEnum.MEDIUM.value,
            "status": request.status.value if request.status else StatusEnum.TODO.value,
            "assignee_id": assignee_id,
            "assignee_name": assignee_name,
            "start_date": start_date,
            "due_date": due_date,
            "deadline_extend": None,
            "type": TypeEnum.EPIC.value,
            "create_at": current_time,
            "update_at": current_time
        }
        
        # 7. Insert vào database
        try:
            insert_query = """
                INSERT INTO ai_proma.task_info (
                    workspace_id, user_id, agent_id, epic_id, epic_name,
                    task_id, task_name, sub_task_id, sub_task_name,
                    description, category, priority, status,
                    assignee_id, assignee_name, start_date, due_date,
                    deadline_extend, type, create_at, update_at
                ) VALUES (
                    :workspace_id, :user_id, :agent_id, :epic_id, :epic_name,
                    :task_id, :task_name, :sub_task_id, :sub_task_name,
                    :description, :category, :priority, :status,
                    :assignee_id, :assignee_name, :start_date, :due_date,
                    :deadline_extend, :type, :create_at, :update_at
                )
            """
            
            await database.execute(insert_query, epic_data)
            
            logger.info(f"Epic created successfully: {epic_id}")
            
            # 8. Trả về EpicResponse
            return EpicResponse(
                workspace_id=epic_data["workspace_id"],
                user_id=epic_data["user_id"],
                agent_id=epic_data["agent_id"],
                epic_id=epic_data["epic_id"],
                epic_name=epic_data["epic_name"],
                task_id=epic_data["task_id"],
                task_name=epic_data["task_name"],
                sub_task_id=epic_data["sub_task_id"],
                sub_task_name=epic_data["sub_task_name"],
                description=epic_data["description"],
                category=epic_data["category"],
                priority=PriorityEnum(epic_data["priority"]),
                status=StatusEnum(epic_data["status"]),
                assignee_id=epic_data["assignee_id"],
                assignee_name=epic_data["assignee_name"],
                start_date=epic_data["start_date"],
                due_date=epic_data["due_date"],
                deadline_extend=epic_data["deadline_extend"],
                type=TypeEnum(epic_data["type"]),
                create_at=epic_data["create_at"],
                update_at=epic_data["update_at"]
            )
            
        except Exception as e:
            logger.error(f"Error creating epic: {e}")
            raise Exception(f"Failed to create epic: {str(e)}")

    async def list_epics(self, workspace_id: str, user_id: Optional[str] = None) -> list[EpicResponse]:
        """
        Lấy danh sách epics từ database
        - workspace_id: ID workspace (bắt buộc)
        - user_id: ID user (tùy chọn, nếu có thì chỉ lấy epics của user đó)
        """
        try:
            # Base query để lấy epics với type = "Epic" (không phân biệt hoa thường)
            base_query = """
                SELECT 
                    workspace_id, user_id, agent_id, epic_id, epic_name,
                    task_id, task_name, sub_task_id, sub_task_name,
                    description, category, priority, status,
                    assignee_id, assignee_name, start_date, due_date,
                    deadline_extend, type, create_at, update_at
                FROM ai_proma.task_info 
                WHERE LOWER(type) = LOWER('Epic')
                AND workspace_id = :workspace_id
            """
            
            params = {"workspace_id": workspace_id}
            
            # Nếu có user_id thì filter thêm
            if user_id:
                base_query += " AND user_id = :user_id"
                params["user_id"] = user_id
            
            # Sắp xếp theo thời gian tạo mới nhất
            base_query += " ORDER BY create_at DESC"
            
            logger.info(f"Querying epics for workspace: {workspace_id}, user: {user_id}")
            
            results = await database.fetch_all(base_query, params)
            
            # Convert results thành EpicResponse objects
            epics = []
            for row in results:
                try:
                    epic = EpicResponse(
                        workspace_id=row["workspace_id"],
                        user_id=row["user_id"],
                        agent_id=row["agent_id"],
                        epic_id=row["epic_id"],
                        epic_name=row["epic_name"],
                        task_id=row["task_id"],
                        task_name=row["task_name"],
                        sub_task_id=row["sub_task_id"],
                        sub_task_name=row["sub_task_name"],
                        description=row["description"],
                        category=row["category"],
                        priority=PriorityEnum(row["priority"]) if row["priority"] else PriorityEnum.MEDIUM,
                        status=StatusEnum(row["status"]) if row["status"] else StatusEnum.TODO,
                        assignee_id=row["assignee_id"],
                        assignee_name=row["assignee_name"],
                        start_date=row["start_date"],
                        due_date=row["due_date"],
                        deadline_extend=row["deadline_extend"],
                        type=TypeEnum(row["type"]) if row["type"] else TypeEnum.EPIC,
                        create_at=row["create_at"],
                        update_at=row["update_at"]
                    )
                    epics.append(epic)
                except Exception as e:
                    logger.error(f"Error converting row to EpicResponse: {e}, row: {dict(row)}")
                    continue
            
            logger.info(f"Found {len(epics)} epics for workspace {workspace_id}")
            return epics
            
        except Exception as e:
            logger.error(f"Error listing epics: {e}")
            raise Exception(f"Failed to list epics: {str(e)}")

# Singleton instance
epic_service = EpicService()
