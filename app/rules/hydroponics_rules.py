"""Hydroponics-specific task generation rules"""
from typing import List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.rules.base_rule import BaseRule
from app.models.care_task import TaskType, TaskPriority


class NutrientCheckRule(BaseRule):
    """
    Generate recurring nutrient solution check tasks for hydroponic gardens.
    Triggers: New planting event in hydroponic garden
    Frequency: Daily for first 2 weeks, then every 3 days
    """

    @property
    def name(self) -> str:
        return "Nutrient Solution Check Generator"

    def generate_tasks(self, db: Session, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        planting_event = context.get("planting_event")
        user_id = context.get("user_id")

        if not planting_event or not planting_event.garden:
            return []

        # Only apply to hydroponic gardens
        if not planting_event.garden.is_hydroponic:
            return []

        tasks = []
        planting_date = planting_event.planting_date

        # Generate daily checks for first 14 days
        for day_offset in range(1, 15):
            due_date = planting_date + timedelta(days=day_offset)
            tasks.append({
                "user_id": user_id,
                "planting_event_id": planting_event.id,
                "task_type": TaskType.CHECK_NUTRIENT_SOLUTION,
                "title": f"Check nutrient solution for {planting_event.plant_variety.common_name}",
                "description": "Check EC/PPM levels and nutrient concentrations. Record readings.",
                "due_date": due_date,
                "priority": TaskPriority.MEDIUM,
                "is_recurring": False
            })

        # Generate recurring check every 3 days after initial period
        first_recurring_date = planting_date + timedelta(days=15)
        tasks.append({
            "user_id": user_id,
            "planting_event_id": planting_event.id,
            "task_type": TaskType.CHECK_NUTRIENT_SOLUTION,
            "title": f"Check nutrient solution for {planting_event.plant_variety.common_name}",
            "description": "Check EC/PPM levels and nutrient concentrations. Record readings.",
            "due_date": first_recurring_date,
            "priority": TaskPriority.MEDIUM,
            "is_recurring": True,
            "recurrence_frequency": "daily"
        })

        return tasks


class PHMonitoringRule(BaseRule):
    """
    Generate pH adjustment tasks when sensor readings show pH is out of range.
    Triggers: Sensor reading with pH outside acceptable range
    Priority: HIGH (immediate action needed)
    """

    @property
    def name(self) -> str:
        return "pH Level Monitoring"

    def generate_tasks(self, db: Session, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        sensor_reading = context.get("sensor_reading")
        user_id = context.get("user_id")

        if not sensor_reading or sensor_reading.ph_level is None:
            return []

        garden = sensor_reading.garden
        if not garden or not garden.is_hydroponic:
            return []

        # Check if pH is within acceptable range
        if garden.ph_min is None or garden.ph_max is None:
            return []

        ph_level = sensor_reading.ph_level
        if garden.ph_min <= ph_level <= garden.ph_max:
            return []  # pH is within range

        # pH is out of range - generate high priority adjustment task
        if ph_level < garden.ph_min:
            description = f"pH is too low ({ph_level:.1f}). Target range: {garden.ph_min}-{garden.ph_max}. Add pH UP solution."
        else:
            description = f"pH is too high ({ph_level:.1f}). Target range: {garden.ph_min}-{garden.ph_max}. Add pH DOWN solution."

        return [{
            "user_id": user_id,
            "task_type": TaskType.ADJUST_PH,
            "title": f"Adjust pH in {garden.name}",
            "description": description,
            "due_date": sensor_reading.reading_date,
            "priority": TaskPriority.HIGH,
            "is_recurring": False
        }]


class ECPPMMonitoringRule(BaseRule):
    """
    Generate EC/PPM adjustment tasks when sensor readings are out of range.
    Triggers: Sensor reading with EC or PPM outside acceptable range
    Priority: HIGH (nutrient imbalance needs correction)
    """

    @property
    def name(self) -> str:
        return "EC/PPM Level Monitoring"

    def generate_tasks(self, db: Session, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        sensor_reading = context.get("sensor_reading")
        user_id = context.get("user_id")

        if not sensor_reading:
            return []

        garden = sensor_reading.garden
        if not garden or not garden.is_hydroponic:
            return []

        tasks = []

        # Check EC levels
        if sensor_reading.ec_ms_cm is not None and garden.ec_min is not None and garden.ec_max is not None:
            ec = sensor_reading.ec_ms_cm
            if ec < garden.ec_min:
                tasks.append({
                    "user_id": user_id,
                    "task_type": TaskType.REPLACE_NUTRIENT_SOLUTION,
                    "title": f"Increase nutrient concentration in {garden.name}",
                    "description": f"EC is too low ({ec:.2f} mS/cm). Target range: {garden.ec_min}-{garden.ec_max}. Add more nutrients.",
                    "due_date": sensor_reading.reading_date,
                    "priority": TaskPriority.HIGH,
                    "is_recurring": False
                })
            elif ec > garden.ec_max:
                tasks.append({
                    "user_id": user_id,
                    "task_type": TaskType.REPLACE_NUTRIENT_SOLUTION,
                    "title": f"Dilute nutrient solution in {garden.name}",
                    "description": f"EC is too high ({ec:.2f} mS/cm). Target range: {garden.ec_min}-{garden.ec_max}. Add water to dilute.",
                    "due_date": sensor_reading.reading_date,
                    "priority": TaskPriority.HIGH,
                    "is_recurring": False
                })

        # Check PPM levels
        if sensor_reading.ppm is not None and garden.ppm_min is not None and garden.ppm_max is not None:
            ppm = sensor_reading.ppm
            if ppm < garden.ppm_min:
                tasks.append({
                    "user_id": user_id,
                    "task_type": TaskType.REPLACE_NUTRIENT_SOLUTION,
                    "title": f"Increase nutrient concentration in {garden.name}",
                    "description": f"PPM is too low ({ppm}). Target range: {garden.ppm_min}-{garden.ppm_max}. Add more nutrients.",
                    "due_date": sensor_reading.reading_date,
                    "priority": TaskPriority.HIGH,
                    "is_recurring": False
                })
            elif ppm > garden.ppm_max:
                tasks.append({
                    "user_id": user_id,
                    "task_type": TaskType.REPLACE_NUTRIENT_SOLUTION,
                    "title": f"Dilute nutrient solution in {garden.name}",
                    "description": f"PPM is too high ({ppm}). Target range: {garden.ppm_min}-{garden.ppm_max}. Add water to dilute.",
                    "due_date": sensor_reading.reading_date,
                    "priority": TaskPriority.HIGH,
                    "is_recurring": False
                })

        return tasks


class WaterTemperatureMonitoringRule(BaseRule):
    """
    Generate water temperature adjustment tasks when readings are out of range.
    Triggers: Sensor reading with water temperature outside acceptable range
    Priority: HIGH (temperature affects plant health and nutrient uptake)
    """

    @property
    def name(self) -> str:
        return "Water Temperature Monitoring"

    def generate_tasks(self, db: Session, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        sensor_reading = context.get("sensor_reading")
        user_id = context.get("user_id")

        if not sensor_reading or sensor_reading.water_temp_f is None:
            return []

        garden = sensor_reading.garden
        if not garden or not garden.is_hydroponic:
            return []

        # Check if water temperature is within acceptable range
        if garden.water_temp_min_f is None or garden.water_temp_max_f is None:
            return []

        water_temp = sensor_reading.water_temp_f
        if garden.water_temp_min_f <= water_temp <= garden.water_temp_max_f:
            return []  # Temperature is within range

        # Temperature is out of range - generate high priority adjustment task
        if water_temp < garden.water_temp_min_f:
            description = f"Water temperature is too low ({water_temp:.1f}°F). Target range: {garden.water_temp_min_f}-{garden.water_temp_max_f}°F. Use water heater."
        else:
            description = f"Water temperature is too high ({water_temp:.1f}°F). Target range: {garden.water_temp_min_f}-{garden.water_temp_max_f}°F. Use chiller or increase aeration."

        return [{
            "user_id": user_id,
            "task_type": TaskType.ADJUST_WATER_CIRCULATION,
            "title": f"Adjust water temperature in {garden.name}",
            "description": description,
            "due_date": sensor_reading.reading_date,
            "priority": TaskPriority.HIGH,
            "is_recurring": False
        }]


class ReservoirMaintenanceRule(BaseRule):
    """
    Generate recurring reservoir cleaning and maintenance tasks.
    Triggers: New planting event in hydroponic garden
    Frequency: Every 14 days (biweekly)
    """

    @property
    def name(self) -> str:
        return "Reservoir Maintenance Scheduler"

    def generate_tasks(self, db: Session, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        planting_event = context.get("planting_event")
        user_id = context.get("user_id")

        if not planting_event or not planting_event.garden:
            return []

        # Only apply to hydroponic gardens
        if not planting_event.garden.is_hydroponic:
            return []

        planting_date = planting_event.planting_date
        first_maintenance_date = planting_date + timedelta(days=14)

        return [{
            "user_id": user_id,
            "planting_event_id": planting_event.id,
            "task_type": TaskType.CLEAN_RESERVOIR,
            "title": f"Clean reservoir and system for {planting_event.garden.name}",
            "description": f"Full reservoir clean, replace nutrient solution, check pumps and filters. System: {planting_event.garden.hydro_system_type.value if planting_event.garden.hydro_system_type else 'hydroponic'}",
            "due_date": first_maintenance_date,
            "priority": TaskPriority.MEDIUM,
            "is_recurring": True,
            "recurrence_frequency": "biweekly"
        }]


class NutrientReplacementRule(BaseRule):
    """
    Generate recurring nutrient solution replacement tasks.
    Triggers: New planting event in hydroponic garden
    Frequency: Weekly (every 7 days)
    """

    @property
    def name(self) -> str:
        return "Nutrient Solution Replacement Scheduler"

    def generate_tasks(self, db: Session, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        planting_event = context.get("planting_event")
        user_id = context.get("user_id")

        if not planting_event or not planting_event.garden:
            return []

        # Only apply to hydroponic gardens
        if not planting_event.garden.is_hydroponic:
            return []

        planting_date = planting_event.planting_date
        first_replacement_date = planting_date + timedelta(days=7)

        garden = planting_event.garden
        reservoir_info = f" (Reservoir: {garden.reservoir_size_liters}L)" if garden.reservoir_size_liters else ""

        return [{
            "user_id": user_id,
            "planting_event_id": planting_event.id,
            "task_type": TaskType.REPLACE_NUTRIENT_SOLUTION,
            "title": f"Replace nutrient solution in {garden.name}",
            "description": f"Complete nutrient solution change{reservoir_info}. Follow {garden.nutrient_schedule if garden.nutrient_schedule else 'recommended nutrient schedule'}.",
            "due_date": first_replacement_date,
            "priority": TaskPriority.MEDIUM,
            "is_recurring": True,
            "recurrence_frequency": "weekly"
        }]
