# Soil Sample Edit & Delete Features

Full documentation for editing and deleting soil samples in the Gardening Service platform.

## Overview

Users can now edit and delete their soil samples with proper authorization, validation, and immediate rule engine reactivity.

---

## Backend API

### Update Soil Sample

**Endpoint:** `PUT /soil-samples/{sample_id}`

**Authorization:** Required (user must own the sample)

**Request Body:** (all fields optional for partial updates)
```json
{
  "ph": 6.5,
  "nitrogen_ppm": 30.0,
  "phosphorus_ppm": 25.0,
  "potassium_ppm": 150.0,
  "organic_matter_percent": 3.5,
  "moisture_percent": 50.0,
  "date_collected": "2026-01-30",
  "notes": "Updated observations"
}
```

**Response:** `200 OK`
```json
{
  "id": 5,
  "user_id": 1,
  "garden_id": 7,
  "ph": 6.5,
  "nitrogen_ppm": 30.0,
  "phosphorus_ppm": 25.0,
  "potassium_ppm": 150.0,
  "organic_matter_percent": 3.5,
  "moisture_percent": 50.0,
  "date_collected": "2026-01-30",
  "notes": "Updated observations",
  "garden_name": "Test Garden",
  "recommendations": [...]
}
```

**Validation:**
- `ph`: 0-14
- `nitrogen_ppm`, `phosphorus_ppm`, `potassium_ppm`: >= 0
- `organic_matter_percent`, `moisture_percent`: 0-100
- All fields optional (partial update supported)

**Error Responses:**
- `404`: Sample not found or unauthorized
- `422`: Validation error (values out of range)

---

### Delete Soil Sample

**Endpoint:** `DELETE /soil-samples/{sample_id}`

**Authorization:** Required (user must own the sample)

**Response:** `200 OK`
```json
{
  "message": "Soil sample deleted successfully",
  "deleted_sample": {
    "id": 5,
    "garden_id": 7,
    "date_collected": "2026-01-30"
  }
}
```

**Error Responses:**
- `404`: Sample not found or unauthorized

**Important Notes:**
- Deletion is **permanent** and cannot be undone
- Historical rule evaluations are not affected
- If a garden is deleted, all associated samples are cascade-deleted

---

## Frontend Components

### EditSoilSample Component

**Location:** `frontend/src/components/EditSoilSample.tsx`

**Usage:**
```tsx
import { EditSoilSample } from './EditSoilSample';

<EditSoilSample
  sample={sampleToEdit}
  onClose={() => setEditingSample(null)}
  onSuccess={() => {
    loadSamples();
    setEditingSample(null);
  }}
/>
```

**Features:**
- Pre-fills form with existing sample values
- Validates all inputs client-side
- Shows loading state during update
- Displays error messages
- Supports partial updates (only changed fields sent)

---

### SoilSampleList Component

**Location:** `frontend/src/components/SoilSampleList.tsx`

**Updates:**
- Added **Edit** button next to each sample
- Updated **Delete** button with confirmation modal
- Delete confirmation prevents accidental deletions
- Edit modal opens when Edit button is clicked
- Refreshes list after successful edit/delete

**UI Flow:**

1. **Edit:**
   - Click "Edit" → Modal opens with pre-filled form
   - Modify values → Click "Update Soil Sample"
   - Success → List refreshes, modal closes

2. **Delete:**
   - Click "Delete" → Confirmation modal appears
   - Click "Delete" in modal → Sample deleted
   - Click "Cancel" → No action, modal closes

---

## Rule Engine Integration

### How Edits Affect Rule Insights

**Immediate Reactivity:**
- Rule engine queries database for latest samples
- Editing a sample updates `Scientific Insights` immediately
- No caching - every rule evaluation reads fresh data

**Example Scenario:**
```
1. Sample created: pH 4.5, moisture 8% → CRITICAL alerts
2. Sample edited:  pH 6.5, moisture 50% → Alerts cleared
3. Rule engine:    Automatically shows "All Systems Optimal"
```

**Same-Date Samples:**
- When multiple samples exist for same date, highest ID (most recent insert) is used
- To ensure your edit is used, update the `date_collected` to today or later

---

### How Deletions Affect Rule Insights

**After Deletion:**
- Sample is permanently removed from database
- Rule engine falls back to next-most-recent sample (if any)
- If no samples remain, default context is used (no soil data)

**Example:**
```
Garden has 3 samples:
- 2026-01-28: pH 6.0 ✓
- 2026-01-29: pH 4.5 ✗ (triggers alert)
- 2026-01-30: pH 6.5 ✓

Delete 2026-01-30 → Rule engine now uses 2026-01-29 → Alert appears
```

---

## Authorization

**Security Rules:**
1. Users can only edit/delete their own samples
2. Cross-user access returns `404` (not `403` to avoid leaking sample existence)
3. Garden ownership is verified indirectly (samples belong to user)

**Implementation:**
```python
# Backend checks
sample = db.query(SoilSample).filter(
    SoilSample.id == sample_id,
    SoilSample.user_id == current_user.id  # Critical check
).first()

if not sample:
    raise HTTPException(status_code=404, detail="Soil sample not found")
```

---

## Testing

### Run Backend Tests

```bash
cd /Users/segorov/Projects/t/gardening-service

# Run all edit/delete tests
docker-compose exec api pytest tests/test_soil_sample_edit_delete.py -v

# Run specific test class
docker-compose exec api pytest tests/test_soil_sample_edit_delete.py::TestUpdateSoilSample -v

# Run with coverage
docker-compose exec api pytest tests/test_soil_sample_edit_delete.py --cov=app.api.soil_samples
```

### Test Coverage

**Test Categories:**
1. **Update Tests (9 tests)**
   - ✓ Successful update
   - ✓ Unauthorized access
   - ✓ Sample not found
   - ✓ Invalid pH validation
   - ✓ Invalid percentage validation
   - ✓ Partial updates
   - ✓ Recommendation regeneration

2. **Delete Tests (4 tests)**
   - ✓ Successful deletion
   - ✓ Unauthorized access
   - ✓ Sample not found
   - ✓ Cascade deletion

3. **Rule Engine Integration (2 tests)**
   - ✓ Rule engine uses latest sample after edit
   - ✓ Rule engine handles deleted samples

**Total: 15 comprehensive tests**

---

## Data Integrity

### Validation Rules

All numeric fields are validated against scientific ranges:

| Field | Min | Max | Unit |
|-------|-----|-----|------|
| pH | 0 | 14 | pH scale |
| Nitrogen | 0 | ∞ | ppm |
| Phosphorus | 0 | ∞ | ppm |
| Potassium | 0 | ∞ | ppm |
| Organic Matter | 0 | 100 | % |
| Moisture | 0 | 100 | % |

### Historical Integrity

- **Edits:** Update the sample in place, preserving history only if needed by application logic
- **Deletes:** Permanent removal, no soft deletes
- **Recommendations:** Regenerated on every read/update (not cached)

---

## Edge Cases Handled

1. **Same-day multiple samples:**
   - Resolved by ID (higher ID = newer)
   - Solution: Order by `date_collected DESC, id DESC`

2. **Missing moisture in edited sample:**
   - Partial updates allowed
   - Null/None values are preserved if not provided

3. **Delete last sample in garden:**
   - No errors thrown
   - Rule engine gracefully handles empty soil context

4. **Edit without changing values:**
   - Update succeeds (idempotent)
   - Recommendations still regenerated

---

## API Examples

### Edit Sample (cURL)

```bash
TOKEN="your_access_token"
SAMPLE_ID=5

curl -X PUT http://localhost:8080/soil-samples/$SAMPLE_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ph": 6.5,
    "moisture_percent": 50.0,
    "notes": "Fixed dry soil issue"
  }'
```

### Delete Sample (cURL)

```bash
TOKEN="your_access_token"
SAMPLE_ID=5

curl -X DELETE http://localhost:8080/soil-samples/$SAMPLE_ID \
  -H "Authorization: Bearer $TOKEN"
```

### Check Rule Insights After Edit

```bash
GARDEN_ID=7

curl -X GET http://localhost:8080/rule-insights/garden/$GARDEN_ID \
  -H "Authorization: Bearer $TOKEN" | jq
```

---

## Troubleshooting

### Problem: Edited sample not reflected in Scientific Insights

**Solution:**
1. Ensure the edited sample has the **latest date** in the garden
2. Refresh the dashboard (F5)
3. Check browser console for API errors

### Problem: Delete button doesn't work

**Solution:**
1. Check browser console for errors
2. Ensure you have network connectivity
3. Verify you're logged in (token not expired)

### Problem: Getting 404 when editing sample

**Possible Causes:**
- Sample belongs to different user (authorization failure)
- Sample was already deleted
- Sample ID is incorrect

---

## Future Enhancements

Potential improvements (not implemented yet):

1. **Audit Trail:** Track who edited what and when
2. **Soft Deletes:** Mark as deleted instead of removing
3. **Batch Operations:** Edit/delete multiple samples at once
4. **Undo:** Restore recently deleted samples
5. **Version History:** Keep edit history for samples

---

## Summary

**What's New:**
- ✅ PUT /soil-samples/{id} endpoint
- ✅ DELETE /soil-samples/{id} endpoint (improved)
- ✅ EditSoilSample modal component
- ✅ Delete confirmation modal
- ✅ Edit/Delete buttons in SoilSampleList
- ✅ 15 comprehensive backend tests
- ✅ Full authorization and validation
- ✅ Immediate rule engine reactivity

**Quality Assurance:**
- Authorization: ✓ Users can only edit/delete their own samples
- Validation: ✓ All values scientifically validated
- Safety: ✓ Delete confirmation prevents accidents
- Testing: ✓ 15 tests covering all scenarios
- Documentation: ✓ Complete API and UI docs

**The feature is production-ready!**
