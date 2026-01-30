import { useState } from 'react';
import { api } from '../services/api';
import type { LandCreate } from '../types';
import './CreateLand.css';

interface CreateLandProps {
  onCreated: () => void;
  onCancel: () => void;
}

export function CreateLand({ onCreated, onCancel }: CreateLandProps) {
  const [formData, setFormData] = useState<LandCreate>({
    name: '',
    width: 10,
    height: 10,
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await api.createLand(formData);
      onCreated();
    } catch (err) {
      setError((err as Error).message || 'Failed to create land');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'name' ? value : parseFloat(value) || 0,
    }));
  };

  return (
    <div className="create-land-form">
      <h3>Create New Land</h3>
      {error && <div className="error-message">{error}</div>}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="name">Land Name *</label>
          <input
            type="text"
            id="name"
            name="name"
            value={formData.name}
            onChange={handleChange}
            required
            placeholder="e.g., Backyard, Front Garden"
            maxLength={100}
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="width">Width *</label>
            <input
              type="number"
              id="width"
              name="width"
              value={formData.width}
              onChange={handleChange}
              required
              min="0.5"
              step="0.5"
            />
            <small>In abstract units (meters, feet, etc.)</small>
          </div>

          <div className="form-group">
            <label htmlFor="height">Height *</label>
            <input
              type="number"
              id="height"
              name="height"
              value={formData.height}
              onChange={handleChange}
              required
              min="0.5"
              step="0.5"
            />
            <small>In abstract units (meters, feet, etc.)</small>
          </div>
        </div>

        <div className="form-actions">
          <button type="button" onClick={onCancel} className="btn-cancel">
            Cancel
          </button>
          <button type="submit" className="btn-submit" disabled={loading}>
            {loading ? 'Creating...' : 'Create Land'}
          </button>
        </div>
      </form>

      <div className="info-box">
        <p><strong>About Units:</strong></p>
        <p>
          Use any consistent unit system (meters, feet, or grid squares).
          For example, a 10×10 land could represent a 10m × 10m backyard
          or a 10ft × 10ft raised bed area.
        </p>
      </div>
    </div>
  );
}
