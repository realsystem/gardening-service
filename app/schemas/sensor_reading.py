"""SensorReading schemas"""
from pydantic import BaseModel, Field, model_validator
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

    @model_validator(mode='after')
    def validate_at_least_one_reading(self):
        """Ensure at least one sensor value is provided"""
        sensor_fields = [
            self.temperature_f,
            self.humidity_percent,
            self.light_hours,
            self.ph_level,
            self.ec_ms_cm,
            self.ppm,
            self.water_temp_f
        ]

        if not any(value is not None for value in sensor_fields):
            raise ValueError(
                "At least one sensor reading must be provided. "
                "Please provide temperature, humidity, light hours, pH, EC, PPM, or water temperature."
            )

        return self


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
