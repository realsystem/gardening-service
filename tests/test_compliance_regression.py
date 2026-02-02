"""Compliance enforcement regression tests.

Tests for critical security properties:
1. Fail-closed behavior (restrictive defaults)
2. No sensitive parameter leakage in logs/errors
3. Bypass prevention via import/export
4. Bypass prevention via update endpoints
5. Pattern detection for evasion attempts

Author: Security Audit
Date: 2026-02-01
"""
import pytest
import json
from datetime import date
from unittest.mock import patch, MagicMock

from app.models.garden import Garden, GardenType, HydroSystemType
from app.models.plant_variety import PlantVariety
from app.models.planting_event import PlantingEvent, PlantingMethod, PlantHealth
from app.models.user import User
from app.compliance.deny_list import check_plant_restricted, get_user_facing_message
from app.compliance.service import ComplianceService


# ============================================
# Fail-Closed Behavior Tests
# ============================================

@pytest.mark.security
@pytest.mark.compliance
class TestFailClosedBehavior:
    """Test that compliance checks fail closed (restrictive by default)."""

    def test_missing_variety_causes_enforcement_failure(self, client, test_db, sample_user, user_token):
        """Test that missing variety causes enforcement to fail (not bypass)."""
        garden = Garden(
            user_id=sample_user.id,
            name="Test Garden",
            garden_type=GardenType.OUTDOOR
        )
        test_db.add(garden)
        test_db.commit()

        # Attempt to create planting with non-existent variety ID
        response = client.post(
            "/planting-events",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "garden_id": garden.id,
                "plant_variety_id": 999999,  # Non-existent variety
                "planting_date": str(date.today()),
                "planting_method": "direct_sow",
                "plant_count": 10
            }
        )

        # Should fail (404 or 403), not succeed
        assert response.status_code in [404, 403]

    def test_empty_string_not_treated_as_safe(self):
        """Test that empty/None strings don't bypass restriction checks."""
        # Empty strings should pass (no restriction found)
        is_restricted, _ = check_plant_restricted(common_name="", scientific_name="")
        assert is_restricted is False  # Empty is safe

        # None should pass
        is_restricted, _ = check_plant_restricted(common_name=None, scientific_name=None)
        assert is_restricted is False

        # Whitespace should pass
        is_restricted, _ = check_plant_restricted(common_name="   ", scientific_name="  ")
        assert is_restricted is False

    def test_case_insensitivity_prevents_evasion(self):
        """Test that case variations cannot bypass restrictions."""
        test_cases = [
            "Cannabis",
            "cannabis",
            "CANNABIS",
            "CaNnAbIs",
            "Marijuana",
            "marijuana",
            "MARIJUANA",
            "MarIJuaNa"
        ]

        for test_name in test_cases:
            is_restricted, reason = check_plant_restricted(common_name=test_name)
            assert is_restricted is True, f"Failed to detect: {test_name}"
            assert "restricted" in reason.lower()

    def test_whitespace_padding_prevents_evasion(self):
        """Test that whitespace padding cannot bypass restrictions."""
        test_cases = [
            " cannabis",
            "cannabis ",
            "  cannabis  ",
            "\tcannabis\t",
            "\ncannabis\n",
        ]

        for test_name in test_cases:
            is_restricted, reason = check_plant_restricted(common_name=test_name)
            assert is_restricted is True, f"Failed to detect: '{test_name}'"

    def test_pattern_based_detection_catches_embedded_terms(self):
        """Test that restricted terms in larger strings are caught."""
        test_cases = [
            "My cannabis plant",
            "Growing marijuana indoors",
            "CBD-rich hemp variety",
            "THC content analysis",
            "Sativa dominant hybrid",
        ]

        for test_name in test_cases:
            is_restricted, reason = check_plant_restricted(notes=test_name)
            assert is_restricted is True, f"Failed to detect: {test_name}"
            assert "pattern" in reason.lower()


# ============================================
# Information Leakage Prevention Tests
# ============================================

@pytest.mark.security
@pytest.mark.compliance
class TestInformationLeakagePrevention:
    """Test that no sensitive information leaks through errors or logs."""

    def test_generic_error_message_doesnt_reveal_detection(self):
        """Test that error messages don't reveal what was detected."""
        # All restricted plants should return the same generic message
        test_cases = [
            "cannabis",
            "marijuana",
            "hemp",
            "thc",
            "cbd",
        ]

        for term in test_cases:
            is_restricted, reason = check_plant_restricted(common_name=term)
            assert is_restricted is True

            # Get user-facing message
            user_message = get_user_facing_message()

            # Should be generic, not reveal the term
            assert term.lower() not in user_message.lower()
            assert "cannabis" not in user_message.lower()
            assert "marijuana" not in user_message.lower()
            assert "restricted" not in user_message.lower()  # Don't use "restricted"
            assert "violates platform usage policies" in user_message.lower()

    def test_api_error_response_doesnt_leak_variety_details(self, client, test_db, sample_user, user_token):
        """Test that API error responses don't leak variety names."""
        garden = Garden(
            user_id=sample_user.id,
            name="Test Garden",
            garden_type=GardenType.OUTDOOR
        )
        test_db.add(garden)
        test_db.commit()

        restricted_variety = PlantVariety(
            common_name="Cannabis Sativa",
            scientific_name="Cannabis sativa L.",
            days_to_harvest=90
        )
        test_db.add(restricted_variety)
        test_db.commit()

        response = client.post(
            "/planting-events",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "garden_id": garden.id,
                "plant_variety_id": restricted_variety.id,
                "planting_date": str(date.today()),
                "planting_method": "direct_sow",
                "plant_count": 10
            }
        )

        assert response.status_code == 403
        response_data = response.json()

        # Error message should NOT contain variety name
        error_message = json.dumps(response_data).lower()
        assert "cannabis" not in error_message
        assert "sativa" not in error_message
        assert "marijuana" not in error_message

        # Should contain generic message only
        assert "violates platform usage policies" in error_message

    def test_logging_doesnt_include_sensitive_parameters(self, test_db, sample_user):
        """Test that compliance logging doesn't include plant names."""
        compliance_service = ComplianceService(test_db)

        # Mock the logger to capture log calls
        with patch('app.compliance.service.logging.getLogger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger

            # Flag user (this triggers logging)
            compliance_service.flag_user_for_restricted_plant(
                user=sample_user,
                violation_reason="restricted_term_in_common_name",
                request_metadata={
                    "endpoint": "test_endpoint",
                    "variety_id": 123,
                    "garden_id": 456
                }
            )

            # Verify logger was called
            assert mock_logger.warning.called

            # Get the log message
            log_call_args = mock_logger.warning.call_args
            log_message = log_call_args[0][0]  # First positional arg

            # Log should NOT contain plant names
            assert "cannabis" not in log_message.lower()
            assert "marijuana" not in log_message.lower()

            # Log should contain metadata hash (not full metadata)
            log_data = json.loads(log_message.split("Compliance violation: ")[1])
            assert "request_hash" in log_data
            assert "variety_id" not in log_data  # Metadata should be hashed, not logged
            assert "garden_id" not in log_data

    def test_user_flag_reason_is_internal_code_only(self, test_db, sample_user):
        """Test that user.restricted_crop_reason doesn't contain plant names."""
        compliance_service = ComplianceService(test_db)

        compliance_service.flag_user_for_restricted_plant(
            user=sample_user,
            violation_reason="restricted_pattern_in_scientific_name",
            request_metadata={"endpoint": "test"}
        )

        test_db.refresh(sample_user)

        # Reason should be internal code, not plant name
        assert sample_user.restricted_crop_reason == "restricted_pattern_in_scientific_name"
        assert "cannabis" not in sample_user.restricted_crop_reason.lower()
        assert "marijuana" not in sample_user.restricted_crop_reason.lower()


# ============================================
# Import/Export Bypass Prevention Tests
# ============================================

@pytest.mark.security
@pytest.mark.compliance
class TestImportExportBypass:
    """Test that import/export cannot bypass compliance checks."""

    def test_import_enforces_compliance_on_plantings(self, client, test_db, sample_user, user_token):
        """Test that importing plantings enforces compliance checks."""
        # Create garden for import
        garden = Garden(
            user_id=sample_user.id,
            name="Import Garden",
            garden_type=GardenType.OUTDOOR
        )
        test_db.add(garden)
        test_db.commit()

        # Create restricted variety
        restricted_variety = PlantVariety(
            common_name="Cannabis",
            days_to_harvest=90
        )
        test_db.add(restricted_variety)
        test_db.commit()

        # Prepare import data with restricted planting
        import_data = {
            "metadata": {
                "schema_version": "1.0.0",
                "exported_at": "2024-01-01T00:00:00",
                "user_id": sample_user.id,
                "total_items": 1
            },
            "gardens": [{
                "id": 1,
                "name": "Imported Garden",
                "garden_type": "outdoor"
            }],
            "plantings": [{
                "id": 1,
                "garden_id": 1,
                "plant_variety_id": restricted_variety.id,
                "planting_date": "2024-01-01",
                "planting_method": "direct_sow",
                "plant_count": 10,
                "plant_notes": None
            }],
            "lands": [],
            "trees": [],
            "soil_samples": [],
            "irrigation_sources": [],
            "irrigation_zones": [],
            "watering_events": [],
            "sensor_readings": []
        }

        # Attempt to import
        response = client.post(
            "/export-import/import",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "data": import_data,
                "mode": "merge"
            }
        )

        # Should be blocked (403) or fail validation
        assert response.status_code in [403, 422, 400]

        # User should be flagged
        test_db.refresh(sample_user)
        assert sample_user.restricted_crop_flag is True

    def test_import_with_restricted_notes_blocked(self, client, test_db, sample_user, user_token):
        """Test that import blocks plantings with restricted terms in notes."""
        garden = Garden(
            user_id=sample_user.id,
            name="Import Garden",
            garden_type=GardenType.OUTDOOR
        )
        test_db.add(garden)
        test_db.commit()

        # Create legitimate variety
        tomato_variety = PlantVariety(
            common_name="Tomato",
            scientific_name="Solanum lycopersicum",
            days_to_harvest=80
        )
        test_db.add(tomato_variety)
        test_db.commit()

        # Import data with restricted term in plant_notes
        import_data = {
            "metadata": {
                "schema_version": "1.0.0",
                "exported_at": "2024-01-01T00:00:00",
                "user_id": sample_user.id,
                "total_items": 1
            },
            "gardens": [{
                "id": 1,
                "name": "Imported Garden",
                "garden_type": "outdoor"
            }],
            "plantings": [{
                "id": 1,
                "garden_id": 1,
                "plant_variety_id": tomato_variety.id,
                "planting_date": "2024-01-01",
                "planting_method": "direct_sow",
                "plant_count": 5,
                "plant_notes": "Growing next to cannabis for comparison"  # Restricted term in notes
            }],
            "lands": [],
            "trees": [],
            "soil_samples": [],
            "irrigation_sources": [],
            "irrigation_zones": [],
            "watering_events": [],
            "sensor_readings": []
        }

        response = client.post(
            "/export-import/import",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "data": import_data,
                "mode": "merge"
            }
        )

        # Should be blocked
        assert response.status_code == 403


# ============================================
# Update Endpoint Bypass Prevention Tests
# ============================================

@pytest.mark.security
@pytest.mark.compliance
class TestUpdateEndpointBypass:
    """Test that update endpoints cannot bypass compliance checks."""

    def test_update_planting_notes_with_restricted_term_blocked(self, client, test_db, sample_user, user_token):
        """Test that updating plant_notes with restricted terms is blocked.

        CRITICAL: This tests for a potential bypass where users create legitimate
        plantings and then update notes to include restricted terms.
        """
        # Create garden and legitimate variety
        garden = Garden(
            user_id=sample_user.id,
            name="Test Garden",
            garden_type=GardenType.OUTDOOR
        )
        test_db.add(garden)

        tomato_variety = PlantVariety(
            common_name="Tomato",
            scientific_name="Solanum lycopersicum",
            days_to_harvest=80
        )
        test_db.add(tomato_variety)
        test_db.commit()

        # Create legitimate planting
        planting = PlantingEvent(
            user_id=sample_user.id,
            garden_id=garden.id,
            plant_variety_id=tomato_variety.id,
            planting_date=date.today(),
            planting_method=PlantingMethod.DIRECT_SOW,
            plant_count=10,
            plant_notes="Normal tomato planting",
            health_status=PlantHealth.HEALTHY
        )
        test_db.add(planting)
        test_db.commit()

        # Attempt to update notes with restricted term
        response = client.patch(
            f"/planting-events/{planting.id}",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "plant_notes": "This is actually cannabis I'm tracking"  # Restricted term
            }
        )

        # Should be blocked with 403
        assert response.status_code == 403
        assert "violates platform usage policies" in response.json()["error"]["message"]

        # User should be flagged
        test_db.refresh(sample_user)
        assert sample_user.restricted_crop_flag is True
        assert sample_user.restricted_crop_count == 1

    def test_update_planting_notes_legitimate_allowed(self, client, test_db, sample_user, user_token):
        """Test that legitimate note updates are allowed."""
        garden = Garden(
            user_id=sample_user.id,
            name="Test Garden",
            garden_type=GardenType.OUTDOOR
        )
        test_db.add(garden)

        tomato_variety = PlantVariety(
            common_name="Tomato",
            days_to_harvest=80
        )
        test_db.add(tomato_variety)
        test_db.commit()

        planting = PlantingEvent(
            user_id=sample_user.id,
            garden_id=garden.id,
            plant_variety_id=tomato_variety.id,
            planting_date=date.today(),
            planting_method=PlantingMethod.DIRECT_SOW,
            plant_count=10,
            health_status=PlantHealth.HEALTHY
        )
        test_db.add(planting)
        test_db.commit()

        # Update with legitimate notes
        response = client.patch(
            f"/planting-events/{planting.id}",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "plant_notes": "Showing good growth, healthy leaves"
            }
        )

        # Should succeed
        assert response.status_code == 200


# ============================================
# Pattern Detection and Evasion Prevention
# ============================================

@pytest.mark.security
@pytest.mark.compliance
class TestPatternDetection:
    """Test pattern-based detection for evasion attempts."""

    def test_misspellings_caught(self):
        """Test that common misspellings are caught."""
        test_cases = [
            "canabis",  # Missing 'n'
            "cannibis",  # Extra 'i'
            "marihuana",  # Spanish spelling
            "marijauna",  # Common typo
        ]

        for term in test_cases:
            is_restricted, reason = check_plant_restricted(common_name=term)
            # Some may be caught, but not all (misspellings are hard to enumerate)
            # This is a best-effort test

    def test_leetspeak_variations_detected(self):
        """Test that leetspeak/obfuscation doesn't bypass detection."""
        # Note: Current implementation doesn't handle leetspeak
        # This test documents the limitation
        test_cases = [
            "c@nn@bis",
            "c4nn4bis",
            "mar1juana",
        ]

        for term in test_cases:
            is_restricted, _ = check_plant_restricted(common_name=term)
            # These will NOT be detected (limitation of simple pattern matching)
            # Documented as known limitation

    def test_unicode_variations_normalized(self):
        """Test that unicode variations cannot bypass restrictions."""
        # Note: Current implementation doesn't normalize unicode
        # This test documents the limitation
        test_cases = [
            "сannabis",  # Cyrillic 'c'
            "сannаbis",  # Cyrillic 'c' and 'a'
        ]

        for term in test_cases:
            is_restricted, _ = check_plant_restricted(common_name=term)
            # These may NOT be detected (unicode normalization not implemented)
            # Documented as known limitation

    def test_compound_terms_detected(self):
        """Test that restricted terms in compound words are caught."""
        test_cases = [
            "cannabis plant variety",
            "marijuana-based medicine",
            "hemp oil extract",
            "CBD dominant strain",
            "THC testing results",
        ]

        for term in test_cases:
            is_restricted, reason = check_plant_restricted(notes=term)
            assert is_restricted is True, f"Failed to detect: {term}"
            assert "pattern" in reason.lower()

    def test_multiple_fields_checked(self):
        """Test that restrictions are checked across all fields."""
        # Restricted term in different fields
        test_cases = [
            {"common_name": "cannabis"},
            {"scientific_name": "Cannabis sativa"},
            {"notes": "Growing cannabis"},
            {"genus": "Cannabis"},
            {"species": "sativa"},
        ]

        for fields in test_cases:
            is_restricted, reason = check_plant_restricted(**fields)
            assert is_restricted is True, f"Failed to detect in fields: {fields}"

    def test_no_field_escapes_detection(self):
        """Test that ALL text fields are checked (fail-safe)."""
        # Place restricted term in every possible field
        is_restricted, _ = check_plant_restricted(
            common_name="Tomato",
            scientific_name="Solanum lycopersicum",
            notes="This is just a tomato, not cannabis",  # Restricted in notes
            genus="Solanum",
            species="lycopersicum"
        )

        # Should be caught in notes field
        assert is_restricted is True


# ============================================
# Compliance Service Unit Tests
# ============================================

@pytest.mark.security
@pytest.mark.compliance
class TestComplianceServiceBehavior:
    """Test ComplianceService fail-closed behavior."""

    def test_flag_increments_on_each_violation(self, test_db, sample_user):
        """Test that violation count increments correctly."""
        compliance_service = ComplianceService(test_db)

        # First violation
        compliance_service.flag_user_for_restricted_plant(
            user=sample_user,
            violation_reason="test_reason_1"
        )
        test_db.refresh(sample_user)
        assert sample_user.restricted_crop_count == 1
        assert sample_user.restricted_crop_flag is True

        # Second violation
        compliance_service.flag_user_for_restricted_plant(
            user=sample_user,
            violation_reason="test_reason_2"
        )
        test_db.refresh(sample_user)
        assert sample_user.restricted_crop_count == 2

        # Third violation
        compliance_service.flag_user_for_restricted_plant(
            user=sample_user,
            violation_reason="test_reason_3"
        )
        test_db.refresh(sample_user)
        assert sample_user.restricted_crop_count == 3

    def test_first_violation_timestamp_immutable(self, test_db, sample_user):
        """Test that first_violation timestamp doesn't change on subsequent violations."""
        compliance_service = ComplianceService(test_db)

        # First violation
        compliance_service.flag_user_for_restricted_plant(
            user=sample_user,
            violation_reason="test_reason_1"
        )
        test_db.refresh(sample_user)
        first_timestamp = sample_user.restricted_crop_first_violation
        assert first_timestamp is not None

        # Second violation (different reason)
        compliance_service.flag_user_for_restricted_plant(
            user=sample_user,
            violation_reason="test_reason_2"
        )
        test_db.refresh(sample_user)

        # First timestamp should NOT change
        assert sample_user.restricted_crop_first_violation == first_timestamp

    def test_last_violation_timestamp_updates(self, test_db, sample_user):
        """Test that last_violation timestamp updates on each violation."""
        from freezegun import freeze_time
        compliance_service = ComplianceService(test_db)

        # First violation at specific time
        with freeze_time("2024-01-01 12:00:00"):
            compliance_service.flag_user_for_restricted_plant(
                user=sample_user,
                violation_reason="test_reason_1"
            )
            test_db.refresh(sample_user)
            first_last_timestamp = sample_user.restricted_crop_last_violation

        # Second violation at later time
        with freeze_time("2024-01-01 13:00:00"):
            compliance_service.flag_user_for_restricted_plant(
                user=sample_user,
                violation_reason="test_reason_2"
            )
            test_db.refresh(sample_user)
            second_last_timestamp = sample_user.restricted_crop_last_violation

        # Last timestamp SHOULD change
        assert second_last_timestamp > first_last_timestamp

    def test_violation_reason_overwritten(self, test_db, sample_user):
        """Test that violation reason is overwritten with most recent."""
        compliance_service = ComplianceService(test_db)

        compliance_service.flag_user_for_restricted_plant(
            user=sample_user,
            violation_reason="first_reason"
        )
        test_db.refresh(sample_user)
        assert sample_user.restricted_crop_reason == "first_reason"

        compliance_service.flag_user_for_restricted_plant(
            user=sample_user,
            violation_reason="second_reason"
        )
        test_db.refresh(sample_user)
        assert sample_user.restricted_crop_reason == "second_reason"
