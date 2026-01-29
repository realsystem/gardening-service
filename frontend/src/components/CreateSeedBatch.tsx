import { useState, useEffect } from 'react';
import { api } from '../services/api';
import type { PlantVariety } from '../types';

interface CreateSeedBatchProps {
  onClose: () => void;
  onSuccess: () => void;
}

export function CreateSeedBatch({ onClose, onSuccess }: CreateSeedBatchProps) {
  const [varieties, setVarieties] = useState<PlantVariety[]>([]);
  const [search, setSearch] = useState('');
  const [plantVarietyId, setPlantVarietyId] = useState('');
  const [source, setSource] = useState('');
  const [harvestYear, setHarvestYear] = useState('');
  const [quantity, setQuantity] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadVarieties = async () => {
      try {
        const data = await api.getPlantVarieties(search);
        setVarieties(data);
      } catch (err) {
        setError('Failed to load plant varieties');
      }
    };
    loadVarieties();
  }, [search]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await api.createSeedBatch({
        plant_variety_id: parseInt(plantVarietyId),
        source: source || undefined,
        harvest_year: harvestYear ? parseInt(harvestYear) : undefined,
        quantity: quantity ? parseInt(quantity) : undefined,
      });
      onSuccess();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create seed batch');
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h2>Add Seed Batch</h2>

        {error && <div className="error">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Search Plant Variety</label>
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by name..."
            />
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
            <label>Source</label>
            <input
              type="text"
              value={source}
              onChange={(e) => setSource(e.target.value)}
              placeholder="e.g. Local nursery"
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label>Harvest Year</label>
            <input
              type="number"
              value={harvestYear}
              onChange={(e) => setHarvestYear(e.target.value)}
              placeholder="e.g. 2024"
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label>Quantity</label>
            <input
              type="number"
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
              placeholder="Number of seeds"
              disabled={loading}
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
      </div>
    </div>
  );
}
