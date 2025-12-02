"""
Tasks router with role-based access control
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models import User, Task, TaskStatus, UserRole
from app.schemas.tasks import TaskCreate, TaskUpdate, TaskResponse, TaskListResponse
from app.routers.auth import get_current_user
from app.auth.security import is_project_manager, is_backend_developer, get_pm_required_exception


router = APIRouter(prefix="/tasks", tags=["tasks"])


# Dependency to check if user is Project Manager
async def require_pm_role(current_user: User = Depends(get_current_user)):
    """
    Require Project Manager role
    """
    if not is_project_manager(current_user.role):
        raise get_pm_required_exception()
    return current_user


# Dependency to check if user is Backend Developer
async def require_dev_role(current_user: User = Depends(get_current_user)):
    """
    Require Backend Developer role (or any authenticated user)
    """
    if not is_backend_developer(current_user.role) and not is_project_manager(current_user.role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid user role"
        )
    return current_user


# Backend Developer endpoints - can only access their own tasks
@router.get("/", response_model=TaskListResponse)
async def get_my_tasks(
    status_filter: Optional[str] = Query(None, description="Filter by task status"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(require_dev_role),
    db: Session = Depends(get_db)
):
    """
    Get tasks for Backend Developer (own tasks only)
    """
    # Build query for user's own tasks
    query = db.query(Task).filter(Task.assigned_to_id == current_user.id)
    
    # Apply status filter if provided
    if status_filter:
        valid_statuses = [status.value for status in TaskStatus]
        if status_filter not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Valid options: {valid_statuses}"
            )
        query = query.filter(Task.status == status_filter)
    
    # Get total count for pagination
    total = query.count()
    
    # Apply pagination and get results
    tasks = query.offset((page - 1) * per_page).limit(per_page).all()
    
    # Convert to response format with user names
    task_responses = []
    for task in tasks:
        task_response = TaskResponse(
            id=task.id,
            title=task.title,
            description=task.description,
            status=task.status,
            priority=task.priority,
            created_by_id=task.created_by_id,
            assigned_to_id=task.assigned_to_id,
            feedback=task.feedback,
            score=task.score,
            created_at=task.created_at,
            updated_at=task.updated_at,
            completed_at=task.completed_at,
            creator_name=task.creator.full_name,
            assignee_name=task.assignee.full_name
        )
        task_responses.append(task_response)
    
    total_pages = (total + per_page - 1) // per_page
    
    return TaskListResponse(
        tasks=task_responses,
        total=total,
        page=page,
        per_page=per_page,
        pages=total_pages
    )


@router.put("/{task_id}/status", response_model=TaskResponse)
async def update_task_status(
    task_id: int,
    status_update: dict,
    current_user: User = Depends(require_dev_role),
    db: Session = Depends(get_db)
):
    """
    Backend Developer can update status of their own tasks
    """
    # Get task and verify ownership
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.assigned_to_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or you don't have permission to access it"
        )
    
    # Validate status
    new_status = status_update.get("status")
    valid_statuses = [status.value for status in TaskStatus]
    
    if new_status not in valid_statuses:
        raise HTTPException(
            status=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Valid options: {valid_statuses}"
        )
    
    # Update status
    task.status = new_status
    
    # Set completed_at if status is completed
    if new_status == TaskStatus.COMPLETED and not task.completed_at:
        from datetime import datetime
        task.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(task)
    
    return TaskResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        created_by_id=task.created_by_id,
        assigned_to_id=task.assigned_to_id,
        feedback=task.feedback,
        score=task.score,
        created_at=task.created_at,
        updated_at=task.updated_at,
        completed_at=task.completed_at,
        creator_name=task.creator.full_name,
        assignee_name=task.assignee.full_name
    )


# Project Manager endpoints - full access to all tasks
@router.get("/all", response_model=TaskListResponse)
async def get_all_tasks(
    status_filter: Optional[str] = Query(None, description="Filter by task status"),
    assignee_filter: Optional[int] = Query(None, description="Filter by assignee ID"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(require_pm_role),
    db: Session = Depends(get_db)
):
    """
    Get all tasks (Project Manager only)
    """
    query = db.query(Task)
    
    # Apply filters
    if status_filter:
        valid_statuses = [status.value for status in TaskStatus]
        if status_filter not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Valid options: {valid_statuses}"
            )
        query = query.filter(Task.status == status_filter)
    
    if assignee_filter:
        query = query.filter(Task.assigned_to_id == assignee_filter)
    
    # Get total count for pagination
    total = query.count()
    
    # Apply pagination and get results
    tasks = query.offset((page - 1) * per_page).limit(per_page).all()
    
    # Convert to response format
    task_responses = []
    for task in tasks:
        task_response = TaskResponse(
            id=task.id,
            title=task.title,
            description=task.description,
            status=task.status,
            priority=task.priority,
            created_by_id=task.created_by_id,
            assigned_to_id=task.assigned_to_id,
            feedback=task.feedback,
            score=task.score,
            created_at=task.created_at,
            updated_at=task.updated_at,
            completed_at=task.completed_at,
            creator_name=task.creator.full_name,
            assignee_name=task.assignee.full_name
        )
        task_responses.append(task_response)
    
    total_pages = (total + per_page - 1) // per_page
    
    return TaskListResponse(
        tasks=task_responses,
        total=total,
        page=page,
        per_page=per_page,
        pages=total_pages
    )


@router.post("/", response_model=TaskResponse)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(require_pm_role),
    db: Session = Depends(get_db)
):
    """
    Create new task (Project Manager only)
    """
    # Verify assignee exists
    assignee = db.query(User).filter(User.id == task_data.assigned_to_id).first()
    if not assignee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignee not found"
        )
    
    # Create task
    db_task = Task(
        title=task_data.title,
        description=task_data.description,
        priority=task_data.priority,
        created_by_id=current_user.id,
        assigned_to_id=task_data.assigned_to_id
    )
    
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    return TaskResponse(
        id=db_task.id,
        title=db_task.title,
        description=db_task.description,
        status=db_task.status,
        priority=db_task.priority,
        created_by_id=db_task.created_by_id,
        assigned_to_id=db_task.assigned_to_id,
        feedback=db_task.feedback,
        score=db_task.score,
        created_at=db_task.created_at,
        updated_at=db_task.updated_at,
        completed_at=db_task.completed_at,
        creator_name=db_task.creator.full_name,
        assignee_name=db_task.assignee.full_name
    )


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    current_user: User = Depends(require_pm_role),
    db: Session = Depends(get_db)
):
    """
    Update task details (Project Manager only)
    """
    # Get task
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Update task fields
    update_data = task_update.dict(exclude_unset=True)
    
    # Validate status if provided
    if "status" in update_data:
        valid_statuses = [status.value for status in TaskStatus]
        if update_data["status"] not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Valid options: {valid_statuses}"
            )
    
    # Validate score if provided
    if "score" in update_data:
        score = update_data["score"]
        if score is not None and (score < 1 or score > 10):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Score must be between 1 and 10"
            )
    
    # Apply updates
    for field, value in update_data.items():
        setattr(task, field, value)
    
    # Set completed_at if status is completed
    if "status" in update_data and update_data["status"] == TaskStatus.COMPLETED and not task.completed_at:
        from datetime import datetime
        task.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(task)
    
    return TaskResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        created_by_id=task.created_by_id,
        assigned_to_id=task.assigned_to_id,
        feedback=task.feedback,
        score=task.score,
        created_at=task.created_at,
        updated_at=task.updated_at,
        completed_at=task.completed_at,
        creator_name=task.creator.full_name,
        assignee_name=task.assignee.full_name
    )


@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    current_user: User = Depends(require_pm_role),
    db: Session = Depends(get_db)
):
    """
    Delete task (Project Manager only)
    """
    # Get task
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Delete task
    db.delete(task)
    db.commit()
    
    return {"message": "Task deleted successfully"}


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task_by_id(
    task_id: int,
    current_user: User = Depends(require_dev_role),
    db: Session = Depends(get_db)
):
    """
    Get task by ID (role-based access)
    """
    # Project Manager can access any task
    if is_project_manager(current_user.role):
        task = db.query(Task).filter(Task.id == task_id).first()
    else:
        # Backend Developer can only access their own tasks
        task = db.query(Task).filter(
            Task.id == task_id,
            Task.assigned_to_id == current_user.id
        ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or you don't have permission to access it"
        )
    
    return TaskResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        created_by_id=task.created_by_id,
        assigned_to_id=task.assigned_to_id,
        feedback=task.feedback,
        score=task.score,
        created_at=task.created_at,
        updated_at=task.updated_at,
        completed_at=task.completed_at,
        creator_name=task.creator.full_name,
        assignee_name=task.assignee.full_name
    )