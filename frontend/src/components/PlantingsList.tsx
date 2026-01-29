import { useState, useEffect } from 'react';
import { api } from '../services/api';
import type { PlantingEvent, Garden } from '../types';

export function PlantingsList() {
  const [plantings, setPlantings] = useState<PlantingEvent[]>([]);
  const [gardens, setGardens] = useState<Garden[]>([]);
  const [selectedGardenId, setSelectedGardenId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [deleteConfirm, setDeleteConfirm] = useState<number | null>(null);

  useEffect(() => {
    loadData();
  }, [selectedGardenId]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [plantingsData, gardensData] = await Promise.all([
        api.getPlantingEvents(selectedGardenId || undefined),
        api.getGardens()
      ]);
      setPlantings(plantingsData);
      setGardens(gardensData);
      setError('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load plantings');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (plantingId: number) => {
    try {
      await api.deletePlantingEvent(plantingId);
      setPlantings(plantings.filter(p => p.id !== plantingId));
      setDeleteConfirm(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete planting');
    }
  };

  const getGardenName = (gardenId: number): string => {
    const garden = gardens.find(g => g.id === gardenId);
    return garden?.name || 'Unknown Garden';
  };

  const getStatus = (planting: PlantingEvent): string => {
    // Simple status calculation based on planting date
    const daysSincePlanting = Math.floor(
      (new Date().getTime() - new Date(planting.planting_date).getTime()) / (1000 * 60 * 60 * 24)
    );

    if (daysSincePlanting < 0) return 'Pending';
    if (daysSincePlanting < 30) return 'Growing';
    return 'Established';
  };

  if (loading) {
    return <div className="loading">Loading plantings...</div>;
  }

  return (
    <div className="plantings-list">
      <div className="header">
        <h2>My Plantings</h2>
        <div className="filter-controls">
          <label>Filter by Garden:</label>
          <select
            value={selectedGardenId || ''}
            onChange={(e) => setSelectedGardenId(e.target.value ? parseInt(e.target.value) : null)}
          >
            <option value="">All Gardens</option>
            {gardens.map(garden => (
              <option key={garden.id} value={garden.id}>{garden.name}</option>
            ))}
          </select>
        </div>
      </div>

      {error && <div className="error">{error}</div>}

      {plantings.length === 0 ? (
        <div className="empty-state">
          <p>No plantings found.</p>
          <p>Create a planting from the garden details page.</p>
        </div>
      ) : (
        <div className="plantings-table">
          <table>
            <thead>
              <tr>
                <th>Plant</th>
                <th>Garden</th>
                <th>Planting Date</th>
                <th>Method</th>
                <th>Count</th>
                <th>Status</th>
                <th>Health</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {plantings.map(planting => (
                <tr key={planting.id}>
                  <td>
                    <strong>Plant #{planting.plant_variety_id}</strong>
                    {planting.location_in_garden && (
                      <div className="location">{planting.location_in_garden}</div>
                    )}
                  </td>
                  <td>{getGardenName(planting.garden_id)}</td>
                  <td>{new Date(planting.planting_date).toLocaleDateString()}</td>
                  <td>{planting.planting_method.replace('_', ' ')}</td>
                  <td>{planting.plant_count || '-'}</td>
                  <td>
                    <span className={`status status-${getStatus(planting).toLowerCase()}`}>
                      {getStatus(planting)}
                    </span>
                  </td>
                  <td>
                    {planting.health_status && (
                      <span className={`health health-${planting.health_status}`}>
                        {planting.health_status}
                      </span>
                    )}
                  </td>
                  <td>
                    {deleteConfirm === planting.id ? (
                      <div className="confirm-delete">
                        <button
                          onClick={() => handleDelete(planting.id)}
                          className="btn btn-danger btn-sm"
                        >
                          Confirm
                        </button>
                        <button
                          onClick={() => setDeleteConfirm(null)}
                          className="btn btn-secondary btn-sm"
                        >
                          Cancel
                        </button>
                      </div>
                    ) : (
                      <button
                        onClick={() => setDeleteConfirm(planting.id)}
                        className="btn btn-danger btn-sm"
                      >
                        Delete
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
