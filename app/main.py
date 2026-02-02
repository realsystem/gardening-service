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
    admin_compliance_router,
    companion_analysis_router,
    metrics_router,
)
from app.error_handlers import (
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
)
from app.middleware import CorrelationIDMiddleware
from app.middleware.metrics_middleware import MetricsMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.utils.structured_logging import configure_logging
from app.database import check_database_migrations

settings = get_settings()

# Configure structured logging with redaction
configure_logging()

# Check database migrations on startup (production/staging only)
try:
    check_database_migrations()
except RuntimeError as e:
    import logging
    logger = logging.getLogger(__name__)
    logger.critical(f"Database migration check failed: {e}")
    logger.critical("Application startup aborted. Please run pending migrations.")
    raise

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="MVP gardening lifecycle management service for amateur gardeners",
    version="0.1.0",
    debug=settings.DEBUG
)

# Add Correlation ID middleware (FIRST - so all logs have correlation ID)
app.add_middleware(CorrelationIDMiddleware)

# Add Metrics middleware (SECOND - after correlation ID)
app.add_middleware(MetricsMiddleware)

# Add Rate Limit middleware (THIRD - protect against abuse)
# Enabled in production/staging, can be disabled via environment
rate_limit_enabled = settings.APP_ENV in ("production", "staging")
app.add_middleware(RateLimitMiddleware, enabled=rate_limit_enabled)

# Add Security Headers middleware (FOURTH - after rate limiting)
app.add_middleware(SecurityHeadersMiddleware, env=settings.APP_ENV)

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
app.include_router(admin_compliance_router)
app.include_router(companion_analysis_router)
app.include_router(metrics_router)


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
