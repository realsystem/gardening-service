"""Functional API tests for Nutrient Optimization endpoint"""
import pytest
from datetime import date, timedelta
from app.models.garden import Garden, GardenType, HydroSystemType
from app.models.plant_variety import PlantVariety
from app.models.planting_event import PlantingEvent, PlantingMethod


@pytest.mark.nutrient_optimization
class TestNutrientOptimizationEndpoint:
    """Test GET /gardens/{id}/nutrient-optimization endpoint"""

    def test_hydroponic_garden_returns_optimization(self, client, test_db, sample_user, user_token):
        """Test hydroponic garden returns nutrient optimization"""
        # Create hydroponic garden
        garden = Garden(
            user_id=sample_user.id,
            name="DWC System",
            garden_type=GardenType.INDOOR,
            is_hydroponic=True,
            hydro_system_type=HydroSystemType.DWC,
            reservoir_size_liters=50.0
        )
        test_db.add(garden)
        test_db.commit()
        test_db.refresh(garden)

        # Create tomato variety with nutrient profile
        tomato = PlantVariety(
            common_name="Tomato",
            days_to_harvest=80,
            vegetative_ec_min=1.5,
            vegetative_ec_max=2.0,
            optimal_ph_min=5.5,
            optimal_ph_max=6.5,
            solution_change_days_max=14
        )
        test_db.add(tomato)
        test_db.commit()

        # Add planting
        planting = PlantingEvent(
            garden_id=garden.id,
            plant_variety_id=tomato.id,
            user_id=sample_user.id,
            planting_date=date.today() - timedelta(days=30),  # Vegetative stage
            planting_method=PlantingMethod.TRANSPLANT
        )
        test_db.add(planting)
        test_db.commit()

        # Get optimization
        response = client.get(
            f"/gardens/{garden.id}/nutrient-optimization",
            headers={"Authorization": f"Bearer {user_token}"}
        )

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "garden_id" in data
        assert "garden_name" in data
        assert "system_type" in data
        assert "ec_recommendation" in data
        assert "ph_recommendation" in data
        assert "replacement_schedule" in data
        assert "warnings" in data
        assert "active_plantings" in data
        assert "generated_at" in data

        # Verify EC recommendation
        assert data["ec_recommendation"]["min_ms_cm"] > 0
        assert data["ec_recommendation"]["max_ms_cm"] > data["ec_recommendation"]["min_ms_cm"]
        assert len(data["ec_recommendation"]["rationale"]) > 0

        # Verify pH recommendation
        assert 4.0 <= data["ph_recommendation"]["min_ph"] <= 7.0
        assert data["ph_recommendation"]["max_ph"] > data["ph_recommendation"]["min_ph"]
        assert len(data["ph_recommendation"]["rationale"]) > 0

        # Verify replacement schedule
        assert data["replacement_schedule"]["topoff_interval_days"] > 0
        assert data["replacement_schedule"]["full_replacement_days"] > 0
        assert len(data["replacement_schedule"]["rationale"]) > 0

        # Verify active plantings
        assert len(data["active_plantings"]) == 1
        assert data["active_plantings"][0]["plant_name"] == "Tomato"
        assert data["active_plantings"][0]["growth_stage"] == "vegetative"

    def test_outdoor_garden_rejects_optimization(self, client, test_db, sample_user, user_token):
        """Test outdoor (non-hydroponic) garden returns 400"""
        garden = Garden(
            user_id=sample_user.id,
            name="Outdoor Plot",
            garden_type=GardenType.OUTDOOR,
            is_hydroponic=False
        )
        test_db.add(garden)
        test_db.commit()
        test_db.refresh(garden)

        response = client.get(
            f"/gardens/{garden.id}/nutrient-optimization",
            headers={"Authorization": f"Bearer {user_token}"}
        )

        assert response.status_code == 400
        error_message = response.json()["error"]["message"].lower()
        assert "hydroponic" in error_message or "not applicable" in error_message

    def test_unauthorized_access_denied(self, client, test_db, sample_user):
        """Test unauthorized access is denied"""
        garden = Garden(
            user_id=sample_user.id,
            name="DWC System",
            garden_type=GardenType.INDOOR,
            is_hydroponic=True,
            hydro_system_type=HydroSystemType.DWC
        )
        test_db.add(garden)
        test_db.commit()
        test_db.refresh(garden)

        response = client.get(f"/gardens/{garden.id}/nutrient-optimization")

        assert response.status_code == 403  # HTTPBearer returns 403 for missing credentials

    def test_wrong_user_garden_denied(self, client, test_db, sample_user, second_user, user_token):
        """Test accessing another user's garden is denied"""
        # Create garden for second user
        garden = Garden(
            user_id=second_user.id,  # Different user
            name="Other User Garden",
            garden_type=GardenType.INDOOR,
            is_hydroponic=True,
            hydro_system_type=HydroSystemType.NFT
        )
        test_db.add(garden)
        test_db.commit()
        test_db.refresh(garden)

        # Try to access with sample_user's token
        response = client.get(
            f"/gardens/{garden.id}/nutrient-optimization",
            headers={"Authorization": f"Bearer {user_token}"}
        )

        assert response.status_code == 403  # Forbidden - cannot access another user's garden

    def test_nonexistent_garden_returns_404(self, client, user_token):
        """Test nonexistent garden returns 404"""
        response = client.get(
            "/gardens/99999/nutrient-optimization",
            headers={"Authorization": f"Bearer {user_token}"}
        )

        assert response.status_code == 404

    def test_empty_garden_returns_defaults(self, client, test_db, sample_user, user_token):
        """Test empty hydroponic garden returns default recommendations"""
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
        test_db.refresh(garden)

        response = client.get(
            f"/gardens/{garden.id}/nutrient-optimization",
            headers={"Authorization": f"Bearer {user_token}"}
        )

        assert response.status_code == 200
        data = response.json()

        # Should have default EC values
        assert data["ec_recommendation"]["min_ms_cm"] == 1.0
        assert data["ec_recommendation"]["max_ms_cm"] == 2.0
        assert "default" in data["ec_recommendation"]["rationale"].lower()

        # Should have NO_PLANTS warning
        warning_ids = [w["warning_id"] for w in data["warnings"]]
        assert "NO_PLANTS" in warning_ids

        # Should have no active plantings
        assert len(data["active_plantings"]) == 0

    def test_fertigation_system_supported(self, client, test_db, sample_user, user_token):
        """Test FERTIGATION system type is supported"""
        garden = Garden(
            user_id=sample_user.id,
            name="Fertigation System",
            garden_type=GardenType.OUTDOOR,
            is_hydroponic=True,  # Fertigation is considered hydroponic
            hydro_system_type=HydroSystemType.FERTIGATION,
            reservoir_size_liters=100.0
        )
        test_db.add(garden)
        test_db.commit()
        test_db.refresh(garden)

        response = client.get(
            f"/gardens/{garden.id}/nutrient-optimization",
            headers={"Authorization": f"Bearer {user_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["system_type"] == "fertigation"

    def test_container_system_supported(self, client, test_db, sample_user, user_token):
        """Test CONTAINER system type is supported"""
        garden = Garden(
            user_id=sample_user.id,
            name="Container Growing",
            garden_type=GardenType.INDOOR,
            is_hydroponic=True,
            hydro_system_type=HydroSystemType.CONTAINER,
            reservoir_size_liters=20.0
        )
        test_db.add(garden)
        test_db.commit()
        test_db.refresh(garden)

        response = client.get(
            f"/gardens/{garden.id}/nutrient-optimization",
            headers={"Authorization": f"Bearer {user_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["system_type"] == "container"

    def test_mixed_crops_ec_calculation(self, client, test_db, sample_user, user_token):
        """Test mixed crops use maximum EC demand"""
        garden = Garden(
            user_id=sample_user.id,
            name="Mixed System",
            garden_type=GardenType.INDOOR,
            is_hydroponic=True,
            hydro_system_type=HydroSystemType.DWC,
            reservoir_size_liters=50.0
        )
        test_db.add(garden)
        test_db.commit()

        # High-demand crop (tomato)
        tomato = PlantVariety(
            common_name="Tomato",
            days_to_harvest=80,
            fruiting_ec_min=2.5,
            fruiting_ec_max=3.0,
            optimal_ph_min=5.5,
            optimal_ph_max=6.5
        )
        # Low-demand crop (lettuce)
        lettuce = PlantVariety(
            common_name="Lettuce",
            days_to_harvest=60,
            vegetative_ec_min=0.8,
            vegetative_ec_max=1.2,
            optimal_ph_min=5.5,
            optimal_ph_max=6.5
        )
        test_db.add_all([tomato, lettuce])
        test_db.commit()

        # Add plantings
        tomato_planting = PlantingEvent(
            garden_id=garden.id,
            plant_variety_id=tomato.id,
            user_id=sample_user.id,
            planting_date=date.today() - timedelta(days=75),  # Fruiting
            planting_method=PlantingMethod.TRANSPLANT
        )
        lettuce_planting = PlantingEvent(
            garden_id=garden.id,
            plant_variety_id=lettuce.id,
            user_id=sample_user.id,
            planting_date=date.today() - timedelta(days=30),  # Vegetative
            planting_method=PlantingMethod.TRANSPLANT
        )
        test_db.add_all([tomato_planting, lettuce_planting])
        test_db.commit()

        response = client.get(
            f"/gardens/{garden.id}/nutrient-optimization",
            headers={"Authorization": f"Bearer {user_token}"}
        )

        assert response.status_code == 200
        data = response.json()

        # Should use tomato's higher EC (3.0) not lettuce's lower EC (1.2)
        assert data["ec_recommendation"]["max_ms_cm"] == 3.0
        assert "tomato" in data["ec_recommendation"]["rationale"].lower()

    def test_small_reservoir_warning(self, client, test_db, sample_user, user_token):
        """Test small reservoir generates warning"""
        garden = Garden(
            user_id=sample_user.id,
            name="Tiny System",
            garden_type=GardenType.INDOOR,
            is_hydroponic=True,
            hydro_system_type=HydroSystemType.DWC,
            reservoir_size_liters=8.0  # Very small
        )
        test_db.add(garden)
        test_db.commit()
        test_db.refresh(garden)

        response = client.get(
            f"/gardens/{garden.id}/nutrient-optimization",
            headers={"Authorization": f"Bearer {user_token}"}
        )

        assert response.status_code == 200
        data = response.json()

        warning_ids = [w["warning_id"] for w in data["warnings"]]
        assert "SMALL_RESERVOIR" in warning_ids

        small_res_warning = next(w for w in data["warnings"] if w["warning_id"] == "SMALL_RESERVOIR")
        assert small_res_warning["severity"] == "warning"
        assert "8" in small_res_warning["message"] or "8.0" in small_res_warning["message"]