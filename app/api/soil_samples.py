"""Soil sample tracking endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.database import get_db
from app.models.user import User
from app.models.soil_sample import SoilSample
from app.models.garden import Garden
from app.models.planting_event import PlantingEvent
from app.models.plant_variety import PlantVariety
from app.schemas.soil_sample import (
    SoilSampleCreate,
    SoilSampleUpdate,
    SoilSampleResponse,
    SoilSampleList,
)
from app.rules.soil_rules import generate_soil_recommendations
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/soil-samples", tags=["Soil Samples"])


@router.post("", response_model=SoilSampleResponse, status_code=201)
def create_soil_sample(
    sample_data: SoilSampleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new soil sample.

    Either garden_id or planting_event_id must be provided.
    Generates scientific recommendations based on soil chemistry and plant requirements.
    """
    # Validate that at least one link is provided
    if not sample_data.garden_id and not sample_data.planting_event_id:
        raise HTTPException(
            status_code=400,
            detail="Either garden_id or planting_event_id must be provided"
        )

    # Validate garden ownership if garden_id provided
    if sample_data.garden_id:
        garden = db.query(Garden).filter(
            Garden.id == sample_data.garden_id,
            Garden.user_id == current_user.id
        ).first()
        if not garden:
            raise HTTPException(status_code=404, detail="Garden not found")

    # Validate planting event ownership if planting_event_id provided
    plant_variety = None
    if sample_data.planting_event_id:
        planting = db.query(PlantingEvent).filter(
            PlantingEvent.id == sample_data.planting_event_id,
            PlantingEvent.user_id == current_user.id
        ).first()
        if not planting:
            raise HTTPException(status_code=404, detail="Planting event not found")

        # Get plant variety for recommendations
        plant_variety = db.query(PlantVariety).filter(
            PlantVariety.id == planting.plant_variety_id
        ).first()

    # Create soil sample
    soil_sample = SoilSample(
        user_id=current_user.id,
        garden_id=sample_data.garden_id,
        planting_event_id=sample_data.planting_event_id,
        ph=sample_data.ph,
        nitrogen_ppm=sample_data.nitrogen_ppm,
        phosphorus_ppm=sample_data.phosphorus_ppm,
        potassium_ppm=sample_data.potassium_ppm,
        organic_matter_percent=sample_data.organic_matter_percent,
        moisture_percent=sample_data.moisture_percent,
        date_collected=sample_data.date_collected,
        notes=sample_data.notes
    )

    db.add(soil_sample)
    db.commit()
    db.refresh(soil_sample)

    # Generate recommendations
    recommendations = generate_soil_recommendations(soil_sample, plant_variety)

    # Build response
    response = SoilSampleResponse.from_orm(soil_sample)
    response.recommendations = recommendations

    # Add garden/plant names
    if sample_data.garden_id:
        response.garden_name = garden.name
    if plant_variety:
        response.plant_name = plant_variety.common_name

    return response


@router.get("", response_model=SoilSampleList)
def list_soil_samples(
    garden_id: Optional[int] = Query(None, description="Filter by garden ID"),
    planting_event_id: Optional[int] = Query(None, description="Filter by planting event ID"),
    start_date: Optional[date] = Query(None, description="Filter samples from this date"),
    end_date: Optional[date] = Query(None, description="Filter samples until this date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all soil samples for the current user.

    Supports filtering by garden, planting event, and date range.
    Includes scientific recommendations for each sample.
    """
    query = db.query(SoilSample).filter(SoilSample.user_id == current_user.id)

    # Apply filters
    if garden_id:
        query = query.filter(SoilSample.garden_id == garden_id)
    if planting_event_id:
        query = query.filter(SoilSample.planting_event_id == planting_event_id)
    if start_date:
        query = query.filter(SoilSample.date_collected >= start_date)
    if end_date:
        query = query.filter(SoilSample.date_collected <= end_date)

    # Order by date (most recent first)
    samples = query.order_by(SoilSample.date_collected.desc()).all()

    # Build response with recommendations
    sample_responses = []
    for sample in samples:
        # Get plant variety if linked to planting
        plant_variety = None
        if sample.planting_event_id:
            planting = db.query(PlantingEvent).filter(
                PlantingEvent.id == sample.planting_event_id
            ).first()
            if planting:
                plant_variety = db.query(PlantVariety).filter(
                    PlantVariety.id == planting.plant_variety_id
                ).first()

        # Generate recommendations
        recommendations = generate_soil_recommendations(sample, plant_variety)

        # Build response
        response = SoilSampleResponse.from_orm(sample)
        response.recommendations = recommendations

        # Add names
        if sample.garden:
            response.garden_name = sample.garden.name
        if plant_variety:
            response.plant_name = plant_variety.common_name

        sample_responses.append(response)

    return SoilSampleList(
        samples=sample_responses,
        total=len(sample_responses),
        latest_sample=sample_responses[0] if sample_responses else None
    )


@router.get("/{sample_id}", response_model=SoilSampleResponse)
def get_soil_sample(
    sample_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific soil sample by ID.

    Returns detailed sample data with scientific recommendations.
    """
    sample = db.query(SoilSample).filter(
        SoilSample.id == sample_id,
        SoilSample.user_id == current_user.id
    ).first()

    if not sample:
        raise HTTPException(status_code=404, detail="Soil sample not found")

    # Get plant variety if linked to planting
    plant_variety = None
    if sample.planting_event_id:
        planting = db.query(PlantingEvent).filter(
            PlantingEvent.id == sample.planting_event_id
        ).first()
        if planting:
            plant_variety = db.query(PlantVariety).filter(
                PlantVariety.id == planting.plant_variety_id
            ).first()

    # Generate recommendations
    recommendations = generate_soil_recommendations(sample, plant_variety)

    # Build response
    response = SoilSampleResponse.from_orm(sample)
    response.recommendations = recommendations

    # Add names
    if sample.garden:
        response.garden_name = sample.garden.name
    if plant_variety:
        response.plant_name = plant_variety.common_name

    return response


@router.put("/{sample_id}", response_model=SoilSampleResponse)
def update_soil_sample(
    sample_id: int,
    update_data: SoilSampleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an existing soil sample.

    Only the owner can update their samples. Supports partial updates.
    All numeric fields are validated against scientific ranges.
    """
    # Find and authorize
    sample = db.query(SoilSample).filter(
        SoilSample.id == sample_id,
        SoilSample.user_id == current_user.id
    ).first()

    if not sample:
        raise HTTPException(status_code=404, detail="Soil sample not found")

    # Update only provided fields
    update_dict = update_data.dict(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(sample, field, value)

    db.commit()
    db.refresh(sample)

    # Get plant variety if linked to planting
    plant_variety = None
    if sample.planting_event_id:
        planting = db.query(PlantingEvent).filter(
            PlantingEvent.id == sample.planting_event_id
        ).first()
        if planting:
            plant_variety = db.query(PlantVariety).filter(
                PlantVariety.id == planting.plant_variety_id
            ).first()

    # Generate updated recommendations
    recommendations = generate_soil_recommendations(sample, plant_variety)

    # Build response
    response = SoilSampleResponse.from_orm(sample)
    response.recommendations = recommendations

    # Add names
    if sample.garden:
        response.garden_name = sample.garden.name
    if plant_variety:
        response.plant_name = plant_variety.common_name

    return response


@router.delete("/{sample_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_soil_sample(
    sample_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a soil sample.

    Only the owner can delete their own samples.
    """
    sample = db.query(SoilSample).filter(
        SoilSample.id == sample_id,
        SoilSample.user_id == current_user.id
    ).first()

    if not sample:
        raise HTTPException(status_code=404, detail="Soil sample not found")

    db.delete(sample)
    db.commit()

    return None
