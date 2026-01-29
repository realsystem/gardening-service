"""API routers"""
from app.api.users import router as users_router
from app.api.gardens import router as gardens_router
from app.api.plant_varieties import router as plant_varieties_router
from app.api.seed_batches import router as seed_batches_router
from app.api.germination_events import router as germination_events_router
from app.api.planting_events import router as planting_events_router
from app.api.care_tasks import router as care_tasks_router

__all__ = [
    "users_router",
    "gardens_router",
    "plant_varieties_router",
    "seed_batches_router",
    "germination_events_router",
    "planting_events_router",
    "care_tasks_router",
]
