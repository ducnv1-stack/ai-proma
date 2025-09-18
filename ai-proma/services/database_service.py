"""
Database Service Layer for Proma AI
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from models import User, Agent, ChatSession, ChatMessage, ApiUsage
import uuid
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DatabaseService:
    """Database service for Proma AI operations"""
    
    @staticmethod
    async def create_user(
        db: AsyncSession,
        username: str,
        workspace_id: str,
        email: Optional[str] = None,
        full_name: Optional[str] = None
    ) -> User:
        """Create a new user"""
        try:
            user = User(
                username=username,
                email=email,
                full_name=full_name,
                workspace_id=workspace_id
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
            logger.info(f"Created user: {username}")
            return user
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to create user {username}: {e}")
            raise
    
    @staticmethod
    async def get_user_by_username(
        db: AsyncSession,
        username: str,
        workspace_id: str
    ) -> Optional[User]:
        """Get user by username and workspace"""
        try:
            result = await db.execute(
                select(User).where(
                    and_(
                        User.username == username,
                        User.workspace_id == workspace_id,
                        User.is_active == True
                    )
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get user {username}: {e}")
            return None
    
    @staticmethod
    async def create_agent(
        db: AsyncSession,
        name: str,
        agent_id: str,
        description: Optional[str] = None,
        system_prompt: Optional[str] = None,
        model_config: Optional[Dict] = None
    ) -> Agent:
        """Create a new agent"""
        try:
            agent = Agent(
                name=name,
                agent_id=agent_id,
                description=description,
                system_prompt=system_prompt,
                model_config=model_config
            )
            db.add(agent)
            await db.commit()
            await db.refresh(agent)
            logger.info(f"Created agent: {name}")
            return agent
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to create agent {name}: {e}")
            raise
    
    @staticmethod
    async def get_agent_by_id(
        db: AsyncSession,
        agent_id: str
    ) -> Optional[Agent]:
        """Get agent by agent_id"""
        try:
            result = await db.execute(
                select(Agent).where(
                    and_(
                        Agent.agent_id == agent_id,
                        Agent.is_active == True
                    )
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get agent {agent_id}: {e}")
            return None
    
    @staticmethod
    async def create_chat_session(
        db: AsyncSession,
        session_id: str,
        user_id: uuid.UUID,
        agent_id: uuid.UUID,
        title: Optional[str] = None
    ) -> ChatSession:
        """Create a new chat session"""
        try:
            session = ChatSession(
                session_id=session_id,
                user_id=user_id,
                agent_id=agent_id,
                title=title
            )
            db.add(session)
            await db.commit()
            await db.refresh(session)
            logger.info(f"Created chat session: {session_id}")
            return session
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to create session {session_id}: {e}")
            raise
    
    @staticmethod
    async def get_chat_session(
        db: AsyncSession,
        session_id: str
    ) -> Optional[ChatSession]:
        """Get chat session by session_id"""
        try:
            result = await db.execute(
                select(ChatSession).where(
                    and_(
                        ChatSession.session_id == session_id,
                        ChatSession.is_active == True
                    )
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get session {session_id}: {e}")
            return None
    
    @staticmethod
    async def save_chat_message(
        db: AsyncSession,
        session_id: uuid.UUID,
        user_id: uuid.UUID,
        agent_id: uuid.UUID,
        content: str,
        message_type: str,
        metadata: Optional[Dict] = None,
        tokens_used: Optional[int] = None,
        response_time: Optional[int] = None
    ) -> ChatMessage:
        """Save a chat message"""
        try:
            message = ChatMessage(
                session_id=session_id,
                user_id=user_id,
                agent_id=agent_id,
                content=content,
                message_type=message_type,
                metadata=metadata,
                tokens_used=tokens_used,
                response_time=response_time
            )
            db.add(message)
            await db.commit()
            await db.refresh(message)
            return message
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to save message: {e}")
            raise
    
    @staticmethod
    async def get_chat_history(
        db: AsyncSession,
        session_id: str,
        limit: int = 50
    ) -> List[ChatMessage]:
        """Get chat history for a session"""
        try:
            # First get the session
            session_result = await db.execute(
                select(ChatSession).where(ChatSession.session_id == session_id)
            )
            session = session_result.scalar_one_or_none()
            
            if not session:
                return []
            
            # Get messages
            result = await db.execute(
                select(ChatMessage)
                .where(ChatMessage.session_id == session.id)
                .order_by(desc(ChatMessage.created_at))
                .limit(limit)
            )
            messages = result.scalars().all()
            return list(reversed(messages))  # Return in chronological order
        except Exception as e:
            logger.error(f"Failed to get chat history for {session_id}: {e}")
            return []
    
    @staticmethod
    async def track_api_usage(
        db: AsyncSession,
        user_id: uuid.UUID,
        agent_id: uuid.UUID,
        endpoint: str,
        tokens_used: int,
        response_time: Optional[int] = None,
        status_code: int = 200,
        cost: Optional[str] = None
    ) -> ApiUsage:
        """Track API usage"""
        try:
            usage = ApiUsage(
                user_id=user_id,
                agent_id=agent_id,
                endpoint=endpoint,
                tokens_used=tokens_used,
                response_time=response_time,
                status_code=status_code,
                cost=cost
            )
            db.add(usage)
            await db.commit()
            await db.refresh(usage)
            return usage
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to track API usage: {e}")
            raise
    
    @staticmethod
    async def get_user_stats(
        db: AsyncSession,
        user_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Get user statistics"""
        try:
            # Count sessions
            sessions_result = await db.execute(
                select(ChatSession).where(ChatSession.user_id == user_id)
            )
            sessions_count = len(sessions_result.scalars().all())
            
            # Count messages
            messages_result = await db.execute(
                select(ChatMessage).where(ChatMessage.user_id == user_id)
            )
            messages_count = len(messages_result.scalars().all())
            
            # Sum tokens used
            usage_result = await db.execute(
                select(ApiUsage).where(ApiUsage.user_id == user_id)
            )
            usage_records = usage_result.scalars().all()
            total_tokens = sum(record.tokens_used for record in usage_records)
            
            return {
                "sessions_count": sessions_count,
                "messages_count": messages_count,
                "total_tokens_used": total_tokens,
                "api_calls": len(usage_records)
            }
        except Exception as e:
            logger.error(f"Failed to get user stats for {user_id}: {e}")
            return {
                "sessions_count": 0,
                "messages_count": 0,
                "total_tokens_used": 0,
                "api_calls": 0
            }
