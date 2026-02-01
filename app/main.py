"""Main FastAPI application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError, HTTPException

from app.config import get_settings
from app.api import (
    users_router,
    gardens_router,
    lands_router,
    plant_varieties_router,
    seed_batches_router,
    germination_events_router,
    planting_events_router,
    care_tasks_router,
    sensor_readings_router,
    soil_samples_router,
    irrigation_router,
    irrigation_system_router,
    password_reset_router,
    password_router,
    dashboard_router,
    rule_insights_router,
    trees_router,
    structures_router,
    export_import_router,
    system_router,
    admin_router,
    companion_analysis_router,
)
from app.error_handlers import (
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
)

settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="MVP gardening lifecycle management service for amateur gardeners",
    version="0.1.0",
    debug=settings.DEBUG
)

# CORS middleware for web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register custom error handlers for consistent error format
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Include routers
app.include_router(users_router)
app.include_router(password_reset_router)
app.include_router(password_router)
app.include_router(gardens_router)
app.include_router(lands_router)
app.include_router(plant_varieties_router)
app.include_router(seed_batches_router)
app.include_router(germination_events_router)
app.include_router(planting_events_router)
app.include_router(care_tasks_router)
app.include_router(sensor_readings_router)
app.include_router(soil_samples_router)
app.include_router(irrigation_router)
app.include_router(irrigation_system_router)
app.include_router(dashboard_router)
app.include_router(rule_insights_router)
app.include_router(trees_router)
app.include_router(structures_router)
app.include_router(export_import_router)
app.include_router(system_router)
app.include_router(admin_router)
app.include_router(companion_analysis_router)


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Gardening Helper Service API",
        "version": "0.1.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
