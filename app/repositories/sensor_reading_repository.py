"""SensorReading repository"""
from typing import List
from datetime import date
from sqlalchemy.orm import Session
from app.models.sensor_reading import SensorReading


class SensorReadingRepository:
    """Repository for SensorReading database operations"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: int, garden_id: int, reading_date: date, **kwargs) -> SensorReading:
        """Create a new sensor reading"""
        reading = SensorReading(
            user_id=user_id,
            garden_id=garden_id,
            reading_date=reading_date,
            **kwargs
        )
        self.db.add(reading)
        self.db.commit()
        self.db.refresh(reading)
        return reading

    def get_by_id(self, reading_id: int) -> SensorReading:
        """Get sensor reading by ID"""
        return self.db.query(SensorReading).filter(SensorReading.id == reading_id).first()

    def get_user_readings(self, user_id: int) -> List[SensorReading]:
        """Get all sensor readings for a user"""
        return self.db.query(SensorReading).filter(
            SensorReading.user_id == user_id
        ).order_by(SensorReading.reading_date.desc()).all()

    def get_by_garden(self, garden_id: int) -> List[SensorReading]:
        """Get all sensor readings for a specific garden"""
        return self.db.query(SensorReading).filter(
            SensorReading.garden_id == garden_id
        ).order_by(SensorReading.reading_date.desc()).all()

    def get_by_garden_and_date_range(
        self, garden_id: int, start_date: date, end_date: date
    ) -> List[SensorReading]:
        """Get sensor readings for a garden within a date range"""
        return self.db.query(SensorReading).filter(
            SensorReading.garden_id == garden_id,
            SensorReading.reading_date >= start_date,
            SensorReading.reading_date <= end_date
        ).order_by(SensorReading.reading_date.desc()).all()

    def delete(self, reading: SensorReading) -> None:
        """Delete a sensor reading"""
        self.db.delete(reading)
        self.db.commit()
