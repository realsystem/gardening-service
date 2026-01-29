"""CareTask repository"""
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.care_task import CareTask, TaskType, TaskStatus, TaskSource
from datetime import date


class CareTaskRepository:
    """Repository for CareTask database operations"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: int, task_type: TaskType, title: str,
               due_date: date, task_source: TaskSource = TaskSource.MANUAL, **kwargs) -> CareTask:
        """Create a new care task"""
        task = CareTask(
            user_id=user_id,
            task_type=task_type,
            title=title,
            due_date=due_date,
            task_source=task_source,
            **kwargs
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def get_by_id(self, task_id: int) -> Optional[CareTask]:
        """Get task by ID"""
        return self.db.query(CareTask).filter(CareTask.id == task_id).first()

    def get_user_tasks(self, user_id: int, status: Optional[TaskStatus] = None) -> List[CareTask]:
        """Get all tasks for a user, optionally filtered by status"""
        query = self.db.query(CareTask).filter(CareTask.user_id == user_id)
        if status:
            query = query.filter(CareTask.status == status)
        return query.order_by(CareTask.due_date).all()

    def get_by_date_range(self, user_id: int, start_date: date, end_date: date) -> List[CareTask]:
        """Get tasks within a date range"""
        return self.db.query(CareTask).filter(
            CareTask.user_id == user_id,
            CareTask.due_date >= start_date,
            CareTask.due_date <= end_date
        ).order_by(CareTask.due_date).all()

    def get_planting_tasks(self, planting_event_id: int) -> List[CareTask]:
        """Get all tasks for a specific planting event"""
        return self.db.query(CareTask).filter(
            CareTask.planting_event_id == planting_event_id
        ).order_by(CareTask.due_date).all()

    def update(self, task: CareTask, **kwargs) -> CareTask:
        """Update task"""
        for key, value in kwargs.items():
            if hasattr(task, key) and value is not None:
                setattr(task, key, value)
        self.db.commit()
        self.db.refresh(task)
        return task

    def complete_task(self, task: CareTask, completed_date: date, notes: Optional[str] = None) -> CareTask:
        """Mark task as completed"""
        task.status = TaskStatus.COMPLETED
        task.completed_date = completed_date
        if notes:
            task.notes = notes
        self.db.commit()
        self.db.refresh(task)
        return task

    def delete(self, task: CareTask) -> None:
        """Delete task"""
        self.db.delete(task)
        self.db.commit()
