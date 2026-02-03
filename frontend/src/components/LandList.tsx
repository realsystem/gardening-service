import { useState, useEffect } from 'react';
import { api } from '../services/api';
import { LandCanvas } from './LandCanvas';
import { CreateLand } from './CreateLand';
import { TreeManager } from './TreeManager';
import { StructureManager } from './StructureManager';
import { useUnitSystem } from '../contexts/UnitSystemContext';
import { convertDistance, getUnitLabels } from '../utils/units';
import type { Land, LandWithGardens, Garden, Tree, Structure } from '../types';
import './LandList.css';

export function LandList() {
  const { unitSystem } = useUnitSystem();
  const unitLabels = getUnitLabels(unitSystem);

  const [lands, setLands] = useState<Land[]>([]);
  const [gardens, setGardens] = useState<Garden[]>([]);
  const [landTrees, setLandTrees] = useState<Tree[]>([]);
  const [landStructures, setLandStructures] = useState<Structure[]>([]);
  const [selectedLand, setSelectedLand] = useState<LandWithGardens | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showCreateForm, setShowCreateForm] = useState(false);
  useEffect(() => {
    loadData();
  }, []);

  const loadData = async (showLoading = true) => {
    try {
      if (showLoading) {
        setLoading(true);
      }
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
      if (showLoading) {
        setLoading(false);
      }
    }
  };

  const handleSelectLand = async (landId: number) => {
    try {
      const [landDetails, treesOnLand, structuresOnLand] = await Promise.all([
        api.getLand(landId),
        api.getTreesOnLand(landId),
        api.getStructuresOnLand(landId),
      ]);
      setSelectedLand(landDetails);
      setLandTrees(treesOnLand);
      setLandStructures(structuresOnLand);
    } catch (err) {
      setError((err as Error).message || 'Failed to load land details');
    }
  };

  const handleToggleLand = (landId: number) => {
    if (selectedLand?.id === landId) {
      // Close the currently selected land
      setSelectedLand(null);
      setLandTrees([]);
      setLandStructures([]);
    } else {
      // Open the new land
      handleSelectLand(landId);
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
    await loadData(false);
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
              <p className="land-info">{convertDistance(land.width, unitSystem).toFixed(1)} × {convertDistance(land.height, unitSystem).toFixed(1)} {unitLabels.distanceShort}</p>
              <button
                className="btn-secondary"
                style={selectedLand?.id === land.id
                  ? { backgroundColor: '#3498db', color: 'white' }
                  : { backgroundColor: 'white', color: '#3498db' }}
                onClick={() => handleToggleLand(land.id)}
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
          <StructureManager
            land={selectedLand}
            structures={landStructures}
            onUpdate={handleLandUpdate}
          />
          <LandCanvas
            land={selectedLand}
            gardens={gardens}
            trees={landTrees}
            structures={landStructures}
            onUpdate={handleLandUpdate}
          />
        </div>
      )}
    </div>
  );
}
