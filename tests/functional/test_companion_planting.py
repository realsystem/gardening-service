"""
Functional tests for companion planting analysis endpoint.

These tests verify the /gardens/{id}/companions endpoint with real HTTP requests.
"""

import pytest
import httpx
from typing import Dict, Any


@pytest.mark.companion_planting
class TestCompanionPlantingAnalysis:
    """Test companion planting analysis endpoint"""

    def test_companion_analysis_empty_garden(
        self,
        authenticated_client: httpx.Client,
        cleanup_gardens: list
    ):
        """Analysis of empty garden returns no relationships"""
        # Create a garden
        garden_response = authenticated_client.post("/gardens", json={
            "name": "Test Empty Garden",
            "garden_type": "outdoor"
        })
        assert garden_response.status_code == 201
        garden_id = garden_response.json()["id"]
        cleanup_gardens.append(garden_id)

        # Get companion analysis
        response = authenticated_client.get(f"/gardens/{garden_id}/companions")

        assert response.status_code == 200
        data = response.json()
        assert data["garden_id"] == garden_id
        assert data["planting_count"] == 0
        assert data["beneficial_pairs"] == []
        assert data["conflicts"] == []
        assert data["suggestions"] == []

    def test_companion_analysis_single_plant(
        self,
        authenticated_client: httpx.Client,
        cleanup_gardens: list,
        cleanup_plantings: list
    ):
        """Analysis with single plant returns message about needing 2+ plants"""
        # Create garden
        garden_response = authenticated_client.post("/gardens", json={
            "name": "Single Plant Garden",
            "garden_type": "outdoor"
        })
        assert garden_response.status_code == 201
        garden_id = garden_response.json()["id"]
        cleanup_gardens.append(garden_id)

        # Get a plant variety (assuming tomato exists from seed data)
        varieties_response = authenticated_client.get("/plant-varieties?search=tomato")
        assert varieties_response.status_code == 200
        varieties = varieties_response.json()
        assert len(varieties) > 0
        tomato_id = varieties[0]["id"]

        # Create a planting
        planting_response = authenticated_client.post("/planting-events", json={
            "garden_id": garden_id,
            "plant_variety_id": tomato_id,
            "planting_method": "seed",
            "quantity": 1,
            "x": 1.0,
            "y": 1.0
        })
        assert planting_response.status_code == 201
        cleanup_plantings.append(planting_response.json()["id"])

        # Get companion analysis
        response = authenticated_client.get(f"/gardens/{garden_id}/companions")

        assert response.status_code == 200
        data = response.json()
        assert data["planting_count"] == 1
        assert "message" in data
        assert "at least 2 plants" in data["message"].lower()

    def test_companion_analysis_beneficial_pair(
        self,
        authenticated_client: httpx.Client,
        cleanup_gardens: list,
        cleanup_plantings: list
    ):
        """Analysis detects beneficial companion pair (Tomato + Basil)"""
        # Create garden
        garden_response = authenticated_client.post("/gardens", json={
            "name": "Companion Garden",
            "garden_type": "outdoor"
        })
        assert garden_response.status_code == 201
        garden_id = garden_response.json()["id"]
        cleanup_gardens.append(garden_id)

        # Get tomato and basil varieties
        tomato_response = authenticated_client.get("/plant-varieties?search=tomato")
        assert tomato_response.status_code == 200
        tomato_id = tomato_response.json()[0]["id"]

        basil_response = authenticated_client.get("/plant-varieties?search=basil")
        assert basil_response.status_code == 200
        basil_id = basil_response.json()[0]["id"]

        # Plant tomato at (0, 0)
        tomato_planting = authenticated_client.post("/planting-events", json={
            "garden_id": garden_id,
            "plant_variety_id": tomato_id,
            "planting_method": "transplant",
            "quantity": 1,
            "x": 0.0,
            "y": 0.0
        })
        assert tomato_planting.status_code == 201
        cleanup_plantings.append(tomato_planting.json()["id"])

        # Plant basil at (0.5, 0) - within optimal distance
        basil_planting = authenticated_client.post("/planting-events", json={
            "garden_id": garden_id,
            "plant_variety_id": basil_id,
            "planting_method": "transplant",
            "quantity": 1,
            "x": 0.5,
            "y": 0.0
        })
        assert basil_planting.status_code == 201
        cleanup_plantings.append(basil_planting.json()["id"])

        # Get companion analysis
        response = authenticated_client.get(f"/gardens/{garden_id}/companions")

        assert response.status_code == 200
        data = response.json()
        assert data["planting_count"] == 2
        assert data["relationships_analyzed"] >= 1

        # Should have at least one beneficial pair
        assert len(data["beneficial_pairs"]) >= 1
        beneficial = data["beneficial_pairs"][0]
        assert beneficial["relationship_type"] == "beneficial"
        assert beneficial["confidence_level"] in ["high", "medium", "low"]
        assert "mechanism" in beneficial
        assert beneficial["distance_m"] == 0.5
        assert beneficial["status"] in ["optimal", "active"]

    def test_companion_analysis_antagonistic_pair(
        self,
        authenticated_client: httpx.Client,
        cleanup_gardens: list,
        cleanup_plantings: list
    ):
        """Analysis detects antagonistic companion pair too close together"""
        # Create garden
        garden_response = authenticated_client.post("/gardens", json={
            "name": "Conflict Garden",
            "garden_type": "outdoor"
        })
        assert garden_response.status_code == 201
        garden_id = garden_response.json()["id"]
        cleanup_gardens.append(garden_id)

        # Get tomato and broccoli varieties (antagonistic pair)
        tomato_response = authenticated_client.get("/plant-varieties?search=tomato")
        assert tomato_response.status_code == 200
        tomato_id = tomato_response.json()[0]["id"]

        broccoli_response = authenticated_client.get("/plant-varieties?search=broccoli")
        assert broccoli_response.status_code == 200
        broccoli_id = broccoli_response.json()[0]["id"]

        # Plant tomato at (0, 0)
        tomato_planting = authenticated_client.post("/planting-events", json={
            "garden_id": garden_id,
            "plant_variety_id": tomato_id,
            "planting_method": "transplant",
            "quantity": 1,
            "x": 0.0,
            "y": 0.0
        })
        assert tomato_planting.status_code == 201
        cleanup_plantings.append(tomato_planting.json()["id"])

        # Plant broccoli at (1.0, 0) - too close (effective distance is 3.0m)
        broccoli_planting = authenticated_client.post("/planting-events", json={
            "garden_id": garden_id,
            "plant_variety_id": broccoli_id,
            "planting_method": "transplant",
            "quantity": 1,
            "x": 1.0,
            "y": 0.0
        })
        assert broccoli_planting.status_code == 201
        cleanup_plantings.append(broccoli_planting.json()["id"])

        # Get companion analysis
        response = authenticated_client.get(f"/gardens/{garden_id}/companions")

        assert response.status_code == 200
        data = response.json()
        assert data["planting_count"] == 2

        # Should have at least one conflict
        assert len(data["conflicts"]) >= 1
        conflict = data["conflicts"][0]
        assert conflict["relationship_type"] == "antagonistic"
        assert conflict["status"] == "conflict"
        assert "recommended_separation_m" in conflict
        assert conflict["distance_m"] == 1.0

    def test_companion_analysis_unauthorized(self, http_client: httpx.Client):
        """Analysis requires authentication"""
        response = http_client.get("/gardens/1/companions")
        assert response.status_code == 401

    def test_companion_analysis_garden_not_found(
        self,
        authenticated_client: httpx.Client
    ):
        """Analysis returns 404 for non-existent garden"""
        response = authenticated_client.get("/gardens/99999/companions")
        assert response.status_code == 404

    def test_companion_analysis_mixed_relationships(
        self,
        authenticated_client: httpx.Client,
        cleanup_gardens: list,
        cleanup_plantings: list
    ):
        """Analysis handles multiple plant pairs with different relationships"""
        # Create garden
        garden_response = authenticated_client.post("/gardens", json={
            "name": "Mixed Companion Garden",
            "garden_type": "outdoor"
        })
        assert garden_response.status_code == 201
        garden_id = garden_response.json()["id"]
        cleanup_gardens.append(garden_id)

        # Get varieties: lettuce, carrot (neutral), radish
        lettuce_response = authenticated_client.get("/plant-varieties?search=lettuce")
        carrot_response = authenticated_client.get("/plant-varieties?search=carrot")
        radish_response = authenticated_client.get("/plant-varieties?search=radish")

        assert lettuce_response.status_code == 200
        assert carrot_response.status_code == 200
        assert radish_response.status_code == 200

        lettuce_id = lettuce_response.json()[0]["id"]
        carrot_id = carrot_response.json()[0]["id"]
        radish_id = radish_response.json()[0]["id"]

        # Plant in a triangle pattern
        plantings_data = [
            {"variety_id": lettuce_id, "x": 0.0, "y": 0.0},
            {"variety_id": carrot_id, "x": 1.0, "y": 0.0},
            {"variety_id": radish_id, "x": 0.5, "y": 0.2}
        ]

        for planting_data in plantings_data:
            planting_response = authenticated_client.post("/planting-events", json={
                "garden_id": garden_id,
                "plant_variety_id": planting_data["variety_id"],
                "planting_method": "seed",
                "quantity": 1,
                "x": planting_data["x"],
                "y": planting_data["y"]
            })
            assert planting_response.status_code == 201
            cleanup_plantings.append(planting_response.json()["id"])

        # Get companion analysis
        response = authenticated_client.get(f"/gardens/{garden_id}/companions")

        assert response.status_code == 200
        data = response.json()
        assert data["planting_count"] == 3
        assert data["relationships_analyzed"] >= 1  # Should analyze all pairs

        # Verify response structure
        assert "beneficial_pairs" in data
        assert "conflicts" in data
        assert "suggestions" in data
        assert "summary" in data
        assert data["summary"]["beneficial_count"] == len(data["beneficial_pairs"])
        assert data["summary"]["conflict_count"] == len(data["conflicts"])
        assert data["summary"]["suggestion_count"] == len(data["suggestions"])
