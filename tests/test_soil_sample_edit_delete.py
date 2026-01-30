"""
Tests for soil sample edit and delete functionality.
Ensures authorization, validation, and rule engine integration.
"""

import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, get_db
from app.models.user import User
from app.models.garden import Garden
from app.models.soil_sample import SoilSample
from app.services.auth_service import AuthService
from sqlalchemy.orm import Session

client = TestClient(app)


@pytest.fixture
def test_db():
    """Create a fresh test database for each test."""
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(test_db: Session):
    """Create a test user."""
    user = User(
        email="test@example.com",
        hashed_password=AuthService.hash_password("testpass123"),
        display_name="Test User"
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def other_user(test_db: Session):
    """Create another user to test authorization."""
    user = User(
        email="other@example.com",
        hashed_password=AuthService.hash_password("testpass123"),
        display_name="Other User"
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def test_garden(test_db: Session, test_user: User):
    """Create a test garden."""
    garden = Garden(
        name="Test Garden",
        garden_type="outdoor",
        user_id=test_user.id
    )
    test_db.add(garden)
    test_db.commit()
    test_db.refresh(garden)
    return garden


@pytest.fixture
def test_sample(test_db: Session, test_user: User, test_garden: Garden):
    """Create a test soil sample."""
    sample = SoilSample(
        user_id=test_user.id,
        garden_id=test_garden.id,
        ph=6.5,
        nitrogen_ppm=30.0,
        phosphorus_ppm=25.0,
        potassium_ppm=150.0,
        moisture_percent=50.0,
        date_collected=date.today(),
        notes="Initial sample"
    )
    test_db.add(sample)
    test_db.commit()
    test_db.refresh(sample)
    return sample


def get_auth_headers(user: User) -> dict:
    """Get authorization headers for a user."""
    token = AuthService.create_access_token(user.id, user.email)
    return {"Authorization": f"Bearer {token}"}


class TestUpdateSoilSample:
    """Tests for PUT /soil-samples/{id} endpoint."""

    def test_update_sample_success(self, test_db, test_user, test_sample):
        """Test successful soil sample update."""
        headers = get_auth_headers(test_user)
        update_data = {
            "ph": 7.0,
            "nitrogen_ppm": 40.0,
            "notes": "Updated sample"
        }

        response = client.put(
            f"/soil-samples/{test_sample.id}",
            json=update_data,
            headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["ph"] == 7.0
        assert data["nitrogen_ppm"] == 40.0
        assert data["notes"] == "Updated sample"
        # Unchanged fields should remain
        assert data["phosphorus_ppm"] == 25.0
        assert data["potassium_ppm"] == 150.0

    def test_update_sample_unauthorized(self, test_db, test_sample, other_user):
        """Test that users cannot update samples they don't own."""
        headers = get_auth_headers(other_user)
        update_data = {"ph": 7.0}

        response = client.put(
            f"/soil-samples/{test_sample.id}",
            json=update_data,
            headers=headers
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_update_sample_not_found(self, test_db, test_user):
        """Test updating a non-existent sample."""
        headers = get_auth_headers(test_user)
        update_data = {"ph": 7.0}

        response = client.put(
            "/soil-samples/99999",
            json=update_data,
            headers=headers
        )

        assert response.status_code == 404

    def test_update_sample_invalid_ph(self, test_db, test_user, test_sample):
        """Test validation for invalid pH values."""
        headers = get_auth_headers(test_user)

        # pH too high
        response = client.put(
            f"/soil-samples/{test_sample.id}",
            json={"ph": 15.0},
            headers=headers
        )
        assert response.status_code == 422

        # pH negative
        response = client.put(
            f"/soil-samples/{test_sample.id}",
            json={"ph": -1.0},
            headers=headers
        )
        assert response.status_code == 422

    def test_update_sample_invalid_percentages(self, test_db, test_user, test_sample):
        """Test validation for percentage fields."""
        headers = get_auth_headers(test_user)

        # Moisture > 100%
        response = client.put(
            f"/soil-samples/{test_sample.id}",
            json={"moisture_percent": 110.0},
            headers=headers
        )
        assert response.status_code == 422

        # Organic matter negative
        response = client.put(
            f"/soil-samples/{test_sample.id}",
            json={"organic_matter_percent": -5.0},
            headers=headers
        )
        assert response.status_code == 422

    def test_update_sample_partial(self, test_db, test_user, test_sample):
        """Test partial updates (only some fields)."""
        headers = get_auth_headers(test_user)

        # Update only notes
        response = client.put(
            f"/soil-samples/{test_sample.id}",
            json={"notes": "Only updated notes"},
            headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["notes"] == "Only updated notes"
        assert data["ph"] == 6.5  # Unchanged

    def test_update_sample_with_recommendations(self, test_db, test_user, test_sample):
        """Test that updated samples generate new recommendations."""
        headers = get_auth_headers(test_user)

        # Update to problematic values
        response = client.put(
            f"/soil-samples/{test_sample.id}",
            json={"ph": 4.5, "nitrogen_ppm": 5.0},
            headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["ph"] == 4.5
        assert len(data.get("recommendations", [])) > 0  # Should have recommendations


class TestDeleteSoilSample:
    """Tests for DELETE /soil-samples/{id} endpoint."""

    def test_delete_sample_success(self, test_db, test_user, test_sample):
        """Test successful soil sample deletion."""
        headers = get_auth_headers(test_user)

        response = client.delete(
            f"/soil-samples/{test_sample.id}",
            headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "deleted_sample" in data
        assert data["deleted_sample"]["id"] == test_sample.id

        # Verify it's actually deleted
        get_response = client.get(
            f"/soil-samples/{test_sample.id}",
            headers=headers
        )
        assert get_response.status_code == 404

    def test_delete_sample_unauthorized(self, test_db, test_sample, other_user):
        """Test that users cannot delete samples they don't own."""
        headers = get_auth_headers(other_user)

        response = client.delete(
            f"/soil-samples/{test_sample.id}",
            headers=headers
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

        # Sample should still exist
        db_sample = test_db.query(SoilSample).filter(
            SoilSample.id == test_sample.id
        ).first()
        assert db_sample is not None

    def test_delete_sample_not_found(self, test_db, test_user):
        """Test deleting a non-existent sample."""
        headers = get_auth_headers(test_user)

        response = client.delete(
            "/soil-samples/99999",
            headers=headers
        )

        assert response.status_code == 404

    def test_delete_sample_cascade(self, test_db, test_user, test_garden):
        """Test that deleting a garden doesn't leave orphaned samples."""
        # Create sample
        sample = SoilSample(
            user_id=test_user.id,
            garden_id=test_garden.id,
            ph=6.5,
            date_collected=date.today()
        )
        test_db.add(sample)
        test_db.commit()
        sample_id = sample.id

        # Delete garden (should cascade to sample)
        test_db.delete(test_garden)
        test_db.commit()

        # Sample should be gone
        db_sample = test_db.query(SoilSample).filter(
            SoilSample.id == sample_id
        ).first()
        assert db_sample is None


class TestRuleEngineIntegration:
    """Tests for rule engine reactivity to edits/deletes."""

    def test_rule_engine_uses_latest_sample(self, test_db, test_user, test_garden):
        """Test that rule engine picks up edited samples."""
        headers = get_auth_headers(test_user)

        # Create bad sample
        sample = SoilSample(
            user_id=test_user.id,
            garden_id=test_garden.id,
            ph=4.5,
            moisture_percent=8.0,
            date_collected=date.today(),
        )
        test_db.add(sample)
        test_db.commit()
        test_db.refresh(sample)

        # Get rule insights - should show critical alerts
        insights_response = client.get(
            f"/rule-insights/garden/{test_garden.id}",
            headers=headers
        )
        assert insights_response.status_code == 200
        insights_before = insights_response.json()
        assert insights_before["rules_by_severity"]["critical"] > 0

        # Edit to good values
        client.put(
            f"/soil-samples/{sample.id}",
            json={"ph": 6.5, "moisture_percent": 50.0},
            headers=headers
        )

        # Get rule insights again - should show fewer/no alerts
        insights_response = client.get(
            f"/rule-insights/garden/{test_garden.id}",
            headers=headers
        )
        assert insights_response.status_code == 200
        insights_after = insights_response.json()
        assert insights_after["rules_by_severity"]["critical"] < insights_before["rules_by_severity"]["critical"]

    def test_rule_engine_after_delete(self, test_db, test_user, test_garden, test_sample):
        """Test that rule engine handles deleted samples."""
        headers = get_auth_headers(test_user)

        # Delete the sample
        client.delete(f"/soil-samples/{test_sample.id}", headers=headers)

        # Rule insights should still work (with empty/default context)
        insights_response = client.get(
            f"/rule-insights/garden/{test_garden.id}",
            headers=headers
        )
        assert insights_response.status_code == 200
        # No errors, just empty insights
        assert "triggered_rules" in insights_response.json()
