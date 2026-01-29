"""CareTask API endpoints"""
from typing import List, Optional
from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.care_task import CareTaskCreate, CareTaskUpdate, CareTaskResponse, CareTaskComplete
from app.repositories.care_task_repository import CareTaskRepository
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.care_task import TaskStatus, TaskSource, RecurrenceFrequency

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=CareTaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task_data: CareTaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new manual task"""
    repo = CareTaskRepository(db)
    task = repo.create(
        user_id=current_user.id,
        planting_event_id=task_data.planting_event_id,
        task_type=task_data.task_type,
        title=task_data.title,
        description=task_data.description,
        due_date=task_data.due_date,
        priority=task_data.priority,
        is_recurring=task_data.is_recurring,
        recurrence_frequency=task_data.recurrence_frequency,
        task_source=TaskSource.MANUAL
    )
    return task


@router.get("", response_model=List[CareTaskResponse])
def get_tasks(
    status_filter: Optional[TaskStatus] = Query(None, alias="status"),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get tasks for current user.
    Can filter by status and date range.
    """
    repo = CareTaskRepository(db)

    if start_date and end_date:
        tasks = repo.get_by_date_range(current_user.id, start_date, end_date)
    else:
        tasks = repo.get_user_tasks(current_user.id, status=status_filter)

    return tasks


@router.get("/{task_id}", response_model=CareTaskResponse)
def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific task"""
    repo = CareTaskRepository(db)
    task = repo.get_by_id(task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    if task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this task"
        )

    return task


@router.patch("/{task_id}", response_model=CareTaskResponse)
def update_task(
    task_id: int,
    task_data: CareTaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a task"""
    repo = CareTaskRepository(db)
    task = repo.get_by_id(task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    if task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this task"
        )

    update_data = task_data.model_dump(exclude_unset=True)
    task = repo.update(task, **update_data)

    return task


@router.post("/{task_id}/complete", response_model=CareTaskResponse)
def complete_task(
    task_id: int,
    completion_data: CareTaskComplete,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a task as completed and generate next occurrence if recurring"""
    repo = CareTaskRepository(db)
    task = repo.get_by_id(task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    if task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to complete this task"
        )

    completed_date = completion_data.completed_date or date.today()
    task = repo.complete_task(task, completed_date, completion_data.notes)

    # Generate next occurrence if task is recurring
    if task.is_recurring and task.recurrence_frequency:
        frequency_days = {
            RecurrenceFrequency.DAILY: 1,
            RecurrenceFrequency.WEEKLY: 7,
            RecurrenceFrequency.BIWEEKLY: 14,
            RecurrenceFrequency.MONTHLY: 30,
        }.get(task.recurrence_frequency)

        if frequency_days:
            next_due_date = task.due_date + timedelta(days=frequency_days)
            repo.create(
                user_id=task.user_id,
                planting_event_id=task.planting_event_id,
                task_type=task.task_type,
                title=task.title,
                description=task.description,
                due_date=next_due_date,
                priority=task.priority,
                is_recurring=True,
                recurrence_frequency=task.recurrence_frequency,
                parent_task_id=task.id,
                task_source=task.task_source
            )

    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a task"""
    repo = CareTaskRepository(db)
    task = repo.get_by_id(task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    if task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this task"
        )

    repo.delete(task)
