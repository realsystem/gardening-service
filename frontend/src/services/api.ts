import type {
  User,
  LoginResponse,
  PlantVariety,
  Garden,
  SeedBatch,
  PlantingEvent,
  Task,
  SensorReading,
  ApiError,
  GardenDetails,
  PlantingInGarden,
  SoilSample,
  SoilSampleCreate,
  SoilSampleList,
  IrrigationEvent,
  IrrigationEventCreate,
  IrrigationEventList,
  IrrigationSummary
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080';

class ApiClient {
  private token: string | null = null;

  setToken(token: string) {
    this.token = token;
  }

  clearToken() {
    this.token = null;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string>),
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.error?.message || 'Request failed');
    }

    return response.json();
  }

  // Auth
  async register(email: string, password: string, zipCode: string): Promise<User> {
    return this.request<User>('/users', {
      method: 'POST',
      body: JSON.stringify({ email, password, zip_code: zipCode }),
    });
  }

  async login(email: string, password: string): Promise<LoginResponse> {
    return this.request<LoginResponse>('/users/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  }

  async getCurrentUser(): Promise<User> {
    return this.request<User>('/users/me');
  }

  async updateProfile(data: {
    display_name?: string;
    avatar_url?: string;
    city?: string;
    gardening_preferences?: string;
  }): Promise<User> {
    return this.request<User>('/users/me', {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  // Gardens
  async getGardens(): Promise<Garden[]> {
    return this.request<Garden[]>('/gardens');
  }

  async createGarden(data: {
    name: string;
    description?: string;
    garden_type?: 'outdoor' | 'indoor';
    location?: string;
    light_source_type?: 'led' | 'fluorescent' | 'natural_supplement' | 'hps' | 'mh';
    light_hours_per_day?: number;
    temp_min_f?: number;
    temp_max_f?: number;
    humidity_min_percent?: number;
    humidity_max_percent?: number;
    container_type?: string;
    grow_medium?: string;
    is_hydroponic?: boolean;
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
  }): Promise<Garden> {
    return this.request<Garden>('/gardens', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getGardenDetails(gardenId: number): Promise<GardenDetails> {
    return this.request<GardenDetails>(`/gardens/${gardenId}`);
  }

  async getGardenPlantings(gardenId: number): Promise<PlantingInGarden[]> {
    return this.request<PlantingInGarden[]>(`/gardens/${gardenId}/plantings`);
  }

  async deleteGarden(gardenId: number): Promise<void> {
    await fetch(`${API_BASE_URL}/gardens/${gardenId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${this.token}`,
      },
    });
  }

  // Plant Varieties
  async getPlantVarieties(search?: string): Promise<PlantVariety[]> {
    const query = search ? `?search=${encodeURIComponent(search)}` : '';
    return this.request<PlantVariety[]>(`/plant-varieties${query}`);
  }

  // Seed Batches
  async getSeedBatches(): Promise<SeedBatch[]> {
    return this.request<SeedBatch[]>('/seed-batches');
  }

  async createSeedBatch(data: {
    plant_variety_id: number;
    source?: string;
    harvest_year?: number;
    quantity?: number;
  }): Promise<SeedBatch> {
    return this.request<SeedBatch>('/seed-batches', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async deleteSeedBatch(batchId: number): Promise<void> {
    await fetch(`${API_BASE_URL}/seed-batches/${batchId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${this.token}`,
      },
    });
  }

  // Planting Events
  async createPlantingEvent(data: {
    garden_id: number;
    plant_variety_id: number;
    planting_date: string;
    planting_method: 'direct_sow' | 'transplant';
    plant_count?: number;
    location_in_garden?: string;
    health_status?: 'healthy' | 'stressed' | 'diseased';
    plant_notes?: string;
  }): Promise<PlantingEvent> {
    return this.request<PlantingEvent>('/planting-events', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updatePlantingEvent(eventId: number, data: {
    plant_count?: number;
    location_in_garden?: string;
    health_status?: 'healthy' | 'stressed' | 'diseased';
    plant_notes?: string;
  }): Promise<PlantingEvent> {
    return this.request<PlantingEvent>(`/planting-events/${eventId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  // Tasks
  async getTasks(status?: string): Promise<Task[]> {
    const query = status ? `?status=${status}` : '';
    return this.request<Task[]>(`/tasks${query}`);
  }

  async createTask(data: {
    planting_event_id?: number;
    task_type: string;
    title: string;
    description?: string;
    due_date: string;
    priority?: 'low' | 'medium' | 'high';
    is_recurring?: boolean;
    recurrence_frequency?: 'daily' | 'weekly' | 'biweekly' | 'monthly';
  }): Promise<Task> {
    return this.request<Task>('/tasks', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateTask(taskId: number, data: {
    title?: string;
    description?: string;
    due_date?: string;
    priority?: 'low' | 'medium' | 'high';
  }): Promise<Task> {
    return this.request<Task>(`/tasks/${taskId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  async completeTask(taskId: number, completedDate: string, notes?: string): Promise<Task> {
    return this.request<Task>(`/tasks/${taskId}/complete`, {
      method: 'POST',
      body: JSON.stringify({ completed_date: completedDate, notes }),
    });
  }

  // Sensor Readings
  async getSensorReadings(gardenId?: number, startDate?: string, endDate?: string): Promise<SensorReading[]> {
    const params = new URLSearchParams();
    if (gardenId) params.append('garden_id', gardenId.toString());
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    const query = params.toString() ? `?${params.toString()}` : '';
    return this.request<SensorReading[]>(`/sensor-readings${query}`);
  }

  async createSensorReading(data: {
    garden_id: number;
    reading_date: string;
    temperature_f?: number;
    humidity_percent?: number;
    light_hours?: number;
    ph_level?: number;
    ec_ms_cm?: number;
    ppm?: number;
    water_temp_f?: number;
  }): Promise<SensorReading> {
    return this.request<SensorReading>('/sensor-readings', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async deleteSensorReading(readingId: number): Promise<void> {
    await fetch(`${API_BASE_URL}/sensor-readings/${readingId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${this.token}`,
      },
    });
  }

  // Soil Samples
  async getSoilSamples(params?: {
    garden_id?: number;
    planting_event_id?: number;
    start_date?: string;
    end_date?: string;
  }): Promise<SoilSampleList> {
    const searchParams = new URLSearchParams();
    if (params?.garden_id) searchParams.append('garden_id', params.garden_id.toString());
    if (params?.planting_event_id) searchParams.append('planting_event_id', params.planting_event_id.toString());
    if (params?.start_date) searchParams.append('start_date', params.start_date);
    if (params?.end_date) searchParams.append('end_date', params.end_date);
    const query = searchParams.toString() ? `?${searchParams.toString()}` : '';
    return this.request<SoilSampleList>(`/soil-samples${query}`);
  }

  async getSoilSample(sampleId: number): Promise<SoilSample> {
    return this.request<SoilSample>(`/soil-samples/${sampleId}`);
  }

  async createSoilSample(data: SoilSampleCreate): Promise<SoilSample> {
    return this.request<SoilSample>('/soil-samples', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async deleteSoilSample(sampleId: number): Promise<void> {
    await fetch(`${API_BASE_URL}/soil-samples/${sampleId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${this.token}`,
      },
    });
  }

  // Irrigation Events
  async getIrrigationEvents(params?: {
    garden_id?: number;
    planting_event_id?: number;
    start_date?: string;
    end_date?: string;
    days?: number;
  }): Promise<IrrigationEventList> {
    const searchParams = new URLSearchParams();
    if (params?.garden_id) searchParams.append('garden_id', params.garden_id.toString());
    if (params?.planting_event_id) searchParams.append('planting_event_id', params.planting_event_id.toString());
    if (params?.start_date) searchParams.append('start_date', params.start_date);
    if (params?.end_date) searchParams.append('end_date', params.end_date);
    if (params?.days) searchParams.append('days', params.days.toString());
    const query = searchParams.toString() ? `?${searchParams.toString()}` : '';
    return this.request<IrrigationEventList>(`/irrigation${query}`);
  }

  async getIrrigationSummary(params: {
    garden_id?: number;
    planting_event_id?: number;
    days?: number;
  }): Promise<IrrigationSummary> {
    const searchParams = new URLSearchParams();
    if (params.garden_id) searchParams.append('garden_id', params.garden_id.toString());
    if (params.planting_event_id) searchParams.append('planting_event_id', params.planting_event_id.toString());
    if (params.days) searchParams.append('days', params.days.toString());
    const query = searchParams.toString() ? `?${searchParams.toString()}` : '';
    return this.request<IrrigationSummary>(`/irrigation/summary${query}`);
  }

  async createIrrigationEvent(data: IrrigationEventCreate): Promise<IrrigationEvent> {
    return this.request<IrrigationEvent>('/irrigation', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async deleteIrrigationEvent(eventId: number): Promise<void> {
    await fetch(`${API_BASE_URL}/irrigation/${eventId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${this.token}`,
      },
    });
  }
}

export const api = new ApiClient();
