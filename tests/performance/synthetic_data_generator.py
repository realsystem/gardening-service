"""Synthetic data generator for performance testing.

Generates realistic test data:
- 100 users
- 1,000 gardens (10 per user average)
- 10,000 planting events (10 per garden average)

Data is representative of real-world usage patterns.
"""
import random
from datetime import date, timedelta
from typing import List
from sqlalchemy.orm import Session
from faker import Faker

from app.models.user import User
from app.models.garden import Garden, GardenType
from app.models.plant_variety import PlantVariety, WaterRequirement
from app.models.planting_event import PlantingEvent, PlantingMethod, PlantHealth
from app.models.care_task import CareTask, TaskType, TaskPriority, TaskSource

faker = Faker()


class SyntheticDataGenerator:
    """Generates synthetic test data for performance testing."""

    def __init__(self, db: Session):
        self.db = db
        self.users: List[User] = []
        self.gardens: List[Garden] = []
        self.plant_varieties: List[PlantVariety] = []
        self.plantings: List[PlantingEvent] = []

    def generate_all(
        self,
        num_users: int = 100,
        num_gardens: int = 1000,
        num_plantings: int = 10000
    ) -> dict:
        """Generate all synthetic data.

        Args:
            num_users: Number of users to create
            num_gardens: Number of gardens to create
            num_plantings: Number of planting events to create

        Returns:
            Dictionary with counts of created entities
        """
        print(f"Generating synthetic data...")
        print(f"  Users: {num_users}")
        print(f"  Gardens: {num_gardens}")
        print(f"  Plantings: {num_plantings}")

        # Create plant varieties first (needed by plantings)
        self._ensure_plant_varieties()

        # Create users
        print("\nCreating users...")
        self._create_users(num_users)

        # Create gardens
        print("Creating gardens...")
        self._create_gardens(num_gardens)

        # Create plantings
        print("Creating plantings...")
        self._create_plantings(num_plantings)

        print("\nData generation complete!")

        return {
            'users': len(self.users),
            'gardens': len(self.gardens),
            'plant_varieties': len(self.plant_varieties),
            'plantings': len(self.plantings),
        }

    def _ensure_plant_varieties(self):
        """Ensure plant varieties exist for testing."""
        # Check if we have plant varieties
        existing = self.db.query(PlantVariety).limit(5).all()

        if len(existing) >= 5:
            self.plant_varieties = existing
            print(f"Using {len(existing)} existing plant varieties")
            return

        # Create common varieties for testing
        varieties_data = [
            {
                'common_name': 'Tomato',
                'scientific_name': 'Solanum lycopersicum',
                'days_to_harvest': 80,
                'water_requirement': WaterRequirement.HIGH,
            },
            {
                'common_name': 'Lettuce',
                'scientific_name': 'Lactuca sativa',
                'days_to_harvest': 45,
                'water_requirement': WaterRequirement.MEDIUM,
            },
            {
                'common_name': 'Carrot',
                'scientific_name': 'Daucus carota',
                'days_to_harvest': 70,
                'water_requirement': WaterRequirement.MEDIUM,
            },
            {
                'common_name': 'Cucumber',
                'scientific_name': 'Cucumis sativus',
                'days_to_harvest': 60,
                'water_requirement': WaterRequirement.HIGH,
            },
            {
                'common_name': 'Pepper',
                'scientific_name': 'Capsicum annuum',
                'days_to_harvest': 75,
                'water_requirement': WaterRequirement.MEDIUM,
            },
            {
                'common_name': 'Basil',
                'scientific_name': 'Ocimum basilicum',
                'days_to_harvest': 30,
                'water_requirement': WaterRequirement.MEDIUM,
            },
            {
                'common_name': 'Spinach',
                'scientific_name': 'Spinacia oleracea',
                'days_to_harvest': 40,
                'water_requirement': WaterRequirement.MEDIUM,
            },
        ]

        for variety_data in varieties_data:
            variety = PlantVariety(**variety_data)
            self.db.add(variety)

        self.db.commit()

        self.plant_varieties = self.db.query(PlantVariety).all()
        print(f"Created {len(self.plant_varieties)} plant varieties")

    def _create_users(self, num_users: int):
        """Create synthetic users."""
        print("Creating users...")

        # Use pre-computed bcrypt hash for "testpass" to avoid bcrypt version issues
        # Generated with: bcrypt.hashpw(b"testpass", bcrypt.gensalt())
        hashed_password = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5eDWpbCp.JLRu"

        for i in range(num_users):
            user = User(
                email=f"perftest_user_{i}@example.com",
                display_name=faker.name(),
                hashed_password=hashed_password,
                is_admin=i == 0,  # First user is admin
            )
            self.db.add(user)
            self.users.append(user)

            # Commit in batches to avoid memory issues
            if (i + 1) % 100 == 0:
                self.db.commit()
                print(f"  Created {i + 1}/{num_users} users")

        self.db.commit()
        print(f"  Created {len(self.users)} users total")

    def _create_gardens(self, num_gardens: int):
        """Create synthetic gardens distributed across users."""
        garden_types = list(GardenType)

        for i in range(num_gardens):
            # Distribute gardens across users (some users have more gardens)
            user = random.choice(self.users)

            garden = Garden(
                user_id=user.id,
                name=f"{faker.word().capitalize()} Garden {i}",
                garden_type=random.choice(garden_types),
                is_hydroponic=random.random() < 0.2,  # 20% hydroponic
            )
            self.db.add(garden)
            self.gardens.append(garden)

            if (i + 1) % 100 == 0:
                self.db.commit()
                print(f"  Created {i + 1}/{num_gardens} gardens")

        self.db.commit()
        print(f"  Created {len(self.gardens)} gardens total")

    def _create_plantings(self, num_plantings: int):
        """Create synthetic planting events distributed across gardens."""
        planting_methods = list(PlantingMethod)
        health_statuses = list(PlantHealth)

        for i in range(num_plantings):
            # Distribute plantings across gardens
            garden = random.choice(self.gardens)
            variety = random.choice(self.plant_varieties)

            # Random planting date within last 120 days
            days_ago = random.randint(0, 120)
            planting_date = date.today() - timedelta(days=days_ago)

            # Random position in garden (for layout testing)
            x = random.uniform(0, 10)  # 10m x 10m garden
            y = random.uniform(0, 10)

            planting = PlantingEvent(
                user_id=garden.user_id,
                garden_id=garden.id,
                plant_variety_id=variety.id,
                planting_date=planting_date,
                planting_method=random.choice(planting_methods),
                plant_count=random.randint(1, 10),
                health_status=random.choice(health_statuses),
                x=x,
                y=y,
                notes=faker.sentence() if random.random() < 0.3 else None,
            )
            self.db.add(planting)
            self.plantings.append(planting)

            if (i + 1) % 1000 == 0:
                self.db.commit()
                print(f"  Created {i + 1}/{num_plantings} plantings")

        self.db.commit()
        print(f"  Created {len(self.plantings)} plantings total")

    def cleanup(self):
        """Delete all generated test data."""
        print("\nCleaning up test data...")

        # Delete in reverse order of creation (respect foreign keys)
        # Care tasks must be deleted before plantings
        deleted_counts = {
            'care_tasks': self.db.query(CareTask).filter(
                CareTask.user_id.in_([u.id for u in self.users])
            ).delete(synchronize_session=False),

            'plantings': self.db.query(PlantingEvent).filter(
                PlantingEvent.user_id.in_([u.id for u in self.users])
            ).delete(synchronize_session=False),

            'gardens': self.db.query(Garden).filter(
                Garden.user_id.in_([u.id for u in self.users])
            ).delete(synchronize_session=False),

            'users': self.db.query(User).filter(
                User.email.like('perftest_user_%@example.com')
            ).delete(synchronize_session=False),
        }

        self.db.commit()

        print(f"Deleted:")
        for entity_type, count in deleted_counts.items():
            print(f"  {entity_type}: {count}")

        return deleted_counts


def generate_synthetic_data(
    db: Session,
    num_users: int = 100,
    num_gardens: int = 1000,
    num_plantings: int = 10000
) -> SyntheticDataGenerator:
    """Generate synthetic data for performance testing.

    Args:
        db: Database session
        num_users: Number of users to create
        num_gardens: Number of gardens to create
        num_plantings: Number of planting events to create

    Returns:
        SyntheticDataGenerator instance (for cleanup)
    """
    generator = SyntheticDataGenerator(db)
    generator.generate_all(num_users, num_gardens, num_plantings)
    return generator
