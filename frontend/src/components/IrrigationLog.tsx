import { useState, useEffect } from 'react';
import { api } from '../services/api';
import type { Garden, IrrigationEventCreate, IrrigationMethod } from '../types';

interface IrrigationLogProps {
  onSuccess?: () => void;
  onCancel?: () => void;
  defaultGardenId?: number;
  defaultPlantingEventId?: number;
}

export function IrrigationLog({
  onSuccess,
  onCancel,
  defaultGardenId,
  defaultPlantingEventId
}: IrrigationLogProps) {
  const [gardens, setGardens] = useState<Garden[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const [formData, setFormData] = useState<IrrigationEventCreate>({
    garden_id: defaultGardenId,
    planting_event_id: defaultPlantingEventId,
    irrigation_date: new Date().toISOString().slice(0, 16), // YYYY-MM-DDTHH:mm
    water_volume_liters: undefined,
    irrigation_method: 'hand_watering',
    duration_minutes: undefined,
    notes: ''
  });

  useEffect(() => {
    loadGardens();
  }, []);

  const loadGardens = async () => {
    try {
      const data = await api.getGardens();
      setGardens(data);
    } catch (err) {
      console.error('Failed to load gardens:', err);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!formData.garden_id && !formData.planting_event_id) {
      setError('Please select a garden or planting event');
      return;
    }

    try {
      setLoading(true);
      await api.createIrrigationEvent(formData);
      if (onSuccess) onSuccess();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to log irrigation event');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{ padding: '20px', maxWidth: '600px' }}>
      <h2>Log Irrigation Event</h2>

      {error && <div className="error" style={{ marginBottom: '15px', color: '#d32f2f' }}>{error}</div>}

      <div className="form-group" style={{ marginBottom: '15px' }}>
        <label htmlFor="garden_id">Garden *</label>
        <select
          id="garden_id"
          value={formData.garden_id || ''}
          onChange={(e) => setFormData({ ...formData, garden_id: e.target.value ? Number(e.target.value) : undefined })}
          style={{ width: '100%', padding: '8px' }}
        >
          <option value="">Select a garden...</option>
          {gardens.map((garden) => (
            <option key={garden.id} value={garden.id}>
              {garden.name}
            </option>
          ))}
        </select>
      </div>

      <div className="form-group" style={{ marginBottom: '15px' }}>
        <label htmlFor="irrigation_date">Date & Time *</label>
        <input
          type="datetime-local"
          id="irrigation_date"
          value={formData.irrigation_date}
          onChange={(e) => setFormData({ ...formData, irrigation_date: e.target.value })}
          style={{ width: '100%', padding: '8px' }}
          required
        />
      </div>

      <div className="form-group" style={{ marginBottom: '15px' }}>
        <label htmlFor="irrigation_method">Irrigation Method *</label>
        <select
          id="irrigation_method"
          value={formData.irrigation_method}
          onChange={(e) => setFormData({ ...formData, irrigation_method: e.target.value as IrrigationMethod })}
          style={{ width: '100%', padding: '8px' }}
          required
        >
          <option value="hand_watering">Hand Watering</option>
          <option value="drip">Drip Irrigation</option>
          <option value="sprinkler">Sprinkler</option>
          <option value="soaker_hose">Soaker Hose</option>
          <option value="flood">Flood Irrigation</option>
          <option value="misting">Misting</option>
        </select>
      </div>

      <div className="form-group" style={{ marginBottom: '15px' }}>
        <label htmlFor="water_volume_liters">Water Volume (Liters)</label>
        <input
          type="number"
          id="water_volume_liters"
          value={formData.water_volume_liters || ''}
          onChange={(e) => setFormData({ ...formData, water_volume_liters: e.target.value ? Number(e.target.value) : undefined })}
          min="0"
          step="0.1"
          style={{ width: '100%', padding: '8px' }}
        />
        <small style={{ color: '#666' }}>Optional: 1 gallon ≈ 3.8 liters</small>
      </div>

      <div className="form-group" style={{ marginBottom: '15px' }}>
        <label htmlFor="duration_minutes">Duration (Minutes)</label>
        <input
          type="number"
          id="duration_minutes"
          value={formData.duration_minutes || ''}
          onChange={(e) => setFormData({ ...formData, duration_minutes: e.target.value ? Number(e.target.value) : undefined })}
          min="0"
          step="1"
          style={{ width: '100%', padding: '8px' }}
        />
        <small style={{ color: '#666' }}>Optional: How long you watered</small>
      </div>

      <div className="form-group" style={{ marginBottom: '20px' }}>
        <label htmlFor="notes">Notes</label>
        <textarea
          id="notes"
          value={formData.notes}
          onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
          rows={3}
          style={{ width: '100%', padding: '8px' }}
          placeholder="Weather conditions, plant observations, etc."
        />
      </div>

      <div className="form-actions" style={{ display: 'flex', gap: '10px' }}>
        <button
          type="submit"
          disabled={loading}
          className="btn"
          style={{ flex: 1 }}
        >
          {loading ? 'Saving...' : 'Log Irrigation'}
        </button>
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="btn btn-secondary"
          >
            Cancel
          </button>
        )}
      </div>
    </form>
  );
}
