# Irrigation System API Quick Reference

## Setup

```bash
# Get auth token (save to variable)
export TOKEN=$(curl -s -X POST http://localhost:8080/users/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}' \
  | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

# Base URL
export API="http://localhost:8080"
```

## Quick Commands

### Overview
```bash
# Get complete system overview
curl -s "$API/irrigation-system/overview" -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# Get insights from rule engine
curl -s "$API/irrigation-system/insights" -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### Water Sources
```bash
# List all sources
curl -s "$API/irrigation-system/sources" -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# Create source
curl -s -X POST "$API/irrigation-system/sources" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"name": "City Water", "source_type": "city", "flow_capacity_lpm": 50}' | python3 -m json.tool

# Get source by ID
curl -s "$API/irrigation-system/sources/1" -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# Delete source
curl -s -X DELETE "$API/irrigation-system/sources/1" -H "Authorization: Bearer $TOKEN"
```

### Irrigation Zones
```bash
# List all zones
curl -s "$API/irrigation-system/zones" -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# Create zone
curl -s -X POST "$API/irrigation-system/zones" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{
    "name": "Veggie Garden",
    "delivery_type": "drip",
    "irrigation_source_id": 1,
    "schedule": {"frequency_days": 3, "duration_minutes": 30},
    "notes": "Main vegetable beds"
  }' | python3 -m json.tool

# Get zone details
curl -s "$API/irrigation-system/zones/1/details" -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# Update zone
curl -s -X PATCH "$API/irrigation-system/zones/1" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"schedule": {"frequency_days": 4, "duration_minutes": 45}}' | python3 -m json.tool

# Delete zone
curl -s -X DELETE "$API/irrigation-system/zones/1" -H "Authorization: Bearer $TOKEN"
```

### Watering Events
```bash
# Record watering event
curl -s -X POST "$API/irrigation-system/events" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{
    "irrigation_zone_id": 1,
    "watered_at": "2026-01-30T12:00:00.000Z",
    "duration_minutes": 30,
    "estimated_volume_liters": 25,
    "is_manual": true,
    "notes": "Regular watering"
  }' | python3 -m json.tool

# List events for zone (last 30 days)
curl -s "$API/irrigation-system/events?zone_id=1&days=30" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# Get event by ID
curl -s "$API/irrigation-system/events/1" -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# Update event
curl -s -X PATCH "$API/irrigation-system/events/1" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"duration_minutes": 35, "notes": "Extended duration"}' | python3 -m json.tool

# Delete event
curl -s -X DELETE "$API/irrigation-system/events/1" -H "Authorization: Bearer $TOKEN"
```

### Garden Assignment
```bash
# Assign garden to zone
curl -s -X POST "$API/irrigation-system/gardens/1/assign-zone?zone_id=1" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# Unassign garden from zone
curl -s -X POST "$API/irrigation-system/gardens/1/assign-zone?zone_id=null" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

## Common Patterns

### Test Rule Engine - Frequent Watering
```bash
# Record events every day for a week (triggers FREQ_001)
for i in {1..7}; do
  DATE=$(date -u -v-${i}d +"%Y-%m-%dT12:00:00.000Z" 2>/dev/null || date -u -d "${i} days ago" +"%Y-%m-%dT12:00:00.000Z")
  curl -s -X POST "$API/irrigation-system/events" \
    -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
    -d "{\"irrigation_zone_id\": 1, \"watered_at\": \"$DATE\", \"duration_minutes\": 30, \"is_manual\": true}"
done

# Check insights
curl -s "$API/irrigation-system/insights" -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### Test Rule Engine - Short Duration
```bash
# Record short-duration events (triggers DUR_001)
for i in {1..5}; do
  DATE=$(date -u -v-${i}d +"%Y-%m-%dT12:00:00.000Z" 2>/dev/null || date -u -d "${i} days ago" +"%Y-%m-%dT12:00:00.000Z")
  curl -s -X POST "$API/irrigation-system/events" \
    -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
    -d "{\"irrigation_zone_id\": 1, \"watered_at\": \"$DATE\", \"duration_minutes\": 5, \"is_manual\": true}"
done

# Check insights
curl -s "$API/irrigation-system/insights" -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### Complete Setup Flow
```bash
# 1. Create water source
SOURCE_ID=$(curl -s -X POST "$API/irrigation-system/sources" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"name": "Main Line", "source_type": "city"}' \
  | grep -o '"id":[0-9]*' | cut -d':' -f2)

# 2. Create zone
ZONE_ID=$(curl -s -X POST "$API/irrigation-system/zones" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d "{\"name\": \"Garden Zone\", \"delivery_type\": \"drip\", \"irrigation_source_id\": $SOURCE_ID, \"schedule\": {\"frequency_days\": 3, \"duration_minutes\": 30}}" \
  | grep -o '"id":[0-9]*' | cut -d':' -f2)

# 3. Assign garden to zone
curl -s -X POST "$API/irrigation-system/gardens/1/assign-zone?zone_id=$ZONE_ID" \
  -H "Authorization: Bearer $TOKEN"

# 4. Record watering
curl -s -X POST "$API/irrigation-system/events" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d "{\"irrigation_zone_id\": $ZONE_ID, \"watered_at\": \"$(date -u +"%Y-%m-%dT%H:%M:%S.000Z")\", \"duration_minutes\": 30, \"is_manual\": true}"

# 5. View overview
curl -s "$API/irrigation-system/overview" -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

## Delivery Types

- `drip` - Drip irrigation
- `sprinkler` - Overhead sprinklers
- `soaker` - Soaker hose
- `manual` - Manual watering

## Source Types

- `city` - Municipal water supply
- `well` - Well water
- `rain` - Rainwater collection
- `manual` - Manual/portable source

## Date Format

All dates must be in ISO 8601 UTC format:
```
2026-01-30T12:00:00.000Z
```

Generate current time:
```bash
date -u +"%Y-%m-%dT%H:%M:%S.000Z"
```
