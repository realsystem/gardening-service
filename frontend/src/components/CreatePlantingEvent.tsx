import { useState, useEffect } from 'react';
import { api } from '../services/api';
import type { Garden, PlantVariety } from '../types';

interface CreatePlantingEventProps {
  onClose: () => void;
  onSuccess: () => void;
}

export function CreatePlantingEvent({ onClose, onSuccess }: CreatePlantingEventProps) {
  const [gardens, setGardens] = useState<Garden[]>([]);
  const [varieties, setVarieties] = useState<PlantVariety[]>([]);
  const [gardenId, setGardenId] = useState('');
  const [plantVarietyId, setPlantVarietyId] = useState('');
  const [plantingDate, setPlantingDate] = useState('');
  const [plantingMethod, setPlantingMethod] = useState<'direct_sow' | 'transplant'>('direct_sow');
  const [plantCount, setPlantCount] = useState('');
  const [location, setLocation] = useState('');
  const [healthStatus, setHealthStatus] = useState<'healthy' | 'stressed' | 'diseased' | ''>('');
  const [plantNotes, setPlantNotes] = useState('');
  const [positionX, setPositionX] = useState('');
  const [positionY, setPositionY] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [needsGarden, setNeedsGarden] = useState(false);
  const [newGardenName, setNewGardenName] = useState('');

  useEffect(() => {
    const loadData = async () => {
      try {
        const [gardensData, varietiesData] = await Promise.all([
          api.getGardens(),
          api.getPlantVarieties(),
        ]);

        // Sort varieties alphabetically by common name, then by variety name
        const sortedVarieties = varietiesData.sort((a, b) => {
          const nameCompare = a.common_name.localeCompare(b.common_name);
          if (nameCompare !== 0) return nameCompare;
          return (a.variety_name || '').localeCompare(b.variety_name || '');
        });

        setGardens(gardensData);
        setVarieties(sortedVarieties);
        if (gardensData.length === 0) {
          setNeedsGarden(true);
        }
      } catch (err) {
        setError('Failed to load data');
      }
    };
    loadData();
  }, []);

  const handleCreateGarden = async () => {
    if (!newGardenName.trim()) return;

    try {
      const garden = await api.createGarden({
        name: newGardenName,
        garden_type: 'outdoor'
      });
      setGardens([...gardens, garden]);
      setGardenId(garden.id.toString());
      setNeedsGarden(false);
      setNewGardenName('');
    } catch (err) {
      setError('Failed to create garden');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await api.createPlantingEvent({
        garden_id: parseInt(gardenId),
        plant_variety_id: parseInt(plantVarietyId),
        planting_date: plantingDate,
        planting_method: plantingMethod,
        plant_count: plantCount ? parseInt(plantCount) : undefined,
        location_in_garden: location || undefined,
        health_status: healthStatus || undefined,
        plant_notes: plantNotes || undefined,
        x: positionX ? parseFloat(positionX) : undefined,
        y: positionY ? parseFloat(positionY) : undefined,
      });
      onSuccess();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create planting event');
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h2>Create Planting Event</h2>

        {error && <div className="error">{error}</div>}

        {needsGarden ? (
          <>
            <p style={{ marginBottom: '15px' }}>You need to create a garden first.</p>
            <div className="form-group">
              <label>Garden Name *</label>
              <input
                type="text"
                value={newGardenName}
                onChange={(e) => setNewGardenName(e.target.value)}
                placeholder="e.g. Backyard Garden"
              />
            </div>
            <div className="form-actions">
              <button onClick={onClose} className="btn btn-secondary">Cancel</button>
              <button onClick={handleCreateGarden} className="btn">Create Garden</button>
            </div>
          </>
        ) : (
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Garden *</label>
              <select
                value={gardenId}
                onChange={(e) => setGardenId(e.target.value)}
                required
                disabled={loading}
              >
                <option value="">Select a garden...</option>
                {gardens.map((g) => (
                  <option key={g.id} value={g.id}>{g.name}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Plant Variety *</label>
              <select
                value={plantVarietyId}
                onChange={(e) => setPlantVarietyId(e.target.value)}
                required
                disabled={loading}
              >
                <option value="">Select a variety...</option>
                {varieties.map((v) => (
                  <option key={v.id} value={v.id}>
                    {v.common_name} {v.variety_name ? `(${v.variety_name})` : ''}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Planting Date *</label>
              <input
                type="date"
                value={plantingDate}
                onChange={(e) => setPlantingDate(e.target.value)}
                required
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label>Planting Method *</label>
              <select
                value={plantingMethod}
                onChange={(e) => setPlantingMethod(e.target.value as 'direct_sow' | 'transplant')}
                required
                disabled={loading}
              >
                <option value="direct_sow">Direct Sow</option>
                <option value="transplant">Transplant</option>
              </select>
            </div>

            <div className="form-group">
              <label>Plant Count</label>
              <input
                type="number"
                value={plantCount}
                onChange={(e) => setPlantCount(e.target.value)}
                placeholder="Number of plants"
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label>Location in Garden</label>
              <input
                type="text"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                placeholder="e.g. Bed 1, Row 2"
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label>Health Status</label>
              <select
                value={healthStatus}
                onChange={(e) => setHealthStatus(e.target.value as typeof healthStatus)}
                disabled={loading}
              >
                <option value="">Not specified</option>
                <option value="healthy">Healthy</option>
                <option value="stressed">Stressed</option>
                <option value="diseased">Diseased</option>
              </select>
            </div>

            <div style={{ background: '#e8f5e9', padding: '12px', borderRadius: '6px', marginBottom: '15px' }}>
              <div style={{ fontSize: '0.95em', fontWeight: '600', marginBottom: '8px', color: '#2c5f2d' }}>
                🌿 Plant Position (for Companion Planting Analysis)
              </div>
              <div style={{ fontSize: '0.85em', color: '#555', marginBottom: '10px' }}>
                Optional: Set plant position to get companion planting recommendations
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                <div className="form-group" style={{ marginBottom: 0 }}>
                  <label>X Position (meters)</label>
                  <input
                    type="number"
                    value={positionX}
                    onChange={(e) => setPositionX(e.target.value)}
                    placeholder="0.0"
                    step="0.1"
                    disabled={loading}
                  />
                </div>
                <div className="form-group" style={{ marginBottom: 0 }}>
                  <label>Y Position (meters)</label>
                  <input
                    type="number"
                    value={positionY}
                    onChange={(e) => setPositionY(e.target.value)}
                    placeholder="0.0"
                    step="0.1"
                    disabled={loading}
                  />
                </div>
              </div>
              <div style={{ fontSize: '0.8em', color: '#666', marginTop: '6px' }}>
                Example: First plant at (0, 0), second plant 0.5m away at (0.5, 0)
              </div>
            </div>

            <div className="form-group">
              <label>Plant Notes</label>
              <textarea
                value={plantNotes}
                onChange={(e) => setPlantNotes(e.target.value)}
                placeholder="Any observations or notes about the plants"
                disabled={loading}
                rows={3}
              />
            </div>

            <div className="form-actions">
              <button type="button" onClick={onClose} className="btn btn-secondary" disabled={loading}>
                Cancel
              </button>
              <button type="submit" className="btn" disabled={loading}>
                {loading ? 'Creating...' : 'Create'}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
