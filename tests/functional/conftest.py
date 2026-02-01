"""Fixtures for functional API tests

These fixtures support real HTTP calls against a running backend.
"""
import os
import uuid
from typing import Generator, Optional
import pytest
import httpx


# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8080")


@pytest.fixture(scope="session")
def api_base_url() -> str:
    """Get the API base URL from environment"""
    return API_BASE_URL


@pytest.fixture(scope="function")
def http_client(api_base_url: str) -> Generator[httpx.Client, None, None]:
    """Create an HTTP client for API calls

    This is a function-scoped fixture, so each test gets a fresh client.
    """
    with httpx.Client(base_url=api_base_url, timeout=10.0) as client:
        yield client


@pytest.fixture(scope="function")
def test_user_credentials() -> dict:
    """Generate unique test user credentials for each test

    Using unique emails ensures tests don't interfere with each other.
    """
    unique_id = str(uuid.uuid4())[:8]
    return {
        "email": f"test_{unique_id}@example.com",
        "password": "TestPassword123!"
    }


@pytest.fixture(scope="function")
def registered_user(http_client: httpx.Client, test_user_credentials: dict) -> dict:
    """Register a test user and return credentials + user data

    This creates a fresh user for each test that needs authentication.
    """
    response = http_client.post(
        "/users",
        json=test_user_credentials
    )
    assert response.status_code == 201, f"User registration failed: {response.text}"
    user_data = response.json()

    return {
        **test_user_credentials,
        "user_id": user_data["id"],
        "user_data": user_data
    }


@pytest.fixture(scope="function")
def auth_token(http_client: httpx.Client, registered_user: dict) -> str:
    """Login and return authentication token

    This provides a valid JWT token for authenticated requests.
    """
    response = http_client.post(
        "/users/login",
        json={
            "email": registered_user["email"],
            "password": registered_user["password"]
        }
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    token_data = response.json()
    return token_data["access_token"]


@pytest.fixture(scope="function")
def auth_headers(auth_token: str) -> dict:
    """Return authentication headers with Bearer token"""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture(scope="function")
def authenticated_client(
    http_client: httpx.Client,
    auth_headers: dict
) -> httpx.Client:
    """Return an HTTP client with authentication headers pre-configured"""
    http_client.headers.update(auth_headers)
    return http_client


# Resource cleanup helpers
@pytest.fixture(scope="function")
def cleanup_gardens(authenticated_client: httpx.Client) -> Generator[list, None, None]:
    """Track and cleanup gardens created during test

    Usage:
        garden_ids = cleanup_gardens
        # create gardens and append IDs to garden_ids
        # cleanup happens automatically after test
    """
    garden_ids = []
    yield garden_ids

    # Cleanup after test
    for garden_id in garden_ids:
        try:
            authenticated_client.delete(f"/gardens/{garden_id}")
        except Exception:
            pass  # Best effort cleanup


@pytest.fixture(scope="function")
def cleanup_lands(authenticated_client: httpx.Client) -> Generator[list, None, None]:
    """Track and cleanup lands created during test"""
    land_ids = []
    yield land_ids

    for land_id in land_ids:
        try:
            authenticated_client.delete(f"/lands/{land_id}")
        except Exception:
            pass


@pytest.fixture(scope="function")
def cleanup_soil_samples(authenticated_client: httpx.Client) -> Generator[list, None, None]:
    """Track and cleanup soil samples created during test"""
    sample_ids = []
    yield sample_ids

    for sample_id in sample_ids:
        try:
            authenticated_client.delete(f"/soil-samples/{sample_id}")
        except Exception:
            pass


@pytest.fixture(scope="function")
def cleanup_irrigation_zones(authenticated_client: httpx.Client) -> Generator[list, None, None]:
    """Track and cleanup irrigation zones created during test"""
    zone_ids = []
    yield zone_ids

    for zone_id in zone_ids:
        try:
            authenticated_client.delete(f"/irrigation-system/zones/{zone_id}")
        except Exception:
            pass


@pytest.fixture(scope="function")
def cleanup_irrigation_sources(authenticated_client: httpx.Client) -> Generator[list, None, None]:
    """Track and cleanup irrigation sources created during test"""
    source_ids = []
    yield source_ids

    for source_id in source_ids:
        try:
            authenticated_client.delete(f"/irrigation-system/sources/{source_id}")
        except Exception:
            pass


@pytest.fixture(scope="function")
def test_land(authenticated_client: httpx.Client) -> dict:
    """Create a test land plot for tree and garden placement tests"""
    land_data = {
        "name": "Test Land",
        "width": 100.0,
        "height": 100.0
    }

    response = authenticated_client.post("/lands", json=land_data)
    assert response.status_code == 201, f"Land creation failed: {response.text}"

    return response.json()
