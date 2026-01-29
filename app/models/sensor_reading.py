"""SensorReading model for indoor garden monitoring"""
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class SensorReading(Base):
    """
    Daily sensor readings for indoor gardens.
    Tracks temperature, humidity, and light hours.
    """
    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    garden_id = Column(Integer, ForeignKey("gardens.id"), nullable=False)

    # Reading metadata
    reading_date = Column(Date, nullable=False, index=True)

    # Sensor data (indoor gardens)
    temperature_f = Column(Float, nullable=True)  # Air temperature in Fahrenheit
    humidity_percent = Column(Float, nullable=True)  # Humidity percentage
    light_hours = Column(Float, nullable=True)  # Actual light hours provided

    # Hydroponics-specific sensor data
    ph_level = Column(Float, nullable=True)  # pH level (0-14)
    ec_ms_cm = Column(Float, nullable=True)  # Electrical Conductivity in mS/cm
    ppm = Column(Integer, nullable=True)  # Parts Per Million
    water_temp_f = Column(Float, nullable=True)  # Water temperature in Fahrenheit

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="sensor_readings")
    garden = relationship("Garden", back_populates="sensor_readings")
