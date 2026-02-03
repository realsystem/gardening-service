"""
Populate large dataset for test6@example.com user.

Creates:
- 100-150 plantings per garden (with positions)
- 5-10 trees per land
- Multiple small structures per land
"""
import sys
import os
import random
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import User
from app.models.garden import Garden
from app.models.land import Land
from app.models.planting_event import PlantingEvent, PlantingMethod, PlantHealth
from app.models.plant_variety import PlantVariety
from app.models.tree import Tree
from app.models.structure import Structure

# Tree species data (common_name: (height_ft, canopy_radius_ft))
TREE_SPECIES = [
    ("Apple", 15, 12),
    ("Pear", 20, 10),
    ("Cherry", 25, 15),
    ("Plum", 15, 10),
    ("Peach", 15, 12),
    ("Apricot", 15, 10),
    ("Fig", 12, 12),
    ("Orange", 20, 15),
    ("Lemon", 15, 12),
    ("Avocado", 30, 25),
]

# Structure types
STRUCTURE_TYPES = [
    ("Shed", 3.0, 4.0),
    ("Greenhouse", 4.0, 6.0),
    ("Compost Bin", 1.5, 1.5),
    ("Tool Storage", 2.0, 2.0),
    ("Garden Bench", 1.5, 0.5),
    ("Raised Bed Frame", 2.0, 1.0),
    ("Water Tank", 2.0, 2.0),
    ("Chicken Coop", 3.0, 3.0),
]


def seed_large_dataset(db: Session):
    """Create large dataset for test6@example.com"""

    # Get user
    user = db.query(User).filter(User.email == "test6@example.com").first()
    if not user:
        print("❌ User test6@example.com not found")
        return

    print(f"✅ Found user: {user.email} (ID: {user.id})")

    # Get all plant varieties for random selection
    varieties = db.query(PlantVariety).filter(PlantVariety.is_tree == False).all()
    print(f"✅ Found {len(varieties)} plant varieties")

    # Get user's gardens
    gardens = db.query(Garden).filter(Garden.user_id == user.id).all()
    print(f"✅ Found {len(gardens)} gardens for this user")

    if not gardens:
        print("❌ No gardens found - create gardens first")
        return

    # Get user's lands
    lands = db.query(Land).filter(Land.user_id == user.id).all()
    print(f"✅ Found {len(lands)} lands for this user")

    print("\n" + "=" * 80)
    print("ADDING PLANTINGS TO GARDENS")
    print("=" * 80)

    total_plantings = 0

    for garden in gardens:
        # Determine number of plantings for this garden (100-150)
        num_plantings = random.randint(100, 150)

        print(f"\n🌱 Garden: {garden.name} (ID: {garden.id})")
        print(f"   Adding {num_plantings} plantings...")

        # Calculate grid layout based on garden dimensions
        garden_width = garden.width or 5.0
        garden_height = garden.height or 5.0

        # Calculate spacing for plantings
        cols = int((garden_width / 0.3) + 1)  # ~30cm spacing
        rows = int((garden_height / 0.3) + 1)

        added = 0
        for i in range(num_plantings):
            # Random position within garden bounds with some clustering
            x = random.uniform(0.1, garden_width - 0.1)
            y = random.uniform(0.1, garden_height - 0.1)

            # Random variety
            variety = random.choice(varieties)

            # Random planting date (last 60 days)
            days_ago = random.randint(0, 60)
            planting_date = datetime.now().date() - timedelta(days=days_ago)

            # Random health status (mostly healthy)
            health_weights = [0.7, 0.2, 0.1]  # healthy, stressed, diseased
            health = random.choices(
                [PlantHealth.HEALTHY, PlantHealth.STRESSED, PlantHealth.DISEASED],
                weights=health_weights
            )[0]

            planting = PlantingEvent(
                user_id=user.id,
                garden_id=garden.id,
                plant_variety_id=variety.id,
                planting_date=planting_date,
                planting_method=PlantingMethod.DIRECT_SOW if random.random() > 0.3 else PlantingMethod.TRANSPLANT,
                plant_count=random.randint(1, 5),
                x=round(x, 2),
                y=round(y, 2),
                health_status=health,
                notes=f"Auto-generated planting {i+1}"
            )

            db.add(planting)
            added += 1

            # Commit in batches of 50 for performance
            if added % 50 == 0:
                db.commit()
                print(f"   ✓ Added {added}/{num_plantings} plantings...")

        db.commit()
        print(f"   ✅ Completed: {added} plantings added to {garden.name}")
        total_plantings += added

    print(f"\n✅ Total plantings added: {total_plantings}")

    # Add trees to lands
    print("\n" + "=" * 80)
    print("ADDING TREES TO LANDS")
    print("=" * 80)

    total_trees = 0

    for land in lands:
        # Add 5-10 trees per land
        num_trees = random.randint(5, 10)

        print(f"\n🌳 Land: {land.name} (ID: {land.id})")
        print(f"   Dimensions: {land.width}m × {land.height}m")
        print(f"   Adding {num_trees} trees...")

        added = 0
        for i in range(num_trees):
            # Random tree species
            species_name, height, canopy = random.choice(TREE_SPECIES)

            # Find variety for this species
            tree_variety = db.query(PlantVariety).filter(
                PlantVariety.common_name == species_name,
                PlantVariety.is_tree == True
            ).first()

            if not tree_variety:
                # Try to find any tree variety as fallback
                tree_variety = db.query(PlantVariety).filter(
                    PlantVariety.is_tree == True
                ).first()

                if not tree_variety:
                    print(f"   ⚠️  No tree varieties found in database")
                    continue

            # Random position within land bounds (avoid edges)
            margin = max(canopy * 0.3048, 2.0)  # Convert ft to m and add margin
            x = random.uniform(margin, land.width - margin)
            y = random.uniform(margin, land.height - margin)

            tree = Tree(
                user_id=user.id,
                land_id=land.id,
                name=f"{tree_variety.common_name} {i+1}",
                species_id=tree_variety.id,
                x=round(x, 2),
                y=round(y, 2),
                height=round(height + random.uniform(-2, 2), 1),  # Slight variation (in feet)
                canopy_radius=round((canopy + random.uniform(-1, 1)) * 0.3048, 2)  # Convert ft to m
            )

            db.add(tree)
            added += 1

        db.commit()
        print(f"   ✅ Added {added} trees to {land.name}")
        total_trees += added

    print(f"\n✅ Total trees added: {total_trees}")

    # Add structures to lands
    print("\n" + "=" * 80)
    print("ADDING STRUCTURES TO LANDS")
    print("=" * 80)

    total_structures = 0

    for land in lands:
        # Add 3-8 structures per land
        num_structures = random.randint(3, 8)

        print(f"\n🏗️  Land: {land.name} (ID: {land.id})")
        print(f"   Adding {num_structures} structures...")

        added = 0
        for i in range(num_structures):
            # Random structure type
            struct_name, width, depth = random.choice(STRUCTURE_TYPES)

            # Random position within land bounds
            margin = 1.0
            x = random.uniform(margin, land.width - width - margin)
            y = random.uniform(margin, land.height - depth - margin)

            # Random vertical height for shadow calculation (2-5m)
            vertical_height = round(random.uniform(2.0, 5.0), 1)

            structure = Structure(
                user_id=user.id,
                land_id=land.id,
                name=f"{struct_name} {i+1}",
                x=round(x, 2),
                y=round(y, 2),
                width=width,
                depth=depth,
                height=vertical_height
            )

            db.add(structure)
            added += 1

        db.commit()
        print(f"   ✅ Added {added} structures to {land.name}")
        total_structures += added

    print(f"\n✅ Total structures added: {total_structures}")

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"✅ Plantings added: {total_plantings}")
    print(f"✅ Trees added: {total_trees}")
    print(f"✅ Structures added: {total_structures}")
    print(f"✅ Total objects created: {total_plantings + total_trees + total_structures}")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_large_dataset(db)
        print("\n✅ Seeding completed successfully!")
    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()
