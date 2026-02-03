"""
Reset test6@example.com with realistic data.

Removes all existing data and creates:
- 2 lands
- 2-3 gardens per land (4-6 total)
- 20-50 plantings per garden (with positions)
- 10-20 soil samples per garden
- A few trees and structures
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
from app.models.soil_sample import SoilSample
from app.models.care_task import CareTask
from app.rules.task_generator import TaskGenerator


def delete_test6_data(db: Session, user: User):
    """Delete all data for test6 user"""
    print("🗑️  Deleting existing test6 data...")

    # Delete in correct order (respecting foreign keys)
    # Care tasks must be deleted before planting events
    db.query(CareTask).filter(CareTask.user_id == user.id).delete()
    db.query(SoilSample).filter(SoilSample.user_id == user.id).delete()
    db.query(Structure).filter(Structure.user_id == user.id).delete()
    db.query(Tree).filter(Tree.user_id == user.id).delete()
    db.query(PlantingEvent).filter(PlantingEvent.user_id == user.id).delete()
    db.query(Garden).filter(Garden.user_id == user.id).delete()
    db.query(Land).filter(Land.user_id == user.id).delete()

    db.commit()
    print("✅ Deleted all existing data")


def create_realistic_data(db: Session, user: User):
    """Create realistic test data"""

    print("\n" + "=" * 80)
    print("CREATING REALISTIC TEST DATA")
    print("=" * 80)

    # Get plant varieties
    varieties = db.query(PlantVariety).filter(PlantVariety.is_tree == False).all()
    print(f"✅ Found {len(varieties)} plant varieties")

    # Create 2 lands
    lands = []
    land_configs = [
        ("Backyard Garden", 20, 15),
        ("Side Yard", 15, 10)
    ]

    for name, width, height in land_configs:
        land = Land(
            user_id=user.id,
            name=name,
            width=width,
            height=height
        )
        db.add(land)
        lands.append(land)

    db.commit()
    print(f"\n✅ Created {len(lands)} lands")

    # Create 2-3 gardens per land
    gardens = []
    garden_types = [
        ("Vegetable Garden", "outdoor"),
        ("Herb Garden", "outdoor"),
        ("Container Garden", "outdoor"),
        ("Raised Beds", "outdoor"),
        ("Greenhouse Plot", "indoor")
    ]

    for land in lands:
        num_gardens = random.randint(2, 3)
        print(f"\n🌱 Creating {num_gardens} gardens for {land.name}")

        for i in range(num_gardens):
            name, garden_type = random.choice(garden_types)
            garden_name = f"{name} {i+1}" if num_gardens > 1 else name

            # Random position on land
            garden_width = random.uniform(3, 5)
            garden_height = random.uniform(3, 5)
            x = random.uniform(0, land.width - garden_width)
            y = random.uniform(0, land.height - garden_height)

            garden = Garden(
                user_id=user.id,
                land_id=land.id,
                name=garden_name,
                garden_type=garden_type,
                location=f"On {land.name}",
                x=round(x, 2),
                y=round(y, 2),
                width=round(garden_width, 2),
                height=round(garden_height, 2)
            )
            db.add(garden)
            gardens.append(garden)

    db.commit()
    print(f"✅ Created {len(gardens)} gardens total")

    # Create 20-50 plantings per garden
    total_plantings = 0
    all_plantings = []  # Track all plantings for task generation

    for garden in gardens:
        num_plantings = random.randint(20, 50)
        print(f"\n🌿 Adding {num_plantings} plantings to {garden.name}")

        for i in range(num_plantings):
            variety = random.choice(varieties)

            # Random position within garden
            x = random.uniform(0.1, garden.width - 0.1)
            y = random.uniform(0.1, garden.height - 0.1)

            # Random planting date (last 90 days)
            days_ago = random.randint(0, 90)
            planting_date = datetime.now().date() - timedelta(days=days_ago)

            # Health status (mostly healthy)
            health = random.choices(
                [PlantHealth.HEALTHY, PlantHealth.STRESSED, PlantHealth.DISEASED],
                weights=[0.8, 0.15, 0.05]
            )[0]

            planting = PlantingEvent(
                user_id=user.id,
                garden_id=garden.id,
                plant_variety_id=variety.id,
                planting_date=planting_date,
                planting_method=random.choice([PlantingMethod.DIRECT_SOW, PlantingMethod.TRANSPLANT]),
                plant_count=random.randint(1, 3),
                x=round(x, 2),
                y=round(y, 2),
                health_status=health,
                location_in_garden=f"Section {random.randint(1, 4)}"
            )
            db.add(planting)
            all_plantings.append(planting)
            total_plantings += 1

            # Commit in batches
            if total_plantings % 50 == 0:
                db.commit()

    db.commit()
    print(f"\n✅ Created {total_plantings} plantings total")

    # Create 10-20 soil samples per garden
    total_samples = 0

    for garden in gardens:
        num_samples = random.randint(10, 20)
        print(f"\n🧪 Adding {num_samples} soil samples to {garden.name}")

        for i in range(num_samples):
            # Random sample date (last 180 days)
            days_ago = random.randint(0, 180)
            sample_date = datetime.now().date() - timedelta(days=days_ago)

            # Realistic soil values
            ph_value = round(random.uniform(5.5, 7.5), 1)
            nitrogen = round(random.uniform(10, 50), 1)
            phosphorus = round(random.uniform(5, 30), 1)
            potassium = round(random.uniform(10, 40), 1)

            sample = SoilSample(
                user_id=user.id,
                garden_id=garden.id,
                date_collected=sample_date,
                ph=ph_value,
                nitrogen_ppm=nitrogen,
                phosphorus_ppm=phosphorus,
                potassium_ppm=potassium,
                notes=f"Regular soil test {i+1}"
            )
            db.add(sample)
            total_samples += 1

    db.commit()
    print(f"\n✅ Created {total_samples} soil samples total")

    # Add a few trees to lands
    total_trees = 0
    tree_species = [
        ("Apple", 15, 12),
        ("Cherry", 20, 15),
        ("Lemon", 15, 10)
    ]

    for land in lands:
        num_trees = random.randint(2, 4)
        print(f"\n🌳 Adding {num_trees} trees to {land.name}")

        for i in range(num_trees):
            species_name, height, canopy = random.choice(tree_species)

            # Find tree variety
            tree_variety = db.query(PlantVariety).filter(
                PlantVariety.common_name == species_name,
                PlantVariety.is_tree == True
            ).first()

            if not tree_variety:
                tree_variety = db.query(PlantVariety).filter(
                    PlantVariety.is_tree == True
                ).first()

            if tree_variety:
                # Random position with margins
                margin = 2.0
                x = random.uniform(margin, land.width - margin)
                y = random.uniform(margin, land.height - margin)

                tree = Tree(
                    user_id=user.id,
                    land_id=land.id,
                    name=f"{tree_variety.common_name} {i+1}",
                    species_id=tree_variety.id,
                    x=round(x, 2),
                    y=round(y, 2),
                    height=round(height + random.uniform(-2, 2), 1),
                    canopy_radius=round((canopy + random.uniform(-1, 1)) * 0.3048, 2)
                )
                db.add(tree)
                total_trees += 1

    db.commit()
    print(f"\n✅ Created {total_trees} trees total")

    # Add a few structures
    total_structures = 0
    structure_types = [
        ("Tool Shed", 2.0, 2.0),
        ("Compost Bin", 1.5, 1.5),
        ("Water Tank", 2.0, 2.0)
    ]

    for land in lands:
        num_structures = random.randint(1, 3)
        print(f"\n🏗️  Adding {num_structures} structures to {land.name}")

        for i in range(num_structures):
            struct_name, width, depth = random.choice(structure_types)

            # Random position
            margin = 1.0
            x = random.uniform(margin, land.width - width - margin)
            y = random.uniform(margin, land.height - depth - margin)

            structure = Structure(
                user_id=user.id,
                land_id=land.id,
                name=f"{struct_name} {i+1}",
                x=round(x, 2),
                y=round(y, 2),
                width=width,
                depth=depth,
                height=round(random.uniform(2.0, 4.0), 1)
            )
            db.add(structure)
            total_structures += 1

    db.commit()
    print(f"\n✅ Created {total_structures} structures total")

    # Generate tasks for all plantings
    print("\n" + "=" * 80)
    print("GENERATING AUTO TASKS")
    print("=" * 80)

    task_generator = TaskGenerator()
    total_tasks = 0
    tasks_by_type = {}

    for planting in all_plantings:
        try:
            # Need to refresh planting from DB to load relationships
            db.refresh(planting)
            tasks = task_generator.generate_tasks_for_planting(db, planting, user.id)
            total_tasks += len(tasks)

            # Count by type
            for task in tasks:
                task_type = task.task_type.value
                tasks_by_type[task_type] = tasks_by_type.get(task_type, 0) + 1
        except Exception as e:
            print(f"⚠️  Failed to generate tasks for planting {planting.id}: {e}")
            continue

    print(f"\n✅ Generated {total_tasks} tasks")
    if tasks_by_type:
        print("\nTasks by type:")
        for task_type, count in sorted(tasks_by_type.items()):
            print(f"  - {task_type}: {count}")

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"✅ Lands: {len(lands)}")
    print(f"✅ Gardens: {len(gardens)}")
    print(f"✅ Plantings: {total_plantings}")
    print(f"✅ Soil Samples: {total_samples}")
    print(f"✅ Trees: {total_trees}")
    print(f"✅ Structures: {total_structures}")
    print(f"✅ Tasks: {total_tasks}")
    print(f"✅ Total objects: {total_plantings + total_samples + total_trees + total_structures + total_tasks}")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        # Get test6 user
        user = db.query(User).filter(User.email == "test6@example.com").first()

        if not user:
            print("❌ User test6@example.com not found")
            sys.exit(1)

        print(f"✅ Found user: {user.email} (ID: {user.id})")

        # Delete existing data
        delete_test6_data(db, user)

        # Create realistic data
        create_realistic_data(db, user)

        print("\n✅ Reset completed successfully!")

    except Exception as e:
        print(f"\n❌ Error during reset: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()
