# Functional API Tests

## Overview

This directory contains **functional API tests** that verify end-to-end behavior by making real HTTP requests to a running backend.

These tests are distinct from unit tests - they test the system as a black box through the HTTP API layer.

## Test Philosophy

- **Real backend**: Tests run against actual FastAPI server with real database
- **HTTP client**: Use httpx to make authentic HTTP requests
- **No mocking**: Backend logic, database, and auth are all real
- **User behavior**: Tests represent actual user workflows and edge cases
- **Deterministic**: Each test creates its own data and cleans up
- **No test order dependency**: Tests can run in any order

## Test Coverage

**76 functional tests** covering:

### Authentication (`test_auth.py` - 13 tests)
- User registration (valid, invalid email, weak password, duplicates)
- User login (success, wrong password, non-existent user)
- Authorization (valid token, invalid token, no token, malformed header)
- User profile (get, delete)

### Gardens (`test_gardens.py` - 18 tests)
- Garden creation (outdoor, indoor, hydroponic)
- Garden listing (empty, filtered by user)
- Garden retrieval (by ID, non-existent, other user's garden)
- Garden updates (success, partial, non-existent)
- Garden deletion (success, non-existent, authorization)

### Soil Samples (`test_soil_samples.py` - 14 tests)
- Soil sample creation (full data, minimal data, invalid garden, invalid pH)
- Soil sample listing (by garden, all user samples)
- Soil sample retrieval (by ID, non-existent)
- Soil sample updates (success, partial fields, non-existent)
- Soil sample deletion (success, non-existent)
- Business logic (date sorting)

### Irrigation System (`test_irrigation.py` - 14 tests)
- Water sources (create, list, delete)
- Irrigation zones (create with/without source, list, update, delete)
- Garden-zone assignments (assign, unassign)
- Watering events (zone events, manual garden events, listing)
- Overview and insights (comprehensive data, rule engine)

### Land Layout (`test_layout.py` - 17 tests)
- Land creation (success, invalid dimensions, listing)
- Garden positioning (place, update, remove)
- Spatial validation (bounds checking, negative coords, zero dims, overlaps, adjacent)
- Land updates (dimensions, constraint validation)
- Land deletion (success, orphaning gardens)

## Running Tests

### Prerequisites

1. **Backend must be running**:
   ```bash
   docker-compose up -d
   ```

2. **Database must be initialized**:
   ```bash
   # Migrations are run automatically by docker-compose
   ```

### Run All Functional Tests

```bash
# Default (uses http://localhost:8080)
pytest tests/functional/ -v

# Custom API URL
API_BASE_URL=http://localhost:8080 pytest tests/functional/ -v

# With coverage
pytest tests/functional/ --cov=app --cov-report=html
```

### Run Specific Test Module

```bash
pytest tests/functional/test_auth.py -v
pytest tests/functional/test_gardens.py -v
pytest tests/functional/test_irrigation.py -v
```

### Run Specific Test Class or Test

```bash
pytest tests/functional/test_auth.py::TestUserRegistration -v
pytest tests/functional/test_auth.py::TestUserRegistration::test_register_new_user_success -v
```

### Useful Options

```bash
# Stop at first failure
pytest tests/functional/ -x

# Show detailed output
pytest tests/functional/ -vv

# Run in parallel (if pytest-xdist installed)
pytest tests/functional/ -n auto

# Show print statements
pytest tests/functional/ -s
```

## Test Structure

### Fixtures (`conftest.py`)

**Session/Function-scoped fixtures:**

- `api_base_url` - API base URL from environment
- `http_client` - Fresh httpx client per test
- `test_user_credentials` - Unique credentials per test
- `registered_user` - Registered user with credentials
- `auth_token` - Valid JWT token
- `auth_headers` - Authorization headers
- `authenticated_client` - Pre-configured authenticated client

**Cleanup fixtures:**

- `cleanup_gardens` - Auto-cleanup for created gardens
- `cleanup_lands` - Auto-cleanup for created lands
- `cleanup_soil_samples` - Auto-cleanup for soil samples
- `cleanup_irrigation_zones` - Auto-cleanup for irrigation zones
- `cleanup_irrigation_sources` - Auto-cleanup for water sources

### Test Organization

Each test module follows this pattern:

```python
class TestFeatureCreation:
    """Tests for creating resources"""

    def test_create_success(self, authenticated_client, cleanup_fixture):
        """Successfully create resource"""
        # Arrange
        data = {...}

        # Act
        response = authenticated_client.post("/endpoint", json=data)

        # Assert
        assert response.status_code == 201
        assert response.json()["field"] == expected_value

        # Cleanup (automatic via fixture)
        cleanup_fixture.append(response.json()["id"])
```

## Environment Variables

- `API_BASE_URL` - Base URL for API (default: `http://localhost:8080`)

## CI/CD Integration

These tests are designed for CI pipelines:

```yaml
# Example GitHub Actions
- name: Start services
  run: docker-compose up -d

- name: Wait for API
  run: ./scripts/wait-for-api.sh

- name: Run functional tests
  run: pytest tests/functional/ -v --tb=short
  env:
    API_BASE_URL: http://localhost:8080
```

## Debugging Failed Tests

### View detailed error
```bash
pytest tests/functional/test_auth.py::test_login_success -vv --tb=long
```

### Check API logs
```bash
docker-compose logs api --tail=50
```

### Inspect database state
```bash
docker-compose exec db psql -U gardener -d gardening_db -c "SELECT * FROM users LIMIT 5;"
```

### Run with pdb debugger
```bash
pytest tests/functional/test_auth.py::test_login_success --pdb
```

## Writing New Functional Tests

### Guidelines

1. **Use fixtures for setup**: Leverage existing fixtures instead of manual setup
2. **Clean up resources**: Use cleanup fixtures to prevent database pollution
3. **Assert HTTP status AND payload**: Verify both status codes and response data
4. **Test error cases**: Don't just test happy paths
5. **Use unique data**: Generate unique emails, names to avoid conflicts
6. **No hardcoded tokens**: Always use fixture-based auth
7. **Test authorization**: Verify users can't access others' resources

### Example

```python
def test_create_garden_success(
    authenticated_client: httpx.Client,
    cleanup_gardens: list
):
    """Successfully create a garden"""
    # Arrange
    garden_data = {
        "name": "Test Garden",
        "garden_type": "outdoor"
    }

    # Act
    response = authenticated_client.post("/gardens", json=garden_data)

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Garden"
    assert "id" in data

    # Cleanup
    cleanup_gardens.append(data["id"])
```

## Comparison with Other Test Types

| Aspect | Functional Tests | Unit Tests | Integration Tests |
|--------|-----------------|------------|-------------------|
| Backend | Real HTTP calls | Mocked/in-memory | Real but isolated |
| Database | Real PostgreSQL | In-memory SQLite | Real PostgreSQL |
| Speed | Slower (~1s/test) | Fast (<0.1s/test) | Medium |
| Scope | Full API stack | Single function | Multiple components |
| Use Case | E2E validation | Logic verification | Component interaction |

## Troubleshooting

### "Connection refused"
- Ensure API is running: `docker-compose ps api`
- Check API_BASE_URL is correct

### "401 Unauthorized"
- Check fixture dependencies (need `authenticated_client` or `auth_token`)
- Verify user creation succeeded

### "Duplicate key error"
- Tests aren't cleaning up properly
- Use unique test data (fixtures handle this)

### "Tests hang"
- Check httpx timeout settings
- Verify API isn't deadlocked

## Future Enhancements

Potential additions:

- [ ] Performance tests (response times)
- [ ] Load tests (concurrent users)
- [ ] WebSocket tests (real-time features)
- [ ] File upload tests (images, imports)
- [ ] Pagination tests (large datasets)
- [ ] Search and filter tests (complex queries)
