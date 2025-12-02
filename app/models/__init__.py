"""
Database models for Taskflow API
"""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, Enum, func
from sqlalchemy.orm import relationship
from sqlalchemy import Enum as SQLEnum

from app.database import Base


class UserRole:
    """User roles enum"""
    BACKEND_DEVELOPER = "backend_developer"
    PROJECT_MANAGER = "project_manager"


class TaskStatus:
    """Task status enum"""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"


class User(Base):
    """
    User model with role-based access control
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole.BACKEND_DEVELOPER, UserRole.PROJECT_MANAGER), 
                  default=UserRole.BACKEND_DEVELOPER, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    tasks_created = relationship("Task", back_populates="creator", foreign_keys="Task.created_by_id")
    tasks_assigned = relationship("Task", back_populates="assignee", foreign_keys="Task.assigned_to_id")


class Task(Base):
    """
    Task model for task management
    """
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(SQLEnum(TaskStatus.TODO, TaskStatus.IN_PROGRESS, TaskStatus.COMPLETED, TaskStatus.BLOCKED),
                     default=TaskStatus.TODO, nullable=False)
    priority = Column(Integer, default=1)  # 1=Low, 2=Medium, 3=High
    
    # Foreign Keys
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Task Management Fields
    feedback = Column(Text, nullable=True)
    score = Column(Integer, nullable=True)  # 1-10 score from project manager
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    creator = relationship("User", back_populates="tasks_created", foreign_keys=[created_by_id])
    assignee = relationship("User", back_populates="tasks_assigned", foreign_keys=[assigned_to_id])