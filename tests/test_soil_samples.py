"""Tests for soil sample tracking functionality."""

import pytest
from datetime import date
from app.models.soil_sample import SoilSample
from app.models.garden import Garden
from app.models.planting_event import PlantingEvent
from app.models.plant_variety import PlantVariety


class TestSoilSampleCRUD:
    """Test soil sample CRUD operations."""

    def test_create_soil_sample_for_garden(self, client, sample_user, outdoor_garden, user_token, test_db):
        """Test creating a soil sample linked to a garden."""
        headers = {"Authorization": f"Bearer {user_token}"}

        data = {
            "garden_id": outdoor_garden.id,
            "ph": 6.5,
            "nitrogen_ppm": 30,
            "phosphorus_ppm": 40,
            "potassium_ppm": 180,
            "organic_matter_percent": 4.5,
            "moisture_percent": 45,
            "date_collected": "2026-01-28",
            "notes": "Spring soil test"
        }

        response = client.post("/soil-samples", json=data, headers=headers)
        assert response.status_code == 201

        result = response.json()
        assert result["ph"] == 6.5
        assert result["nitrogen_ppm"] == 30
        assert result["garden_id"] == outdoor_garden.id
        assert "recommendations" in result
        assert len(result["recommendations"]) > 0

    def test_create_soil_sample_for_planting(self, client, sample_user, outdoor_garden, outdoor_planting_event, user_token, test_db):
        """Test creating a soil sample linked to a planting event."""
        headers = {"Authorization": f"Bearer {user_token}"}

        data = {
            "planting_event_id": outdoor_planting_event.id,
            "ph": 5.8,
            "nitrogen_ppm": 15,
            "phosphorus_ppm": 25,
            "potassium_ppm": 120,
            "organic_matter_percent": 2.5,
            "moisture_percent": 25,
            "date_collected": "2026-01-28",
            "notes": "Low nitrogen detected"
        }

        response = client.post("/soil-samples", json=data, headers=headers)
        assert response.status_code == 201

        result = response.json()
        assert result["ph"] == 5.8
        assert result["planting_event_id"] == outdoor_planting_event.id
        assert "recommendations" in result

    def test_create_soil_sample_without_garden_or_planting_fails(self, client, user_token):
        """Test that creating a soil sample requires either garden_id or planting_event_id."""
        headers = {"Authorization": f"Bearer {user_token}"}

        data = {
            "ph": 7.0,
            "date_collected": "2026-01-28"
        }

        response = client.post("/soil-samples", json=data, headers=headers)
        assert response.status_code == 400

    def test_list_soil_samples(self, client, sample_user, outdoor_garden, user_token, test_db):
        """Test listing soil samples."""
        # Create multiple samples
        sample1 = SoilSample(
            user_id=sample_user.id,
            garden_id=outdoor_garden.id,
            ph=6.5,
            nitrogen_ppm=30,
            date_collected=date(2026, 1, 20)
        )
        sample2 = SoilSample(
            user_id=sample_user.id,
            garden_id=outdoor_garden.id,
            ph=6.8,
            nitrogen_ppm=35,
            date_collected=date(2026, 1, 25)
        )
        test_db.add_all([sample1, sample2])
        test_db.commit()

        headers = {"Authorization": f"Bearer {user_token}"}
        response = client.get("/soil-samples", headers=headers)

        assert response.status_code == 200
        result = response.json()
        assert result["total"] == 2
        assert len(result["samples"]) == 2
        # Should be ordered by date (most recent first)
        assert result["samples"][0]["date_collected"] == "2026-01-25"

    def test_list_soil_samples_filtered_by_garden(self, client, sample_user, outdoor_garden, user_token, test_db):
        """Test filtering soil samples by garden."""
        # Create another garden and samples
        garden2 = Garden(user_id=sample_user.id, name="Garden 2", garden_type="outdoor")
        test_db.add(garden2)
        test_db.commit()

        sample1 = SoilSample(user_id=sample_user.id, garden_id=outdoor_garden.id, ph=6.5, date_collected=date(2026, 1, 20))
        sample2 = SoilSample(user_id=sample_user.id, garden_id=garden2.id, ph=7.0, date_collected=date(2026, 1, 21))
        test_db.add_all([sample1, sample2])
        test_db.commit()

        headers = {"Authorization": f"Bearer {user_token}"}
        response = client.get(f"/soil-samples?garden_id={outdoor_garden.id}", headers=headers)

        assert response.status_code == 200
        result = response.json()
        assert result["total"] == 1
        assert result["samples"][0]["garden_id"] == outdoor_garden.id

    def test_get_soil_sample_details(self, client, sample_user, outdoor_garden, user_token, test_db):
        """Test getting specific soil sample details."""
        sample = SoilSample(
            user_id=sample_user.id,
            garden_id=outdoor_garden.id,
            ph=6.5,
            nitrogen_ppm=30,
            phosphorus_ppm=40,
            potassium_ppm=180,
            organic_matter_percent=4.5,
            moisture_percent=45,
            date_collected=date(2026, 1, 28),
            notes="Test sample"
        )
        test_db.add(sample)
        test_db.commit()

        headers = {"Authorization": f"Bearer {user_token}"}
        response = client.get(f"/soil-samples/{sample.id}", headers=headers)

        assert response.status_code == 200
        result = response.json()
        assert result["id"] == sample.id
        assert result["ph"] == 6.5
        assert result["notes"] == "Test sample"
        assert "recommendations" in result

    def test_delete_soil_sample(self, client, sample_user, outdoor_garden, user_token, test_db):
        """Test deleting a soil sample."""
        sample = SoilSample(
            user_id=sample_user.id,
            garden_id=outdoor_garden.id,
            ph=6.5,
            date_collected=date(2026, 1, 28)
        )
        test_db.add(sample)
        test_db.commit()
        sample_id = sample.id

        headers = {"Authorization": f"Bearer {user_token}"}
        response = client.delete(f"/soil-samples/{sample_id}", headers=headers)

        assert response.status_code == 204

        # Verify deletion
        deleted = test_db.query(SoilSample).filter(SoilSample.id == sample_id).first()
        assert deleted is None

    def test_cannot_access_other_users_samples(self, client, sample_user, outdoor_garden, user_token, test_db):
        """Test that users cannot access other users' soil samples."""
        # Create another user and their sample
        from app.models.user import User
        from app.services.auth_service import AuthService

        other_user = User(email="other@example.com", hashed_password=AuthService.hash_password("testpass123"))
        test_db.add(other_user)
        test_db.commit()

        other_garden = Garden(user_id=other_user.id, name="Other Garden", garden_type="outdoor")
        test_db.add(other_garden)
        test_db.commit()

        other_sample = SoilSample(
            user_id=other_user.id,
            garden_id=other_garden.id,
            ph=7.0,
            date_collected=date(2026, 1, 28)
        )
        test_db.add(other_sample)
        test_db.commit()

        headers = {"Authorization": f"Bearer {user_token}"}
        response = client.get(f"/soil-samples/{other_sample.id}", headers=headers)

        assert response.status_code == 404


class TestSoilRecommendations:
    """Test scientific soil recommendations."""

    def test_recommendations_for_low_ph(self, client, sample_user, outdoor_garden, user_token):
        """Test that low pH generates lime recommendation."""
        headers = {"Authorization": f"Bearer {user_token}"}

        data = {
            "garden_id": outdoor_garden.id,
            "ph": 5.0,  # Low pH for vegetables
            "date_collected": "2026-01-28"
        }

        response = client.post("/soil-samples", json=data, headers=headers)
        result = response.json()

        # Should have pH recommendation
        ph_rec = next((r for r in result["recommendations"] if r["parameter"] == "pH"), None)
        assert ph_rec is not None
        assert ph_rec["status"] == "low"
        assert "lime" in ph_rec["recommendation"].lower()
        assert ph_rec["priority"] in ["high", "critical"]

    def test_recommendations_for_high_ph(self, client, sample_user, outdoor_garden, user_token):
        """Test that high pH generates sulfur recommendation."""
        headers = {"Authorization": f"Bearer {user_token}"}

        data = {
            "garden_id": outdoor_garden.id,
            "ph": 8.5,  # High pH
            "date_collected": "2026-01-28"
        }

        response = client.post("/soil-samples", json=data, headers=headers)
        result = response.json()

        ph_rec = next((r for r in result["recommendations"] if r["parameter"] == "pH"), None)
        assert ph_rec is not None
        assert ph_rec["status"] == "critical"
        assert "sulfur" in ph_rec["recommendation"].lower()

    def test_recommendations_for_low_nitrogen(self, client, sample_user, outdoor_garden, user_token):
        """Test that low nitrogen generates fertilizer recommendation."""
        headers = {"Authorization": f"Bearer {user_token}"}

        data = {
            "garden_id": outdoor_garden.id,
            "ph": 6.5,
            "nitrogen_ppm": 10,  # Very low nitrogen
            "date_collected": "2026-01-28"
        }

        response = client.post("/soil-samples", json=data, headers=headers)
        result = response.json()

        n_rec = next((r for r in result["recommendations"] if r["parameter"] == "Nitrogen"), None)
        assert n_rec is not None
        assert n_rec["status"] in ["low", "critical"]
        assert "compost" in n_rec["recommendation"].lower() or "blood meal" in n_rec["recommendation"].lower()

    def test_recommendations_include_numeric_guidance(self, client, sample_user, outdoor_garden, user_token):
        """Test that recommendations include specific numeric amounts."""
        headers = {"Authorization": f"Bearer {user_token}"}

        data = {
            "garden_id": outdoor_garden.id,
            "ph": 5.0,
            "nitrogen_ppm": 10,
            "date_collected": "2026-01-28"
        }

        response = client.post("/soil-samples", json=data, headers=headers)
        result = response.json()

        # Check that recommendations contain numbers (lbs, inches, etc.)
        has_numeric = False
        for rec in result["recommendations"]:
            if any(unit in rec["recommendation"].lower() for unit in ["lbs", "lb", "inches", "inch", "per 100 sq ft"]):
                has_numeric = True
                break

        assert has_numeric, "Recommendations should include specific numeric amounts"

    def test_optimal_soil_gives_maintenance_recommendations(self, client, sample_user, outdoor_garden, user_token):
        """Test that optimal soil still provides maintenance advice."""
        headers = {"Authorization": f"Bearer {user_token}"}

        data = {
            "garden_id": outdoor_garden.id,
            "ph": 6.5,  # Optimal
            "nitrogen_ppm": 40,  # Good
            "phosphorus_ppm": 50,  # Good
            "potassium_ppm": 180,  # Good
            "organic_matter_percent": 5.0,  # Excellent
            "moisture_percent": 40,  # Good
            "date_collected": "2026-01-28"
        }

        response = client.post("/soil-samples", json=data, headers=headers)
        result = response.json()

        assert len(result["recommendations"]) > 0
        optimal_recs = [r for r in result["recommendations"] if r["status"] == "optimal"]
        assert len(optimal_recs) > 0

        # Optimal recommendations should still provide maintenance guidance
        for rec in optimal_recs:
            assert len(rec["recommendation"]) > 0
            assert rec["priority"] == "low"
