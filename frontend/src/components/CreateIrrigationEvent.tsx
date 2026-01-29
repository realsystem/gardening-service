import { useState, useEffect } from 'react';
import { api } from '../services/api';
import type { Garden, IrrigationMethod } from '../types';

interface CreateIrrigationEventProps {
  onClose: () => void;
  onSuccess: () => void;
  preselectedGardenId?: number;
}

export function CreateIrrigationEvent({ onClose, onSuccess, preselectedGardenId }: CreateIrrigationEventProps) {
  const [gardens, setGardens] = useState<Garden[]>([]);
  const [gardenId, setGardenId] = useState(preselectedGardenId?.toString() || '');
  const [irrigationDate, setIrrigationDate] = useState(new Date().toISOString().slice(0, 16));
  const [waterVolumeLiters, setWaterVolumeLiters] = useState('');
  const [irrigationMethod, setIrrigationMethod] = useState<IrrigationMethod>('hand_watering');
  const [durationMinutes, setDurationMinutes] = useState('');
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadGardens = async () => {
      try {
        const data = await api.getGardens();
        setGardens(data);
      } catch (err) {
        setError('Failed to load gardens');
      }
    };
    loadGardens();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await api.createIrrigationEvent({
        garden_id: gardenId ? parseInt(gardenId) : undefined,
        irrigation_date: irrigationDate,
        water_volume_liters: waterVolumeLiters ? parseFloat(waterVolumeLiters) : undefined,
        irrigation_method: irrigationMethod,
        duration_minutes: durationMinutes ? parseInt(durationMinutes) : undefined,
        notes: notes || undefined,
      });
      onSuccess();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to log irrigation event');
      setLoading(false);
    }
  };

  const irrigationMethods: { value: IrrigationMethod; label: string }[] = [
    { value: 'hand_watering', label: 'Hand Watering' },
    { value: 'drip', label: 'Drip Irrigation' },
    { value: 'sprinkler', label: 'Sprinkler' },
    { value: 'soaker_hose', label: 'Soaker Hose' },
    { value: 'flood', label: 'Flood' },
    { value: 'misting', label: 'Misting' },
  ];

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h2>Log Irrigation Event</h2>

        {error && <div className="error">{error}</div>}

        {gardens.length === 0 ? (
          <div style={{ padding: '15px', backgroundColor: '#fff3cd', borderRadius: '4px', marginBottom: '15px' }}>
            <p style={{ margin: 0 }}>
              No gardens found. Create a garden first to log irrigation events.
            </p>
          </div>
        ) : (
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Garden *</label>
              <select
                value={gardenId}
                onChange={(e) => setGardenId(e.target.value)}
                disabled={loading}
                required
              >
                <option value="">Select a garden...</option>
                {gardens.map((g) => (
                  <option key={g.id} value={g.id}>
                    {g.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Irrigation Date & Time *</label>
              <input
                type="datetime-local"
                value={irrigationDate}
                onChange={(e) => setIrrigationDate(e.target.value)}
                required
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label>Irrigation Method *</label>
              <select
                value={irrigationMethod}
                onChange={(e) => setIrrigationMethod(e.target.value as IrrigationMethod)}
                required
                disabled={loading}
              >
                {irrigationMethods.map((method) => (
                  <option key={method.value} value={method.value}>
                    {method.label}
                  </option>
                ))}
              </select>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
              <div className="form-group">
                <label>Water Volume (liters)</label>
                <input
                  type="number"
                  step="0.1"
                  min="0"
                  value={waterVolumeLiters}
                  onChange={(e) => setWaterVolumeLiters(e.target.value)}
                  placeholder="10.0"
                  disabled={loading}
                />
                <small style={{ color: '#666', fontSize: '0.75em' }}>
                  Total water applied
                </small>
              </div>

              <div className="form-group">
                <label>Duration (minutes)</label>
                <input
                  type="number"
                  min="0"
                  value={durationMinutes}
                  onChange={(e) => setDurationMinutes(e.target.value)}
                  placeholder="15"
                  disabled={loading}
                />
                <small style={{ color: '#666', fontSize: '0.75em' }}>
                  How long it took
                </small>
              </div>
            </div>

            <div className="form-group">
              <label>Notes</label>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
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
                disabled={loading}
              >
                {loading ? 'Logging...' : 'Log Irrigation'}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
