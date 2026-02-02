# Platform Simplification Refactoring Plan

**Date**: February 1, 2026
**Objective**: Reduce cognitive load, remove unrealistic user burdens, align with real human behavior
**Based on**: Independent Product Audit findings

---

## Executive Summary

This refactoring removes **70% of platform features** to focus on the 20% that delivers real value to amateur gardeners. The changes are **subtractive, not additive** - every removed feature improves usability.

**Guiding Principle**: The system must remain useful even if users never log anything after initial setup.

---

## Phase 1: Remove Watering Tracking System

### 🗑️ Complete Removal

**Database Tables** (DROP):
- `watering_events` - User logging of watering activities
- `irrigation_events` - Automated irrigation tracking
- `irrigation_zones` - Zone-based watering schedules
- `irrigation_sources` - Water source management

**Models** (DELETE):
- `app/models/watering_event.py`
- `app/models/irrigation_event.py`
- `app/models/irrigation_zone.py`
- `app/models/irrigation_source.py`

**API Endpoints** (DELETE):
- `POST /irrigation-zones` - Create irrigation zone
- `GET /irrigation-zones` - List zones
- `PUT /irrigation-zones/{id}` - Update zone
- `DELETE /irrigation-zones/{id}` - Delete zone
- `POST /watering-events` - Log watering
- `GET /watering-events` - List watering history
- `GET /irrigation-system/insights` - Irrigation insights with alerts

**Rules** (DELETE):
- `app/rules/rules_irrigation.py` - All irrigation rules
  - `FREQ_001` - Watering too frequently
  - `DUR_001` - Short duration watering
  - `RESPONSE_001` - Low moisture despite watering

**Foreign Keys** (UPDATE):
- Remove `irrigation_zone_id` from `gardens` table
- Remove `irrigation_source_id` references

**Relationships** (UPDATE):
- Remove `watering_events` from User model
- Remove `irrigation_zones` from User model
- Remove `irrigation_zone` from Garden model

### ✅ Replacement: Advisory Information Only

**Add to PlantVariety model**:
```python
# Reference information (no tracking)
water_needs = Column(String, nullable=True)  # "low", "medium", "high"
drought_tolerant = Column(Boolean, default=False)
typical_watering_frequency_days = Column(Integer, nullable=True)  # Advisory only
```

**UI Changes**:
- Show "Typical watering: Every 3-4 days in summer" (read-only)
- Show "💧 Water needs: Medium" badge
- Remove all watering logs, schedules, zone management
- No tracking, no alerts, no user input

**Migration**:
```sql
-- Drop tables (preserve data for 30 days via backup)
-- Add advisory fields to plant_varieties
-- Remove foreign keys from gardens
```

---

## Phase 2: User Groups & Feature Gating

### 🎯 User Groups (Mandatory at Registration)

**New Enum**:
```python
class UserGroup(str, enum.Enum):
    AMATEUR_GARDENER = "amateur_gardener"  # Default, 90% of users
    FARMER = "farmer"  # Intermediate features
    SCIENTIFIC_RESEARCHER = "scientific_researcher"  # Full access
```

**Add to Users Table**:
```python
user_group = Column(Enum(UserGroup),
                    default=UserGroup.AMATEUR_GARDENER,
                    nullable=False)
show_trees = Column(Boolean, default=False)  # Amateur toggle for tree visibility
enable_alerts = Column(Boolean, default=False)  # All users: alerts off by default
```

### 🔒 Feature Matrix (Backend Enforced)

| Feature | Amateur | Farmer | Researcher |
|---------|---------|--------|------------|
| **Core** |
| Garden list | ✅ | ✅ | ✅ |
| Plant list with photos | ✅ | ✅ | ✅ |
| Days to harvest countdown | ✅ | ✅ | ✅ |
| Planting date history | ✅ | ✅ | ✅ |
| Basic layout visual | ✅ | ✅ | ✅ |
| **Intermediate** |
| Soil type selection | Simple | Detailed | Full |
| Watering reminders | Advisory | Advisory | Advisory |
| Tree positions | Hidden* | Visible | Visible |
| Tree shadows | Hidden | Visible | Visible |
| Companion planting | Info only | Info only | Analysis |
| **Advanced** |
| Hydroponic systems | ❌ | ❌ | ✅ |
| EC/pH monitoring | ❌ | ❌ | ✅ |
| Nutrient optimization | ❌ | ❌ | ✅ |
| Soil samples (detailed) | ❌ | View-only | ✅ |
| Rule engine config | ❌ | ❌ | ✅ |
| Sensor integration | ❌ | ❌ | ✅ |

\* Amateur users can toggle `show_trees` in profile settings

### 🛡️ Backend Enforcement

**Decorator for feature gating**:
```python
@require_user_group([UserGroup.SCIENTIFIC_RESEARCHER])
def create_hydroponic_garden(...):
    pass

@require_user_group([UserGroup.FARMER, UserGroup.SCIENTIFIC_RESEARCHER])
def view_soil_samples(...):
    pass
```

**API Returns**:
- Amateur requesting hydroponic endpoint: `403 Forbidden - Feature requires Researcher account`
- Feature flags in user profile response for frontend visibility

---

## Phase 3: Onboarding Simplification

### 📱 New 3-Screen Onboarding

**Current state**: 8-12 screens with 30+ fields
**Target**: 3 screens, 3 fields total

#### Screen 1: Climate Setup
```
┌─────────────────────────────────┐
│ What's your location?           │
│                                 │
│ ZIP Code: [_____]              │
│                                 │
│ We'll use this to:             │
│ • Set your climate zone        │
│ • Suggest planting dates       │
│ • Show appropriate plants      │
│                                 │
│         [Continue →]            │
└─────────────────────────────────┘
```

**Backend**: Auto-infer climate zone, frost dates from ZIP

#### Screen 2: First Garden
```
┌─────────────────────────────────┐
│ Create your first garden        │
│                                 │
│ Garden name: [____________]    │
│                                 │
│ [📷 Add photo (optional)]      │
│                                 │
│ That's it! You can add more    │
│ details later if you want.     │
│                                 │
│         [Continue →]            │
└─────────────────────────────────┘
```

**No fields for**: size, soil type, layout, irrigation

#### Screen 3: Add Plants
```
┌─────────────────────────────────┐
│ What are you growing?           │
│                                 │
│ [🔍 Search plants...]          │
│                                 │
│ Popular in your area:           │
│ [ ] Tomatoes                   │
│ [ ] Basil                      │
│ [ ] Peppers                    │
│ [ ] Lettuce                    │
│                                 │
│     [Skip]    [Get Started →]  │
└─────────────────────────────────┘
```

**On completion**: User lands on garden view with plants visible immediately. No tutorial. No checklist.

### 🗑️ Removed from Onboarding
- Land creation (auto-created on first garden)
- Land dimensions
- Tree positioning
- Garden positioning on grid
- Soil sample requirements
- Irrigation zone setup
- Water source configuration
- Hydroponic system questions

---

## Phase 4: Tree Modeling Refactor

### 🚫 Remove User Input

**Current** (asking users):
- Tree height in feet
- Canopy radius in feet
- Growth rate
- Exact coordinates (x, y)

**New** (scientific defaults):
- Auto-calculate from species
- Hidden by default for amateurs
- Toggle in profile: "Show trees on my layout"

### 🌲 Species Reference Data

**Add to database**:
```python
# Tree species reference table
tree_species:
  - name: "Oak (Mature)"
    typical_height_ft: 60
    typical_canopy_radius_ft: 30
    growth_rate: "slow"

  - name: "Maple (Mature)"
    typical_height_ft: 50
    typical_canopy_radius_ft: 25
    growth_rate: "medium"
```

**Tree model changes**:
```python
class Tree:
    species_name = Column(String, nullable=False)  # User selects from list
    # REMOVED: height, radius (use species defaults)
    # KEPT: x, y position (simplified to drag-and-drop)
    position_x = Column(Float)
    position_y = Column(Float)

    @property
    def height(self):
        """Auto-calculate from species reference"""
        return TreeSpecies.get(self.species_name).typical_height_ft
```

### 👁️ Visibility Control

**Amateur users**:
- Trees hidden by default
- Profile toggle: `☐ Show trees on my garden layout`
- If enabled: trees appear, shadows calculate automatically
- If disabled: clean layout, no shadow complexity

**Farmer/Researcher**:
- Trees always visible
- Shadow analysis available

---

## Phase 5: Rule Engine Changes

### 🔕 Alerts Off by Default

**User profile**:
```python
enable_alerts = Column(Boolean, default=False)
```

**Settings UI**:
```
Recommendations & Alerts
☐ Enable garden recommendations and alerts

  When enabled, you'll receive suggestions about:
  • Companion planting combinations
  • Seasonal planting timing
  • Potential issues detected

  All suggestions are advisory - you can always ignore them.
```

### 📋 Alert Philosophy Changes

**Before**:
- Red error-style warnings
- Blocking UI elements
- Feels punitive ("You're doing it wrong")

**After**:
- Soft blue info cards
- Dismissible
- Helpful tone: "Consider..." / "You might want to..."
- Never blocks functionality

**Example transformation**:
```
BEFORE:
⚠️ ERROR: Tomato and Broccoli conflict detected!
[Fix Now] [Ignore]

AFTER (if alerts enabled):
💡 Planting Tip
Some gardeners report better results keeping tomatoes
and brassicas in separate areas.
[Learn More] [Dismiss]
```

### 🗑️ Removed Alert Categories

- Watering frequency warnings (FREQ_001) - DELETED
- Watering duration warnings (DUR_001) - DELETED
- Moisture response warnings (RESPONSE_001) - DELETED
- Any alert dependent on user logging - DELETED

### ✅ Kept Alert Categories (Optional)

- Companion planting suggestions (reworded as tips)
- Frost date reminders
- Harvest window notifications

---

## Phase 6: Database Schema Changes

### Migration Plan

**Create migration: `remove_watering_system.py`**

```python
def upgrade():
    # 1. Backup data to archive tables (30-day retention)
    op.execute("""
        CREATE TABLE _archive_watering_events AS
        SELECT * FROM watering_events
    """)

    op.execute("""
        CREATE TABLE _archive_irrigation_zones AS
        SELECT * FROM irrigation_zones
    """)

    # 2. Drop foreign keys
    op.drop_constraint('gardens_irrigation_zone_id_fkey', 'gardens')

    # 3. Drop columns
    op.drop_column('gardens', 'irrigation_zone_id')

    # 4. Drop tables
    op.drop_table('watering_events')
    op.drop_table('irrigation_events')
    op.drop_table('irrigation_zones')
    op.drop_table('irrigation_sources')

    # 5. Add user groups
    op.execute("""
        CREATE TYPE usergroup AS ENUM (
            'amateur_gardener',
            'farmer',
            'scientific_researcher'
        )
    """)

    op.add_column('users',
        sa.Column('user_group',
                  sa.Enum('amateur_gardener', 'farmer', 'scientific_researcher',
                          name='usergroup'),
                  server_default='amateur_gardener',
                  nullable=False))

    op.add_column('users',
        sa.Column('show_trees', sa.Boolean(),
                  server_default='false', nullable=False))

    op.add_column('users',
        sa.Column('enable_alerts', sa.Boolean(),
                  server_default='false', nullable=False))

    # 6. Add advisory watering fields to plant_varieties
    op.add_column('plant_varieties',
        sa.Column('water_needs', sa.String(), nullable=True))
    op.add_column('plant_varieties',
        sa.Column('drought_tolerant', sa.Boolean(),
                  server_default='false'))
    op.add_column('plant_varieties',
        sa.Column('typical_watering_frequency_days', sa.Integer(),
                  nullable=True))

def downgrade():
    # Restore from archive (if within 30 days)
    # Reverse all schema changes
```

### Data Migration Strategy

**Existing users**:
- Default to `amateur_gardener` group
- Send email: "We've simplified your gardening experience!"
- Provide upgrade path to Farmer/Researcher if needed

**Archived data**:
- Retain for 30 days in `_archive_*` tables
- After 30 days: permanent deletion
- Users can export their data before migration

---

## Phase 7: API Changes

### 🗑️ Removed Endpoints

```
DELETE /irrigation-zones
DELETE /irrigation-zones/{id}
POST /irrigation-zones
PUT /irrigation-zones/{id}

DELETE /irrigation-sources
DELETE /irrigation-sources/{id}
POST /irrigation-sources
PUT /irrigation-sources/{id}

DELETE /watering-events
POST /watering-events
GET /watering-events

DELETE /irrigation-events
POST /irrigation-events
GET /irrigation-events

DELETE /irrigation-system/insights
```

### ✅ Modified Endpoints

**`GET /plant-varieties/{id}`**:
```json
{
  "id": 1,
  "common_name": "Tomato",
  "water_needs": "medium",
  "drought_tolerant": false,
  "typical_watering_frequency_days": 3,
  "watering_guidance": "Water deeply every 2-4 days in summer. Reduce frequency in cooler weather."
}
```

**`GET /users/me`**:
```json
{
  "id": 1,
  "email": "user@example.com",
  "user_group": "amateur_gardener",
  "show_trees": false,
  "enable_alerts": false,
  "feature_flags": {
    "hydroponics": false,
    "soil_samples": false,
    "tree_shadows": false,
    "companion_analysis": false
  }
}
```

**`GET /gardens/{id}`**:
```json
{
  "id": 1,
  "name": "Vegetable Garden",
  // REMOVED: irrigation_zone_id, watering_schedule
  // REMOVED: last_watered_at, days_since_watering
  "plants": [...]
}
```

---

## Phase 8: Frontend Changes

### 🎨 UI Simplification

**Removed screens**:
- Irrigation zone management
- Watering event logging
- Watering history
- Water source setup
- Irrigation insights dashboard

**Removed components**:
- `<IrrigationZoneForm />`
- `<WateringEventLogger />`
- `<IrrigationInsights />`
- `<WateringHistory />`

**Modified components**:

**Garden Details**:
```tsx
// BEFORE: Complex irrigation section
<IrrigationSection
  zone={garden.irrigation_zone}
  lastWatered={garden.last_watered_at}
  onLogWatering={() => {...}}
/>

// AFTER: Simple reference
<PlantCareSection>
  <WateringGuide plants={garden.plants} />
  {/* Shows: "Typical watering: Every 2-4 days in summer" */}
</PlantCareSection>
```

**Navigation**:
```tsx
// REMOVED from main nav:
- "Irrigation System"
- "Watering Log"

// KEPT:
- "My Gardens"
- "Plants"
- "Layout" (if user_group !== amateur OR show_trees enabled)
```

### 🎯 Progressive Disclosure

**Amateur users see**:
- Simple garden list
- Plant cards with photos
- Days to harvest prominently
- Optional watering guidance (read-only)

**Amateur users DON'T see**:
- Hydroponic features
- EC/pH fields
- Tree shadows
- Detailed soil samples
- Irrigation zone management

**Upgrade prompt** (subtle, bottom of settings):
```
Need more advanced features?
Switch to Farmer or Researcher mode →
```

---

## Phase 9: Testing Strategy

### ✅ New Tests Required

**User group enforcement**:
```python
def test_amateur_cannot_create_hydroponic_garden():
    user = create_user(user_group=UserGroup.AMATEUR_GARDENER)
    response = client.post('/gardens', json={
        'name': 'Hydro Garden',
        'is_hydroponic': True
    }, headers=auth_headers(user))

    assert response.status_code == 403
    assert 'requires Researcher account' in response.json()['detail']

def test_researcher_can_create_hydroponic_garden():
    user = create_user(user_group=UserGroup.SCIENTIFIC_RESEARCHER)
    response = client.post('/gardens', json={
        'name': 'Hydro Garden',
        'is_hydroponic': True
    }, headers=auth_headers(user))

    assert response.status_code == 201
```

**Graceful degradation**:
```python
def test_system_works_without_any_watering_logs():
    """System must provide value even if user never logs watering"""
    user = create_user()
    garden = create_garden(user)
    planting = create_planting(garden, variety='Tomato')

    # Don't log any watering

    # System still works
    response = client.get(f'/gardens/{garden.id}')
    assert response.status_code == 200
    assert response.json()['plants'][0]['days_to_harvest'] > 0
    # No warnings about missing watering data
```

**Onboarding completion**:
```python
def test_onboarding_completes_in_3_steps():
    # Step 1: Set ZIP
    response = client.post('/onboarding/climate', json={'zip_code': '94110'})
    assert response.status_code == 200

    # Step 2: Create garden
    response = client.post('/onboarding/garden', json={'name': 'My Garden'})
    assert response.status_code == 201

    # Step 3: Add plants (optional - can skip)
    response = client.post('/onboarding/complete')
    assert response.status_code == 200
    assert response.json()['onboarding_complete'] == True
```

**Tree visibility**:
```python
def test_trees_hidden_for_amateur_by_default():
    user = create_user(user_group=UserGroup.AMATEUR_GARDENER)
    garden = create_garden(user)
    tree = create_tree(user)

    response = client.get(f'/gardens/{garden.id}/layout')
    assert 'trees' not in response.json()
    assert 'shadows' not in response.json()

def test_trees_visible_when_toggled():
    user = create_user(user_group=UserGroup.AMATEUR_GARDENER)
    client.patch('/users/me', json={'show_trees': True})

    response = client.get(f'/gardens/{garden.id}/layout')
    assert 'trees' in response.json()
```

**Alert opt-in**:
```python
def test_alerts_disabled_by_default():
    user = create_user()
    # Create scenario that would trigger alert

    response = client.get('/alerts')
    assert response.json()['alerts'] == []

def test_alerts_enabled_when_opted_in():
    user = create_user()
    client.patch('/users/me', json={'enable_alerts': True})

    # Now alerts appear
    response = client.get('/alerts')
    assert len(response.json()['alerts']) > 0
```

### 🗑️ Tests to Remove

- All watering event tests
- All irrigation zone tests
- All irrigation rule tests (FREQ_001, DUR_001, RESPONSE_001)
- Irrigation insights tests

---

## Migration Checklist

### Pre-Migration

- [ ] Backup entire database
- [ ] Export watering/irrigation data for users who request it
- [ ] Send notification email to all users (7 days advance notice)
- [ ] Create rollback plan

### Migration Execution

- [ ] Run data archive script (preserve 30 days)
- [ ] Execute schema migration
- [ ] Update all users to `user_group = amateur_gardener`
- [ ] Seed plant variety watering guidance
- [ ] Verify foreign key constraints dropped
- [ ] Run database integrity checks

### Post-Migration Validation

- [ ] Amateur users cannot access hidden features (tested via API)
- [ ] Onboarding completes in 3 screens
- [ ] System works without watering logs
- [ ] Tree visibility toggle works
- [ ] Alert toggle works
- [ ] No 500 errors from removed tables
- [ ] API documentation updated
- [ ] Frontend deploys without errors

### Communication

- [ ] Send "Platform Updated" email to users
- [ ] Update documentation site
- [ ] Create upgrade guide (amateur → farmer/researcher)
- [ ] Post changelog

---

## Risk Analysis

### High Risk Items

1. **Data loss perception**: Users may feel their watering logs are deleted
   - **Mitigation**: Archive for 30 days, offer export, communicate clearly

2. **Feature removal backlash**: Power users may complain about removed features
   - **Mitigation**: Provide upgrade path to Researcher mode

3. **Breaking API changes**: External integrations may fail
   - **Mitigation**: Version API, deprecation notices, migration guide

### Medium Risk Items

1. **User confusion**: "Where did irrigation zones go?"
   - **Mitigation**: In-app messaging, help docs, support articles

2. **Test coverage gaps**: New feature gating logic needs comprehensive testing
   - **Mitigation**: 100+ new tests for user group enforcement

### Low Risk Items

1. **Performance impact**: Fewer tables = faster queries
   - **Impact**: Positive

2. **Storage reduction**: Removing watering logs reduces DB size
   - **Impact**: Positive

---

## Success Metrics

### Usability Metrics (Target: +50% improvement)

- **Onboarding completion rate**: 40% → 70%
- **Time to first value** (garden created + plant added): 10 min → 2 min
- **Feature confusion reports**: 30/week → 5/week

### Retention Metrics (Target: +200% improvement)

- **Week 1 retention**: 27% → 60%
- **Week 4 retention**: 10% → 30%
- **Month 3 active users**: 3% → 15%

### Trust Metrics (Target: +300% improvement)

- **"App doesn't know what it's doing" complaints**: 15/week → 2/week
- **Alert dismissal rate**: 90% → 30%
- **Feature adoption** (layout, companion tips): 5% → 25%

### Technical Metrics

- **Database size reduction**: -40% (watering logs removed)
- **API response time**: -15% (fewer joins)
- **Code complexity**: -35% (4 models + endpoints removed)

---

## Timeline

### Week 1: Phase 1 (Remove Watering System)
- Day 1-2: Create migrations, archive data
- Day 3-4: Remove models, APIs, tests
- Day 5: Integration testing

### Week 2: Phase 2-3 (User Groups + Onboarding)
- Day 1-2: Add user groups, feature gating
- Day 3-4: Simplify onboarding flow
- Day 5: Testing + validation

### Week 3: Phase 4-5 (Trees + Alerts)
- Day 1-2: Refactor tree modeling
- Day 3-4: Disable alerts by default
- Day 5: End-to-end testing

### Week 4: Phase 6-7 (Cleanup + Documentation)
- Day 1-2: Remove dead code
- Day 3-4: Update documentation
- Day 5: Final validation, deploy

---

## Rollback Plan

**If migration fails or user backlash is severe**:

1. **Immediate**: Restore database from backup (< 1 hour)
2. **Short-term**: Re-enable archived endpoints in read-only mode
3. **Long-term**: Create "Classic Mode" toggle (not recommended)

**Rollback triggers**:
- >50% support ticket increase
- >30% user churn in first week
- Critical bugs affecting core functionality

---

## Communication Plan

### Email to Users (7 days before migration)

**Subject**: We're Simplifying Your Gardening Experience

> Hi [Name],
>
> We've heard your feedback: our gardening platform was too complex. So we're making it radically simpler.
>
> **What's changing:**
> - Faster setup (3 simple steps instead of 12)
> - No more irrigation zone management
> - No more watering logs to maintain
> - Cleaner interface focused on what matters: your plants!
>
> **What you're keeping:**
> - All your gardens and plants
> - Planting history
> - Days to harvest countdowns
> - Everything that helps you actually grow food
>
> **What if I need advanced features?**
> You can upgrade to "Farmer" or "Researcher" mode in settings to get hydroponics, detailed soil tracking, and more.
>
> **Questions?** Reply to this email or visit our help center.
>
> Happy gardening,
> The Team

### In-App Messaging (Day of migration)

```
🎉 Welcome to Simplified Gardening!

We've removed the complexity and kept what matters.

Your gardens, plants, and history are all here.

[Take a Quick Tour] [Dismiss]
```

---

## Post-Launch Monitoring

### Week 1 Checklist

- [ ] Monitor error rates (target: <0.5%)
- [ ] Track onboarding completion (target: >60%)
- [ ] Read support tickets (expect spike, should decline)
- [ ] Watch for user group distribution (expect 90% amateur)

### Week 2-4 Checklist

- [ ] Measure retention rates
- [ ] Survey users: "How was onboarding?"
- [ ] Identify feature requests (expect: hydroponics access)
- [ ] Optimize based on usage patterns

---

## Documentation Updates Required

- [ ] API reference (remove irrigation endpoints)
- [ ] User guide (simplify to 3 pages)
- [ ] Developer docs (user group gating)
- [ ] Migration guide (v1 → v2)
- [ ] FAQ: "Where did irrigation zones go?"

---

## Appendix: Before/After Comparison

### User Journey: Creating a Garden

**BEFORE** (12 steps, 30+ fields):
1. Create land parcel (dimensions required)
2. Position land on map
3. Add trees (height, radius, coordinates)
4. Create water source (flow rate, type)
5. Create irrigation zone (schedule, delivery type)
6. Create garden (name, size, soil, position)
7. Assign garden to irrigation zone
8. Add soil sample (moisture %, N-P-K levels)
9. Add plants (search, select)
10. Position plants on grid (x, y coordinates)
11. Log first watering event (duration, volume)
12. Set up watering alerts

**AFTER** (3 steps, 3 fields):
1. Enter ZIP code
2. Name your garden
3. Add plants (optional)

**Completion time**: 25 minutes → 2 minutes

---

**END OF REFACTORING PLAN**

This plan removes the burden of unrealistic data entry while preserving genuine value for amateur gardeners. Implementation begins immediately.
