"""
Database Models for Proma AI
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID
import hashlib

class User(Base):
    """User model for authentication - matches existing DB table"""
    __tablename__ = "users_proma"
    __table_args__ = {"schema": "ai_proma"}
    
    user_id = Column(String, primary_key=True)  # Matches existing table structure
    user_name = Column(String(50), unique=True, nullable=False, index=True)
    user_pass = Column(String(255), nullable=False)  # Hashed password
    
    # Relationships
    sessions = relationship("ChatSession", back_populates="user")
    messages = relationship("ChatMessage", back_populates="user")
    
    def set_password(self, password: str):
        """Hash and set password"""
        self.user_pass = hashlib.sha256(password.encode()).hexdigest()
    
    def check_password(self, password: str) -> bool:
        """Check if password matches"""
        return self.user_pass == hashlib.sha256(password.encode()).hexdigest()

class Agent(Base):
    """AI Agent model"""
    __tablename__ = "agents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    agent_id = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    system_prompt = Column(Text, nullable=True)
    model_config = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    sessions = relationship("ChatSession", back_populates="agent")
    messages = relationship("ChatMessage", back_populates="agent")

class ChatSession(Base):
    """Chat session model"""
    __tablename__ = "chat_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(100), unique=True, nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.user_id"), nullable=False)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=False)
    title = Column(String(200), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    agent = relationship("Agent", back_populates="sessions")
    messages = relationship("ChatMessage", back_populates="session", order_by="ChatMessage.created_at")

class ChatMessage(Base):
    """Chat message model"""
    __tablename__ = "chat_messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("chat_sessions.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.user_id"), nullable=False)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=False)
    content = Column(Text, nullable=False)
    message_type = Column(String(20), nullable=False)  # 'user' or 'agent'
    message_metadata = Column(JSON, nullable=True)  # Store images, files, etc.
    tokens_used = Column(Integer, nullable=True)
    response_time = Column(Integer, nullable=True)  # milliseconds
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages")
    user = relationship("User", back_populates="messages")
    agent = relationship("Agent", back_populates="messages")

class ApiUsage(Base):
    """API usage tracking"""
    __tablename__ = "api_usage"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.user_id"), nullable=False)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=False)
    endpoint = Column(String(100), nullable=False)
    tokens_used = Column(Integer, nullable=False, default=0)
    cost = Column(String(20), nullable=True)  # Store as string to avoid float precision issues
    response_time = Column(Integer, nullable=True)  # milliseconds
    status_code = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SystemLog(Base):
    """System logs"""
    __tablename__ = "system_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    level = Column(String(20), nullable=False)  # INFO, WARNING, ERROR, etc.
    message = Column(Text, nullable=False)
    module = Column(String(100), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.user_id"), nullable=True)
    log_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
