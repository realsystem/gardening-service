import { useState, useEffect } from 'react';
import { api } from '../services/api';
import type { Task, User, SeedBatch } from '../types';
import { TaskList } from './TaskList';
import { CreateSeedBatch } from './CreateSeedBatch';
import { CreatePlantingEvent } from './CreatePlantingEvent';

interface DashboardProps {
  user: User;
  onLogout: () => void;
}

export function Dashboard({ user, onLogout }: DashboardProps) {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [seedBatches, setSeedBatches] = useState<SeedBatch[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeModal, setActiveModal] = useState<'seed' | 'planting' | null>(null);
  const [priorityFilter, setPriorityFilter] = useState<'all' | 'high' | 'medium' | 'low'>('all');

  const loadData = async () => {
    try {
      setLoading(true);
      const [tasksData, batchesData] = await Promise.all([
        api.getTasks('pending'),
        api.getSeedBatches(),
      ]);
      setTasks(tasksData);
      setSeedBatches(batchesData);
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
          <span>{user.email}</span>
          <button onClick={onLogout} className="btn btn-secondary">
            Logout
          </button>
        </div>
      </div>

      <div className="container">
        <div className="dashboard">
          {error && <div className="error">{error}</div>}

          <div className="card">
            <h2>Quick Actions</h2>
            <div style={{ display: 'flex', gap: '10px', marginTop: '15px' }}>
              <button className="btn" onClick={() => setActiveModal('seed')}>
                Add Seed Batch
              </button>
              <button className="btn" onClick={() => setActiveModal('planting')}>
                Create Planting Event
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
                        <div style={{ flex: 1 }}>
                          <div style={{ fontWeight: 'bold' }}>
                            {batch.plant_variety?.common_name || `Plant #${batch.plant_variety_id}`}
                            {batch.plant_variety?.variety_name && ` (${batch.plant_variety.variety_name})`}
                          </div>
                          <div style={{ fontSize: '0.9em', color: '#666', marginTop: '5px' }}>
                            {batch.source && `Source: ${batch.source}`}
                            {batch.harvest_year && ` • Year: ${batch.harvest_year}`}
                            {batch.quantity && ` • Quantity: ${batch.quantity} seeds`}
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
    </>
  );
}
