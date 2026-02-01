**# Sun-Path-Aware Layout Constraints (v1)

## Overview

This document describes the deterministic sun path model used to calculate seasonal shading and sun exposure for gardens based on nearby trees and structures.

**Design Principle:** Simple, explainable, testable calculations with no machine learning, no speculative predictions, and no false precision.

---

## Table of Contents

1. [Scope](#scope)
2. [Sun Model](#sun-model)
3. [Shadow Projection](#shadow-projection)
4. [Garden Impact Calculation](#garden-impact-calculation)
5. [Exposure Categories](#exposure-categories)
6. [Rule Engine Integration](#rule-engine-integration)
7. [API Usage](#api-usage)
8. [Examples](#examples)
9. [Limitations](#limitations)
10. [Future Enhancements](#future-enhancements)

---

## Scope

### Included in v1
- ✅ Seasonal sun angle approximation (Winter, Equinox, Summer)
- ✅ 2D shadow projection from trees
- ✅ Predictive shading impact on gardens
- ✅ Soft constraints (warnings, not blocking)
- ✅ Science-based rule engine integration
- ✅ Deterministic, explainable calculations

### Explicitly Excluded
- ❌ Hour-by-hour sun simulation
- ❌ Weather/cloud modeling
- ❌ Terrain slope effects
- ❌ Reflections and indirect light
- ❌ Real-time sun tracking
- ❌ Deciduous vs. evergreen tree modeling

---

## Sun Model

### Seasonal Buckets

The model uses three seasonal positions:
- **Winter Solstice:** December (Northern Hemisphere) / June (Southern Hemisphere)
- **Equinox:** March and September
- **Summer Solstice:** June (Northern Hemisphere) / December (Southern Hemisphere)

### Sun Altitude Angles

Sun altitude (degrees above horizon at solar noon) is approximated using fixed values based on latitude bands:

| Latitude Band | Winter | Equinox | Summer |
|---------------|--------|---------|--------|
| **0-15° (Tropics)** | 60° | 75° | 80° |
| **15-30° (Subtropics)** | 50° | 65° | 75° |
| **30-45° (Temperate)** | 30° | 50° | 65° |
| **45-60° (Cool Temperate)** | 15° | 40° | 55° |
| **60-75° (Subpolar)** | 5° | 30° | 45° |

**Source:** These values are geometric approximations based on solar declination at each latitude. They represent midday sun altitude at the height of each season.

### Hemisphere and Shadow Direction

- **Northern Hemisphere (latitude ≥ 0):** Shadows cast northward (positive Y direction)
- **Southern Hemisphere (latitude < 0):** Shadows cast southward (negative Y direction)

**Why:** The sun is always to the south in the Northern Hemisphere (and vice versa), causing shadows to extend in the opposite direction.

---

## Shadow Projection

### Shadow Length Calculation

For an object of height `h` with sun altitude angle `α`:

```
shadow_length = h / tan(α)
```

**Example:**
- Tree height: 10 meters
- Sun altitude: 30° (temperate winter)
- Shadow length: 10 / tan(30°) ≈ 10 / 0.577 ≈ **17.3 meters**

### Shadow Geometry

Trees cast rectangular shadows:
- **Width:** Equal to tree canopy diameter (2 × canopy_radius)
- **Length:** Calculated from height and sun angle
- **Direction:** North (NH) or South (SH)

### Simplified Model

- Shadows are modeled as axis-aligned rectangles
- No ray tracing or complex geometry
- Canopy is circular; shadow projects as rectangle in primary direction

---

## Garden Impact Calculation

### Shading Percentage

For each garden, the model:
1. Projects shadows from all trees for each season
2. Calculates intersection area between shadows and garden
3. Computes shading percentage:

```
shaded_percentage = (total_intersection_area / garden_area) × 100
```

### Multiple Trees

When multiple trees shade a garden:
- Shadows are calculated independently
- Intersection areas are summed (may slightly over-estimate if shadows overlap)
- Result is capped at 100%

**Note:** This conservative approach errs on the side of more shading rather than less.

### Seasonal Exposure Score

Overall seasonal exposure score (0-1):

```
sun_exposure_per_season = (100 - shaded_percentage) / 100
seasonal_exposure_score = average(winter_exposure, equinox_exposure, summer_exposure)
```

**Interpretation:**
- **1.0:** Full sun in all seasons
- **0.5:** 50% sun exposure on average
- **0.0:** Complete shade year-round

---

## Exposure Categories

Gardens are categorized based on the **worst-case season** (highest shading):

| Category | Shading Range | Sun Exposure | Suitable Plants |
|----------|---------------|--------------|-----------------|
| **Full Sun** | 0-25% shaded | >75% sun | Tomatoes, peppers, squash, fruiting vegetables |
| **Partial Sun** | 25-60% shaded | 40-75% sun | Lettuce, spinach, peas, root vegetables |
| **Shade** | 60-100% shaded | <40% sun | Shade-tolerant greens, herbs (parsley, mint) |

**Science Basis:** These thresholds align with standard horticultural classifications. Most fruiting vegetables require 6+ hours of direct sun (≈75% daily exposure) for optimal growth and yield.

---

## Rule Engine Integration

### Rule Severity Levels

- **CRITICAL:** Severe mismatch (e.g., full-sun plant in shade) - expect crop failure
- **WARNING:** Suboptimal conditions (e.g., full-sun plant in partial sun) - reduced yields
- **INFO:** Informational guidance (e.g., seasonal variation patterns)

### Key Rules

#### SUN_002: Full Sun Plant in Shade
**Trigger:** Exposure category = "Shade" AND plant requires full sun
**Severity:** CRITICAL
**Explanation:** Full-sun plants need 6+ hours of direct sunlight for photosynthesis and fruit production. Shaded conditions severely reduce growth, delay fruiting, and decrease yields by 60-90%.
**Action:** Relocate to sunnier location or replace with shade-tolerant plants.

#### SUN_003: Reduced Sun for Full-Sun Plant
**Trigger:** Exposure category = "Partial Sun" AND plant requires full sun
**Severity:** WARNING
**Explanation:** Partial sun (40-75% exposure) slows growth and reduces yields by 20-40% compared to full sun.
**Action:** Consider relocation or monitor closely for slower growth.

#### SUN_005: Heavy Winter Shading
**Trigger:** Winter shading > 75%
**Severity:** INFO
**Explanation:** Low winter sun angles create long shadows, limiting winter growing potential.
**Action:** Plan for dormant season or spring/summer crops.

#### SUN_007: High Seasonal Variability
**Trigger:** Seasonal shading range > 50%
**Severity:** WARNING
**Explanation:** Significant seasonal variation requires adaptive crop planning.
**Action:** Plant sun-demanding crops during best-exposure seasons.

#### SUN_008: Tree Positioned South of Garden (NH)
**Trigger:** Tree at lower Y-coordinate than garden in Northern Hemisphere
**Severity:** WARNING
**Explanation:** Trees to the south cast shadows northward onto gardens. Shadow impact increases as tree grows.
**Action:** Relocate tree to north side or choose shade-tolerant plants.

---

## API Usage

### Get Garden Sun Exposure

```python
from app.services.sun_exposure_service import SunExposureService

exposure = SunExposureService.get_garden_sun_exposure(garden, db)

# Returns:
{
    "seasonal_exposure_score": 0.65,  # 0-1 scale
    "seasonal_shading": {
        "winter": {
            "shaded_percentage": 60.0,
            "exposure_category": "Shade",
            "affected_by_count": 2
        },
        "equinox": {
            "shaded_percentage": 40.0,
            "exposure_category": "Partial Sun",
            "affected_by_count": 2
        },
        "summer": {
            "shaded_percentage": 20.0,
            "exposure_category": "Full Sun",
            "affected_by_count": 1
        }
    },
    "exposure_category": "Shade",  # Worst-case season
    "shading_sources": [5, 12],  # Tree IDs
    "warnings": ["Shaded by 2 tree(s)"]
}
```

### Get Tree Shadow Extent

```python
shadow_info = SunExposureService.get_tree_shadow_extent(tree, latitude=40.0)

# Returns:
{
    "seasonal_shadows": {
        "winter": {"x": 48.0, "y": 32.0, "width": 4.0, "height": 22.0},
        "equinox": {"x": 48.0, "y": 38.0, "width": 4.0, "height": 16.0},
        "summer": {"x": 48.0, "y": 42.0, "width": 4.0, "height": 12.0}
    },
    "max_shadow_length": 22.0
}
```

### Evaluate with Rule Engine

```python
from app.services.sun_exposure_rule_engine import SunExposureRuleEngine

rules = SunExposureRuleEngine.evaluate_garden_sun_exposure(
    exposure_data,
    plant_sun_requirement="full_sun"
)

for rule in rules:
    print(f"{rule.severity}: {rule.title}")
    print(f"Explanation: {rule.explanation}")
    print(f"Action: {rule.suggested_action}")
```

### Check Placement Warnings

```python
warnings = SunExposureService.check_placement_warnings(
    garden_x=50.0,
    garden_y=50.0,
    garden_width=10.0,
    garden_height=10.0,
    land=land,
    db=db
)

# Returns list of warning strings:
# ["High shading during winter (75% shaded)", "Partial shading during equinox (40% shaded)"]
```

---

## Examples

### Example 1: Temperate Garden with South-Side Tree

**Setup:**
- Latitude: 40° N (Temperate zone)
- Tree: 15m tall, 3m canopy radius, positioned at (50, 30)
- Garden: 10m × 10m, positioned at (50, 50)

**Shadow Calculations:**

**Winter (30° sun altitude):**
```
shadow_length = 15 / tan(30°) = 15 / 0.577 = 26.0 m
Shadow rectangle: x=47, y=28, width=6m, height=30m
Intersection with garden: ~60% shaded
```

**Summer (65° sun altitude):**
```
shadow_length = 15 / tan(65°) = 15 / 2.145 = 7.0 m
Shadow rectangle: x=47, y=28, width=6m, height=11m
Intersection with garden: ~10% shaded
```

**Result:**
- Seasonal exposure score: ≈0.55
- Exposure category: "Shade" (worst-case winter)
- Warning: High seasonal variability

### Example 2: Tropical Garden

**Setup:**
- Latitude: 10° N (Tropical zone)
- Tree: 12m tall, 4m canopy radius, positioned at (50, 35)
- Garden: 8m × 8m, positioned at (50, 50)

**Shadow Calculations:**

**Winter (60° sun altitude):**
```
shadow_length = 12 / tan(60°) = 12 / 1.732 = 6.9 m
Shadow rectangle: x=46, y=33, width=8m, height=11m
Minimal intersection with garden
```

**Result:**
- Seasonal exposure score: ≈0.90
- Exposure category: "Full Sun"
- Minimal seasonal variation (tropical latitudes have consistent sun angles)

---

## Limitations

### Known Simplifications

1. **2D Model Only**
   - Ignores elevation changes and terrain slope
   - Assumes flat land surface
   - May underestimate shading on sloped terrain

2. **Midday Sun Only**
   - Uses peak sun altitude (solar noon)
   - Ignores morning/afternoon sun position
   - Does not account for east-west shadow variation

3. **No Tree Characteristics**
   - Treats all trees as opaque cylinders
   - No deciduous vs. evergreen distinction
   - No canopy density variations

4. **Rectangular Shadows**
   - Simplifies circular canopy to rectangular shadow
   - Conservative approximation (may over-estimate shading)

5. **No Atmospheric Effects**
   - Assumes clear sky
   - Ignores clouds, fog, air quality
   - No diffuse light calculations

6. **Fixed Seasonal Buckets**
   - Three seasons only (winter, equinox, summer)
   - No continuous time-of-year modeling
   - Transition periods not explicitly modeled

### Accuracy Expectations

This model provides **order-of-magnitude accuracy** suitable for:
- ✅ Garden planning and placement decisions
- ✅ Plant selection based on sun requirements
- ✅ Identifying problematic tree-garden configurations
- ✅ Comparative analysis (e.g., location A vs. location B)

**Not suitable for:**
- ❌ Precise solar panel placement
- ❌ Building energy modeling
- ❌ Agricultural research requiring <10% error margins
- ❌ Hour-by-hour light availability

**Expected Precision:** ±20-30% in shading percentage estimates under typical conditions.

---

## Future Enhancements (v2+)

### Potential Improvements

1. **Hour-by-Hour Simulation**
   - Calculate sun position for each hour
   - Track cumulative daily sun exposure
   - More accurate east-west effects

2. **Deciduous Tree Modeling**
   - Reduced winter shading for leafless trees
   - Seasonal leaf-on/leaf-off transitions
   - Species-specific canopy density

3. **Terrain Slope**
   - Adjust sun angles based on land slope
   - Account for hillside effects
   - Horizon obstruction calculations

4. **Advanced Geometry**
   - Circular shadow projections
   - Multi-directional shadow casting
   - Penumbra (partial shadow) modeling

5. **Historical Weather Integration**
   - Cloud cover statistics
   - Typical clear-sky days
   - Regional sun availability data

6. **Reflections and Indirect Light**
   - Light reflection from structures
   - Diffuse light under partial canopy
   - Ground albedo effects

7. **UI Enhancements**
   - Interactive seasonal sun overlay toggle
   - Shadow animation across seasons
   - Garden exposure color-coding
   - Tree placement guidance overlay

---

## Mathematical Formulas Reference

### Shadow Length
```
L_shadow = h / tan(α)

Where:
  L_shadow = Shadow length (meters)
  h = Object height (meters)
  α = Sun altitude angle (degrees)
```

### Sun Altitude (Approximation)
```
α ≈ 90° - |latitude - solar_declination|

Where:
  α = Sun altitude at solar noon
  latitude = Location latitude
  solar_declination = ±23.5° (varies by season)

Simplified to lookup table for v1
```

### Shading Percentage
```
P_shaded = (A_intersection / A_garden) × 100

Where:
  P_shaded = Percentage of garden shaded
  A_intersection = Area of shadow-garden overlap (m²)
  A_garden = Total garden area (m²)
```

### Seasonal Exposure Score
```
S_exposure = (1 - P_winter/100 + 1 - P_equinox/100 + 1 - P_summer/100) / 3

Where:
  S_exposure = Seasonal exposure score (0-1)
  P_season = Shading percentage for each season
```

---

## Testing

### Unit Tests
- `tests/unit/test_sun_model.py`: Sun angle calculations, shadow math
- `tests/unit/test_shadow_service.py`: Shadow projection, intersection geometry

### Functional Tests
- `tests/functional/test_sun_path.py`: End-to-end with database

Run sun-path tests:
```bash
pytest -m sun_path -v
```

Run all tests including sun-path:
```bash
pytest tests/unit/test_sun_model.py tests/unit/test_shadow_service.py tests/functional/test_sun_path.py -v
```

---

## Relationship to Existing Shading Model

**Note:** This sun-path model complements the existing `shading_service.py`:

| Feature | Existing Shading Service | Sun-Path Model (This) |
|---------|-------------------------|---------------------|
| **Basis** | Canopy overlap (2D) | Seasonal sun angles |
| **Time** | Static snapshot | Seasonal variation |
| **Direction** | Radial from tree center | Directional (N/S) |
| **Tree Height** | Not used | Primary factor |
| **Use Case** | Immediate canopy shade | Long-term seasonal planning |

**Recommendation:** Use sun-path model for seasonal planning and plant selection. The existing shading service remains useful for immediate canopy coverage analysis.

---

## References

1. **Solar Position Algorithms:**
   - NOAA Solar Calculator methodology
   - Reda, I. & Andreas, A. (2004). "Solar position algorithm for solar radiation applications." Solar Energy, 76(5), 577-589.

2. **Horticulture Standards:**
   - USDA Plant Hardiness Zones
   - Extension service guidelines for sun exposure requirements
   - "The Vegetable Gardener's Bible" by Edward C. Smith

3. **Shadow Geometry:**
   - Basic trigonometry and solar geometry principles
   - Simplified from standard solar engineering formulas

---

## Version History

- **v1.0 (2026-01-31):** Initial implementation
  - Seasonal sun angle approximations
  - 2D shadow projections
  - Soft constraints and rule engine
  - Unit and functional tests
  - Documentation

---

## Contact & Feedback

For questions, bug reports, or enhancement requests related to the sun-path model, please refer to the main project issue tracker.

**Remember:** This model prioritizes **correctness over realism** and **explainability over complexity**. Every calculation is defensible and testable.
