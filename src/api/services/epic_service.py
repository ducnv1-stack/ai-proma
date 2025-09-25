from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import uuid
import pytz
from src.database.postgres import get_db_connection
from src.api.schemas.epics import CreateEpicRequest, CreateTaskRequest, EpicResponse, PriorityEnum, StatusEnum, TypeEnum
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
    
    def get_vietnam_datetime(self) -> str:
        """Lấy thởi gian hiện tại theo múi giờ UTC+7"""
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

# Singleton instance
epic_service = EpicService()
