# Data Export & Import

This document describes the data export and import functionality for the Gardening Service platform.

## Overview

The export/import feature provides data portability, allowing users to:
- **Backup** their gardening data
- **Transfer** data between accounts
- **Migrate** data to different environments
- **Archive** historical gardening records

All export/import operations use a portable JSON format with schema versioning for backward compatibility.

## Export Format

### Schema Version

Current schema version: **1.0.0**

The schema version follows semantic versioning (MAJOR.MINOR.PATCH):
- MAJOR version changes indicate incompatible format changes
- MINOR version changes indicate backward-compatible additions
- PATCH version changes indicate backward-compatible fixes

### Export Structure

```json
{
  "metadata": {
    "schema_version": "1.0.0",
    "app_version": "0.1.0",
    "export_timestamp": "2026-01-31T12:00:00Z",
    "user_id": 123,
    "include_sensor_readings": false
  },
  "user_profile": {
    "display_name": "John Gardener",
    "city": "Portland",
    "zip_code": "97201",
    "usda_zone": "8b",
    "gardening_preferences": "Organic, native plants"
  },
  "lands": [...],
  "gardens": [...],
  "trees": [...],
  "plantings": [...],
  "soil_samples": [...],
  "irrigation_sources": [...],
  "irrigation_zones": [...],
  "watering_events": [...],
  "sensor_readings": [...]
}
```

### Included Data

The export includes:
- **User Profile**: Display name, city, ZIP code, USDA zone, gardening preferences
- **Lands**: Property layouts with dimensions
- **Gardens**: All garden configurations including indoor/outdoor settings, hydroponic systems
- **Trees**: Tree positions and canopy data for shading calculations
- **Plantings**: Planting events with varieties, dates, and health status
- **Soil Samples**: Soil test results (pH, NPK, organic matter, moisture)
- **Irrigation Sources**: Water sources and flow capacities
- **Irrigation Zones**: Irrigation zones with delivery types and schedules
- **Watering Events**: Historical watering records
- **Sensor Readings**: (Optional) Time-series sensor data

### Excluded Data

For security reasons, the following are **never** exported:
- Email addresses
- Passwords (hashed or plain)
- Authentication tokens
- API keys
- Session data

## Using the Export Feature

### Via UI (Recommended)

1. Navigate to **Profile Settings** → **Data** tab
2. (Optional) Check "Include sensor readings" if you want historical sensor data
3. Click **Download Export File**
4. Save the JSON file to a secure location

**Note**: Files with sensor readings can be large (several MB). Export without sensor readings for faster transfers.

### Via API

**Endpoint**: `GET /export-import/export`

**Query Parameters**:
- `include_sensor_readings` (boolean, optional): Include sensor readings in export

**Authentication**: Required (Bearer token)

**Example**:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8080/export-import/export > export.json
```

**With sensor readings**:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8080/export-import/export?include_sensor_readings=true" > export-full.json
```

## Using the Import Feature

### Import Modes

Three import modes are available:

#### 1. Dry Run (Recommended First)
- **Purpose**: Validate import file without making changes
- **Use when**: Testing import files, checking for errors
- **Result**: Validation report with no database changes

#### 2. Merge
- **Purpose**: Add imported data to existing data
- **Use when**: Combining data from multiple sources, restoring specific items
- **Result**: New items created with new IDs, relationships preserved
- **Safety**: Existing data is preserved

#### 3. Overwrite ⚠️
- **Purpose**: Delete all existing data and replace with imported data
- **Use when**: Full account restoration, complete data replacement
- **Result**: ALL existing data deleted, then import data inserted
- **Safety**: DESTRUCTIVE - Cannot be undone!

### Via UI (Recommended)

1. Navigate to **Profile Settings** → **Data** tab
2. Click **Select Export File** and choose your JSON file
3. Select an **Import Mode**:
   - Start with **Dry Run** to validate
   - Use **Merge** to add data
   - Use **Overwrite** only if you want to replace everything
4. Review the **Validation Results**:
   - Check schema compatibility
   - Review item counts
   - Read any warnings or errors
5. Click the import button to proceed

**Best Practice**: Always run a dry-run validation before performing actual imports.

### Via API

**Preview Import** (Validation only):
```bash
POST /export-import/import/preview
```

**Perform Import**:
```bash
POST /export-import/import
```

**Request Body**:
```json
{
  "mode": "dry_run",  // or "merge" or "overwrite"
  "data": {
    // ... export data object
  }
}
```

**Example using curl**:
```bash
# Validate import
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d @export.json \
  http://localhost:8080/export-import/import/preview

# Perform merge import
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"mode":"merge","data":'$(cat export.json)'}' \
  http://localhost:8080/export-import/import
```

## Import Validation

The import system performs comprehensive validation:

### Schema Compatibility
- Checks that major version matches (e.g., 1.x.x is compatible with 1.y.z)
- Warns about minor version differences
- Rejects incompatible major versions

### Relationship Integrity
- Validates foreign key references (e.g., gardens reference existing lands)
- Ensures parent entities exist before children
- Checks for circular dependencies

### Data Type Validation
- Validates required fields are present
- Checks data types match expected types
- Validates enum values are valid

### Validation Results

The preview/validation returns:
```json
{
  "valid": true,
  "schema_version_compatible": true,
  "issues": [],
  "warnings": [],
  "counts": {
    "lands": 2,
    "gardens": 5,
    "plantings": 12
  },
  "would_overwrite": 15  // In overwrite mode
}
```

**Issue Severity Levels**:
- **Error**: Prevents import from proceeding
- **Warning**: Import can proceed but review recommended
- **Info**: Informational message only

## ID Remapping

During import (merge and overwrite modes), the system:

1. **Assigns new IDs** to all imported entities
2. **Preserves relationships** by remapping foreign keys
3. **Returns ID mapping** showing old ID → new ID conversions

This ensures no ID conflicts and maintains data integrity.

**Example ID Mapping**:
```json
{
  "lands": {
    "100": 45,    // Land with old ID 100 now has ID 45
    "101": 46
  },
  "gardens": {
    "200": 89,    // Garden with old ID 200 now has ID 89
    "201": 90
  }
}
```

## Security & Privacy

### Data Ownership
- Imported data is **always** assigned to the authenticated user
- Original user IDs are preserved in metadata for reference only
- Sensitive data (email, password) is never exported or imported

### Authentication
- All export/import operations require authentication
- Bearer token must be valid and not expired
- Users can only export/import their own data

### Safe Practices
1. **Store export files securely** - They contain your gardening data
2. **Never share export files** containing private garden layouts
3. **Validate before importing** - Use dry-run mode first
4. **Backup before overwrite** - Export current data before using overwrite mode
5. **Keep exports up-to-date** - Regular exports serve as backups

## Error Handling

### Common Errors

**Invalid JSON Format**:
```
Error: Invalid JSON file. Please select a valid export file.
```
**Solution**: Ensure file is valid JSON and not corrupted.

**Incompatible Schema Version**:
```
Error: Schema version 2.0.0 is not compatible with current version 1.0.0
```
**Solution**: Update application or convert export to compatible version.

**Missing Referenced Entity**:
```
Error: Garden references land_id 999 which doesn't exist in import data
```
**Solution**: Ensure export file includes all related entities.

**Permission Denied**:
```
Error: Authentication required
```
**Solution**: Log in and ensure Bearer token is valid.

### Transaction Safety

All imports use database transactions:
- **Success**: All data committed atomically
- **Failure**: Complete rollback, no partial imports
- **Result**: Database is never left in inconsistent state

## Examples

### Example 1: Backup Current Data

```bash
# Export all data including sensors
curl -H "Authorization: Bearer TOKEN" \
  "http://localhost:8080/export-import/export?include_sensor_readings=true" \
  > backup-$(date +%Y%m%d).json
```

### Example 2: Migrate to New Account

1. Export from old account:
   ```bash
   # Using old account token
   curl -H "Authorization: Bearer OLD_TOKEN" \
     http://localhost:8080/export-import/export > migration.json
   ```

2. Validate on new account:
   ```bash
   # Using new account token
   curl -X POST \
     -H "Authorization: Bearer NEW_TOKEN" \
     -H "Content-Type: application/json" \
     --data @migration.json \
     http://localhost:8080/export-import/import/preview
   ```

3. Import to new account:
   ```bash
   curl -X POST \
     -H "Authorization: Bearer NEW_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"mode":"merge","data":'$(cat migration.json)'}' \
     http://localhost:8080/export-import/import
   ```

### Example 3: Restore from Backup

```bash
# First, validate the backup
curl -X POST \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  --data @backup-20260131.json \
  http://localhost:8080/export-import/import/preview

# If validation passes, restore (overwrite mode)
curl -X POST \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"mode":"overwrite","data":'$(cat backup-20260131.json)'}' \
  http://localhost:8080/export-import/import
```

## Troubleshooting

### Large File Handling

If export files are very large (>10MB):
- Exclude sensor readings: `include_sensor_readings=false`
- Use compression: `gzip export.json` → `export.json.gz`
- Split data: Export subsets if needed

### Performance

- **Export**: Typically completes in 1-5 seconds for normal datasets
- **Import validation**: 1-3 seconds
- **Import execution**: 5-15 seconds depending on data size
- Large imports with sensor data may take longer

### Browser Compatibility

The UI export/import feature works in:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Support

For issues with export/import:
1. Check this documentation
2. Validate using dry-run mode
3. Review validation errors/warnings
4. Report issues at: https://github.com/anthropics/gardening-service/issues

## Version History

### v1.0.0 (2026-01-31)
- Initial release
- Full data export/import
- Three import modes (dry-run, merge, overwrite)
- Schema versioning
- Comprehensive validation
- ID remapping for relationships
