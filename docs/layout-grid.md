# Layout Grid System

This document describes the garden layout grid system, including grid resolution, snapping rules, and user controls.

## Table of Contents

- [Overview](#overview)
- [Grid Resolution](#grid-resolution)
- [Snap-to-Grid Behavior](#snap-to-grid-behavior)
- [User Controls](#user-controls)
- [API](#api)
- [Implementation Details](#implementation-details)
- [Testing](#testing)
- [Examples](#examples)

## Overview

The garden layout system uses a **10× finer grid** for precise garden placement on land plots. Gardens snap to grid intersections for consistent positioning while maintaining flexibility through optional snap-to-grid control.

### Key Features

- **10× finer resolution**: Grid cells are 0.1 units instead of 1 unit
- **Visual grid**: Minor grid lines (0.1 units) and major grid lines (1 unit)
- **Snap-to-grid**: Automatic snapping enabled by default
- **User control**: Toggle snapping on/off, or hold Alt key to temporarily disable
- **Backward compatible**: Existing gardens with unsnapped coordinates remain valid

## Grid Resolution

### Current Grid (10× Finer)

```
1 unit = 10 grid cells
1 grid cell = 0.1 units
```

**Example**: A land plot of 10×10 units has a 100×100 grid (0.1 unit resolution).

### Before/After Comparison

| Aspect | Before (Old) | After (New - 10× Finer) |
|--------|--------------|--------------------------|
| Grid cell size | 0.5 units | 0.1 units |
| Cells per unit | 2 | 10 |
| Precision | ±0.25 units | ±0.05 units |
| Example snap | 1.3 → 1.5 | 1.234 → 1.2 |

### Grid Visualization

```
Major grid lines (1 unit):  ────────────
Minor grid lines (0.1):     ─ ─ ─ ─ ─ ─

Example 3×3 unit area:

0   0.5   1.0   1.5   2.0   2.5   3.0
│   │     │     │     │     │     │
├─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┤
│ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │
├─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┤
  ↑       ↑       ↑       ↑       ↑
  Minor   Major   Minor   Major   Minor
  0.1     1.0     0.1     1.0     0.1
```

## Snap-to-Grid Behavior

### Default Behavior

Gardens **automatically snap to grid** by default when:
- Creating a new garden
- Moving an existing garden
- Resizing a garden

### Snapping Rules

1. **Nearest Grid Point**: Coordinates snap to the nearest 0.1 unit grid intersection
2. **Rounding**: Standard rounding (0.05 rounds up, 0.04 rounds down)
3. **Independence**: X, Y, width, and height snap independently
4. **Idempotent**: Snapping the same value multiple times yields the same result

### Snapping Examples

```javascript
// Position snapping
1.234 → 1.2  // Closer to 1.2 than 1.3
1.267 → 1.3  // Closer to 1.3 than 1.2
0.05  → 0.1  // Exactly halfway rounds up
0.04  → 0.0  // Below halfway rounds down

// Rectangle snapping
{
  x: 1.234,
  y: 2.567,
  width: 3.149,
  height: 4.298
}
↓ (snapped)
{
  x: 1.2,
  y: 2.6,
  width: 3.1,
  height: 4.3
}
```

### When Snap is Applied

Snap-to-grid is applied **before validation**:
1. User provides coordinates (e.g., drag garden to x=1.234)
2. Coordinates snap to grid (x=1.234 → x=1.2)
3. Validation checks bounds and overlaps using snapped coordinates
4. If valid, snapped coordinates are saved

## User Controls

### Frontend Controls

#### Toggle Control

A checkbox in the layout UI allows users to enable/disable snapping:

```
☑ Snap to grid (0.1 unit precision)
  Hold Alt key to temporarily disable snapping while dragging
```

- **Default**: Enabled (checked)
- **Persistent**: Setting persists during the session
- **Visual**: Checkbox with descriptive label

#### Keyboard Shortcut

- **Alt Key**: Hold while dragging to temporarily disable snapping
- **Release**: Snapping re-enables when Alt is released
- **Works with**: All drag operations (move, resize)

### Workflow Examples

#### Precise Placement (Snap Enabled)

1. Enable "Snap to grid" checkbox
2. Drag garden to desired location
3. Garden snaps to nearest grid point (e.g., 1.234 → 1.2)
4. Release mouse - garden placed at snapped coordinates

#### Free Placement (Snap Disabled)

1. Disable "Snap to grid" checkbox, OR
2. Hold Alt key while dragging
3. Drag garden to exact location
4. Garden remains at exact coordinates (e.g., 1.234 stays 1.234)

#### Temporary Override

1. Keep "Snap to grid" enabled
2. Hold Alt key for ONE garden
3. Drag that garden - snapping disabled temporarily
4. Release Alt - snapping re-enables for next operation

## API

### Update Garden Layout Endpoint

```http
PUT /gardens/{garden_id}/layout
```

#### Request Body

```json
{
  "land_id": 1,
  "x": 1.234,
  "y": 2.567,
  "width": 3.149,
  "height": 4.298,
  "snap_to_grid": true  // Optional, defaults to true
}
```

#### Response (Success)

```json
{
  "id": 42,
  "name": "Tomato Garden",
  "land_id": 1,
  "x": 1.2,        // Snapped coordinates
  "y": 2.6,
  "width": 3.1,
  "height": 4.3,
  // ... other garden fields
}
```

#### Snap Behavior

| `snap_to_grid` Value | Behavior |
|---------------------|----------|
| `true` (default) | Coordinates snap to 0.1 grid |
| `false` | Coordinates preserved exactly |
| Not specified | Defaults to `true` (snap enabled) |

### Error Responses

#### Out of Bounds (After Snapping)

```json
{
  "detail": "Garden exceeds land boundaries. Garden: (x=8.1, y=8.1, width=2.1, height=2.1), Land: (width=10, height=10)"
}
```

**Cause**: Garden coordinates after snapping exceed land dimensions.

#### Overlap (After Snapping)

```json
{
  "detail": "Garden overlaps with 1 existing garden(s). Conflicting garden IDs: [5]"
}
```

**Cause**: Snapped garden overlaps with another garden on the same land.

## Implementation Details

### Data Storage

- **Positions stored in real-world units** (meters, feet, or abstract units)
- **Grid is for visualization and placement only** - not stored in database
- **No migration required** - existing gardens work without changes

### Backend (Python)

**Configuration**: `app/utils/grid_config.py`

```python
GRID_RESOLUTION = 0.1  # 0.1 units per grid cell
GRID_CELLS_PER_UNIT = 10  # 10 cells per unit

def snap_to_grid(value: float, grid_resolution: float = GRID_RESOLUTION) -> float:
    """Snap coordinate to nearest grid intersection"""
    return round(value / grid_resolution) * grid_resolution
```

**Layout Service**: `app/services/layout_service.py`

```python
def apply_snap_to_grid(
    x: float,
    y: float,
    width: float,
    height: float,
    snap_enabled: bool = True
) -> Tuple[float, float, float, float]:
    """Apply snap-to-grid if enabled"""
    if snap_enabled:
        return snap_rectangle_to_grid(x, y, width, height)
    return x, y, width, height
```

### Frontend (TypeScript/React)

**Configuration**: `LandCanvas.tsx`

```typescript
const GRID_SIZE = 50;        // 50px per unit (visualization)
const GRID_RESOLUTION = 0.1; // 0.1 units per grid cell
const GRID_CELLS_PER_UNIT = 10;

const snapToGrid = (value: number, resolution: number): number => {
  return Math.round(value / resolution) * resolution;
};
```

**Grid Rendering**: SVG patterns for minor and major grid lines

```tsx
{/* Minor grid (0.1 unit cells) - subtle */}
<pattern id="minor-grid" width={5} height={5}>
  <path stroke="#f0f0f0" strokeWidth="0.5" />
</pattern>

{/* Major grid (1 unit cells) - more visible */}
<pattern id="major-grid" width={50} height={50}>
  <path stroke="#d0d0d0" strokeWidth="1" />
</pattern>
```

### Performance Considerations

- **No database changes**: Grid is purely UI/validation logic
- **Minimal rendering cost**: SVG patterns reuse, no DOM explosion
- **Snapping on client**: Immediate visual feedback before API call
- **Server validation**: Backend verifies snapped coordinates

## Testing

### Running Grid Tests

```bash
# Run all layout grid tests
pytest -m layout_grid -v

# Run specific test file
pytest tests/functional/test_layout_grid.py -v

# Run unit tests for grid utilities
pytest tests/unit/test_grid_config.py -v
pytest tests/unit/test_layout_snap.py -v
```

### Test Coverage

#### Unit Tests

**Grid Configuration** (`test_grid_config.py`):
- ✓ Grid resolution constants (0.1 units)
- ✓ Snap-to-grid math (rounding, precision)
- ✓ Rectangle snapping (all coordinates)
- ✓ Grid alignment validation
- ✓ Edge cases (zero, negative, large values)

**Layout Snapping** (`test_layout_snap.py`):
- ✓ Snap enabled/disabled behavior
- ✓ Boundary checks with snapped coordinates
- ✓ Overlap detection with snapped gardens
- ✓ Idempotent snapping

#### Functional Tests

**Grid Snapping** (`test_layout_grid.py`, marked with `@pytest.mark.layout_grid`):
- ✓ Garden placement with snap enabled
- ✓ Garden placement with snap disabled
- ✓ Snap defaults to enabled
- ✓ Boundary enforcement with snapping
- ✓ Overlap prevention with snapping
- ✓ Backward compatibility (existing unsnapped gardens)

### Test Markers

Use `@pytest.mark.layout_grid` to filter layout grid tests:

```bash
pytest -m layout_grid  # Run only grid tests
pytest -m "not layout_grid"  # Exclude grid tests
```

## Examples

### Example 1: Precise Garden Placement

**Scenario**: Place a 2×2 garden at exact grid intersection

```javascript
// User drags garden to approximately (3.2, 4.5)
// With snap enabled:
api.updateGardenLayout(gardenId, {
  land_id: 1,
  x: 3.234,      // User's exact drag position
  y: 4.467,
  width: 2.0,
  height: 2.0,
  snap_to_grid: true
});

// Response: Garden snapped to (3.2, 4.5)
{
  "x": 3.2,
  "y": 4.5,
  "width": 2.0,
  "height": 2.0
}
```

### Example 2: Free-Form Placement

**Scenario**: Place garden at exact coordinates for custom layout

```javascript
// User holds Alt key, drags garden
api.updateGardenLayout(gardenId, {
  land_id: 1,
  x: 3.234,      // Exact position
  y: 4.467,
  width: 2.0,
  height: 2.0,
  snap_to_grid: false  // Snap disabled
});

// Response: Exact coordinates preserved
{
  "x": 3.234,
  "y": 4.467,
  "width": 2.0,
  "height": 2.0
}
```

### Example 3: Adjacent Garden Placement

**Scenario**: Place two gardens side-by-side using grid alignment

```javascript
// Garden 1 at (0, 0) with size (2, 2)
api.updateGardenLayout(garden1Id, {
  land_id: 1,
  x: 0.0,
  y: 0.0,
  width: 2.0,
  height: 2.0,
  snap_to_grid: true
});

// Garden 2 adjacent (touching but not overlapping)
api.updateGardenLayout(garden2Id, {
  land_id: 1,
  x: 2.0,  // Starts exactly where garden1 ends
  y: 0.0,
  width: 2.0,
  height: 2.0,
  snap_to_grid: true
});

// Success! Gardens touch at x=2.0 but don't overlap
```

### Example 4: Migrating Existing Garden to Grid

**Scenario**: Update old garden to use new grid system

```javascript
// Existing garden at (1.234567, 2.345678) - created before grid feature
// User decides to align it to grid

api.updateGardenLayout(gardenId, {
  land_id: 1,
  x: 1.234567,   // Will snap to 1.2
  y: 2.345678,   // Will snap to 2.3
  width: 3.456789,  // Will snap to 3.5
  height: 4.567890, // Will snap to 4.6
  snap_to_grid: true  // Enable snapping
});

// Response: Garden now aligned to grid
{
  "x": 1.2,
  "y": 2.3,
  "width": 3.5,
  "height": 4.6
}
```

## Best Practices

1. **Use snap for most gardens**: Easier to align and manage
2. **Disable snap for custom layouts**: Use when precise positioning is required
3. **Test placement first**: Verify gardens fit within bounds before final placement
4. **Keep major grid visible**: Helps with spatial planning
5. **Use Alt key for quick override**: Faster than toggling checkbox

## Troubleshooting

### Garden Exceeds Bounds After Snapping

**Problem**: Garden placed successfully without snap, fails with snap enabled

**Cause**: Snapping rounds coordinates up, pushing garden outside land boundaries

**Solution**: Adjust initial coordinates or disable snapping for that garden

### Garden Overlaps After Snapping

**Problem**: Gardens that don't overlap without snap, overlap with snap

**Cause**: Snapping changes dimensions/positions slightly

**Solution**: Leave more space between gardens, or use snap consistently for all gardens on a land

### Existing Gardens Look Misaligned

**Problem**: Old gardens (before grid feature) don't align to grid

**Cause**: Created with exact coordinates before snap-to-grid was implemented

**Solution**: Optional - update gardens one by one with snap enabled to align them

## Future Enhancements

Potential future improvements:

- Variable grid resolution (configurable per land)
- Snap to custom increments (e.g., 0.05 units)
- Grid display toggle (show/hide grid lines)
- Magnetic snapping (visual feedback as garden approaches grid)
- Batch snap operation (snap all gardens on a land at once)

## Questions?

For questions about the layout grid system:
- Review this documentation
- Check test suite for examples (`tests/functional/test_layout_grid.py`)
- Verify grid configuration (`app/utils/grid_config.py`)
