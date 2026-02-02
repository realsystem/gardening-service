"""Metrics API endpoint.

Exposes Prometheus-formatted metrics at /metrics for scraping.
"""
from fastapi import APIRouter
from app.utils.metrics import get_metrics

router = APIRouter(tags=["metrics"])


@router.get("/metrics")
async def metrics_endpoint():
    """
    Prometheus metrics endpoint.

    Exposes application metrics in Prometheus text format for scraping.

    Metrics include:
    - HTTP request count, latency, error rate
    - Rule engine execution time
    - Compliance block counts
    - Authentication metrics

    This endpoint is typically scraped by Prometheus server every 15-60 seconds.

    Returns:
        Prometheus-formatted metrics
    """
    return get_metrics()
