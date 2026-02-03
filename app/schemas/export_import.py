"""Export/Import schemas for user data portability"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# Current schema version - increment when format changes
EXPORT_SCHEMA_VERSION = "1.0.0"


class ExportMetadata(BaseModel):
    """Metadata for export file"""
    schema_version: str = Field(default=EXPORT_SCHEMA_VERSION, description="Export schema version")
    app_version: str = Field(default="0.1.0", description="Application version")
    export_timestamp: datetime = Field(description="When this export was created")
    user_id: int = Field(description="Original user ID (for reference only)")
    include_sensor_readings: bool = Field(default=False, description="Whether sensor readings are included")


class ExportUserProfile(BaseModel):
    """Non-sensitive user profile data"""
    display_name: Optional[str] = None
    city: Optional[str] = None
    zip_code: Optional[str] = None
    usda_zone: Optional[str] = None
    gardening_preferences: Optional[str] = None
    # Explicitly NOT including: email, password, tokens


class ExportLand(BaseModel):
    """Land plot data for export"""
    id: int  # Original ID for relationship mapping
    name: str
    width: float
    height: float
    created_at: datetime


class ExportGarden(BaseModel):
    """Garden data for export"""
    id: int  # Original ID
    land_id: Optional[int] = None  # Reference to land
    name: str
    description: Optional[str] = None
    garden_type: str
    location: Optional[str] = None
    light_source_type: Optional[str] = None
    light_hours_per_day: Optional[float] = None
    temp_min_f: Optional[float] = None
    temp_max_f: Optional[float] = None
    humidity_min_percent: Optional[float] = None
    humidity_max_percent: Optional[float] = None
    container_type: Optional[str] = None
    grow_medium: Optional[str] = None
    is_hydroponic: bool
    hydro_system_type: Optional[str] = None
    reservoir_size_liters: Optional[float] = None
    nutrient_schedule: Optional[str] = None
    ph_min: Optional[float] = None
    ph_max: Optional[float] = None
    ec_min: Optional[float] = None
    ec_max: Optional[float] = None
    ppm_min: Optional[int] = None
    ppm_max: Optional[int] = None
    water_temp_min_f: Optional[float] = None
    water_temp_max_f: Optional[float] = None
    # Spatial layout
    x: Optional[float] = None
    y: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    # Irrigation
    irrigation_zone_id: Optional[int] = None
    mulch_depth_inches: Optional[float] = None
    is_raised_bed: bool
    soil_texture_override: Optional[str] = None
    created_at: datetime


class ExportTree(BaseModel):
    """Tree data for export"""
    id: int
    land_id: int
    name: str
    species_id: Optional[int] = None
    x: float
    y: float
    canopy_radius: float
    height: Optional[float] = None
    created_at: datetime


class ExportPlanting(BaseModel):
    """Planting event data for export"""
    id: int
    garden_id: int
    plant_variety_id: int
    planting_date: str
    planting_method: str
    plant_count: Optional[int] = None
    location_in_garden: Optional[str] = None
    health_status: Optional[str] = None
    plant_notes: Optional[str] = None


class ExportSoilSample(BaseModel):
    """Soil sample data for export"""
    id: int
    garden_id: Optional[int] = None
    planting_event_id: Optional[int] = None
    ph: float
    nitrogen_ppm: Optional[float] = None
    phosphorus_ppm: Optional[float] = None
    potassium_ppm: Optional[float] = None
    organic_matter_percent: Optional[float] = None
    moisture_percent: Optional[float] = None
    date_collected: str
    notes: Optional[str] = None


class ExportIrrigationSource(BaseModel):
    """Irrigation source data for export"""
    id: int
    name: str
    source_type: str
    flow_capacity_lpm: Optional[float] = None
    notes: Optional[str] = None
    created_at: datetime


class ExportIrrigationZone(BaseModel):
    """Irrigation zone data for export"""
    id: int
    irrigation_source_id: Optional[int] = None
    name: str
    delivery_type: str
    schedule: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    created_at: datetime


class ExportSensorReading(BaseModel):
    """Sensor reading data for export (optional - can be large)"""
    id: int
    garden_id: int
    reading_date: str
    temperature_f: Optional[float] = None
    humidity_percent: Optional[float] = None
    light_hours: Optional[float] = None
    ph_level: Optional[float] = None
    ec_ms_cm: Optional[float] = None
    ppm: Optional[int] = None
    water_temp_f: Optional[float] = None
    created_at: datetime


class ExportData(BaseModel):
    """Complete export data structure"""
    metadata: ExportMetadata
    user_profile: ExportUserProfile
    lands: List[ExportLand] = Field(default_factory=list)
    gardens: List[ExportGarden] = Field(default_factory=list)
    trees: List[ExportTree] = Field(default_factory=list)
    plantings: List[ExportPlanting] = Field(default_factory=list)
    soil_samples: List[ExportSoilSample] = Field(default_factory=list)
    irrigation_sources: List[ExportIrrigationSource] = Field(default_factory=list)
    irrigation_zones: List[ExportIrrigationZone] = Field(default_factory=list)
    sensor_readings: List[ExportSensorReading] = Field(default_factory=list)


class ImportMode(str):
    """Import mode options"""
    DRY_RUN = "dry_run"
    MERGE = "merge"
    OVERWRITE = "overwrite"


class ImportRequest(BaseModel):
    """Import request with mode and data"""
    mode: str = Field(description="Import mode: dry_run, merge, or overwrite")
    data: ExportData


class ImportValidationIssue(BaseModel):
    """Validation issue found during import"""
    severity: str = Field(description="info, warning, or error")
    category: str = Field(description="Category of issue")
    message: str
    details: Optional[Dict[str, Any]] = None


class ImportPreview(BaseModel):
    """Preview of what would be imported"""
    valid: bool
    issues: List[ImportValidationIssue] = Field(default_factory=list)
    counts: Dict[str, int] = Field(description="Count of each entity type")
    warnings: List[str] = Field(default_factory=list)
    schema_version_compatible: bool
    would_overwrite: Optional[int] = Field(None, description="Number of items that would be deleted in overwrite mode")


class ImportResult(BaseModel):
    """Result of import operation"""
    success: bool
    mode: str
    items_imported: Dict[str, int] = Field(description="Count of imported items by type")
    items_updated: Dict[str, int] = Field(default_factory=dict, description="Count of updated items (merge mode)")
    items_deleted: Optional[int] = Field(None, description="Items deleted (overwrite mode)")
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    id_mapping: Optional[Dict[str, Dict[int, int]]] = Field(
        None,
        description="Mapping of old IDs to new IDs for reference"
    )
