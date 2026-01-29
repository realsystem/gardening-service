import { useState, useEffect } from 'react';
import { api } from '../services/api';
import type { Garden, SoilSampleCreate } from '../types';

interface SoilSampleFormProps {
  onSuccess?: () => void;
  onCancel?: () => void;
  defaultGardenId?: number;
  defaultPlantingEventId?: number;
}

export function SoilSampleForm({
  onSuccess,
  onCancel,
  defaultGardenId,
  defaultPlantingEventId
}: SoilSampleFormProps) {
  const [gardens, setGardens] = useState<Garden[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const [formData, setFormData] = useState<SoilSampleCreate>({
    garden_id: defaultGardenId,
    planting_event_id: defaultPlantingEventId,
    ph: 7.0,
    nitrogen_ppm: undefined,
    phosphorus_ppm: undefined,
    potassium_ppm: undefined,
    organic_matter_percent: undefined,
    moisture_percent: undefined,
    date_collected: new Date().toISOString().split('T')[0],
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
      await api.createSoilSample(formData);
      if (onSuccess) onSuccess();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save soil sample');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{ padding: '20px', maxWidth: '600px' }}>
      <h2>Record Soil Sample</h2>

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
        <label htmlFor="date_collected">Date Collected *</label>
        <input
          type="date"
          id="date_collected"
          value={formData.date_collected}
          onChange={(e) => setFormData({ ...formData, date_collected: e.target.value })}
          style={{ width: '100%', padding: '8px' }}
          required
        />
      </div>

      <div className="form-group" style={{ marginBottom: '15px' }}>
        <label htmlFor="ph">Soil pH * (0-14)</label>
        <input
          type="number"
          id="ph"
          value={formData.ph}
          onChange={(e) => setFormData({ ...formData, ph: Number(e.target.value) })}
          min="0"
          max="14"
          step="0.1"
          style={{ width: '100%', padding: '8px' }}
          required
        />
        <small style={{ color: '#666' }}>Typical range: 4.0-9.0</small>
      </div>

      <div className="form-group" style={{ marginBottom: '15px' }}>
        <label htmlFor="nitrogen_ppm">Nitrogen (PPM)</label>
        <input
          type="number"
          id="nitrogen_ppm"
          value={formData.nitrogen_ppm || ''}
          onChange={(e) => setFormData({ ...formData, nitrogen_ppm: e.target.value ? Number(e.target.value) : undefined })}
          min="0"
          step="1"
          style={{ width: '100%', padding: '8px' }}
        />
        <small style={{ color: '#666' }}>Optional: Parts per million</small>
      </div>

      <div className="form-group" style={{ marginBottom: '15px' }}>
        <label htmlFor="phosphorus_ppm">Phosphorus (PPM)</label>
        <input
          type="number"
          id="phosphorus_ppm"
          value={formData.phosphorus_ppm || ''}
          onChange={(e) => setFormData({ ...formData, phosphorus_ppm: e.target.value ? Number(e.target.value) : undefined })}
          min="0"
          step="1"
          style={{ width: '100%', padding: '8px' }}
        />
        <small style={{ color: '#666' }}>Optional: Parts per million</small>
      </div>

      <div className="form-group" style={{ marginBottom: '15px' }}>
        <label htmlFor="potassium_ppm">Potassium (PPM)</label>
        <input
          type="number"
          id="potassium_ppm"
          value={formData.potassium_ppm || ''}
          onChange={(e) => setFormData({ ...formData, potassium_ppm: e.target.value ? Number(e.target.value) : undefined })}
          min="0"
          step="1"
          style={{ width: '100%', padding: '8px' }}
        />
        <small style={{ color: '#666' }}>Optional: Parts per million</small>
      </div>

      <div className="form-group" style={{ marginBottom: '15px' }}>
        <label htmlFor="organic_matter_percent">Organic Matter (%)</label>
        <input
          type="number"
          id="organic_matter_percent"
          value={formData.organic_matter_percent || ''}
          onChange={(e) => setFormData({ ...formData, organic_matter_percent: e.target.value ? Number(e.target.value) : undefined })}
          min="0"
          max="100"
          step="0.1"
          style={{ width: '100%', padding: '8px' }}
        />
        <small style={{ color: '#666' }}>Optional: 0-100%</small>
      </div>

      <div className="form-group" style={{ marginBottom: '15px' }}>
        <label htmlFor="moisture_percent">Soil Moisture (%)</label>
        <input
          type="number"
          id="moisture_percent"
          value={formData.moisture_percent || ''}
          onChange={(e) => setFormData({ ...formData, moisture_percent: e.target.value ? Number(e.target.value) : undefined })}
          min="0"
          max="100"
          step="0.1"
          style={{ width: '100%', padding: '8px' }}
        />
        <small style={{ color: '#666' }}>Optional: 0-100%</small>
      </div>

      <div className="form-group" style={{ marginBottom: '20px' }}>
        <label htmlFor="notes">Notes</label>
        <textarea
          id="notes"
          value={formData.notes}
          onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
          rows={3}
          style={{ width: '100%', padding: '8px' }}
        />
      </div>

      <div className="form-actions" style={{ display: 'flex', gap: '10px' }}>
        <button
          type="submit"
          disabled={loading}
          className="btn"
          style={{ flex: 1 }}
        >
          {loading ? 'Saving...' : 'Save Soil Sample'}
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
