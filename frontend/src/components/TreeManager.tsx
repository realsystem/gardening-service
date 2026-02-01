import { useState } from 'react';
import { api } from '../services/api';
import type { Tree, TreeCreate, TreeUpdate, LandWithGardens } from '../types';
import './TreeManager.css';

interface TreeManagerProps {
  land: LandWithGardens;
  trees: Tree[];
  onUpdate: () => void;
}

export function TreeManager({ land, trees, onUpdate }: TreeManagerProps) {
  const [isAdding, setIsAdding] = useState(false);
  const [editingTree, setEditingTree] = useState<Tree | null>(null);
  const [errorMessage, setErrorMessage] = useState('');
  const [formData, setFormData] = useState<Partial<TreeCreate>>({
    land_id: land.id,
    name: '',
    x: 0,
    y: 0,
    canopy_radius: 3,
    height: 10,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage('');

    try {
      if (editingTree) {
        // Update existing tree
        await api.updateTree(editingTree.id, formData as TreeUpdate);
      } else {
        // Create new tree
        await api.createTree(formData as TreeCreate);
      }

      setIsAdding(false);
      setEditingTree(null);
      setFormData({
        land_id: land.id,
        name: '',
        x: 0,
        y: 0,
        canopy_radius: 3,
        height: 10,
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
    setFormData({
      name: tree.name,
      x: tree.x,
      y: tree.y,
      canopy_radius: tree.canopy_radius,
      height: tree.height,
    });
    setIsAdding(true);
  };

  const handleCancel = () => {
    setIsAdding(false);
    setEditingTree(null);
    setFormData({
      land_id: land.id,
      name: '',
      x: 0,
      y: 0,
      canopy_radius: 3,
      height: 10,
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
              <label htmlFor="tree-radius">Canopy Radius * (units)</label>
              <input
                id="tree-radius"
                type="number"
                step="0.5"
                min="0.5"
                value={formData.canopy_radius}
                onChange={(e) => setFormData({ ...formData, canopy_radius: parseFloat(e.target.value) })}
                required
              />
              <small>Radius of the tree's canopy (shade area)</small>
            </div>

            <div className="form-group">
              <label htmlFor="tree-height">Height (units)</label>
              <input
                id="tree-height"
                type="number"
                step="1"
                min="1"
                value={formData.height || ''}
                onChange={(e) => setFormData({ ...formData, height: e.target.value ? parseFloat(e.target.value) : undefined })}
              />
              <small>Optional: Tree height for future calculations</small>
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
                    <span>Canopy: {tree.canopy_radius} units</span>
                    {tree.height && <span>Height: {tree.height} units</span>}
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
