"""
Indoor gardening task generation rules.

These rules generate tasks specific to indoor growing environments based on:
- Light schedules
- Temperature ranges
- Humidity ranges
- Sensor readings
"""
from typing import List, Dict, Any
from datetime import date, timedelta
from sqlalchemy.orm import Session

from app.rules.base_rule import BaseRule
from app.models.care_task import TaskType, TaskSource, TaskPriority
from app.models.garden import GardenType
from app.repositories.sensor_reading_repository import SensorReadingRepository


class LightScheduleRule(BaseRule):
    """
    Generates daily reminder to maintain light schedule for indoor gardens.
    """

    @property
    def name(self) -> str:
        return "Indoor Light Schedule Reminder"

    def generate_tasks(self, db: Session, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate light schedule reminder task.

        Required context:
            - planting_event: PlantingEvent instance with indoor garden
            - user_id: int
        """
        planting_event = context.get("planting_event")
        user_id = context.get("user_id")

        if not planting_event or not user_id:
            return []

        # Only generate for indoor gardens
        if not planting_event.garden or planting_event.garden.garden_type != GardenType.INDOOR:
            return []

        garden = planting_event.garden
        if not garden.light_hours_per_day:
            return []

        # Generate task for next day
        task_date = date.today() + timedelta(days=1)

        task = {
            "user_id": user_id,
            "planting_event_id": planting_event.id,
            "task_type": TaskType.ADJUST_LIGHTING,
            "title": f"Maintain light schedule - {garden.name}",
            "description": (
                f"Ensure {garden.light_hours_per_day} hours of light per day. "
                f"Light source: {garden.light_source_type.value if garden.light_source_type else 'Not specified'}"
            ),
            "due_date": task_date,
            "priority": TaskPriority.MEDIUM,
            "is_recurring": True,
            "recurrence_frequency": "daily",
            "task_source": TaskSource.AUTO_GENERATED,
        }

        return [task]


class TemperatureMonitoringRule(BaseRule):
    """
    Generates warning task if temperature is outside acceptable range.
    Based on latest sensor reading.
    """

    @property
    def name(self) -> str:
        return "Indoor Temperature Monitoring"

    def generate_tasks(self, db: Session, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate temperature warning task if out of range.

        Required context:
            - sensor_reading: SensorReading instance
            - user_id: int
        """
        sensor_reading = context.get("sensor_reading")
        user_id = context.get("user_id")

        if not sensor_reading or not user_id:
            return []

        garden = sensor_reading.garden
        if not garden or garden.garden_type != GardenType.INDOOR:
            return []

        if not garden.temp_min_f or not garden.temp_max_f or not sensor_reading.temperature_f:
            return []

        # Check if temperature is out of range
        temp = sensor_reading.temperature_f
        if temp < garden.temp_min_f or temp > garden.temp_max_f:
            task = {
                "user_id": user_id,
                "planting_event_id": None,
                "task_type": TaskType.ADJUST_TEMPERATURE,
                "title": f"Temperature Alert - {garden.name}",
                "description": (
                    f"Temperature is {temp}°F, outside acceptable range "
                    f"({garden.temp_min_f}°F - {garden.temp_max_f}°F). "
                    f"Adjust climate control as needed."
                ),
                "due_date": date.today(),
                "priority": TaskPriority.HIGH,
                "task_source": TaskSource.AUTO_GENERATED,
            }
            return [task]

        return []


class HumidityMonitoringRule(BaseRule):
    """
    Generates warning task if humidity is outside acceptable range.
    Based on latest sensor reading.
    """

    @property
    def name(self) -> str:
        return "Indoor Humidity Monitoring"

    def generate_tasks(self, db: Session, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate humidity warning task if out of range.

        Required context:
            - sensor_reading: SensorReading instance
            - user_id: int
        """
        sensor_reading = context.get("sensor_reading")
        user_id = context.get("user_id")

        if not sensor_reading or not user_id:
            return []

        garden = sensor_reading.garden
        if not garden or garden.garden_type != GardenType.INDOOR:
            return []

        if not garden.humidity_min_percent or not garden.humidity_max_percent or not sensor_reading.humidity_percent:
            return []

        # Check if humidity is out of range
        humidity = sensor_reading.humidity_percent
        if humidity < garden.humidity_min_percent or humidity > garden.humidity_max_percent:
            task = {
                "user_id": user_id,
                "planting_event_id": None,
                "task_type": TaskType.ADJUST_HUMIDITY,
                "title": f"Humidity Alert - {garden.name}",
                "description": (
                    f"Humidity is {humidity}%, outside acceptable range "
                    f"({garden.humidity_min_percent}% - {garden.humidity_max_percent}%). "
                    f"Adjust humidifier/dehumidifier as needed."
                ),
                "due_date": date.today(),
                "priority": TaskPriority.HIGH,
                "task_source": TaskSource.AUTO_GENERATED,
            }
            return [task]

        return []


class NutrientScheduleRule(BaseRule):
    """
    Generates nutrient solution task for hydroponic systems.
    """

    @property
    def name(self) -> str:
        return "Indoor Nutrient Schedule"

    def generate_tasks(self, db: Session, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate nutrient solution tasks for hydroponic systems.

        Required context:
            - planting_event: PlantingEvent instance with indoor garden
            - user_id: int
        """
        planting_event = context.get("planting_event")
        user_id = context.get("user_id")

        if not planting_event or not user_id:
            return []

        garden = planting_event.garden
        if not garden or garden.garden_type != GardenType.INDOOR:
            return []

        # Only generate for hydroponic systems
        if not garden.grow_medium or "hydro" not in garden.grow_medium.lower():
            return []

        # Generate weekly nutrient task
        tasks = []
        base_date = planting_event.planting_date

        for i in range(1, 5):  # 4 weeks ahead
            task_date = base_date + timedelta(weeks=i)

            task = {
                "user_id": user_id,
                "planting_event_id": planting_event.id,
                "task_type": TaskType.NUTRIENT_SOLUTION,
                "title": f"Change nutrient solution - {garden.name}",
                "description": (
                    f"Weekly nutrient solution change for hydroponic system. "
                    f"Check EC/TDS and pH levels."
                ),
                "due_date": task_date,
                "priority": TaskPriority.MEDIUM,
                "task_source": TaskSource.AUTO_GENERATED,
            }
            tasks.append(task)

        return tasks
