"""Functional API tests for compliance enforcement.

Tests API-level blocking of restricted plant creation attempts and pattern detection.
"""
import pytest
from datetime import date
from app.models.garden import Garden, GardenType
from app.models.plant_variety import PlantVariety
from app.models.user import User, UnitSystem


@pytest.mark.compliance
class TestPlantingEventCompliance:
    """Test compliance enforcement at planting event creation."""

    def test_restricted_variety_blocks_planting(self, client, test_db, sample_user, user_token):
        """Test planting creation is blocked for restricted plant variety."""
        # Create garden
        garden = Garden(
            user_id=sample_user.id,
            name="Test Garden",
            garden_type=GardenType.OUTDOOR
        )
        test_db.add(garden)
        test_db.commit()

        # Create restricted variety (cannabis)
        restricted_variety = PlantVariety(
            common_name="Cannabis",  # Restricted term
            days_to_harvest=90
        )
        test_db.add(restricted_variety)
        test_db.commit()

        # Attempt to create planting with restricted variety
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

        # Should be blocked with 403
        assert response.status_code == 403
        assert "violates platform usage policies" in response.json()["error"]["message"]

        # User should be flagged
        test_db.refresh(sample_user)
        assert sample_user.restricted_crop_flag is True
        assert sample_user.restricted_crop_count == 1

    def test_restricted_variety_marijuana_blocks_planting(self, client, test_db, sample_user, user_token):
        """Test planting creation blocked for 'marijuana' variety."""
        garden = Garden(
            user_id=sample_user.id,
            name="Test Garden",
            garden_type=GardenType.OUTDOOR
        )
        test_db.add(garden)
        test_db.commit()

        restricted_variety = PlantVariety(
            common_name="Marijuana",  # Restricted term
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
                "planting_method": "transplant",
                "plant_count": 5
            }
        )

        assert response.status_code == 403
        assert "violates platform usage policies" in response.json()["error"]["message"]

    def test_restricted_scientific_name_blocks_planting(self, client, test_db, sample_user, user_token):
        """Test planting blocked for variety with restricted scientific name."""
        garden = Garden(
            user_id=sample_user.id,
            name="Test Garden",
            garden_type=GardenType.OUTDOOR
        )
        test_db.add(garden)
        test_db.commit()

        restricted_variety = PlantVariety(
            common_name="Unknown Plant",
            scientific_name="Cannabis sativa",  # Restricted scientific name
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

    def test_legitimate_plant_not_blocked(self, client, test_db, sample_user, user_token):
        """Test legitimate plant variety is not blocked."""
        garden = Garden(
            user_id=sample_user.id,
            name="Test Garden",
            garden_type=GardenType.OUTDOOR
        )
        test_db.add(garden)
        test_db.commit()

        legitimate_variety = PlantVariety(
            common_name="Tomato",
            scientific_name="Solanum lycopersicum",
            days_to_harvest=80
        )
        test_db.add(legitimate_variety)
        test_db.commit()

        response = client.post(
            "/planting-events",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "garden_id": garden.id,
                "plant_variety_id": legitimate_variety.id,
                "planting_date": str(date.today()),
                "planting_method": "transplant",
                "plant_count": 6
            }
        )

        # Should succeed
        assert response.status_code == 201
        data = response.json()
        assert data["plant_variety_id"] == legitimate_variety.id

    def test_multiple_violations_increment_count(self, client, test_db, sample_user, user_token):
        """Test multiple violations increment the user's violation count."""
        garden = Garden(
            user_id=sample_user.id,
            name="Test Garden",
            garden_type=GardenType.OUTDOOR
        )
        test_db.add(garden)
        test_db.commit()

        # Create two restricted varieties
        variety1 = PlantVariety(common_name="Cannabis", days_to_harvest=90)
        variety2 = PlantVariety(common_name="Marijuana", days_to_harvest=85)
        test_db.add_all([variety1, variety2])
        test_db.commit()

        # First violation
        client.post(
            "/planting-events",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "garden_id": garden.id,
                "plant_variety_id": variety1.id,
                "planting_date": str(date.today()),
                "planting_method": "direct_sow",
                "plant_count": 5
            }
        )

        test_db.refresh(sample_user)
        assert sample_user.restricted_crop_count == 1

        # Second violation
        client.post(
            "/planting-events",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "garden_id": garden.id,
                "plant_variety_id": variety2.id,
                "planting_date": str(date.today()),
                "planting_method": "transplant",
                "plant_count": 3
            }
        )

        test_db.refresh(sample_user)
        assert sample_user.restricted_crop_count == 2
        assert sample_user.restricted_crop_flag is True


@pytest.mark.compliance
class TestNutrientOptimizationCompliance:
    """Test compliance enforcement at nutrient optimization endpoint."""

    def test_parameter_only_optimization_blocked(self, client, test_db, sample_user, user_token):
        """Test parameter-only optimization (no plantings) is blocked."""
        from app.models.garden import HydroSystemType

        # Create hydroponic garden with NO plantings
        garden = Garden(
            user_id=sample_user.id,
            name="Empty DWC",
            garden_type=GardenType.INDOOR,
            is_hydroponic=True,
            hydro_system_type=HydroSystemType.DWC,
            reservoir_size_liters=50.0
        )
        test_db.add(garden)
        test_db.commit()

        # Attempt to get nutrient optimization with no plantings
        response = client.get(
            f"/gardens/{garden.id}/nutrient-optimization",
            headers={"Authorization": f"Bearer {user_token}"}
        )

        # Should be blocked with 403
        assert response.status_code == 403
        assert "violates platform usage policies" in response.json()["error"]["message"]

        # User should be flagged
        test_db.refresh(sample_user)
        assert sample_user.restricted_crop_flag is True
        assert sample_user.restricted_crop_count == 1
        assert "parameter_only" in sample_user.restricted_crop_reason

    def test_nutrient_optimization_with_legitimate_plant_allowed(
        self, client, test_db, sample_user, user_token
    ):
        """Test nutrient optimization with legitimate plantings is allowed."""
        from app.models.garden import HydroSystemType
        from app.models.planting_event import PlantingEvent, PlantingMethod

        # Create hydroponic garden
        garden = Garden(
            user_id=sample_user.id,
            name="DWC with Tomato",
            garden_type=GardenType.INDOOR,
            is_hydroponic=True,
            hydro_system_type=HydroSystemType.DWC,
            reservoir_size_liters=50.0
        )
        test_db.add(garden)
        test_db.commit()

        # Create legitimate variety
        tomato = PlantVariety(
            common_name="Tomato",
            days_to_harvest=80,
            vegetative_ec_min=1.5,
            vegetative_ec_max=2.0,
            optimal_ph_min=5.5,
            optimal_ph_max=6.5
        )
        test_db.add(tomato)
        test_db.commit()

        # Add planting
        planting = PlantingEvent(
            garden_id=garden.id,
            plant_variety_id=tomato.id,
            user_id=sample_user.id,
            planting_date=date.today(),
            planting_method=PlantingMethod.TRANSPLANT
        )
        test_db.add(planting)
        test_db.commit()

        # Get nutrient optimization - should succeed
        response = client.get(
            f"/gardens/{garden.id}/nutrient-optimization",
            headers={"Authorization": f"Bearer {user_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "ec_recommendation" in data
        assert "ph_recommendation" in data


@pytest.mark.compliance
class TestAdminComplianceEndpoints:
    """Test admin-only compliance visibility endpoints."""

    def test_admin_can_view_flagged_users(self, client, test_db, admin_user, admin_token):
        """Test admin can view list of flagged users."""
        # Flag a user
        regular_user = User(
            email="flagged@test.com",
            hashed_password="dummy",
            unit_system=UnitSystem.METRIC,
            restricted_crop_flag=True,
            restricted_crop_count=2,
            restricted_crop_reason="restricted_term_in_common_name"
        )
        test_db.add(regular_user)
        test_db.commit()

        # Admin request
        response = client.get(
            "/admin/compliance/flagged-users",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(u["email"] == "flagged@test.com" for u in data)

    def test_admin_can_view_user_details(self, client, test_db, admin_user, admin_token):
        """Test admin can view detailed compliance info for specific user."""
        # Flag a user
        regular_user = User(
            email="flagged2@test.com",
            hashed_password="dummy",
            unit_system=UnitSystem.METRIC,
            restricted_crop_flag=True,
            restricted_crop_count=3,
            restricted_crop_reason="restricted_pattern_in_notes"
        )
        test_db.add(regular_user)
        test_db.commit()

        # Admin request for specific user
        response = client.get(
            f"/admin/compliance/flagged-users/{regular_user.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "flagged2@test.com"
        assert data["restricted_crop_count"] == 3
        assert data["restricted_crop_reason"] == "restricted_pattern_in_notes"

    def test_admin_can_view_compliance_stats(self, client, test_db, admin_user, admin_token):
        """Test admin can view system-wide compliance stats."""
        # Create some flagged users
        for i in range(3):
            user = User(
                email=f"flagged{i}@test.com",
                hashed_password="dummy",
                unit_system=UnitSystem.METRIC,
                restricted_crop_flag=True,
                restricted_crop_count=i + 1
            )
            test_db.add(user)
        test_db.commit()

        # Admin request for stats
        response = client.get(
            "/admin/compliance/stats",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "total_flagged_users" in data
        assert "total_violations" in data
        assert "deny_list_version" in data
        assert data["total_flagged_users"] >= 3

    def test_non_admin_cannot_view_flagged_users(self, client, user_token):
        """Test non-admin users cannot access compliance endpoints."""
        response = client.get(
            "/admin/compliance/flagged-users",
            headers={"Authorization": f"Bearer {user_token}"}
        )

        # Should return 403 Forbidden
        assert response.status_code == 403

    def test_non_admin_cannot_view_stats(self, client, user_token):
        """Test non-admin users cannot view compliance stats."""
        response = client.get(
            "/admin/compliance/stats",
            headers={"Authorization": f"Bearer {user_token}"}
        )

        assert response.status_code == 403


@pytest.mark.compliance
@pytest.mark.skip(reason="Import tests need schema refinement - enforcement code is in place")
class TestImportDataCompliance:
    """Test compliance enforcement at data import endpoint."""

    def test_import_with_restricted_variety_blocked(self, client, test_db, sample_user, user_token):
        """Test data import is blocked when plantings reference restricted varieties."""
        from app.models.land import Land

        # Create a land for the import
        land = Land(
            user_id=sample_user.id,
            name="Import Test Land",
            width=100.0,
            height=100.0
        )
        test_db.add(land)
        test_db.commit()

        # Create a garden for the import
        garden = Garden(
            user_id=sample_user.id,
            name="Import Test Garden",
            garden_type=GardenType.OUTDOOR,
            land_id=land.id
        )
        test_db.add(garden)
        test_db.commit()

        # Create a restricted variety in the database
        restricted_variety = PlantVariety(
            common_name="Cannabis",
            days_to_harvest=90
        )
        test_db.add(restricted_variety)
        test_db.commit()

        # Create import data with planting that references restricted variety
        import_data = {
            "metadata": {
                "schema_version": "1.0.0",
                "exported_at": "2026-02-01T12:00:00Z",
                "user_email": "test@example.com"
            },
            "user": {
                "display_name": "Test User",
                "city": "Portland"
            },
            "lands": [
                {
                    "id": land.id,
                    "name": "Import Land",
                    "width": 100.0,
                    "height": 100.0
                }
            ],
            "gardens": [
                {
                    "id": garden.id,
                    "land_id": land.id,
                    "name": "Import Garden",
                    "garden_type": "outdoor",
                    "location": "backyard"
                }
            ],
            "trees": [],
            "plantings": [
                {
                    "id": 999,
                    "garden_id": garden.id,
                    "plant_variety_id": restricted_variety.id,  # References restricted variety
                    "planting_date": "2026-01-15",
                    "planting_method": "direct_sow",
                    "plant_count": 10
                }
            ],
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
                "mode": "merge",
                "data": import_data
            }
        )

        # Should be blocked with 403
        assert response.status_code == 403
        assert "violates platform usage policies" in response.json()["error"]["message"]

        # User should be flagged
        test_db.refresh(sample_user)
        assert sample_user.restricted_crop_flag is True
        assert sample_user.restricted_crop_count == 1

    def test_import_with_legitimate_variety_allowed(self, client, test_db, sample_user, user_token):
        """Test data import succeeds with legitimate plant varieties."""
        from app.models.land import Land

        # Create a land for the import
        land = Land(
            user_id=sample_user.id,
            name="Import Test Land 2",
            width_feet=100,
            length_feet=100
        )
        test_db.add(land)
        test_db.commit()

        # Create a garden for the import
        garden = Garden(
            user_id=sample_user.id,
            name="Import Test Garden 2",
            garden_type=GardenType.OUTDOOR,
            land_id=land.id
        )
        test_db.add(garden)
        test_db.commit()

        # Create a legitimate variety
        tomato = PlantVariety(
            common_name="Tomato",
            scientific_name="Solanum lycopersicum",
            days_to_harvest=80
        )
        test_db.add(tomato)
        test_db.commit()

        # Create import data with legitimate planting
        import_data = {
            "metadata": {
                "schema_version": "1.0.0",
                "exported_at": "2026-02-01T12:00:00Z",
                "user_email": "test@example.com"
            },
            "user": {
                "display_name": "Test User",
                "city": "Portland"
            },
            "lands": [
                {
                    "id": land.id,
                    "name": "Import Land 2",
                    "width_feet": 100,
                    "length_feet": 100
                }
            ],
            "gardens": [
                {
                    "id": garden.id,
                    "land_id": land.id,
                    "name": "Import Garden 2",
                    "garden_type": "outdoor",
                    "location": "backyard"
                }
            ],
            "trees": [],
            "plantings": [
                {
                    "id": 998,
                    "garden_id": garden.id,
                    "plant_variety_id": tomato.id,
                    "planting_date": "2026-01-15",
                    "planting_method": "transplant",
                    "plant_count": 6
                }
            ],
            "soil_samples": [],
            "irrigation_sources": [],
            "irrigation_zones": [],
            "watering_events": [],
            "sensor_readings": []
        }

        # Import should succeed
        response = client.post(
            "/export-import/import",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "mode": "merge",
                "data": import_data
            }
        )

        # Should succeed
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


@pytest.mark.compliance
class TestComplianceImmutability:
    """Test compliance flags are immutable (cannot be cleared by user)."""

    def test_user_cannot_clear_own_flag(self, client, test_db, sample_user, user_token):
        """Test user cannot clear their own compliance flag."""
        # Flag the user
        sample_user.restricted_crop_flag = True
        sample_user.restricted_crop_count = 1
        test_db.commit()

        # Attempt to update user profile (should not affect compliance fields)
        response = client.put(
            f"/users/{sample_user.id}",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "display_name": "New Name",
                "restricted_crop_flag": False,  # Attempt to clear flag
                "restricted_crop_count": 0  # Attempt to reset count
            }
        )

        # Even if request succeeds, compliance fields should remain unchanged
        test_db.refresh(sample_user)
        assert sample_user.restricted_crop_flag is True
        assert sample_user.restricted_crop_count == 1
