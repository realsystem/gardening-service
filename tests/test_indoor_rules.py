"""Tests for indoor gardening rules"""
import pytest
from datetime import date, timedelta
from unittest.mock import Mock

from app.rules.indoor_rules import (
    LightScheduleRule,
    TemperatureMonitoringRule,
    HumidityMonitoringRule
)
from app.models.care_task import TaskType, TaskPriority


class TestLightScheduleRule:
    """Test lighting check rule for indoor gardens"""

    def test_lighting_check_rule_generates_tasks(self, test_db, sample_user, indoor_planting_event):
        """Test that lighting check tasks are generated for indoor gardens"""
        rule = LightScheduleRule()
        context = {
            "planting_event": indoor_planting_event,
            "user_id": sample_user.id
        }
        tasks = rule.generate_tasks(test_db, context)

        # Should generate multiple lighting check tasks
        assert len(tasks) > 0
        assert all(task["task_type"] == TaskType.ADJUST_LIGHTING for task in tasks)
        assert all(task["user_id"] == sample_user.id for task in tasks)

    def test_lighting_check_not_for_outdoor_garden(self, test_db, sample_user, outdoor_planting_event):
        """Test that lighting check tasks are NOT generated for outdoor gardens"""
        rule = LightScheduleRule()
        context = {
            "planting_event": outdoor_planting_event,
            "user_id": sample_user.id
        }
        tasks = rule.generate_tasks(test_db, context)

        # Should not generate tasks for outdoor gardens
        assert len(tasks) == 0


class TestTemperatureMonitoringRule:
    """Test temperature monitoring rule"""

    def test_temperature_too_low_alert(self, test_db, sample_user, indoor_garden):
        """Test alert generation when temperature is too low"""
        # Create sensor reading with low temperature
        from app.models.sensor_reading import SensorReading
        sensor_reading = SensorReading(
            user_id=sample_user.id,
            garden_id=indoor_garden.id,
            reading_date=date.today(),
            temperature_f=60.0,  # Below min (65.0)
            humidity_percent=50.0
        )
        test_db.add(sensor_reading)
        test_db.commit()
        test_db.refresh(sensor_reading)

        rule = TemperatureMonitoringRule()
        context = {
            "sensor_reading": sensor_reading,
            "user_id": sample_user.id
        }
        tasks = rule.generate_tasks(test_db, context)

        # Should generate high priority temperature adjustment task
        assert len(tasks) == 1
        task = tasks[0]
        assert task["task_type"] == TaskType.ADJUST_TEMPERATURE
        assert task["priority"] == TaskPriority.HIGH
        assert "outside acceptable range" in task["description"].lower()

    def test_temperature_too_high_alert(self, test_db, sample_user, indoor_garden):
        """Test alert generation when temperature is too high"""
        from app.models.sensor_reading import SensorReading
        sensor_reading = SensorReading(
            user_id=sample_user.id,
            garden_id=indoor_garden.id,
            reading_date=date.today(),
            temperature_f=80.0,  # Above max (75.0)
            humidity_percent=50.0
        )
        test_db.add(sensor_reading)
        test_db.commit()
        test_db.refresh(sensor_reading)

        rule = TemperatureMonitoringRule()
        context = {
            "sensor_reading": sensor_reading,
            "user_id": sample_user.id
        }
        tasks = rule.generate_tasks(test_db, context)

        assert len(tasks) == 1
        task = tasks[0]
        assert task["task_type"] == TaskType.ADJUST_TEMPERATURE
        assert task["priority"] == TaskPriority.HIGH
        assert "outside acceptable range" in task["description"].lower()

    def test_temperature_in_range_no_alert(self, test_db, sample_user, indoor_sensor_reading):
        """Test that no alert is generated when temperature is in range"""
        rule = TemperatureMonitoringRule()
        context = {
            "sensor_reading": indoor_sensor_reading,
            "user_id": sample_user.id
        }
        tasks = rule.generate_tasks(test_db, context)

        # Temperature is within range (65-75), no task should be generated
        assert len(tasks) == 0

    def test_no_alert_without_temperature_limits(self, test_db, sample_user, indoor_garden):
        """Test that no alert is generated if garden has no temperature limits set"""
        # Remove temperature limits
        indoor_garden.temp_min_f = None
        indoor_garden.temp_max_f = None
        test_db.commit()

        from app.models.sensor_reading import SensorReading
        sensor_reading = SensorReading(
            user_id=sample_user.id,
            garden_id=indoor_garden.id,
            reading_date=date.today(),
            temperature_f=80.0
        )
        test_db.add(sensor_reading)
        test_db.commit()

        rule = TemperatureMonitoringRule()
        context = {
            "sensor_reading": sensor_reading,
            "user_id": sample_user.id
        }
        tasks = rule.generate_tasks(test_db, context)

        assert len(tasks) == 0


class TestHumidityMonitoringRule:
    """Test humidity monitoring rule"""

    def test_humidity_too_low_alert(self, test_db, sample_user, indoor_garden):
        """Test alert generation when humidity is too low"""
        from app.models.sensor_reading import SensorReading
        sensor_reading = SensorReading(
            user_id=sample_user.id,
            garden_id=indoor_garden.id,
            reading_date=date.today(),
            temperature_f=70.0,
            humidity_percent=30.0  # Below min (40.0)
        )
        test_db.add(sensor_reading)
        test_db.commit()
        test_db.refresh(sensor_reading)

        rule = HumidityMonitoringRule()
        context = {
            "sensor_reading": sensor_reading,
            "user_id": sample_user.id
        }
        tasks = rule.generate_tasks(test_db, context)

        assert len(tasks) == 1
        task = tasks[0]
        assert task["task_type"] == TaskType.ADJUST_HUMIDITY
        assert task["priority"] == TaskPriority.HIGH
        assert "outside acceptable range" in task["description"].lower()

    def test_humidity_too_high_alert(self, test_db, sample_user, indoor_garden):
        """Test alert generation when humidity is too high"""
        from app.models.sensor_reading import SensorReading
        sensor_reading = SensorReading(
            user_id=sample_user.id,
            garden_id=indoor_garden.id,
            reading_date=date.today(),
            temperature_f=70.0,
            humidity_percent=70.0  # Above max (60.0)
        )
        test_db.add(sensor_reading)
        test_db.commit()
        test_db.refresh(sensor_reading)

        rule = HumidityMonitoringRule()
        context = {
            "sensor_reading": sensor_reading,
            "user_id": sample_user.id
        }
        tasks = rule.generate_tasks(test_db, context)

        assert len(tasks) == 1
        task = tasks[0]
        assert task["task_type"] == TaskType.ADJUST_HUMIDITY
        assert task["priority"] == TaskPriority.HIGH
        assert "outside acceptable range" in task["description"].lower()

    def test_humidity_in_range_no_alert(self, test_db, sample_user, indoor_sensor_reading):
        """Test that no alert is generated when humidity is in range"""
        rule = HumidityMonitoringRule()
        context = {
            "sensor_reading": indoor_sensor_reading,
            "user_id": sample_user.id
        }
        tasks = rule.generate_tasks(test_db, context)

        # Humidity is within range (40-60), no task should be generated
        assert len(tasks) == 0
