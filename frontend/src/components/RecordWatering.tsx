/**
 * Record Watering Event Form
 * Records watering events for irrigation zones
 */
import { useState, useEffect } from 'react';
import { api } from '../services/api';
import type { IrrigationZone, WateringEventCreate } from '../types';

interface RecordWateringProps {
  onClose: () => void;
  onSuccess: () => void;
  preselectedZoneId?: number;
}

export function RecordWatering({ onClose, onSuccess, preselectedZoneId }: RecordWateringProps) {
  const [zones, setZones] = useState<IrrigationZone[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Form state
  const [formData, setFormData] = useState<WateringEventCreate>({
    irrigation_zone_id: preselectedZoneId || 0,
    watered_at: new Date().toISOString().slice(0, 16), // yyyy-MM-ddThh:mm format
    duration_minutes: 0,
    estimated_volume_liters: undefined,
    is_manual: true,
    notes: ''
  });

  useEffect(() => {
    loadZones();
  }, []);

  const loadZones = async () => {
    try {
      const data = await api.getIrrigationZones();
      setZones(data);
    } catch (err) {
      setError('Failed to load irrigation zones');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // Convert datetime-local string to ISO string for API
      const wateredAt = new Date(formData.watered_at).toISOString();

      await api.createWateringEvent({
        ...formData,
        watered_at: wateredAt
      });
      onSuccess();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to record watering event');
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h2>Record Watering Event</h2>

        {error && <div className="error">{error}</div>}

        {zones.length === 0 ? (
          <div style={{ padding: '15px', backgroundColor: '#fff3cd', borderRadius: '4px', marginBottom: '15px' }}>
            <p style={{ margin: 0 }}>
              No irrigation zones found. Create an irrigation zone first to record watering events.
            </p>
          </div>
        ) : (
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Irrigation Zone *</label>
              <select
                value={formData.irrigation_zone_id}
                onChange={(e) => setFormData({ ...formData, irrigation_zone_id: Number(e.target.value) })}
                disabled={loading}
                required
              >
                <option value="">Select a zone...</option>
                {zones.map((zone) => (
                  <option key={zone.id} value={zone.id}>
                    {zone.name} ({zone.delivery_type})
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Watered At *</label>
              <input
                type="datetime-local"
                value={formData.watered_at}
                onChange={(e) => setFormData({ ...formData, watered_at: e.target.value })}
                required
                disabled={loading}
              />
              <small style={{ color: '#666', fontSize: '0.75em', display: 'block', marginTop: '4px' }}>
                When this watering occurred
              </small>
            </div>

            <div className="form-group">
              <label>Duration (minutes) *</label>
              <input
                type="number"
                min="1"
                step="1"
                value={formData.duration_minutes || ''}
                onChange={(e) => setFormData({ ...formData, duration_minutes: Number(e.target.value) })}
                placeholder="30"
                required
                disabled={loading}
              />
              <small style={{ color: '#666', fontSize: '0.75em', display: 'block', marginTop: '4px' }}>
                How long the zone was watered
              </small>
            </div>

            <div className="form-group">
              <label>Estimated Volume (liters)</label>
              <input
                type="number"
                min="0"
                step="0.1"
                value={formData.estimated_volume_liters || ''}
                onChange={(e) => setFormData({
                  ...formData,
                  estimated_volume_liters: e.target.value ? Number(e.target.value) : undefined
                })}
                placeholder="Optional"
                disabled={loading}
              />
              <small style={{ color: '#666', fontSize: '0.75em', display: 'block', marginTop: '4px' }}>
                Total water applied (optional)
              </small>
            </div>

            <div className="form-group">
              <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
                <input
                  type="checkbox"
                  checked={formData.is_manual}
                  onChange={(e) => setFormData({ ...formData, is_manual: e.target.checked })}
                  disabled={loading}
                  style={{ marginRight: '8px' }}
                />
                <span>Manual watering (uncheck if automated)</span>
              </label>
              <small style={{ color: '#666', fontSize: '0.75em', display: 'block', marginTop: '4px' }}>
                Check this if you manually watered this zone
              </small>
            </div>

            <div className="form-group">
              <label>Notes</label>
              <textarea
                value={formData.notes}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                placeholder="Any observations about this watering..."
                rows={3}
                disabled={loading}
              />
            </div>

            <div className="button-group">
              <button
                type="button"
                onClick={onClose}
                className="btn btn-secondary"
                disabled={loading}
              >
                Cancel
              </button>
              <button
                type="submit"
                className="btn btn-primary"
                disabled={loading || !formData.irrigation_zone_id}
              >
                {loading ? 'Recording...' : 'Record Watering'}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
