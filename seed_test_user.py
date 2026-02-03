"""Create comprehensive test data for test6@example.com"""
import sys
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import User
from app.models.land import Land
from app.models.garden import Garden
from app.models.tree import Tree
from app.models.structure import Structure
from app.models.planting_event import PlantingEvent, PlantingMethod
from app.models.care_task import CareTask, TaskType, TaskStatus, TaskPriority, TaskSource
from app.models.seed_batch import SeedBatch
from app.models.germination_event import GerminationEvent
from app.models.soil_sample import SoilSample
from app.services.auth_service import AuthService
from app.repositories.plant_variety_repository import PlantVarietyRepository


def create_test_user(db: Session) -> User:
    """Create or get test user"""
    user = db.query(User).filter(User.email == "test6@example.com").first()
    if not user:
        user = User(
            email="test6@example.com",
            username="test6",
            hashed_password=AuthService.hash_password("password123"),
            is_active=True,
            is_admin=False,
            user_group=0  # Free tier
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"✓ Created user: {user.email} (ID: {user.id})")
    else:
        print(f"✓ User exists: {user.email} (ID: {user.id})")
    return user


def create_land(db: Session, user: User) -> Land:
    """Create land plot"""
    land = Land(
        user_id=user.id,
        name="Test Garden Estate",
        width=20,
        height=20
    )
    db.add(land)
    db.commit()
    db.refresh(land)
    print(f"✓ Created land: {land.name} (20x20m)")
    return land


def create_structures(db: Session, user: User, land: Land):
    """Create various structures"""
    structures = [
        Structure(
            user_id=user.id,
            land_id=land.id,
            name="Garden Shed",
            x=1,
            y=1,
            width=5,
            depth=3,
            height=3
        ),
        Structure(
            user_id=user.id,
            land_id=land.id,
            name="Greenhouse",
            x=15,
            y=1,
            width=4,
            depth=3,
            height=3
        ),
        Structure(
            user_id=user.id,
            land_id=land.id,
            name="Compost Bin",
            x=1,
            y=17,
            width=2,
            depth=2,
            height=1.5
        )
    ]
    for structure in structures:
        db.add(structure)
    db.commit()
    print(f"✓ Created {len(structures)} structures: shed, greenhouse, compost bin")


def create_trees(db: Session, user: User, land: Land, variety_repo: PlantVarietyRepository):
    """Create trees"""
    # Get tree varieties
    apple = variety_repo.search_by_name("Apple")
    peach = variety_repo.search_by_name("Peach")
    cherry = variety_repo.search_by_name("Cherry")

    trees = []
    if apple:
        trees.append(Tree(
            user_id=user.id,
            land_id=land.id,
            name="Apple Tree",
            species_id=apple[0].id,
            x=10,
            y=5,
            canopy_radius=2.5,
            height=5
        ))
    if peach:
        trees.append(Tree(
            user_id=user.id,
            land_id=land.id,
            name="Peach Tree",
            species_id=peach[0].id,
            x=5,
            y=10,
            canopy_radius=2,
            height=4
        ))
    if cherry:
        trees.append(Tree(
            user_id=user.id,
            land_id=land.id,
            name="Cherry Tree",
            species_id=cherry[0].id,
            x=15,
            y=10,
            canopy_radius=2,
            height=4.5
        ))

    for tree in trees:
        db.add(tree)
    db.commit()
    print(f"✓ Created {len(trees)} trees: apple, peach, cherry")


def create_gardens(db: Session, user: User, land: Land, variety_repo: PlantVarietyRepository):
    """Create gardens with various plants"""
    # Get plant varieties
    tomato = variety_repo.search_by_name("Tomato")
    lettuce = variety_repo.search_by_name("Lettuce")
    basil = variety_repo.search_by_name("Basil")
    carrot = variety_repo.search_by_name("Carrot")
    cucumber = variety_repo.search_by_name("Cucumber")
    strawberry = variety_repo.search_by_name("Strawberry")

    gardens = [
        {
            "garden": Garden(
                user_id=user.id,
                land_id=land.id,
                name="Vegetable Garden",
                x=7,
                y=7,
                width=5,
                height=4
            ),
            "plants": [
                (tomato, "Tomatoes", 60),
                (lettuce, "Spring Lettuce", 30),
                (carrot, "Carrots", 45)
            ]
        },
        {
            "garden": Garden(
                user_id=user.id,
                land_id=land.id,
                name="Herb Garden",
                x=13,
                y=13,
                width=3,
                height=3
            ),
            "plants": [
                (basil, "Sweet Basil", 25)
            ]
        },
        {
            "garden": Garden(
                user_id=user.id,
                land_id=land.id,
                name="Summer Crops",
                x=7,
                y=13,
                width=4,
                height=5
            ),
            "plants": [
                (cucumber, "Cucumbers", 50),
                (strawberry, "Strawberries", 90)
            ]
        }
    ]

    total_plants = 0
    for garden_data in gardens:
        garden = garden_data["garden"]
        db.add(garden)
        db.commit()
        db.refresh(garden)

        # Add planting events for each plant type in the garden
        for variety_list, plant_name, days_ago in garden_data["plants"]:
            if variety_list:
                variety = variety_list[0]
                planting = PlantingEvent(
                    user_id=user.id,
                    garden_id=garden.id,
                    plant_variety_id=variety.id,
                    plant_count=10,
                    planting_method=PlantingMethod.DIRECT_SOW,
                    planting_date=(datetime.utcnow() - timedelta(days=days_ago)).date(),
                    notes=f"Planted {plant_name} in {garden.name}"
                )
                db.add(planting)
                total_plants += 1

    db.commit()
    print(f"✓ Created {len(gardens)} gardens with {total_plants} planting events")


def create_seed_batches(db: Session, user: User, variety_repo: PlantVarietyRepository):
    """Create seed batches"""
    tomato = variety_repo.search_by_name("Tomato")
    pepper = variety_repo.search_by_name("Pepper")

    batches = []
    if tomato:
        batches.append(SeedBatch(
            user_id=user.id,
            plant_variety_id=tomato[0].id,
            quantity=50,
            source="Local nursery",
            harvest_year=2026,
            notes="Heirloom variety, purchased 120 days ago"
        ))
    if pepper:
        batches.append(SeedBatch(
            user_id=user.id,
            plant_variety_id=pepper[0].id,
            quantity=30,
            source="Online store",
            harvest_year=2026,
            notes="Bell pepper mix, purchased 90 days ago"
        ))

    for batch in batches:
        db.add(batch)
    db.commit()
    print(f"✓ Created {len(batches)} seed batches")

    return batches


def create_germination_events(db: Session, user: User, seed_batches, variety_repo: PlantVarietyRepository):
    """Create germination tracking"""
    events = []
    for batch in seed_batches:
        started_date = (datetime.utcnow() - timedelta(days=30)).date()
        germination_date = (datetime.utcnow() - timedelta(days=23)).date()
        event = GerminationEvent(
            user_id=user.id,
            seed_batch_id=batch.id,
            plant_variety_id=batch.plant_variety_id,
            started_date=started_date,
            seed_count=20,
            germinated=True,
            germination_date=germination_date,
            germination_count=18,
            germination_success_rate=90.0,
            notes="Good germination rate, took 7 days"
        )
        events.append(event)
        db.add(event)

    db.commit()
    print(f"✓ Created {len(events)} germination events")


def create_care_tasks(db: Session, user: User):
    """Create care tasks"""
    plantings = db.query(PlantingEvent).filter(PlantingEvent.user_id == user.id).all()

    tasks = []

    # Planting-level tasks
    if plantings:
        # Water task - high priority
        tasks.append(CareTask(
            user_id=user.id,
            planting_event_id=plantings[0].id,
            task_type=TaskType.WATER,
            task_source=TaskSource.MANUAL,
            title="Water tomatoes",
            description="Water thoroughly in the morning",
            due_date=(datetime.utcnow() + timedelta(days=1)).date(),
            status=TaskStatus.PENDING,
            priority=TaskPriority.HIGH
        ))

        # Fertilize task - medium priority
        tasks.append(CareTask(
            user_id=user.id,
            planting_event_id=plantings[1].id if len(plantings) > 1 else plantings[0].id,
            task_type=TaskType.FERTILIZE,
            task_source=TaskSource.MANUAL,
            title="Fertilize lettuce",
            description="Use organic fertilizer",
            due_date=(datetime.utcnow() + timedelta(days=7)).date(),
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM,
            notes="Apply half-strength liquid fertilizer"
        ))

        # Weed task - medium priority
        tasks.append(CareTask(
            user_id=user.id,
            planting_event_id=plantings[0].id,
            task_type=TaskType.WEED,
            task_source=TaskSource.MANUAL,
            title="Weed vegetable garden",
            due_date=(datetime.utcnow() + timedelta(days=3)).date(),
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM
        ))

        # Completed harvest task
        tasks.append(CareTask(
            user_id=user.id,
            planting_event_id=plantings[0].id,
            task_type=TaskType.HARVEST,
            task_source=TaskSource.MANUAL,
            title="Harvest tomatoes",
            due_date=(datetime.utcnow() - timedelta(days=2)).date(),
            completed_date=(datetime.utcnow() - timedelta(days=1)).date(),
            status=TaskStatus.COMPLETED,
            priority=TaskPriority.HIGH,
            notes="Harvested 5kg of ripe tomatoes"
        ))

    for task in tasks:
        db.add(task)

    db.commit()
    print(f"✓ Created {len(tasks)} care tasks (pending and completed)")


def create_soil_samples(db: Session, user: User):
    """Create soil samples"""
    gardens = db.query(Garden).filter(Garden.user_id == user.id).all()

    samples = []
    for i, garden in enumerate(gardens[:2]):
        sample = SoilSample(
            user_id=user.id,
            garden_id=garden.id,
            date_collected=(datetime.utcnow() - timedelta(days=30 * (i + 1))).date(),
            ph=6.5 + (i * 0.3),
            nitrogen_ppm=45.0,
            phosphorus_ppm=30.0,
            potassium_ppm=150.0,
            organic_matter_percent=4.5,
            notes=f"Soil test for {garden.name}"
        )
        samples.append(sample)
        db.add(sample)

    db.commit()
    print(f"✓ Created {len(samples)} soil samples")


def main():
    print("=" * 60)
    print("Creating comprehensive test data for test6@example.com")
    print("=" * 60)
    print()

    db = SessionLocal()
    try:
        # Create user
        user = create_test_user(db)

        # Create variety repository
        variety_repo = PlantVarietyRepository(db)

        # Create land
        land = create_land(db, user)

        # Create all resources
        create_structures(db, user, land)
        create_trees(db, user, land, variety_repo)
        create_gardens(db, user, land, variety_repo)
        seed_batches = create_seed_batches(db, user, variety_repo)
        create_germination_events(db, user, seed_batches, variety_repo)
        create_care_tasks(db, user)
        create_soil_samples(db, user)

        print()
        print("=" * 60)
        print("✓ Test data creation complete!")
        print("=" * 60)
        print()
        print(f"Login credentials:")
        print(f"  Email: test6@example.com")
        print(f"  Password: password123")
        print()
        print(f"Resources created:")
        print(f"  - 1 land plot (20x20m)")
        print(f"  - 3 structures")
        print(f"  - 3 trees")
        print(f"  - 3 gardens")
        print(f"  - Multiple planting events")
        print(f"  - 2 seed batches")
        print(f"  - 2 germination events")
        print(f"  - Multiple care tasks")
        print(f"  - 2 soil samples")
        print()

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
