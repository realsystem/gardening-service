# Garden Convenience Features

This document describes the garden management convenience features added to the gardening service.

## Overview

Three new convenience features have been added to make garden management easier:

1. **List Garden Plantings** - View all plants in a specific garden
2. **Delete Gardens** - Remove gardens with cascade deletion
3. **Open Garden / View Details** - See comprehensive garden information with statistics

## Backend API Endpoints

### 1. List Plantings for a Garden

**Endpoint:** `GET /gardens/{garden_id}/plantings`

**Description:** Returns all planting events for a specific garden, including plant names, expected harvest dates, and status.

**Response:**
```json
[
  {
    "id": 1,
    "plant_variety_id": 1,
    "plant_name": "Tomato",
    "variety_name": "Beefsteak",
    "planting_date": "2026-01-20",
    "planting_method": "direct_sow",
    "plant_count": 6,
    "location_in_garden": "Bed 1, Row 2",
    "health_status": "healthy",
    "expected_harvest_date": "2026-04-10",
    "days_to_harvest": 80,
    "status": "growing"
  }
]
```

**Status Values:**
- `pending` - Planting date is in the future
- `growing` - Currently growing
- `ready_to_harvest` - Expected harvest date has arrived
- `harvested` - Completed (future enhancement)

**Authorization:** Requires JWT token. Users can only access their own gardens.

**Example:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8080/gardens/1/plantings
```

### 2. Delete a Garden

**Endpoint:** `DELETE /gardens/{garden_id}`

**Description:** Deletes a garden and all associated data. This is a destructive operation that:
- Deletes the garden
- Deletes all planting events in the garden (cascade)
- Deletes all tasks associated with those plantings (cascade)

**Response:** 204 No Content

**Authorization:** Requires JWT token. Users can only delete their own gardens.

**Example:**
```bash
curl -X DELETE \
  -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8080/gardens/1
```

**⚠️ Warning:** This operation cannot be undone. All plantings and tasks will be permanently deleted.

### 3. Get Garden Details

**Endpoint:** `GET /gardens/{garden_id}`

**Description:** Returns comprehensive information about a garden, including:
- Garden metadata
- All plantings in the garden
- All tasks related to the garden
- Statistics summary

**Response:**
```json
{
  "garden": {
    "id": 1,
    "name": "Main Garden",
    "description": "Outdoor vegetable garden",
    "garden_type": "outdoor",
    "is_hydroponic": false,
    ...
  },
  "plantings": [
    {
      "id": 1,
      "plant_name": "Tomato",
      "variety_name": "Beefsteak",
      "planting_date": "2026-01-20",
      "status": "growing",
      ...
    }
  ],
  "tasks": [
    {
      "id": 1,
      "title": "Water tomatoes",
      "task_type": "water",
      "priority": "medium",
      "due_date": "2026-01-29",
      "status": "pending",
      ...
    }
  ],
  "stats": {
    "total_plantings": 5,
    "active_plantings": 4,
    "total_tasks": 10,
    "pending_tasks": 7,
    "high_priority_tasks": 2,
    "upcoming_harvests": 1
  }
}
```

**Authorization:** Requires JWT token. Users can only access their own gardens.

**Example:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8080/gardens/1
```

## Frontend Components

### GardenList Component

**Location:** `frontend/src/components/GardenList.tsx`

**Purpose:** Displays all gardens for the logged-in user with management options.

**Features:**
- Grid layout showing all gardens
- Visual indicators for garden type (outdoor 🌱, indoor 🏠, hydroponic 💧)
- Delete button with confirmation modal
- View details button
- Empty state when no gardens exist

**Props:**
```typescript
interface GardenListProps {
  onSelectGarden: (gardenId: number) => void;
  onRefresh?: () => void;
}
```

**Usage:**
```tsx
<GardenList
  onSelectGarden={(id) => setSelectedGardenId(id)}
  onRefresh={() => loadGardens()}
/>
```

### GardenDetails Component

**Location:** `frontend/src/components/GardenDetails.tsx`

**Purpose:** Displays comprehensive information about a specific garden.

**Features:**
- Garden metadata display
- Statistics cards (total plantings, active plants, pending tasks, etc.)
- List of all plantings with status indicators
- List of all tasks with priority badges
- Hydroponic-specific information display
- Back button to return to garden list

**Props:**
```typescript
interface GardenDetailsProps {
  gardenId: number;
  onBack: () => void;
}
```

**Usage:**
```tsx
<GardenDetails
  gardenId={selectedGardenId}
  onBack={() => setSelectedGardenId(null)}
/>
```

## Integration Example

Complete workflow for managing gardens in your application:

```typescript
function GardenManagement() {
  const [selectedGardenId, setSelectedGardenId] = useState<number | null>(null);

  if (selectedGardenId) {
    return (
      <GardenDetails
        gardenId={selectedGardenId}
        onBack={() => setSelectedGardenId(null)}
      />
    );
  }

  return (
    <GardenList
      onSelectGarden={(id) => setSelectedGardenId(id)}
      onRefresh={() => window.location.reload()}
    />
  );
}
```

## Testing

### Backend Tests

**File:** `tests/test_garden_features.py`

**Coverage:**
- List plantings endpoint
- Delete garden endpoint with cascade behavior
- Garden details endpoint with stats
- Authorization checks
- Edge cases (empty gardens, non-existent gardens)
- Integration workflows

**Run tests:**
```bash
pytest tests/test_garden_features.py -v
```

### Frontend Tests

**Files:**
- `frontend/src/components/GardenList.test.tsx`
- `frontend/src/components/GardenDetails.test.tsx`

**Coverage:**
- Component rendering
- User interactions (view, delete, cancel)
- Delete confirmation modal
- Empty states
- Error handling
- API integration

**Run tests:**
```bash
cd frontend
npm test GardenList.test.tsx
npm test GardenDetails.test.tsx
```

## Database Schema

These features leverage existing database cascade relationships:

```sql
-- Gardens table (existing)
CREATE TABLE gardens (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id),
  name VARCHAR(100) NOT NULL,
  ...
);

-- Planting events with cascade delete
CREATE TABLE planting_events (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id),
  garden_id INTEGER REFERENCES gardens(id) ON DELETE CASCADE,
  ...
);

-- Care tasks with cascade delete
CREATE TABLE care_tasks (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id),
  planting_event_id INTEGER REFERENCES planting_events(id) ON DELETE CASCADE,
  ...
);
```

When a garden is deleted:
1. All planting_events for that garden are deleted (ON DELETE CASCADE)
2. All care_tasks for those plantings are deleted (ON DELETE CASCADE)
3. No orphaned data remains

## API Examples

### Complete Garden Workflow

**1. List all gardens:**
```bash
GET /gardens
```

**2. View specific garden details:**
```bash
GET /gardens/1
```

**3. List plantings in garden:**
```bash
GET /gardens/1/plantings
```

**4. Delete garden:**
```bash
DELETE /gardens/1
```

## Compatibility

These features are fully compatible with:
- ✅ MVP workflows (outdoor gardening)
- ✅ Indoor gardening features
- ✅ Hydroponics support
- ✅ User profiles and authentication
- ✅ Task generation rules
- ✅ Sensor readings
- ✅ All existing frontend components

No existing workflows were modified or broken.

## Security

**Authorization:**
- All endpoints require JWT authentication
- Users can only access/modify/delete their own gardens
- Cross-user access is prevented (403 Forbidden)

**Validation:**
- Garden IDs are validated before operations
- Non-existent gardens return 404
- Cascade deletes are database-enforced

## Performance

**Optimizations:**
- Single query for garden details includes plantings and tasks
- Stats are calculated in-memory from fetched data
- No N+1 query problems

**Considerations:**
- For gardens with 100+ plantings, consider pagination (future enhancement)
- Stats calculation is currently synchronous (acceptable for typical use)

## Future Enhancements

Potential improvements for these features:

1. **Pagination** - For gardens with many plantings
2. **Filtering** - Filter plantings by status, plant type, date range
3. **Sorting** - Sort plantings by different criteria
4. **Export** - Export garden data to CSV/PDF
5. **Archive** - Soft-delete gardens instead of hard delete
6. **Bulk Operations** - Delete multiple gardens at once
7. **Search** - Search plants within a garden

## Summary

These convenience features make garden management significantly easier:

- **List Plantings** - Quickly see all plants in a garden with harvest info
- **Delete Gardens** - Clean up old gardens safely with cascade deletion
- **View Details** - Get comprehensive overview with statistics

All features are fully tested, documented, and integrated with existing functionality.
