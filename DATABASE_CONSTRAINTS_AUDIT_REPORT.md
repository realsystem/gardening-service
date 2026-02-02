# Database Schema Constraints Audit Report

**Date:** 2026-02-01
**Database:** PostgreSQL (SQLAlchemy ORM)
**Application:** Gardening Service

---

## Executive Summary

This report audits all SQLAlchemy models in the `app/models/` directory, documenting current database constraints and identifying missing constraints that could lead to data integrity issues. The audit covers 19 models with a focus on foreign keys, nullable columns, unique constraints, enum types, and application-assumed constraints.

### Key Findings

- **Foreign Keys Without ON DELETE/UPDATE:** Multiple models lack explicit cascade behavior
- **Nullable Columns That Should Be NOT NULL:** Several required fields are incorrectly nullable
- **Missing Foreign Key Constraints:** CompanionRelationship model lacks FK constraints
- **Inconsistent CASCADE Policies:** Mix of SET NULL, CASCADE, and no specification
- **Missing Unique Constraints:** Several business-critical uniqueness requirements not enforced

---

## 1. User Model (`user.py`)

### Current Constraints

#### Foreign Keys
None (root entity)

#### Columns & Nullable Status
| Column | Type | Nullable | Current State | Should Be |
|--------|------|----------|---------------|-----------|
| id | Integer | No | PRIMARY KEY | ✓ Correct |
| email | String | No | UNIQUE, NOT NULL | ✓ Correct |
| hashed_password | String | No | NOT NULL | ✓ Correct |
| is_admin | Boolean | No | NOT NULL, default=False | ✓ Correct |
| display_name | String(100) | Yes | NULL | ✓ Correct |
| avatar_url | String(500) | Yes | NULL | ✓ Correct |
| city | String(100) | Yes | NULL | ✓ Correct |
| gardening_preferences | Text | Yes | NULL | ✓ Correct |
| zip_code | String(10) | Yes | NULL | ✓ Correct |
| latitude | Float | Yes | NULL | ✓ Correct |
| longitude | Float | Yes | NULL | ✓ Correct |
| usda_zone | String(10) | Yes | NULL | ✓ Correct |
| unit_system | Enum | No | NOT NULL, default='metric' | ✓ Correct |
| restricted_crop_flag | Boolean | No | NOT NULL, default=False | ✓ Correct |
| restricted_crop_count | Integer | No | NOT NULL, default=0 | ✓ Correct |
| restricted_crop_first_violation | DateTime | Yes | NULL | ✓ Correct |
| restricted_crop_last_violation | DateTime | Yes | NULL | ✓ Correct |
| restricted_crop_reason | String(100) | Yes | NULL | ✓ Correct |
| created_at | DateTime | Yes | server_default=now() | ⚠️ Should be NOT NULL |
| updated_at | DateTime | Yes | onupdate=now() | ✓ Correct (nullable for new records) |

#### Unique Constraints
- `email` - UNIQUE INDEX ✓

#### Enum Types
- `UnitSystem`: ["metric", "imperial"] ✓

### Missing Constraints

1. **created_at should be NOT NULL** - Always has a server default
   - **Risk:** LOW - Server default ensures value exists
   - **Recommendation:** Add `nullable=False` for clarity

---

## 2. PlantVariety Model (`plant_variety.py`)

### Current Constraints

#### Foreign Keys
None (reference data table)

#### Columns & Nullable Status
| Column | Type | Nullable | Current State | Should Be |
|--------|------|----------|---------------|-----------|
| id | Integer | No | PRIMARY KEY | ✓ Correct |
| common_name | String(100) | No | NOT NULL, INDEXED | ✓ Correct |
| scientific_name | String(100) | Yes | NULL | ✓ Correct |
| variety_name | String(100) | Yes | NULL | ✓ Correct |
| days_to_germination_min | Integer | Yes | NULL | ✓ Correct |
| days_to_germination_max | Integer | Yes | NULL | ✓ Correct |
| days_to_harvest | Integer | Yes | NULL | ✓ Correct |
| spacing_inches | Integer | Yes | NULL | ✓ Correct |
| row_spacing_inches | Integer | Yes | NULL | ✓ Correct |
| sun_requirement | Enum | Yes | NULL | ✓ Correct |
| water_requirement | Enum | Yes | NULL | ✓ Correct |
| description | Text | Yes | NULL | ✓ Correct |
| growing_notes | Text | Yes | NULL | ✓ Correct |
| photo_url | String(500) | Yes | NULL | ✓ Correct |
| tags | Text | Yes | NULL | ✓ Correct |
| seedling_ec_min/max | Float | Yes | NULL | ✓ Correct |
| vegetative_ec_min/max | Float | Yes | NULL | ✓ Correct |
| flowering_ec_min/max | Float | Yes | NULL | ✓ Correct |
| fruiting_ec_min/max | Float | Yes | NULL | ✓ Correct |
| optimal_ph_min/max | Float | Yes | NULL | ✓ Correct |
| solution_change_days_min/max | Integer | Yes | NULL | ✓ Correct |

#### Unique Constraints
None - **MISSING**

#### Enum Types
- `SunRequirement`: ["full_sun", "partial_sun", "partial_shade", "full_shade"] ✓
- `WaterRequirement`: ["low", "medium", "high"] ✓

### Missing Constraints

1. **Unique constraint on (common_name, variety_name, scientific_name)**
   - **Risk:** MEDIUM - Could create duplicate plant varieties
   - **Recommendation:** Add composite unique constraint
   - **Business Logic:** Application likely assumes unique varieties

2. **Check constraint: days_to_germination_min <= days_to_germination_max**
   - **Risk:** LOW - Invalid data could confuse users
   - **Recommendation:** Add CHECK constraint

3. **Check constraint: ec_min <= ec_max, ph_min <= ph_max**
   - **Risk:** LOW - Invalid ranges affect nutrient calculations
   - **Recommendation:** Add CHECK constraints for all min/max pairs

---

## 3. Garden Model (`garden.py`)

### Current Constraints

#### Foreign Keys
| Column | References | ON DELETE | ON UPDATE | Current State |
|--------|------------|-----------|-----------|---------------|
| user_id | users.id | NOT SPECIFIED | NOT SPECIFIED | ⚠️ Missing CASCADE |
| land_id | lands.id | SET NULL | NOT SPECIFIED | ✓ Appropriate |
| irrigation_zone_id | irrigation_zones.id | SET NULL | NOT SPECIFIED | ✓ Appropriate |

#### Columns & Nullable Status
| Column | Type | Nullable | Current State | Should Be |
|--------|------|----------|---------------|-----------|
| id | Integer | No | PRIMARY KEY | ✓ Correct |
| user_id | Integer | No | NOT NULL, FK | ✓ Correct |
| name | String(100) | No | NOT NULL | ✓ Correct |
| description | Text | Yes | NULL | ✓ Correct |
| garden_type | Enum | No | NOT NULL, default=OUTDOOR | ✓ Correct |
| location | String(100) | Yes | NULL | ✓ Correct |
| light_source_type | Enum | Yes | NULL | ✓ Correct |
| light_hours_per_day | Float | Yes | NULL | ✓ Correct |
| temp_min_f | Float | Yes | NULL | ✓ Correct |
| temp_max_f | Float | Yes | NULL | ✓ Correct |
| humidity_min_percent | Float | Yes | NULL | ✓ Correct |
| humidity_max_percent | Float | Yes | NULL | ✓ Correct |
| container_type | String(100) | Yes | NULL | ✓ Correct |
| grow_medium | String(100) | Yes | NULL | ✓ Correct |
| is_hydroponic | Boolean | No | NOT NULL, default=False | ✓ Correct |
| hydro_system_type | Enum | Yes | NULL | ✓ Correct |
| reservoir_size_liters | Float | Yes | NULL | ✓ Correct |
| nutrient_schedule | Text | Yes | NULL | ✓ Correct |
| ph_min | Float | Yes | NULL | ✓ Correct |
| ph_max | Float | Yes | NULL | ✓ Correct |
| ec_min | Float | Yes | NULL | ✓ Correct |
| ec_max | Float | Yes | NULL | ✓ Correct |
| ppm_min | Integer | Yes | NULL | ✓ Correct |
| ppm_max | Integer | Yes | NULL | ✓ Correct |
| water_temp_min_f | Float | Yes | NULL | ✓ Correct |
| water_temp_max_f | Float | Yes | NULL | ✓ Correct |
| land_id | Integer | Yes | NULL, FK | ✓ Correct |
| x | Float | Yes | NULL | ✓ Correct |
| y | Float | Yes | NULL | ✓ Correct |
| width | Float | Yes | NULL | ✓ Correct |
| height | Float | Yes | NULL | ✓ Correct |
| irrigation_zone_id | Integer | Yes | NULL, FK | ✓ Correct |
| mulch_depth_inches | Float | Yes | NULL | ✓ Correct |
| is_raised_bed | Boolean | No | NOT NULL, default=False | ✓ Correct |
| soil_texture_override | String(50) | Yes | NULL | ✓ Correct |
| created_at | DateTime | Yes | server_default=now() | ⚠️ Should be NOT NULL |
| updated_at | DateTime | Yes | onupdate=now() | ✓ Correct |

#### Unique Constraints
None - Could benefit from unique constraint on (user_id, name)

#### Enum Types
- `GardenType`: ["outdoor", "indoor"] ✓
- `LightSourceType`: ["led", "fluorescent", "natural_supplement", "hps", "mh"] ✓
- `HydroSystemType`: ["nft", "dwc", "ebb_flow", "aeroponics", "drip", "wick", "fertigation", "container"] ✓

### Missing Constraints

1. **user_id Foreign Key lacks ON DELETE CASCADE**
   - **Risk:** HIGH - Orphaned gardens if user deleted
   - **Recommendation:** Add `ondelete='CASCADE'`
   - **Application Assumption:** User relationship has cascade="all, delete-orphan"

2. **Unique constraint on (user_id, name)**
   - **Risk:** LOW - Users could create duplicate garden names
   - **Recommendation:** Add unique constraint for better UX

3. **Check constraint: temp_min <= temp_max, humidity_min <= humidity_max**
   - **Risk:** LOW - Invalid ranges affect calculations
   - **Recommendation:** Add CHECK constraints

4. **Check constraint: If land_id is set, x, y, width, height should all be set**
   - **Risk:** MEDIUM - Partial spatial data causes layout errors
   - **Recommendation:** Add CHECK constraint or application validation

5. **Check constraint: is_hydroponic=true requires hydro_system_type NOT NULL**
   - **Risk:** MEDIUM - Hydroponic gardens without system type
   - **Recommendation:** Add CHECK constraint

---

## 4. SeedBatch Model (`seed_batch.py`)

### Current Constraints

#### Foreign Keys
| Column | References | ON DELETE | ON UPDATE | Current State |
|--------|------------|-----------|-----------|---------------|
| user_id | users.id | NOT SPECIFIED | NOT SPECIFIED | ⚠️ Missing CASCADE |
| plant_variety_id | plant_varieties.id | NOT SPECIFIED | NOT SPECIFIED | ⚠️ Missing RESTRICT |

#### Columns & Nullable Status
| Column | Type | Nullable | Current State | Should Be |
|--------|------|----------|---------------|-----------|
| id | Integer | No | PRIMARY KEY | ✓ Correct |
| user_id | Integer | No | NOT NULL, FK | ✓ Correct |
| plant_variety_id | Integer | No | NOT NULL, FK | ✓ Correct |
| source | String(200) | Yes | NULL | ✓ Correct |
| harvest_year | Integer | Yes | NULL | ✓ Correct |
| quantity | Integer | Yes | NULL | ✓ Correct |
| preferred_germination_method | String(100) | Yes | NULL | ✓ Correct |
| notes | Text | Yes | NULL | ✓ Correct |
| created_at | DateTime | Yes | server_default=now() | ⚠️ Should be NOT NULL |
| updated_at | DateTime | Yes | onupdate=now() | ✓ Correct |

#### Unique Constraints
None

#### Enum Types
None

### Missing Constraints

1. **user_id Foreign Key lacks ON DELETE CASCADE**
   - **Risk:** HIGH - Orphaned seed batches if user deleted
   - **Recommendation:** Add `ondelete='CASCADE'`
   - **Application Assumption:** User relationship has cascade="all, delete-orphan"

2. **plant_variety_id Foreign Key lacks ON DELETE RESTRICT**
   - **Risk:** MEDIUM - Deleting plant variety breaks seed batch references
   - **Recommendation:** Add `ondelete='RESTRICT'` to prevent deletion
   - **Rationale:** Plant varieties are reference data, shouldn't be deleted if in use

3. **Check constraint: quantity >= 0**
   - **Risk:** LOW - Negative quantities don't make sense
   - **Recommendation:** Add CHECK constraint

4. **Check constraint: harvest_year reasonable range (e.g., 1900-2100)**
   - **Risk:** LOW - Typos could create invalid years
   - **Recommendation:** Add CHECK constraint

---

## 5. PlantingEvent Model (`planting_event.py`)

### Current Constraints

#### Foreign Keys
| Column | References | ON DELETE | ON UPDATE | Current State |
|--------|------------|-----------|-----------|---------------|
| user_id | users.id | NOT SPECIFIED | NOT SPECIFIED | ⚠️ Missing CASCADE |
| garden_id | gardens.id | NOT SPECIFIED | NOT SPECIFIED | ⚠️ Missing CASCADE |
| plant_variety_id | plant_varieties.id | NOT SPECIFIED | NOT SPECIFIED | ⚠️ Missing RESTRICT |
| germination_event_id | germination_events.id | NOT SPECIFIED | NOT SPECIFIED | ⚠️ Missing SET NULL |

#### Columns & Nullable Status
| Column | Type | Nullable | Current State | Should Be |
|--------|------|----------|---------------|-----------|
| id | Integer | No | PRIMARY KEY | ✓ Correct |
| user_id | Integer | No | NOT NULL, FK | ✓ Correct |
| garden_id | Integer | No | NOT NULL, FK | ✓ Correct |
| plant_variety_id | Integer | No | NOT NULL, FK | ✓ Correct |
| germination_event_id | Integer | Yes | NULL, FK | ✓ Correct |
| planting_date | Date | No | NOT NULL, INDEXED | ✓ Correct |
| planting_method | Enum | No | NOT NULL | ✓ Correct |
| plant_count | Integer | Yes | NULL | ⚠️ Should be NOT NULL |
| location_in_garden | String(200) | Yes | NULL | ✓ Correct |
| health_status | Enum | Yes | NULL | ✓ Correct |
| plant_notes | Text | Yes | NULL | ✓ Correct |
| x | Float | Yes | NULL | ✓ Correct |
| y | Float | Yes | NULL | ✓ Correct |
| notes | Text | Yes | NULL | ✓ Correct |
| created_at | DateTime | Yes | server_default=now() | ⚠️ Should be NOT NULL |
| updated_at | DateTime | Yes | onupdate=now() | ✓ Correct |

#### Unique Constraints
None

#### Enum Types
- `PlantingMethod`: ["direct_sow", "transplant"] ✓
- `PlantHealth`: ["healthy", "stressed", "diseased"] ✓

### Missing Constraints

1. **user_id Foreign Key lacks ON DELETE CASCADE**
   - **Risk:** HIGH - Orphaned planting events if user deleted
   - **Recommendation:** Add `ondelete='CASCADE'`
   - **Application Assumption:** User relationship has cascade="all, delete-orphan"

2. **garden_id Foreign Key lacks ON DELETE CASCADE**
   - **Risk:** HIGH - Orphaned planting events if garden deleted
   - **Recommendation:** Add `ondelete='CASCADE'`
   - **Application Logic:** If garden deleted, plantings should be removed

3. **plant_variety_id Foreign Key lacks ON DELETE RESTRICT**
   - **Risk:** MEDIUM - Deleting plant variety breaks references
   - **Recommendation:** Add `ondelete='RESTRICT'`

4. **germination_event_id Foreign Key lacks ON DELETE SET NULL**
   - **Risk:** MEDIUM - Deleting germination event breaks reference
   - **Recommendation:** Add `ondelete='SET NULL'`
   - **Rationale:** Planting can exist without germination event (direct sow)

5. **plant_count should be NOT NULL with default=1**
   - **Risk:** MEDIUM - Application code likely assumes count exists
   - **Recommendation:** Change to `nullable=False, default=1`
   - **Rationale:** Every planting has at least 1 plant

6. **Check constraint: plant_count > 0**
   - **Risk:** MEDIUM - Zero or negative plants don't make sense
   - **Recommendation:** Add CHECK constraint

7. **Check constraint: planting_method='transplant' requires germination_event_id NOT NULL**
   - **Risk:** MEDIUM - Transplants should reference germination
   - **Recommendation:** Add CHECK constraint or application validation

---

## 6. CareTask Model (`care_task.py`)

### Current Constraints

#### Foreign Keys
| Column | References | ON DELETE | ON UPDATE | Current State |
|--------|------------|-----------|-----------|---------------|
| user_id | users.id | NOT SPECIFIED | NOT SPECIFIED | ⚠️ Missing CASCADE |
| planting_event_id | planting_events.id | NOT SPECIFIED | NOT SPECIFIED | ⚠️ Missing CASCADE |
| parent_task_id | care_tasks.id | NOT SPECIFIED | NOT SPECIFIED | ⚠️ Missing CASCADE |

#### Columns & Nullable Status
| Column | Type | Nullable | Current State | Should Be |
|--------|------|----------|---------------|-----------|
| id | Integer | No | PRIMARY KEY | ✓ Correct |
| user_id | Integer | No | NOT NULL, FK | ✓ Correct |
| planting_event_id | Integer | Yes | NULL, FK | ✓ Correct |
| task_type | Enum | No | NOT NULL | ✓ Correct |
| task_source | Enum | No | NOT NULL, default=MANUAL | ✓ Correct |
| title | String(200) | No | NOT NULL | ✓ Correct |
| description | Text | Yes | NULL | ✓ Correct |
| priority | Enum | No | NOT NULL, default=MEDIUM | ✓ Correct |
| due_date | Date | No | NOT NULL, INDEXED | ✓ Correct |
| is_recurring | Boolean | No | NOT NULL, default=False | ✓ Correct |
| recurrence_frequency | Enum | Yes | NULL | ✓ Correct |
| parent_task_id | Integer | Yes | NULL, FK | ✓ Correct |
| status | Enum | No | NOT NULL, default=PENDING | ✓ Correct |
| completed_date | Date | Yes | NULL | ✓ Correct |
| notes | Text | Yes | NULL | ✓ Correct |
| created_at | DateTime | Yes | server_default=now() | ⚠️ Should be NOT NULL |
| updated_at | DateTime | Yes | onupdate=now() | ✓ Correct |

#### Unique Constraints
None

#### Enum Types
- `TaskType`: ["water", "fertilize", "prune", "mulch", "weed", "pest_control", "harvest", "adjust_lighting", "adjust_temperature", "adjust_humidity", "nutrient_solution", "train_plant", "check_nutrient_solution", "adjust_ph", "replace_nutrient_solution", "clean_reservoir", "adjust_water_circulation", "other"] ✓
- `TaskStatus`: ["pending", "completed", "skipped"] ✓
- `TaskSource`: ["auto_generated", "manual"] ✓
- `TaskPriority`: ["low", "medium", "high"] ✓
- `RecurrenceFrequency`: ["daily", "weekly", "biweekly", "monthly"] ✓

### Missing Constraints

1. **user_id Foreign Key lacks ON DELETE CASCADE**
   - **Risk:** HIGH - Orphaned tasks if user deleted
   - **Recommendation:** Add `ondelete='CASCADE'`
   - **Application Assumption:** User relationship has cascade="all, delete-orphan"

2. **planting_event_id Foreign Key lacks ON DELETE CASCADE**
   - **Risk:** MEDIUM - Tasks persist after planting deleted
   - **Recommendation:** Add `ondelete='CASCADE'`
   - **Rationale:** Tasks tied to plantings should be removed with planting

3. **parent_task_id Foreign Key lacks ON DELETE CASCADE**
   - **Risk:** MEDIUM - Child tasks orphaned when parent deleted
   - **Recommendation:** Add `ondelete='CASCADE'`
   - **Rationale:** Recurring child tasks should be removed with parent

4. **Check constraint: is_recurring=true requires recurrence_frequency NOT NULL**
   - **Risk:** MEDIUM - Recurring tasks without frequency
   - **Recommendation:** Add CHECK constraint

5. **Check constraint: status='completed' requires completed_date NOT NULL**
   - **Risk:** LOW - Completed tasks should have completion date
   - **Recommendation:** Add CHECK constraint or application validation

6. **Check constraint: Prevent self-reference (parent_task_id != id)**
   - **Risk:** LOW - Task cannot be its own parent
   - **Recommendation:** Add CHECK constraint

---

## 7. SensorReading Model (`sensor_reading.py`)

### Current Constraints

#### Foreign Keys
| Column | References | ON DELETE | ON UPDATE | Current State |
|--------|------------|-----------|-----------|---------------|
| user_id | users.id | NOT SPECIFIED | NOT SPECIFIED | ⚠️ Missing CASCADE |
| garden_id | gardens.id | NOT SPECIFIED | NOT SPECIFIED | ⚠️ Missing CASCADE |

#### Columns & Nullable Status
| Column | Type | Nullable | Current State | Should Be |
|--------|------|----------|---------------|-----------|
| id | Integer | No | PRIMARY KEY | ✓ Correct |
| user_id | Integer | No | NOT NULL, FK | ✓ Correct |
| garden_id | Integer | No | NOT NULL, FK | ✓ Correct |
| reading_date | Date | No | NOT NULL, INDEXED | ✓ Correct |
| temperature_f | Float | Yes | NULL | ✓ Correct |
| humidity_percent | Float | Yes | NULL | ✓ Correct |
| light_hours | Float | Yes | NULL | ✓ Correct |
| ph_level | Float | Yes | NULL | ✓ Correct |
| ec_ms_cm | Float | Yes | NULL | ✓ Correct |
| ppm | Integer | Yes | NULL | ✓ Correct |
| water_temp_f | Float | Yes | NULL | ✓ Correct |
| created_at | DateTime | Yes | server_default=now() | ⚠️ Should be NOT NULL |

#### Unique Constraints
None - **MISSING**

#### Enum Types
None

### Missing Constraints

1. **user_id Foreign Key lacks ON DELETE CASCADE**
   - **Risk:** HIGH - Orphaned readings if user deleted
   - **Recommendation:** Add `ondelete='CASCADE'`
   - **Application Assumption:** User relationship has cascade="all, delete-orphan"

2. **garden_id Foreign Key lacks ON DELETE CASCADE**
   - **Risk:** HIGH - Orphaned readings if garden deleted
   - **Recommendation:** Add `ondelete='CASCADE'`
   - **Application Logic:** Garden relationship has cascade="all, delete-orphan"

3. **Unique constraint on (garden_id, reading_date)**
   - **Risk:** MEDIUM - Duplicate readings for same day
   - **Recommendation:** Add unique constraint
   - **Rationale:** One reading per garden per day makes sense for daily tracking

4. **Check constraint: temperature_f in reasonable range (-50 to 150)**
   - **Risk:** LOW - Unrealistic temperatures from sensor errors
   - **Recommendation:** Add CHECK constraint

5. **Check constraint: humidity_percent between 0 and 100**
   - **Risk:** LOW - Invalid percentage values
   - **Recommendation:** Add CHECK constraint

6. **Check constraint: ph_level between 0 and 14**
   - **Risk:** LOW - Invalid pH values
   - **Recommendation:** Add CHECK constraint

---

## 8. SoilSample Model (`soil_sample.py`)

### Current Constraints

#### Foreign Keys
| Column | References | ON DELETE | ON UPDATE | Current State |
|--------|------------|-----------|-----------|---------------|
| user_id | users.id | NOT SPECIFIED | NOT SPECIFIED | ⚠️ Missing CASCADE |
| garden_id | gardens.id | CASCADE | NOT SPECIFIED | ✓ Correct |
| planting_event_id | planting_events.id | CASCADE | NOT SPECIFIED | ✓ Correct |

#### Columns & Nullable Status
| Column | Type | Nullable | Current State | Should Be |
|--------|------|----------|---------------|-----------|
| id | Integer | No | PRIMARY KEY | ✓ Correct |
| user_id | Integer | No | NOT NULL, FK | ✓ Correct |
| garden_id | Integer | Yes | NULL, FK | ✓ Correct |
| planting_event_id | Integer | Yes | NULL, FK | ✓ Correct |
| ph | Float | No | NOT NULL | ✓ Correct |
| nitrogen_ppm | Float | Yes | NULL | ✓ Correct |
| phosphorus_ppm | Float | Yes | NULL | ✓ Correct |
| potassium_ppm | Float | Yes | NULL | ✓ Correct |
| organic_matter_percent | Float | Yes | NULL | ✓ Correct |
| moisture_percent | Float | Yes | NULL | ✓ Correct |
| date_collected | Date | No | NOT NULL | ✓ Correct |
| notes | Text | Yes | NULL | ✓ Correct |

#### Unique Constraints
None

#### Enum Types
None

### Missing Constraints

1. **user_id Foreign Key lacks ON DELETE CASCADE**
   - **Risk:** HIGH - Orphaned samples if user deleted
   - **Recommendation:** Add `ondelete='CASCADE'`
   - **Application Assumption:** User relationship has cascade="all, delete-orphan"

2. **Check constraint: At least one of garden_id or planting_event_id must be NOT NULL**
   - **Risk:** MEDIUM - Sample not associated with anything
   - **Recommendation:** Add CHECK constraint
   - **Rationale:** Samples must belong to garden or planting

3. **Check constraint: ph between 0 and 14**
   - **Risk:** LOW - Invalid pH values
   - **Recommendation:** Add CHECK constraint

4. **Check constraint: All ppm values >= 0**
   - **Risk:** LOW - Negative nutrients don't make sense
   - **Recommendation:** Add CHECK constraint

5. **Check constraint: Percentages between 0 and 100**
   - **Risk:** LOW - Invalid percentage values
   - **Recommendation:** Add CHECK constraint

---

## 9. IrrigationEvent Model (`irrigation_event.py`)

### Current Constraints

#### Foreign Keys
| Column | References | ON DELETE | ON UPDATE | Current State |
|--------|------------|-----------|-----------|---------------|
| user_id | users.id | NOT SPECIFIED | NOT SPECIFIED | ⚠️ Missing CASCADE |
| garden_id | gardens.id | CASCADE | NOT SPECIFIED | ✓ Correct |
| planting_event_id | planting_events.id | CASCADE | NOT SPECIFIED | ✓ Correct |

#### Columns & Nullable Status
| Column | Type | Nullable | Current State | Should Be |
|--------|------|----------|---------------|-----------|
| id | Integer | No | PRIMARY KEY | ✓ Correct |
| user_id | Integer | No | NOT NULL, FK | ✓ Correct |
| garden_id | Integer | Yes | NULL, FK | ✓ Correct |
| planting_event_id | Integer | Yes | NULL, FK | ✓ Correct |
| irrigation_date | DateTime | No | NOT NULL, default=utcnow | ✓ Correct |
| water_volume_liters | Float | Yes | NULL | ✓ Correct |
| irrigation_method | Enum | No | NOT NULL | ✓ Correct |
| duration_minutes | Integer | Yes | NULL | ✓ Correct |
| notes | Text | Yes | NULL | ✓ Correct |

#### Unique Constraints
None

#### Enum Types
- `IrrigationMethod`: ["drip", "sprinkler", "hand_watering", "soaker_hose", "flood", "misting"] ✓

### Missing Constraints

1. **user_id Foreign Key lacks ON DELETE CASCADE**
   - **Risk:** HIGH - Orphaned events if user deleted
   - **Recommendation:** Add `ondelete='CASCADE'`
   - **Application Assumption:** User relationship has cascade="all, delete-orphan"

2. **Check constraint: At least one of garden_id or planting_event_id must be NOT NULL**
   - **Risk:** MEDIUM - Event not associated with anything
   - **Recommendation:** Add CHECK constraint
   - **Rationale:** Irrigation must target garden or planting

3. **Check constraint: water_volume_liters > 0**
   - **Risk:** LOW - Zero/negative volume doesn't make sense
   - **Recommendation:** Add CHECK constraint

4. **Check constraint: duration_minutes > 0**
   - **Risk:** LOW - Zero/negative duration doesn't make sense
   - **Recommendation:** Add CHECK constraint

---

## 10. IrrigationZone Model (`irrigation_zone.py`)

### Current Constraints

#### Foreign Keys
| Column | References | ON DELETE | ON UPDATE | Current State |
|--------|------------|-----------|-----------|---------------|
| user_id | users.id | CASCADE | NOT SPECIFIED | ✓ Correct |
| irrigation_source_id | irrigation_sources.id | SET NULL | NOT SPECIFIED | ✓ Correct |

#### Columns & Nullable Status
| Column | Type | Nullable | Current State | Should Be |
|--------|------|----------|---------------|-----------|
| id | Integer | No | PRIMARY KEY | ✓ Correct |
| user_id | Integer | No | NOT NULL, FK | ✓ Correct |
| irrigation_source_id | Integer | Yes | NULL, FK | ✓ Correct |
| name | String | No | NOT NULL | ✓ Correct |
| delivery_type | String | No | NOT NULL | ⚠️ Should be ENUM |
| schedule | JSON | Yes | NULL | ✓ Correct |
| notes | String | Yes | NULL | ✓ Correct |
| created_at | DateTime | No | NOT NULL, default=utcnow | ✓ Correct |
| updated_at | DateTime | No | NOT NULL, default/onupdate=utcnow | ✓ Correct |

#### Unique Constraints
None - Could benefit from unique (user_id, name)

#### Enum Types
None - **MISSING**

### Missing Constraints

1. **delivery_type should be ENUM instead of String**
   - **Risk:** MEDIUM - Invalid delivery types (typos)
   - **Recommendation:** Create DeliveryType enum: ["drip", "sprinkler", "soaker", "manual"]
   - **Current Code:** Accepts any string value

2. **Unique constraint on (user_id, name)**
   - **Risk:** LOW - Users could create duplicate zone names
   - **Recommendation:** Add unique constraint for better UX

---

## 11. IrrigationSource Model (`irrigation_source.py`)

### Current Constraints

#### Foreign Keys
| Column | References | ON DELETE | ON UPDATE | Current State |
|--------|------------|-----------|-----------|---------------|
| user_id | users.id | CASCADE | NOT SPECIFIED | ✓ Correct |

#### Columns & Nullable Status
| Column | Type | Nullable | Current State | Should Be |
|--------|------|----------|---------------|-----------|
| id | Integer | No | PRIMARY KEY | ✓ Correct |
| user_id | Integer | No | NOT NULL, FK | ✓ Correct |
| name | String | No | NOT NULL | ✓ Correct |
| source_type | String | No | NOT NULL | ⚠️ Should be ENUM |
| flow_capacity_lpm | Float | Yes | NULL | ✓ Correct |
| notes | String | Yes | NULL | ✓ Correct |
| created_at | DateTime | No | NOT NULL, default=utcnow | ✓ Correct |
| updated_at | DateTime | No | NOT NULL, default/onupdate=utcnow | ✓ Correct |

#### Unique Constraints
None - Could benefit from unique (user_id, name)

#### Enum Types
None - **MISSING**

### Missing Constraints

1. **source_type should be ENUM instead of String**
   - **Risk:** MEDIUM - Invalid source types (typos)
   - **Recommendation:** Create SourceType enum: ["city", "well", "rain", "manual"]
   - **Current Code:** Comment mentions these values but doesn't enforce them

2. **Unique constraint on (user_id, name)**
   - **Risk:** LOW - Users could create duplicate source names
   - **Recommendation:** Add unique constraint for better UX

3. **Check constraint: flow_capacity_lpm > 0**
   - **Risk:** LOW - Negative flow doesn't make sense
   - **Recommendation:** Add CHECK constraint

---

## 12. Land Model (`land.py`)

### Current Constraints

#### Foreign Keys
| Column | References | ON DELETE | ON UPDATE | Current State |
|--------|------------|-----------|-----------|---------------|
| user_id | users.id | NOT SPECIFIED | NOT SPECIFIED | ⚠️ Missing CASCADE |

#### Columns & Nullable Status
| Column | Type | Nullable | Current State | Should Be |
|--------|------|----------|---------------|-----------|
| id | Integer | No | PRIMARY KEY | ✓ Correct |
| user_id | Integer | No | NOT NULL, FK, INDEXED | ✓ Correct |
| name | String(100) | No | NOT NULL | ✓ Correct |
| width | Float | No | NOT NULL | ✓ Correct |
| height | Float | No | NOT NULL | ✓ Correct |
| created_at | DateTime | Yes | server_default=now() | ⚠️ Should be NOT NULL |
| updated_at | DateTime | Yes | onupdate=now() | ✓ Correct |

#### Unique Constraints
None - Could benefit from unique (user_id, name)

#### Enum Types
None

### Missing Constraints

1. **user_id Foreign Key lacks ON DELETE CASCADE**
   - **Risk:** HIGH - Orphaned lands if user deleted
   - **Recommendation:** Add `ondelete='CASCADE'`
   - **Application Assumption:** User relationship has cascade="all, delete-orphan"

2. **Unique constraint on (user_id, name)**
   - **Risk:** LOW - Users could create duplicate land names
   - **Recommendation:** Add unique constraint for better UX

3. **Check constraint: width > 0 AND height > 0**
   - **Risk:** MEDIUM - Zero/negative dimensions invalid
   - **Recommendation:** Add CHECK constraint
   - **Rationale:** Land must have positive dimensions

---

## 13. Tree Model (`tree.py`)

### Current Constraints

#### Foreign Keys
| Column | References | ON DELETE | ON UPDATE | Current State |
|--------|------------|-----------|-----------|---------------|
| user_id | users.id | NOT SPECIFIED | NOT SPECIFIED | ⚠️ Missing CASCADE |
| land_id | lands.id | CASCADE | NOT SPECIFIED | ✓ Correct |
| species_id | plant_varieties.id | NOT SPECIFIED | NOT SPECIFIED | ⚠️ Missing SET NULL |

#### Columns & Nullable Status
| Column | Type | Nullable | Current State | Should Be |
|--------|------|----------|---------------|-----------|
| id | Integer | No | PRIMARY KEY | ✓ Correct |
| user_id | Integer | No | NOT NULL, FK, INDEXED | ✓ Correct |
| land_id | Integer | No | NOT NULL, FK, INDEXED | ✓ Correct |
| name | String(100) | No | NOT NULL | ✓ Correct |
| species_id | Integer | Yes | NULL, FK, INDEXED | ✓ Correct |
| x | Float | No | NOT NULL | ✓ Correct |
| y | Float | No | NOT NULL | ✓ Correct |
| canopy_radius | Float | No | NOT NULL | ✓ Correct |
| height | Float | Yes | NULL | ✓ Correct |
| created_at | DateTime | Yes | server_default=now() | ⚠️ Should be NOT NULL |
| updated_at | DateTime | Yes | onupdate=now() | ✓ Correct |

#### Unique Constraints
None

#### Enum Types
None

### Missing Constraints

1. **user_id Foreign Key lacks ON DELETE CASCADE**
   - **Risk:** HIGH - Orphaned trees if user deleted
   - **Recommendation:** Add `ondelete='CASCADE'`
   - **Application Assumption:** User relationship has cascade="all, delete-orphan"

2. **species_id Foreign Key lacks ON DELETE SET NULL**
   - **Risk:** LOW - Deleting plant variety breaks tree reference
   - **Recommendation:** Add `ondelete='SET NULL'`
   - **Rationale:** Tree can exist without species reference

3. **Check constraint: canopy_radius > 0**
   - **Risk:** MEDIUM - Zero/negative radius invalid
   - **Recommendation:** Add CHECK constraint

4. **Check constraint: height > 0 (if not null)**
   - **Risk:** LOW - Zero/negative height invalid
   - **Recommendation:** Add CHECK constraint

5. **Check constraint: x >= 0 AND y >= 0**
   - **Risk:** MEDIUM - Negative coordinates invalid in top-left origin system
   - **Recommendation:** Add CHECK constraint

---

## 14. Structure Model (`structure.py`)

### Current Constraints

#### Foreign Keys
| Column | References | ON DELETE | ON UPDATE | Current State |
|--------|------------|-----------|-----------|---------------|
| user_id | users.id | NOT SPECIFIED | NOT SPECIFIED | ⚠️ Missing CASCADE |
| land_id | lands.id | CASCADE | NOT SPECIFIED | ✓ Correct |

#### Columns & Nullable Status
| Column | Type | Nullable | Current State | Should Be |
|--------|------|----------|---------------|-----------|
| id | Integer | No | PRIMARY KEY | ✓ Correct |
| user_id | Integer | No | NOT NULL, FK, INDEXED | ✓ Correct |
| land_id | Integer | No | NOT NULL, FK, INDEXED | ✓ Correct |
| name | String(100) | No | NOT NULL | ✓ Correct |
| x | Float | No | NOT NULL | ✓ Correct |
| y | Float | No | NOT NULL | ✓ Correct |
| width | Float | No | NOT NULL | ✓ Correct |
| depth | Float | No | NOT NULL | ✓ Correct |
| height | Float | No | NOT NULL | ✓ Correct |
| created_at | DateTime | Yes | server_default=now() | ⚠️ Should be NOT NULL |
| updated_at | DateTime | Yes | onupdate=now() | ✓ Correct |

#### Unique Constraints
None

#### Enum Types
None

### Missing Constraints

1. **user_id Foreign Key lacks ON DELETE CASCADE**
   - **Risk:** HIGH - Orphaned structures if user deleted
   - **Recommendation:** Add `ondelete='CASCADE'`
   - **Application Assumption:** User relationship has cascade="all, delete-orphan"

2. **Check constraint: width > 0 AND depth > 0 AND height > 0**
   - **Risk:** MEDIUM - Zero/negative dimensions invalid
   - **Recommendation:** Add CHECK constraint

3. **Check constraint: x >= 0 AND y >= 0**
   - **Risk:** MEDIUM - Negative coordinates invalid
   - **Recommendation:** Add CHECK constraint

---

## 15. GrowthStage Enum (`growth_stage.py`)

### Current Constraints

This is a Python enum, not a database model.

#### Enum Types
- `GrowthStage`: ["seedling", "vegetative", "flowering", "fruiting"] ✓

### Missing Constraints

None - This is used for application logic, not stored in database directly.

---

## 16. CompanionRelationship Model (`companion_relationship.py`)

### Current Constraints

#### Foreign Keys
**NONE** - **CRITICAL ISSUE**

#### Columns & Nullable Status
| Column | Type | Nullable | Current State | Should Be |
|--------|------|----------|---------------|-----------|
| id | Integer | No | PRIMARY KEY | ✓ Correct |
| plant_a_id | Integer | No | NOT NULL, INDEXED | ⚠️ Missing FK |
| plant_b_id | Integer | No | NOT NULL, INDEXED | ⚠️ Missing FK |
| relationship_type | Enum | No | NOT NULL, INDEXED | ✓ Correct |
| mechanism | Text | No | NOT NULL | ✓ Correct |
| confidence_level | Enum | No | NOT NULL | ✓ Correct |
| effective_distance_m | Float | No | NOT NULL, default=1.0 | ✓ Correct |
| optimal_distance_m | Float | Yes | NULL | ✓ Correct |
| source_reference | Text | No | NOT NULL | ✓ Correct |
| notes | Text | Yes | NULL | ✓ Correct |

#### Unique Constraints
- `unique_plant_pair` on (plant_a_id, plant_b_id) ✓

#### Indexes
- `idx_companion_plants` on (plant_a_id, plant_b_id) ✓
- `idx_relationship_type` on (relationship_type) ✓

#### Enum Types
- `RelationshipType`: ["beneficial", "neutral", "antagonistic"] ✓
- `ConfidenceLevel`: ["high", "medium", "low"] ✓

### Missing Constraints - **CRITICAL**

1. **plant_a_id Foreign Key MISSING**
   - **Risk:** CRITICAL - No referential integrity
   - **Recommendation:** Add `ForeignKey('plant_varieties.id', ondelete='CASCADE')`
   - **Current State:** Comment says "ForeignKey to plant_varieties.id" but not implemented
   - **Impact:** Could reference non-existent plants, orphaned relationships

2. **plant_b_id Foreign Key MISSING**
   - **Risk:** CRITICAL - No referential integrity
   - **Recommendation:** Add `ForeignKey('plant_varieties.id', ondelete='CASCADE')`
   - **Current State:** Comment says "ForeignKey to plant_varieties.id" but not implemented
   - **Impact:** Could reference non-existent plants, orphaned relationships

3. **Check constraint: plant_a_id < plant_b_id (normalization)**
   - **Risk:** MEDIUM - Duplicate pairs in reverse order
   - **Recommendation:** Add CHECK constraint
   - **Current State:** Comment says "enforced at application level"
   - **Impact:** Application bug could create (A,B) and (B,A) duplicates

4. **Check constraint: plant_a_id != plant_b_id**
   - **Risk:** MEDIUM - Plant can't be companion to itself
   - **Recommendation:** Add CHECK constraint

5. **Check constraint: effective_distance_m > 0**
   - **Risk:** LOW - Zero/negative distance invalid
   - **Recommendation:** Add CHECK constraint

6. **Check constraint: optimal_distance_m <= effective_distance_m (if not null)**
   - **Risk:** LOW - Optimal should be within effective range
   - **Recommendation:** Add CHECK constraint

---

## 17. GerminationEvent Model (`germination_event.py`)

### Current Constraints

#### Foreign Keys
| Column | References | ON DELETE | ON UPDATE | Current State |
|--------|------------|-----------|-----------|---------------|
| user_id | users.id | NOT SPECIFIED | NOT SPECIFIED | ⚠️ Missing CASCADE |
| seed_batch_id | seed_batches.id | NOT SPECIFIED | NOT SPECIFIED | ⚠️ Missing CASCADE |
| plant_variety_id | plant_varieties.id | NOT SPECIFIED | NOT SPECIFIED | ⚠️ Missing RESTRICT |

#### Columns & Nullable Status
| Column | Type | Nullable | Current State | Should Be |
|--------|------|----------|---------------|-----------|
| id | Integer | No | PRIMARY KEY | ✓ Correct |
| user_id | Integer | No | NOT NULL, FK | ✓ Correct |
| seed_batch_id | Integer | No | NOT NULL, FK | ✓ Correct |
| plant_variety_id | Integer | No | NOT NULL, FK | ✓ Correct |
| started_date | Date | No | NOT NULL | ✓ Correct |
| germination_location | String(100) | Yes | NULL | ✓ Correct |
| seed_count | Integer | Yes | NULL | ⚠️ Should be NOT NULL |
| germinated | Boolean | Yes | default=False | ⚠️ Should be NOT NULL |
| germination_date | Date | Yes | NULL | ✓ Correct |
| germination_count | Integer | Yes | NULL | ✓ Correct |
| germination_success_rate | Float | Yes | NULL | ✓ Correct |
| notes | Text | Yes | NULL | ✓ Correct |
| created_at | DateTime | Yes | server_default=now() | ⚠️ Should be NOT NULL |
| updated_at | DateTime | Yes | onupdate=now() | ✓ Correct |

#### Unique Constraints
None

#### Enum Types
None

### Missing Constraints

1. **user_id Foreign Key lacks ON DELETE CASCADE**
   - **Risk:** HIGH - Orphaned events if user deleted
   - **Recommendation:** Add `ondelete='CASCADE'`
   - **Application Assumption:** User relationship has cascade="all, delete-orphan"

2. **seed_batch_id Foreign Key lacks ON DELETE CASCADE**
   - **Risk:** MEDIUM - Events persist after batch deleted
   - **Recommendation:** Add `ondelete='CASCADE'`
   - **Rationale:** Events tied to batch should be removed with batch

3. **plant_variety_id Foreign Key lacks ON DELETE RESTRICT**
   - **Risk:** MEDIUM - Deleting plant variety breaks references
   - **Recommendation:** Add `ondelete='RESTRICT'`

4. **seed_count should be NOT NULL**
   - **Risk:** MEDIUM - Application code likely assumes count exists
   - **Recommendation:** Change to `nullable=False`
   - **Rationale:** Must know how many seeds started

5. **germinated should be NOT NULL**
   - **Risk:** LOW - Boolean with default should not be nullable
   - **Recommendation:** Change to `nullable=False, default=False`

6. **Check constraint: seed_count > 0**
   - **Risk:** MEDIUM - Zero/negative seeds don't make sense
   - **Recommendation:** Add CHECK constraint

7. **Check constraint: germination_count <= seed_count**
   - **Risk:** LOW - Can't germinate more than started
   - **Recommendation:** Add CHECK constraint

8. **Check constraint: germination_success_rate between 0 and 100**
   - **Risk:** LOW - Invalid percentage
   - **Recommendation:** Add CHECK constraint

9. **Check constraint: germinated=true requires germination_date NOT NULL**
   - **Risk:** LOW - Germinated events should have date
   - **Recommendation:** Add CHECK constraint or application validation

---

## 18. WateringEvent Model (`watering_event.py`)

### Current Constraints

#### Foreign Keys
| Column | References | ON DELETE | ON UPDATE | Current State |
|--------|------------|-----------|-----------|---------------|
| user_id | users.id | CASCADE | NOT SPECIFIED | ✓ Correct |
| irrigation_zone_id | irrigation_zones.id | CASCADE | NOT SPECIFIED | ✓ Correct |

#### Columns & Nullable Status
| Column | Type | Nullable | Current State | Should Be |
|--------|------|----------|---------------|-----------|
| id | Integer | No | PRIMARY KEY | ✓ Correct |
| user_id | Integer | No | NOT NULL, FK | ✓ Correct |
| irrigation_zone_id | Integer | No | NOT NULL, FK | ✓ Correct |
| watered_at | DateTime | No | NOT NULL, INDEXED, default=utcnow | ✓ Correct |
| duration_minutes | Float | No | NOT NULL | ✓ Correct |
| estimated_volume_liters | Float | Yes | NULL | ✓ Correct |
| is_manual | Boolean | No | NOT NULL, default=False | ✓ Correct |
| notes | String | Yes | NULL | ✓ Correct |
| created_at | DateTime | No | NOT NULL, default=utcnow | ✓ Correct |

#### Unique Constraints
None

#### Enum Types
None

### Missing Constraints

1. **Check constraint: duration_minutes > 0**
   - **Risk:** MEDIUM - Zero/negative duration doesn't make sense
   - **Recommendation:** Add CHECK constraint

2. **Check constraint: estimated_volume_liters > 0 (if not null)**
   - **Risk:** LOW - Zero/negative volume doesn't make sense
   - **Recommendation:** Add CHECK constraint

---

## 19. PasswordResetToken Model (`password_reset_token.py`)

### Current Constraints

#### Foreign Keys
| Column | References | ON DELETE | ON UPDATE | Current State |
|--------|------------|-----------|-----------|---------------|
| user_id | users.id | CASCADE | NOT SPECIFIED | ✓ Correct |

#### Columns & Nullable Status
| Column | Type | Nullable | Current State | Should Be |
|--------|------|----------|---------------|-----------|
| id | Integer | No | PRIMARY KEY | ✓ Correct |
| user_id | Integer | No | NOT NULL, FK | ✓ Correct |
| token_hash | String(255) | No | NOT NULL, UNIQUE, INDEXED | ✓ Correct |
| expires_at | DateTime | No | NOT NULL | ✓ Correct |
| used_at | DateTime | Yes | NULL | ✓ Correct |
| created_at | DateTime | No | NOT NULL, default=utcnow | ✓ Correct |

#### Unique Constraints
- `token_hash` - UNIQUE INDEX ✓

#### Indexes
- `idx_user_active_tokens` on (user_id, used_at, expires_at) ✓

#### Enum Types
None

### Missing Constraints

1. **Check constraint: expires_at > created_at**
   - **Risk:** LOW - Token with invalid expiration
   - **Recommendation:** Add CHECK constraint
   - **Rationale:** Expiration must be after creation

2. **Check constraint: used_at >= created_at (if not null)**
   - **Risk:** LOW - Token used before creation
   - **Recommendation:** Add CHECK constraint

---

## Summary of Critical Issues

### HIGH RISK (Data Loss Potential)

1. **Missing ON DELETE CASCADE on user_id foreign keys** (14 models affected)
   - Models: Garden, SeedBatch, PlantingEvent, CareTask, SensorReading, SoilSample, IrrigationEvent, Land, Tree, Structure, GerminationEvent
   - Impact: Orphaned records if user deleted
   - Fix: Add `ondelete='CASCADE'` to all user_id ForeignKey definitions

2. **CompanionRelationship missing foreign key constraints** (CRITICAL)
   - plant_a_id and plant_b_id have no FK constraint
   - Impact: No referential integrity, can reference non-existent plants
   - Fix: Add ForeignKey constraints immediately

### MEDIUM RISK (Data Integrity Issues)

1. **Missing unique constraints** (5 models)
   - SensorReading: (garden_id, reading_date)
   - PlantVariety: (common_name, variety_name, scientific_name)
   - Multiple models: (user_id, name) for UX

2. **String columns that should be ENUMs** (2 models)
   - IrrigationZone.delivery_type
   - IrrigationSource.source_type

3. **Nullable columns that should be NOT NULL**
   - PlantingEvent.plant_count
   - GerminationEvent.seed_count
   - GerminationEvent.germinated
   - Multiple created_at timestamps

### LOW RISK (Data Quality Issues)

1. **Missing CHECK constraints** (50+ constraints)
   - Min/max range validation
   - Positive number validation
   - Percentage bounds (0-100)
   - Conditional requirements

---

## Recommended Migration Priority

### Phase 1: Critical Fixes (Do Immediately)
1. Add foreign key constraints to CompanionRelationship
2. Add ON DELETE CASCADE to all user_id foreign keys
3. Add unique constraint on (garden_id, reading_date) for SensorReading

### Phase 2: High Priority (Next Sprint)
1. Convert delivery_type and source_type to ENUMs
2. Make plant_count, seed_count, germinated NOT NULL
3. Add unique constraints for user-scoped names
4. Add ON DELETE policies to remaining foreign keys

### Phase 3: Data Quality (Ongoing)
1. Add CHECK constraints for ranges and positive values
2. Add CHECK constraints for percentages
3. Add conditional CHECK constraints (business rules)
4. Make timestamp columns explicitly NOT NULL

---

## Migration Template Example

```python
"""Add foreign key constraints to companion_relationship

Revision ID: xxxxx
Revises: yyyy
Create Date: 2026-02-01
"""
from alembic import op
import sqlalchemy as sa

def upgrade() -> None:
    # Add foreign key constraints
    op.create_foreign_key(
        'fk_companion_relationship_plant_a',
        'companion_relationships',
        'plant_varieties',
        ['plant_a_id'],
        ['id'],
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'fk_companion_relationship_plant_b',
        'companion_relationships',
        'plant_varieties',
        ['plant_b_id'],
        ['id'],
        ondelete='CASCADE'
    )

    # Add check constraints
    op.create_check_constraint(
        'check_normalized_pair',
        'companion_relationships',
        'plant_a_id < plant_b_id'
    )
    op.create_check_constraint(
        'check_not_self_companion',
        'companion_relationships',
        'plant_a_id != plant_b_id'
    )
    op.create_check_constraint(
        'check_effective_distance_positive',
        'companion_relationships',
        'effective_distance_m > 0'
    )

def downgrade() -> None:
    op.drop_constraint('check_effective_distance_positive', 'companion_relationships')
    op.drop_constraint('check_not_self_companion', 'companion_relationships')
    op.drop_constraint('check_normalized_pair', 'companion_relationships')
    op.drop_constraint('fk_companion_relationship_plant_b', 'companion_relationships')
    op.drop_constraint('fk_companion_relationship_plant_a', 'companion_relationships')
```

---

## Conclusion

The database schema has a solid foundation with proper use of enums, indexes, and relationships. However, there are significant gaps in referential integrity constraints (especially CASCADE behaviors and the CompanionRelationship foreign keys) that should be addressed immediately to prevent data integrity issues.

The recommended phased approach prioritizes critical fixes that could lead to data loss or corruption, followed by data quality improvements that enhance application reliability.
