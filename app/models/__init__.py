"""Database models"""
from app.models.user import User
from app.models.garden import Garden
from app.models.land import Land
from app.models.plant_variety import PlantVariety
from app.models.seed_batch import SeedBatch
from app.models.germination_event import GerminationEvent
from app.models.planting_event import PlantingEvent
from app.models.care_task import CareTask
# SensorReading removed in Phase 6 of platform simplification
from app.models.soil_sample import SoilSample
from app.models.password_reset_token import PasswordResetToken
from app.models.tree import Tree
from app.models.structure import Structure
from app.models.companion_relationship import CompanionRelationship

__all__ = [
    "User",
    "Garden",
    "Land",
    "PlantVariety",
    "SeedBatch",
    "GerminationEvent",
    "PlantingEvent",
    "CareTask",
    # "SensorReading",  # Removed in Phase 6 of platform simplification
    "SoilSample",
    "PasswordResetToken",
    "Tree",
    "Structure",
    "CompanionRelationship",
]
