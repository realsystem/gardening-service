"""API routers"""
from app.api.users import router as users_router
from app.api.gardens import router as gardens_router
from app.api.plant_varieties import router as plant_varieties_router
from app.api.seed_batches import router as seed_batches_router
from app.api.germination_events import router as germination_events_router
from app.api.planting_events import router as planting_events_router
from app.api.care_tasks import router as care_tasks_router
from app.api.sensor_readings import router as sensor_readings_router
from app.api.soil_samples import router as soil_samples_router
from app.api.irrigation import router as irrigation_router
from app.api.password_reset import router as password_reset_router, password_router

__all__ = [
    "users_router",
    "gardens_router",
    "plant_varieties_router",
    "seed_batches_router",
    "germination_events_router",
    "planting_events_router",
    "care_tasks_router",
    "sensor_readings_router",
    "soil_samples_router",
    "irrigation_router",
    "password_reset_router",
    "password_router",
]
