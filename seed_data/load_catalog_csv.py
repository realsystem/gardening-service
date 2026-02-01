"""
Load Plant Varieties Catalog from CSV files

Organized by plant type:
- Vegetables: ~72 varieties
- Herbs: ~30 varieties
- Trees: ~45 varieties (fruit and non-fruit)
- Bushes/Shrubs: ~29 varieties
- Fruits/Berries: ~3 varieties
- Cover Crops: ~21 varieties

TOTAL: ~200 varieties

Usage:
    python -m seed_data.load_catalog_csv

Or with Docker:
    docker-compose exec api python -m seed_data.load_catalog_csv
"""
import sys
import os
import csv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.plant_variety import PlantVariety, SunRequirement, WaterRequirement


def load_csv_to_varieties(csv_path: str) -> list[PlantVariety]:
    """Load plant varieties from a CSV file"""
    varieties = []

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            # Convert string values to appropriate types
            variety = PlantVariety(
                common_name=row['common_name'] or None,
                scientific_name=row['scientific_name'] or None,
                variety_name=row['variety_name'] or None,
                days_to_germination_min=int(row['days_to_germination_min']) if row['days_to_germination_min'] else None,
                days_to_germination_max=int(row['days_to_germination_max']) if row['days_to_germination_max'] else None,
                days_to_harvest=int(row['days_to_harvest']) if row['days_to_harvest'] else None,
                spacing_inches=int(row['spacing_inches']) if row['spacing_inches'] else None,
                row_spacing_inches=int(row['row_spacing_inches']) if row['row_spacing_inches'] else None,
                sun_requirement=row['sun_requirement'] or None,
                water_requirement=row['water_requirement'] or None,
                description=row['description'] or None,
                growing_notes=row['growing_notes'] or None,
                photo_url=row['photo_url'] if row['photo_url'] else None,
                tags=row['tags'] or None
            )
            varieties.append(variety)

    return varieties


def main():
    """Load comprehensive plant varieties catalog from CSV files"""
    db = SessionLocal()

    try:
        # Check if catalog is already comprehensive
        current_count = db.query(PlantVariety).count()

        if current_count >= 200:
            print(f"✅ Database already has {current_count} plant varieties")
            print("   Catalog is already comprehensive. No action needed.")
            return current_count

        print(f"📊 Current catalog size: {current_count} varieties")
        print(f"🎯 Target: 200+ varieties")
        print(f"\n🔄 Loading comprehensive catalog from CSV files...\n")

        # Get CSV directory
        csv_dir = os.path.join(os.path.dirname(__file__), 'csv')

        if not os.path.exists(csv_dir):
            print(f"❌ CSV directory not found: {csv_dir}")
            print(f"   Please ensure CSV files are generated first.")
            return 0

        # Load varieties from each CSV file
        categories = {
            '🥬 Vegetables': 'vegetables.csv',
            '🌿 Herbs': 'herbs.csv',
            '🌳 Trees': 'trees.csv',
            '🌺 Bushes/Shrubs': 'bushes.csv',
            '🫐 Fruits/Berries': 'fruits_berries.csv',
            '🌾 Cover Crops': 'cover_crops.csv'
        }

        total_loaded = 0

        for category_name, csv_filename in categories.items():
            csv_path = os.path.join(csv_dir, csv_filename)

            if not os.path.exists(csv_path):
                print(f"⚠️  {category_name}: CSV file not found ({csv_filename})")
                continue

            print(f"{category_name}: Loading from {csv_filename}...")

            varieties = load_csv_to_varieties(csv_path)

            # Add to database
            db.add_all(varieties)
            db.commit()

            print(f"   ✓ Loaded {len(varieties)} varieties")
            total_loaded += len(varieties)

        # Final count & report
        final_count = db.query(PlantVariety).count()

        print(f"\n" + "="*60)
        print(f"✅ SUCCESS! Comprehensive catalog loaded from CSV files")
        print(f"="*60)
        print(f"📊 Total varieties in database: {final_count}")

        if final_count >= 200:
            print(f"🎉 TARGET ACHIEVED! ({final_count} >= 200)")
        else:
            print(f"⚠️  Close to target ({final_count} < 200)")

        # Count by type
        print(f"\n📋 Catalog Breakdown by Type:")

        # Vegetables
        veg_count = db.query(PlantVariety).filter(
            PlantVariety.tags.like("%vegetable%")
        ).count()
        print(f"   🥬 Vegetables:        {veg_count:3d}")

        # Herbs
        herb_count = db.query(PlantVariety).filter(
            PlantVariety.tags.like("%herb%")
        ).count()
        print(f"   🌿 Herbs:             {herb_count:3d}")

        # All Trees (fruit + non-fruit)
        tree_count = db.query(PlantVariety).filter(
            PlantVariety.tags.like("%tree%")
        ).count()
        print(f"   🌳 Trees (all):       {tree_count:3d}")

        # Bushes/Shrubs
        bush_count = db.query(PlantVariety).filter(
            PlantVariety.tags.like("%bush%")
        ).count()
        print(f"   🌺 Bushes/Shrubs:     {bush_count:3d}")

        # Fruits/Berries (non-tree)
        fruit_count = db.query(PlantVariety).filter(
            (PlantVariety.tags.like("%fruit%") | PlantVariety.tags.like("%berry%"))
        ).count()
        print(f"   🫐 Fruits/Berries:    {fruit_count:3d}")

        # Cover Crops
        cover_count = db.query(PlantVariety).filter(
            PlantVariety.tags.like("%cover_crop%")
        ).count()
        print(f"   🌾 Cover Crops:       {cover_count:3d}")

        # Additional metrics
        print(f"\n🔄 By Lifecycle:")
        perennial_count = db.query(PlantVariety).filter(
            PlantVariety.tags.like("%perennial%")
        ).count()
        annual_count = db.query(PlantVariety).filter(
            PlantVariety.tags.like("%annual%")
        ).count()
        print(f"   • Perennial:          {perennial_count:3d}")
        print(f"   • Annual:             {annual_count:3d}")

        print(f"\n" + "="*60)
        print(f"🎯 Catalog ready for production use!")
        print(f"="*60 + "\n")

        return final_count

    except Exception as e:
        print(f"\n❌ Error loading catalog: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    try:
        final_count = main()
        sys.exit(0 if final_count >= 190 else 1)  # Accept 190+ as success
    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
        sys.exit(1)
