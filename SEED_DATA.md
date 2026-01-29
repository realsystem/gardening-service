# Seed Data Documentation

## Overview

The database is seeded with **27 plant varieties** across **17 different plant types** to provide a rich starting catalog for users.

## Plant Varieties Included

### Vegetables

**Tomatoes (3 varieties)**
- 🍅 Cherry - Small, sweet tomatoes (60 days to harvest)
- 🍅 Beefsteak - Large, meaty slicing tomatoes (85 days)
- 🍅 Roma - Paste tomatoes for sauces (75 days)

**Lettuce (3 varieties)** - Excellent for hydroponics
- 🥬 Butterhead - Tender, buttery leaves (45 days)
- 🥬 Romaine - Crisp, heat tolerant (55 days)
- 🥬 Oak Leaf - Loose leaf, slow to bolt (50 days)

**Peppers (2 varieties)**
- 🌶️ Bell Pepper - Sweet, colorful (75 days)
- 🌶️ Jalapeño - Moderately spicy (70 days)

**Cucumbers (2 varieties)**
- 🥒 Pickling - Small, perfect for pickles (55 days)
- 🥒 Slicing - Long, fresh eating (60 days)

**Beans (2 varieties)**
- 🫘 Green Bush - Compact, no support needed (55 days)
- 🫘 Pole - Climbing, higher yield (65 days)

**Leafy Greens**
- 🥬 Spinach (Baby Leaf) - Tender baby spinach (40 days)
- 🥬 Kale (Lacinato) - Dinosaur kale, frost hardy (60 days)
- 🥬 Arugula (Rocket) - Peppery salad green (40 days)
- 🥬 Swiss Chard (Rainbow) - Colorful stems (55 days)

**Root Vegetables**
- 🥕 Carrot (Nantes) - Sweet, cylindrical (70 days)
- 🥕 Radish (Cherry Belle) - Fast-growing red (25 days)

**Fruits**
- 🍓 Strawberry (Everbearing) - Spring through fall (120 days)

### Herbs

**Basil (2 varieties)**
- 🌿 Sweet Basil - Classic Italian (60 days)
- 🌿 Thai Basil - Anise-flavored for Asian cuisine (60 days)

**Other Herbs**
- 🌿 Cilantro (Standard) - Mexican & Asian dishes (50 days)
- 🌿 Parsley (Flat Leaf) - Italian parsley (70 days)
- 🌿 Mint (Spearmint) - Refreshing for teas (60 days)

### Microgreens

**Microgreens (3 varieties)** - Perfect for indoor/hydroponic
- 🌱 Broccoli - Nutrient-dense (10 days)
- 🌱 Sunflower - Crunchy, nutty (12 days)
- 🌱 Pea Shoots - Sweet, tender (14 days)

## Categories & Tags

Each plant variety is tagged for easy filtering:

- **vegetable, fruit** - Tomatoes, Peppers, Cucumbers
- **leafy-green, salad** - Lettuce, Spinach, Arugula
- **leafy-green, nutritious** - Kale, Swiss Chard
- **herb, aromatic** - Basil, Cilantro, Parsley, Mint
- **legume, nitrogen-fixer** - Beans
- **root-vegetable** - Carrots, Radishes
- **microgreen, quick-growing, hydroponic** - Microgreens
- **fruit, perennial** - Strawberries

## Growing Requirements

### Sun Requirements
- **Full Sun** - 6-8 hours daily (Tomatoes, Peppers, Cucumbers, Beans, etc.)
- **Partial Sun** - 4-6 hours daily (Lettuce, Arugula, Microgreens)
- **Partial Shade** - 2-4 hours daily (Mint)

### Water Requirements
- **High** - Lettuce, Spinach, Cucumbers, Microgreens
- **Medium** - Most vegetables and herbs
- **Low** - Not used in current varieties

## Ideal for Different Garden Types

### 🏡 Outdoor Gardens
- All tomatoes, peppers, beans
- Root vegetables (carrots, radishes)
- Leafy greens (kale, swiss chard)
- Herbs (basil, cilantro, parsley)

### 🏠 Indoor Gardens
- Microgreens (all varieties)
- Herbs (basil, cilantro, mint, parsley)
- Baby leafy greens (lettuce, spinach, arugula)
- Strawberries (in containers)

### 💧 Hydroponic Systems
- **Fastest Growing**: Microgreens (10-14 days)
- **Best Performers**: Lettuce, Spinach, Arugula
- **Herbs**: Basil, Cilantro
- **Advanced**: Tomatoes, Peppers, Strawberries

## Quick Reference

### Fastest to Harvest
1. 🏆 Microgreens - 10-14 days
2. 🥕 Radish - 25 days
3. 🥬 Spinach - 40 days
4. 🥬 Arugula - 40 days
5. 🥬 Lettuce - 45-55 days

### Best for Beginners
- 🥬 Lettuce (any variety)
- 🥕 Radish
- 🌱 Microgreens
- 🌿 Basil
- 🥬 Arugula

### Space-Efficient
- Microgreens (1" spacing)
- Radish (2" spacing)
- Lettuce (8" spacing)
- Spinach (4" spacing)

## Database Schema

```sql
CREATE TABLE plant_varieties (
    id SERIAL PRIMARY KEY,
    common_name VARCHAR(100) NOT NULL,
    scientific_name VARCHAR(200),
    variety_name VARCHAR(100),
    days_to_germination_min INT,
    days_to_germination_max INT,
    days_to_harvest INT,
    spacing_inches DECIMAL(5,2),
    row_spacing_inches DECIMAL(5,2),
    sun_requirement sunrequirement,
    water_requirement waterrequirement,
    description TEXT,
    growing_notes TEXT,
    photo_url VARCHAR(500),
    tags TEXT[]
);
```

## Loading Seed Data

### Initial Load
```bash
docker-compose exec db psql -U gardener -d gardening_db < migrations/seed_plant_varieties.sql
```

### Verify Data
```sql
-- Count varieties
SELECT COUNT(*) FROM plant_varieties;  -- Should be 27

-- Group by common name
SELECT common_name, COUNT(*) as varieties
FROM plant_varieties
GROUP BY common_name
ORDER BY common_name;

-- View all with tags
SELECT common_name, variety_name, tags
FROM plant_varieties
ORDER BY common_name, variety_name;
```

## Using Plant Varieties in the App

### Frontend Flow
1. **Create a Garden** - Select garden type (outdoor/indoor)
2. **Add Planting Event** - Plant varieties dropdown now populated
3. **Select Plant** - Choose from 27 varieties
4. **View Details** - See germination time, harvest days, care requirements
5. **Get Tasks** - Auto-generated care tasks based on plant needs

### API Endpoints
```bash
# Get all plant varieties
GET /plant-varieties

# Search by common name
GET /plant-varieties?search=tomato

# Filter by tags
GET /plant-varieties?tags=microgreen,quick-growing
```

## Maintenance

### Adding New Varieties
```sql
INSERT INTO plant_varieties (
    common_name, scientific_name, variety_name,
    days_to_germination_min, days_to_germination_max,
    days_to_harvest, spacing_inches, row_spacing_inches,
    sun_requirement, water_requirement,
    description, growing_notes, tags
) VALUES (
    'Basil', 'Ocimum basilicum', 'Genovese',
    5, 10, 60, 10, 12,
    'full_sun', 'medium',
    'Traditional Italian basil',
    'Pinch to encourage bushiness',
    ARRAY['herb', 'aromatic']
);
```

### Updating Existing Varieties
```sql
UPDATE plant_varieties
SET growing_notes = 'Updated growing instructions'
WHERE common_name = 'Tomato' AND variety_name = 'Cherry';
```

## Migration Script

**File:** [`migrations/seed_plant_varieties.sql`](migrations/seed_plant_varieties.sql)

**Features:**
- Truncates existing data (use with caution in production)
- Inserts 27 plant varieties
- Adds category tags
- Includes verification queries
- Idempotent (can be run multiple times)

**Warning:** The `TRUNCATE CASCADE` will remove all related data:
- Seed batches
- Germination events
- Planting events
- Care tasks
- Soil samples
- Irrigation events

Only run this on a fresh database or when you want to reset all data.

## Future Enhancements

Potential additions:
- More varieties per plant type
- Regional varieties (climate-specific)
- Companion planting information
- Pest resistance data
- Photos/images for each variety
- Seasonal planting calendars
- Certified organic/heirloom flags

## Related Files

- [`migrations/seed_plant_varieties.sql`](migrations/seed_plant_varieties.sql) - Seed data script
- [`app/models/plant_variety.py`](app/models/plant_variety.py) - Model definition
- [`app/api/plant_varieties.py`](app/api/plant_varieties.py) - API endpoints

## Summary

✅ **27 plant varieties** loaded and ready to use
✅ Covers **outdoor, indoor, and hydroponic** gardening
✅ Range from **10 days (microgreens)** to **120 days (strawberries)**
✅ Tagged and categorized for easy filtering
✅ Detailed growing notes and requirements included

Users can now immediately start adding plantings with a rich selection of vegetables, herbs, and greens!
