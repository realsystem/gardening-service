"""GerminationEvent schemas"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime


class GerminationEventCreate(BaseModel):
    """Schema for creating a new germination event"""
    seed_batch_id: int
    started_date: date
    germination_location: Optional[str] = None
    seed_count: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = None


class GerminationEventUpdate(BaseModel):
    """Schema for updating a germination event"""
    germinated: Optional[bool] = None
    germination_date: Optional[date] = None
    germination_count: Optional[int] = Field(None, ge=0)
    germination_success_rate: Optional[float] = Field(None, ge=0, le=100)
    notes: Optional[str] = None


class GerminationEventResponse(BaseModel):
    """Schema for germination event response"""
    id: int
    user_id: int
    seed_batch_id: int
    plant_variety_id: int
    started_date: date
    germination_location: Optional[str] = None
    seed_count: Optional[int] = None
    germinated: bool
    germination_date: Optional[date] = None
    germination_count: Optional[int] = None
    germination_success_rate: Optional[float] = None
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
