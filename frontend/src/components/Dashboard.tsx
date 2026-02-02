import { useState, useEffect } from 'react';
import { api } from '../services/api';
import type { Task, User, SeedBatch, Garden, SensorReading, SystemStats } from '../types';
import { TaskList } from './TaskList';
import { CreateSeedBatch } from './CreateSeedBatch';
import { CreatePlantingEvent } from './CreatePlantingEvent';
import { CreateGarden } from './CreateGarden';
import { CreateSensorReading } from './CreateSensorReading';
import { CreateSoilSample } from './CreateSoilSample';
import { CreateIrrigationEvent } from './CreateIrrigationEvent';
import { Profile } from './Profile';
import { PlantingsList } from './PlantingsList';
import { SoilHealthCard } from './SoilHealthCard';
import { SoilSampleList } from './SoilSampleList';
import { IrrigationOverviewCard } from './IrrigationOverviewCard';
import { RuleInsightsCard } from './RuleInsightsCard';
import { LandList } from './LandList';
import { IrrigationDashboard } from './IrrigationDashboard';
import { IrrigationZoneManager } from './IrrigationZoneManager';
import { GardenDetails } from './GardenDetails';
import { Onboarding } from './Onboarding';

interface DashboardProps {
  user: User;
  onLogout: () => void;
  onUserUpdate?: (user: User) => void;
}

export function Dashboard({ user: initialUser, onLogout, onUserUpdate }: DashboardProps) {
  // Show onboarding wizard for new users
  if (!initialUser.has_completed_onboarding) {
    return (
      <Onboarding
        user={initialUser}
        onComplete={(updatedUser) => {
          if (onUserUpdate) {
            onUserUpdate(updatedUser);
          }
        }}
      />
    );
  }
  const [user, setUser] = useState(initialUser);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [seedBatches, setSeedBatches] = useState<SeedBatch[]>([]);
  const [gardens, setGardens] = useState<Garden[]>([]);
  const [sensorReadings, setSensorReadings] = useState<SensorReading[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeModal, setActiveModal] = useState<'seed' | 'planting' | 'profile' | 'garden' | 'sensor' | 'soil' | 'irrigation' | null>(null);
  const [priorityFilter, setPriorityFilter] = useState<'all' | 'high' | 'medium' | 'low'>('all');
  const [deletingGardenId, setDeletingGardenId] = useState<number | null>(null);
  const [confirmDeleteGardenId, setConfirmDeleteGardenId] = useState<number | null>(null);
  const [viewMode, setViewMode] = useState<'dashboard' | 'plantings' | 'land-layout' | 'irrigation-system' | 'garden-details'>('dashboard');
  const [selectedGardenId, setSelectedGardenId] = useState<number | undefined>(undefined);
  const [systemStats, setSystemStats] = useState<SystemStats | null>(null);

  // Update selected garden when gardens load or change
  useEffect(() => {
    if (gardens.length === 0) {
      // No gardens, clear selection
      setSelectedGardenId(undefined);
    } else if (selectedGardenId === undefined) {
      // No selection, select first garden
      setSelectedGardenId(gardens[0].id);
    } else {
      // Check if currently selected garden still exists
      const gardenExists = gardens.some(g => g.id === selectedGardenId);
      if (!gardenExists) {
        // Selected garden was deleted, select first available
        setSelectedGardenId(gardens[0].id);
      }
    }
  }, [gardens, selectedGardenId]);

  // Update user when prop changes
  useEffect(() => {
    setUser(initialUser);
  }, [initialUser]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [tasksData, batchesData, gardensData, readingsData] = await Promise.all([
        api.getTasks('pending'),
        api.getSeedBatches(),
        api.getGardens(),
        api.getSensorReadings(),
      ]);
      setTasks(tasksData);
      setSeedBatches(batchesData);
      setGardens(gardensData);
      setSensorReadings(readingsData);
      setError('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // Load system stats only for admin users
  useEffect(() => {
    const loadSystemStats = async () => {
      if (user.is_admin) {
        try {
          const stats = await api.getSystemStats();
          setSystemStats(stats);
        } catch (err) {
          console.error('Failed to load system stats:', err);
        }
      }
    };

    loadSystemStats();
  }, [user.is_admin]);

  const handleTaskComplete = async (taskId: number) => {
    try {
      await api.completeTask(taskId, new Date().toISOString().split('T')[0]);
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to complete task');
    }
  };

  const handleSeedBatchCreated = () => {
    setActiveModal(null);
    loadData();
  };

  const handlePlantingEventCreated = () => {
    setActiveModal(null);
    loadData();
  };

  const handleGardenCreated = () => {
    setActiveModal(null);
    loadData();
  };

  const handleSensorReadingCreated = () => {
    setActiveModal(null);
    loadData();
  };

  const handleSoilSampleCreated = () => {
    setActiveModal(null);
    loadData();
  };

  const handleIrrigationEventCreated = () => {
    setActiveModal(null);
    loadData();
  };

  const handleDeleteSeedBatch = async (batchId: number, plantName: string) => {
    if (!window.confirm(`Delete seed batch for ${plantName}?`)) {
      return;
    }

    try {
      await api.deleteSeedBatch(batchId);
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete seed batch');
    }
  };

  const handleDeleteGarden = async (gardenId: number) => {
    setDeletingGardenId(gardenId);
    try {
      await api.deleteGarden(gardenId);
      setGardens(gardens.filter(g => g.id !== gardenId));
      setConfirmDeleteGardenId(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete garden');
    } finally {
      setDeletingGardenId(null);
    }
  };

  // Filter tasks for today and upcoming
  const today = new Date().toISOString().split('T')[0];

  const applyFilters = (taskList: Task[]) => {
    return taskList.filter(t =>
      priorityFilter === 'all' || t.priority === priorityFilter
    );
  };

  const todayTasks = applyFilters(tasks.filter(t => t.due_date === today));
  const upcomingTasks = applyFilters(tasks.filter(t => t.due_date > today));

  // Calculate stats
  const stats = {
    high: tasks.filter(t => t.priority === 'high').length,
    medium: tasks.filter(t => t.priority === 'medium').length,
    low: tasks.filter(t => t.priority === 'low').length,
    total: tasks.length,
    recurring: tasks.filter(t => t.is_recurring).length,
  };

  return (
    <>
      <div className="header">
        <h1>🌱 Gardening Helper</h1>
        <div className="header-right">
          <button onClick={() => setActiveModal('profile')} className="btn btn-secondary" style={{ marginRight: '10px' }}>
            Profile
          </button>
          <button onClick={onLogout} className="btn btn-secondary">
            Logout
          </button>
        </div>
      </div>

      <div className="container">
        <div style={{ padding: '15px 0', borderBottom: '1px solid #ddd', marginBottom: '20px' }}>
          <h2 style={{ margin: '0 0 5px 0' }}>
            Welcome{user.display_name ? `, ${user.display_name}` : ''}! 👋
          </h2>
          <div style={{ fontSize: '0.9em', color: '#666' }}>
            {user.city && <span>{user.city} • </span>}
            {user.usda_zone && <span>Zone {user.usda_zone}</span>}
            {!user.city && !user.usda_zone && <span>{user.email}</span>}
          </div>
          {user.gardening_preferences && (
            <div style={{ marginTop: '8px', fontSize: '0.85em', color: '#555', fontStyle: 'italic' }}>
              {user.gardening_preferences}
            </div>
          )}
        </div>

        <div className="dashboard">
          {error && <div className="error">{error}</div>}

          <div className="card" style={{ maxWidth: '1200px' }}>
            <h2>Quick Actions</h2>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '10px', marginTop: '15px' }}>
              <button className="btn" onClick={() => setActiveModal('garden')}>
                Create Garden
              </button>
              <button className="btn" onClick={() => setActiveModal('seed')}>
                Add Seed Batch
              </button>
              <button className="btn" onClick={() => setActiveModal('planting')}>
                Create Planting
              </button>
              <button className="btn" onClick={() => setActiveModal('sensor')}>
                Add Sensor Reading
              </button>
              <button
                className="btn"
                style={{ backgroundColor: viewMode === 'plantings' ? '#4a90e2' : undefined }}
                onClick={() => setViewMode(viewMode === 'plantings' ? 'dashboard' : 'plantings')}
              >
                {viewMode === 'plantings' ? 'Back to Dashboard' : 'View Plantings'}
              </button>
              <button
                className="btn"
                style={{ backgroundColor: viewMode === 'land-layout' ? '#4a90e2' : undefined }}
                onClick={() => setViewMode(viewMode === 'land-layout' ? 'dashboard' : 'land-layout')}
              >
                {viewMode === 'land-layout' ? 'Back to Dashboard' : 'Land Layout'}
              </button>
              <button
                className="btn"
                style={{ backgroundColor: viewMode === 'irrigation-system' ? '#4a90e2' : undefined }}
                onClick={() => setViewMode(viewMode === 'irrigation-system' ? 'dashboard' : 'irrigation-system')}
              >
                {viewMode === 'irrigation-system' ? 'Back to Dashboard' : 'Irrigation System'}
              </button>
              {selectedGardenId && (
                <button
                  className="btn"
                  style={{ backgroundColor: viewMode === 'garden-details' ? '#4a90e2' : undefined }}
                  onClick={() => setViewMode(viewMode === 'garden-details' ? 'dashboard' : 'garden-details')}
                >
                  {viewMode === 'garden-details' ? 'Back to Dashboard' : 'Garden Details'}
                </button>
              )}
            </div>
          </div>

          {gardens.length > 1 && viewMode === 'dashboard' && (
            <div className="card">
              <h2>Garden Selection</h2>
              <div style={{ marginTop: '15px' }}>
                <label style={{ display: 'block', marginBottom: '5px', fontWeight: '500' }}>
                  View data for:
                </label>
                <select
                  value={selectedGardenId || ''}
                  onChange={(e) => setSelectedGardenId(e.target.value ? Number(e.target.value) : undefined)}
                  style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
                >
                  {gardens.map(garden => (
                    <option key={garden.id} value={garden.id}>
                      {garden.name} ({garden.garden_type})
                    </option>
                  ))}
                </select>
              </div>
            </div>
          )}

          {loading ? (
            <div className="loading">Loading...</div>
          ) : viewMode === 'garden-details' && selectedGardenId ? (
            <GardenDetails
              gardenId={selectedGardenId}
              onBack={() => setViewMode('dashboard')}
            />
          ) : viewMode === 'plantings' ? (
            <PlantingsList />
          ) : viewMode === 'land-layout' ? (
            <LandList />
          ) : viewMode === 'irrigation-system' ? (
            <>
              <IrrigationDashboard />
              <IrrigationZoneManager />
            </>
          ) : (
            <>
              <div className="card">
                <SoilHealthCard gardenId={selectedGardenId} onAddSample={() => setActiveModal('soil')} />
              </div>

              <div className="card">
                <SoilSampleList gardenId={selectedGardenId} onRefresh={loadData} />
              </div>

              <div className="card">
                <RuleInsightsCard gardenId={selectedGardenId} />
              </div>

              <div className="card">
                <IrrigationOverviewCard gardenId={selectedGardenId} onLogWatering={() => setActiveModal('irrigation')} />
              </div>

              <div className="card">
                <h2>Gardens ({gardens.length})</h2>
                {gardens.length === 0 ? (
                  <p style={{ color: '#666', fontStyle: 'italic' }}>
                    No gardens yet. Create one to start tracking your plants!
                  </p>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                    {gardens.map((garden) => (
                      <div
                        key={garden.id}
                        style={{
                          padding: '10px',
                          border: '1px solid #ddd',
                          borderRadius: '4px',
                          backgroundColor: garden.garden_type === 'indoor' ? '#f0f8ff' : '#f9f9f9',
                        }}
                      >
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                          <div style={{ flex: 1 }}>
                            <div style={{ fontWeight: 'bold', marginBottom: '5px' }}>
                              {garden.name}
                              <span style={{
                                marginLeft: '10px',
                                padding: '2px 8px',
                                backgroundColor: garden.garden_type === 'indoor' ? '#4a90e2' : '#5cb85c',
                                color: 'white',
                                borderRadius: '3px',
                                fontSize: '0.75em',
                                textTransform: 'uppercase'
                              }}>
                                {garden.garden_type}
                              </span>
                            </div>
                            {garden.description && (
                              <div style={{ fontSize: '0.9em', color: '#666', marginBottom: '5px' }}>
                                {garden.description}
                              </div>
                            )}
                            {garden.garden_type === 'indoor' && (
                              <div style={{ fontSize: '0.85em', color: '#555', marginTop: '5px' }}>
                                {garden.location && `Location: ${garden.location}`}
                                {garden.light_source_type && ` • Light: ${garden.light_source_type.toUpperCase()}`}
                                {garden.light_hours_per_day && ` (${garden.light_hours_per_day}h/day)`}
                                {garden.temp_min_f && garden.temp_max_f && ` • Temp: ${garden.temp_min_f}-${garden.temp_max_f}°F`}
                                {garden.humidity_min_percent && garden.humidity_max_percent && ` • Humidity: ${garden.humidity_min_percent}-${garden.humidity_max_percent}%`}
                              </div>
                            )}
                          </div>
                          <button
                            onClick={() => setConfirmDeleteGardenId(garden.id)}
                            style={{
                              marginLeft: '10px',
                              padding: '5px 12px',
                              fontSize: '0.85em',
                              backgroundColor: '#dc3545',
                              color: 'white',
                              border: 'none',
                              borderRadius: '4px',
                              cursor: deletingGardenId === garden.id ? 'not-allowed' : 'pointer',
                              whiteSpace: 'nowrap',
                              flexShrink: 0
                            }}
                            disabled={deletingGardenId === garden.id}
                          >
                            {deletingGardenId === garden.id ? 'Deleting...' : 'Delete'}
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="card">
                <h2>Seed Batches ({seedBatches.length})</h2>
                {seedBatches.length === 0 ? (
                  <p style={{ color: '#666', fontStyle: 'italic' }}>
                    No seed batches yet. Add one to track your seeds!
                  </p>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                    {seedBatches.map((batch) => (
                      <div
                        key={batch.id}
                        style={{
                          padding: '10px',
                          border: '1px solid #ddd',
                          borderRadius: '4px',
                          backgroundColor: '#f9f9f9',
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center'
                        }}
                      >
                        {batch.plant_variety?.photo_url && (
                          <img
                            src={batch.plant_variety.photo_url}
                            alt={batch.plant_variety.common_name}
                            style={{ width: '60px', height: '60px', objectFit: 'cover', borderRadius: '4px', marginRight: '15px' }}
                            onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }}
                          />
                        )}
                        <div style={{ flex: 1 }}>
                          <div style={{ fontWeight: 'bold' }}>
                            {batch.plant_variety?.common_name || `Plant #${batch.plant_variety_id}`}
                            {batch.plant_variety?.variety_name && ` (${batch.plant_variety.variety_name})`}
                          </div>
                          {batch.plant_variety?.tags && (
                            <div style={{ fontSize: '0.8em', marginTop: '3px' }}>
                              {batch.plant_variety.tags.split(',').map((tag: string) => (
                                <span key={tag} style={{ display: 'inline-block', backgroundColor: '#e3f2fd', padding: '2px 6px', borderRadius: '3px', marginRight: '4px', marginTop: '2px' }}>
                                  {tag.trim()}
                                </span>
                              ))}
                            </div>
                          )}
                          <div style={{ fontSize: '0.9em', color: '#666', marginTop: '5px' }}>
                            {batch.source && `Source: ${batch.source}`}
                            {batch.harvest_year && ` • Year: ${batch.harvest_year}`}
                            {batch.quantity && ` • Quantity: ${batch.quantity} seeds`}
                            {batch.preferred_germination_method && ` • Method: ${batch.preferred_germination_method}`}
                          </div>
                        </div>
                        <button
                          onClick={() => handleDeleteSeedBatch(
                            batch.id,
                            batch.plant_variety?.common_name || `Plant #${batch.plant_variety_id}`
                          )}
                          className="btn btn-secondary"
                          style={{ marginLeft: '10px', padding: '5px 10px', fontSize: '0.9em' }}
                        >
                          Delete
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {gardens.filter(g => g.garden_type === 'indoor').length > 0 && (
                <div className="card">
                  <h2>Recent Sensor Readings</h2>
                  {sensorReadings.length === 0 ? (
                    <p style={{ color: '#666', fontStyle: 'italic' }}>
                      No sensor readings yet. Add readings to track your indoor garden environment.
                    </p>
                  ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                      {sensorReadings.slice(0, 5).map((reading) => {
                        const garden = gardens.find(g => g.id === reading.garden_id);
                        return (
                          <div
                            key={reading.id}
                            style={{
                              padding: '10px',
                              border: '1px solid #ddd',
                              borderRadius: '4px',
                              backgroundColor: '#f0f8ff',
                            }}
                          >
                            <div style={{ fontWeight: 'bold', marginBottom: '5px' }}>
                              {garden?.name || `Garden #${reading.garden_id}`}
                              <span style={{ marginLeft: '10px', color: '#666', fontSize: '0.9em', fontWeight: 'normal' }}>
                                {new Date(reading.reading_date).toLocaleDateString()}
                              </span>
                            </div>
                            <div style={{ fontSize: '0.9em', color: '#555' }}>
                              {reading.temperature_f && `Temperature: ${reading.temperature_f}°F`}
                              {reading.humidity_percent && ` • Humidity: ${reading.humidity_percent}%`}
                              {reading.light_hours && ` • Light: ${reading.light_hours}h`}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              )}

              <div className="card">
                <h2>Task Statistics</h2>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', gap: '10px', marginTop: '15px' }}>
                  <div style={{ padding: '10px', backgroundColor: '#f5f5f5', borderRadius: '4px', textAlign: 'center' }}>
                    <div style={{ fontSize: '1.5em', fontWeight: 'bold' }}>{stats.total}</div>
                    <div style={{ fontSize: '0.9em', color: '#666' }}>Total Tasks</div>
                  </div>
                  <div style={{ padding: '10px', backgroundColor: '#ffebee', borderRadius: '4px', textAlign: 'center' }}>
                    <div style={{ fontSize: '1.5em', fontWeight: 'bold', color: '#d32f2f' }}>{stats.high}</div>
                    <div style={{ fontSize: '0.9em', color: '#666' }}>High Priority</div>
                  </div>
                  <div style={{ padding: '10px', backgroundColor: '#fff3e0', borderRadius: '4px', textAlign: 'center' }}>
                    <div style={{ fontSize: '1.5em', fontWeight: 'bold', color: '#f57c00' }}>{stats.medium}</div>
                    <div style={{ fontSize: '0.9em', color: '#666' }}>Medium Priority</div>
                  </div>
                  <div style={{ padding: '10px', backgroundColor: '#e8f5e9', borderRadius: '4px', textAlign: 'center' }}>
                    <div style={{ fontSize: '1.5em', fontWeight: 'bold', color: '#388e3c' }}>{stats.low}</div>
                    <div style={{ fontSize: '0.9em', color: '#666' }}>Low Priority</div>
                  </div>
                  <div style={{ padding: '10px', backgroundColor: '#e3f2fd', borderRadius: '4px', textAlign: 'center' }}>
                    <div style={{ fontSize: '1.5em', fontWeight: 'bold', color: '#1976d2' }}>{stats.recurring}</div>
                    <div style={{ fontSize: '0.9em', color: '#666' }}>Recurring</div>
                  </div>
                </div>
              </div>

              <div className="card">
                <h2>Filters</h2>
                <div style={{ marginTop: '15px' }}>
                  <label style={{ display: 'block', marginBottom: '5px', fontWeight: '500' }}>Priority</label>
                  <select
                    value={priorityFilter}
                    onChange={(e) => setPriorityFilter(e.target.value as typeof priorityFilter)}
                    style={{ width: '200px', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
                  >
                    <option value="all">All Priorities</option>
                    <option value="high">High Priority</option>
                    <option value="medium">Medium Priority</option>
                    <option value="low">Low Priority</option>
                  </select>
                </div>
              </div>

              <div className="card">
                <h2>Tasks for Today</h2>
                <TaskList
                  tasks={todayTasks}
                  onComplete={handleTaskComplete}
                  emptyMessage="No tasks for today! 🎉"
                />
              </div>

              <div className="card">
                <h2>Upcoming Tasks</h2>
                <TaskList
                  tasks={upcomingTasks}
                  onComplete={handleTaskComplete}
                  emptyMessage="No upcoming tasks. Create a planting event to get started."
                />
              </div>
            </>
          )}
        </div>
      </div>

      {activeModal === 'seed' && (
        <CreateSeedBatch
          onClose={() => setActiveModal(null)}
          onSuccess={handleSeedBatchCreated}
        />
      )}

      {activeModal === 'planting' && (
        <CreatePlantingEvent
          onClose={() => setActiveModal(null)}
          onSuccess={handlePlantingEventCreated}
        />
      )}

      {activeModal === 'profile' && (
        <Profile
          user={user}
          onUpdate={(updatedUser) => {
            setUser(updatedUser);
            onUserUpdate?.(updatedUser);
          }}
          onClose={() => setActiveModal(null)}
        />
      )}

      {activeModal === 'garden' && (
        <CreateGarden
          user={user}
          onClose={() => setActiveModal(null)}
          onSuccess={handleGardenCreated}
        />
      )}

      {activeModal === 'sensor' && (
        <CreateSensorReading
          onClose={() => setActiveModal(null)}
          onSuccess={handleSensorReadingCreated}
        />
      )}

      {activeModal === 'soil' && (
        <CreateSoilSample
          onClose={() => setActiveModal(null)}
          onSuccess={handleSoilSampleCreated}
        />
      )}

      {activeModal === 'irrigation' && (
        <CreateIrrigationEvent
          onClose={() => setActiveModal(null)}
          onSuccess={handleIrrigationEventCreated}
        />
      )}

      {/* Delete Garden Confirmation Modal */}
      {confirmDeleteGardenId !== null && (
        <div className="modal-overlay" onClick={() => setConfirmDeleteGardenId(null)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Delete Garden?</h2>
            <p>
              Are you sure you want to delete <strong>{gardens.find(g => g.id === confirmDeleteGardenId)?.name}</strong>?
            </p>
            <p style={{ color: '#d32f2f', fontSize: '0.9em' }}>
              ⚠️ This will permanently delete all plantings, sensor readings, soil samples, irrigation events, and tasks associated with this garden.
            </p>
            <div className="form-actions">
              <button
                onClick={() => setConfirmDeleteGardenId(null)}
                className="btn btn-secondary"
              >
                Cancel
              </button>
              <button
                onClick={() => handleDeleteGarden(confirmDeleteGardenId)}
                className="btn"
                style={{ backgroundColor: '#d32f2f' }}
                disabled={deletingGardenId === confirmDeleteGardenId}
              >
                {deletingGardenId === confirmDeleteGardenId ? 'Deleting...' : 'Delete Garden'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Admin Footer - Only rendered for admin users */}
      {user.is_admin && systemStats && (
        <div style={{
          position: 'fixed',
          bottom: 0,
          left: 0,
          right: 0,
          backgroundColor: '#2c3e50',
          color: 'white',
          padding: '10px 20px',
          borderTop: '2px solid #e74c3c',
          fontSize: '0.85em',
          zIndex: 1000
        }}>
          <div style={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            gap: '30px',
            maxWidth: '1200px',
            margin: '0 auto'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
              <span style={{ color: '#ecf0f1', fontWeight: '500' }}>Admin View</span>
              <span style={{ color: '#95a5a6' }}>|</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
              <span style={{ color: '#bdc3c7' }}>Total Users:</span>
              <span style={{ fontWeight: 'bold' }}>{systemStats.total_users}</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
              <span style={{ color: '#bdc3c7' }}>Active (24h):</span>
              <span style={{ fontWeight: 'bold' }}>{systemStats.active_users_24h}</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
              <span style={{ color: '#bdc3c7' }}>Total Gardens:</span>
              <span style={{ fontWeight: 'bold' }}>{systemStats.total_gardens}</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
              <span style={{ color: '#bdc3c7' }}>Total Lands:</span>
              <span style={{ fontWeight: 'bold' }}>{systemStats.total_lands}</span>
            </div>
            <div style={{ fontSize: '0.75em', color: '#95a5a6' }}>
              Updated: {new Date(systemStats.timestamp).toLocaleTimeString()}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
