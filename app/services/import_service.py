"""Service for importing user data"""
from datetime import datetime
from sqlalchemy.orm import Session
from typing import Dict, List, Tuple
from packaging import version
from fastapi import HTTPException, status

from app.models.user import User
from app.models.land import Land
from app.models.garden import Garden, GardenType, LightSourceType, HydroSystemType
from app.models.tree import Tree
from app.models.planting_event import PlantingEvent, PlantingMethod, PlantHealth
from app.models.plant_variety import PlantVariety
from app.models.soil_sample import SoilSample
# SensorReading removed in Phase 6 of platform simplification
# Irrigation models removed in Phase 1 of platform simplification
from app.schemas.export_import import (
    ExportData,
    ImportPreview,
    ImportResult,
    ImportValidationIssue,
    EXPORT_SCHEMA_VERSION,
)
from app.compliance.service import ComplianceService


class ImportService:
    """Service for importing user data from export format"""

    @staticmethod
    def validate_import(
        db: Session,
        user: User,
        data: ExportData,
        mode: str
    ) -> ImportPreview:
        """
        Validate import data and generate preview.

        Args:
            db: Database session
            user: User who will own the imported data
            data: Export data to import
            mode: Import mode (dry_run, merge, overwrite)

        Returns:
            ImportPreview with validation results
        """
        issues: List[ImportValidationIssue] = []
        warnings: List[str] = []

        # Check schema version compatibility
        schema_version_compatible = ImportService._check_schema_version(
            data.metadata.schema_version,
            issues
        )

        # Count items
        counts = {
            "lands": len(data.lands),
            "gardens": len(data.gardens),
            "trees": len(data.trees),
            "plantings": len(data.plantings),
            "soil_samples": len(data.soil_samples),
            "irrigation_sources": len(data.irrigation_sources),
            "irrigation_zones": len(data.irrigation_zones)
            # sensor_readings removed in Phase 6 of platform simplification
            # watering_events removed with watering event tracking
        }

        # Validate relationships
        ImportService._validate_relationships(data, issues, warnings)

        # Check for overwrite impact
        would_overwrite = None
        if mode == "overwrite":
            would_overwrite = ImportService._count_existing_data(db, user)
            if would_overwrite > 0:
                warnings.append(
                    f"Overwrite mode will delete {would_overwrite} existing items before import"
                )

        # Validate data types and required fields
        ImportService._validate_data_types(data, issues)

        # Determine if valid (no error-level issues)
        valid = all(issue.severity != "error" for issue in issues)

        return ImportPreview(
            valid=valid,
            issues=issues,
            counts=counts,
            warnings=warnings,
            schema_version_compatible=schema_version_compatible,
            would_overwrite=would_overwrite
        )

    @staticmethod
    def import_user_data(
        db: Session,
        user: User,
        data: ExportData,
        mode: str
    ) -> ImportResult:
        """
        Import user data with specified mode.

        Args:
            db: Database session
            user: User who will own the imported data
            data: Export data to import
            mode: Import mode (dry_run, merge, overwrite)

        Returns:
            ImportResult with operation results
        """
        # Validate first
        preview = ImportService.validate_import(db, user, data, mode)

        if mode == "dry_run":
            return ImportResult(
                success=preview.valid,
                mode=mode,
                items_imported={},
                errors=[issue.message for issue in preview.issues if issue.severity == "error"],
                warnings=preview.warnings
            )

        if not preview.valid:
            return ImportResult(
                success=False,
                mode=mode,
                items_imported={},
                errors=[issue.message for issue in preview.issues if issue.severity == "error"],
                warnings=preview.warnings
            )

        # Execute import within transaction
        try:
            deleted_count = None
            if mode == "overwrite":
                deleted_count = ImportService._delete_existing_data(db, user)

            id_mapping = ImportService._import_data(db, user, data, mode)

            db.commit()

            return ImportResult(
                success=True,
                mode=mode,
                items_imported=preview.counts,
                items_deleted=deleted_count,
                warnings=preview.warnings,
                id_mapping=id_mapping
            )

        except Exception as e:
            db.rollback()
            return ImportResult(
                success=False,
                mode=mode,
                items_imported={},
                errors=[f"Import failed: {str(e)}"],
                warnings=preview.warnings
            )

    @staticmethod
    def _check_schema_version(schema_ver: str, issues: List[ImportValidationIssue]) -> bool:
        """Check if schema version is compatible"""
        try:
            import_version = version.parse(schema_ver)
            current_version = version.parse(EXPORT_SCHEMA_VERSION)

            # Major version must match
            if import_version.major != current_version.major:
                issues.append(ImportValidationIssue(
                    severity="error",
                    category="schema_version",
                    message=f"Incompatible schema version: {schema_ver} (current: {EXPORT_SCHEMA_VERSION})",
                    details={"import_version": schema_ver, "current_version": EXPORT_SCHEMA_VERSION}
                ))
                return False

            # Minor version warning if newer
            if import_version.minor > current_version.minor:
                issues.append(ImportValidationIssue(
                    severity="warning",
                    category="schema_version",
                    message=f"Import data from newer version ({schema_ver}), some features may be ignored"
                ))

            return True
        except Exception as e:
            issues.append(ImportValidationIssue(
                severity="error",
                category="schema_version",
                message=f"Invalid schema version format: {schema_ver}"
            ))
            return False

    @staticmethod
    def _validate_relationships(data: ExportData, issues: List[ImportValidationIssue], warnings: List[str]):
        """Validate that foreign key relationships are valid"""
        land_ids = {land.id for land in data.lands}
        garden_ids = {garden.id for garden in data.gardens}
        irrigation_source_ids = {source.id for source in data.irrigation_sources}
        irrigation_zone_ids = {zone.id for zone in data.irrigation_zones}

        # Check garden -> land references
        for garden in data.gardens:
            if garden.land_id and garden.land_id not in land_ids:
                warnings.append(f"Garden '{garden.name}' references non-existent land_id {garden.land_id}")

        # Check tree -> land references
        for tree in data.trees:
            if tree.land_id not in land_ids:
                issues.append(ImportValidationIssue(
                    severity="error",
                    category="relationships",
                    message=f"Tree '{tree.name}' references non-existent land_id {tree.land_id}"
                ))

        # Check planting -> garden references
        for planting in data.plantings:
            if planting.garden_id not in garden_ids:
                issues.append(ImportValidationIssue(
                    severity="error",
                    category="relationships",
                    message=f"Planting references non-existent garden_id {planting.garden_id}"
                ))

        # Check irrigation zone -> source references
        for zone in data.irrigation_zones:
            if zone.irrigation_source_id and zone.irrigation_source_id not in irrigation_source_ids:
                warnings.append(f"Irrigation zone '{zone.name}' references non-existent source_id {zone.irrigation_source_id}")

    @staticmethod
    def _validate_data_types(data: ExportData, issues: List[ImportValidationIssue]):
        """Validate data types and required fields"""
        # Validate lands
        for land in data.lands:
            if not land.name or land.width <= 0 or land.height <= 0:
                issues.append(ImportValidationIssue(
                    severity="error",
                    category="data_validation",
                    message=f"Invalid land data: {land.name}"
                ))

        # Validate gardens
        for garden in data.gardens:
            if not garden.name:
                issues.append(ImportValidationIssue(
                    severity="error",
                    category="data_validation",
                    message="Garden missing required name"
                ))

    @staticmethod
    def _count_existing_data(db: Session, user: User) -> int:
        """Count existing user data that would be deleted in overwrite mode"""
        counts = (
            db.query(Land).filter(Land.user_id == user.id).count() +
            db.query(Garden).filter(Garden.user_id == user.id).count() +
            db.query(Tree).filter(Tree.user_id == user.id).count() +
            db.query(PlantingEvent).filter(PlantingEvent.user_id == user.id).count() +
            db.query(SoilSample).filter(SoilSample.user_id == user.id).count() +
            db.query(IrrigationSource).filter(IrrigationSource.user_id == user.id).count() +
            db.query(IrrigationZone).filter(IrrigationZone.user_id == user.id).count()
            # WateringEvent and SensorReading removed in platform simplification
        )
        return counts

    @staticmethod
    def _delete_existing_data(db: Session, user: User) -> int:
        """Delete all existing user data (for overwrite mode)

        Returns:
            Total number of items deleted
        """
        # Delete in correct order to respect foreign key constraints
        # Count deletions
        count = 0
        # WateringEvent and SensorReading removed in platform simplification
        count += db.query(SoilSample).filter(SoilSample.user_id == user.id).delete()
        count += db.query(PlantingEvent).filter(PlantingEvent.user_id == user.id).delete()
        count += db.query(Tree).filter(Tree.user_id == user.id).delete()
        count += db.query(IrrigationZone).filter(IrrigationZone.user_id == user.id).delete()
        count += db.query(IrrigationSource).filter(IrrigationSource.user_id == user.id).delete()
        count += db.query(Garden).filter(Garden.user_id == user.id).delete()
        count += db.query(Land).filter(Land.user_id == user.id).delete()
        return count

    @staticmethod
    def _import_data(
        db: Session,
        user: User,
        data: ExportData,
        mode: str
    ) -> Dict[str, Dict[int, int]]:
        """
        Import data and return ID mappings.

        Returns dict mapping entity type to old_id -> new_id mapping
        """
        id_mapping: Dict[str, Dict[int, int]] = {}

        # Import lands
        land_id_map = {}
        for land_data in data.lands:
            new_land = Land(
                user_id=user.id,
                name=land_data.name,
                width=land_data.width,
                height=land_data.height
            )
            db.add(new_land)
            db.flush()  # Get new ID
            land_id_map[land_data.id] = new_land.id
        id_mapping["lands"] = land_id_map

        # Import irrigation sources (needed before zones)
        irrigation_source_id_map = {}
        for source_data in data.irrigation_sources:
            new_source = IrrigationSource(
                user_id=user.id,
                name=source_data.name,
                source_type=source_data.source_type,
                flow_capacity_lpm=source_data.flow_capacity_lpm,
                notes=source_data.notes
            )
            db.add(new_source)
            db.flush()
            irrigation_source_id_map[source_data.id] = new_source.id
        id_mapping["irrigation_sources"] = irrigation_source_id_map

        # Import irrigation zones
        irrigation_zone_id_map = {}
        for zone_data in data.irrigation_zones:
            new_zone = IrrigationZone(
                user_id=user.id,
                irrigation_source_id=irrigation_source_id_map.get(zone_data.irrigation_source_id),
                name=zone_data.name,
                delivery_type=zone_data.delivery_type,
                schedule=zone_data.schedule,
                notes=zone_data.notes
            )
            db.add(new_zone)
            db.flush()
            irrigation_zone_id_map[zone_data.id] = new_zone.id
        id_mapping["irrigation_zones"] = irrigation_zone_id_map

        # Import gardens
        garden_id_map = {}
        for garden_data in data.gardens:
            new_garden = Garden(
                user_id=user.id,
                land_id=land_id_map.get(garden_data.land_id) if garden_data.land_id else None,
                name=garden_data.name,
                description=garden_data.description,
                garden_type=GardenType[garden_data.garden_type.upper()],
                location=garden_data.location,
                light_source_type=LightSourceType[garden_data.light_source_type.upper()] if garden_data.light_source_type else None,
                light_hours_per_day=garden_data.light_hours_per_day,
                temp_min_f=garden_data.temp_min_f,
                temp_max_f=garden_data.temp_max_f,
                humidity_min_percent=garden_data.humidity_min_percent,
                humidity_max_percent=garden_data.humidity_max_percent,
                container_type=garden_data.container_type,
                grow_medium=garden_data.grow_medium,
                is_hydroponic=garden_data.is_hydroponic,
                hydro_system_type=HydroSystemType[garden_data.hydro_system_type.upper()] if garden_data.hydro_system_type else None,
                reservoir_size_liters=garden_data.reservoir_size_liters,
                nutrient_schedule=garden_data.nutrient_schedule,
                ph_min=garden_data.ph_min,
                ph_max=garden_data.ph_max,
                ec_min=garden_data.ec_min,
                ec_max=garden_data.ec_max,
                ppm_min=garden_data.ppm_min,
                ppm_max=garden_data.ppm_max,
                water_temp_min_f=garden_data.water_temp_min_f,
                water_temp_max_f=garden_data.water_temp_max_f,
                x=garden_data.x,
                y=garden_data.y,
                width=garden_data.width,
                height=garden_data.height,
                irrigation_zone_id=irrigation_zone_id_map.get(garden_data.irrigation_zone_id) if garden_data.irrigation_zone_id else None,
                mulch_depth_inches=garden_data.mulch_depth_inches,
                is_raised_bed=garden_data.is_raised_bed,
                soil_texture_override=garden_data.soil_texture_override
            )
            db.add(new_garden)
            db.flush()
            garden_id_map[garden_data.id] = new_garden.id
        id_mapping["gardens"] = garden_id_map

        # Import trees
        tree_id_map = {}
        for tree_data in data.trees:
            new_tree = Tree(
                user_id=user.id,
                land_id=land_id_map[tree_data.land_id],
                name=tree_data.name,
                species_id=tree_data.species_id,
                x=tree_data.x,
                y=tree_data.y,
                canopy_radius=tree_data.canopy_radius,
                height=tree_data.height
            )
            db.add(new_tree)
            db.flush()
            tree_id_map[tree_data.id] = new_tree.id
        id_mapping["trees"] = tree_id_map

        # Import plantings (with compliance check for restricted varieties)
        compliance_service = ComplianceService(db)
        planting_id_map = {}
        for planting_data in data.plantings:
            # Compliance check: verify plant variety is not restricted
            # This prevents importing plantings that reference restricted varieties
            variety = db.query(PlantVariety).filter(
                PlantVariety.id == planting_data.plant_variety_id
            ).first()

            if variety:
                # Check if this variety is restricted
                compliance_service.check_and_enforce_plant_restriction(
                    user=user,
                    common_name=variety.common_name,
                    scientific_name=variety.scientific_name,
                    notes=planting_data.plant_notes,
                    request_metadata={
                        "endpoint": "import_user_data",
                        "variety_id": variety.id,
                        "import_mode": mode
                    }
                )

            new_planting = PlantingEvent(
                user_id=user.id,
                garden_id=garden_id_map[planting_data.garden_id],
                plant_variety_id=planting_data.plant_variety_id,
                planting_date=datetime.fromisoformat(planting_data.planting_date),
                planting_method=PlantingMethod[planting_data.planting_method.upper()],
                plant_count=planting_data.plant_count,
                location_in_garden=planting_data.location_in_garden,
                health_status=PlantHealth[planting_data.health_status.upper()] if planting_data.health_status else None,
                plant_notes=planting_data.plant_notes
            )
            db.add(new_planting)
            db.flush()
            planting_id_map[planting_data.id] = new_planting.id
        id_mapping["plantings"] = planting_id_map

        # Import soil samples
        for sample_data in data.soil_samples:
            new_sample = SoilSample(
                user_id=user.id,
                garden_id=garden_id_map.get(sample_data.garden_id) if sample_data.garden_id else None,
                planting_event_id=planting_id_map.get(sample_data.planting_event_id) if sample_data.planting_event_id else None,
                ph=sample_data.ph,
                nitrogen_ppm=sample_data.nitrogen_ppm,
                phosphorus_ppm=sample_data.phosphorus_ppm,
                potassium_ppm=sample_data.potassium_ppm,
                organic_matter_percent=sample_data.organic_matter_percent,
                moisture_percent=sample_data.moisture_percent,
                date_collected=datetime.fromisoformat(sample_data.date_collected),
                notes=sample_data.notes
            )
            db.add(new_sample)

        # Watering event import removed with watering event tracking feature
        # Sensor reading import removed in Phase 6 of platform simplification

        return id_mapping
