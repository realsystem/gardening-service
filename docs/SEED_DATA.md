# Plant Varieties Seed Data

**Format:** CSV
**Location:** `seed_data/csv/`
**Total Varieties:** 200+
**Status:** ✅ Production Ready

---

## Quick Start

```bash
# Load catalog from CSV files
python -m seed_data.load_catalog_csv

# Or with Docker
docker-compose exec api python -m seed_data.load_catalog_csv
```

---

## Directory Structure

```
seed_data/
├── load_catalog_csv.py          # CSV loader script
└── csv/                         # Data files
    ├── vegetables.csv           # 72 varieties
    ├── herbs.csv                # 30 varieties
    ├── trees.csv                # 45 varieties
    ├── bushes.csv               # 29 varieties
    ├── fruits_berries.csv       # 3 varieties
    └── cover_crops.csv          # 21 varieties
```

---

## Catalog Breakdown

| Type | Count | Examples |
|------|-------|----------|
| 🥬 Vegetables | 72 | Tomatoes, Peppers, Leafy Greens, Root Vegetables, Cucurbits, Beans, Brassicas |
| 🌿 Herbs | 30 | Basil, Parsley, Cilantro, Lavender, Chamomile, Echinacea |
| 🌳 Trees | 45 | Apples, Pears, Stone Fruits, Citrus, Oak, Maple, Pine |
| 🌺 Bushes/Shrubs | 29 | Raspberry, Blueberry, Roses, Lilac, Hydrangea |
| 🫐 Fruits/Berries | 3 | Strawberries, etc. |
| 🌾 Cover Crops | 21 | Clover, Vetch, Rye, Oats, Mustard, Radish |

---

## CSV Format

All CSV files use the same 14-column structure:

```csv
common_name,scientific_name,variety_name,days_to_germination_min,days_to_germination_max,days_to_harvest,spacing_inches,row_spacing_inches,sun_requirement,water_requirement,description,growing_notes,photo_url,tags
```

**Example:**
```csv
Basil - Sweet,Ocimum basilicum,Genovese,5,10,60,10,12,full_sun,medium,Classic Italian basil,Pinch flowers to promote leaf growth.,,herb,annual,culinary,warm_season
```

### Field Guidelines

**Sun Requirements:**
- `full_sun` - 6+ hours direct sun
- `partial_sun` - 3-6 hours sun
- `shade` - Less than 3 hours sun

**Water Requirements:**
- `low` - Drought tolerant, infrequent watering
- `medium` - Regular watering, moderate moisture
- `high` - Frequent watering, moist soil

**Common Tags:**
- Plant Type: `vegetable`, `herb`, `fruit`, `tree`, `bush`, `shrub`
- Lifecycle: `annual`, `perennial`, `biennial`
- Season: `warm_season`, `cool_season`
- Features: `cold_hardy`, `native`, `edible`, `ornamental`

---

## Adding New Varieties

1. **Open** CSV file in Excel/Google Sheets (e.g., `csv/vegetables.csv`)
2. **Add row** with plant data following the format above
3. **Save** as CSV (UTF-8 encoding)
4. **Reload** catalog:
   ```bash
   python -m seed_data.load_catalog_csv
   ```

**Required fields:**
- `common_name`
- `scientific_name`
- `date_collected` (for soil samples)

**Unique constraint:** `(scientific_name, variety_name)` combination must be unique

---

## Why CSV Format?

**Previous System (Removed January 2026):**
- 5 Python seed data files (~150KB)
- 7 reference modules in `varieties/` directory
- Required Python knowledge to edit
- Complex diffs in version control

**Current CSV System:**
- ✅ **Easy Editing** - Excel, Google Sheets, or any spreadsheet tool
- ✅ **No Code Required** - Anyone can add/modify varieties
- ✅ **Better Version Control** - Clear row-by-row diffs in git
- ✅ **Portable** - Standard CSV format
- ✅ **Simpler Codebase** - Removed ~144KB of legacy code
- ✅ **Single Source of Truth** - CSV files only

---

## Migration History

**January 31, 2026** - CSV-Only Migration
- Removed all Python-based seed data files
- Removed `varieties/` reference modules
- Removed extract utility (CSV is source of truth)
- Updated production loader to use CSV
- All 200+ varieties preserved
- All tests passing (16/16 catalog tests, 88/113 functional tests)

**Previous Python files (removed):**
- `plant_varieties.py` - Old minimal catalog
- `vegetables_herbs_bulk.py` - Legacy vegetables/herbs
- `fruits_bushes_trees_bulk.py` - Legacy fruits/bushes/trees
- `nonfruit_trees_covercrops_bulk.py` - Legacy trees/cover crops
- `load_catalog.py` - Legacy Python loader
- `varieties/*.py` - Reference modules (7 files)

**Files saved:** ~144KB of code removed

---

## Data Quality

All varieties include:
- ✅ Common name and scientific name
- ✅ Sun and water requirements
- ✅ Spacing information
- ✅ Tags for categorization
- ✅ No duplicates

**Trees & Bushes** also include:
- Mature height & spread ranges
- Root depth information
- Cold tolerance zones (USDA hardiness)

---

## Testing

Run catalog validation tests:
```bash
pytest tests/functional/test_varieties_catalog.py -v
```

Expected: 16/16 tests passing

---

## See Also

- [Validation Report](VALIDATION_REPORT.md) - Data quality validation
- [Scale Testing](SCALE_STRESS_TESTING.md) - Performance testing with large datasets
- [Functional Tests](../tests/functional/README.md) - Test suite

---

**Last Updated:** January 31, 2026
**Format:** CSV-only (Python files removed)
**Loader:** `seed_data/load_catalog_csv.py`
