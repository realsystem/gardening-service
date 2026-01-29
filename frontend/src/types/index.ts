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
