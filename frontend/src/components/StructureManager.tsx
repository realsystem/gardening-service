import { useState } from 'react';
import { api } from '../services/api';
import type { Structure, StructureCreate, StructureUpdate, LandWithGardens } from '../types';
import { useUnitSystem } from '../contexts/UnitSystemContext';
import { convertDistance, convertToMeters, getUnitLabels } from '../utils/units';
import './StructureManager.css';

interface StructureManagerProps {
  land: LandWithGardens;
  structures: Structure[];
  onUpdate: () => void;
}

export function StructureManager({ land, structures, onUpdate }: StructureManagerProps) {
  const { unitSystem } = useUnitSystem();
  const unitLabels = getUnitLabels(unitSystem);

  const [isAdding, setIsAdding] = useState(false);
  const [editingStructure, setEditingStructure] = useState<Structure | null>(null);
  const [errorMessage, setErrorMessage] = useState('');
  const [formData, setFormData] = useState<Partial<StructureCreate>>({
    land_id: land.id,
    name: '',
    x: 0,
    y: 0,
    width: convertDistance(5, unitSystem),
    depth: convertDistance(3, unitSystem),
    height: convertDistance(3, unitSystem),
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage('');

    try {
      // Convert form data from display units to meters for API
      const apiData = {
        ...formData,
        width: formData.width !== undefined ? convertToMeters(formData.width, unitSystem) : undefined,
        depth: formData.depth !== undefined ? convertToMeters(formData.depth, unitSystem) : undefined,
        height: formData.height !== undefined ? convertToMeters(formData.height, unitSystem) : undefined,
      };

      if (editingStructure) {
        // Update existing structure
        await api.updateStructure(editingStructure.id, apiData as StructureUpdate);
      } else {
        // Create new structure
        await api.createStructure(apiData as StructureCreate);
      }

      setIsAdding(false);
      setEditingStructure(null);
      setFormData({
        land_id: land.id,
        name: '',
        x: 0,
        y: 0,
        width: convertDistance(5, unitSystem),
        depth: convertDistance(3, unitSystem),
        height: convertDistance(3, unitSystem),
      });
      onUpdate();
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : 'Failed to save structure');
    }
  };

  const handleDelete = async (structureId: number) => {
    if (!confirm('Are you sure you want to remove this structure?')) return;

    try {
      await api.deleteStructure(structureId);
      onUpdate();
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : 'Failed to delete structure');
    }
  };

  const handleEdit = (structure: Structure) => {
    setEditingStructure(structure);
    // Convert structure's meter values to display units
    setFormData({
      name: structure.name,
      x: structure.x,
      y: structure.y,
      width: convertDistance(structure.width, unitSystem),
      depth: convertDistance(structure.depth, unitSystem),
      height: convertDistance(structure.height, unitSystem),
    });
    setIsAdding(true);
  };

  const handleCancel = () => {
    setIsAdding(false);
    setEditingStructure(null);
    setFormData({
      land_id: land.id,
      name: '',
      x: 0,
      y: 0,
      width: convertDistance(5, unitSystem),
      depth: convertDistance(3, unitSystem),
      height: convertDistance(3, unitSystem),
    });
    setErrorMessage('');
  };

  return (
    <div className="structure-manager">
      <div className="structure-manager-header">
        <h3>Structures on {land.name}</h3>
        {!isAdding && (
          <button onClick={() => setIsAdding(true)} className="btn-primary">
            + Add Structure
          </button>
        )}
      </div>

      {errorMessage && (
        <div className="error-message">{errorMessage}</div>
      )}

      {isAdding && (
        <form onSubmit={handleSubmit} className="structure-form">
          <h4>{editingStructure ? 'Edit Structure' : 'Add New Structure'}</h4>

          <div className="form-group">
            <label htmlFor="structure-name">Structure Name *</label>
            <input
              id="structure-name"
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="e.g., Garage, Shed, North Fence"
              required
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="structure-x">X Position * (top-left)</label>
              <input
                id="structure-x"
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
              <label htmlFor="structure-y">Y Position * (top-left)</label>
              <input
                id="structure-y"
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
              <label htmlFor="structure-width">Width * ({unitLabels.distanceShort})</label>
              <input
                id="structure-width"
                type="number"
                step={unitSystem === 'imperial' ? '1' : '0.5'}
                min={unitSystem === 'imperial' ? '1' : '0.5'}
                value={formData.width}
                onChange={(e) => setFormData({ ...formData, width: parseFloat(e.target.value) })}
                required
              />
              <small>Width of structure (east-west)</small>
            </div>

            <div className="form-group">
              <label htmlFor="structure-depth">Depth * ({unitLabels.distanceShort})</label>
              <input
                id="structure-depth"
                type="number"
                step={unitSystem === 'imperial' ? '1' : '0.5'}
                min={unitSystem === 'imperial' ? '1' : '0.5'}
                value={formData.depth}
                onChange={(e) => setFormData({ ...formData, depth: parseFloat(e.target.value) })}
                required
              />
              <small>Depth of structure (north-south)</small>
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="structure-height">Height * ({unitLabels.distanceShort})</label>
            <input
              id="structure-height"
              type="number"
              step={unitSystem === 'imperial' ? '1' : '0.5'}
              min={unitSystem === 'imperial' ? '1' : '0.5'}
              value={formData.height}
              onChange={(e) => setFormData({ ...formData, height: parseFloat(e.target.value) })}
              required
            />
            <small>Height of structure (affects shadow length)</small>
          </div>

          <div className="form-actions">
            <button type="submit" className="btn-primary">
              {editingStructure ? 'Update Structure' : 'Add Structure'}
            </button>
            <button type="button" onClick={handleCancel} className="btn-secondary">
              Cancel
            </button>
          </div>
        </form>
      )}

      <div className="structures-list">
        {structures.length === 0 ? (
          <p className="empty-message">
            No structures on this land. Add a structure to model shadows from buildings, fences, or walls.
          </p>
        ) : (
          <div className="structures-grid">
            {structures.map((structure) => (
              <div key={structure.id} className="structure-card">
                <div className="structure-info">
                  <h4>{structure.name}</h4>
                  <div className="structure-details">
                    <span>Position: ({structure.x.toFixed(1)}, {structure.y.toFixed(1)})</span>
                    <span>Size: {convertDistance(structure.width, unitSystem).toFixed(1)} × {convertDistance(structure.depth, unitSystem).toFixed(1)} {unitLabels.distanceShort}</span>
                    <span>Height: {convertDistance(structure.height, unitSystem).toFixed(1)} {unitLabels.distanceShort}</span>
                  </div>
                </div>
                <div className="structure-actions">
                  <button onClick={() => handleEdit(structure)} className="btn-sm">
                    Edit
                  </button>
                  <button onClick={() => handleDelete(structure.id)} className="btn-sm btn-danger">
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
