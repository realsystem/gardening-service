import { useState, useEffect } from 'react';
import { api } from '../services/api';
import { LandCanvas } from './LandCanvas';
import { CreateLand } from './CreateLand';
import { TreeManager } from './TreeManager';
import type { Land, LandWithGardens, Garden, Tree } from '../types';
import './LandList.css';

export function LandList() {
  const [lands, setLands] = useState<Land[]>([]);
  const [gardens, setGardens] = useState<Garden[]>([]);
  const [landTrees, setLandTrees] = useState<Tree[]>([]);
  const [selectedLand, setSelectedLand] = useState<LandWithGardens | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showCreateForm, setShowCreateForm] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [landsData, gardensData] = await Promise.all([
        api.getLands(),
        api.getGardens(),
      ]);
      setLands(landsData);
      setGardens(gardensData);
      setError('');
    } catch (err) {
      setError((err as Error).message || 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectLand = async (landId: number) => {
    try {
      const [landDetails, treesOnLand] = await Promise.all([
        api.getLand(landId),
        api.getTreesOnLand(landId),
      ]);
      setSelectedLand(landDetails);
      setLandTrees(treesOnLand);
    } catch (err) {
      setError((err as Error).message || 'Failed to load land details');
    }
  };

  const handleDeleteLand = async (landId: number) => {
    if (!confirm('Are you sure you want to delete this land? Gardens will be removed from layout but not deleted.')) {
      return;
    }

    try {
      await api.deleteLand(landId);
      await loadData();
      if (selectedLand?.id === landId) {
        setSelectedLand(null);
      }
    } catch (err) {
      setError((err as Error).message || 'Failed to delete land');
    }
  };

  const handleLandCreated = async () => {
    setShowCreateForm(false);
    await loadData();
  };

  const handleLandUpdate = async () => {
    // Reload all data (gardens and lands)
    await loadData();
    // Refresh the selected land details
    if (selectedLand) {
      await handleSelectLand(selectedLand.id);
    }
  };

  if (loading) {
    return <div className="loading">Loading lands...</div>;
  }

  return (
    <div className="land-list-container">
      <div className="land-list-header">
        <h2>Land Layout Management</h2>
        <button
          className="btn-primary"
          onClick={() => setShowCreateForm(!showCreateForm)}
        >
          {showCreateForm ? 'Cancel' : '+ Create Land'}
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {showCreateForm && (
        <CreateLand
          onCreated={handleLandCreated}
          onCancel={() => setShowCreateForm(false)}
        />
      )}

      {lands.length === 0 ? (
        <div className="empty-state">
          <p>No lands created yet. Create your first land to start organizing your gardens.</p>
        </div>
      ) : (
        <div className="lands-grid">
          {lands.map((land) => (
            <div
              key={land.id}
              className={`land-card ${selectedLand?.id === land.id ? 'selected' : ''}`}
            >
              <div className="land-card-header">
                <h3>{land.name}</h3>
                <button
                  className="btn-delete"
                  onClick={() => handleDeleteLand(land.id)}
                  title="Delete land"
                >
                  🗑️
                </button>
              </div>
              <p className="land-info">{land.width} × {land.height} units</p>
              <button
                className="btn-secondary"
                onClick={() => handleSelectLand(land.id)}
              >
                {selectedLand?.id === land.id ? 'Viewing' : 'View Layout'}
              </button>
            </div>
          ))}
        </div>
      )}

      {selectedLand && (
        <div className="land-canvas-section">
          <TreeManager
            land={selectedLand}
            trees={landTrees}
            onUpdate={handleLandUpdate}
          />
          <LandCanvas
            land={selectedLand}
            gardens={gardens}
            trees={landTrees}
            onUpdate={handleLandUpdate}
          />
        </div>
      )}
    </div>
  );
}
