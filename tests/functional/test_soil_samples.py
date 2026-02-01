"""Functional tests for soil sample endpoints

These tests verify soil sample CRUD operations and business logic.
"""
from datetime import date
import pytest
import httpx


@pytest.fixture
def test_garden(authenticated_client: httpx.Client, cleanup_gardens: list) -> dict:
    """Create a test garden for soil sample tests"""
    response = authenticated_client.post(
        "/gardens",
        json={"name": "Soil Test Garden", "garden_type": "outdoor"}
    )
    garden = response.json()
    cleanup_gardens.append(garden["id"])
    return garden


class TestSoilSampleCreation:
    """Test soil sample creation"""

    def test_create_soil_sample_success(
        self,
        authenticated_client: httpx.Client,
        test_garden: dict,
        cleanup_soil_samples: list
    ):
        """Successfully create a soil sample"""
        sample_data = {
            "garden_id": test_garden["id"],
            "ph": 6.5,
            "nitrogen_ppm": 50,
            "phosphorus_ppm": 30,
            "potassium_ppm": 150,
            "moisture_percent": 40.0,
            "organic_matter_percent": 5.0,
            "date_collected": str(date.today()),
            "notes": "First soil test"
        }

        response = authenticated_client.post("/soil-samples", json=sample_data)

        assert response.status_code == 201
        data = response.json()
        assert data["garden_id"] == test_garden["id"]
        assert data["ph"] == 6.5
        assert data["nitrogen_ppm"] == 50
        assert "id" in data

        cleanup_soil_samples.append(data["id"])

    def test_create_soil_sample_minimal_data(
        self,
        authenticated_client: httpx.Client,
        test_garden: dict,
        cleanup_soil_samples: list
    ):
        """Create soil sample with minimal required fields"""
        sample_data = {
            "garden_id": test_garden["id"],
            "ph": 6.5,  # pH is required
            "date_collected": str(date.today())
        }

        response = authenticated_client.post("/soil-samples", json=sample_data)

        assert response.status_code == 201
        data = response.json()
        assert data["garden_id"] == test_garden["id"]
        assert data["ph"] == 6.5

        cleanup_soil_samples.append(data["id"])

    def test_create_soil_sample_invalid_garden_fails(
        self,
        authenticated_client: httpx.Client
    ):
        """Cannot create soil sample for non-existent garden"""
        sample_data = {
            "garden_id": 99999,
            "date_collected": str(date.today())
        }

        response = authenticated_client.post("/soil-samples", json=sample_data)

        assert response.status_code in [404, 422]

    def test_create_soil_sample_invalid_ph_fails(
        self,
        authenticated_client: httpx.Client,
        test_garden: dict
    ):
        """Cannot create soil sample with pH out of valid range"""
        sample_data = {
            "garden_id": test_garden["id"],
            "ph": 15.0,  # Invalid - pH should be 0-14
            "date_collected": str(date.today())
        }

        response = authenticated_client.post("/soil-samples", json=sample_data)

        assert response.status_code == 422


class TestSoilSampleListing:
    """Test soil sample listing"""

    def test_list_soil_samples_for_garden(
        self,
        authenticated_client: httpx.Client,
        test_garden: dict,
        cleanup_soil_samples: list
    ):
        """List all soil samples for a specific garden"""
        # Create 2 samples
        for i in range(2):
            response = authenticated_client.post(
                "/soil-samples",
                json={
                    "garden_id": test_garden["id"],
                    "ph": 6.0 + i * 0.5,
                    "date_collected": str(date.today())
                }
            )
            cleanup_soil_samples.append(response.json()["id"])

        # List samples for garden
        response = authenticated_client.get(f"/soil-samples?garden_id={test_garden['id']}")

        assert response.status_code == 200
        data = response.json()
        assert "samples" in data
        assert data["total"] == 2
        assert len(data["samples"]) == 2

    def test_list_all_user_soil_samples(
        self,
        authenticated_client: httpx.Client,
        test_garden: dict,
        cleanup_gardens: list,
        cleanup_soil_samples: list
    ):
        """List all soil samples across all user's gardens"""
        # Create second garden
        garden2 = authenticated_client.post(
            "/gardens",
            json={"name": "Garden 2", "garden_type": "outdoor"}
        ).json()
        cleanup_gardens.append(garden2["id"])

        # Create samples in both gardens
        sample1 = authenticated_client.post(
            "/soil-samples",
            json={"garden_id": test_garden["id"], "ph": 6.5, "date_collected": str(date.today())}
        ).json()
        sample2 = authenticated_client.post(
            "/soil-samples",
            json={"garden_id": garden2["id"], "ph": 7.0, "date_collected": str(date.today())}
        ).json()

        cleanup_soil_samples.extend([sample1["id"], sample2["id"]])

        # List all samples (no garden_id filter)
        response = authenticated_client.get("/soil-samples")

        assert response.status_code == 200
        data = response.json()
        assert "samples" in data
        assert data["total"] >= 2
        assert len(data["samples"]) >= 2


class TestSoilSampleRetrieval:
    """Test individual soil sample retrieval"""

    def test_get_soil_sample_by_id(
        self,
        authenticated_client: httpx.Client,
        test_garden: dict,
        cleanup_soil_samples: list
    ):
        """Successfully retrieve soil sample by ID"""
        # Create sample
        sample = authenticated_client.post(
            "/soil-samples",
            json={
                "garden_id": test_garden["id"],
                "ph": 6.8,
                "date_collected": str(date.today()),
                "notes": "Test sample"
            }
        ).json()
        cleanup_soil_samples.append(sample["id"])

        # Retrieve sample
        response = authenticated_client.get(f"/soil-samples/{sample['id']}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample["id"]
        assert data["ph"] == 6.8
        assert data["notes"] == "Test sample"

    def test_get_nonexistent_sample_fails(self, authenticated_client: httpx.Client):
        """Cannot retrieve non-existent soil sample"""
        response = authenticated_client.get("/soil-samples/99999")

        assert response.status_code == 404


class TestSoilSampleUpdate:
    """Test soil sample update/edit"""

    def test_update_soil_sample_success(
        self,
        authenticated_client: httpx.Client,
        test_garden: dict,
        cleanup_soil_samples: list
    ):
        """Successfully update soil sample"""
        # Create sample
        sample = authenticated_client.post(
            "/soil-samples",
            json={
                "garden_id": test_garden["id"],
                "ph": 6.5,
                "nitrogen_ppm": 40,
                "date_collected": str(date.today())
            }
        ).json()
        cleanup_soil_samples.append(sample["id"])

        # Update sample
        update_data = {
            "ph": 7.0,
            "nitrogen_ppm": 60,
            "notes": "Updated measurements"
        }
        response = authenticated_client.put(
            f"/soil-samples/{sample['id']}",
            json=update_data
        )

        assert response.status_code == 200
        updated = response.json()
        assert updated["ph"] == 7.0
        assert updated["nitrogen_ppm"] == 60
        assert updated["notes"] == "Updated measurements"

    def test_update_partial_fields(
        self,
        authenticated_client: httpx.Client,
        test_garden: dict,
        cleanup_soil_samples: list
    ):
        """Can update only specific fields without affecting others"""
        # Create sample with multiple fields
        sample = authenticated_client.post(
            "/soil-samples",
            json={
                "garden_id": test_garden["id"],
                "ph": 6.5,
                "nitrogen_ppm": 40,
                "phosphorus_ppm": 30,
                "date_collected": str(date.today())
            }
        ).json()
        cleanup_soil_samples.append(sample["id"])

        # Update only pH
        response = authenticated_client.put(
            f"/soil-samples/{sample['id']}",
            json={"ph": 7.2}
        )

        assert response.status_code == 200
        updated = response.json()
        assert updated["ph"] == 7.2
        assert updated["nitrogen_ppm"] == 40  # Unchanged
        assert updated["phosphorus_ppm"] == 30  # Unchanged

    def test_update_nonexistent_sample_fails(self, authenticated_client: httpx.Client):
        """Cannot update non-existent soil sample"""
        response = authenticated_client.put(
            "/soil-samples/99999",
            json={"ph": 7.0}
        )

        assert response.status_code == 404


class TestSoilSampleDeletion:
    """Test soil sample deletion"""

    def test_delete_soil_sample_success(
        self,
        authenticated_client: httpx.Client,
        test_garden: dict
    ):
        """Successfully delete a soil sample"""
        # Create sample
        sample = authenticated_client.post(
            "/soil-samples",
            json={
                "garden_id": test_garden["id"],
                "ph": 6.5,
                "date_collected": str(date.today())
            }
        ).json()

        # Delete sample
        response = authenticated_client.delete(f"/soil-samples/{sample['id']}")

        assert response.status_code == 204

        # Verify deletion
        get_response = authenticated_client.get(f"/soil-samples/{sample['id']}")
        assert get_response.status_code == 404

    def test_delete_nonexistent_sample_fails(self, authenticated_client: httpx.Client):
        """Cannot delete non-existent soil sample"""
        response = authenticated_client.delete("/soil-samples/99999")

        assert response.status_code == 404


class TestSoilSampleBusinessLogic:
    """Test business logic and validation"""

    def test_soil_samples_sorted_by_date(
        self,
        authenticated_client: httpx.Client,
        test_garden: dict,
        cleanup_soil_samples: list
    ):
        """Soil samples should be sorted by collection date (most recent first)"""
        from datetime import timedelta

        # Create samples with different dates
        today = date.today()
        dates = [
            today - timedelta(days=10),
            today - timedelta(days=5),
            today
        ]

        for collection_date in dates:
            response = authenticated_client.post(
                "/soil-samples",
                json={
                    "garden_id": test_garden["id"],
                    "ph": 6.5,
                    "date_collected": str(collection_date)
                }
            )
            cleanup_soil_samples.append(response.json()["id"])

        # Get samples
        response = authenticated_client.get(f"/soil-samples?garden_id={test_garden['id']}")
        data = response.json()
        samples = data["samples"]

        # Verify sorting (most recent first)
        assert len(samples) == 3
        dates_returned = [sample["date_collected"] for sample in samples]
        assert dates_returned == sorted(dates_returned, reverse=True)
