// API Types
export interface User {
  id: number;
  email: string;
  display_name?: string;
  avatar_url?: string;
  city?: string;
  gardening_preferences?: string;
  usda_zone?: string;
  zip_code?: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface PlantVariety {
  id: number;
  common_name: string;
  scientific_name?: string;
  variety_name?: string;
  days_to_harvest?: number;
  water_requirement?: 'low' | 'medium' | 'high';
  photo_url?: string;
  tags?: string;
  description?: string;
}

export interface Garden {
  id: number;
  name: string;
  description?: string;
  garden_type: 'outdoor' | 'indoor';
  location?: string;
  light_source_type?: 'led' | 'fluorescent' | 'natural_supplement' | 'hps' | 'mh';
  light_hours_per_day?: number;
  temp_min_f?: number;
  temp_max_f?: number;
  humidity_min_percent?: number;
  humidity_max_percent?: number;
  container_type?: string;
  grow_medium?: string;
  // Hydroponics-specific fields
  is_hydroponic: boolean;
  hydro_system_type?: 'nft' | 'dwc' | 'ebb_flow' | 'aeroponics' | 'drip' | 'wick';
  reservoir_size_liters?: number;
  nutrient_schedule?: string;
  ph_min?: number;
  ph_max?: number;
  ec_min?: number;
  ec_max?: number;
  ppm_min?: number;
  ppm_max?: number;
  water_temp_min_f?: number;
  water_temp_max_f?: number;
  // Spatial layout fields
  land_id?: number;
  x?: number;
  y?: number;
  width?: number;
  height?: number;
  // Irrigation system fields
  irrigation_zone_id?: number;
  mulch_depth_inches?: number;
  is_raised_bed: boolean;
  soil_texture_override?: string;
}

export interface SensorReading {
  id: number;
  user_id: number;
  garden_id: number;
  reading_date: string;
  // Indoor garden readings
  temperature_f?: number;
  humidity_percent?: number;
  light_hours?: number;
  // Hydroponics-specific readings
  ph_level?: number;
  ec_ms_cm?: number;
  ppm?: number;
  water_temp_f?: number;
  created_at?: string;
}

export interface SeedBatch {
  id: number;
  plant_variety_id: number;
  plant_variety?: PlantVariety;
  source?: string;
  harvest_year?: number;
  quantity?: number;
  preferred_germination_method?: string;
  created_at?: string;
}

export interface PlantingEvent {
  id: number;
  garden_id: number;
  plant_variety_id: number;
  plant_variety?: PlantVariety;
  planting_date: string;
  planting_method: 'direct_sow' | 'transplant';
  plant_count?: number;
  location_in_garden?: string;
  health_status?: 'healthy' | 'stressed' | 'diseased';
  plant_notes?: string;
}

export interface Task {
  id: number;
  task_type: string;
  title: string;
  description?: string;
  due_date: string;
  status: 'pending' | 'completed' | 'skipped';
  task_source: 'auto_generated' | 'manual';
  priority: 'low' | 'medium' | 'high';
  is_recurring: boolean;
  recurrence_frequency?: 'daily' | 'weekly' | 'biweekly' | 'monthly';
  parent_task_id?: number;
  completed_date?: string;
}

export interface ApiError {
  error: {
    code: string;
    message: string;
  };
}

export interface PlantingInGarden {
  id: number;
  plant_variety_id: number;
  plant_name: string;
  variety_name?: string;
  planting_date: string;
  planting_method: string;
  plant_count?: number;
  location_in_garden?: string;
  health_status?: string;
  expected_harvest_date?: string;
  days_to_harvest?: number;
  status: string; // 'pending', 'growing', 'ready_to_harvest', 'harvested'
}

export interface TaskSummary {
  id: number;
  title: string;
  task_type: string;
  priority: string;
  due_date: string;
  status: string;
  planting_event_id?: number;
}

export interface GardenStats {
  total_plantings: number;
  active_plantings: number;
  total_tasks: number;
  pending_tasks: number;
  high_priority_tasks: number;
  upcoming_harvests: number;
}

export interface GardenDetails {
  garden: Garden;
  plantings: PlantingInGarden[];
  tasks: TaskSummary[];
  stats: GardenStats;
}

// Soil Tracking Types
export interface SoilSample {
  id: number;
  user_id: number;
  garden_id?: number;
  planting_event_id?: number;
  ph: number;
  nitrogen_ppm?: number;
  phosphorus_ppm?: number;
  potassium_ppm?: number;
  organic_matter_percent?: number;
  moisture_percent?: number;
  date_collected: string;
  notes?: string;
  garden_name?: string;
  plant_name?: string;
  recommendations: SoilRecommendation[];
}

export interface SoilRecommendation {
  parameter: string;
  current_value: number;
  optimal_range: string;
  status: 'optimal' | 'low' | 'high' | 'critical';
  recommendation: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
}

export interface SoilSampleCreate {
  garden_id?: number;
  planting_event_id?: number;
  ph: number;
  nitrogen_ppm?: number;
  phosphorus_ppm?: number;
  potassium_ppm?: number;
  organic_matter_percent?: number;
  moisture_percent?: number;
  date_collected: string;
  notes?: string;
}

export interface SoilSampleList {
  samples: SoilSample[];
  total: number;
  latest_sample?: SoilSample;
}

// Irrigation Tracking Types
export type IrrigationMethod = 'drip' | 'sprinkler' | 'hand_watering' | 'soaker_hose' | 'flood' | 'misting';

export interface IrrigationEvent {
  id: number;
  user_id: number;
  garden_id?: number;
  planting_event_id?: number;
  irrigation_date: string;
  water_volume_liters?: number;
  irrigation_method: IrrigationMethod;
  duration_minutes?: number;
  notes?: string;
  garden_name?: string;
  plant_name?: string;
}

export interface IrrigationEventCreate {
  garden_id?: number;
  planting_event_id?: number;
  irrigation_date: string;
  water_volume_liters?: number;
  irrigation_method: IrrigationMethod;
  duration_minutes?: number;
  notes?: string;
}

export interface IrrigationRecommendation {
  plant_name: string;
  days_since_last_watering?: number;
  recommended_frequency_days: number;
  recommended_volume_liters?: number;
  status: 'on_schedule' | 'overdue' | 'overwatered' | 'no_data';
  recommendation: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
}

export interface IrrigationSummary {
  total_events: number;
  total_volume_liters: number;
  last_irrigation_date?: string;
  days_since_last_irrigation?: number;
  average_volume_per_event?: number;
  most_common_method?: IrrigationMethod;
  recommendations: IrrigationRecommendation[];
}

export interface IrrigationEventList {
  events: IrrigationEvent[];
  summary: IrrigationSummary;
}

// Dashboard Types
export type SoilHealthStatus = 'in_range' | 'low' | 'high' | 'unknown';

export interface SoilParameterStatus {
  value?: number;
  status: SoilHealthStatus;
  unit: string;
}

export interface SoilTrendPoint {
  date: string;
  value: number;
}

export interface SoilRecommendationSummary {
  severity: 'info' | 'warning' | 'critical';
  message: string;
  parameter: string;
}

export interface SoilHealthSummary {
  garden_id?: number;
  garden_name?: string;
  last_sample_date?: string;
  ph?: SoilParameterStatus;
  nitrogen?: SoilParameterStatus;
  phosphorus?: SoilParameterStatus;
  potassium?: SoilParameterStatus;
  organic_matter?: SoilParameterStatus;
  moisture?: SoilParameterStatus;
  ph_trend: SoilTrendPoint[];
  moisture_trend: SoilTrendPoint[];
  recommendations: SoilRecommendationSummary[];
  overall_health: 'good' | 'fair' | 'poor' | 'unknown';
  total_samples: number;
}

export interface IrrigationAlert {
  type: 'under_watering' | 'over_watering' | 'moisture_mismatch';
  severity: 'info' | 'warning' | 'critical';
  message: string;
  garden_id?: number;
  planting_event_id?: number;
}

export interface IrrigationWeeklySummary {
  total_volume_liters: number;
  event_count: number;
  average_interval_days?: number;
}

export interface IrrigationOverviewSummary {
  garden_id?: number;
  garden_name?: string;
  last_irrigation_date?: string;
  last_irrigation_volume?: number;
  last_irrigation_method?: string;
  days_since_last_watering?: number;
  weekly: IrrigationWeeklySummary;
  alerts: IrrigationAlert[];
  total_events: number;
}

// Rule Insights Types (Science-Based Rule Engine)
export type RuleSeverity = 'info' | 'warning' | 'critical';
export type RuleCategory = 'water_stress' | 'soil_chemistry' | 'temperature_stress' | 'light_stress' | 'growth_stage' | 'pest_disease' | 'nutrient_timing';

export interface RuleResult {
  rule_id: string;
  category: RuleCategory;
  title: string;
  triggered: boolean;
  severity: RuleSeverity;
  confidence: number;
  explanation: string;
  scientific_rationale: string;
  recommended_action?: string;
  measured_value?: number;
  optimal_range?: string;
  deviation_severity?: string;
  evaluation_time: string;
  references: string[];
}

export interface GardenRuleInsights {
  garden_id: number;
  garden_name: string;
  evaluation_time: string;
  triggered_rules: RuleResult[];
  rules_by_severity: {
    critical: number;
    warning: number;
    info: number;
  };
  rules_by_category: Record<RuleCategory, number>;
}

export interface PlantingRuleInsights {
  planting_event_id: number;
  plant_name: string;
  garden_name: string;
  evaluation_time: string;
  triggered_rules: RuleResult[];
  rules_by_severity: {
    critical: number;
    warning: number;
    info: number;
  };
  rules_by_category: Record<RuleCategory, number>;
}

// Land Layout Types
export interface Land {
  id: number;
  user_id: number;
  name: string;
  width: number;
  height: number;
  created_at: string;
}

export interface GardenSpatialInfo {
  id: number;
  name: string;
  land_id?: number;
  x?: number;
  y?: number;
  width?: number;
  height?: number;
}

export interface LandWithGardens extends Land {
  gardens: GardenSpatialInfo[];
}

export interface LandCreate {
  name: string;
  width: number;
  height: number;
}

export interface LandUpdate {
  name?: string;
  width?: number;
  height?: number;
}

export interface GardenLayoutUpdate {
  land_id?: number;
  x?: number;
  y?: number;
  width?: number;
  height?: number;
}

// ============================================================================
// TREE SHADING TYPES
// ============================================================================

export interface Tree {
  id: number;
  user_id: number;
  land_id: number;
  name: string;
  species_id?: number;
  species_common_name?: string;
  species_scientific_name?: string;
  x: number;
  y: number;
  canopy_radius: number;
  height?: number;
  created_at: string;
  updated_at?: string;
}

export interface TreeCreate {
  land_id: number;
  name: string;
  species_id?: number;
  x: number;
  y: number;
  canopy_radius: number;
  height?: number;
}

export interface TreeUpdate {
  name?: string;
  species_id?: number;
  x?: number;
  y?: number;
  canopy_radius?: number;
  height?: number;
}

export interface ShadingContribution {
  tree_id: number;
  tree_name: string;
  shade_contribution: number;
  intersection_area: number;
  average_intensity: number;
}

export interface GardenShadingInfo {
  garden_id: number;
  sun_exposure_score: number;
  sun_exposure_category: 'full_sun' | 'partial_sun' | 'shade';
  total_shade_factor: number;
  baseline_sun_exposure: number;
  contributing_trees: ShadingContribution[];
}

// ============================================================================
// IRRIGATION SYSTEM TYPES
// ============================================================================

export interface IrrigationSource {
  id: number;
  user_id: number;
  name: string;
  source_type: 'city' | 'well' | 'rain' | 'manual';
  flow_capacity_lpm?: number;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface IrrigationSourceCreate {
  name: string;
  source_type: 'city' | 'well' | 'rain' | 'manual';
  flow_capacity_lpm?: number;
  notes?: string;
}

export interface IrrigationSourceUpdate {
  name?: string;
  source_type?: 'city' | 'well' | 'rain' | 'manual';
  flow_capacity_lpm?: number;
  notes?: string;
}

export interface IrrigationZoneSchedule {
  frequency_days?: number;
  duration_minutes?: number;
  time_of_day?: string;
  [key: string]: any; // Allow additional fields
}

export interface IrrigationZone {
  id: number;
  user_id: number;
  irrigation_source_id?: number;
  name: string;
  delivery_type: 'drip' | 'sprinkler' | 'soaker' | 'manual';
  schedule?: IrrigationZoneSchedule;
  notes?: string;
  created_at: string;
  updated_at: string;
  garden_count?: number; // Populated by backend
}

export interface IrrigationZoneCreate {
  name: string;
  irrigation_source_id?: number;
  delivery_type: 'drip' | 'sprinkler' | 'soaker' | 'manual';
  schedule?: IrrigationZoneSchedule;
  notes?: string;
}

export interface IrrigationZoneUpdate {
  name?: string;
  irrigation_source_id?: number;
  delivery_type?: 'drip' | 'sprinkler' | 'soaker' | 'manual';
  schedule?: IrrigationZoneSchedule;
  notes?: string;
}

export interface WateringEvent {
  id: number;
  user_id: number;
  irrigation_zone_id: number;
  watered_at: string;
  duration_minutes: number;
  estimated_volume_liters?: number;
  is_manual: boolean;
  notes?: string;
  created_at: string;
}

export interface WateringEventCreate {
  irrigation_zone_id: number;
  watered_at: string;
  duration_minutes: number;
  estimated_volume_liters?: number;
  is_manual?: boolean;
  notes?: string;
}

export interface WateringEventUpdate {
  watered_at?: string;
  duration_minutes?: number;
  estimated_volume_liters?: number;
  is_manual?: boolean;
  notes?: string;
}

export interface IrrigationInsight {
  rule_id: string;
  severity: 'info' | 'warning' | 'critical';
  title: string;
  explanation: string;
  suggested_action: string;
  affected_zones: number[];
  affected_gardens: number[];
}

export interface IrrigationInsightsResponse {
  insights: IrrigationInsight[];
  total_count: number;
  by_severity: {
    critical: number;
    warning: number;
    info: number;
  };
}

export interface UpcomingWatering {
  zone_id: number;
  zone_name: string;
  next_watering: string;
  days_until: number;
  status: 'upcoming' | 'today' | 'overdue';
  last_watered?: string;
}

export interface IrrigationOverview {
  zones: Array<{
    zone: IrrigationZone;
    garden_count: number;
  }>;
  sources: IrrigationSource[];
  recent_events: WateringEvent[];
  upcoming_waterings: UpcomingWatering[];
}

export interface ZoneStatistics {
  total_events: number;
  avg_duration_minutes: number;
  total_duration_hours: number;
  manual_count: number;
  automated_count: number;
}

export interface IrrigationZoneDetails {
  zone: IrrigationZone;
  gardens: Garden[];
  recent_events: WateringEvent[];
  statistics: ZoneStatistics;
}

// ============================================================================
// DATA EXPORT/IMPORT TYPES
// ============================================================================

export interface ExportData {
  metadata: {
    schema_version: string;
    app_version: string;
    export_timestamp: string;
    user_id: number;
    include_sensor_readings: boolean;
  };
  user_profile: {
    display_name?: string;
    city?: string;
    zip_code?: string;
    usda_zone?: string;
    gardening_preferences?: string;
  };
  lands: any[];
  gardens: any[];
  trees: any[];
  plantings: any[];
  soil_samples: any[];
  irrigation_sources: any[];
  irrigation_zones: any[];
  watering_events: any[];
  sensor_readings: any[];
}

export interface ImportValidationIssue {
  severity: 'info' | 'warning' | 'error';
  category: string;
  message: string;
  details?: any;
}

export interface ImportPreview {
  valid: boolean;
  issues: ImportValidationIssue[];
  counts: Record<string, number>;
  warnings: string[];
  schema_version_compatible: boolean;
  would_overwrite?: number;
}

export interface ImportRequest {
  mode: 'dry_run' | 'merge' | 'overwrite';
  data: ExportData;
}

export interface ImportResult {
  success: boolean;
  mode: string;
  items_imported: Record<string, number>;
  items_updated?: Record<string, number>;
  items_deleted?: number;
  errors: string[];
  warnings: string[];
  id_mapping?: Record<string, Record<number, number>>;
}
