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
  IrrigationSummary,
  SoilHealthSummary,
  IrrigationOverviewSummary,
  GardenRuleInsights,
  PlantingRuleInsights,
  Land,
  LandWithGardens,
  LandCreate,
  LandUpdate,
  GardenLayoutUpdate,
  IrrigationSource,
  IrrigationSourceCreate,
  IrrigationSourceUpdate,
  IrrigationZone,
  IrrigationZoneCreate,
  IrrigationZoneUpdate,
  IrrigationZoneDetails,
  WateringEvent,
  WateringEventCreate,
  WateringEventUpdate,
  IrrigationOverview,
  IrrigationInsightsResponse,
  Tree,
  TreeCreate,
  TreeUpdate,
  Structure,
  StructureCreate,
  StructureUpdate,
  StructureShadowExtent,
  GardenShadingInfo,
  GardenSunExposure,
  TreeShadowExtent,
  ExportData,
  ImportPreview,
  ImportRequest,
  ImportResult,
  SystemStats,
  CompanionAnalysisResponse
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
    zip_code?: string;
    unit_system?: 'metric' | 'imperial';
  }): Promise<User> {
    return this.request<User>('/users/me', {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  async requestPasswordReset(email: string): Promise<{ message: string; success: boolean }> {
    return this.request<{ message: string; success: boolean }>('/auth/password-reset/request', {
      method: 'POST',
      body: JSON.stringify({ email }),
    });
  }

  async confirmPasswordReset(token: string, newPassword: string): Promise<{ message: string; success: boolean }> {
    return this.request<{ message: string; success: boolean }>('/auth/password-reset/confirm', {
      method: 'POST',
      body: JSON.stringify({ token, new_password: newPassword }),
    });
  }

  async getPasswordRequirements(): Promise<{ requirements: string[] }> {
    return this.request<{ requirements: string[] }>('/auth/password-reset/requirements');
  }

  async changePassword(currentPassword: string, newPassword: string): Promise<{ message: string; success: boolean }> {
    return this.request<{ message: string; success: boolean }>('/auth/password/change', {
      method: 'POST',
      body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }),
    });
  }

  async requestPasswordResetAuthenticated(): Promise<{ message: string; success: boolean }> {
    return this.request<{ message: string; success: boolean }>('/auth/password-reset/request-authenticated', {
      method: 'POST',
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

  async getGardenSensorReadings(gardenId: number): Promise<SensorReading[]> {
    return this.request<SensorReading[]>(`/gardens/${gardenId}/sensor-readings`);
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

  async getPlantingEvents(gardenId?: number): Promise<PlantingEvent[]> {
    const query = gardenId ? `?garden_id=${gardenId}` : '';
    return this.request<PlantingEvent[]>(`/planting-events${query}`);
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

  async deletePlantingEvent(eventId: number): Promise<void> {
    await fetch(`${API_BASE_URL}/planting-events/${eventId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${this.token}`,
      },
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

  async updateSoilSample(sampleId: number, data: Partial<SoilSampleCreate>): Promise<SoilSample> {
    return this.request<SoilSample>(`/soil-samples/${sampleId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteSoilSample(sampleId: number): Promise<{message: string; deleted_sample: {id: number; garden_id: number; date_collected: string}}> {
    return this.request(`/soil-samples/${sampleId}`, {
      method: 'DELETE',
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

  // Dashboard
  async getSoilHealthSummary(gardenId?: number): Promise<SoilHealthSummary> {
    const query = gardenId ? `?garden_id=${gardenId}` : '';
    return this.request<SoilHealthSummary>(`/dashboard/soil-summary${query}`);
  }

  async getIrrigationOverviewSummary(gardenId?: number): Promise<IrrigationOverviewSummary> {
    const query = gardenId ? `?garden_id=${gardenId}` : '';
    return this.request<IrrigationOverviewSummary>(`/dashboard/irrigation-summary${query}`);
  }

  // Rule Insights (Science-Based Rule Engine)
  async getGardenRuleInsights(gardenId: number): Promise<GardenRuleInsights> {
    return this.request<GardenRuleInsights>(`/rule-insights/garden/${gardenId}`);
  }

  async getPlantingRuleInsights(plantingId: number): Promise<PlantingRuleInsights> {
    return this.request<PlantingRuleInsights>(`/rule-insights/planting/${plantingId}`);
  }

  // Land Management
  async getLands(): Promise<Land[]> {
    return this.request<Land[]>('/lands');
  }

  async getLand(landId: number): Promise<LandWithGardens> {
    return this.request<LandWithGardens>(`/lands/${landId}`);
  }

  async createLand(data: LandCreate): Promise<Land> {
    return this.request<Land>('/lands', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateLand(landId: number, data: LandUpdate): Promise<Land> {
    return this.request<Land>(`/lands/${landId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  async deleteLand(landId: number): Promise<void> {
    await fetch(`${API_BASE_URL}/lands/${landId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${this.token}`,
      },
    });
  }

  // Garden Layout
  async updateGardenLayout(gardenId: number, layout: GardenLayoutUpdate): Promise<Garden> {
    return this.request<Garden>(`/gardens/${gardenId}/layout`, {
      method: 'PUT',
      body: JSON.stringify(layout),
    });
  }

  // ========================================================================
  // IRRIGATION SYSTEM
  // ========================================================================

  // Irrigation Sources
  async createIrrigationSource(data: IrrigationSourceCreate): Promise<IrrigationSource> {
    return this.request<IrrigationSource>('/irrigation-system/sources', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getIrrigationSources(): Promise<IrrigationSource[]> {
    return this.request<IrrigationSource[]>('/irrigation-system/sources');
  }

  async getIrrigationSource(sourceId: number): Promise<IrrigationSource> {
    return this.request<IrrigationSource>(`/irrigation-system/sources/${sourceId}`);
  }

  async updateIrrigationSource(sourceId: number, data: IrrigationSourceUpdate): Promise<IrrigationSource> {
    return this.request<IrrigationSource>(`/irrigation-system/sources/${sourceId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  async deleteIrrigationSource(sourceId: number): Promise<void> {
    await fetch(`${API_BASE_URL}/irrigation-system/sources/${sourceId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${this.token}`,
      },
    });
  }

  // Irrigation Zones
  async createIrrigationZone(data: IrrigationZoneCreate): Promise<IrrigationZone> {
    return this.request<IrrigationZone>('/irrigation-system/zones', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getIrrigationZones(): Promise<IrrigationZone[]> {
    return this.request<IrrigationZone[]>('/irrigation-system/zones');
  }

  async getIrrigationZone(zoneId: number): Promise<IrrigationZone> {
    return this.request<IrrigationZone>(`/irrigation-system/zones/${zoneId}`);
  }

  async updateIrrigationZone(zoneId: number, data: IrrigationZoneUpdate): Promise<IrrigationZone> {
    return this.request<IrrigationZone>(`/irrigation-system/zones/${zoneId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  async deleteIrrigationZone(zoneId: number): Promise<void> {
    await fetch(`${API_BASE_URL}/irrigation-system/zones/${zoneId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${this.token}`,
      },
    });
  }

  async getIrrigationZoneDetails(zoneId: number): Promise<IrrigationZoneDetails> {
    return this.request<IrrigationZoneDetails>(`/irrigation-system/zones/${zoneId}/details`);
  }

  // Watering Events
  async createWateringEvent(data: WateringEventCreate): Promise<WateringEvent> {
    return this.request<WateringEvent>('/irrigation-system/events', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getWateringEvents(zoneId?: number, days?: number): Promise<WateringEvent[]> {
    const params = new URLSearchParams();
    if (zoneId !== undefined) params.append('zone_id', zoneId.toString());
    if (days !== undefined) params.append('days', days.toString());
    const query = params.toString() ? `?${params.toString()}` : '';
    return this.request<WateringEvent[]>(`/irrigation-system/events${query}`);
  }

  async getWateringEvent(eventId: number): Promise<WateringEvent> {
    return this.request<WateringEvent>(`/irrigation-system/events/${eventId}`);
  }

  async updateWateringEvent(eventId: number, data: WateringEventUpdate): Promise<WateringEvent> {
    return this.request<WateringEvent>(`/irrigation-system/events/${eventId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  async deleteWateringEvent(eventId: number): Promise<void> {
    await fetch(`${API_BASE_URL}/irrigation-system/events/${eventId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${this.token}`,
      },
    });
  }

  // High-level operations
  async getIrrigationOverview(): Promise<IrrigationOverview> {
    return this.request<IrrigationOverview>('/irrigation-system/overview');
  }

  async getIrrigationInsights(): Promise<IrrigationInsightsResponse> {
    return this.request<IrrigationInsightsResponse>('/irrigation-system/insights');
  }

  async assignGardenToZone(gardenId: number, zoneId: number | null): Promise<{ message: string }> {
    const params = zoneId !== null ? `?zone_id=${zoneId}` : '';
    return this.request<{ message: string }>(`/irrigation-system/gardens/${gardenId}/assign-zone${params}`, {
      method: 'POST',
    });
  }

  // ========================================================================
  // TREE SHADING
  // ========================================================================

  // Trees
  async createTree(data: TreeCreate): Promise<Tree> {
    return this.request<Tree>('/trees', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getTrees(): Promise<Tree[]> {
    return this.request<Tree[]>('/trees');
  }

  async getTree(treeId: number): Promise<Tree> {
    return this.request<Tree>(`/trees/${treeId}`);
  }

  async getTreesOnLand(landId: number): Promise<Tree[]> {
    return this.request<Tree[]>(`/trees/land/${landId}`);
  }

  async updateTree(treeId: number, data: TreeUpdate): Promise<Tree> {
    return this.request<Tree>(`/trees/${treeId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  async deleteTree(treeId: number): Promise<void> {
    await fetch(`${API_BASE_URL}/trees/${treeId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${this.token}`,
      },
    });
  }

  // Garden shading
  async getGardenShading(gardenId: number): Promise<GardenShadingInfo> {
    return this.request<GardenShadingInfo>(`/gardens/${gardenId}/shading`);
  }

  // Sun exposure (seasonal sun path model)
  async getGardenSunExposure(gardenId: number): Promise<GardenSunExposure> {
    return this.request<GardenSunExposure>(`/gardens/${gardenId}/sun-exposure`);
  }

  async getTreeShadowExtent(treeId: number, latitude?: number, hour?: number): Promise<TreeShadowExtent> {
    const params = new URLSearchParams();
    if (latitude !== undefined) params.append('latitude', latitude.toString());
    if (hour !== undefined) params.append('hour', hour.toString());
    const queryString = params.toString() ? `?${params.toString()}` : '';
    return this.request<TreeShadowExtent>(`/trees/${treeId}/shadow-extent${queryString}`);
  }

  // Structures
  async createStructure(data: StructureCreate): Promise<Structure> {
    return this.request<Structure>('/structures', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getStructures(): Promise<Structure[]> {
    return this.request<Structure[]>('/structures');
  }

  async getStructure(structureId: number): Promise<Structure> {
    return this.request<Structure>(`/structures/${structureId}`);
  }

  async getStructuresOnLand(landId: number): Promise<Structure[]> {
    return this.request<Structure[]>(`/structures/land/${landId}`);
  }

  async updateStructure(structureId: number, data: StructureUpdate): Promise<Structure> {
    return this.request<Structure>(`/structures/${structureId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  async deleteStructure(structureId: number): Promise<void> {
    await fetch(`${API_BASE_URL}/structures/${structureId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${this.token}`,
      },
    });
  }

  async getStructureShadowExtent(structureId: number, latitude?: number, hour?: number): Promise<StructureShadowExtent> {
    const params = new URLSearchParams();
    if (latitude !== undefined) params.append('latitude', latitude.toString());
    if (hour !== undefined) params.append('hour', hour.toString());
    const queryString = params.toString() ? `?${params.toString()}` : '';
    return this.request<StructureShadowExtent>(`/structures/${structureId}/shadow-extent${queryString}`);
  }

  // ========================================================================
  // DATA EXPORT/IMPORT
  // ========================================================================

  async exportData(includeSensorReadings: boolean = false): Promise<ExportData> {
    const params = includeSensorReadings ? '?include_sensor_readings=true' : '';
    return this.request<ExportData>(`/export-import/export${params}`);
  }

  async previewImport(data: ExportData, _mode: 'dry_run' | 'merge' | 'overwrite' = 'dry_run'): Promise<ImportPreview> {
    return this.request<ImportPreview>('/export-import/import/preview', {
      method: 'POST',
      body: JSON.stringify(data),
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  async importData(request: ImportRequest): Promise<ImportResult> {
    return this.request<ImportResult>('/export-import/import', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  // ========================================================================
  // SYSTEM STATS (Admin-only)
  // ========================================================================

  async getSystemStats(): Promise<SystemStats> {
    return this.request<SystemStats>('/system/stats');
  }

  // ========================================================================
  // COMPANION PLANTING
  // ========================================================================

  async getCompanionAnalysis(gardenId: number): Promise<CompanionAnalysisResponse> {
    return this.request<CompanionAnalysisResponse>(`/gardens/${gardenId}/companions`);
  }
}

export const api = new ApiClient();
