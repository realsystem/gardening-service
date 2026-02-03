"""Tests for indoor gardening rules"""
import pytest
from datetime import date, timedelta
from unittest.mock import Mock

from app.rules.indoor_rules import LightScheduleRule
from app.models.care_task import TaskType, TaskPriority
# TemperatureMonitoringRule and HumidityMonitoringRule removed in Phase 6


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


# TestTemperatureMonitoringRule removed - TemperatureMonitoringRule deleted in Phase 6
# TestHumidityMonitoringRule removed - HumidityMonitoringRule deleted in Phase 6
