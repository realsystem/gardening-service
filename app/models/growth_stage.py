"""Growth Stage enum for plant lifecycle tracking"""
import enum


class GrowthStage(str, enum.Enum):
    """
    Plant growth stages for nutrient optimization.

    Used to determine appropriate EC/pH levels and nutrient requirements
    based on the plant's current developmental stage.
    """
    SEEDLING = "seedling"       # Early growth, tender roots, low nutrient needs
    VEGETATIVE = "vegetative"   # Rapid leaf/stem growth, medium nutrient needs
    FLOWERING = "flowering"     # Flower development, transitioning nutrient needs
    FRUITING = "fruiting"       # Fruit production, high nutrient needs