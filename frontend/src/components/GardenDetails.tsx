import { useState, useEffect } from 'react';
import { api } from '../services/api';
import type { GardenDetails as GardenDetailsType } from '../types';
import { GardenSensorReadings } from './GardenSensorReadings';

interface GardenDetailsProps {
  gardenId: number;
  onBack: () => void;
}

export function GardenDetails({ gardenId, onBack }: GardenDetailsProps) {
  const [details, setDetails] = useState<GardenDetailsType | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadDetails = async () => {
      try {
        setLoading(true);
        const data = await api.getGardenDetails(gardenId);
        setDetails(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load garden details');
      } finally {
        setLoading(false);
      }
    };

    loadDetails();
  }, [gardenId]);

  if (loading) {
    return <div style={{ padding: '20px' }}>Loading garden details...</div>;
  }

  if (error) {
    return (
      <div style={{ padding: '20px' }}>
        <div className="error">{error}</div>
        <button onClick={onBack} className="btn" style={{ marginTop: '15px' }}>
          Back to Gardens
        </button>
      </div>
    );
  }

  if (!details) {
    return null;
  }

  const { garden, plantings, tasks, stats } = details;

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ready_to_harvest': return '#4caf50';
      case 'growing': return '#2196f3';
      case 'pending': return '#ff9800';
      default: return '#666';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return '#d32f2f';
      case 'medium': return '#ff9800';
      case 'low': return '#666';
      default: return '#666';
    }
  };

  return (
    <div style={{ padding: '20px' }}>
      <div style={{ marginBottom: '20px' }}>
        <button onClick={onBack} className="btn btn-secondary">
          ← Back to Gardens
        </button>
      </div>

      {/* Garden Header */}
      <div style={{ marginBottom: '30px' }}>
        <h1>{garden.name}</h1>
        <div style={{ fontSize: '1.1em', color: '#666', marginBottom: '10px' }}>
          {garden.is_hydroponic ? '💧 Hydroponic' : garden.garden_type === 'indoor' ? '🏠 Indoor' : '🌱 Outdoor'}
          {garden.location && ` • ${garden.location}`}
        </div>
        {garden.description && <p style={{ color: '#555' }}>{garden.description}</p>}

        {garden.is_hydroponic && (
          <div style={{ marginTop: '15px', padding: '15px', backgroundColor: '#e3f2fd', borderRadius: '8px' }}>
            <strong>Hydroponic System:</strong> {garden.hydro_system_type?.toUpperCase()}
            {garden.reservoir_size_liters && ` • Reservoir: ${garden.reservoir_size_liters}L`}
            {garden.ph_min !== undefined && garden.ph_max !== undefined && (
              <div style={{ marginTop: '5px' }}>
                pH Range: {garden.ph_min} - {garden.ph_max}
                {garden.ec_min !== undefined && garden.ec_max !== undefined &&
                  ` • EC: ${garden.ec_min} - ${garden.ec_max} mS/cm`}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Stats */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
        gap: '15px',
        marginBottom: '30px'
      }}>
        <div style={{ padding: '15px', backgroundColor: '#f5f5f5', borderRadius: '8px', textAlign: 'center' }}>
          <div style={{ fontSize: '2em', fontWeight: 'bold', color: '#2196f3' }}>{stats.total_plantings}</div>
          <div style={{ fontSize: '0.9em', color: '#666' }}>Total Plantings</div>
        </div>
        <div style={{ padding: '15px', backgroundColor: '#f5f5f5', borderRadius: '8px', textAlign: 'center' }}>
          <div style={{ fontSize: '2em', fontWeight: 'bold', color: '#4caf50' }}>{stats.active_plantings}</div>
          <div style={{ fontSize: '0.9em', color: '#666' }}>Active Plants</div>
        </div>
        <div style={{ padding: '15px', backgroundColor: '#f5f5f5', borderRadius: '8px', textAlign: 'center' }}>
          <div style={{ fontSize: '2em', fontWeight: 'bold', color: '#ff9800' }}>{stats.pending_tasks}</div>
          <div style={{ fontSize: '0.9em', color: '#666' }}>Pending Tasks</div>
        </div>
        <div style={{ padding: '15px', backgroundColor: '#f5f5f5', borderRadius: '8px', textAlign: 'center' }}>
          <div style={{ fontSize: '2em', fontWeight: 'bold', color: '#d32f2f' }}>{stats.high_priority_tasks}</div>
          <div style={{ fontSize: '0.9em', color: '#666' }}>High Priority</div>
        </div>
        <div style={{ padding: '15px', backgroundColor: '#f5f5f5', borderRadius: '8px', textAlign: 'center' }}>
          <div style={{ fontSize: '2em', fontWeight: 'bold', color: '#4caf50' }}>{stats.upcoming_harvests}</div>
          <div style={{ fontSize: '0.9em', color: '#666' }}>Ready to Harvest</div>
        </div>
      </div>

      {/* Plantings */}
      <div style={{ marginBottom: '30px' }}>
        <h2>Plants in this Garden</h2>
        {plantings.length === 0 ? (
          <p style={{ color: '#666' }}>No plants in this garden yet.</p>
        ) : (
          <div style={{ display: 'grid', gap: '15px' }}>
            {plantings.map((planting) => (
              <div
                key={planting.id}
                style={{
                  border: '1px solid #ddd',
                  borderRadius: '8px',
                  padding: '15px',
                  backgroundColor: '#fff',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                  <div style={{ flex: 1 }}>
                    <h3 style={{ margin: '0 0 5px 0' }}>
                      {planting.plant_name}
                      {planting.variety_name && ` - ${planting.variety_name}`}
                    </h3>
                    <div style={{ fontSize: '0.9em', color: '#666' }}>
                      Planted: {new Date(planting.planting_date).toLocaleDateString()}
                      {planting.plant_count && ` • ${planting.plant_count} plants`}
                      {planting.location_in_garden && ` • ${planting.location_in_garden}`}
                    </div>
                    {planting.expected_harvest_date && (
                      <div style={{ fontSize: '0.9em', color: '#666', marginTop: '5px' }}>
                        Expected Harvest: {new Date(planting.expected_harvest_date).toLocaleDateString()}
                        {planting.days_to_harvest && ` (${planting.days_to_harvest} days)`}
                      </div>
                    )}
                  </div>
                  <div
                    style={{
                      padding: '5px 12px',
                      borderRadius: '20px',
                      fontSize: '0.85em',
                      fontWeight: 'bold',
                      color: '#fff',
                      backgroundColor: getStatusColor(planting.status),
                    }}
                  >
                    {planting.status.replace('_', ' ')}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Tasks */}
      <div>
        <h2>Tasks for this Garden</h2>
        {tasks.length === 0 ? (
          <p style={{ color: '#666' }}>No tasks for this garden.</p>
        ) : (
          <div style={{ display: 'grid', gap: '10px' }}>
            {tasks.map((task) => (
              <div
                key={task.id}
                style={{
                  border: '1px solid #ddd',
                  borderRadius: '8px',
                  padding: '12px',
                  backgroundColor: task.status === 'completed' ? '#f5f5f5' : '#fff',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ flex: 1 }}>
                    <strong>{task.title}</strong>
                    <div style={{ fontSize: '0.85em', color: '#666', marginTop: '3px' }}>
                      {task.task_type.replace('_', ' ')} • Due: {new Date(task.due_date).toLocaleDateString()}
                    </div>
                  </div>
                  <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                    <div
                      style={{
                        padding: '3px 8px',
                        borderRadius: '12px',
                        fontSize: '0.75em',
                        fontWeight: 'bold',
                        color: '#fff',
                        backgroundColor: getPriorityColor(task.priority),
                      }}
                    >
                      {task.priority}
                    </div>
                    <div
                      style={{
                        padding: '3px 8px',
                        borderRadius: '12px',
                        fontSize: '0.75em',
                        backgroundColor: task.status === 'completed' ? '#4caf50' : '#ff9800',
                        color: '#fff',
                      }}
                    >
                      {task.status}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Sensor Readings Section */}
      <GardenSensorReadings gardenId={gardenId} />
    </div>
  );
}
