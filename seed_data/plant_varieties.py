"""
Seed data for plant varieties.
Run this script to populate the database with common plant varieties.

Usage:
    python -m seed_data.plant_varieties
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.plant_variety import PlantVariety, SunRequirement, WaterRequirement


def create_plant_varieties():
    """Create common plant varieties in the database"""
    db = SessionLocal()

    try:
        # Check if data already exists
        existing = db.query(PlantVariety).first()
        if existing:
            print("Plant varieties already exist. Skipping seed data.")
            return

        varieties = [
            # Tomatoes
            PlantVariety(
                common_name="Tomato - Beefsteak",
                scientific_name="Solanum lycopersicum",
                variety_name="Beefsteak",
                days_to_germination_min=5,
                days_to_germination_max=10,
                days_to_harvest=80,
                spacing_inches=24,
                row_spacing_inches=36,
                sun_requirement=SunRequirement.FULL_SUN,
                water_requirement=WaterRequirement.MEDIUM,
                description="Large, meaty tomatoes perfect for slicing",
                growing_notes="Requires staking or caging. Indeterminate variety."
            ),
            PlantVariety(
                common_name="Tomato - Cherry",
                scientific_name="Solanum lycopersicum",
                variety_name="Cherry",
                days_to_germination_min=5,
                days_to_germination_max=10,
                days_to_harvest=65,
                spacing_inches=24,
                row_spacing_inches=36,
                sun_requirement=SunRequirement.FULL_SUN,
                water_requirement=WaterRequirement.MEDIUM,
                description="Small, sweet tomatoes great for snacking",
                growing_notes="Very productive. Often indeterminate."
            ),
            # Peppers
            PlantVariety(
                common_name="Pepper - Bell",
                scientific_name="Capsicum annuum",
                variety_name="Bell",
                days_to_germination_min=7,
                days_to_germination_max=14,
                days_to_harvest=75,
                spacing_inches=18,
                row_spacing_inches=24,
                sun_requirement=SunRequirement.FULL_SUN,
                water_requirement=WaterRequirement.MEDIUM,
                description="Sweet bell peppers in various colors",
                growing_notes="Harvest green or wait for color change"
            ),
            PlantVariety(
                common_name="Pepper - Jalapeño",
                scientific_name="Capsicum annuum",
                variety_name="Jalapeño",
                days_to_germination_min=7,
                days_to_germination_max=14,
                days_to_harvest=70,
                spacing_inches=14,
                row_spacing_inches=24,
                sun_requirement=SunRequirement.FULL_SUN,
                water_requirement=WaterRequirement.MEDIUM,
                description="Medium-heat chili pepper",
                growing_notes="Harvest while green or let ripen to red"
            ),
            # Lettuce
            PlantVariety(
                common_name="Lettuce - Romaine",
                scientific_name="Lactuca sativa",
                variety_name="Romaine",
                days_to_germination_min=2,
                days_to_germination_max=7,
                days_to_harvest=60,
                spacing_inches=8,
                row_spacing_inches=12,
                sun_requirement=SunRequirement.PARTIAL_SUN,
                water_requirement=WaterRequirement.HIGH,
                description="Crisp, upright lettuce",
                growing_notes="Cool season crop. Harvest before bolting."
            ),
            PlantVariety(
                common_name="Lettuce - Leaf",
                scientific_name="Lactuca sativa",
                variety_name="Leaf",
                days_to_germination_min=2,
                days_to_germination_max=7,
                days_to_harvest=45,
                spacing_inches=6,
                row_spacing_inches=12,
                sun_requirement=SunRequirement.PARTIAL_SUN,
                water_requirement=WaterRequirement.HIGH,
                description="Loose-leaf lettuce for cut-and-come-again",
                growing_notes="Can harvest outer leaves continuously"
            ),
            # Cucumbers
            PlantVariety(
                common_name="Cucumber - Slicing",
                scientific_name="Cucumis sativus",
                variety_name="Slicing",
                days_to_germination_min=3,
                days_to_germination_max=10,
                days_to_harvest=55,
                spacing_inches=12,
                row_spacing_inches=60,
                sun_requirement=SunRequirement.FULL_SUN,
                water_requirement=WaterRequirement.HIGH,
                description="Fresh eating cucumbers",
                growing_notes="Provide trellis for vertical growing"
            ),
            # Carrots
            PlantVariety(
                common_name="Carrot - Nantes",
                scientific_name="Daucus carota",
                variety_name="Nantes",
                days_to_germination_min=10,
                days_to_germination_max=21,
                days_to_harvest=70,
                spacing_inches=2,
                row_spacing_inches=12,
                sun_requirement=SunRequirement.FULL_SUN,
                water_requirement=WaterRequirement.MEDIUM,
                description="Sweet, cylindrical carrots",
                growing_notes="Direct sow, thin seedlings. Needs loose soil."
            ),
            # Beans
            PlantVariety(
                common_name="Bean - Green Bush",
                scientific_name="Phaseolus vulgaris",
                variety_name="Bush",
                days_to_germination_min=5,
                days_to_germination_max=10,
                days_to_harvest=50,
                spacing_inches=4,
                row_spacing_inches=18,
                sun_requirement=SunRequirement.FULL_SUN,
                water_requirement=WaterRequirement.MEDIUM,
                description="Compact bush bean plants",
                growing_notes="Direct sow after frost. Pick regularly."
            ),
            # Zucchini
            PlantVariety(
                common_name="Zucchini",
                scientific_name="Cucurbita pepo",
                variety_name="Summer Squash",
                days_to_germination_min=3,
                days_to_germination_max=7,
                days_to_harvest=45,
                spacing_inches=24,
                row_spacing_inches=36,
                sun_requirement=SunRequirement.FULL_SUN,
                water_requirement=WaterRequirement.MEDIUM,
                description="Prolific summer squash",
                growing_notes="Very productive. Harvest when 6-8 inches."
            ),
            # Basil
            PlantVariety(
                common_name="Basil - Sweet",
                scientific_name="Ocimum basilicum",
                variety_name="Sweet Basil",
                days_to_germination_min=5,
                days_to_germination_max=10,
                days_to_harvest=60,
                spacing_inches=10,
                row_spacing_inches=12,
                sun_requirement=SunRequirement.FULL_SUN,
                water_requirement=WaterRequirement.MEDIUM,
                description="Classic Italian herb",
                growing_notes="Pinch flowers to promote leaf growth"
            ),
            # Radish
            PlantVariety(
                common_name="Radish - Cherry Belle",
                scientific_name="Raphanus sativus",
                variety_name="Cherry Belle",
                days_to_germination_min=3,
                days_to_germination_max=7,
                days_to_harvest=25,
                spacing_inches=2,
                row_spacing_inches=6,
                sun_requirement=SunRequirement.FULL_SUN,
                water_requirement=WaterRequirement.MEDIUM,
                description="Fast-growing red radishes",
                growing_notes="Quick crop, great for beginners"
            ),
            # Spinach
            PlantVariety(
                common_name="Spinach",
                scientific_name="Spinacia oleracea",
                variety_name="Space",
                days_to_germination_min=5,
                days_to_germination_max=14,
                days_to_harvest=40,
                spacing_inches=3,
                row_spacing_inches=12,
                sun_requirement=SunRequirement.PARTIAL_SUN,
                water_requirement=WaterRequirement.MEDIUM,
                description="Nutritious leafy green",
                growing_notes="Cool season crop. Bolts in heat."
            ),
            # Kale
            PlantVariety(
                common_name="Kale - Curly",
                scientific_name="Brassica oleracea",
                variety_name="Curly Kale",
                days_to_germination_min=5,
                days_to_germination_max=10,
                days_to_harvest=55,
                spacing_inches=12,
                row_spacing_inches=18,
                sun_requirement=SunRequirement.FULL_SUN,
                water_requirement=WaterRequirement.MEDIUM,
                description="Hardy, nutritious green",
                growing_notes="Frost tolerant. Sweeter after frost."
            ),
        ]

        # Add all varieties to database
        for variety in varieties:
            db.add(variety)

        db.commit()
        print(f"Successfully created {len(varieties)} plant varieties!")

    except Exception as e:
        print(f"Error creating plant varieties: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_plant_varieties()
