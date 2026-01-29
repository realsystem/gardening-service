import { useState, useEffect } from 'react';
import { api } from '../services/api';
import type { Garden } from '../types';

interface CreateSoilSampleProps {
  onClose: () => void;
  onSuccess: () => void;
  preselectedGardenId?: number;
}

export function CreateSoilSample({ onClose, onSuccess, preselectedGardenId }: CreateSoilSampleProps) {
  const [gardens, setGardens] = useState<Garden[]>([]);
  const [gardenId, setGardenId] = useState(preselectedGardenId?.toString() || '');
  const [dateCollected, setDateCollected] = useState(new Date().toISOString().split('T')[0]);
  const [ph, setPh] = useState('');
  const [nitrogenPpm, setNitrogenPpm] = useState('');
  const [phosphorusPpm, setPhosphorusPpm] = useState('');
  const [potassiumPpm, setPotassiumPpm] = useState('');
  const [organicMatterPercent, setOrganicMatterPercent] = useState('');
  const [moisturePercent, setMoisturePercent] = useState('');
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

    if (!ph) {
      setError('pH level is required');
      return;
    }

    setLoading(true);

    try {
      await api.createSoilSample({
        garden_id: gardenId ? parseInt(gardenId) : undefined,
        ph: parseFloat(ph),
        nitrogen_ppm: nitrogenPpm ? parseFloat(nitrogenPpm) : undefined,
        phosphorus_ppm: phosphorusPpm ? parseFloat(phosphorusPpm) : undefined,
        potassium_ppm: potassiumPpm ? parseFloat(potassiumPpm) : undefined,
        organic_matter_percent: organicMatterPercent ? parseFloat(organicMatterPercent) : undefined,
        moisture_percent: moisturePercent ? parseFloat(moisturePercent) : undefined,
        date_collected: dateCollected,
        notes: notes || undefined,
      });
      onSuccess();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create soil sample');
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h2>Add Soil Sample</h2>

        {error && <div className="error">{error}</div>}

        {gardens.length === 0 ? (
          <div style={{ padding: '15px', backgroundColor: '#fff3cd', borderRadius: '4px', marginBottom: '15px' }}>
            <p style={{ margin: 0 }}>
              No gardens found. Create a garden first to add soil samples.
            </p>
          </div>
        ) : (
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Garden (optional)</label>
              <select
                value={gardenId}
                onChange={(e) => setGardenId(e.target.value)}
                disabled={loading}
              >
                <option value="">Select a garden...</option>
                {gardens.map((g) => (
                  <option key={g.id} value={g.id}>
                    {g.name}
                  </option>
                ))}
              </select>
              <small style={{ color: '#666', fontSize: '0.85em' }}>
                Link this sample to a specific garden
              </small>
            </div>

            <div className="form-group">
              <label>Collection Date *</label>
              <input
                type="date"
                value={dateCollected}
                onChange={(e) => setDateCollected(e.target.value)}
                required
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label>pH Level * (0-14)</label>
              <input
                type="number"
                step="0.1"
                min="0"
                max="14"
                value={ph}
                onChange={(e) => setPh(e.target.value)}
                placeholder="6.5"
                required
                disabled={loading}
              />
              <small style={{ color: '#666', fontSize: '0.85em' }}>
                Optimal: 6.0-7.0 for most plants
              </small>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '10px' }}>
              <div className="form-group">
                <label>Nitrogen (ppm)</label>
                <input
                  type="number"
                  step="0.1"
                  min="0"
                  value={nitrogenPpm}
                  onChange={(e) => setNitrogenPpm(e.target.value)}
                  placeholder="30"
                  disabled={loading}
                />
                <small style={{ color: '#666', fontSize: '0.75em' }}>Optimal: 20-50</small>
              </div>

              <div className="form-group">
                <label>Phosphorus (ppm)</label>
                <input
                  type="number"
                  step="0.1"
                  min="0"
                  value={phosphorusPpm}
                  onChange={(e) => setPhosphorusPpm(e.target.value)}
                  placeholder="25"
                  disabled={loading}
                />
                <small style={{ color: '#666', fontSize: '0.75em' }}>Optimal: 15-40</small>
              </div>

              <div className="form-group">
                <label>Potassium (ppm)</label>
                <input
                  type="number"
                  step="0.1"
                  min="0"
                  value={potassiumPpm}
                  onChange={(e) => setPotassiumPpm(e.target.value)}
                  placeholder="150"
                  disabled={loading}
                />
                <small style={{ color: '#666', fontSize: '0.75em' }}>Optimal: 80-200</small>
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
              <div className="form-group">
                <label>Organic Matter (%)</label>
                <input
                  type="number"
                  step="0.1"
                  min="0"
                  max="100"
                  value={organicMatterPercent}
                  onChange={(e) => setOrganicMatterPercent(e.target.value)}
                  placeholder="3.5"
                  disabled={loading}
                />
                <small style={{ color: '#666', fontSize: '0.75em' }}>Optimal: &gt;3%</small>
              </div>

              <div className="form-group">
                <label>Soil Moisture (%)</label>
                <input
                  type="number"
                  step="0.1"
                  min="0"
                  max="100"
                  value={moisturePercent}
                  onChange={(e) => setMoisturePercent(e.target.value)}
                  placeholder="50"
                  disabled={loading}
                />
                <small style={{ color: '#666', fontSize: '0.75em' }}>Optimal: 40-60%</small>
              </div>
            </div>

            <div className="form-group">
              <label>Notes</label>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Any observations or context about this sample..."
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
                {loading ? 'Adding...' : 'Add Soil Sample'}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
