"""CareTask schemas"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from app.models.care_task import TaskType, TaskStatus, TaskSource, TaskPriority, RecurrenceFrequency


class CareTaskCreate(BaseModel):
    """Schema for creating a new care task"""
    planting_event_id: Optional[int] = None
    task_type: TaskType
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    due_date: date
    priority: TaskPriority = TaskPriority.MEDIUM
    is_recurring: bool = False
    recurrence_frequency: Optional[RecurrenceFrequency] = None


class CareTaskUpdate(BaseModel):
    """Schema for updating a care task"""
    task_type: Optional[TaskType] = None
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    due_date: Optional[date] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    is_recurring: Optional[bool] = None
    recurrence_frequency: Optional[RecurrenceFrequency] = None
    notes: Optional[str] = None


class CareTaskComplete(BaseModel):
    """Schema for completing a task"""
    completed_date: Optional[date] = None
    notes: Optional[str] = None


class CareTaskResponse(BaseModel):
    """Schema for care task response"""
    id: int
    user_id: int
    planting_event_id: Optional[int] = None
    task_type: TaskType
    task_source: TaskSource
    title: str
    description: Optional[str] = None
    priority: TaskPriority
    due_date: date
    is_recurring: bool
    recurrence_frequency: Optional[RecurrenceFrequency] = None
    parent_task_id: Optional[int] = None
    status: TaskStatus
    completed_date: Optional[date] = None
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
