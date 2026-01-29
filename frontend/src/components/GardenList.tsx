import { useState, useEffect } from 'react';
import { api } from '../services/api';
import type { Garden } from '../types';

interface GardenListProps {
  onSelectGarden: (gardenId: number) => void;
  onRefresh?: () => void;
}

export function GardenList({ onSelectGarden, onRefresh }: GardenListProps) {
  const [gardens, setGardens] = useState<Garden[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [confirmDeleteId, setConfirmDeleteId] = useState<number | null>(null);

  const loadGardens = async () => {
    try {
      setLoading(true);
      const data = await api.getGardens();
      setGardens(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load gardens');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadGardens();
  }, []);

  const handleDelete = async (gardenId: number) => {
    setDeletingId(gardenId);
    try {
      await api.deleteGarden(gardenId);
      setGardens(gardens.filter(g => g.id !== gardenId));
      setConfirmDeleteId(null);
      if (onRefresh) onRefresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete garden');
    } finally {
      setDeletingId(null);
    }
  };

  const getGardenTypeIcon = (garden: Garden) => {
    if (garden.is_hydroponic) return '💧';
    if (garden.garden_type === 'indoor') return '🏠';
    return '🌱';
  };

  const getGardenTypeLabel = (garden: Garden) => {
    if (garden.is_hydroponic) return 'Hydroponic';
    if (garden.garden_type === 'indoor') return 'Indoor';
    return 'Outdoor';
  };

  if (loading) {
    return <div style={{ padding: '20px' }}>Loading gardens...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  if (gardens.length === 0) {
    return (
      <div style={{ padding: '20px', textAlign: 'center', color: '#666' }}>
        <p>No gardens yet. Create your first garden to get started!</p>
      </div>
    );
  }

  return (
    <div style={{ padding: '20px' }}>
      <h2>My Gardens</h2>
      <div style={{ display: 'grid', gap: '15px', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))' }}>
        {gardens.map((garden) => (
          <div
            key={garden.id}
            style={{
              border: '1px solid #ddd',
              borderRadius: '8px',
              padding: '15px',
              backgroundColor: '#fff',
              cursor: 'pointer',
              transition: 'box-shadow 0.2s',
            }}
            onMouseEnter={(e) => (e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)')}
            onMouseLeave={(e) => (e.currentTarget.style.boxShadow = 'none')}
          >
            <div onClick={() => onSelectGarden(garden.id)}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px' }}>
                <span style={{ fontSize: '24px' }}>{getGardenTypeIcon(garden)}</span>
                <div style={{ flex: 1 }}>
                  <h3 style={{ margin: 0 }}>{garden.name}</h3>
                  <div style={{ fontSize: '0.9em', color: '#666' }}>
                    {getGardenTypeLabel(garden)}
                    {garden.location && ` • ${garden.location}`}
                  </div>
                </div>
              </div>

              {garden.description && (
                <p style={{ margin: '10px 0', fontSize: '0.9em', color: '#555' }}>
                  {garden.description}
                </p>
              )}

              {garden.is_hydroponic && garden.hydro_system_type && (
                <div style={{ fontSize: '0.85em', color: '#2196f3', marginTop: '8px' }}>
                  System: {garden.hydro_system_type.toUpperCase()}
                </div>
              )}
            </div>

            <div style={{ marginTop: '15px', display: 'flex', gap: '10px' }}>
              <button
                onClick={() => onSelectGarden(garden.id)}
                className="btn"
                style={{ flex: 1 }}
              >
                View Details
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setConfirmDeleteId(garden.id);
                }}
                className="btn btn-secondary"
                disabled={deletingId === garden.id}
              >
                {deletingId === garden.id ? 'Deleting...' : 'Delete'}
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Delete Confirmation Modal */}
      {confirmDeleteId !== null && (
        <div className="modal-overlay" onClick={() => setConfirmDeleteId(null)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Delete Garden?</h2>
            <p>
              Are you sure you want to delete <strong>{gardens.find(g => g.id === confirmDeleteId)?.name}</strong>?
            </p>
            <p style={{ color: '#d32f2f', fontSize: '0.9em' }}>
              ⚠️ This will permanently delete all plantings and tasks associated with this garden.
            </p>
            <div className="form-actions">
              <button
                onClick={() => setConfirmDeleteId(null)}
                className="btn btn-secondary"
              >
                Cancel
              </button>
              <button
                onClick={() => handleDelete(confirmDeleteId)}
                className="btn"
                style={{ backgroundColor: '#d32f2f' }}
              >
                Delete Garden
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
