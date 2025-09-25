from typing import Optional, Dict, Any
from datetime import datetime
import uuid
import pytz
from src.database.postgres import get_db_connection
from src.api.schemas.members import CreateMemberRequest, CreateMemberResponse, ListMembersResponse, MemberInfo, UpdateMemberRequest, UpdateMemberResponse
import logging

logger = logging.getLogger(__name__)

class MemberService:
    def __init__(self):
        self.vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')  # UTC+7
    
    def generate_member_id(self) -> str:
        """Tạo member_id 32 ký tự"""
        return uuid.uuid4().hex  # Tạo UUID và lấy hex string (32 ký tự)
    
    async def create_member(
        self, 
        request: CreateMemberRequest, 
        user_id: str, 
        workspace_id: str
    ) -> CreateMemberResponse:
        """Tạo member mới trong database"""
        
        # 1. Tạo member_id 32 ký tự
        member_id = self.generate_member_id()
        
        # 2. Tạo thời gian hiện tại theo múi giờ Việt Nam
        current_time = datetime.now(self.vietnam_tz).strftime('%d/%m/%Y %H:%M:%S')
        
        # 3. Chuẩn bị dữ liệu để insert
        member_data = {
            "workspace_id": workspace_id,
            "user_id": user_id,
            "member_id": member_id,
            "member_name": request.member_name,
            "team": request.team,
            "email": request.email,
            "created_at": current_time,
            "updated_at": None
        }
        
        logger.info(f"Creating member: {request.member_name} with ID: {member_id}")
        
        # 4. Insert vào database
        conn = None
        try:
            conn = await get_db_connection()
            insert_query = """
                INSERT INTO ai_proma.team_info (
                    workspace_id, user_id, member_id, member_name,
                    team, email, created_at, updated_at
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7, $8
                )
            """
            
            await conn.execute(
                insert_query,
                member_data["workspace_id"], member_data["user_id"], 
                member_data["member_id"], member_data["member_name"],
                member_data["team"], member_data["email"], 
                member_data["created_at"], member_data["updated_at"]
            )
            
            logger.info(f"Member created successfully: {member_id}")
            
            # 5. Trả về CreateMemberResponse
            return CreateMemberResponse(
                workspace_id=member_data["workspace_id"],
                user_id=member_data["user_id"],
                member_id=member_data["member_id"],
                member_name=member_data["member_name"],
                team=member_data["team"],
                email=member_data["email"],
                created_at=member_data["created_at"],
                updated_at=member_data["updated_at"]
            )
            
        except Exception as e:
            logger.error(f"Error creating member: {e}")
            raise Exception(f"Failed to create member: {str(e)}")
        finally:
            if conn:
                await conn.close()

    async def list_members(
        self, 
        workspace_id: str, 
        user_id: str
    ) -> ListMembersResponse:
        """Lấy danh sách members theo workspace_id và user_id"""
        
        logger.info(f"Listing members for workspace: {workspace_id}, user: {user_id}")
        
        conn = None
        try:
            conn = await get_db_connection()
            query = """
                SELECT workspace_id, user_id, member_id, member_name, team, email, created_at
                FROM ai_proma.team_info 
                WHERE workspace_id = $1 AND user_id = $2
                ORDER BY created_at DESC
            """
            
            results = await conn.fetch(query, workspace_id, user_id)
            logger.info(f"Found {len(results)} members")
            
            # Convert results thành MemberInfo objects
            members = []
            for row in results:
                member_info = MemberInfo(
                    workspace_id=row["workspace_id"],
                    user_id=row["user_id"],
                    member_id=row["member_id"],
                    member_name=row["member_name"],
                    team=row["team"],
                    email=row["email"],
                    created_at=row["created_at"]
                )
                members.append(member_info)
            
            # Trả về ListMembersResponse
            return ListMembersResponse(
                members=members,
                total=len(members),
                workspace_id=workspace_id,
                user_id=user_id
            )
            
        except Exception as e:
            logger.error(f"Error listing members: {e}")
            raise Exception(f"Failed to list members: {str(e)}")
        finally:
            if conn:
                await conn.close()

    async def update_member(
        self, 
        member_id: str,
        request: UpdateMemberRequest, 
        workspace_id: str, 
        user_id: str
    ) -> UpdateMemberResponse:
        """Update member theo workspace_id, user_id, member_id"""
        
        logger.info(f"Updating member: {member_id} for workspace: {workspace_id}, user: {user_id}")
        
        conn = None
        try:
            conn = await get_db_connection()
            
            # 1. Kiểm tra member có tồn tại không
            check_query = """
                SELECT workspace_id, user_id, member_id, member_name, team, email, created_at
                FROM ai_proma.team_info 
                WHERE workspace_id = $1 AND user_id = $2 AND member_id = $3
            """
            
            existing_member = await conn.fetchrow(check_query, workspace_id, user_id, member_id)
            if not existing_member:
                raise Exception(f"Member not found: {member_id}")
            
            # 2. Chuẩn bị dữ liệu update (chỉ update các field có giá trị)
            update_fields = []
            update_values = []
            param_count = 1
            
            if request.member_name is not None:
                update_fields.append(f"member_name = ${param_count}")
                update_values.append(request.member_name)
                param_count += 1
            
            if request.team is not None:
                update_fields.append(f"team = ${param_count}")
                update_values.append(request.team)
                param_count += 1
            
            if request.email is not None:
                update_fields.append(f"email = ${param_count}")
                update_values.append(request.email)
                param_count += 1
            
            # Luôn update updated_at
            current_time = datetime.now(self.vietnam_tz).strftime('%d/%m/%Y %H:%M:%S')
            update_fields.append(f"updated_at = ${param_count}")
            update_values.append(current_time)
            param_count += 1
            
            # Thêm WHERE conditions
            update_values.extend([workspace_id, user_id, member_id])
            
            # 3. Thực hiện update
            if update_fields:
                update_query = f"""
                    UPDATE ai_proma.team_info 
                    SET {', '.join(update_fields)}
                    WHERE workspace_id = ${param_count} AND user_id = ${param_count + 1} AND member_id = ${param_count + 2}
                """
                
                await conn.execute(update_query, *update_values)
                logger.info(f"Member updated successfully: {member_id}")
            
            # 4. Lấy dữ liệu sau khi update
            updated_member = await conn.fetchrow(check_query, workspace_id, user_id, member_id)
            
            # 5. Trả về UpdateMemberResponse
            return UpdateMemberResponse(
                workspace_id=updated_member["workspace_id"],
                user_id=updated_member["user_id"],
                member_id=updated_member["member_id"],
                member_name=updated_member["member_name"],
                team=updated_member["team"],
                email=updated_member["email"],
                created_at=updated_member["created_at"],
                updated_at=current_time
            )
            
        except Exception as e:
            logger.error(f"Error updating member: {e}")
            raise Exception(f"Failed to update member: {str(e)}")
        finally:
            if conn:
                await conn.close()

# Singleton instance
member_service = MemberService()
