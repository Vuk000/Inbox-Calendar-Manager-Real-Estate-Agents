"""
Task management router - Convert emails to tasks
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from datetime import date

from ..db import get_db
from ..models.user import User
from ..models.task import Task, TaskType, TaskStatus
from ..models.message import Message
from ..models.property import Property
from datetime import date as date_type
from ..dependencies import get_current_user
from ..security.audit import log_action

router = APIRouter()


# Pydantic schemas
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    task_type: str
    due_date: Optional[date] = None
    due_time: Optional[str] = None
    priority: str = "medium"
    message_id: Optional[int] = None
    property_id: Optional[int] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[date] = None
    due_time: Optional[str] = None
    priority: Optional[str] = None
    completion_notes: Optional[str] = None


class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    task_type: str
    status: str
    priority: str
    due_date: Optional[date]
    due_time: Optional[str]
    is_completed: bool
    completed_at: Optional[datetime]
    created_at: datetime
    message_id: Optional[int]
    property_id: Optional[int]
    
    class Config:
        from_attributes = True


@router.get("/tasks", response_model=List[TaskResponse])
async def list_tasks(
    status: Optional[str] = Query(None),
    task_type: Optional[str] = Query(None),
    property_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List tasks with optional filtering.
    
    - **status**: Filter by status (todo, in_progress, done, cancelled)
    - **task_type**: Filter by type (showing, inspection, etc.)
    - **property_id**: Filter by property
    """
    query = db.query(Task).filter(Task.user_id == current_user.id)
    
    if status:
        try:
            query = query.filter(Task.status == TaskStatus(status))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status}"
            )
    
    if task_type:
        try:
            query = query.filter(Task.task_type == TaskType(task_type))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid task_type: {task_type}"
            )
    
    if property_id:
        query = query.filter(Task.property_id == property_id)
    
    tasks = query.order_by(
        Task.is_completed,
        Task.due_date.asc().nullslast(),
        Task.created_at.desc()
    ).all()
    
    return tasks


@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new task.
    
    - **title**: Task title
    - **task_type**: Type of task
    - **due_date**: Optional due date
    - **message_id**: Optional linked email
    - **property_id**: Optional linked property
    """
    try:
        task_type_enum = TaskType(task_data.task_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid task_type: {task_data.task_type}"
        )
    
    new_task = Task(
        user_id=current_user.id,
        title=task_data.title,
        description=task_data.description,
        task_type=task_type_enum,
        due_date=task_data.due_date,
        due_time=task_data.due_time,
        priority=task_data.priority,
        message_id=task_data.message_id,
        property_id=task_data.property_id,
        status=TaskStatus.TODO
    )
    
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    
    # Log action
    await log_action(
        db=db,
        action="create_task",
        user_id=current_user.id,
        resource_type="task",
        resource_id=new_task.id,
        description=f"Created task: {new_task.title}"
    )
    
    return new_task


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific task"""
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return task


@router.patch("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a task.
    
    - **task_id**: Task ID
    - **status**: Update status
    - **title**: Update title
    - Other fields as needed
    """
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Update fields
    if task_update.title:
        task.title = task_update.title
    if task_update.description is not None:
        task.description = task_update.description
    if task_update.status:
        try:
            task.status = TaskStatus(task_update.status)
            if task.status == TaskStatus.DONE and not task.is_completed:
                task.is_completed = True
                task.completed_at = datetime.utcnow()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {task_update.status}"
            )
    if task_update.due_date is not None:
        task.due_date = task_update.due_date
    if task_update.due_time is not None:
        task.due_time = task_update.due_time
    if task_update.priority:
        task.priority = task_update.priority
    if task_update.completion_notes:
        task.completion_notes = task_update.completion_notes
    
    db.commit()
    db.refresh(task)
    
    return task


@router.delete("/tasks/{task_id}")
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a task"""
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    db.delete(task)
    db.commit()
    
    return {"success": True, "task_id": task_id}


@router.get("/tasks/stats/summary")
async def get_task_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get task statistics"""
    total = db.query(Task).filter(Task.user_id == current_user.id).count()
    todo = db.query(Task).filter(
        Task.user_id == current_user.id,
        Task.status == TaskStatus.TODO
    ).count()
    in_progress = db.query(Task).filter(
        Task.user_id == current_user.id,
        Task.status == TaskStatus.IN_PROGRESS
    ).count()
    done = db.query(Task).filter(
        Task.user_id == current_user.id,
        Task.status == TaskStatus.DONE
    ).count()
    overdue = db.query(Task).filter(
        Task.user_id == current_user.id,
        Task.status.in_([TaskStatus.TODO, TaskStatus.IN_PROGRESS]),
        Task.due_date < date.today()
    ).count()
    
    return {
        "total": total,
        "todo": todo,
        "in_progress": in_progress,
        "done": done,
        "overdue": overdue
    }

