"""SensorReading schemas"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime


class SensorReadingCreate(BaseModel):
    """Schema for creating a new sensor reading"""
    garden_id: int
    reading_date: date
    # Indoor garden readings
    temperature_f: Optional[float] = Field(None, ge=-50, le=150)
    humidity_percent: Optional[float] = Field(None, ge=0, le=100)
    light_hours: Optional[float] = Field(None, ge=0, le=24)
    # Hydroponics-specific readings
    ph_level: Optional[float] = Field(None, ge=0, le=14)
    ec_ms_cm: Optional[float] = Field(None, ge=0)
    ppm: Optional[int] = Field(None, ge=0)
    water_temp_f: Optional[float] = Field(None, ge=-50, le=150)


class SensorReadingResponse(BaseModel):
    """Schema for sensor reading response"""
    id: int
    user_id: int
    garden_id: int
    reading_date: date
    # Indoor garden readings
    temperature_f: Optional[float] = None
    humidity_percent: Optional[float] = None
    light_hours: Optional[float] = None
    # Hydroponics-specific readings
    ph_level: Optional[float] = None
    ec_ms_cm: Optional[float] = None
    ppm: Optional[int] = None
    water_temp_f: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True
