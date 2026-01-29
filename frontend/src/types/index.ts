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
