"""Tests for feature flag system.

Tests that feature flags:
1. Can be loaded and reloaded at runtime
2. Provide fail-safe behavior when disabled
3. Are accessible only to admins
4. Properly disable features without breaking the system

Security: Verifies feature flags can disable critical paths for incident response.
"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import date

from app.utils.feature_flags import (
    FeatureFlags,
    is_rule_engine_enabled,
    is_compliance_enforcement_enabled,
    is_optimization_engines_enabled,
    reload_feature_flags,
    get_feature_flag_status,
)


# ============================================
# Feature Flag Service Tests
# ============================================

@pytest.mark.unit
class TestFeatureFlagService:
    """Test feature flag loading and management."""

    def test_flags_load_from_settings(self):
        """Test that flags load from settings."""
        # Reload to get current settings
        flags = FeatureFlags.reload()

        assert 'FEATURE_RULE_ENGINE_ENABLED' in flags
        assert 'FEATURE_COMPLIANCE_ENFORCEMENT_ENABLED' in flags
        assert 'FEATURE_OPTIMIZATION_ENGINES_ENABLED' in flags

    def test_flags_default_to_enabled(self):
        """Test that flags default to enabled (fail-safe)."""
        flags = FeatureFlags.get_flags()

        # All flags should default to True for fail-safe operation
        assert flags['FEATURE_RULE_ENGINE_ENABLED'] is True
        assert flags['FEATURE_COMPLIANCE_ENFORCEMENT_ENABLED'] is True
        assert flags['FEATURE_OPTIMIZATION_ENGINES_ENABLED'] is True

    def test_unknown_flag_returns_fail_safe_default(self):
        """Test that unknown flags return fail-safe default."""
        result = FeatureFlags.is_enabled('UNKNOWN_FLAG')

        # Unknown flags should default to True (fail open)
        assert result is True

    def test_reload_updates_cached_flags(self):
        """Test that reload updates the flag cache."""
        # Initial load
        initial_flags = FeatureFlags.get_flags()

        # Reload
        reloaded_flags = FeatureFlags.reload()

        # Should have reloaded
        assert FeatureFlags._last_reload is not None

    def test_get_status_returns_metadata(self):
        """Test that get_status returns flag metadata."""
        status = get_feature_flag_status()

        assert 'flags' in status
        assert 'last_reload' in status
        assert 'definitions' in status

        # Should include flag descriptions
        assert 'FEATURE_RULE_ENGINE_ENABLED' in status['definitions']


# ============================================
# Convenience Function Tests
# ============================================

@pytest.mark.unit
class TestConvenienceFunctions:
    """Test convenience functions for checking flags."""

    def test_is_rule_engine_enabled(self):
        """Test rule engine flag check."""
        result = is_rule_engine_enabled()

        assert isinstance(result, bool)
        assert result is True  # Default

    def test_is_compliance_enforcement_enabled(self):
        """Test compliance enforcement flag check."""
        result = is_compliance_enforcement_enabled()

        assert isinstance(result, bool)
        assert result is True  # Default

    def test_is_optimization_engines_enabled(self):
        """Test optimization engines flag check."""
        result = is_optimization_engines_enabled()

        assert isinstance(result, bool)
        assert result is True  # Default


# ============================================
# Rule Engine Integration Tests
# ============================================

@pytest.mark.integration
class TestRuleEngineFeatureFlag:
    """Test rule engine behavior when feature flag is disabled."""

    def test_rule_engine_disabled_returns_empty_tasks(self, test_db, sample_user):
        """Test that disabled rule engine returns empty task list."""
        from app.rules.task_generator import TaskGenerator
        from app.models.planting_event import PlantingEvent, PlantingMethod
        from app.models.plant_variety import PlantVariety
        from app.models.garden import Garden, GardenType

        # Create test data
        garden = Garden(
            user_id=sample_user.id,
            name="Test Garden",
            garden_type=GardenType.OUTDOOR
        )
        test_db.add(garden)
        test_db.commit()

        variety = PlantVariety(
            common_name="Tomato",
            scientific_name="Solanum lycopersicum",
            days_to_harvest=80
        )
        test_db.add(variety)
        test_db.commit()

        planting = PlantingEvent(
            user_id=sample_user.id,
            garden_id=garden.id,
            plant_variety_id=variety.id,
            planting_date=date.today(),
            planting_method=PlantingMethod.DIRECT_SOW,
            plant_count=5
        )
        test_db.add(planting)
        test_db.commit()

        # Disable rule engine via mock
        with patch('app.rules.task_generator.is_rule_engine_enabled', return_value=False):
            generator = TaskGenerator()
            tasks = generator.generate_tasks_for_planting(test_db, planting, sample_user.id)

            # Should return empty list (graceful degradation)
            assert tasks == []

    def test_rule_engine_enabled_generates_tasks(self, test_db, sample_user):
        """Test that enabled rule engine generates tasks normally."""
        from app.rules.task_generator import TaskGenerator
        from app.models.planting_event import PlantingEvent, PlantingMethod
        from app.models.plant_variety import PlantVariety
        from app.models.garden import Garden, GardenType

        # Create test data
        garden = Garden(
            user_id=sample_user.id,
            name="Test Garden",
            garden_type=GardenType.OUTDOOR
        )
        test_db.add(garden)
        test_db.commit()

        variety = PlantVariety(
            common_name="Tomato",
            scientific_name="Solanum lycopersicum",
            days_to_harvest=80
        )
        test_db.add(variety)
        test_db.commit()

        planting = PlantingEvent(
            user_id=sample_user.id,
            garden_id=garden.id,
            plant_variety_id=variety.id,
            planting_date=date.today(),
            planting_method=PlantingMethod.DIRECT_SOW,
            plant_count=5
        )
        test_db.add(planting)
        test_db.commit()

        # Rule engine enabled (default)
        with patch('app.rules.task_generator.is_rule_engine_enabled', return_value=True):
            generator = TaskGenerator()
            tasks = generator.generate_tasks_for_planting(test_db, planting, sample_user.id)

            # Should generate tasks
            assert len(tasks) > 0


# ============================================
# Compliance Enforcement Integration Tests
# ============================================

@pytest.mark.integration
class TestComplianceEnforcementFeatureFlag:
    """Test compliance behavior when enforcement is disabled."""

    def test_compliance_disabled_logs_but_does_not_block(self, test_db, sample_user):
        """Test that disabled compliance logs violations but doesn't block."""
        from app.compliance.service import ComplianceService

        service = ComplianceService(test_db)

        # Disable enforcement
        with patch('app.compliance.service.is_compliance_enforcement_enabled', return_value=False):
            # Should NOT raise exception even with restricted plant
            try:
                service.check_and_enforce_plant_restriction(
                    user=sample_user,
                    common_name="Cannabis",  # Restricted
                    request_metadata={"endpoint": "test"}
                )
                # Should succeed without exception
                success = True
            except Exception:
                success = False

            assert success is True

            # User should still be flagged
            test_db.refresh(sample_user)
            assert sample_user.restricted_crop_flag is True

    def test_compliance_enabled_blocks_violations(self, test_db, sample_user):
        """Test that enabled compliance blocks violations."""
        from app.compliance.service import ComplianceService
        from fastapi import HTTPException

        service = ComplianceService(test_db)

        # Enforcement enabled (default)
        with patch('app.compliance.service.is_compliance_enforcement_enabled', return_value=True):
            with pytest.raises(HTTPException) as exc_info:
                service.check_and_enforce_plant_restriction(
                    user=sample_user,
                    common_name="Marijuana",  # Restricted
                    request_metadata={"endpoint": "test"}
                )

            # Should raise 403
            assert exc_info.value.status_code == 403

    def test_compliance_disabled_still_flags_users(self, test_db, sample_user):
        """Test that disabled enforcement still flags users for violations."""
        from app.compliance.service import ComplianceService

        service = ComplianceService(test_db)

        # Verify user starts unflagged
        assert sample_user.restricted_crop_flag is not True

        # Disable enforcement
        with patch('app.compliance.service.is_compliance_enforcement_enabled', return_value=False):
            # Attempt restricted plant (should not block)
            service.check_and_enforce_plant_restriction(
                user=sample_user,
                scientific_name="Cannabis sativa",  # Restricted
                request_metadata={"endpoint": "test"}
            )

            # User should be flagged despite enforcement being disabled
            test_db.refresh(sample_user)
            assert sample_user.restricted_crop_flag is True
            assert sample_user.restricted_crop_count >= 1


# ============================================
# Optimization Engines Integration Tests
# ============================================

@pytest.mark.integration
class TestOptimizationEnginesFeatureFlag:
    """Test optimization features when flag is disabled."""

    def test_companion_analysis_disabled_returns_empty(self, client, user_token, test_db, sample_user):
        """Test that disabled optimization returns empty results."""
        from app.models.garden import Garden, GardenType

        # Create a garden
        garden = Garden(
            user_id=sample_user.id,
            name="Test Garden",
            garden_type=GardenType.OUTDOOR
        )
        test_db.add(garden)
        test_db.commit()

        # Disable optimization engines
        with patch('app.api.companion_analysis.is_optimization_engines_enabled', return_value=False):
            response = client.get(
                f"/gardens/{garden.id}/companions",
                headers={"Authorization": f"Bearer {user_token}"}
            )

            assert response.status_code == 200
            data = response.json()

            # Should return empty results
            assert data['feature_disabled'] is True
            assert data['beneficial_pairs'] == []
            assert data['conflicts'] == []
            assert data['suggestions'] == []

    def test_companion_analysis_enabled_works_normally(self, client, user_token, test_db, sample_user):
        """Test that enabled optimization works normally."""
        from app.models.garden import Garden, GardenType

        # Create a garden
        garden = Garden(
            user_id=sample_user.id,
            name="Test Garden",
            garden_type=GardenType.OUTDOOR
        )
        test_db.add(garden)
        test_db.commit()

        # Optimization enabled (default)
        with patch('app.api.companion_analysis.is_optimization_engines_enabled', return_value=True):
            response = client.get(
                f"/gardens/{garden.id}/companions",
                headers={"Authorization": f"Bearer {user_token}"}
            )

            assert response.status_code == 200
            data = response.json()

            # Should have normal structure (even if empty due to no plantings)
            assert 'garden_id' in data
            assert 'beneficial_pairs' in data
            assert 'feature_disabled' not in data


# ============================================
# Admin Endpoint Tests
# ============================================

@pytest.mark.integration
class TestFeatureFlagAdminEndpoints:
    """Test admin endpoints for feature flag management."""

    def test_get_feature_flags_requires_admin(self, client, user_token):
        """Test that non-admins cannot view feature flags."""
        response = client.get(
            "/admin/feature-flags",
            headers={"Authorization": f"Bearer {user_token}"}
        )

        # Should be forbidden for non-admin
        assert response.status_code == 403

    def test_admin_can_view_feature_flags(self, client, admin_token):
        """Test that admins can view feature flags."""
        response = client.get(
            "/admin/feature-flags",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()

        assert 'flags' in data
        assert 'definitions' in data
        assert 'last_reload' in data

    def test_reload_feature_flags_requires_admin(self, client, user_token):
        """Test that non-admins cannot reload feature flags."""
        response = client.post(
            "/admin/feature-flags/reload",
            headers={"Authorization": f"Bearer {user_token}"}
        )

        # Should be forbidden
        assert response.status_code == 403

    def test_admin_can_reload_feature_flags(self, client, admin_token):
        """Test that admins can reload feature flags."""
        response = client.post(
            "/admin/feature-flags/reload",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()

        assert 'message' in data
        assert 'flags' in data
        assert 'reloaded_by' in data
        assert data['message'] == "Feature flags reloaded successfully"


# ============================================
# Fail-Safe Behavior Tests
# ============================================

@pytest.mark.unit
class TestFailSafeBehavior:
    """Test that feature flags provide fail-safe defaults."""

    def test_corrupted_flag_value_uses_fail_safe(self):
        """Test that corrupted flag values use fail-safe defaults."""
        # Mock settings with corrupted value
        with patch('app.utils.feature_flags.get_settings') as mock_settings:
            mock_settings.return_value = MagicMock(
                FEATURE_RULE_ENGINE_ENABLED="corrupted_value"
            )

            # Should handle gracefully and return False (bool of string)
            flags = FeatureFlags.reload()

            # String conversion should work
            assert isinstance(flags['FEATURE_RULE_ENGINE_ENABLED'], bool)

    def test_missing_flag_uses_definition_default(self):
        """Test that missing flags use their definition defaults."""
        # Mock settings missing a flag
        with patch('app.utils.feature_flags.get_settings') as mock_settings:
            mock_instance = MagicMock()
            # Remove one flag
            del mock_instance.FEATURE_RULE_ENGINE_ENABLED
            mock_instance.FEATURE_COMPLIANCE_ENFORCEMENT_ENABLED = True
            mock_instance.FEATURE_OPTIMIZATION_ENGINES_ENABLED = True
            mock_settings.return_value = mock_instance

            flags = FeatureFlags.reload()

            # Should use definition default
            assert flags['FEATURE_RULE_ENGINE_ENABLED'] is True

    def test_all_flags_disabled_system_still_works(self, test_db, sample_user):
        """Test that system works (doesn't crash) with all flags disabled."""
        from app.rules.task_generator import TaskGenerator
        from app.compliance.service import ComplianceService

        # Disable all flags
        with patch('app.utils.feature_flags.FeatureFlags.get_flags', return_value={
            'FEATURE_RULE_ENGINE_ENABLED': False,
            'FEATURE_COMPLIANCE_ENFORCEMENT_ENABLED': False,
            'FEATURE_OPTIMIZATION_ENGINES_ENABLED': False
        }):
            # Rule engine should return empty
            with patch('app.rules.task_generator.is_rule_engine_enabled', return_value=False):
                generator = TaskGenerator()
                tasks = generator._apply_rules_and_create_tasks(test_db, {}, [])
                assert tasks == []

            # Compliance should not block
            with patch('app.compliance.service.is_compliance_enforcement_enabled', return_value=False):
                service = ComplianceService(test_db)
                # Should not raise
                service.check_and_enforce_plant_restriction(
                    user=sample_user,
                    common_name="Cannabis"
                )
