"""SensorReading API endpoints"""
from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.sensor_reading import SensorReadingCreate, SensorReadingResponse
from app.repositories.sensor_reading_repository import SensorReadingRepository
from app.repositories.garden_repository import GardenRepository
from app.api.dependencies import get_current_user
from app.models.user import User
from app.rules.task_generator import TaskGenerator

router = APIRouter(prefix="/sensor-readings", tags=["sensor-readings"])


@router.post("", response_model=SensorReadingResponse, status_code=status.HTTP_201_CREATED)
def create_sensor_reading(
    reading_data: SensorReadingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new sensor reading for an indoor garden"""
    # Verify garden exists and belongs to user
    garden_repo = GardenRepository(db)
    garden = garden_repo.get_by_id(reading_data.garden_id)
    if not garden:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Garden not found"
        )
    if garden.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this garden"
        )

    # Create sensor reading
    reading_repo = SensorReadingRepository(db)
    reading = reading_repo.create(
        user_id=current_user.id,
        garden_id=reading_data.garden_id,
        reading_date=reading_data.reading_date,
        temperature_f=reading_data.temperature_f,
        humidity_percent=reading_data.humidity_percent,
        light_hours=reading_data.light_hours,
        # Hydroponics-specific fields
        ph_level=reading_data.ph_level,
        ec_ms_cm=reading_data.ec_ms_cm,
        ppm=reading_data.ppm,
        water_temp_f=reading_data.water_temp_f
    )

    # Generate warning tasks if sensor readings are out of range
    task_generator = TaskGenerator()
    task_generator.generate_tasks_for_sensor_reading(db, reading, current_user.id)

    return reading


@router.get("", response_model=List[SensorReadingResponse])
def get_sensor_readings(
    garden_id: Optional[int] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get sensor readings for user's gardens, optionally filtered by garden and date range"""
    reading_repo = SensorReadingRepository(db)

    if garden_id:
        # Verify garden belongs to user
        garden_repo = GardenRepository(db)
        garden = garden_repo.get_by_id(garden_id)
        if not garden or garden.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this garden"
            )
        if start_date and end_date:
            readings = reading_repo.get_by_garden_and_date_range(garden_id, start_date, end_date)
        else:
            readings = reading_repo.get_by_garden(garden_id)
    else:
        readings = reading_repo.get_user_readings(current_user.id)

    return readings


@router.get("/{reading_id}", response_model=SensorReadingResponse)
def get_sensor_reading(
    reading_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific sensor reading"""
    reading_repo = SensorReadingRepository(db)
    reading = reading_repo.get_by_id(reading_id)

    if not reading:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sensor reading not found"
        )

    if reading.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this reading"
        )

    return reading


@router.delete("/{reading_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sensor_reading(
    reading_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a sensor reading"""
    reading_repo = SensorReadingRepository(db)
    reading = reading_repo.get_by_id(reading_id)

    if not reading:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sensor reading not found"
        )

    if reading.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this reading"
        )

    reading_repo.delete(reading)
