import type {
  User,
  LoginResponse,
  PlantVariety,
  Garden,
  SeedBatch,
  PlantingEvent,
  Task,
  ApiError
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

  async createGarden(name: string, description?: string): Promise<Garden> {
    return this.request<Garden>('/gardens', {
      method: 'POST',
      body: JSON.stringify({ name, description }),
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
}

export const api = new ApiClient();
