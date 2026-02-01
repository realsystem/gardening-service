"""
Unit tests for export/import functionality

Tests serialization, deserialization, validation, and data integrity.
"""
import pytest
from datetime import datetime, date
from app.services.export_service import ExportService
from app.services.import_service import ImportService
from app.models.user import User
from app.models.land import Land
from app.models.garden import Garden, GardenType
from app.models.tree import Tree
from app.models.planting_event import PlantingEvent, PlantingMethod
from app.models.soil_sample import SoilSample
from app.models.irrigation_source import IrrigationSource
from app.models.irrigation_zone import IrrigationZone
from app.models.watering_event import WateringEvent
from app.models.sensor_reading import SensorReading
from app.models.plant_variety import PlantVariety, WaterRequirement, SunRequirement
from app.schemas.export_import import (
    ExportData,
    ImportMode,
    EXPORT_SCHEMA_VERSION,
)
from app.services.auth_service import AuthService


class TestExportService:
    """Test export service functionality"""

    def test_export_empty_user(self, test_db):
        """Exporting user with no data should succeed"""
        user = User(
            email="empty@example.com",
            hashed_password=AuthService.hash_password("test123"),
            display_name="Empty User"
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        export_data = ExportService.export_user_data(test_db, user)

        assert export_data.metadata.schema_version == EXPORT_SCHEMA_VERSION
        assert export_data.metadata.user_id == user.id
        assert export_data.user_profile.display_name == "Empty User"
        assert len(export_data.lands) == 0
        assert len(export_data.gardens) == 0
        assert len(export_data.trees) == 0
        assert len(export_data.plantings) == 0

    def test_export_user_profile_no_sensitive_data(self, test_db):
        """Export should not include sensitive user data"""
        user = User(
            email="sensitive@example.com",
            hashed_password=AuthService.hash_password("secretpassword"),
            display_name="Test User",
            city="Portland",
            zip_code="97201"
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        export_data = ExportService.export_user_data(test_db, user)

        # Check that sensitive data is NOT in export
        export_json = export_data.model_dump_json()
        assert "sensitive@example.com" not in export_json
        assert "secretpassword" not in export_json
        assert "hashed_password" not in export_json

        # Check that non-sensitive data IS in export
        assert export_data.user_profile.display_name == "Test User"
        assert export_data.user_profile.city == "Portland"
        assert export_data.user_profile.zip_code == "97201"

    def test_export_lands_and_gardens(self, test_db):
        """Export lands with gardens"""
        user = User(
            email="lands@example.com",
            hashed_password=AuthService.hash_password("test123")
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        land = Land(
            user_id=user.id,
            name="My Land",
            width=100.0,
            height=100.0
        )
        test_db.add(land)
        test_db.commit()
        test_db.refresh(land)

        garden = Garden(
            user_id=user.id,
            land_id=land.id,
            name="Veggie Garden",
            garden_type=GardenType.OUTDOOR,
            x=10.0,
            y=10.0,
            width=20.0,
            height=20.0
        )
        test_db.add(garden)
        test_db.commit()

        export_data = ExportService.export_user_data(test_db, user)

        assert len(export_data.lands) == 1
        assert export_data.lands[0].name == "My Land"
        assert export_data.lands[0].width == 100.0

        assert len(export_data.gardens) == 1
        assert export_data.gardens[0].name == "Veggie Garden"
        assert export_data.gardens[0].land_id == land.id
        assert export_data.gardens[0].garden_type == "outdoor"

    def test_export_enum_conversion(self, test_db):
        """Export should convert enums to string values"""
        user = User(
            email="enums@example.com",
            hashed_password=AuthService.hash_password("test123")
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        variety = PlantVariety(
            common_name="Tomato",
            water_requirement=WaterRequirement.MEDIUM,
            sun_requirement=SunRequirement.FULL_SUN
        )
        test_db.add(variety)
        test_db.commit()
        test_db.refresh(variety)

        garden = Garden(
            user_id=user.id,
            name="Test Garden",
            garden_type=GardenType.INDOOR
        )
        test_db.add(garden)
        test_db.commit()
        test_db.refresh(garden)

        planting = PlantingEvent(
            user_id=user.id,
            garden_id=garden.id,
            plant_variety_id=variety.id,
            planting_date=date.today(),
            planting_method=PlantingMethod.DIRECT_SOW
        )
        test_db.add(planting)
        test_db.commit()

        export_data = ExportService.export_user_data(test_db, user)

        # Check enum was converted to string
        assert export_data.plantings[0].planting_method == "direct_sow"
        assert isinstance(export_data.plantings[0].planting_method, str)

    def test_export_with_sensor_readings(self, test_db):
        """Export with sensor readings when requested"""
        user = User(
            email="sensors@example.com",
            hashed_password=AuthService.hash_password("test123")
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        garden = Garden(
            user_id=user.id,
            name="Sensor Garden",
            garden_type=GardenType.INDOOR
        )
        test_db.add(garden)
        test_db.commit()
        test_db.refresh(garden)

        reading = SensorReading(
            user_id=user.id,
            garden_id=garden.id,
            reading_date=datetime.utcnow(),
            temperature_f=72.5,
            humidity_percent=65.0
        )
        test_db.add(reading)
        test_db.commit()

        # Export without sensor readings
        export_without = ExportService.export_user_data(test_db, user, include_sensor_readings=False)
        assert len(export_without.sensor_readings) == 0
        assert export_without.metadata.include_sensor_readings is False

        # Export with sensor readings
        export_with = ExportService.export_user_data(test_db, user, include_sensor_readings=True)
        assert len(export_with.sensor_readings) == 1
        assert export_with.sensor_readings[0].temperature_f == 72.5
        assert export_with.metadata.include_sensor_readings is True


class TestImportValidation:
    """Test import validation logic"""

    def test_validate_empty_import(self, test_db):
        """Validating empty import should succeed"""
        user = User(
            email="validator@example.com",
            hashed_password=AuthService.hash_password("test123")
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        # Create minimal export data
        from app.schemas.export_import import ExportMetadata, ExportUserProfile
        export_data = ExportData(
            metadata=ExportMetadata(
                export_timestamp=datetime.utcnow(),
                user_id=999,  # Different user ID
                include_sensor_readings=False
            ),
            user_profile=ExportUserProfile()
        )

        preview = ImportService.validate_import(test_db, user, export_data, ImportMode.MERGE)

        assert preview.valid is True
        assert preview.schema_version_compatible is True
        assert len(preview.issues) == 0
        assert preview.counts["lands"] == 0

    def test_validate_schema_version_compatibility(self, test_db):
        """Validation should check schema version compatibility"""
        user = User(
            email="version@example.com",
            hashed_password=AuthService.hash_password("test123")
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        from app.schemas.export_import import ExportMetadata, ExportUserProfile

        # Test with incompatible major version
        export_data = ExportData(
            metadata=ExportMetadata(
                schema_version="2.0.0",  # Incompatible major version
                export_timestamp=datetime.utcnow(),
                user_id=999
            ),
            user_profile=ExportUserProfile()
        )

        preview = ImportService.validate_import(test_db, user, export_data, ImportMode.MERGE)

        assert preview.schema_version_compatible is False
        # Should have a warning or error about version
        assert any("version" in issue.message.lower() for issue in preview.issues)

    def test_validate_relationship_integrity(self, test_db):
        """Validation should check foreign key relationships"""
        user = User(
            email="relations@example.com",
            hashed_password=AuthService.hash_password("test123")
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        from app.schemas.export_import import (
            ExportMetadata, ExportUserProfile, ExportGarden
        )

        # Create export with garden referencing non-existent land
        export_data = ExportData(
            metadata=ExportMetadata(
                export_timestamp=datetime.utcnow(),
                user_id=999
            ),
            user_profile=ExportUserProfile(),
            gardens=[
                ExportGarden(
                    id=1,
                    land_id=999,  # Non-existent land
                    name="Orphan Garden",
                    garden_type="outdoor",
                    is_hydroponic=False,
                    is_raised_bed=False,
                    created_at=datetime.utcnow()
                )
            ]
        )

        preview = ImportService.validate_import(test_db, user, export_data, ImportMode.MERGE)

        # Should have validation issue or warning about missing land reference
        has_land_issue = any(
            "land_id" in issue.message.lower() or "reference" in issue.message.lower()
            for issue in preview.issues
        )
        has_land_warning = any(
            "land_id" in warning.lower() or "reference" in warning.lower()
            for warning in preview.warnings
        )
        assert has_land_issue or has_land_warning

    def test_validate_overwrite_mode_counts(self, test_db):
        """Validation in overwrite mode should count items to be deleted"""
        user = User(
            email="overwrite@example.com",
            hashed_password=AuthService.hash_password("test123")
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        # Add some existing data
        land1 = Land(user_id=user.id, name="Land 1", width=50, height=50)
        land2 = Land(user_id=user.id, name="Land 2", width=50, height=50)
        test_db.add_all([land1, land2])
        test_db.commit()

        from app.schemas.export_import import ExportMetadata, ExportUserProfile
        export_data = ExportData(
            metadata=ExportMetadata(
                export_timestamp=datetime.utcnow(),
                user_id=999
            ),
            user_profile=ExportUserProfile()
        )

        preview = ImportService.validate_import(test_db, user, export_data, ImportMode.OVERWRITE)

        # Should indicate that existing data would be deleted
        assert preview.would_overwrite is not None
        assert preview.would_overwrite > 0


class TestImportService:
    """Test import service functionality"""

    def test_dry_run_no_changes(self, test_db):
        """Dry run mode should not make any database changes"""
        user = User(
            email="dryrun@example.com",
            hashed_password=AuthService.hash_password("test123")
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        from app.schemas.export_import import (
            ExportMetadata, ExportUserProfile, ExportLand
        )

        export_data = ExportData(
            metadata=ExportMetadata(
                export_timestamp=datetime.utcnow(),
                user_id=999
            ),
            user_profile=ExportUserProfile(),
            lands=[
                ExportLand(
                    id=1,
                    name="Test Land",
                    width=100.0,
                    height=100.0,
                    created_at=datetime.utcnow()
                )
            ]
        )

        # Import in dry run mode
        result = ImportService.import_user_data(test_db, user, export_data, ImportMode.DRY_RUN)

        assert result.success is True
        assert result.mode == ImportMode.DRY_RUN

        # No lands should have been created
        lands_count = test_db.query(Land).filter(Land.user_id == user.id).count()
        assert lands_count == 0

    def test_merge_mode_preserves_existing(self, test_db):
        """Merge mode should add data without deleting existing"""
        user = User(
            email="merge@example.com",
            hashed_password=AuthService.hash_password("test123")
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        # Add existing land
        existing_land = Land(user_id=user.id, name="Existing Land", width=50, height=50)
        test_db.add(existing_land)
        test_db.commit()

        from app.schemas.export_import import (
            ExportMetadata, ExportUserProfile, ExportLand
        )

        export_data = ExportData(
            metadata=ExportMetadata(
                export_timestamp=datetime.utcnow(),
                user_id=999
            ),
            user_profile=ExportUserProfile(),
            lands=[
                ExportLand(
                    id=1,
                    name="Imported Land",
                    width=100.0,
                    height=100.0,
                    created_at=datetime.utcnow()
                )
            ]
        )

        # Import in merge mode
        result = ImportService.import_user_data(test_db, user, export_data, ImportMode.MERGE)

        assert result.success is True
        assert result.items_imported["lands"] == 1

        # Should now have 2 lands (existing + imported)
        lands = test_db.query(Land).filter(Land.user_id == user.id).all()
        assert len(lands) == 2
        land_names = {land.name for land in lands}
        assert "Existing Land" in land_names
        assert "Imported Land" in land_names

    def test_overwrite_mode_deletes_existing(self, test_db):
        """Overwrite mode should delete existing data before import"""
        user = User(
            email="overwrite@example.com",
            hashed_password=AuthService.hash_password("test123")
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        # Add existing land
        existing_land = Land(user_id=user.id, name="To Be Deleted", width=50, height=50)
        test_db.add(existing_land)
        test_db.commit()

        from app.schemas.export_import import (
            ExportMetadata, ExportUserProfile, ExportLand
        )

        export_data = ExportData(
            metadata=ExportMetadata(
                export_timestamp=datetime.utcnow(),
                user_id=999
            ),
            user_profile=ExportUserProfile(),
            lands=[
                ExportLand(
                    id=1,
                    name="New Land",
                    width=100.0,
                    height=100.0,
                    created_at=datetime.utcnow()
                )
            ]
        )

        # Import in overwrite mode
        result = ImportService.import_user_data(test_db, user, export_data, ImportMode.OVERWRITE)

        assert result.success is True
        assert result.items_deleted is not None
        assert result.items_deleted > 0

        # Should only have 1 land (the imported one)
        lands = test_db.query(Land).filter(Land.user_id == user.id).all()
        assert len(lands) == 1
        assert lands[0].name == "New Land"

    def test_id_remapping_preserves_relationships(self, test_db):
        """Import should remap IDs while preserving relationships"""
        user = User(
            email="remap@example.com",
            hashed_password=AuthService.hash_password("test123")
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        from app.schemas.export_import import (
            ExportMetadata, ExportUserProfile, ExportLand, ExportGarden
        )

        # Export data with land and garden relationship
        export_data = ExportData(
            metadata=ExportMetadata(
                export_timestamp=datetime.utcnow(),
                user_id=999
            ),
            user_profile=ExportUserProfile(),
            lands=[
                ExportLand(
                    id=100,  # Old ID
                    name="Test Land",
                    width=100.0,
                    height=100.0,
                    created_at=datetime.utcnow()
                )
            ],
            gardens=[
                ExportGarden(
                    id=200,  # Old ID
                    land_id=100,  # References old land ID
                    name="Test Garden",
                    garden_type="outdoor",
                    is_hydroponic=False,
                    is_raised_bed=False,
                    created_at=datetime.utcnow()
                )
            ]
        )

        # Import in merge mode
        result = ImportService.import_user_data(test_db, user, export_data, ImportMode.MERGE)

        assert result.success is True
        assert result.id_mapping is not None

        # Check that IDs were remapped
        assert 100 in result.id_mapping["lands"]
        new_land_id = result.id_mapping["lands"][100]

        # Check that relationship was preserved with new IDs
        garden = test_db.query(Garden).filter(Garden.user_id == user.id).first()
        assert garden is not None
        assert garden.land_id == new_land_id

    def test_round_trip_export_import(self, test_db):
        """Export and then import should preserve all data"""
        # Create first user with data
        user1 = User(
            email="original@example.com",
            hashed_password=AuthService.hash_password("test123"),
            display_name="Original User",
            city="Portland"
        )
        test_db.add(user1)
        test_db.commit()
        test_db.refresh(user1)

        land = Land(user_id=user1.id, name="Original Land", width=100, height=100)
        test_db.add(land)
        test_db.commit()
        test_db.refresh(land)

        garden = Garden(
            user_id=user1.id,
            land_id=land.id,
            name="Original Garden",
            garden_type=GardenType.OUTDOOR,
            x=10.0,
            y=10.0,
            width=20.0,
            height=20.0
        )
        test_db.add(garden)
        test_db.commit()

        # Export from user1
        export_data = ExportService.export_user_data(test_db, user1)

        # Create second user
        user2 = User(
            email="destination@example.com",
            hashed_password=AuthService.hash_password("test123")
        )
        test_db.add(user2)
        test_db.commit()
        test_db.refresh(user2)

        # Import to user2
        result = ImportService.import_user_data(test_db, user2, export_data, ImportMode.MERGE)

        assert result.success is True

        # Verify data was imported correctly
        user2_lands = test_db.query(Land).filter(Land.user_id == user2.id).all()
        assert len(user2_lands) == 1
        assert user2_lands[0].name == "Original Land"

        user2_gardens = test_db.query(Garden).filter(Garden.user_id == user2.id).all()
        assert len(user2_gardens) == 1
        assert user2_gardens[0].name == "Original Garden"
        assert user2_gardens[0].land_id == user2_lands[0].id  # Relationship preserved
