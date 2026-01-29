import { useState, useEffect } from 'react';
import { api } from '../services/api';
import type { Task, User, SeedBatch, Garden, SensorReading } from '../types';
import { TaskList } from './TaskList';
import { CreateSeedBatch } from './CreateSeedBatch';
import { CreatePlantingEvent } from './CreatePlantingEvent';
import { CreateGarden } from './CreateGarden';
import { CreateSensorReading } from './CreateSensorReading';
import { Profile } from './Profile';

interface DashboardProps {
  user: User;
  onLogout: () => void;
}

export function Dashboard({ user: initialUser, onLogout }: DashboardProps) {
  const [user, setUser] = useState(initialUser);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [seedBatches, setSeedBatches] = useState<SeedBatch[]>([]);
  const [gardens, setGardens] = useState<Garden[]>([]);
  const [sensorReadings, setSensorReadings] = useState<SensorReading[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeModal, setActiveModal] = useState<'seed' | 'planting' | 'profile' | 'garden' | 'sensor' | null>(null);
  const [priorityFilter, setPriorityFilter] = useState<'all' | 'high' | 'medium' | 'low'>('all');

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

          <div className="card">
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
            </div>
          </div>

          {loading ? (
            <div className="loading">Loading...</div>
          ) : (
            <>
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
          onUpdate={setUser}
          onClose={() => setActiveModal(null)}
        />
      )}

      {activeModal === 'garden' && (
        <CreateGarden
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
    </>
  );
}
