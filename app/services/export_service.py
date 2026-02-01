"""Service for exporting user data"""
from datetime import datetime
from sqlalchemy.orm import Session
from typing import Optional

from app.models.user import User
from app.models.land import Land
from app.models.garden import Garden
from app.models.tree import Tree
from app.models.planting_event import PlantingEvent
from app.models.soil_sample import SoilSample
from app.models.irrigation_source import IrrigationSource
from app.models.irrigation_zone import IrrigationZone
from app.models.watering_event import WateringEvent
from app.models.sensor_reading import SensorReading
from app.schemas.export_import import (
    ExportData,
    ExportMetadata,
    ExportUserProfile,
    ExportLand,
    ExportGarden,
    ExportTree,
    ExportPlanting,
    ExportSoilSample,
    ExportIrrigationSource,
    ExportIrrigationZone,
    ExportWateringEvent,
    ExportSensorReading,
    EXPORT_SCHEMA_VERSION,
)


class ExportService:
    """Service for exporting user data to portable format"""

    @staticmethod
    def export_user_data(
        db: Session,
        user: User,
        include_sensor_readings: bool = False
    ) -> ExportData:
        """
        Export all data for a user to a portable JSON format.

        Args:
            db: Database session
            user: User whose data to export
            include_sensor_readings: Whether to include sensor readings (can be large)

        Returns:
            ExportData object containing all user data
        """
        # Create metadata
        metadata = ExportMetadata(
            export_timestamp=datetime.utcnow(),
            user_id=user.id,
            include_sensor_readings=include_sensor_readings
        )

        # Export user profile (non-sensitive only)
        user_profile = ExportUserProfile(
            display_name=user.display_name,
            city=user.city,
            zip_code=user.zip_code,
            usda_zone=user.usda_zone,
            gardening_preferences=user.gardening_preferences
        )

        # Export lands
        lands = db.query(Land).filter(Land.user_id == user.id).all()
        export_lands = [
            ExportLand(
                id=land.id,
                name=land.name,
                width=land.width,
                height=land.height,
                created_at=land.created_at
            )
            for land in lands
        ]

        # Export gardens
        gardens = db.query(Garden).filter(Garden.user_id == user.id).all()
        export_gardens = [
            ExportGarden(
                id=garden.id,
                land_id=garden.land_id,
                name=garden.name,
                description=garden.description,
                garden_type=garden.garden_type.value if garden.garden_type else 'outdoor',
                location=garden.location,
                light_source_type=garden.light_source_type.value if garden.light_source_type else None,
                light_hours_per_day=garden.light_hours_per_day,
                temp_min_f=garden.temp_min_f,
                temp_max_f=garden.temp_max_f,
                humidity_min_percent=garden.humidity_min_percent,
                humidity_max_percent=garden.humidity_max_percent,
                container_type=garden.container_type,
                grow_medium=garden.grow_medium,
                is_hydroponic=garden.is_hydroponic,
                hydro_system_type=garden.hydro_system_type.value if garden.hydro_system_type else None,
                reservoir_size_liters=garden.reservoir_size_liters,
                nutrient_schedule=garden.nutrient_schedule,
                ph_min=garden.ph_min,
                ph_max=garden.ph_max,
                ec_min=garden.ec_min,
                ec_max=garden.ec_max,
                ppm_min=garden.ppm_min,
                ppm_max=garden.ppm_max,
                water_temp_min_f=garden.water_temp_min_f,
                water_temp_max_f=garden.water_temp_max_f,
                x=garden.x,
                y=garden.y,
                width=garden.width,
                height=garden.height,
                irrigation_zone_id=garden.irrigation_zone_id,
                mulch_depth_inches=garden.mulch_depth_inches,
                is_raised_bed=garden.is_raised_bed,
                soil_texture_override=garden.soil_texture_override,
                created_at=garden.created_at
            )
            for garden in gardens
        ]

        # Export trees
        trees = db.query(Tree).filter(Tree.user_id == user.id).all()
        export_trees = [
            ExportTree(
                id=tree.id,
                land_id=tree.land_id,
                name=tree.name,
                species_id=tree.species_id,
                x=tree.x,
                y=tree.y,
                canopy_radius=tree.canopy_radius,
                height=tree.height,
                created_at=tree.created_at
            )
            for tree in trees
        ]

        # Export plantings
        plantings = db.query(PlantingEvent).filter(PlantingEvent.user_id == user.id).all()
        export_plantings = [
            ExportPlanting(
                id=planting.id,
                garden_id=planting.garden_id,
                plant_variety_id=planting.plant_variety_id,
                planting_date=planting.planting_date.isoformat() if planting.planting_date else None,
                planting_method=planting.planting_method.value if planting.planting_method else 'direct_sow',
                plant_count=planting.plant_count,
                location_in_garden=planting.location_in_garden,
                health_status=planting.health_status.value if planting.health_status else None,
                plant_notes=planting.plant_notes
            )
            for planting in plantings
        ]

        # Export soil samples
        soil_samples = db.query(SoilSample).filter(SoilSample.user_id == user.id).all()
        export_soil_samples = [
            ExportSoilSample(
                id=sample.id,
                garden_id=sample.garden_id,
                planting_event_id=sample.planting_event_id,
                ph=sample.ph,
                nitrogen_ppm=sample.nitrogen_ppm,
                phosphorus_ppm=sample.phosphorus_ppm,
                potassium_ppm=sample.potassium_ppm,
                organic_matter_percent=sample.organic_matter_percent,
                moisture_percent=sample.moisture_percent,
                date_collected=sample.date_collected.isoformat() if sample.date_collected else None,
                notes=sample.notes
            )
            for sample in soil_samples
        ]

        # Export irrigation sources
        irrigation_sources = db.query(IrrigationSource).filter(IrrigationSource.user_id == user.id).all()
        export_irrigation_sources = [
            ExportIrrigationSource(
                id=source.id,
                name=source.name,
                source_type=source.source_type.value if source.source_type else 'manual',
                flow_capacity_lpm=source.flow_capacity_lpm,
                notes=source.notes,
                created_at=source.created_at
            )
            for source in irrigation_sources
        ]

        # Export irrigation zones
        irrigation_zones = db.query(IrrigationZone).filter(IrrigationZone.user_id == user.id).all()
        export_irrigation_zones = [
            ExportIrrigationZone(
                id=zone.id,
                irrigation_source_id=zone.irrigation_source_id,
                name=zone.name,
                delivery_type=zone.delivery_type.value if zone.delivery_type else 'manual',
                schedule=zone.schedule,
                notes=zone.notes,
                created_at=zone.created_at
            )
            for zone in irrigation_zones
        ]

        # Export watering events
        watering_events = db.query(WateringEvent).filter(WateringEvent.user_id == user.id).all()
        export_watering_events = [
            ExportWateringEvent(
                id=event.id,
                irrigation_zone_id=event.irrigation_zone_id,
                watered_at=event.watered_at.isoformat() if event.watered_at else None,
                duration_minutes=event.duration_minutes,
                estimated_volume_liters=event.estimated_volume_liters,
                is_manual=event.is_manual,
                notes=event.notes,
                created_at=event.created_at
            )
            for event in watering_events
        ]

        # Export sensor readings (optional - can be large)
        export_sensor_readings = []
        if include_sensor_readings:
            sensor_readings = db.query(SensorReading).filter(SensorReading.user_id == user.id).all()
            export_sensor_readings = [
                ExportSensorReading(
                    id=reading.id,
                    garden_id=reading.garden_id,
                    reading_date=reading.reading_date.isoformat() if reading.reading_date else None,
                    temperature_f=reading.temperature_f,
                    humidity_percent=reading.humidity_percent,
                    light_hours=reading.light_hours,
                    ph_level=reading.ph_level,
                    ec_ms_cm=reading.ec_ms_cm,
                    ppm=reading.ppm,
                    water_temp_f=reading.water_temp_f,
                    created_at=reading.created_at
                )
                for reading in sensor_readings
            ]

        # Assemble export data
        export_data = ExportData(
            metadata=metadata,
            user_profile=user_profile,
            lands=export_lands,
            gardens=export_gardens,
            trees=export_trees,
            plantings=export_plantings,
            soil_samples=export_soil_samples,
            irrigation_sources=export_irrigation_sources,
            irrigation_zones=export_irrigation_zones,
            watering_events=export_watering_events,
            sensor_readings=export_sensor_readings
        )

        return export_data
