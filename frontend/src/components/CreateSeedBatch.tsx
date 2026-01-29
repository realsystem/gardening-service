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

  // Reset search on mount to ensure we load all varieties
  useEffect(() => {
    setSearch('');
  }, []);

  useEffect(() => {
    const loadVarieties = async () => {
      try {
        console.log('[CreateSeedBatch] Loading varieties with search:', search);
        const data = await api.getPlantVarieties(search);
        console.log('[CreateSeedBatch] Received varieties:', data?.length, 'items');
        console.log('[CreateSeedBatch] First variety:', data?.[0]);
        setVarieties(data);
      } catch (err) {
        console.error('[CreateSeedBatch] Error loading varieties:', err);
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
            <div style={{ display: 'flex', gap: '8px' }}>
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search by name... (leave empty to see all)"
                style={{ flex: 1 }}
              />
              {search && (
                <button
                  type="button"
                  onClick={() => setSearch('')}
                  className="btn btn-secondary"
                  style={{ padding: '0 12px' }}
                >
                  Clear
                </button>
              )}
            </div>
            {search && varieties.length === 0 && (
              <div style={{ color: '#666', fontSize: '0.9em', marginTop: '4px' }}>
                No varieties found matching "{search}". Try clearing the search.
              </div>
            )}
            {!search && varieties.length === 0 && (
              <div style={{ color: '#666', fontSize: '0.9em', marginTop: '4px' }}>
                Loading varieties...
              </div>
            )}
          </div>

          <div className="form-group">
            <label>Plant Variety * {!search && `(${varieties.length} available)`}</label>
            <select
              value={plantVarietyId}
              onChange={(e) => setPlantVarietyId(e.target.value)}
              required
              disabled={loading}
            >
              <option value="">
                {varieties.length === 0
                  ? (search ? 'No matching varieties' : 'Loading...')
                  : 'Select a variety...'}
              </option>
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
