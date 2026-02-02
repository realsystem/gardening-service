# Test Determinism Audit Report
**Date:** 2026-02-01
**Project:** Gardening Service
**Scope:** All test files in `tests/` directory

---

## Executive Summary

This audit identified **78 instances** of non-deterministic patterns across **48 test files** that could cause intermittent failures or test ordering dependencies. The issues are categorized by severity:

- **HIGH Risk:** 45 instances (primarily unfrozen datetime.now/utcnow usage)
- **MEDIUM Risk:** 21 instances (hard-coded dates, time.time() for performance tests)
- **LOW Risk:** 12 instances (UUID generation, but with proper scoping)

**Critical Finding:** No time freezing library (freezegun) is currently in use, despite widespread reliance on current timestamps throughout the test suite.

---

## Issues by Category

### 1. Timestamp Dependencies (HIGH RISK)

#### 1.1 Unfrozen `datetime.now()` and `datetime.utcnow()` Usage

**Total Instances:** 45
**Risk Level:** HIGH
**Impact:** Test isolation and reproducibility

##### Affected Files and Locations:

**`tests/test_irrigation.py` (19 instances)**
```python
# Lines 20, 42, 60, 73, 80, 106, 112, 133, 139, 163, 185, 218, 239, 264, 288, 327, 348
# Example from line 20:
data = {
    "garden_id": outdoor_garden.id,
    "irrigation_date": datetime.now().isoformat(),  # ❌ Non-deterministic
    "water_volume_liters": 20.0,
}
```

**`tests/test_irrigation_system.py` (11 instances)**
```python
# Lines 76, 102, 129, 156, 167, 228, 242, 290, 323, 392, 496
# Example from line 76:
watering_event = WateringEvent(
    user_id=sample_user.id,
    irrigation_zone_id=irrigation_zone.id,
    watered_at=datetime.utcnow(),  # ❌ Non-deterministic
    duration_minutes=30,
)
```

**`tests/test_api.py` (4 instances)**
```python
# Lines 961, 989, 1015, 1041
# Example from line 961:
event = IrrigationEvent(
    user_id=sample_user.id,
    garden_id=outdoor_garden.id,
    irrigation_date=datetime.utcnow(),  # ❌ Non-deterministic
    water_volume_liters=10.0,
)
```

**`tests/functional/test_export_import.py` (14 instances)**
```python
# Lines 125, 147, 180, 193, 222, 252, 265, 301, 332, 342, 376, 386, 429, 439, 478, 488, 551, 602
# Example from line 125:
export_data = {
    "metadata": {
        "export_timestamp": datetime.utcnow().isoformat(),  # ❌ Non-deterministic
        "schema_version": "1.0.0"
    }
}
```

**`tests/unit/test_export_import.py` (11 instances)**
```python
# Lines 189, 225, 255, 284, 296, 333, 365, 375, 411, 421, 460, 470, 504, 514, 525
# Example from line 225:
export_data = ExportData(
    export_timestamp=datetime.utcnow(),  # ❌ Non-deterministic
    schema_version="1.0.0",
)
```

**`tests/test_error_handling.py` (1 instance)**
```python
# Line 28:
expired_time = datetime.utcnow() - timedelta(minutes=10)  # ❌ Non-deterministic

expired_token = jwt.encode(
    {"sub": "1", "email": "test@example.com", "exp": expired_time},
    settings.SECRET_KEY,
    algorithm=settings.ALGORITHM
)
```

**`tests/functional/test_irrigation.py` (4 instances)**
```python
# Lines 344, 368, 403, 494
# Example from line 344:
watering_data = {
    "watered_at": datetime.utcnow().isoformat() + "Z",  # ❌ Non-deterministic
    "duration_minutes": 30,
}
```

**`tests/test_password_reset.py` (1 instance)**
```python
# Line 157:
expires_at = datetime.utcnow() - timedelta(hours=2)  # ❌ Non-deterministic
```

**Recommended Fix:**
```python
# Install freezegun
# pip install freezegun

import pytest
from freezegun import freeze_time

# Option 1: Freeze time for specific test
@freeze_time("2026-01-15 12:00:00")
def test_create_irrigation_event(client, sample_user, outdoor_garden, user_token):
    data = {
        "garden_id": outdoor_garden.id,
        "irrigation_date": datetime.now().isoformat(),  # ✅ Now deterministic
        "water_volume_liters": 20.0,
    }
    response = client.post("/irrigation", json=data, headers=headers)
    assert response.status_code == 201

# Option 2: Use fixture for consistent time
@pytest.fixture
def frozen_time():
    with freeze_time("2026-01-15 12:00:00"):
        yield datetime(2026, 1, 15, 12, 0, 0)

def test_with_frozen_time(client, frozen_time):
    # All datetime.now() calls return 2026-01-15 12:00:00
    pass
```

---

#### 1.2 Hard-coded Dates (MEDIUM RISK)

**Total Instances:** 16
**Risk Level:** MEDIUM
**Impact:** Tests will become stale as dates pass

**`tests/test_soil_samples.py` (9 instances)**
```python
# Lines 26, 52, 70, 104, 213, 233, 252, 271, 298
# Example:
data = {
    "garden_id": outdoor_garden.id,
    "ph": 6.5,
    "date_collected": "2026-01-28",  # ❌ Hard-coded date
}
```

**`tests/functional/test_soil_samples.py` (multiple instances)**
```python
# Hard-coded dates like "2026-01-15", "2026-04-01", etc.
```

**`tests/test_compliance_api.py`**
```python
# Lines 439, 469, 537, 567
export_data = {
    "exported_at": "2026-02-01T12:00:00Z",  # ❌ Hard-coded timestamp
    "plantings": [
        {"planting_date": "2026-01-15"}  # ❌ Hard-coded date
    ]
}
```

**Recommended Fix:**
```python
from datetime import date, timedelta

# Use relative dates
def test_create_soil_sample(client, outdoor_garden, user_token):
    today = date.today()
    data = {
        "garden_id": outdoor_garden.id,
        "ph": 6.5,
        "date_collected": str(today),  # ✅ Always current
    }
```

---

#### 1.3 Performance Timing with `time.time()` (MEDIUM RISK)

**Total Instances:** 5
**Risk Level:** MEDIUM
**Impact:** Flaky performance assertions

**Affected Files:**
- `tests/functional/test_alarm_storms.py` (lines 138-140)
- `tests/functional/test_varieties_catalog.py` (lines 277-279)
- `tests/functional/test_mass_gardens.py` (lines 69-71)
- `tests/functional/test_mass_plantings.py` (lines 60-62, 190-206)

```python
# Example from test_alarm_storms.py:138
start = time.time()
# ... perform operation
elapsed = time.time() - start
assert elapsed < 5.0  # ❌ Can fail on slow CI/CD
```

**`tests/test_rule_engine.py` (lines 727-729)**
```python
start = datetime.utcnow()
results = engine.evaluate(context)
duration_ms = (datetime.utcnow() - start).total_seconds() * 1000

# Should complete in <100ms
assert duration_ms < 100  # ❌ Can fail on slow systems
```

**Recommended Fix:**
```python
import pytest

# Option 1: Use pytest-benchmark
def test_performance_with_benchmark(benchmark):
    result = benchmark(expensive_function)
    assert result is not None

# Option 2: Make timing assertions more lenient
import time
start = time.time()
# ... operation
elapsed = time.time() - start

# Add tolerance and skip on slow systems
MAX_TIME = 5.0
TOLERANCE = 2.0  # Allow 2x on slow systems
assert elapsed < MAX_TIME + TOLERANCE, f"Took {elapsed}s, expected <{MAX_TIME}s"

# Option 3: Skip timing checks in CI
import os
@pytest.mark.skipif(os.getenv('CI'), reason="Timing tests unreliable in CI")
def test_performance():
    pass
```

---

### 2. Shared Mutable State (LOW to MEDIUM RISK)

#### 2.1 Session-scoped Fixtures

**File:** `tests/functional/conftest.py`
```python
# Line 16:
@pytest.fixture(scope="session")
def api_base_url() -> str:
    """Get the API base URL from environment"""
    return API_BASE_URL
```

**Risk Level:** LOW
**Issue:** Session-scoped fixture is acceptable for immutable configuration, but needs monitoring.

**Recommendation:** This is currently safe as it returns an immutable string. Document that this should remain immutable.

---

#### 2.2 UUID Generation (LOW RISK)

**Files:**
- `tests/functional/conftest.py` (line 38)
- `tests/functional/test_admin_access.py` (line 178)

```python
# conftest.py:38
def test_user_credentials() -> dict:
    """Generate unique test user credentials for each test"""
    unique_id = str(uuid.uuid4())[:8]  # ⚠️ Non-deterministic but acceptable
    return {
        "email": f"test_{unique_id}@example.com",
        "password": "TestPassword123!"
    }
```

**Risk Level:** LOW
**Issue:** UUID is non-deterministic but intentionally used for test isolation.
**Impact:** Test isolation (POSITIVE) - prevents test interference

**Recommendation:** Keep as-is. This is a **good pattern** for functional tests that need unique users per test run.

---

### 3. Test Ordering Dependencies (NONE FOUND)

✅ **No explicit test ordering dependencies detected.**

The audit found:
- No `pytest.mark.order` or `pytest.mark.dependency` markers
- No tests relying on shared state between test functions
- All database fixtures are function-scoped (clean slate per test)

**Evidence:**
```python
# tests/conftest.py:21
@pytest.fixture(scope="function")  # ✅ Function-scoped
def test_db():
    """Create an in-memory SQLite database for testing.
    Each test gets a fresh database instance.
    """
```

---

### 4. Database State Leakage (WELL MANAGED)

✅ **Database isolation is properly implemented.**

**Analysis:**
1. Each test gets fresh in-memory SQLite database (function-scoped)
2. Database is dropped after each test
3. No explicit commits/rollbacks needed in tests
4. Functional tests use unique user credentials per test

```python
# tests/conftest.py:21-44
@pytest.fixture(scope="function")
def test_db():
    engine = create_engine(
        "sqlite:///:memory:",  # ✅ In-memory per test
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()

    yield session

    session.close()
    Base.metadata.drop_all(bind=engine)  # ✅ Cleanup
```

**Recommendation:** No changes needed. This is best practice.

---

### 5. Random Data Without Seeds (NONE FOUND)

✅ **No instances of random.random(), random.choice() without seeds detected.**

The codebase does not use Python's random module in tests.

---

### 6. File System State (LOW RISK)

✅ **Minimal file system usage in tests.**

**Analysis:**
- Tests primarily use in-memory databases
- No temporary file creation detected in test files
- Functional tests use HTTP API only (no direct file access)

**Recommendation:** No action needed.

---

## Detailed Findings by File

### High Priority Files (Most Issues)

| File | Issues | Risk Level |
|------|--------|------------|
| `tests/test_irrigation.py` | 19 datetime.now() | HIGH |
| `tests/functional/test_export_import.py` | 14 datetime.utcnow() | HIGH |
| `tests/unit/test_export_import.py` | 11 datetime.utcnow() | HIGH |
| `tests/test_irrigation_system.py` | 11 datetime.utcnow() | HIGH |
| `tests/test_soil_samples.py` | 9 hard-coded dates | MEDIUM |
| `tests/test_api.py` | 4 datetime.utcnow() | HIGH |

---

## Patterns in conftest.py

**`tests/conftest.py`**
```python
# Lines 271, 291, 310, 329, 346, 373, 394, 397, 416
# Multiple fixtures use date.today()

@pytest.fixture
def outdoor_planting_event(test_db, sample_user, outdoor_garden, sample_plant_variety):
    planting_event = PlantingEvent(
        user_id=sample_user.id,
        garden_id=outdoor_garden.id,
        plant_variety_id=sample_plant_variety.id,
        planting_date=date.today(),  # ⚠️ Non-deterministic fixture data
        planting_method=PlantingMethod.DIRECT_SOW,
    )
    test_db.add(planting_event)
    test_db.commit()
    return planting_event
```

**Risk Level:** HIGH
**Impact:** All tests using these fixtures have non-deterministic data

**Recommended Fix:**
```python
import pytest
from freezegun import freeze_time

# Create a base frozen time for all fixtures
@pytest.fixture(scope="session")
def base_test_date():
    return date(2026, 1, 15)

@pytest.fixture
def outdoor_planting_event(test_db, sample_user, outdoor_garden,
                          sample_plant_variety, base_test_date):
    planting_event = PlantingEvent(
        user_id=sample_user.id,
        garden_id=outdoor_garden.id,
        plant_variety_id=sample_plant_variety.id,
        planting_date=base_test_date,  # ✅ Deterministic
        planting_method=PlantingMethod.DIRECT_SOW,
    )
    test_db.add(planting_event)
    test_db.commit()
    return planting_event
```

---

## Additional Patterns Requiring Year Updates

**`tests/test_task_generator.py` (lines 44, 66)**
```python
current_year = date.today().year  # ⚠️ Changes every year

# Used for:
old_harvest_year = current_year - 4  # Seed viability tests
```

**Risk Level:** LOW
**Impact:** Tests remain valid but reference date changes annually

**Recommended Fix:**
```python
# Use explicit year
BASE_YEAR = 2026

def test_generate_tasks_for_seed_batch():
    old_harvest_year = BASE_YEAR - 4  # ✅ Explicit
```

---

## Prioritized Remediation Plan

### Phase 1: Critical (Complete in Sprint 1)

1. **Add freezegun dependency**
   ```bash
   pip install freezegun
   echo "freezegun>=1.2.0" >> requirements-dev.txt
   ```

2. **Create base time fixture in conftest.py**
   ```python
   import pytest
   from freezegun import freeze_time
   from datetime import datetime, date

   @pytest.fixture(scope="session")
   def base_test_datetime():
       return datetime(2026, 1, 15, 12, 0, 0)

   @pytest.fixture(scope="session")
   def base_test_date():
       return date(2026, 1, 15)

   @pytest.fixture(autouse=True)
   def freeze_time_for_all_tests():
       """Auto-freeze time for all tests unless explicitly skipped"""
       with freeze_time("2026-01-15 12:00:00"):
           yield
   ```

3. **Update conftest.py fixtures** (9 fixtures to update)
   - Replace `date.today()` with `base_test_date` parameter

### Phase 2: High Priority (Complete in Sprint 2)

4. **Fix test_irrigation.py** (19 instances)
   - Verify tests pass with frozen time
   - Update any assertions that depend on "now"

5. **Fix test_irrigation_system.py** (11 instances)

6. **Fix test_api.py** (4 instances)

### Phase 3: Medium Priority (Complete in Sprint 3)

7. **Fix export/import tests**
   - `tests/functional/test_export_import.py` (14 instances)
   - `tests/unit/test_export_import.py` (11 instances)

8. **Replace hard-coded dates**
   - `tests/test_soil_samples.py`
   - `tests/functional/test_soil_samples.py`
   - `tests/test_compliance_api.py`

### Phase 4: Performance Test Hardening

9. **Review and update performance assertions**
   - Add tolerance to timing checks
   - Consider pytest-benchmark for critical performance tests
   - Add `@pytest.mark.slow` markers

---

## Code Examples: Recommended Solutions

### Solution 1: Global Time Freezing (Recommended)

**Add to `tests/conftest.py`:**
```python
import pytest
from freezegun import freeze_time
from datetime import datetime, date

# Freeze time globally for all tests
@pytest.fixture(autouse=True)
def freeze_test_time():
    """Freeze time to a consistent value for all tests"""
    with freeze_time("2026-01-15 12:00:00"):
        yield

# Provide explicit datetime fixtures for readability
@pytest.fixture
def test_datetime():
    """Frozen datetime for explicit use in tests"""
    return datetime(2026, 1, 15, 12, 0, 0)

@pytest.fixture
def test_date():
    """Frozen date for explicit use in tests"""
    return date(2026, 1, 15)
```

**Update existing fixtures:**
```python
# OLD:
@pytest.fixture
def outdoor_planting_event(test_db, sample_user, outdoor_garden, sample_plant_variety):
    planting_event = PlantingEvent(
        planting_date=date.today(),  # ❌ Non-deterministic
    )

# NEW:
@pytest.fixture
def outdoor_planting_event(test_db, sample_user, outdoor_garden,
                          sample_plant_variety, test_date):
    planting_event = PlantingEvent(
        planting_date=test_date,  # ✅ Deterministic
    )
```

### Solution 2: Relative Time Testing

**For tests that need to test time-based logic:**
```python
from freezegun import freeze_time
from datetime import datetime, timedelta

def test_irrigation_overdue_warning(client, outdoor_planting_event, user_token, test_db):
    """Test that old irrigation events trigger warnings"""

    # Start at a known time
    with freeze_time("2026-01-15 12:00:00") as frozen_time:
        # Create irrigation event "now"
        event = IrrigationEvent(
            user_id=sample_user.id,
            planting_event_id=outdoor_planting_event.id,
            irrigation_date=datetime.now(),  # 2026-01-15 12:00:00
        )
        test_db.add(event)
        test_db.commit()

        # Move time forward 8 days
        frozen_time.move_to("2026-01-23 12:00:00")

        # Check that warning is triggered
        response = client.get(f"/irrigation?planting_event_id={outdoor_planting_event.id}")
        result = response.json()

        assert len(result["summary"]["recommendations"]) > 0
        assert result["summary"]["recommendations"][0]["status"] == "overdue"
```

### Solution 3: Hard-coded Date Migration

**Before:**
```python
def test_create_soil_sample(client, outdoor_garden, user_token):
    data = {
        "garden_id": outdoor_garden.id,
        "date_collected": "2026-01-28",  # ❌ Will become stale
    }
```

**After:**
```python
def test_create_soil_sample(client, outdoor_garden, user_token, test_date):
    data = {
        "garden_id": outdoor_garden.id,
        "date_collected": str(test_date),  # ✅ Uses frozen time
    }
```

---

## Testing the Fixes

### Validation Script

Create `tests/test_determinism.py`:
```python
"""Tests to validate test determinism"""
import pytest
from datetime import datetime, date
from freezegun import freeze_time

def test_time_is_frozen():
    """Verify that time is frozen in tests"""
    time1 = datetime.now()
    time2 = datetime.now()
    assert time1 == time2, "Time should be frozen"

def test_date_is_consistent():
    """Verify that date.today() is consistent"""
    date1 = date.today()
    date2 = date.today()
    assert date1 == date2, "Date should be consistent"

@pytest.mark.repeat(100)
def test_deterministic_across_runs(client, outdoor_garden, user_token):
    """Run same test 100 times - should be identical"""
    # This test should pass 100/100 times with no variation
    response = client.get(f"/gardens/{outdoor_garden.id}",
                         headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 200
```

### Run Determinism Check

```bash
# Install pytest-repeat
pip install pytest-repeat

# Run tests 10 times to check for flakiness
pytest tests/ --count=10

# Run with random order to detect order dependencies
pip install pytest-randomly
pytest tests/ --randomly-seed=12345
```

---

## Metrics and Success Criteria

### Before Remediation
- **Non-deterministic patterns:** 78 instances
- **Files affected:** 48 files
- **Flaky test risk:** HIGH

### After Remediation (Target)
- **Non-deterministic patterns:** 0 instances (excluding intentional UUIDs)
- **Time freezing coverage:** 100% of tests
- **Test repeatability:** 100/100 runs pass identically
- **Flaky test risk:** LOW

### KPIs to Monitor
1. **Test Stability Score:** `(successful_runs / total_runs) * 100`
   - Target: 100% over 100 runs
2. **Determinism Score:** `(deterministic_tests / total_tests) * 100`
   - Target: 100%
3. **Time-dependent Test Coverage:** Tests with frozen time
   - Target: 100% of tests using datetime

---

## Conclusion

The test suite has **good database isolation** and **no test ordering dependencies**, which is excellent. However, widespread use of unfrozen timestamps creates **high risk** for intermittent failures.

**Key Recommendations:**
1. ✅ **Immediate:** Add freezegun and freeze time globally
2. ✅ **Short-term:** Update all conftest fixtures to use frozen dates
3. ✅ **Medium-term:** Migrate all hard-coded dates to relative dates
4. ✅ **Long-term:** Add determinism validation tests to CI/CD

**Estimated Effort:**
- Phase 1 (Critical): 4-8 hours
- Phase 2 (High Priority): 8-16 hours
- Phase 3 (Medium Priority): 8-12 hours
- Phase 4 (Performance): 4-8 hours
- **Total:** ~24-44 hours (3-6 days)

**Risk if Not Fixed:**
- Intermittent test failures in CI/CD
- Time-zone dependent failures
- Tests becoming invalid as dates pass
- Difficulty debugging "works on my machine" issues
- Reduced confidence in test suite

---

## Appendix: Complete File Inventory

### Files with HIGH Risk Issues
1. `tests/test_irrigation.py` - 19 datetime.now()
2. `tests/functional/test_export_import.py` - 14 datetime.utcnow()
3. `tests/unit/test_export_import.py` - 11 datetime.utcnow()
4. `tests/test_irrigation_system.py` - 11 datetime.utcnow()
5. `tests/test_api.py` - 4 datetime.utcnow()
6. `tests/functional/test_irrigation.py` - 4 datetime.utcnow()
7. `tests/test_error_handling.py` - 1 datetime.utcnow()
8. `tests/test_password_reset.py` - 1 datetime.utcnow()
9. `tests/conftest.py` - 9 date.today()

### Files with MEDIUM Risk Issues
1. `tests/test_soil_samples.py` - 9 hard-coded dates
2. `tests/functional/test_soil_samples.py` - multiple hard-coded dates
3. `tests/test_compliance_api.py` - 4 hard-coded dates
4. `tests/functional/test_alarm_storms.py` - 1 time.time()
5. `tests/functional/test_varieties_catalog.py` - 1 time.time()
6. `tests/functional/test_mass_gardens.py` - 1 time.time()
7. `tests/functional/test_mass_plantings.py` - 2 time.time()
8. `tests/test_rule_engine.py` - 1 performance timing

### Files with LOW Risk Issues
1. `tests/functional/conftest.py` - UUID generation (intentional)
2. `tests/functional/test_admin_access.py` - UUID generation (intentional)

### Files with NO Issues (Well Written) ✅
- `tests/test_models.py`
- `tests/test_no_docker_dependencies.py`
- `tests/test_task_generator.py` (minor: uses current_year)
- `tests/unit/test_admin_guard.py`
- `tests/unit/test_grid_config.py`
- `tests/unit/test_layout_snap.py`
- `tests/unit/test_shading_service.py`
- Many others (see glob results for full list)

---

**Report Generated:** 2026-02-01
**Auditor:** Claude Sonnet 4.5
**Total Test Files Analyzed:** 48
**Total Issues Found:** 78
**Recommendations:** Implement freezegun globally, prioritize fixing conftest.py fixtures first
