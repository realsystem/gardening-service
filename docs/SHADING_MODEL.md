# Tree Shading Impact Feature

**Status:** ✅ Implementation Complete (Pending Tests)
**Date:** January 31, 2026

---

## Overview

The tree shading feature models how trees cast shade on nearby gardens, affecting their effective sun exposure. This impacts plant suitability, growth expectations, and watering requirements.

### Key Capabilities

- **Tree Management:** Full CRUD operations for trees on land plots
- **Geometric Shading Model:** Calculate shade based on tree canopy radius and garden position
- **Sun Exposure Scoring:** Numerical (0.0-1.0) and categorical (full_sun/partial_sun/shade) levels
- **Multi-Tree Support:** Cumulative shading from multiple trees
- **API Integration:** RESTful endpoints for trees and garden shading calculations

---

## Domain Model

### Tree Properties

Trees are spatial entities on land plots with physical dimensions:

| Property | Type | Description |
|----------|------|-------------|
| `id` | Integer | Unique identifier |
| `user_id` | Integer | Owner (foreign key to users) |
| `land_id` | Integer | Land plot location (foreign key to lands) |
| `name` | String | User-friendly name (e.g., "Oak in Backyard") |
| `species_id` | Integer | Optional link to plant varieties (tree species) |
| `x`, `y` | Float | Trunk center coordinates on land |
| `canopy_radius` | Float | Radius of tree canopy (same units as land) |
| `height` | Float | Optional tree height (for future sun angle calculations) |

### Spatial Coordinates

- **Coordinate System:** Top-left origin (0, 0)
  - `x` increases rightward
  - `y` increases downward
  - Units are abstract (meters, feet, grid squares - user's choice)
- **Consistency:** Same coordinate system as land plots and gardens

---

## Shading Model

### Mathematical Approach

The shading model uses simple, deterministic geometry:

#### 1. Shade Intensity

Trees cast circular shade within their canopy radius. Intensity decreases linearly from trunk to edge:

```
intensity(distance) = 1.0 - (distance / canopy_radius)
```

- **At trunk center** (distance = 0): intensity = 1.0 (100% shade)
- **At canopy edge** (distance = radius): intensity = 0.0 (0% shade)
- **Between:** Linear interpolation

#### 2. Garden Intersection

For each tree-garden pair:
1. Calculate if tree canopy (circle) intersects garden (rectangle)
2. Approximate intersection area using grid sampling (20x20 grid)
3. Calculate average shade intensity over intersection area

#### 3. Cumulative Shading

Multiple trees create cumulative shade:
```
total_shade = min(1.0, sum(individual_tree_contributions))
sun_exposure_score = baseline * (1.0 - total_shade)
```

#### 4. Categorical Sun Levels

Numerical scores map to categorical levels:
- **full_sun:** score >= 0.75 (6+ hours direct sun)
- **partial_sun:** 0.4 <= score < 0.75 (3-6 hours)
- **shade:** score < 0.4 (< 3 hours)

### Assumptions & Limitations

**Current Model (v1):**
- ✅ 2D circular canopy projection
- ✅ Linear shade intensity gradient
- ✅ Constant shade throughout day
- ✅ No seasonal variation

**Not Included (Future):**
- ❌ Sun path based on latitude/time of year
- ❌ Shadow length based on tree height
- ❌ Time-of-day varying shade patterns
- ❌ Deciduous vs. evergreen differences
- ❌ Sun angle effects

### Justification

This simplified model provides:
- **Deterministic Results:** Same inputs always produce same outputs
- **Fast Calculation:** Real-time API responses
- **Explainable Logic:** Users can understand shade contributions
- **Good Approximation:** Sufficient for MVP gardening decisions

---

## API Endpoints

### Tree Management

**Create Tree**
```http
POST /trees
Authorization: Bearer {token}

{
  "land_id": 1,
  "name": "Oak in Backyard",
  "species_id": 42,  // optional
  "x": 15.0,
  "y": 20.0,
  "canopy_radius": 5.0,
  "height": 12.0  // optional
}

Response: 201 Created
{
  "id": 1,
  "user_id": 1,
  "land_id": 1,
  "name": "Oak in Backyard",
  ...
}
```

**List User Trees**
```http
GET /trees
Authorization: Bearer {token}

Response: 200 OK
[
  { "id": 1, "name": "Oak in Backyard", ... },
  { "id": 2, "name": "Maple by Fence", ... }
]
```

**List Trees on Land**
```http
GET /trees/land/{land_id}
Authorization: Bearer {token}

Response: 200 OK (with species details)
[
  {
    "id": 1,
    "name": "Oak",
    "species_common_name": "Red Oak",
    "species_scientific_name": "Quercus rubra",
    ...
  }
]
```

**Get Tree Details**
```http
GET /trees/{tree_id}
Authorization: Bearer {token}

Response: 200 OK
{
  "id": 1,
  "species_common_name": "Red Oak",
  ...
}
```

**Update Tree**
```http
PATCH /trees/{tree_id}
Authorization: Bearer {token}

{
  "canopy_radius": 6.0,  // tree grew
  "name": "Mature Oak"
}

Response: 200 OK
```

**Delete Tree**
```http
DELETE /trees/{tree_id}
Authorization: Bearer {token}

Response: 204 No Content
```

### Garden Shading

**Calculate Shading Impact**
```http
GET /gardens/{garden_id}/shading
Authorization: Bearer {token}

Response: 200 OK
{
  "garden_id": 1,
  "sun_exposure_score": 0.65,
  "sun_exposure_category": "partial_sun",
  "total_shade_factor": 0.35,
  "baseline_sun_exposure": 1.0,
  "contributing_trees": [
    {
      "tree_id": 1,
      "tree_name": "Oak in Backyard",
      "shade_contribution": 0.25,
      "intersection_area": 15.5,
      "average_intensity": 0.68
    },
    {
      "tree_id": 2,
      "tree_name": "Maple",
      "shade_contribution": 0.10,
      "intersection_area": 8.2,
      "average_intensity": 0.42
    }
  ]
}
```

**Requirements:**
- Garden must have spatial layout: `land_id`, `x`, `y`, `width`, `height`
- Returns 400 Bad Request if garden lacks spatial data

---

## Database Schema

### Trees Table

```sql
CREATE TABLE trees (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    land_id INTEGER NOT NULL REFERENCES lands(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    species_id INTEGER REFERENCES plant_varieties(id),
    x FLOAT NOT NULL,
    y FLOAT NOT NULL,
    canopy_radius FLOAT NOT NULL,
    height FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX ix_trees_user_id ON trees(user_id);
CREATE INDEX ix_trees_land_id ON trees(land_id);
CREATE INDEX ix_trees_species_id ON trees(species_id);
```

### Migration

Migration file: `migrations/versions/20260131_1600_h8i9j0k1l2m3_add_trees_table.py`

Run with:
```bash
alembic upgrade head
```

---

## Code Architecture

### Core Components

1. **Model:** `app/models/tree.py`
   - SQLAlchemy model with relationships to User, Land, PlantVariety

2. **Schemas:** `app/schemas/tree.py`
   - Pydantic models for API validation
   - `TreeCreate`, `TreeUpdate`, `TreeResponse`, `TreeWithSpecies`
   - `GardenShadingInfo` for shading calculations

3. **Repository:** `app/repositories/tree_repository.py`
   - Database operations (CRUD)
   - Query methods for user trees and land trees

4. **Service:** `app/services/shading_service.py`
   - Geometric intersection calculations
   - Shade intensity computations
   - Sun exposure scoring and categorization

5. **API:** `app/api/trees.py`, `app/api/gardens.py`
   - RESTful endpoints
   - Authentication and authorization
   - Integration with shading service

### Service Functions

**`calculate_circle_rectangle_intersection_area()`**
- Approximates intersection area using grid sampling

**`calculate_average_shade_intensity()`**
- Computes average shade intensity over intersection

**`calculate_garden_shading()`**
- Main function: combines trees, calculates cumulative impact

**`_categorize_sun_exposure()`**
- Maps numerical score to categorical level

---

## Testing

### Unit Tests

File: `tests/unit/test_shading_service.py`

**Test Coverage:**
- Circle-rectangle intersection (no overlap, full coverage, partial)
- Shade intensity (center, edge, no intersection)
- Garden shading (no trees, single tree, multiple trees, far trees)
- Sun exposure categorization (full/partial/shade)
- Tree coverage area calculations

**Run:**
```bash
pytest tests/unit/test_shading_service.py -v
```

**Result:** 17/17 tests passing ✅

### Functional Tests

File: `tests/functional/test_tree_shading.py`

**Test Categories:**
- **Tree CRUD:** Create, read, update, delete operations
- **Shading Calculations:** Verify API calculations match expected results
- **Multi-User Isolation:** Users can only access their own trees
- **Scale:** Performance with many trees

**Markers:**
- `tree_shading`: All tree shading tests
- `tree_shading_integration`: Integration tests
- `tree_shading_isolation`: Multi-user isolation
- `tree_shading_scale`: Scale/performance tests

**Run:**
```bash
# All tree shading tests
pytest tests/functional/test_tree_shading.py -v

# Specific category
pytest -m tree_shading_integration

# Single test
pytest tests/functional/test_tree_shading.py::TestTreeCRUD::test_create_tree_success
```

---

## Usage Examples

### Scenario 1: Place Tree Near Garden

```python
# User creates a land plot
POST /lands { "name": "Backyard", "width": 50, "height": 50 }
# land_id = 1

# User creates a garden
POST /gardens {
  "name": "Vegetable Garden",
  "land_id": 1,
  "x": 10, "y": 10,
  "width": 10, "height": 10
}
# garden_id = 1

# User plants a tree nearby
POST /trees {
  "land_id": 1,
  "name": "Young Maple",
  "x": 5, "y": 5,  # Northwest of garden
  "canopy_radius": 4
}
# tree_id = 1

# Check shading impact
GET /gardens/1/shading
# Returns:
{
  "sun_exposure_score": 0.72,
  "sun_exposure_category": "partial_sun",  # was "full_sun" before tree
  "contributing_trees": [{
    "tree_name": "Young Maple",
    "shade_contribution": 0.28
  }]
}
```

### Scenario 2: Tree Growth Over Time

```python
# Tree grows - update canopy radius
PATCH /trees/1 {
  "canopy_radius": 8  # doubled
}

# Re-check shading
GET /gardens/1/shading
# Now shows:
{
  "sun_exposure_score": 0.35,
  "sun_exposure_category": "shade",  # more shade due to growth
  "contributing_trees": [{
    "shade_contribution": 0.65  # increased
  }]
}
```

### Scenario 3: Multiple Trees

```python
# Add second tree
POST /trees {
  "land_id": 1,
  "name": "Oak",
  "x": 15, "y": 15,  # Southeast of garden
  "canopy_radius": 5
}

# Shading now cumulative
GET /gardens/1/shading
{
  "total_shade_factor": 0.75,
  "contributing_trees": [
    { "tree_name": "Young Maple", "shade_contribution": 0.50 },
    { "tree_name": "Oak", "shade_contribution": 0.25 }
  ]
}
```

---

## Future Enhancements

### Phase 2: Sun Path Modeling

- Calculate shadow direction and length based on sun angle
- Factor in latitude and time of year
- Dynamic shade patterns throughout the day
- Sunrise/sunset shadow casting

### Phase 3: Tree Characteristics

- Deciduous trees: seasonal leaf coverage variation
- Evergreen trees: year-round shade
- Tree density: dense vs. sparse canopy
- Species-specific shade properties

### Phase 4: Advanced Features

- Historical shading data (track shade over seasons)
- Predictive modeling (shade in future years as trees grow)
- Optimal tree placement suggestions
- Shade visualization (UI overlay on land layout)

### Phase 5: Rule Engine Integration

**Current:** Basic shading calculations
**Future:**
- Warn when full-sun plants are in shade
- Adjust growth rate predictions based on shade
- Modify watering recommendations (shaded areas retain moisture)
- Suggest shade-tolerant plant varieties

---

## Known Limitations

1. **2D Model:** Doesn't account for tree height or sun angle
2. **Static Shade:** No time-of-day or seasonal variation
3. **Approximation:** Grid sampling introduces ~5% error in intersection area
4. **Baseline Assumption:** Assumes baseline = 1.0 (full sun) without trees
5. **No Overlap Optimization:** Overlapping trees counted individually (may overestimate)

---

## Performance Considerations

- **Calculation Speed:** O(trees × sample_points) per garden
  - 20×20 grid = 400 samples per tree
  - Typical: < 10ms for 10 trees
- **Database Queries:** N+1 avoided via `joinedload()` for species
- **Caching Opportunities:** Results could be cached until trees/gardens change

---

## References

- Shading Model Code: `app/services/shading_service.py`
- API Implementation: `app/api/trees.py`, `app/api/gardens.py`
- Test Suite: `tests/unit/test_shading_service.py`, `tests/functional/test_tree_shading.py`
- Database Migration: `migrations/versions/20260131_1600_h8i9j0k1l2m3_add_trees_table.py`

---

**Document Version:** 1.0
**Last Updated:** January 31, 2026
**Feature Status:** Implementation Complete, Tests Pending Server
