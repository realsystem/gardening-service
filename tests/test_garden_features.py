"""Tests for garden convenience features (list plantings, delete, open garden)"""
import pytest
from datetime import date, timedelta

from app.models.planting_event import PlantingEvent
from app.models.care_task import CareTask, TaskType, TaskPriority, TaskStatus, TaskSource


class TestGardenPlantingsEndpoint:
    """Test GET /gardens/{garden_id}/plantings endpoint"""

    def test_get_garden_plantings(self, client, sample_user, outdoor_garden, outdoor_planting_event, user_token):
        """Test getting all plantings for a garden"""
        headers = {"Authorization": f"Bearer {user_token}"}

        response = client.get(f"/gardens/{outdoor_garden.id}/plantings", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

        # Check planting details
        planting = data[0]
        assert "plant_name" in planting
        assert "planting_date" in planting
        assert "status" in planting
        assert planting["status"] in ["pending", "growing", "ready_to_harvest"]

    def test_get_garden_plantings_with_harvest_info(self, client, sample_user, outdoor_garden, outdoor_planting_event, user_token, sample_plant_variety):
        """Test that plantings include expected harvest date"""
        headers = {"Authorization": f"Bearer {user_token}"}

        response = client.get(f"/gardens/{outdoor_garden.id}/plantings", headers=headers)

        assert response.status_code == 200
        data = response.json()

        planting = data[0]
        assert planting["plant_name"] == "Tomato"
        if planting.get("expected_harvest_date"):
            # Should be planting_date + days_to_harvest
            expected = outdoor_planting_event.planting_date + timedelta(days=sample_plant_variety.days_to_harvest)
            assert planting["expected_harvest_date"] == str(expected)

    def test_get_garden_plantings_unauthorized(self, client, sample_user, second_user, outdoor_garden):
        """Test that users cannot access other users' garden plantings"""
        from app.services.auth_service import AuthService
        second_user_token = AuthService.create_access_token(second_user.id, second_user.email)
        headers = {"Authorization": f"Bearer {second_user_token}"}

        response = client.get(f"/gardens/{outdoor_garden.id}/plantings", headers=headers)

        assert response.status_code == 403

    def test_get_plantings_for_nonexistent_garden(self, client, user_token):
        """Test getting plantings for non-existent garden"""
        headers = {"Authorization": f"Bearer {user_token}"}

        response = client.get("/gardens/99999/plantings", headers=headers)

        assert response.status_code == 404

    def test_get_plantings_empty_garden(self, client, sample_user, user_token, test_db):
        """Test getting plantings for garden with no plants"""
        from app.repositories.garden_repository import GardenRepository
        from app.models.garden import GardenType

        # Create empty garden
        repo = GardenRepository(test_db)
        garden = repo.create(user_id=sample_user.id, name="Empty Garden", garden_type=GardenType.OUTDOOR)

        headers = {"Authorization": f"Bearer {user_token}"}
        response = client.get(f"/gardens/{garden.id}/plantings", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0


class TestDeleteGardenEndpoint:
    """Test DELETE /gardens/{garden_id} endpoint"""

    def test_delete_garden_success(self, client, sample_user, outdoor_garden, user_token):
        """Test successful garden deletion"""
        headers = {"Authorization": f"Bearer {user_token}"}
        garden_id = outdoor_garden.id

        response = client.delete(f"/gardens/{garden_id}", headers=headers)

        assert response.status_code == 204

        # Verify garden is deleted
        response = client.get(f"/gardens/{garden_id}", headers=headers)
        assert response.status_code == 404

    def test_delete_garden_cascades_to_plantings(self, client, sample_user, outdoor_garden, outdoor_planting_event, user_token, test_db):
        """Test that deleting garden deletes associated plantings"""
        headers = {"Authorization": f"Bearer {user_token}"}
        garden_id = outdoor_garden.id
        planting_id = outdoor_planting_event.id

        # Verify planting exists
        planting = test_db.query(PlantingEvent).filter(PlantingEvent.id == planting_id).first()
        assert planting is not None

        # Delete garden
        response = client.delete(f"/gardens/{garden_id}", headers=headers)
        assert response.status_code == 204

        # Verify planting is deleted
        planting = test_db.query(PlantingEvent).filter(PlantingEvent.id == planting_id).first()
        assert planting is None

    def test_delete_garden_cascades_to_tasks(self, client, sample_user, outdoor_garden, outdoor_planting_event, sample_care_task, user_token, test_db):
        """Test that deleting garden deletes associated tasks"""
        headers = {"Authorization": f"Bearer {user_token}"}
        garden_id = outdoor_garden.id
        task_id = sample_care_task.id

        # Verify task exists
        task = test_db.query(CareTask).filter(CareTask.id == task_id).first()
        assert task is not None

        # Delete garden
        response = client.delete(f"/gardens/{garden_id}", headers=headers)
        assert response.status_code == 204

        # Verify task is deleted
        task = test_db.query(CareTask).filter(CareTask.id == task_id).first()
        assert task is None

    def test_delete_garden_unauthorized(self, client, sample_user, second_user, outdoor_garden):
        """Test that users cannot delete other users' gardens"""
        from app.services.auth_service import AuthService
        second_user_token = AuthService.create_access_token(second_user.id, second_user.email)
        headers = {"Authorization": f"Bearer {second_user_token}"}

        response = client.delete(f"/gardens/{outdoor_garden.id}", headers=headers)

        assert response.status_code == 403

    def test_delete_nonexistent_garden(self, client, user_token):
        """Test deleting non-existent garden"""
        headers = {"Authorization": f"Bearer {user_token}"}

        response = client.delete("/gardens/99999", headers=headers)

        assert response.status_code == 404


class TestGardenDetailsEndpoint:
    """Test GET /gardens/{garden_id} endpoint (enhanced with details)"""

    def test_get_garden_details_structure(self, client, sample_user, outdoor_garden, outdoor_planting_event, user_token):
        """Test that garden details includes all required fields"""
        headers = {"Authorization": f"Bearer {user_token}"}

        response = client.get(f"/gardens/{outdoor_garden.id}", headers=headers)

        assert response.status_code == 200
        data = response.json()

        # Check structure
        assert "garden" in data
        assert "plantings" in data
        assert "tasks" in data
        assert "stats" in data

        # Check garden details
        assert data["garden"]["id"] == outdoor_garden.id
        assert data["garden"]["name"] == outdoor_garden.name

        # Check plantings list
        assert isinstance(data["plantings"], list)

        # Check tasks list
        assert isinstance(data["tasks"], list)

        # Check stats
        stats = data["stats"]
        assert "total_plantings" in stats
        assert "active_plantings" in stats
        assert "total_tasks" in stats
        assert "pending_tasks" in stats
        assert "high_priority_tasks" in stats
        assert "upcoming_harvests" in stats

    def test_get_garden_details_with_plantings_and_tasks(self, client, sample_user, outdoor_garden, outdoor_planting_event, sample_care_task, user_token):
        """Test garden details includes plantings and tasks"""
        headers = {"Authorization": f"Bearer {user_token}"}

        response = client.get(f"/gardens/{outdoor_garden.id}", headers=headers)

        assert response.status_code == 200
        data = response.json()

        # Should have at least one planting
        assert len(data["plantings"]) >= 1
        planting = data["plantings"][0]
        assert "plant_name" in planting
        assert "status" in planting

        # Should have at least one task
        assert len(data["tasks"]) >= 1
        task = data["tasks"][0]
        assert "title" in task
        assert "priority" in task

    def test_get_garden_details_stats_accuracy(self, client, sample_user, outdoor_garden, outdoor_planting_event, test_db, user_token):
        """Test that stats are calculated correctly"""
        from app.models.care_task import CareTask, TaskType, TaskPriority, TaskStatus, TaskSource

        # Add a high priority task
        high_priority_task = CareTask(
            user_id=sample_user.id,
            planting_event_id=outdoor_planting_event.id,
            task_type=TaskType.WATER,
            task_source=TaskSource.AUTO_GENERATED,
            title="Urgent: Water plants",
            priority=TaskPriority.HIGH,
            due_date=date.today(),
            status=TaskStatus.PENDING,
            is_recurring=False
        )
        test_db.add(high_priority_task)
        test_db.commit()

        headers = {"Authorization": f"Bearer {user_token}"}
        response = client.get(f"/gardens/{outdoor_garden.id}", headers=headers)

        assert response.status_code == 200
        data = response.json()

        stats = data["stats"]
        assert stats["total_plantings"] >= 1
        assert stats["high_priority_tasks"] >= 1
        assert stats["total_tasks"] >= 1  # At least the high priority task we created

    def test_get_hydroponic_garden_details(self, client, sample_user, hydroponic_garden, hydroponic_planting_event, user_token):
        """Test garden details for hydroponic garden"""
        headers = {"Authorization": f"Bearer {user_token}"}

        response = client.get(f"/gardens/{hydroponic_garden.id}", headers=headers)

        assert response.status_code == 200
        data = response.json()

        # Check hydroponic-specific fields
        garden = data["garden"]
        assert garden["is_hydroponic"] is True
        assert garden["hydro_system_type"] == "nft"
        assert garden["reservoir_size_liters"] == 100.0

    def test_get_empty_garden_details(self, client, sample_user, user_token, test_db):
        """Test garden details for garden with no plantings"""
        from app.repositories.garden_repository import GardenRepository
        from app.models.garden import GardenType

        # Create empty garden
        repo = GardenRepository(test_db)
        garden = repo.create(user_id=sample_user.id, name="Empty Garden", garden_type=GardenType.OUTDOOR)

        headers = {"Authorization": f"Bearer {user_token}"}
        response = client.get(f"/gardens/{garden.id}", headers=headers)

        assert response.status_code == 200
        data = response.json()

        assert len(data["plantings"]) == 0
        assert len(data["tasks"]) == 0
        assert data["stats"]["total_plantings"] == 0
        assert data["stats"]["active_plantings"] == 0


class TestGardenFeaturesIntegration:
    """Integration tests for garden convenience features"""

    def test_complete_garden_workflow(self, client, sample_user, sample_plant_variety, user_token, test_db):
        """Test: Create garden → Add planting → View details → Delete garden"""
        from app.repositories.garden_repository import GardenRepository
        from app.models.garden import GardenType
        from app.models.planting_event import PlantingEvent, PlantingMethod

        headers = {"Authorization": f"Bearer {user_token}"}

        # Create garden
        repo = GardenRepository(test_db)
        garden = repo.create(user_id=sample_user.id, name="Test Garden", garden_type=GardenType.OUTDOOR)

        # Use plant variety from fixture
        variety = sample_plant_variety

        # Add planting
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

        # View garden details
        response = client.get(f"/gardens/{garden.id}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["plantings"]) == 1
        assert data["stats"]["total_plantings"] == 1

        # List plantings
        response = client.get(f"/gardens/{garden.id}/plantings", headers=headers)
        assert response.status_code == 200
        plantings = response.json()
        assert len(plantings) == 1

        # Delete garden
        response = client.delete(f"/gardens/{garden.id}", headers=headers)
        assert response.status_code == 204

        # Verify garden is gone
        response = client.get(f"/gardens/{garden.id}", headers=headers)
        assert response.status_code == 404
