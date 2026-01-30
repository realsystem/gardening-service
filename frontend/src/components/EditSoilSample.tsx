import { useState } from 'react';
import { api } from '../services/api';
import type { SoilSample } from '../types';

interface EditSoilSampleProps {
  sample: SoilSample;
  onClose: () => void;
  onSuccess: () => void;
}

export function EditSoilSample({ sample, onClose, onSuccess }: EditSoilSampleProps) {
  const [dateCollected, setDateCollected] = useState(sample.date_collected);
  const [ph, setPh] = useState(sample.ph.toString());
  const [nitrogenPpm, setNitrogenPpm] = useState(sample.nitrogen_ppm?.toString() || '');
  const [phosphorusPpm, setPhosphorusPpm] = useState(sample.phosphorus_ppm?.toString() || '');
  const [potassiumPpm, setPotassiumPpm] = useState(sample.potassium_ppm?.toString() || '');
  const [organicMatterPercent, setOrganicMatterPercent] = useState(sample.organic_matter_percent?.toString() || '');
  const [moisturePercent, setMoisturePercent] = useState(sample.moisture_percent?.toString() || '');
  const [notes, setNotes] = useState(sample.notes || '');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!ph) {
      setError('pH level is required');
      return;
    }

    setLoading(true);

    try {
      await api.updateSoilSample(sample.id, {
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
      setError(err instanceof Error ? err.message : 'Failed to update soil sample');
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h2>Edit Soil Sample</h2>

        {error && <div className="error">{error}</div>}

        <form onSubmit={handleSubmit}>
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
              {loading ? 'Updating...' : 'Update Soil Sample'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
