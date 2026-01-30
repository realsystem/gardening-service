/**
 * Irrigation Zone Manager
 * CRUD interface for managing irrigation zones
 */
import { useState, useEffect } from 'react';
import { api } from '../services/api';
import type {
  IrrigationZone,
  IrrigationZoneCreate,
  IrrigationSource,
  Garden
} from '../types';
import './IrrigationZoneManager.css';

export function IrrigationZoneManager() {
  const [zones, setZones] = useState<IrrigationZone[]>([]);
  const [sources, setSources] = useState<IrrigationSource[]>([]);
  const [gardens, setGardens] = useState<Garden[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingZone, setEditingZone] = useState<IrrigationZone | null>(null);

  // Form state
  const [formData, setFormData] = useState<IrrigationZoneCreate>({
    name: '',
    delivery_type: 'drip',
    irrigation_source_id: undefined,
    schedule: undefined,
    notes: ''
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [zonesData, sourcesData, gardensData] = await Promise.all([
        api.getIrrigationZones(),
        api.getIrrigationSources(),
        api.getGardens()
      ]);
      setZones(zonesData);
      setSources(sourcesData);
      setGardens(gardensData);
      setError('');
    } catch (err) {
      setError((err as Error).message || 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingZone) {
        await api.updateIrrigationZone(editingZone.id, formData);
      } else {
        await api.createIrrigationZone(formData);
      }
      resetForm();
      await loadData();
    } catch (err) {
      setError((err as Error).message || 'Failed to save zone');
    }
  };

  const handleDelete = async (zoneId: number) => {
    if (!confirm('Delete this irrigation zone? Gardens will be unassigned but not deleted.')) {
      return;
    }
    try {
      await api.deleteIrrigationZone(zoneId);
      await loadData();
    } catch (err) {
      setError((err as Error).message || 'Failed to delete zone');
    }
  };

  const handleEdit = (zone: IrrigationZone) => {
    setEditingZone(zone);
    setFormData({
      name: zone.name,
      delivery_type: zone.delivery_type,
      irrigation_source_id: zone.irrigation_source_id,
      schedule: zone.schedule,
      notes: zone.notes || ''
    });
    setShowCreateForm(true);
  };

  const resetForm = () => {
    setFormData({
      name: '',
      delivery_type: 'drip',
      irrigation_source_id: undefined,
      schedule: undefined,
      notes: ''
    });
    setEditingZone(null);
    setShowCreateForm(false);
  };

  const handleAssignGarden = async (gardenId: number, zoneId: number | null) => {
    try {
      await api.assignGardenToZone(gardenId, zoneId);
      await loadData();
    } catch (err) {
      setError((err as Error).message || 'Failed to assign garden');
    }
  };

  if (loading) {
    return <div className="loading">Loading irrigation zones...</div>;
  }

  return (
    <div className="zone-manager">
      <div className="zone-manager-header">
        <h2>Irrigation Zone Management</h2>
        <button
          className="btn-primary"
          onClick={() => setShowCreateForm(!showCreateForm)}
        >
          {showCreateForm ? 'Cancel' : '+ Create Zone'}
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {showCreateForm && (
        <div className="card zone-form">
          <h3>{editingZone ? 'Edit Zone' : 'Create Zone'}</h3>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Zone Name *</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
                placeholder="e.g., Vegetable Garden Zone"
              />
            </div>

            <div className="form-group">
              <label>Delivery Type *</label>
              <select
                value={formData.delivery_type}
                onChange={(e) => setFormData({ ...formData, delivery_type: e.target.value as any })}
                required
              >
                <option value="drip">Drip Irrigation</option>
                <option value="sprinkler">Sprinkler</option>
                <option value="soaker">Soaker Hose</option>
                <option value="manual">Manual Watering</option>
              </select>
            </div>

            {sources.length > 0 && (
              <div className="form-group">
                <label>Water Source</label>
                <select
                  value={formData.irrigation_source_id || ''}
                  onChange={(e) => setFormData({
                    ...formData,
                    irrigation_source_id: e.target.value ? Number(e.target.value) : undefined
                  })}
                >
                  <option value="">None</option>
                  {sources.map(source => (
                    <option key={source.id} value={source.id}>
                      {source.name} ({source.source_type})
                    </option>
                  ))}
                </select>
              </div>
            )}

            <div className="schedule-section">
              <h4>Watering Schedule (Optional)</h4>
              <div className="form-row">
                <div className="form-group">
                  <label>Frequency (days)</label>
                  <input
                    type="number"
                    min="1"
                    value={formData.schedule?.frequency_days || ''}
                    onChange={(e) => setFormData({
                      ...formData,
                      schedule: {
                        ...formData.schedule,
                        frequency_days: e.target.value ? Number(e.target.value) : undefined
                      }
                    })}
                    placeholder="e.g., 3"
                  />
                </div>
                <div className="form-group">
                  <label>Duration (minutes)</label>
                  <input
                    type="number"
                    min="1"
                    value={formData.schedule?.duration_minutes || ''}
                    onChange={(e) => setFormData({
                      ...formData,
                      schedule: {
                        ...formData.schedule,
                        duration_minutes: e.target.value ? Number(e.target.value) : undefined
                      }
                    })}
                    placeholder="e.g., 30"
                  />
                </div>
              </div>
            </div>

            <div className="form-group">
              <label>Notes</label>
              <textarea
                value={formData.notes}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                rows={3}
                placeholder="Optional notes about this zone..."
              />
            </div>

            <div className="form-actions">
              <button type="submit" className="btn-primary">
                {editingZone ? 'Update Zone' : 'Create Zone'}
              </button>
              <button type="button" onClick={resetForm} className="btn-secondary">
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Zones List */}
      {zones.length === 0 ? (
        <div className="card empty-state">
          <p>No irrigation zones yet. Create one to organize your watering schedule.</p>
        </div>
      ) : (
        <div className="zones-list">
          {zones.map(zone => {
            const zoneGardens = gardens.filter(g => g.irrigation_zone_id === zone.id);
            return (
              <div key={zone.id} className="card zone-card-detailed">
                <div className="zone-card-header">
                  <div>
                    <h3>{zone.name}</h3>
                    <span className={`delivery-badge ${zone.delivery_type}`}>
                      {zone.delivery_type}
                    </span>
                  </div>
                  <div className="zone-actions">
                    <button onClick={() => handleEdit(zone)} className="btn-icon" title="Edit">
                      ✏️
                    </button>
                    <button onClick={() => handleDelete(zone.id)} className="btn-icon" title="Delete">
                      🗑️
                    </button>
                  </div>
                </div>

                <div className="zone-details">
                  {zone.schedule && (
                    <div className="detail-row">
                      <strong>Schedule:</strong>
                      <span>
                        Every {zone.schedule.frequency_days || '?'} days
                        {zone.schedule.duration_minutes && ` for ${zone.schedule.duration_minutes} min`}
                      </span>
                    </div>
                  )}
                  {zone.notes && (
                    <div className="detail-row">
                      <strong>Notes:</strong>
                      <span>{zone.notes}</span>
                    </div>
                  )}
                </div>

                <div className="zone-gardens">
                  <strong>Assigned Gardens ({zone.garden_count || 0}):</strong>
                  {zoneGardens.length > 0 ? (
                    <ul>
                      {zoneGardens.map(garden => (
                        <li key={garden.id}>
                          {garden.name}
                          <button
                            onClick={() => handleAssignGarden(garden.id, null)}
                            className="btn-link"
                            title="Unassign"
                          >
                            ✕
                          </button>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="no-gardens">No gardens assigned</p>
                  )}
                </div>

                {/* Unassigned gardens for this zone */}
                {gardens.filter(g => !g.irrigation_zone_id).length > 0 && (
                  <div className="assign-section">
                    <label>Assign garden to this zone:</label>
                    <select
                      onChange={(e) => {
                        if (e.target.value) {
                          handleAssignGarden(Number(e.target.value), zone.id);
                          e.target.value = '';
                        }
                      }}
                      defaultValue=""
                    >
                      <option value="">Select a garden...</option>
                      {gardens
                        .filter(g => !g.irrigation_zone_id)
                        .map(garden => (
                          <option key={garden.id} value={garden.id}>
                            {garden.name}
                          </option>
                        ))}
                    </select>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Unassigned Gardens Warning */}
      {gardens.filter(g => !g.irrigation_zone_id).length > 0 && (
        <div className="card warning-card">
          <h4>⚠️ Unassigned Gardens</h4>
          <p>The following gardens are not assigned to any irrigation zone:</p>
          <ul>
            {gardens
              .filter(g => !g.irrigation_zone_id)
              .map(garden => (
                <li key={garden.id}>{garden.name}</li>
              ))}
          </ul>
          <p className="help-text">
            Assign them to zones above to track watering schedules and get irrigation insights.
          </p>
        </div>
      )}
    </div>
  );
}
