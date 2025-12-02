"""
Pydantic schemas for task management
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class TaskBase(BaseModel):
    """Base task schema"""
    title: str
    description: Optional[str] = None
    priority: Optional[int] = 1


class TaskCreate(TaskBase):
    """Task creation request schema"""
    assigned_to_id: int


class TaskUpdate(BaseModel):
    """Task update request schema"""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[int] = None
    feedback: Optional[str] = None
    score: Optional[int] = None


class TaskResponse(BaseModel):
    """Task response schema"""
    id: int
    title: str
    description: Optional[str]
    status: str
    priority: int
    created_by_id: int
    assigned_to_id: int
    feedback: Optional[str]
    score: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    # Related user information
    creator_name: str
    assignee_name: str
    
    class Config:
        from_attributes = True


class TaskFilter(BaseModel):
    """Task filtering parameters"""
    status: Optional[str] = None
    assignee: Optional[int] = None
    created_by: Optional[int] = None


class TaskListResponse(BaseModel):
    """Task list response schema"""
    tasks: List[TaskResponse]
    total: int
    page: int
    per_page: int
    pages: int