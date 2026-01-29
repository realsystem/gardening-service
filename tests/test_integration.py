"""Integration tests for complete user workflows"""
import pytest
from datetime import date, timedelta

from app.models.care_task import TaskType, TaskStatus


class TestCompleteOutdoorGardeningWorkflow:
    """Test complete outdoor gardening workflow from registration to harvest"""

    def test_full_outdoor_workflow(self, client, test_db):
        """Test: Register → Create garden → Plant → Complete tasks → Harvest"""

        # Step 1: Register user
        register_response = client.post(
            "/auth/register",
            json={
                "email": "gardener@example.com",
                "password": "securepass123",
                "full_name": "Test Gardener"
            }
        )
        assert register_response.status_code == 200

        # Step 2: Login
        login_response = client.post(
            "/auth/login",
            data={
                "username": "gardener@example.com",
                "password": "securepass123"
            }
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Step 3: Create user profile
        profile_response = client.post(
            "/user-profiles/",
            headers=headers,
            json={
                "bio": "New to gardening",
                "location": "Portland, OR"
            }
        )
        assert profile_response.status_code == 200

        # Step 4: Create outdoor garden
        garden_response = client.post(
            "/gardens/",
            headers=headers,
            json={
                "name": "Backyard Vegetable Garden",
                "description": "My first garden",
                "garden_type": "outdoor"
            }
        )
        assert garden_response.status_code == 200
        garden = garden_response.json()

        # Step 5: Create seed batch
        # First get plant varieties
        varieties_response = client.get("/plant-varieties/")
        assert varieties_response.status_code == 200
        varieties = varieties_response.json()
        tomato = next(v for v in varieties if v["common_name"] == "Tomato")

        seed_response = client.post(
            "/seed-batches/",
            headers=headers,
            json={
                "plant_variety_id": tomato["id"],
                "source": "Local nursery",
                "harvest_year": 2023,
                "quantity": 20
            }
        )
        assert seed_response.status_code == 200

        # Step 6: Create planting event
        planting_response = client.post(
            "/planting-events/",
            headers=headers,
            json={
                "garden_id": garden["id"],
                "plant_variety_id": tomato["id"],
                "planting_date": str(date.today()),
                "planting_method": "direct_sow",
                "plant_count": 6,
                "location_in_garden": "Bed 1"
            }
        )
        assert planting_response.status_code == 200

        # Step 7: Verify tasks were auto-generated
        tasks_response = client.get("/tasks/", headers=headers)
        assert tasks_response.status_code == 200
        tasks = tasks_response.json()
        assert len(tasks) > 0

        # Should have watering and harvest tasks
        task_types = [t["task_type"] for t in tasks]
        assert "water" in task_types
        assert "harvest" in task_types

        # Step 8: Complete a watering task
        water_task = next(t for t in tasks if t["task_type"] == "water")
        complete_response = client.patch(
            f"/tasks/{water_task['id']}/complete",
            headers=headers
        )
        assert complete_response.status_code == 200
        completed_task = complete_response.json()
        assert completed_task["status"] == "completed"

        # Step 9: Verify dashboard shows updated tasks
        updated_tasks = client.get("/tasks/", headers=headers).json()
        completed_count = sum(1 for t in updated_tasks if t["status"] == "completed")
        assert completed_count >= 1


class TestCompleteIndoorGardeningWorkflow:
    """Test complete indoor gardening workflow with sensor monitoring"""

    def test_full_indoor_workflow(self, client, test_db):
        """Test: Register → Create indoor garden → Plant → Monitor sensors → Adjust conditions"""

        # Setup: Register and login
        client.post("/auth/register", json={
            "email": "indoor@example.com",
            "password": "pass123",
            "full_name": "Indoor Gardener"
        })
        login = client.post("/auth/login", data={
            "username": "indoor@example.com",
            "password": "pass123"
        })
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create indoor garden with environmental settings
        garden_response = client.post(
            "/gardens/",
            headers=headers,
            json={
                "name": "Indoor Grow Room",
                "garden_type": "indoor",
                "location": "Basement",
                "light_source_type": "led",
                "light_hours_per_day": 16.0,
                "temp_min_f": 65.0,
                "temp_max_f": 75.0,
                "humidity_min_percent": 40.0,
                "humidity_max_percent": 60.0
            }
        )
        assert garden_response.status_code == 200
        garden = garden_response.json()

        # Get lettuce variety for indoor growing
        varieties = client.get("/plant-varieties/").json()
        lettuce = next(v for v in varieties if "Lettuce" in v["common_name"])

        # Create planting event
        planting_response = client.post(
            "/planting-events/",
            headers=headers,
            json={
                "garden_id": garden["id"],
                "plant_variety_id": lettuce["id"],
                "planting_date": str(date.today()),
                "planting_method": "transplant",
                "plant_count": 12
            }
        )
        assert planting_response.status_code == 200

        # Simulate sensor reading with out-of-range temperature
        sensor_response = client.post(
            "/sensor-readings/",
            headers=headers,
            json={
                "garden_id": garden["id"],
                "reading_date": str(date.today()),
                "temperature_f": 80.0,  # Too high!
                "humidity_percent": 50.0,
                "light_hours": 16.0
            }
        )
        assert sensor_response.status_code == 200

        # Verify high-priority temperature adjustment task was created
        tasks = client.get("/tasks/", headers=headers).json()
        temp_tasks = [t for t in tasks if t["task_type"] == "adjust_temperature"]
        assert len(temp_tasks) >= 1
        assert any(t["priority"] == "high" for t in temp_tasks)


class TestCompleteHydroponicsWorkflow:
    """Test complete hydroponics workflow with nutrient monitoring"""

    def test_full_hydroponics_workflow(self, client, test_db):
        """Test: Register → Create hydro garden → Plant → Monitor nutrients → Adjust pH/EC"""

        # Setup
        client.post("/auth/register", json={
            "email": "hydro@example.com",
            "password": "pass123",
            "full_name": "Hydro Grower"
        })
        login = client.post("/auth/login", data={
            "username": "hydro@example.com",
            "password": "pass123"
        })
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create hydroponic garden with full configuration
        garden_response = client.post(
            "/gardens/",
            headers=headers,
            json={
                "name": "NFT Hydro System",
                "garden_type": "indoor",
                "is_hydroponic": True,
                "hydro_system_type": "nft",
                "reservoir_size_liters": 100.0,
                "nutrient_schedule": "General Hydroponics",
                "ph_min": 5.5,
                "ph_max": 6.5,
                "ec_min": 1.2,
                "ec_max": 2.0,
                "ppm_min": 800,
                "ppm_max": 1400,
                "water_temp_min_f": 65.0,
                "water_temp_max_f": 72.0,
                "light_source_type": "led",
                "light_hours_per_day": 18.0
            }
        )
        assert garden_response.status_code == 200
        garden = garden_response.json()
        assert garden["is_hydroponic"] is True

        # Get lettuce variety
        varieties = client.get("/plant-varieties/").json()
        lettuce = next(v for v in varieties if "Lettuce" in v["common_name"])

        # Create planting event
        planting_response = client.post(
            "/planting-events/",
            headers=headers,
            json={
                "garden_id": garden["id"],
                "plant_variety_id": lettuce["id"],
                "planting_date": str(date.today()),
                "planting_method": "transplant",
                "plant_count": 24
            }
        )
        assert planting_response.status_code == 200

        # Verify hydroponic tasks were created
        tasks = client.get("/tasks/", headers=headers).json()
        task_types = [t["task_type"] for t in tasks]

        # Should have hydroponic-specific tasks
        assert "check_nutrient_solution" in task_types
        assert "clean_reservoir" in task_types
        assert "replace_nutrient_solution" in task_types

        # Simulate sensor reading with out-of-range pH
        sensor_response = client.post(
            "/sensor-readings/",
            headers=headers,
            json={
                "garden_id": garden["id"],
                "reading_date": str(date.today()),
                "temperature_f": 70.0,
                "humidity_percent": 60.0,
                "light_hours": 18.0,
                "ph_level": 7.2,  # Too high!
                "ec_ms_cm": 1.5,
                "ppm": 1050,
                "water_temp_f": 68.0
            }
        )
        assert sensor_response.status_code == 200

        # Verify pH adjustment task was created
        updated_tasks = client.get("/tasks/", headers=headers).json()
        ph_tasks = [t for t in updated_tasks if t["task_type"] == "adjust_ph"]
        assert len(ph_tasks) >= 1
        ph_task = ph_tasks[0]
        assert ph_task["priority"] == "high"
        assert "7.2" in ph_task["description"]

        # Simulate fixing pH and adding new reading
        sensor_response2 = client.post(
            "/sensor-readings/",
            headers=headers,
            json={
                "garden_id": garden["id"],
                "reading_date": str(date.today()),
                "ph_level": 6.0,  # Now in range
                "ec_ms_cm": 1.5
            }
        )
        assert sensor_response2.status_code == 200

        # Complete the pH adjustment task
        complete_response = client.patch(
            f"/tasks/{ph_task['id']}/complete",
            headers=headers
        )
        assert complete_response.status_code == 200


class TestMultiGardenManagement:
    """Test managing multiple gardens simultaneously"""

    def test_multiple_gardens_and_tasks(self, client, test_db):
        """Test user with outdoor, indoor, and hydroponic gardens"""

        # Setup
        client.post("/auth/register", json={
            "email": "multi@example.com",
            "password": "pass123",
            "full_name": "Multi Gardener"
        })
        login = client.post("/auth/login", data={
            "username": "multi@example.com",
            "password": "pass123"
        })
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create three different gardens
        outdoor = client.post("/gardens/", headers=headers, json={
            "name": "Outdoor Beds",
            "garden_type": "outdoor"
        }).json()

        indoor = client.post("/gardens/", headers=headers, json={
            "name": "Indoor Shelves",
            "garden_type": "indoor",
            "light_source_type": "led",
            "light_hours_per_day": 16.0
        }).json()

        hydro = client.post("/gardens/", headers=headers, json={
            "name": "Hydro System",
            "garden_type": "indoor",
            "is_hydroponic": True,
            "hydro_system_type": "dwc",
            "ph_min": 5.5,
            "ph_max": 6.5
        }).json()

        # Verify all gardens created
        gardens = client.get("/gardens/", headers=headers).json()
        assert len(gardens) == 3

        # Get varieties
        varieties = client.get("/plant-varieties/").json()
        tomato = next(v for v in varieties if v["common_name"] == "Tomato")
        lettuce = next(v for v in varieties if "Lettuce" in v["common_name"])

        # Plant in each garden
        for garden in [outdoor, indoor, hydro]:
            variety = tomato if garden["id"] == outdoor["id"] else lettuce
            client.post("/planting-events/", headers=headers, json={
                "garden_id": garden["id"],
                "plant_variety_id": variety["id"],
                "planting_date": str(date.today()),
                "planting_method": "transplant",
                "plant_count": 6
            })

        # Get all tasks
        all_tasks = client.get("/tasks/", headers=headers).json()

        # Should have tasks from all three gardens
        assert len(all_tasks) > 10  # Many tasks across all gardens

        # Verify task diversity
        task_types = set(t["task_type"] for t in all_tasks)
        assert "water" in task_types  # Common to all
        assert "check_nutrient_solution" in task_types  # Hydro-specific


class TestErrorRecoveryWorkflows:
    """Test error handling and recovery scenarios"""

    def test_invalid_sensor_reading_recovery(self, client, sample_user, hydroponic_garden, user_token):
        """Test that invalid sensor readings are rejected properly"""
        headers = {"Authorization": f"Bearer {user_token}"}

        # Try to submit invalid pH
        response = client.post(
            "/sensor-readings/",
            headers=headers,
            json={
                "garden_id": hydroponic_garden.id,
                "reading_date": str(date.today()),
                "ph_level": 15.0  # Invalid!
            }
        )
        assert response.status_code == 422

        # Submit valid reading
        response = client.post(
            "/sensor-readings/",
            headers=headers,
            json={
                "garden_id": hydroponic_garden.id,
                "reading_date": str(date.today()),
                "ph_level": 6.0
            }
        )
        assert response.status_code == 200

    def test_unauthorized_access_protection(self, client, test_db):
        """Test that users cannot access each other's data"""

        # Create two users
        client.post("/auth/register", json={
            "email": "user1@example.com",
            "password": "pass123",
            "full_name": "User One"
        })
        login1 = client.post("/auth/login", data={
            "username": "user1@example.com",
            "password": "pass123"
        })
        token1 = login1.json()["access_token"]

        client.post("/auth/register", json={
            "email": "user2@example.com",
            "password": "pass456",
            "full_name": "User Two"
        })
        login2 = client.post("/auth/login", data={
            "username": "user2@example.com",
            "password": "pass456"
        })
        token2 = login2.json()["access_token"]

        # User 1 creates a garden
        garden = client.post(
            "/gardens/",
            headers={"Authorization": f"Bearer {token1}"},
            json={"name": "User1 Garden", "garden_type": "outdoor"}
        ).json()

        # User 2 tries to access User 1's garden
        response = client.get(
            f"/gardens/{garden['id']}",
            headers={"Authorization": f"Bearer {token2}"}
        )
        # Should be 404 (not found) or 403 (forbidden)
        assert response.status_code in [403, 404]
