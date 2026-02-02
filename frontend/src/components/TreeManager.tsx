import { useState, useEffect } from 'react';
import { api } from '../services/api';
import type { Tree, TreeCreate, TreeUpdate, LandWithGardens } from '../types';
import { useUnitSystem } from '../contexts/UnitSystemContext';
import { convertDistance, convertToMeters, getUnitLabels } from '../utils/units';
import './TreeManager.css';

interface TreeManagerProps {
  land: LandWithGardens;
  trees: Tree[];
  onUpdate: () => void;
}

interface TreeSpecies {
  id: number;
  common_name: string;
  scientific_name: string;
  variety_name: string | null;
  typical_height_ft: number | null;
  typical_canopy_radius_ft: number | null;
  growth_rate: string | null;
  description: string | null;
  tags: string[] | null;
}

export function TreeManager({ land, trees, onUpdate }: TreeManagerProps) {
  const { unitSystem } = useUnitSystem();
  const unitLabels = getUnitLabels(unitSystem);

  const [isAdding, setIsAdding] = useState(false);
  const [editingTree, setEditingTree] = useState<Tree | null>(null);
  const [errorMessage, setErrorMessage] = useState('');
  const [treeSpecies, setTreeSpecies] = useState<TreeSpecies[]>([]);
  const [loadingSpecies, setLoadingSpecies] = useState(true);
  const [formData, setFormData] = useState<Partial<TreeCreate>>({
    land_id: land.id,
    name: '',
    species_id: undefined,
    x: 0,
    y: 0,
    canopy_radius: undefined,
    height: undefined,
  });

  // Load tree species on component mount
  useEffect(() => {
    loadTreeSpecies();
  }, []);

  const loadTreeSpecies = async () => {
    try {
      const species = await api.getTreeSpecies();
      setTreeSpecies(species);
    } catch (error) {
      setErrorMessage('Failed to load tree species');
    } finally {
      setLoadingSpecies(false);
    }
  };

  const handleSpeciesChange = (speciesId: string) => {
    const selectedSpecies = treeSpecies.find(s => s.id === parseInt(speciesId));
    const autoName = selectedSpecies ? selectedSpecies.common_name : '';

    setFormData({
      ...formData,
      species_id: speciesId ? parseInt(speciesId) : undefined,
      name: autoName
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage('');

    try {
      // Convert form data from display units to meters for API
      const apiData = {
        ...formData,
        canopy_radius: formData.canopy_radius !== undefined
          ? convertToMeters(formData.canopy_radius, unitSystem)
          : undefined,
        height: formData.height !== undefined
          ? convertToMeters(formData.height, unitSystem)
          : undefined,
      };

      if (editingTree) {
        // Update existing tree
        await api.updateTree(editingTree.id, apiData as TreeUpdate);
      } else {
        // Create new tree
        await api.createTree(apiData as TreeCreate);
      }

      setIsAdding(false);
      setEditingTree(null);
      setFormData({
        land_id: land.id,
        name: '',
        species_id: undefined,
        x: 0,
        y: 0,
        canopy_radius: undefined,
        height: undefined,
      });
      onUpdate();
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : 'Failed to save tree');
    }
  };

  const handleDelete = async (treeId: number) => {
    if (!confirm('Are you sure you want to remove this tree?')) return;

    try {
      await api.deleteTree(treeId);
      onUpdate();
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : 'Failed to delete tree');
    }
  };

  const handleEdit = (tree: Tree) => {
    setEditingTree(tree);
    // Convert tree's meter values to display units
    setFormData({
      name: tree.name,
      species_id: tree.species_id || undefined,
      x: tree.x,
      y: tree.y,
      canopy_radius: convertDistance(tree.canopy_radius, unitSystem),
      height: tree.height ? convertDistance(tree.height, unitSystem) : undefined,
    });
    setIsAdding(true);
  };

  const handleCancel = () => {
    setIsAdding(false);
    setEditingTree(null);
    setFormData({
      land_id: land.id,
      name: '',
      species_id: undefined,
      x: 0,
      y: 0,
      canopy_radius: undefined,
      height: undefined,
    });
    setErrorMessage('');
  };

  return (
    <div className="tree-manager">
      <div className="tree-manager-header">
        <h3>Trees on {land.name}</h3>
        {!isAdding && (
          <button onClick={() => setIsAdding(true)} className="btn-primary">
            + Add Tree
          </button>
        )}
      </div>

      {errorMessage && (
        <div className="error-message">{errorMessage}</div>
      )}

      {isAdding && (
        <form onSubmit={handleSubmit} className="tree-form">
          <h4>{editingTree ? 'Edit Tree' : 'Add New Tree'}</h4>

          {editingTree && (
            <div className="form-group">
              <label htmlFor="tree-name">Tree Name *</label>
              <input
                id="tree-name"
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="e.g., Oak in Backyard"
                required
              />
            </div>
          )}

          <div className="form-group">
            <label htmlFor="tree-species">Tree Species *</label>
            {loadingSpecies ? (
              <p>Loading species...</p>
            ) : (
              <select
                id="tree-species"
                value={formData.species_id || ''}
                onChange={(e) => handleSpeciesChange(e.target.value)}
                required
              >
                <option value="">-- Select a tree species --</option>
                {treeSpecies.map((species) => {
                  // Convert height from feet to user's preferred units
                  const heightInMeters = species.typical_height_ft ? species.typical_height_ft * 0.3048 : null;
                  const heightDisplay = heightInMeters
                    ? ` - ${convertDistance(heightInMeters, unitSystem).toFixed(1)}${unitLabels.distanceShort} tall`
                    : '';

                  return (
                    <option key={species.id} value={species.id}>
                      {species.common_name}
                      {species.variety_name && ` (${species.variety_name})`}
                      {heightDisplay}
                    </option>
                  );
                })}
              </select>
            )}
            <small>
              {editingTree
                ? 'Dimensions will be auto-calculated from species defaults'
                : 'Tree name and dimensions will be auto-generated from species'}
            </small>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="tree-x">X Position *</label>
              <input
                id="tree-x"
                type="number"
                step="0.1"
                min="0"
                max={land.width}
                value={formData.x}
                onChange={(e) => setFormData({ ...formData, x: parseFloat(e.target.value) })}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="tree-y">Y Position *</label>
              <input
                id="tree-y"
                type="number"
                step="0.1"
                min="0"
                max={land.height}
                value={formData.y}
                onChange={(e) => setFormData({ ...formData, y: parseFloat(e.target.value) })}
                required
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="tree-radius">Canopy Radius ({unitLabels.distanceShort})</label>
              <input
                id="tree-radius"
                type="number"
                step={unitSystem === 'imperial' ? '1' : '0.5'}
                min={unitSystem === 'imperial' ? '1' : '0.5'}
                value={formData.canopy_radius || ''}
                onChange={(e) => setFormData({ ...formData, canopy_radius: e.target.value ? parseFloat(e.target.value) : undefined })}
              />
              <small>Optional: Override species default canopy radius</small>
            </div>

            <div className="form-group">
              <label htmlFor="tree-height">Height ({unitLabels.distanceShort})</label>
              <input
                id="tree-height"
                type="number"
                step={unitSystem === 'imperial' ? '1' : '1'}
                min={unitSystem === 'imperial' ? '1' : '1'}
                value={formData.height || ''}
                onChange={(e) => setFormData({ ...formData, height: e.target.value ? parseFloat(e.target.value) : undefined })}
              />
              <small>Optional: Override species default height</small>
            </div>
          </div>

          <div className="form-actions">
            <button type="submit" className="btn-primary">
              {editingTree ? 'Update Tree' : 'Add Tree'}
            </button>
            <button type="button" onClick={handleCancel} className="btn-secondary">
              Cancel
            </button>
          </div>
        </form>
      )}

      <div className="trees-list">
        {trees.length === 0 ? (
          <p className="empty-message">
            No trees on this land. Add a tree to see how it affects your gardens' sun exposure.
          </p>
        ) : (
          <div className="trees-grid">
            {trees.map((tree) => (
              <div key={tree.id} className="tree-card">
                <div className="tree-info">
                  <h4>{tree.name}</h4>
                  <div className="tree-details">
                    <span>Position: ({tree.x.toFixed(1)}, {tree.y.toFixed(1)})</span>
                    <span>Canopy: {convertDistance(tree.canopy_radius, unitSystem).toFixed(1)} {unitLabels.distanceShort}</span>
                    {tree.height && <span>Height: {convertDistance(tree.height, unitSystem).toFixed(1)} {unitLabels.distanceShort}</span>}
                    {tree.species_common_name && (
                      <span className="species">{tree.species_common_name}</span>
                    )}
                  </div>
                </div>
                <div className="tree-actions">
                  <button onClick={() => handleEdit(tree)} className="btn-sm">
                    Edit
                  </button>
                  <button onClick={() => handleDelete(tree.id)} className="btn-sm btn-danger">
                    Remove
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
