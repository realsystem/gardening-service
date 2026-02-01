"""Extended garden schemas with details"""
from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime

from app.schemas.garden import GardenResponse
from app.models.planting_event import PlantingMethod, PlantHealth


class PlantingInGardenResponse(BaseModel):
    """Planting event details for garden view"""
    id: int
    plant_variety_id: int
    plant_name: str
    variety_name: Optional[str] = None
    planting_date: date
    planting_method: PlantingMethod
    plant_count: Optional[int] = None
    location_in_garden: Optional[str] = None
    health_status: Optional[PlantHealth] = None
    expected_harvest_date: Optional[date] = None
    days_to_harvest: Optional[int] = None
    status: str  # 'pending', 'growing', 'ready_to_harvest', 'harvested'
    x: Optional[float] = None
    y: Optional[float] = None

    class Config:
        from_attributes = True


class TaskSummaryInGarden(BaseModel):
    """Task summary for garden view"""
    id: int
    title: str
    task_type: str
    priority: str
    due_date: date
    status: str
    planting_event_id: Optional[int] = None

    class Config:
        from_attributes = True


class GardenStatsResponse(BaseModel):
    """Garden statistics"""
    total_plantings: int
    active_plantings: int
    total_tasks: int
    pending_tasks: int
    high_priority_tasks: int
    upcoming_harvests: int


class GardenDetailsResponse(BaseModel):
    """Detailed garden information with plantings and tasks"""
    garden: GardenResponse
    plantings: List[PlantingInGardenResponse]
    tasks: List[TaskSummaryInGarden]
    stats: GardenStatsResponse

    class Config:
        from_attributes = True
