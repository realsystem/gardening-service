"""
Companion Planting Analysis API.

Provides science-based companion planting recommendations for gardens
based on documented plant-to-plant relationships.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Dict, Any, Optional
from datetime import datetime
import math

from app.database import get_db
from app.models.user import User
from app.models.garden import Garden
from app.models.planting_event import PlantingEvent
from app.models.plant_variety import PlantVariety
from app.models.companion_relationship import (
    CompanionRelationship,
    RelationshipType,
    ConfidenceLevel
)
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/gardens", tags=["Companion Planting"])


def calculate_distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """Calculate Euclidean distance between two points in meters."""
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)


def normalize_plant_pair(plant_a_id: int, plant_b_id: int) -> tuple:
    """Ensure plant_a_id < plant_b_id for normalized lookups."""
    if plant_a_id < plant_b_id:
        return (plant_a_id, plant_b_id)
    return (plant_b_id, plant_a_id)


@router.get("/{garden_id}/companions")
def get_companion_analysis(
    garden_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Analyze companion planting relationships in a garden.

    Returns:
        - Beneficial pairs: Plants that are helping each other
        - Conflicts: Antagonistic plants that are too close
        - Suggestions: Recommendations for improving plant placement
    """
    # Verify garden ownership
    garden = db.query(Garden).filter(
        Garden.id == garden_id,
        Garden.user_id == current_user.id
    ).first()

    if not garden:
        raise HTTPException(status_code=404, detail="Garden not found")

    # Get all planting events in this garden with positions
    plantings = db.query(PlantingEvent).join(PlantVariety).filter(
        PlantingEvent.garden_id == garden_id,
        PlantingEvent.x.isnot(None),  # Has position
        PlantingEvent.y.isnot(None)
    ).all()

    if len(plantings) < 2:
        return {
            "garden_id": garden_id,
            "garden_name": garden.name,
            "analysis_time": datetime.utcnow().isoformat(),
            "planting_count": len(plantings),
            "beneficial_pairs": [],
            "conflicts": [],
            "suggestions": [],
            "message": "Need at least 2 plants for companion analysis"
        }

    # Build lookup maps
    variety_map = {}  # planting_id -> PlantVariety
    for planting in plantings:
        variety = db.query(PlantVariety).get(planting.plant_variety_id)
        if variety:
            variety_map[planting.id] = variety

    beneficial_pairs = []
    conflicts = []
    suggestions = []
    analyzed_pairs = set()  # Track (plant_a_id, plant_b_id) pairs we've seen

    # Analyze each pair of plantings
    for i, planting_a in enumerate(plantings):
        variety_a = variety_map.get(planting_a.id)
        if not variety_a:
            continue

        for planting_b in plantings[i+1:]:
            variety_b = variety_map.get(planting_b.id)
            if not variety_b:
                continue

            # Calculate distance between plantings
            distance = calculate_distance(
                planting_a.x, planting_a.y,
                planting_b.x, planting_b.y
            )

            # Query companion relationship (normalized lookup)
            norm_a, norm_b = normalize_plant_pair(variety_a.id, variety_b.id)
            pair_key = (norm_a, norm_b)

            if pair_key in analyzed_pairs:
                continue
            analyzed_pairs.add(pair_key)

            relationship = db.query(CompanionRelationship).filter(
                CompanionRelationship.plant_a_id == norm_a,
                CompanionRelationship.plant_b_id == norm_b
            ).first()

            if not relationship:
                continue  # No documented relationship

            # Determine if relationship is active based on distance
            is_within_effective_range = distance <= relationship.effective_distance_m
            is_within_optimal_range = (
                relationship.optimal_distance_m is not None and
                distance <= relationship.optimal_distance_m
            )

            # Build result object
            pair_info = {
                "plant_a": {
                    "planting_id": planting_a.id,
                    "variety_id": variety_a.id,
                    "common_name": variety_a.common_name,
                    "position": {"x": planting_a.x, "y": planting_a.y}
                },
                "plant_b": {
                    "planting_id": planting_b.id,
                    "variety_id": variety_b.id,
                    "common_name": variety_b.common_name,
                    "position": {"x": planting_b.x, "y": planting_b.y}
                },
                "distance_m": round(distance, 2),
                "relationship_type": relationship.relationship_type.value,
                "confidence_level": relationship.confidence_level.value,
                "mechanism": relationship.mechanism,
                "source_reference": relationship.source_reference,
                "notes": relationship.notes,
                "effective_distance_m": relationship.effective_distance_m,
                "optimal_distance_m": relationship.optimal_distance_m
            }

            # Categorize based on relationship type and distance
            if relationship.relationship_type == RelationshipType.BENEFICIAL:
                if is_within_effective_range:
                    pair_info["status"] = "optimal" if is_within_optimal_range else "active"
                    pair_info["benefit_description"] = (
                        f"{variety_a.common_name} and {variety_b.common_name} are "
                        f"benefiting each other (distance: {distance:.1f}m). {relationship.mechanism}"
                    )
                    beneficial_pairs.append(pair_info)
                else:
                    # Too far apart - suggest moving closer
                    suggestions.append({
                        "type": "move_closer",
                        "plant_a": variety_a.common_name,
                        "plant_b": variety_b.common_name,
                        "current_distance_m": round(distance, 2),
                        "recommended_distance_m": relationship.optimal_distance_m or relationship.effective_distance_m,
                        "reason": f"These plants have a beneficial relationship but are too far apart. {relationship.mechanism}",
                        "confidence": relationship.confidence_level.value
                    })

            elif relationship.relationship_type == RelationshipType.ANTAGONISTIC:
                if is_within_effective_range:
                    pair_info["status"] = "conflict"
                    pair_info["problem_description"] = (
                        f"{variety_a.common_name} and {variety_b.common_name} are "
                        f"antagonistic and too close (distance: {distance:.1f}m). {relationship.mechanism}"
                    )
                    pair_info["recommended_separation_m"] = relationship.effective_distance_m
                    conflicts.append(pair_info)
                else:
                    # Good - they're far enough apart
                    pass

            # Note: NEUTRAL relationships are tracked but don't generate insights

    # Generate additional suggestions based on available space
    # (Future enhancement: suggest complementary plants that aren't currently in the garden)

    return {
        "garden_id": garden_id,
        "garden_name": garden.name,
        "analysis_time": datetime.utcnow().isoformat(),
        "planting_count": len(plantings),
        "relationships_analyzed": len(analyzed_pairs),
        "beneficial_pairs": beneficial_pairs,
        "conflicts": conflicts,
        "suggestions": suggestions,
        "summary": {
            "beneficial_count": len(beneficial_pairs),
            "conflict_count": len(conflicts),
            "suggestion_count": len(suggestions)
        }
    }
