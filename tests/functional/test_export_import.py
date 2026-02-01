"""Functional tests for export/import endpoints

These tests verify real HTTP export/import operations against a running backend.
"""
import pytest
import httpx
from datetime import datetime


pytestmark = pytest.mark.export_import


class TestExportEndpoint:
    """Test export endpoint functionality"""

    def test_export_requires_authentication(self, http_client: httpx.Client):
        """Export endpoint requires authentication"""
        response = http_client.get("/export-import/export")
        assert response.status_code == 401

    def test_export_empty_user_success(self, authenticated_client: httpx.Client):
        """Export for user with no data succeeds"""
        response = authenticated_client.get("/export-import/export")

        assert response.status_code == 200
        data = response.json()

        # Verify structure
        assert "metadata" in data
        assert "user_profile" in data
        assert "lands" in data
        assert "gardens" in data
        assert "trees" in data
        assert "plantings" in data
        assert "soil_samples" in data
        assert "irrigation_sources" in data
        assert "irrigation_zones" in data
        assert "watering_events" in data
        assert "sensor_readings" in data

        # Verify metadata
        assert data["metadata"]["schema_version"] == "1.0.0"
        assert "export_timestamp" in data["metadata"]
        assert "user_id" in data["metadata"]

        # Empty user should have empty arrays
        assert data["lands"] == []
        assert data["gardens"] == []

    def test_export_with_data(self, authenticated_client: httpx.Client):
        """Export includes user's data"""
        # Create a land
        land_response = authenticated_client.post(
            "/lands",
            json={"name": "Test Land", "width": 100.0, "height": 100.0}
        )
        assert land_response.status_code == 201
        land = land_response.json()

        # Create a garden
        garden_response = authenticated_client.post(
            "/gardens",
            json={
                "name": "Test Garden",
                "garden_type": "outdoor"
            }
        )
        assert garden_response.status_code == 201

        # Export data
        export_response = authenticated_client.get("/export-import/export")
        assert export_response.status_code == 200
        export_data = export_response.json()

        # Verify data is included
        assert len(export_data["lands"]) == 1
        assert export_data["lands"][0]["name"] == "Test Land"
        assert len(export_data["gardens"]) == 1
        assert export_data["gardens"][0]["name"] == "Test Garden"

    def test_export_without_sensor_readings(self, authenticated_client: httpx.Client):
        """Export excludes sensor readings by default"""
        response = authenticated_client.get("/export-import/export")
        assert response.status_code == 200
        data = response.json()

        assert data["sensor_readings"] == []
        assert data["metadata"]["include_sensor_readings"] is False

    def test_export_with_sensor_readings_flag(self, authenticated_client: httpx.Client):
        """Export can include sensor readings when requested"""
        response = authenticated_client.get(
            "/export-import/export",
            params={"include_sensor_readings": True}
        )
        assert response.status_code == 200
        data = response.json()

        assert data["metadata"]["include_sensor_readings"] is True

    def test_export_excludes_sensitive_data(self, authenticated_client: httpx.Client):
        """Export never includes sensitive user data"""
        response = authenticated_client.get("/export-import/export")
        assert response.status_code == 200

        # Convert to JSON string to search
        response_text = response.text

        # Should NOT contain email, password, tokens
        # (This is a basic check - the real check is in unit tests)
        assert "hashed_password" not in response_text
        assert "password" not in response_text.lower() or "password_reset" in response_text.lower()


class TestImportPreview:
    """Test import preview endpoint"""

    def test_preview_requires_authentication(self, http_client: httpx.Client):
        """Import preview requires authentication"""
        response = http_client.post(
            "/export-import/import/preview",
            json={
                "metadata": {
                    "schema_version": "1.0.0",
                    "export_timestamp": datetime.utcnow().isoformat(),
                    "user_id": 1
                },
                "user_profile": {},
                "lands": [],
                "gardens": [],
                "trees": [],
                "plantings": [],
                "soil_samples": [],
                "irrigation_sources": [],
                "irrigation_zones": [],
                "watering_events": [],
                "sensor_readings": []
            }
        )
        assert response.status_code == 401

    def test_preview_valid_empty_import(self, authenticated_client: httpx.Client):
        """Preview empty import succeeds"""
        import_data = {
            "metadata": {
                "schema_version": "1.0.0",
                "export_timestamp": datetime.utcnow().isoformat(),
                "user_id": 999
            },
            "user_profile": {},
            "lands": [],
            "gardens": [],
            "trees": [],
            "plantings": [],
            "soil_samples": [],
            "irrigation_sources": [],
            "irrigation_zones": [],
            "watering_events": [],
            "sensor_readings": []
        }

        response = authenticated_client.post(
            "/export-import/import/preview",
            json=import_data
        )

        assert response.status_code == 200
        preview = response.json()

        assert preview["valid"] is True
        assert preview["schema_version_compatible"] is True
        assert "counts" in preview
        assert preview["counts"]["lands"] == 0

    def test_preview_with_data(self, authenticated_client: httpx.Client):
        """Preview shows what would be imported"""
        import_data = {
            "metadata": {
                "schema_version": "1.0.0",
                "export_timestamp": datetime.utcnow().isoformat(),
                "user_id": 999
            },
            "user_profile": {
                "display_name": "Test User",
                "city": "Portland"
            },
            "lands": [
                {
                    "id": 1,
                    "name": "Test Land",
                    "width": 100.0,
                    "height": 100.0,
                    "created_at": datetime.utcnow().isoformat()
                }
            ],
            "gardens": [],
            "trees": [],
            "plantings": [],
            "soil_samples": [],
            "irrigation_sources": [],
            "irrigation_zones": [],
            "watering_events": [],
            "sensor_readings": []
        }

        response = authenticated_client.post(
            "/export-import/import/preview",
            json=import_data
        )

        assert response.status_code == 200
        preview = response.json()

        assert preview["valid"] is True
        assert preview["counts"]["lands"] == 1

    def test_preview_invalid_schema_version(self, authenticated_client: httpx.Client):
        """Preview detects incompatible schema version"""
        import_data = {
            "metadata": {
                "schema_version": "2.0.0",  # Incompatible major version
                "export_timestamp": datetime.utcnow().isoformat(),
                "user_id": 999
            },
            "user_profile": {},
            "lands": [],
            "gardens": [],
            "trees": [],
            "plantings": [],
            "soil_samples": [],
            "irrigation_sources": [],
            "irrigation_zones": [],
            "watering_events": [],
            "sensor_readings": []
        }

        response = authenticated_client.post(
            "/export-import/import/preview",
            json=import_data
        )

        assert response.status_code == 200
        preview = response.json()

        assert preview["schema_version_compatible"] is False

    def test_preview_invalid_relationship(self, authenticated_client: httpx.Client):
        """Preview detects invalid foreign key relationships"""
        import_data = {
            "metadata": {
                "schema_version": "1.0.0",
                "export_timestamp": datetime.utcnow().isoformat(),
                "user_id": 999
            },
            "user_profile": {},
            "lands": [],
            "gardens": [
                {
                    "id": 1,
                    "land_id": 999,  # Non-existent land
                    "name": "Orphan Garden",
                    "garden_type": "outdoor",
                    "is_hydroponic": False,
                    "is_raised_bed": False,
                    "created_at": datetime.utcnow().isoformat()
                }
            ],
            "trees": [],
            "plantings": [],
            "soil_samples": [],
            "irrigation_sources": [],
            "irrigation_zones": [],
            "watering_events": [],
            "sensor_readings": []
        }

        response = authenticated_client.post(
            "/export-import/import/preview",
            json=import_data
        )

        assert response.status_code == 200
        preview = response.json()

        # Should have validation issues
        assert len(preview["issues"]) > 0


class TestImportEndpoint:
    """Test import endpoint functionality"""

    def test_import_requires_authentication(self, http_client: httpx.Client):
        """Import requires authentication"""
        response = http_client.post(
            "/export-import/import",
            json={
                "mode": "dry_run",
                "data": {
                    "metadata": {
                        "schema_version": "1.0.0",
                        "export_timestamp": datetime.utcnow().isoformat(),
                        "user_id": 1
                    },
                    "user_profile": {},
                    "lands": [],
                    "gardens": [],
                    "trees": [],
                    "plantings": [],
                    "soil_samples": [],
                    "irrigation_sources": [],
                    "irrigation_zones": [],
                    "watering_events": [],
                    "sensor_readings": []
                }
            }
        )
        assert response.status_code == 401

    def test_import_dry_run_no_changes(self, authenticated_client: httpx.Client):
        """Dry run mode makes no database changes"""
        # Get initial lands count
        lands_before = authenticated_client.get("/lands")
        assert lands_before.status_code == 200
        lands_count_before = len(lands_before.json())

        # Import in dry run mode
        import_request = {
            "mode": "dry_run",
            "data": {
                "metadata": {
                    "schema_version": "1.0.0",
                    "export_timestamp": datetime.utcnow().isoformat(),
                    "user_id": 999
                },
                "user_profile": {},
                "lands": [
                    {
                        "id": 1,
                        "name": "Test Land",
                        "width": 100.0,
                        "height": 100.0,
                        "created_at": datetime.utcnow().isoformat()
                    }
                ],
                "gardens": [],
                "trees": [],
                "plantings": [],
                "soil_samples": [],
                "irrigation_sources": [],
                "irrigation_zones": [],
                "watering_events": [],
                "sensor_readings": []
            }
        }

        response = authenticated_client.post("/export-import/import", json=import_request)
        assert response.status_code == 200
        result = response.json()

        assert result["success"] is True
        assert result["mode"] == "dry_run"

        # Verify no changes were made
        lands_after = authenticated_client.get("/lands")
        assert lands_after.status_code == 200
        lands_count_after = len(lands_after.json())
        assert lands_count_after == lands_count_before

    def test_import_merge_mode_success(self, authenticated_client: httpx.Client):
        """Merge mode imports data successfully"""
        import_request = {
            "mode": "merge",
            "data": {
                "metadata": {
                    "schema_version": "1.0.0",
                    "export_timestamp": datetime.utcnow().isoformat(),
                    "user_id": 999
                },
                "user_profile": {},
                "lands": [
                    {
                        "id": 100,
                        "name": "Imported Land",
                        "width": 100.0,
                        "height": 100.0,
                        "created_at": datetime.utcnow().isoformat()
                    }
                ],
                "gardens": [],
                "trees": [],
                "plantings": [],
                "soil_samples": [],
                "irrigation_sources": [],
                "irrigation_zones": [],
                "watering_events": [],
                "sensor_readings": []
            }
        }

        response = authenticated_client.post("/export-import/import", json=import_request)
        assert response.status_code == 200
        result = response.json()

        assert result["success"] is True
        assert result["mode"] == "merge"
        assert result["items_imported"]["lands"] == 1

        # Verify land was created
        lands = authenticated_client.get("/lands")
        assert lands.status_code == 200
        lands_data = lands.json()
        assert any(land["name"] == "Imported Land" for land in lands_data)

    def test_import_merge_preserves_existing(self, authenticated_client: httpx.Client):
        """Merge mode preserves existing data"""
        # Create existing land
        existing = authenticated_client.post(
            "/lands",
            json={"name": "Existing Land", "width": 50.0, "height": 50.0}
        )
        assert existing.status_code == 201

        # Import new land in merge mode
        import_request = {
            "mode": "merge",
            "data": {
                "metadata": {
                    "schema_version": "1.0.0",
                    "export_timestamp": datetime.utcnow().isoformat(),
                    "user_id": 999
                },
                "user_profile": {},
                "lands": [
                    {
                        "id": 1,
                        "name": "New Land",
                        "width": 100.0,
                        "height": 100.0,
                        "created_at": datetime.utcnow().isoformat()
                    }
                ],
                "gardens": [],
                "trees": [],
                "plantings": [],
                "soil_samples": [],
                "irrigation_sources": [],
                "irrigation_zones": [],
                "watering_events": [],
                "sensor_readings": []
            }
        }

        response = authenticated_client.post("/export-import/import", json=import_request)
        assert response.status_code == 200

        # Both lands should exist
        lands = authenticated_client.get("/lands")
        lands_data = lands.json()
        land_names = {land["name"] for land in lands_data}
        assert "Existing Land" in land_names
        assert "New Land" in land_names

    def test_import_overwrite_mode_deletes_existing(self, authenticated_client: httpx.Client):
        """Overwrite mode deletes existing data"""
        # Create existing land
        existing = authenticated_client.post(
            "/lands",
            json={"name": "To Be Deleted", "width": 50.0, "height": 50.0}
        )
        assert existing.status_code == 201

        # Import in overwrite mode
        import_request = {
            "mode": "overwrite",
            "data": {
                "metadata": {
                    "schema_version": "1.0.0",
                    "export_timestamp": datetime.utcnow().isoformat(),
                    "user_id": 999
                },
                "user_profile": {},
                "lands": [
                    {
                        "id": 1,
                        "name": "New Land",
                        "width": 100.0,
                        "height": 100.0,
                        "created_at": datetime.utcnow().isoformat()
                    }
                ],
                "gardens": [],
                "trees": [],
                "plantings": [],
                "soil_samples": [],
                "irrigation_sources": [],
                "irrigation_zones": [],
                "watering_events": [],
                "sensor_readings": []
            }
        }

        response = authenticated_client.post("/export-import/import", json=import_request)
        assert response.status_code == 200
        result = response.json()

        assert result["success"] is True
        assert result["items_deleted"] is not None
        assert result["items_deleted"] > 0

        # Only new land should exist
        lands = authenticated_client.get("/lands")
        lands_data = lands.json()
        assert len(lands_data) == 1
        assert lands_data[0]["name"] == "New Land"

    def test_round_trip_export_import(self, authenticated_client: httpx.Client):
        """Export and import preserves all data"""
        # Create data
        land_response = authenticated_client.post(
            "/lands",
            json={"name": "Original Land", "width": 100.0, "height": 100.0}
        )
        assert land_response.status_code == 201
        land = land_response.json()

        garden_response = authenticated_client.post(
            "/gardens",
            json={
                "name": "Original Garden",
                "garden_type": "outdoor",
                "land_id": land["id"],
                "x": 10.0,
                "y": 10.0,
                "width": 20.0,
                "height": 20.0
            }
        )
        assert garden_response.status_code == 201

        # Export
        export_response = authenticated_client.get("/export-import/export")
        assert export_response.status_code == 200
        export_data = export_response.json()

        # Delete all data (overwrite with empty)
        delete_request = {
            "mode": "overwrite",
            "data": {
                "metadata": {
                    "schema_version": "1.0.0",
                    "export_timestamp": datetime.utcnow().isoformat(),
                    "user_id": 999
                },
                "user_profile": {},
                "lands": [],
                "gardens": [],
                "trees": [],
                "plantings": [],
                "soil_samples": [],
                "irrigation_sources": [],
                "irrigation_zones": [],
                "watering_events": [],
                "sensor_readings": []
            }
        }
        delete_response = authenticated_client.post("/export-import/import", json=delete_request)
        assert delete_response.status_code == 200

        # Verify data was deleted
        lands_empty = authenticated_client.get("/lands")
        assert len(lands_empty.json()) == 0

        # Re-import original data
        reimport_request = {
            "mode": "merge",
            "data": export_data
        }
        reimport_response = authenticated_client.post("/export-import/import", json=reimport_request)
        assert reimport_response.status_code == 200
        reimport_result = reimport_response.json()

        assert reimport_result["success"] is True

        # Verify data was restored
        lands_restored = authenticated_client.get("/lands")
        lands_data = lands_restored.json()
        assert len(lands_data) == 1
        assert lands_data[0]["name"] == "Original Land"

        gardens_restored = authenticated_client.get("/gardens")
        gardens_data = gardens_restored.json()
        assert len(gardens_data) == 1
        assert gardens_data[0]["name"] == "Original Garden"

    def test_import_invalid_mode_fails(self, authenticated_client: httpx.Client):
        """Import with invalid mode fails"""
        import_request = {
            "mode": "invalid_mode",
            "data": {
                "metadata": {
                    "schema_version": "1.0.0",
                    "export_timestamp": datetime.utcnow().isoformat(),
                    "user_id": 999
                },
                "user_profile": {},
                "lands": [],
                "gardens": [],
                "trees": [],
                "plantings": [],
                "soil_samples": [],
                "irrigation_sources": [],
                "irrigation_zones": [],
                "watering_events": [],
                "sensor_readings": []
            }
        }

        response = authenticated_client.post("/export-import/import", json=import_request)
        assert response.status_code == 400
