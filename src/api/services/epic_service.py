from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import uuid
import pytz
from fastapi import HTTPException
from src.database.postgres import get_db_connection
from src.api.schemas.epics import CreateEpicRequest, CreateTaskRequest, DeleteTaskResponse, GetTaskResponse, UpdateTaskRequest, UpdateTaskResponse, EpicResponse, PriorityEnum, StatusEnum, TypeEnum
import logging

logger = logging.getLogger(__name__)

class EpicService:
    def __init__(self):
        self.vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')  # UTC+7
    
    def generate_epic_id(self) -> str:
        """Tạo epic ID theo format: epic-[32 ký tự]"""
        random_string = str(uuid.uuid4()).replace('-', '')
        return f"epic-{random_string}"
    
    def generate_task_id(self) -> str:
        """Tạo task ID theo format: task-[32 ký tự]"""
        random_string = str(uuid.uuid4()).replace('-', '')
        return f"task-{random_string}"
    
    def generate_subtask_id(self) -> str:
        """Tạo subtask ID theo format: subtask-[32 ký tự]"""
        random_string = str(uuid.uuid4()).replace('-', '')
        return f"subtask-{random_string}"
    
    def detect_type_from_id(self, item_id: str) -> str:
        """Detect type từ ID prefix"""
        if item_id.startswith("epic-"):
            return "Epic"
        elif item_id.startswith("task-"):
            return "Task"
        elif item_id.startswith("subtask-"):
            return "Sub_task"
        else:
            raise ValueError(f"Invalid ID format: {item_id}. Must start with epic-, task-, or subtask-")
    
    def get_vietnam_datetime(self) -> str:
        """Lấy ngày hiện tại theo múi giờ UTC+7"""
        now = datetime.now(self.vietnam_tz)
        return now.strftime('%d/%m/%Y')
    
    def calculate_due_date(self, start_date_str: str) -> str:
        """Tính due_date = start_date + 7 ngày"""
        try:
            # Debug log để xem input
            logger.info(f"Parsing start_date: '{start_date_str}' (type: {type(start_date_str)})")
            
            # Parse với format dd/MM/yyyy
            start_date = datetime.strptime(start_date_str, '%d/%m/%Y')
            due_date = start_date + timedelta(days=7)
            result = due_date.strftime('%d/%m/%Y')
            
            logger.info(f"Calculated due_date: '{result}'")
            return result
            
        except ValueError as e:
            logger.error(f"Date parsing error: {e}, input: '{start_date_str}'")
            # Fallback: return current date + 7 days
            fallback_date = datetime.now(self.vietnam_tz) + timedelta(days=7)
            return fallback_date.strftime('%d/%m/%Y')
        except Exception as e:
            logger.error(f"Unexpected error in calculate_due_date: {e}")
            # Fallback: return current date + 7 days  
            fallback_date = datetime.now(self.vietnam_tz) + timedelta(days=7)
            return fallback_date.strftime('%d/%m/%Y')
    
    async def get_assignee_info(self, assignee_name: str) -> Optional[Dict[str, str]]:
        """Lấy thông tin assignee từ bảng team_info"""
        conn = None
        try:
            conn = await get_db_connection()
            query = """
                SELECT member_id, member_name 
                FROM ai_proma.team_info 
                WHERE LOWER(member_name) = LOWER($1)
                LIMIT 1
            """
            result = await conn.fetchrow(query, assignee_name)
            
            if result:
                return {
                    "assignee_id": result["member_id"],
                    "assignee_name": result["member_name"]
                }
            return None
        except Exception as e:
            logger.error(f"Error getting assignee info: {e}")
            return None
        finally:
            if conn:
                await conn.close()
    
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
        conn = None
        try:
            conn = await get_db_connection()
            insert_query = """
                INSERT INTO ai_proma.task_info (
                    workspace_id, user_id, agent_id, epic_id, epic_name,
                    task_id, task_name, sub_task_id, sub_task_name,
                    description, category, priority, status,
                    assignee_id, assignee_name, start_date, due_date,
                    deadline_extend, type, create_at, update_at
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21
                )
            """
            
            await conn.execute(
                insert_query,
                epic_data["workspace_id"], epic_data["user_id"], epic_data["agent_id"], 
                epic_data["epic_id"], epic_data["epic_name"], epic_data["task_id"], 
                epic_data["task_name"], epic_data["sub_task_id"], epic_data["sub_task_name"],
                epic_data["description"], epic_data["category"], epic_data["priority"], 
                epic_data["status"], epic_data["assignee_id"], epic_data["assignee_name"], 
                epic_data["start_date"], epic_data["due_date"], epic_data["deadline_extend"], 
                epic_data["type"], epic_data["create_at"], epic_data["update_at"]
            )
            
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
        finally:
            if conn:
                await conn.close()

    async def list_epics(self, workspace_id: str, user_id: Optional[str] = None) -> list[EpicResponse]:
        """
        Lấy danh sách epics từ database
        - workspace_id: ID workspace (bắt buộc)
        - user_id: ID user (tùy chọn, nếu có thì chỉ lấy epics của user đó)
        """
        conn = None
        try:
            conn = await get_db_connection()
            # Debug: Đầu tiên kiểm tra tất cả records trong table
            debug_query = """
                SELECT COUNT(*) as total_records, 
                       COUNT(CASE WHEN TRIM(type) = 'Epic' THEN 1 END) as epic_records
                FROM ai_proma.task_info
            """
            debug_result = await conn.fetchrow(debug_query)
            logger.info(f"DEBUG - Total records: {debug_result['total_records']}, Epic records: {debug_result['epic_records']}")
            
            # Debug: Kiểm tra các type values có trong DB
            type_query = """
                SELECT DISTINCT TRIM(type) as type_trimmed, type as type_raw, COUNT(*) as count
                FROM ai_proma.task_info 
                GROUP BY type
            """
            type_results = await conn.fetch(type_query)
            logger.info(f"DEBUG - Type distribution: {[(row['type_trimmed'], row['type_raw'][:10] + '...', row['count']) for row in type_results]}")
            
            # Debug: Kiểm tra workspace_id distribution
            workspace_query = """
                SELECT DISTINCT TRIM(workspace_id) as workspace_trimmed, COUNT(*) as count
                FROM ai_proma.task_info 
                GROUP BY workspace_id
            """
            workspace_results = await conn.fetch(workspace_query)
            logger.info(f"DEBUG - Workspace distribution: {[(row['workspace_trimmed'], row['count']) for row in workspace_results]}")
            
            # Debug: Lấy 5 records đầu tiên để xem structure
            sample_query = """
                SELECT workspace_id, type, epic_name
                FROM ai_proma.task_info 
                LIMIT 5
            """
            sample_results = await conn.fetch(sample_query)
            logger.info(f"DEBUG - Sample records: {[dict(row) for row in sample_results]}")
            
            # Main query - sử dụng TRIM để loại bỏ trailing spaces
            base_query = """
                SELECT 
                    TRIM(workspace_id) as workspace_id, TRIM(user_id) as user_id, TRIM(agent_id) as agent_id, 
                    TRIM(epic_id) as epic_id, TRIM(epic_name) as epic_name,
                    TRIM(task_id) as task_id, TRIM(task_name) as task_name, 
                    TRIM(sub_task_id) as sub_task_id, TRIM(sub_task_name) as sub_task_name,
                    TRIM(description) as description, TRIM(category) as category, 
                    TRIM(priority) as priority, TRIM(status) as status,
                    TRIM(assignee_id) as assignee_id, TRIM(assignee_name) as assignee_name, 
                    TRIM(start_date) as start_date, TRIM(due_date) as due_date,
                    TRIM(deadline_extend) as deadline_extend, TRIM(type) as type, 
                    TRIM(create_at) as create_at, TRIM(update_at) as update_at
                FROM ai_proma.task_info 
                WHERE TRIM(type) = 'Epic'
            """
            
            params = {}
            
            # Thêm workspace filter nếu có data
            if workspace_id and workspace_id != "default_workspace":
                base_query += " AND TRIM(workspace_id) = :workspace_id"
                params["workspace_id"] = workspace_id
                logger.info(f"DEBUG - Adding workspace filter: {workspace_id}")
            else:
                logger.info(f"DEBUG - No workspace filter applied (workspace_id: {workspace_id})")
            
            # Nếu có user_id thì filter thêm
            if user_id:
                base_query += " AND TRIM(user_id) = :user_id"
                params["user_id"] = user_id
                logger.info(f"DEBUG - Adding user filter: {user_id}")
            
            # Sắp xếp theo thởi gian tạo mới nhất
            base_query += " ORDER BY create_at DESC"
            
            logger.info(f"DEBUG - Final query: {base_query}")
            logger.info(f"DEBUG - Query params: {params}")
            
            # Convert params dict to list for asyncpg
            param_values = []
            query_with_placeholders = base_query
            param_counter = 1
            
            if workspace_id and workspace_id != "default_workspace":
                query_with_placeholders = query_with_placeholders.replace(":workspace_id", f"${param_counter}")
                param_values.append(workspace_id)
                param_counter += 1
            
            if user_id:
                query_with_placeholders = query_with_placeholders.replace(":user_id", f"${param_counter}")
                param_values.append(user_id)
                param_counter += 1
            
            results = await conn.fetch(query_with_placeholders, *param_values)
            logger.info(f"DEBUG - Raw query returned {len(results)} rows")
            
            # Nếu không có results, thử query không có filters
            if len(results) == 0:
                logger.info("DEBUG - No results with filters, trying without filters...")
                simple_query = """
                    SELECT COUNT(*) as count, 
                           MIN(type) as sample_type,
                           MIN(workspace_id) as sample_workspace
                    FROM ai_proma.task_info 
                    WHERE TRIM(type) = 'Epic'
                """
                simple_result = await conn.fetchrow(simple_query)
                logger.info(f"DEBUG - Simple epic count: {simple_result}")
                
                # Thử lấy tất cả records để debug
                all_query = """
                    SELECT workspace_id, type, epic_name
                    FROM ai_proma.task_info 
                    LIMIT 10
                """
                all_results = await conn.fetch(all_query)
                logger.info(f"DEBUG - All records sample: {[dict(row) for row in all_results]}")
            
            # Convert results thành EpicResponse objects
            epics = []
            for row in results:
                try:
                    logger.info(f"Processing row: epic_id={row.get('epic_id')}, type={row.get('type')}")
                    
                    epic = EpicResponse(
                        workspace_id=row["workspace_id"] or "default_workspace",
                        user_id=row["user_id"] or "unknown",
                        agent_id=row["agent_id"] or "unknown",
                        epic_id=row["epic_id"] or "unknown",
                        epic_name=row["epic_name"] or "Untitled Epic",
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
                        start_date=row["start_date"] or "01/01/2025 00:00:00",
                        due_date=row["due_date"] or "01/01/2025 00:00:00",
                        deadline_extend=row["deadline_extend"],
                        type=TypeEnum(row["type"]) if row["type"] else TypeEnum.EPIC,
                        create_at=row["create_at"] or "01/01/2025 00:00:00",
                        update_at=row["update_at"] or "01/01/2025 00:00:00"
                    )
                    epics.append(epic)
                    logger.info(f"Successfully converted epic: {epic.epic_name}")
                    
                except Exception as e:
                    logger.error(f"Error converting row to EpicResponse: {e}")
                    logger.error(f"Row data: {dict(row)}")
                    continue
            
            logger.info(f"Successfully converted {len(epics)} epics out of {len(results)} rows")
            return epics
            
        except Exception as e:
            logger.error(f"Error listing epics: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise Exception(f"Failed to list epics: {str(e)}")
        finally:
            if conn:
                await conn.close()

    async def list_epics_with_filters(self, workspace_id: str, user_id: str, agent_id: str) -> list[EpicResponse]:
        """
        Lấy danh sách epics với filters chính xác theo JWT token
        - workspace_id: ID workspace (bắt buộc)
        - user_id: ID user (bắt buộc)  
        - agent_id: ID agent (bắt buộc)
        """
        conn = None
        try:
            conn = await get_db_connection()
            logger.info(f"Filtering epics - workspace: '{workspace_id}', user: '{user_id}', agent: '{agent_id}'")
            
            # Query với tất cả filters từ JWT
            query = """
                SELECT 
                    TRIM(workspace_id) as workspace_id, TRIM(user_id) as user_id, TRIM(agent_id) as agent_id, 
                    TRIM(epic_id) as epic_id, TRIM(epic_name) as epic_name,
                    TRIM(task_id) as task_id, TRIM(task_name) as task_name, 
                    TRIM(sub_task_id) as sub_task_id, TRIM(sub_task_name) as sub_task_name,
                    TRIM(description) as description, TRIM(category) as category, 
                    TRIM(priority) as priority, TRIM(status) as status,
                    TRIM(assignee_id) as assignee_id, TRIM(assignee_name) as assignee_name, 
                    TRIM(start_date) as start_date, TRIM(due_date) as due_date,
                    TRIM(deadline_extend) as deadline_extend, TRIM(type) as type, 
                    TRIM(create_at) as create_at, TRIM(update_at) as update_at
                FROM ai_proma.task_info 
                WHERE TRIM(type) = 'Epic'
                AND TRIM(workspace_id) = $1
                AND TRIM(user_id) = $2
                AND TRIM(agent_id) = $3
                ORDER BY create_at DESC
            """
            
            params = {
                "workspace_id": workspace_id,
                "user_id": user_id,
                "agent_id": agent_id
            }
            
            logger.info(f"Executing filtered query with params: {params}")
            
            results = await conn.fetch(query, workspace_id, user_id, agent_id)
            logger.info(f"Filtered query returned {len(results)} rows")
            
            # DEBUG: Return raw data để test
            if len(results) > 0:
                logger.info(f"DEBUG - Raw row data: {[dict(row) for row in results]}")
                # Tạm thởi return raw data để test
                raw_epics = []
                for row in results:
                    raw_epic = {
                        "workspace_id": row["workspace_id"] or workspace_id,
                        "user_id": row["user_id"] or user_id,
                        "agent_id": row["agent_id"] or agent_id,
                        "epic_id": row["epic_id"] or "unknown",
                        "epic_name": row["epic_name"] or "Untitled Epic",
                        "task_id": row["task_id"],
                        "task_name": row["task_name"],
                        "sub_task_id": row["sub_task_id"],
                        "sub_task_name": row["sub_task_name"],
                        "description": row["description"] or "",
                        "category": row["category"] or "",
                        "priority": row["priority"] or "Medium",
                        "status": row["status"] or "To do",
                        "assignee_id": row["assignee_id"] or "",
                        "assignee_name": row["assignee_name"] or "",
                        "start_date": row["start_date"] or "01/01/2025 00:00:00",
                        "due_date": row["due_date"] or "01/01/2025 00:00:00",
                        "deadline_extend": row["deadline_extend"],
                        "type": row["type"] or "Epic",
                        "create_at": row["create_at"] or "01/01/2025 00:00:00",
                        "update_at": row["update_at"] or "01/01/2025 00:00:00"
                    }
                    raw_epics.append(raw_epic)
                
                logger.info(f"DEBUG - Returning {len(raw_epics)} raw epics")
                # Convert raw dict to EpicResponse for return type compatibility
                converted_epics = []
                for raw_epic in raw_epics:
                    try:
                        epic_response = EpicResponse(**raw_epic)
                        converted_epics.append(epic_response)
                        logger.info(f"Successfully converted: {raw_epic['epic_name']}")
                    except Exception as e:
                        logger.error(f"Conversion error: {e}")
                        logger.error(f"Raw epic data: {raw_epic}")
                        continue
                
                return converted_epics
            
            # Convert results thành EpicResponse objects (original code)
            epics = []
            for row in results:
                try:
                    logger.info(f"Processing filtered row: epic_id={row.get('epic_id')}, type={row.get('type')}")
                    
                    epic = EpicResponse(
                        workspace_id=row["workspace_id"] or workspace_id,
                        user_id=row["user_id"] or user_id,
                        agent_id=row["agent_id"] or agent_id,
                        epic_id=row["epic_id"] or "unknown",
                        epic_name=row["epic_name"] or "Untitled Epic",
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
                        start_date=row["start_date"] or "01/01/2025 00:00:00",
                        due_date=row["due_date"] or "01/01/2025 00:00:00",
                        deadline_extend=row["deadline_extend"],
                        type=TypeEnum(row["type"]) if row["type"] else TypeEnum.EPIC,
                        create_at=row["create_at"] or "01/01/2025 00:00:00",
                        update_at=row["update_at"] or "01/01/2025 00:00:00"
                    )
                    epics.append(epic)
                    logger.info(f"Successfully converted filtered epic: {epic.epic_name}")
                    
                except Exception as e:
                    logger.error(f"Error converting filtered row to EpicResponse: {e}")
                    logger.error(f"Row data: {dict(row)}")
                    continue
            
            logger.info(f"Successfully converted {len(epics)} filtered epics out of {len(results)} rows")
            return epics
            
        except Exception as e:
            logger.error(f"Error listing filtered epics: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise Exception(f"Failed to list filtered epics: {str(e)}")
        finally:
            if conn:
                await conn.close()

    async def create_epic_simple(
        self, 
        request: CreateEpicRequest, 
        workspace_id: str,
        user_id: str, 
        user_name: str
    ) -> EpicResponse:
        """Tạo epic đơn giản chỉ với thông tin từ JWT và body request"""
        
        # 1. Tạo epic_id
        epic_id = self.generate_epic_id()
        
        # 2. Xử lý start_date
        start_date = request.start_date or self.get_vietnam_datetime()
        
        # 3. Xử lý due_date
        due_date = request.due_date or self.calculate_due_date(start_date)
        
        # 4. Xử lý assignee - mặc định là người tạo
        assignee_id = user_id
        assignee_name = user_name
        
        # Nếu có assignee_name trong request, thử lookup trong team_info
        if request.assignee_name and request.assignee_name.strip():
            assignee_info = await self.get_assignee_info(request.assignee_name)
            if assignee_info:
                assignee_id = assignee_info["assignee_id"]
                assignee_name = assignee_info["assignee_name"]
            else:
                logger.warning(f"Assignee '{request.assignee_name}' not found in team_info, using creator as assignee")
        
        # 5. Tạo timestamps
        current_time = self.get_vietnam_datetime()
        
        # 6. Chuẩn bị data để insert (loại bỏ agent_id)
        epic_data = {
            "workspace_id": workspace_id,
            "user_id": user_id,
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
        
        # 7. Insert vào database (không có agent_id column)
        conn = None
        try:
            conn = await get_db_connection()
            insert_query = """
                INSERT INTO ai_proma.task_info (
                    workspace_id, user_id, epic_id, epic_name,
                    task_id, task_name, sub_task_id, sub_task_name,
                    description, category, priority, status,
                    assignee_id, assignee_name, start_date, due_date,
                    deadline_extend, type, create_at, update_at
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20
                )
            """
            
            await conn.execute(
                insert_query,
                epic_data["workspace_id"], epic_data["user_id"], 
                epic_data["epic_id"], epic_data["epic_name"], epic_data["task_id"], 
                epic_data["task_name"], epic_data["sub_task_id"], epic_data["sub_task_name"],
                epic_data["description"], epic_data["category"], epic_data["priority"], 
                epic_data["status"], epic_data["assignee_id"], epic_data["assignee_name"], 
                epic_data["start_date"], epic_data["due_date"], epic_data["deadline_extend"], 
                epic_data["type"], epic_data["create_at"], epic_data["update_at"]
            )
            
            logger.info(f"Epic created successfully: {epic_id}")
            
            # 8. Trả về EpicResponse (không có agent_id)
            return EpicResponse(
                workspace_id=epic_data["workspace_id"],
                user_id=epic_data["user_id"],
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
        finally:
            if conn:
                await conn.close()

    async def list_epics_simple(self, workspace_id: str, user_id: str) -> list[EpicResponse]:
        """
        Lấy danh sách epics đơn giản chỉ với workspace_id và user_id
        Không cần agent_id
        """
        conn = None
        try:
            conn = await get_db_connection()
            logger.info(f"Listing epics - workspace: '{workspace_id}', user: '{user_id}'")
            
            # Query đơn giản chỉ với workspace_id và user_id
            query = """
                SELECT 
                    TRIM(workspace_id) as workspace_id, TRIM(user_id) as user_id, 
                    TRIM(epic_id) as epic_id, TRIM(epic_name) as epic_name,
                    TRIM(task_id) as task_id, TRIM(task_name) as task_name, 
                    TRIM(sub_task_id) as sub_task_id, TRIM(sub_task_name) as sub_task_name,
                    TRIM(description) as description, TRIM(category) as category, 
                    TRIM(priority) as priority, TRIM(status) as status,
                    TRIM(assignee_id) as assignee_id, TRIM(assignee_name) as assignee_name, 
                    TRIM(start_date) as start_date, TRIM(due_date) as due_date,
                    TRIM(deadline_extend) as deadline_extend, TRIM(type) as type, 
                    TRIM(create_at) as create_at, TRIM(update_at) as update_at
                FROM ai_proma.task_info 
                WHERE TRIM(type) = 'Epic'
                AND TRIM(workspace_id) = $1
                AND TRIM(user_id) = $2
                ORDER BY create_at DESC
            """
            
            logger.info(f"Executing simple query with params: workspace_id={workspace_id}, user_id={user_id}")
            
            results = await conn.fetch(query, workspace_id, user_id)
            logger.info(f"Simple query returned {len(results)} rows")
            
            # Convert results thành EpicResponse objects
            epics = []
            for row in results:
                try:
                    logger.info(f"Processing row: epic_id={row.get('epic_id')}, type={row.get('type')}")
                    
                    epic = EpicResponse(
                        workspace_id=row["workspace_id"] or workspace_id,
                        user_id=row["user_id"] or user_id,
                        epic_id=row["epic_id"] or "unknown",
                        epic_name=row["epic_name"] or "Untitled Epic",
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
                        start_date=row["start_date"] or "01/01/2025 00:00:00",
                        due_date=row["due_date"] or "01/01/2025 00:00:00",
                        deadline_extend=row["deadline_extend"],
                        type=TypeEnum(row["type"]) if row["type"] else TypeEnum.EPIC,
                        create_at=row["create_at"] or "01/01/2025 00:00:00",
                        update_at=row["update_at"] or "01/01/2025 00:00:00"
                    )
                    epics.append(epic)
                    logger.info(f"Successfully converted epic: {epic.epic_name}")
                    
                except Exception as e:
                    logger.error(f"Error converting row to EpicResponse: {e}")
                    logger.error(f"Row data: {dict(row)}")
                    continue
            
            logger.info(f"Successfully converted {len(epics)} epics out of {len(results)} rows")
            return epics
            
        except Exception as e:
            logger.error(f"Error listing simple epics: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise Exception(f"Failed to list simple epics: {str(e)}")
        finally:
            if conn:
                await conn.close()

    async def list_tasks_by_type(self, workspace_id: str, user_id: str, type_filter: str) -> list[EpicResponse]:
        """
        Lấy danh sách tasks theo type filter
        
        Args:
            workspace_id: ID của workspace
            user_id: ID của user
            type_filter: "Epic", "Task", "Sub_task", hoặc "All"
        """
        conn = None
        try:
            conn = await get_db_connection()
            logger.info(f"Listing {type_filter} - workspace: '{workspace_id}', user: '{user_id}'")
            
            # Build WHERE clause dựa trên type_filter
            if type_filter == "All":
                type_condition = "TRIM(type) IN ('Epic', 'Task', 'Sub_task')"
                query_params = [workspace_id, user_id]
            else:
                type_condition = "TRIM(type) = $3"
                query_params = [workspace_id, user_id, type_filter]
            
            # Query với type filter
            query = f"""
                SELECT 
                    TRIM(workspace_id) as workspace_id, TRIM(user_id) as user_id, 
                    TRIM(epic_id) as epic_id, TRIM(epic_name) as epic_name,
                    TRIM(task_id) as task_id, TRIM(task_name) as task_name, 
                    TRIM(sub_task_id) as sub_task_id, TRIM(sub_task_name) as sub_task_name,
                    TRIM(description) as description, TRIM(category) as category, 
                    TRIM(priority) as priority, TRIM(status) as status,
                    TRIM(assignee_id) as assignee_id, TRIM(assignee_name) as assignee_name, 
                    TRIM(start_date) as start_date, TRIM(due_date) as due_date,
                    TRIM(deadline_extend) as deadline_extend, TRIM(type) as type, 
                    TRIM(create_at) as create_at, TRIM(update_at) as update_at
                FROM ai_proma.task_info 
                WHERE {type_condition}
                AND TRIM(workspace_id) = $1
                AND TRIM(user_id) = $2
                ORDER BY create_at DESC
            """
            
            logger.info(f"Executing query with params: workspace_id={workspace_id}, user_id={user_id}, type_filter={type_filter}")
            
            results = await conn.fetch(query, *query_params)
            logger.info(f"Query returned {len(results)} rows")
            
            # Convert results thành EpicResponse objects
            items = []
            for row in results:
                try:
                    logger.info(f"Processing row: id={row.get('epic_id') or row.get('task_id') or row.get('sub_task_id')}, type={row.get('type')}")
                    
                    item = EpicResponse(
                        workspace_id=row["workspace_id"] or workspace_id,
                        user_id=row["user_id"] or user_id,
                        epic_id=row["epic_id"] or "unknown",
                        epic_name=row["epic_name"] or "Untitled Epic",
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
                        start_date=row["start_date"] or "01/01/2025 00:00:00",
                        due_date=row["due_date"] or "01/01/2025 00:00:00",
                        deadline_extend=row["deadline_extend"],
                        type=TypeEnum(row["type"]) if row["type"] else TypeEnum.EPIC,
                        create_at=row["create_at"] or "01/01/2025 00:00:00",
                        update_at=row["update_at"] or "01/01/2025 00:00:00"
                    )
                    items.append(item)
                    
                    # Log tên item dựa trên type
                    item_name = row.get("epic_name") or row.get("task_name") or row.get("sub_task_name") or "Unnamed"
                    logger.info(f"Successfully converted {row.get('type')}: {item_name}")
                    
                except Exception as e:
                    logger.error(f"Error converting row to EpicResponse: {e}")
                    logger.error(f"Row data: {dict(row)}")
                    continue
            
            logger.info(f"Successfully converted {len(items)} items out of {len(results)} rows")
            return items
            
        except Exception as e:
            logger.error(f"Error listing tasks by type: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise Exception(f"Failed to list tasks by type: {str(e)}")
        finally:
            if conn:
                await conn.close()

    async def create_task_unified(
        self, 
        request: CreateTaskRequest, 
        workspace_id: str,
        user_id: str, 
        user_name: str
    ) -> EpicResponse:
        """API thống nhất để tạo Epic, Task, hoặc Sub_task"""
        
        # 1. Generate ID dựa trên type
        if request.type == TypeEnum.EPIC:
            item_id = self.generate_epic_id()
            item_name = request.epic_name
        elif request.type == TypeEnum.TASK:
            item_id = self.generate_task_id()
            item_name = request.task_name
        elif request.type == TypeEnum.SUBTASK:
            item_id = self.generate_subtask_id()
            item_name = request.sub_task_name
        else:
            raise ValueError(f"Unsupported type: {request.type}")
        
        # 2. Xử lý start_date và due_date
        start_date = request.start_date or self.get_vietnam_datetime()
        due_date = request.due_date or self.calculate_due_date(start_date)
        
        # 3. Xử lý assignee - mặc định là người tạo
        assignee_id = user_id
        assignee_name = user_name
        
        if request.assignee_name and request.assignee_name.strip():
            assignee_info = await self.get_assignee_info(request.assignee_name)
            if assignee_info:
                assignee_id = assignee_info["assignee_id"]
                assignee_name = assignee_info["assignee_name"]
            else:
                logger.warning(f"Assignee '{request.assignee_name}' not found in team_info, using creator as assignee")
        
        # 4. Tạo timestamps
        current_time = self.get_vietnam_datetime()
        
        # 5. Chuẩn bị data để insert
        task_data = {
            "workspace_id": workspace_id,
            "user_id": user_id,
            "epic_id": request.epic_id if request.type != TypeEnum.EPIC else item_id,
            "epic_name": request.epic_name if request.type == TypeEnum.EPIC else request.epic_name,
            "task_id": item_id if request.type == TypeEnum.TASK else (request.parent_id if request.type == TypeEnum.SUBTASK else None),
            "task_name": item_name if request.type == TypeEnum.TASK else None,
            "sub_task_id": item_id if request.type == TypeEnum.SUBTASK else None,
            "sub_task_name": item_name if request.type == TypeEnum.SUBTASK else None,
            "description": request.description,
            "category": request.category,
            "priority": request.priority.value if request.priority else PriorityEnum.MEDIUM.value,
            "status": request.status.value if request.status else StatusEnum.TODO.value,
            "assignee_id": assignee_id,
            "assignee_name": assignee_name,
            "start_date": start_date,
            "due_date": due_date,
            "deadline_extend": None,
            "type": request.type.value,
            "create_at": current_time,
            "update_at": current_time
        }
        
        # 6. Insert vào database
        conn = None
        try:
            conn = await get_db_connection()
            insert_query = """
                INSERT INTO ai_proma.task_info (
                    workspace_id, user_id, epic_id, epic_name,
                    task_id, task_name, sub_task_id, sub_task_name,
                    description, category, priority, status,
                    assignee_id, assignee_name, start_date, due_date,
                    deadline_extend, type, create_at, update_at
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20
                )
            """
            
            await conn.execute(
                insert_query,
                task_data["workspace_id"], task_data["user_id"], 
                task_data["epic_id"], task_data["epic_name"], task_data["task_id"], 
                task_data["task_name"], task_data["sub_task_id"], task_data["sub_task_name"],
                task_data["description"], task_data["category"], task_data["priority"], 
                task_data["status"], task_data["assignee_id"], task_data["assignee_name"], 
                task_data["start_date"], task_data["due_date"], task_data["deadline_extend"], 
                task_data["type"], task_data["create_at"], task_data["update_at"]
            )
            
            logger.info(f"{request.type.value} created successfully: {item_id}")
            
            # 7. Trả về EpicResponse
            return EpicResponse(
                workspace_id=task_data["workspace_id"],
                user_id=task_data["user_id"],
                epic_id=task_data["epic_id"],
                epic_name=task_data["epic_name"],
                task_id=task_data["task_id"],
                task_name=task_data["task_name"],
                sub_task_id=task_data["sub_task_id"],
                sub_task_name=task_data["sub_task_name"],
                description=task_data["description"],
                category=task_data["category"],
                priority=PriorityEnum(task_data["priority"]),
                status=StatusEnum(task_data["status"]),
                assignee_id=task_data["assignee_id"],
                assignee_name=task_data["assignee_name"],
                start_date=task_data["start_date"],
                due_date=task_data["due_date"],
                deadline_extend=task_data["deadline_extend"],
                type=TypeEnum(task_data["type"]),
                create_at=task_data["create_at"],
                update_at=task_data["update_at"]
            )
            
        except Exception as e:
            logger.error(f"Error creating {request.type.value}: {e}")
            raise Exception(f"Failed to create {request.type.value}: {str(e)}")
        finally:
            if conn:
                await conn.close()

    async def delete_task_cascade(
        self, 
        item_id: str,
        workspace_id: str, 
        user_id: str,
        dry_run: bool = False
    ) -> DeleteTaskResponse:
        """
        Xóa Epic/Task/Sub_task với cascade logic
        
        Args:
            item_id: ID của item cần xóa
            workspace_id: ID workspace
            user_id: ID user
            dry_run: True = preview only, False = execute delete
        """
        conn = None
        try:
            # 1. Detect type từ ID prefix
            item_type = self.detect_type_from_id(item_id)
            logger.info(f"Detected type: {item_type} for item_id: {item_id}")
            
            conn = await get_db_connection()
            
            # 2. Build cascade query dựa trên type
            if item_type == "Epic":
                # Xóa Epic + tất cả Task + tất cả Sub_task thuộc Epic
                if dry_run:
                    query = """
                        SELECT epic_id, task_id, sub_task_id, type, epic_name, task_name, sub_task_name
                        FROM ai_proma.task_info 
                        WHERE epic_id = $1 AND workspace_id = $2 AND user_id = $3
                        ORDER BY type DESC
                    """
                else:
                    query = """
                        DELETE FROM ai_proma.task_info 
                        WHERE epic_id = $1 AND workspace_id = $2 AND user_id = $3
                        RETURNING epic_id, task_id, sub_task_id, type, epic_name, task_name, sub_task_name
                    """
                query_params = [item_id, workspace_id, user_id]
                
            elif item_type == "Task":
                # Xóa Task + tất cả Sub_task thuộc Task
                if dry_run:
                    query = """
                        SELECT epic_id, task_id, sub_task_id, type, epic_name, task_name, sub_task_name
                        FROM ai_proma.task_info 
                        WHERE (task_id = $1 OR (sub_task_id IS NOT NULL AND task_id = $1))
                        AND workspace_id = $2 AND user_id = $3
                        ORDER BY type DESC
                    """
                else:
                    query = """
                        DELETE FROM ai_proma.task_info 
                        WHERE (task_id = $1 OR (sub_task_id IS NOT NULL AND task_id = $1))
                        AND workspace_id = $2 AND user_id = $3
                        RETURNING epic_id, task_id, sub_task_id, type, epic_name, task_name, sub_task_name
                    """
                query_params = [item_id, workspace_id, user_id]
                
            else:  # Sub_task
                # Chỉ xóa Sub_task
                if dry_run:
                    query = """
                        SELECT epic_id, task_id, sub_task_id, type, epic_name, task_name, sub_task_name
                        FROM ai_proma.task_info 
                        WHERE sub_task_id = $1 AND workspace_id = $2 AND user_id = $3
                    """
                else:
                    query = """
                        DELETE FROM ai_proma.task_info 
                        WHERE sub_task_id = $1 AND workspace_id = $2 AND user_id = $3
                        RETURNING epic_id, task_id, sub_task_id, type, epic_name, task_name, sub_task_name
                    """
                query_params = [item_id, workspace_id, user_id]
            
            # 3. Execute query
            logger.info(f"Executing {'preview' if dry_run else 'delete'} query for {item_type}")
            
            if dry_run:
                results = await conn.fetch(query, *query_params)
            else:
                # Sử dụng transaction cho delete
                async with conn.transaction():
                    results = await conn.fetch(query, *query_params)
            
            logger.info(f"Query returned {len(results)} affected rows")
            
            # 4. Process results
            deleted_count = {"epic": 0, "task": 0, "subtask": 0}
            affected_ids = []
            
            for row in results:
                row_type = row["type"]
                
                if row_type == "Epic":
                    deleted_count["epic"] += 1
                    affected_ids.append(row["epic_id"])
                elif row_type == "Task":
                    deleted_count["task"] += 1
                    affected_ids.append(row["task_id"])
                elif row_type == "Sub_task":
                    deleted_count["subtask"] += 1
                    affected_ids.append(row["sub_task_id"])
            
            # 5. Validate có items để xóa
            if not results:
                raise HTTPException(
                    status_code=404,
                    detail=f"Item {item_id} not found or not owned by user"
                )
            
            # 6. Build response message
            total_items = sum(deleted_count.values())
            action = "Would delete" if dry_run else "Deleted"
            
            parts = []
            if deleted_count["epic"] > 0:
                parts.append(f"{deleted_count['epic']} epic(s)")
            if deleted_count["task"] > 0:
                parts.append(f"{deleted_count['task']} task(s)")
            if deleted_count["subtask"] > 0:
                parts.append(f"{deleted_count['subtask']} subtask(s)")
            
            message = f"{action} {', '.join(parts)} (total: {total_items} items)"
            
            logger.info(f"Delete cascade completed: {message}")
            
            return DeleteTaskResponse(
                status="success",
                message=message,
                deleted_count=deleted_count,
                affected_ids=affected_ids,
                dry_run=dry_run
            )
            
        except Exception as e:
            logger.error(f"Error in delete_task_cascade: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise Exception(f"Failed to delete task cascade: {str(e)}")
        finally:
            if conn:
                await conn.close()

    async def get_task_by_id_cascade(
        self, 
        item_id: str,
        workspace_id: str, 
        user_id: str
    ) -> GetTaskResponse:
        """
        Lấy Epic/Task/Sub_task theo ID với cascade logic
        
        Args:
            item_id: ID của item cần lấy
            workspace_id: ID workspace
            user_id: ID user
        
        Returns:
            GetTaskResponse với item chính + related items
        """
        conn = None
        try:
            # 1. Detect type từ ID prefix
            item_type = self.detect_type_from_id(item_id)
            logger.info(f"Detected type: {item_type} for item_id: {item_id}")
            
            conn = await get_db_connection()
            
            # 2. Build cascade query dựa trên type
            if item_type == "Epic":
                # Get Epic + tất cả Task + tất cả Sub_task thuộc Epic
                query = """
                    SELECT 
                        TRIM(workspace_id) as workspace_id, TRIM(user_id) as user_id, 
                        TRIM(epic_id) as epic_id, TRIM(epic_name) as epic_name,
                        TRIM(task_id) as task_id, TRIM(task_name) as task_name, 
                        TRIM(sub_task_id) as sub_task_id, TRIM(sub_task_name) as sub_task_name,
                        TRIM(description) as description, TRIM(category) as category, 
                        TRIM(priority) as priority, TRIM(status) as status,
                        TRIM(assignee_id) as assignee_id, TRIM(assignee_name) as assignee_name, 
                        TRIM(start_date) as start_date, TRIM(due_date) as due_date,
                        TRIM(deadline_extend) as deadline_extend, TRIM(type) as type, 
                        TRIM(create_at) as create_at, TRIM(update_at) as update_at
                    FROM ai_proma.task_info 
                    WHERE epic_id = $1 AND workspace_id = $2 AND user_id = $3
                    ORDER BY 
                        CASE type 
                            WHEN 'Epic' THEN 1 
                            WHEN 'Task' THEN 2 
                            WHEN 'Sub_task' THEN 3 
                        END, create_at ASC
                """
                query_params = [item_id, workspace_id, user_id]
                
            elif item_type == "Task":
                # Get Task + tất cả Sub_task thuộc Task
                query = """
                    SELECT 
                        TRIM(workspace_id) as workspace_id, TRIM(user_id) as user_id, 
                        TRIM(epic_id) as epic_id, TRIM(epic_name) as epic_name,
                        TRIM(task_id) as task_id, TRIM(task_name) as task_name, 
                        TRIM(sub_task_id) as sub_task_id, TRIM(sub_task_name) as sub_task_name,
                        TRIM(description) as description, TRIM(category) as category, 
                        TRIM(priority) as priority, TRIM(status) as status,
                        TRIM(assignee_id) as assignee_id, TRIM(assignee_name) as assignee_name, 
                        TRIM(start_date) as start_date, TRIM(due_date) as due_date,
                        TRIM(deadline_extend) as deadline_extend, TRIM(type) as type, 
                        TRIM(create_at) as create_at, TRIM(update_at) as update_at
                    FROM ai_proma.task_info 
                    WHERE (task_id = $1 OR (sub_task_id IS NOT NULL AND task_id = $1))
                    AND workspace_id = $2 AND user_id = $3
                    ORDER BY 
                        CASE type 
                            WHEN 'Task' THEN 1 
                            WHEN 'Sub_task' THEN 2 
                        END, create_at ASC
                """
                query_params = [item_id, workspace_id, user_id]
                
            else:  # Sub_task
                # Chỉ get Sub_task
                query = """
                    SELECT 
                        TRIM(workspace_id) as workspace_id, TRIM(user_id) as user_id, 
                        TRIM(epic_id) as epic_id, TRIM(epic_name) as epic_name,
                        TRIM(task_id) as task_id, TRIM(task_name) as task_name, 
                        TRIM(sub_task_id) as sub_task_id, TRIM(sub_task_name) as sub_task_name,
                        TRIM(description) as description, TRIM(category) as category, 
                        TRIM(priority) as priority, TRIM(status) as status,
                        TRIM(assignee_id) as assignee_id, TRIM(assignee_name) as assignee_name, 
                        TRIM(start_date) as start_date, TRIM(due_date) as due_date,
                        TRIM(deadline_extend) as deadline_extend, TRIM(type) as type, 
                        TRIM(create_at) as create_at, TRIM(update_at) as update_at
                    FROM ai_proma.task_info 
                    WHERE sub_task_id = $1 AND workspace_id = $2 AND user_id = $3
                """
                query_params = [item_id, workspace_id, user_id]
            
            # 3. Execute query
            logger.info(f"Executing get cascade query for {item_type}")
            results = await conn.fetch(query, *query_params)
            logger.info(f"Query returned {len(results)} rows")
            
            # 4. Validate có items
            if not results:
                raise HTTPException(
                    status_code=404,
                    detail=f"Item {item_id} not found or not owned by user"
                )
            
            # 5. Convert results thành EpicResponse objects
            items = []
            for row in results:
                try:
                    item = EpicResponse(
                        workspace_id=row["workspace_id"] or workspace_id,
                        user_id=row["user_id"] or user_id,
                        epic_id=row["epic_id"] or "unknown",
                        epic_name=row["epic_name"] or "Untitled Epic",
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
                        start_date=row["start_date"] or "01/01/2025 00:00:00",
                        due_date=row["due_date"] or "01/01/2025 00:00:00",
                        deadline_extend=row["deadline_extend"],
                        type=TypeEnum(row["type"]) if row["type"] else TypeEnum.EPIC,
                        create_at=row["create_at"] or "01/01/2025 00:00:00",
                        update_at=row["update_at"] or "01/01/2025 00:00:00"
                    )
                    items.append(item)
                    
                    # Log item name dựa trên type
                    item_name = row.get("epic_name") or row.get("task_name") or row.get("sub_task_name") or "Unnamed"
                    logger.info(f"Successfully converted {row.get('type')}: {item_name}")
                    
                except Exception as e:
                    logger.error(f"Error converting row to EpicResponse: {e}")
                    logger.error(f"Row data: {dict(row)}")
                    continue
            
            # 6. Build response message
            total_items = len(items)
            
            # Count by type for message
            type_counts = {"Epic": 0, "Task": 0, "Sub_task": 0}
            for item in items:
                type_counts[item.type.value] += 1
            
            # Build message parts
            parts = []
            if type_counts["Epic"] > 0:
                parts.append(f"{type_counts['Epic']} epic(s)")
            if type_counts["Task"] > 0:
                parts.append(f"{type_counts['Task']} task(s)")
            if type_counts["Sub_task"] > 0:
                parts.append(f"{type_counts['Sub_task']} subtask(s)")
            
            message = f"Found {', '.join(parts)} for {item_type} {item_id}"
            
            logger.info(f"Get cascade completed: {message}")
            
            return GetTaskResponse(
                status="success",
                message=message,
                item_type=item_type,
                total_count=total_items,
                items=items
            )
            
        except HTTPException:
            # Re-raise HTTP exceptions (like 404)
            raise
        except Exception as e:
            logger.error(f"Error in get_task_by_id_cascade: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise Exception(f"Failed to get task cascade: {str(e)}")
        finally:
            if conn:
                await conn.close()

    async def update_task_by_type(
        self,
        request: UpdateTaskRequest,
        item_type: str,  # "Epic", "Task", "Sub_task"
        item_id: str,
        workspace_id: str,
        user_id: str
    ) -> UpdateTaskResponse:
        """
        Update Epic/Task/Sub_task theo type và ID
        
        Args:
            request: UpdateTaskRequest với fields cần update
            item_type: "Epic", "Task", "Sub_task"
            item_id: ID của item cần update
            workspace_id: ID workspace
            user_id: ID user
        """
        conn = None
        try:
            conn = await get_db_connection()
            
            # 1. Build dynamic UPDATE fields
            update_fields = []
            params = []
            param_count = 1
            
            # 2. Handle type-specific name field
            if item_type == "Epic" and request.epic_name:
                update_fields.append(f"epic_name = ${param_count}")
                params.append(request.epic_name.strip())
                param_count += 1
            elif item_type == "Task" and request.task_name:
                update_fields.append(f"task_name = ${param_count}")
                params.append(request.task_name.strip())
                param_count += 1
            elif item_type == "Sub_task" and request.sub_task_name:
                update_fields.append(f"sub_task_name = ${param_count}")
                params.append(request.sub_task_name.strip())
                param_count += 1
            
            # 3. Handle common fields
            if request.description is not None:
                update_fields.append(f"description = ${param_count}")
                params.append(request.description.strip() if request.description else None)
                param_count += 1
                
            if request.category is not None:
                update_fields.append(f"category = ${param_count}")
                params.append(request.category.strip() if request.category else None)
                param_count += 1
                
            if request.priority is not None:
                update_fields.append(f"priority = ${param_count}")
                params.append(request.priority.value)
                param_count += 1
                
            if request.status is not None:
                update_fields.append(f"status = ${param_count}")
                params.append(request.status.value)
                param_count += 1
                
            if request.start_date is not None:
                update_fields.append(f"start_date = ${param_count}")
                params.append(request.start_date.strip() if request.start_date else None)
                param_count += 1
                
            if request.due_date is not None:
                update_fields.append(f"due_date = ${param_count}")
                params.append(request.due_date.strip() if request.due_date else None)
                param_count += 1
                
            if request.deadline_extend is not None:
                update_fields.append(f"deadline_extend = ${param_count}")
                params.append(request.deadline_extend.strip() if request.deadline_extend else None)
                param_count += 1
            
            # 4. Handle assignee fields
            assignee_id = None
            assignee_name = None
            
            if request.assignee_name:
                # Lookup assignee từ team_info
                assignee_info = await self.get_assignee_info(request.assignee_name.strip())
                if assignee_info:
                    assignee_id = assignee_info["member_id"]
                    assignee_name = assignee_info["member_name"]
                    logger.info(f"Found assignee: {assignee_name} ({assignee_id})")
                else:
                    logger.warning(f"Assignee not found: {request.assignee_name}")
                    assignee_name = request.assignee_name.strip()
                    
                update_fields.append(f"assignee_id = ${param_count}")
                params.append(assignee_id)
                param_count += 1
                
                update_fields.append(f"assignee_name = ${param_count}")
                params.append(assignee_name)
                param_count += 1
                
            elif request.assignee_id is not None:
                update_fields.append(f"assignee_id = ${param_count}")
                params.append(request.assignee_id.strip() if request.assignee_id else None)
                param_count += 1
            
            # 5. Auto-set update_at
            update_fields.append(f"update_at = ${param_count}")
            params.append(self.get_vietnam_datetime())
            param_count += 1
            
            # 6. Check if có fields để update
            if len(update_fields) <= 1:  # Chỉ có update_at
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No fields to update"
                )
            
            # 7. Build WHERE clause theo type
            if item_type == "Epic":
                where_clause = f"epic_id = ${param_count} AND workspace_id = ${param_count+1} AND user_id = ${param_count+2}"
            elif item_type == "Task":
                where_clause = f"task_id = ${param_count} AND workspace_id = ${param_count+1} AND user_id = ${param_count+2}"
            else:  # Sub_task
                where_clause = f"sub_task_id = ${param_count} AND workspace_id = ${param_count+1} AND user_id = ${param_count+2}"
            
            params.extend([item_id, workspace_id, user_id])
            
            # 8. Execute UPDATE query
            query = f"""
                UPDATE ai_proma.task_info 
                SET {', '.join(update_fields)}
                WHERE {where_clause}
                RETURNING 
                    TRIM(workspace_id) as workspace_id, TRIM(user_id) as user_id, 
                    TRIM(epic_id) as epic_id, TRIM(epic_name) as epic_name,
                    TRIM(task_id) as task_id, TRIM(task_name) as task_name, 
                    TRIM(sub_task_id) as sub_task_id, TRIM(sub_task_name) as sub_task_name,
                    TRIM(description) as description, TRIM(category) as category, 
                    TRIM(priority) as priority, TRIM(status) as status,
                    TRIM(assignee_id) as assignee_id, TRIM(assignee_name) as assignee_name, 
                    TRIM(start_date) as start_date, TRIM(due_date) as due_date,
                    TRIM(deadline_extend) as deadline_extend, TRIM(type) as type, 
                    TRIM(create_at) as create_at, TRIM(update_at) as update_at
            """
            
            logger.info(f"Executing update query for {item_type}")
            logger.debug(f"Query: {query}")
            logger.debug(f"Params: {params}")
            
            result = await conn.fetchrow(query, *params)
            
            if not result:
                raise HTTPException(
                    status_code=404,
                    detail=f"{item_type} {item_id} not found or not owned by user"
                )
            
            # 9. Convert result to EpicResponse
            updated_item = EpicResponse(
                workspace_id=result["workspace_id"] or workspace_id,
                user_id=result["user_id"] or user_id,
                epic_id=result["epic_id"] or "unknown",
                epic_name=result["epic_name"] or "Untitled Epic",
                task_id=result["task_id"],
                task_name=result["task_name"],
                sub_task_id=result["sub_task_id"],
                sub_task_name=result["sub_task_name"],
                description=result["description"],
                category=result["category"],
                priority=PriorityEnum(result["priority"]) if result["priority"] else PriorityEnum.MEDIUM,
                status=StatusEnum(result["status"]) if result["status"] else StatusEnum.TODO,
                assignee_id=result["assignee_id"],
                assignee_name=result["assignee_name"],
                start_date=result["start_date"] or "01/01/2025",
                due_date=result["due_date"] or "01/01/2025",
                deadline_extend=result["deadline_extend"],
                type=TypeEnum(result["type"]) if result["type"] else TypeEnum.EPIC,
                create_at=result["create_at"] or "01/01/2025",
                update_at=result["update_at"] or "01/01/2025"
            )
            
            # 10. Build response message
            item_name = result.get("epic_name") or result.get("task_name") or result.get("sub_task_name") or "Unnamed"
            message = f"Successfully updated {item_type}: {item_name}"
            
            logger.info(f"Update completed: {message}")
            
            return UpdateTaskResponse(
                status="success",
                message=message,
                updated_item=updated_item
            )
            
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            logger.error(f"Error in update_task_by_type: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise Exception(f"Failed to update {item_type}: {str(e)}")
        finally:
            if conn:
                await conn.close()

# Singleton instance
epic_service = EpicService()
