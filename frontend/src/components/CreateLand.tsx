import { useState } from 'react';
import { api } from '../services/api';
import type { LandCreate } from '../types';
import { useUnitSystem } from '../contexts/UnitSystemContext';
import { convertDistance, convertToMeters, getUnitLabels } from '../utils/units';
import './CreateLand.css';

interface CreateLandProps {
  onCreated: () => void;
  onCancel: () => void;
}

export function CreateLand({ onCreated, onCancel }: CreateLandProps) {
  const { unitSystem } = useUnitSystem();
  const unitLabels = getUnitLabels(unitSystem);

  const [formData, setFormData] = useState<LandCreate>({
    name: '',
    width: convertDistance(10, unitSystem),
    height: convertDistance(10, unitSystem),
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // Convert form data from display units to meters for API
      const apiData = {
        ...formData,
        width: convertToMeters(formData.width, unitSystem),
        height: convertToMeters(formData.height, unitSystem),
      };
      await api.createLand(apiData);
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
            <label htmlFor="width">Width * ({unitLabels.distanceShort})</label>
            <input
              type="number"
              id="width"
              name="width"
              value={formData.width}
              onChange={handleChange}
              required
              min={unitSystem === 'imperial' ? '1' : '0.5'}
              step={unitSystem === 'imperial' ? '1' : '0.5'}
            />
            <small>East-west dimension of your land</small>
          </div>

          <div className="form-group">
            <label htmlFor="height">Height * ({unitLabels.distanceShort})</label>
            <input
              type="number"
              id="height"
              name="height"
              value={formData.height}
              onChange={handleChange}
              required
              min={unitSystem === 'imperial' ? '1' : '0.5'}
              step={unitSystem === 'imperial' ? '1' : '0.5'}
            />
            <small>North-south dimension of your land</small>
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
        <p><strong>About Dimensions:</strong></p>
        <p>
          Enter the dimensions of your land in {unitLabels.distance}.
          For example, a 10×10 land represents a 10{unitLabels.distanceShort} × 10{unitLabels.distanceShort} area.
          You can place gardens, trees, and structures on this land.
        </p>
      </div>
    </div>
  );
}
