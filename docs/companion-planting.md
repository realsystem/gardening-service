# Companion Planting Recommendations

**Status**: ✅ Implemented
**Version**: 1.0.0
**Last Updated**: 2026-02-01

## Overview

The Companion Planting system provides science-based recommendations for plant-to-plant relationships in gardens. It analyzes spatial arrangements of plants and identifies beneficial pairs, antagonistic conflicts, and suggests improvements based on documented agronomic research.

### Key Features

- **Science-Based**: All relationships backed by peer-reviewed research or agricultural extension publications
- **Deterministic**: Same garden state always produces same recommendations
- **Explainable**: Every recommendation includes mechanism of action and source references
- **Spatial-Aware**: Considers actual distances between plants for active relationships
- **Confidence Levels**: Relationships classified by evidence quality (high, medium, low)

## Data Model

### Companion Relationship Schema

```python
class CompanionRelationship:
    id: int
    plant_a_id: int  # Normalized: always < plant_b_id
    plant_b_id: int
    relationship_type: Enum['beneficial', 'neutral', 'antagonistic']
    mechanism: str  # How the interaction works (scientific explanation)
    confidence_level: Enum['high', 'medium', 'low']
    effective_distance_m: float  # Maximum distance for relationship to apply
    optimal_distance_m: float | None  # Best distance for beneficial relationships
    source_reference: str  # Scientific citation
    notes: str | None  # Additional context
```

### Relationship Types

| Type | Description | Example |
|------|-------------|---------|
| **BENEFICIAL** | Plants that help each other | Tomato + Basil (pest deterrence) |
| **NEUTRAL** | No documented positive or negative effects | Lettuce + Carrot (compatible resources) |
| **ANTAGONISTIC** | Plants that harm each other | Tomato + Broccoli (allelopathy + competition) |

### Confidence Levels

- **HIGH**: Multiple peer-reviewed studies or robust field trials
- **MEDIUM**: Extension service documentation or limited studies
- **LOW**: Anecdotal evidence or theoretical mechanisms

## API Endpoint

### GET /api/gardens/{garden_id}/companions

Analyzes all active planting events in a garden and returns companion planting insights.

**Authentication**: Required (Bearer token)

**Response Structure**:

```json
{
  "garden_id": 123,
  "garden_name": "Vegetable Garden",
  "analysis_time": "2026-02-01T10:30:00Z",
  "planting_count": 5,
  "relationships_analyzed": 10,

  "beneficial_pairs": [
    {
      "plant_a": {
        "planting_id": 1,
        "variety_id": 42,
        "common_name": "Tomato - Cherry",
        "position": {"x": 2.0, "y": 3.0}
      },
      "plant_b": {
        "planting_id": 2,
        "variety_id": 73,
        "common_name": "Basil - Sweet",
        "position": {"x": 2.5, "y": 3.0}
      },
      "distance_m": 0.5,
      "status": "optimal",
      "relationship_type": "beneficial",
      "confidence_level": "high",
      "mechanism": "Basil produces aromatic compounds (linalool, eugenol) that repel aphids, whiteflies, and hornworms.",
      "source_reference": "Journal of Chemical Ecology, 2003",
      "effective_distance_m": 2.0,
      "optimal_distance_m": 0.5
    }
  ],

  "conflicts": [
    {
      "plant_a": {...},
      "plant_b": {...},
      "distance_m": 1.0,
      "status": "conflict",
      "relationship_type": "antagonistic",
      "recommended_separation_m": 3.0,
      "mechanism": "Both are heavy nitrogen feeders. Competition for nutrients results in reduced yield.",
      "problem_description": "Tomato and Broccoli are antagonistic and too close (distance: 1.0m)."
    }
  ],

  "suggestions": [
    {
      "type": "move_closer",
      "plant_a": "Carrot - Nantes",
      "plant_b": "Onion - Yellow",
      "current_distance_m": 3.0,
      "recommended_distance_m": 0.3,
      "reason": "These plants have a beneficial relationship but are too far apart. Onion volatiles mask carrot scent from carrot fly.",
      "confidence": "medium"
    }
  ],

  "summary": {
    "beneficial_count": 1,
    "conflict_count": 1,
    "suggestion_count": 1
  }
}
```

**Status Codes**:
- `200 OK`: Analysis completed successfully
- `401 Unauthorized`: Authentication required
- `404 Not Found`: Garden not found or user doesn't own it

## Scientific Foundations

### Example Relationships

#### Tomato + Basil (BENEFICIAL, HIGH confidence)

- **Mechanism**: Basil produces aromatic compounds (linalool, eugenol) that repel aphids, whiteflies, and hornworms. May improve tomato flavor.
- **Source**: Journal of Chemical Ecology, 2003; Purdue University Extension HO-2
- **Effective Distance**: 2.0m
- **Optimal Distance**: 0.5m
- **Notes**: Plant basil 0.5m from tomato base for best pest deterrence. Multiple studies confirm aphid reduction.

#### Carrot + Onion (BENEFICIAL, MEDIUM confidence)

- **Mechanism**: Onion family volatiles (allyl sulfides) mask carrot scent from carrot fly. Carrot foliage may deter onion fly.
- **Source**: Royal Horticultural Society trials; University of Maine Bulletin 2063
- **Effective Distance**: 1.5m
- **Optimal Distance**: 0.3m
- **Notes**: Interplant rows for best pest confusion effect. Both pests use scent to locate host plants.

#### Tomato + Broccoli (ANTAGONISTIC, MEDIUM confidence)

- **Mechanism**: Tomato root exudates may inhibit brassica growth. Both are heavy nitrogen feeders causing competition.
- **Source**: Research on allelopathic effects of Solanaceae; University of Maryland Extension HG 84
- **Effective Distance**: 3.0m
- **Notes**: Keep separated by at least 3m. Both require high nitrogen - competition is severe.

## Database Population

Initial companion data is loaded via:

```bash
docker-compose exec api python scripts/populate_companion_data.py
```

This script:
- Loads 12+ science-based relationships
- Includes mechanisms, sources, and confidence levels
- Handles plant variety name matching flexibly
- Normalizes plant pairs (plant_a_id < plant_b_id)
- Skips duplicates and missing varieties

## Testing

### Unit Tests

Located in `tests/unit/test_companion_logic.py`:

- Distance calculation tests
- Plant pair normalization tests
- Effective/optimal distance logic tests

Run with:
```bash
pytest tests/unit/test_companion_logic.py -v -m companion_planting
```

### Functional Tests

Located in `tests/functional/test_companion_planting.py`:

- Empty garden analysis
- Single plant handling
- Beneficial pair detection
- Antagonistic conflict detection
- Mixed relationship analysis
- Authentication and authorization
- 404 handling

Run with:
```bash
pytest tests/functional/test_companion_planting.py -v -m companion_planting --no-cov
```

## Implementation Details

### Distance Calculation

Uses Euclidean distance in garden coordinate space:

```python
distance = sqrt((x2 - x1)^2 + (y2 - y1)^2)
```

### Relationship Activation

A relationship is "active" if `distance <= effective_distance_m`.

For beneficial relationships:
- **Optimal**: `distance <= optimal_distance_m` (if defined)
- **Active**: `distance <= effective_distance_m` but > optimal
- **Too Far**: `distance > effective_distance_m` (generates suggestion)

For antagonistic relationships:
- **Conflict**: `distance <= effective_distance_m` (plants are too close)
- **Safe**: `distance > effective_distance_m` (adequate separation)

### Plant Pair Normalization

All relationships are stored with `plant_a_id < plant_b_id` to ensure bidirectionality:

```python
def normalize_plant_pair(plant_a_id, plant_b_id):
    if plant_a_id < plant_b_id:
        return (plant_a_id, plant_b_id)
    return (plant_b_id, plant_a_id)
```

This prevents duplicate entries like (Tomato, Basil) and (Basil, Tomato).

## Architecture

### Database Layer

- **Model**: `app/models/companion_relationship.py`
- **Migration**: `migrations/versions/20260201_2300_n5o6p7q8r9s0_add_companion_relationships.py`
- **Enum Types**: `relationshiptype`, `confidencelevel`

### API Layer

- **Router**: `app/api/companion_analysis.py`
- **Endpoint**: `GET /gardens/{garden_id}/companions`
- **Authentication**: Required via `get_current_user` dependency

### Business Logic

Core analysis functions:
- `calculate_distance()`: Euclidean distance between plants
- `normalize_plant_pair()`: Bidirectional relationship key
- Spatial relationship evaluation
- Suggestion generation

## Future Enhancements

Potential improvements (not currently implemented):

1. **Plant Suggestions**: Recommend complementary plants not currently in garden
2. **Zone Analysis**: Analyze companion relationships by irrigation zone
3. **Seasonal Considerations**: Account for planting dates and growth stages
4. **Crop Rotation**: Extend to multi-season companion planning
5. **Visual Layout Optimizer**: Suggest optimal plant placement
6. **Mobile Notifications**: Alert when new conflicts detected

## References

- Journal of Chemical Ecology (2003): Basil-Tomato interactions
- University of Wisconsin Extension: Beneficial insect attraction
- Royal Horticultural Society: Pest confusion trials
- Oregon State University Extension EM 8840: Polyculture disease reduction
- Penn State Extension: Heavy feeder competition
- University of Maryland Extension HG 84: Allelopathic effects

## Support

For questions or issues:
- API Documentation: `http://localhost:8080/docs` (when running)
- Test Coverage: Run `pytest --cov=app.api.companion_analysis`
- Issues: Report via project issue tracker
