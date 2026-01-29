import { useState, useEffect } from 'react';
import { api } from '../services/api';
import type { IrrigationEvent, IrrigationSummary, IrrigationRecommendation } from '../types';

interface IrrigationHistoryProps {
  gardenId?: number;
  plantingEventId?: number;
  days?: number;
  onRefresh?: () => void;
}

export function IrrigationHistory({
  gardenId,
  plantingEventId,
  days = 30,
  onRefresh
}: IrrigationHistoryProps) {
  const [events, setEvents] = useState<IrrigationEvent[]>([]);
  const [summary, setSummary] = useState<IrrigationSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showRecommendations, setShowRecommendations] = useState(true);

  useEffect(() => {
    loadIrrigationData();
  }, [gardenId, plantingEventId, days]);

  const loadIrrigationData = async () => {
    try {
      setLoading(true);
      const data = await api.getIrrigationEvents({
        garden_id: gardenId,
        planting_event_id: plantingEventId,
        days
      });
      setEvents(data.events);
      setSummary(data.summary);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load irrigation history');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (eventId: number) => {
    if (!confirm('Delete this irrigation event?')) return;

    try {
      await api.deleteIrrigationEvent(eventId);
      setEvents(events.filter(e => e.id !== eventId));
      if (onRefresh) onRefresh();
      loadIrrigationData(); // Reload to update summary
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete event');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'on_schedule': return '#4caf50';
      case 'overdue': return '#d32f2f';
      case 'overwatered': return '#ff9800';
      case 'no_data': return '#666';
      default: return '#666';
    }
  };

  const getPriorityBadge = (priority: string) => {
    const colors: Record<string, string> = {
      critical: '#d32f2f',
      high: '#ff9800',
      medium: '#2196f3',
      low: '#4caf50'
    };

    return (
      <span
        style={{
          backgroundColor: colors[priority] || '#666',
          color: 'white',
          padding: '2px 8px',
          borderRadius: '4px',
          fontSize: '0.85em',
          fontWeight: 'bold'
        }}
      >
        {priority.toUpperCase()}
      </span>
    );
  };

  const formatMethod = (method: string) => {
    return method.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
  };

  if (loading) {
    return <div style={{ padding: '20px' }}>Loading irrigation history...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div style={{ padding: '20px' }}>
      <h2>Irrigation History (Last {days} Days)</h2>

      {/* Summary Statistics */}
      {summary && (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
          gap: '15px',
          marginBottom: '20px'
        }}>
          <div style={{
            padding: '15px',
            backgroundColor: '#f5f5f5',
            borderRadius: '8px',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '2em', fontWeight: 'bold', color: '#2196f3' }}>
              {summary.total_events}
            </div>
            <div style={{ fontSize: '0.9em', color: '#666' }}>Total Events</div>
          </div>

          <div style={{
            padding: '15px',
            backgroundColor: '#f5f5f5',
            borderRadius: '8px',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '2em', fontWeight: 'bold', color: '#2196f3' }}>
              {summary.total_volume_liters.toFixed(1)}L
            </div>
            <div style={{ fontSize: '0.9em', color: '#666' }}>Total Volume</div>
          </div>

          {summary.days_since_last_irrigation !== null && (
            <div style={{
              padding: '15px',
              backgroundColor: '#f5f5f5',
              borderRadius: '8px',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: '2em', fontWeight: 'bold', color: '#2196f3' }}>
                {summary.days_since_last_irrigation}
              </div>
              <div style={{ fontSize: '0.9em', color: '#666' }}>Days Since Last</div>
            </div>
          )}

          {summary.average_volume_per_event && (
            <div style={{
              padding: '15px',
              backgroundColor: '#f5f5f5',
              borderRadius: '8px',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: '2em', fontWeight: 'bold', color: '#2196f3' }}>
                {summary.average_volume_per_event.toFixed(1)}L
              </div>
              <div style={{ fontSize: '0.9em', color: '#666' }}>Avg Per Event</div>
            </div>
          )}
        </div>
      )}

      {/* Irrigation Recommendations */}
      {summary && summary.recommendations && summary.recommendations.length > 0 && (
        <div style={{ marginBottom: '20px' }}>
          <button
            onClick={() => setShowRecommendations(!showRecommendations)}
            style={{
              background: 'none',
              border: 'none',
              color: '#2196f3',
              cursor: 'pointer',
              padding: '5px 0',
              fontSize: '1.1em',
              fontWeight: 'bold',
              marginBottom: '10px'
            }}
          >
            {showRecommendations ? '▼' : '▶'} Watering Recommendations ({summary.recommendations.length})
          </button>

          {showRecommendations && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {summary.recommendations
                .sort((a, b) => {
                  const priorityOrder: Record<string, number> = { critical: 0, high: 1, medium: 2, low: 3 };
                  return priorityOrder[a.priority] - priorityOrder[b.priority];
                })
                .map((rec, idx) => (
                  <div
                    key={idx}
                    style={{
                      padding: '15px',
                      borderLeft: `4px solid ${getStatusColor(rec.status)}`,
                      backgroundColor: '#f9f9f9',
                      borderRadius: '4px'
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                      <strong style={{ color: getStatusColor(rec.status) }}>
                        {rec.plant_name}
                      </strong>
                      {getPriorityBadge(rec.priority)}
                    </div>
                    <div style={{ fontSize: '0.85em', color: '#666', marginBottom: '8px' }}>
                      Recommended: Every {rec.recommended_frequency_days} days
                      {rec.recommended_volume_liters && ` • ${rec.recommended_volume_liters.toFixed(1)}L per sq ft`}
                    </div>
                    {rec.days_since_last_watering !== undefined && (
                      <div style={{ fontSize: '0.85em', color: '#666', marginBottom: '8px' }}>
                        Last watered: {rec.days_since_last_watering} days ago
                      </div>
                    )}
                    <div style={{ fontSize: '0.95em', lineHeight: '1.5' }}>
                      {rec.recommendation}
                    </div>
                  </div>
                ))}
            </div>
          )}
        </div>
      )}

      {/* Irrigation Events List */}
      {events.length === 0 ? (
        <div style={{ textAlign: 'center', color: '#666', padding: '20px' }}>
          <p>No irrigation events recorded in the last {days} days.</p>
          <p>Start logging your watering to get personalized recommendations!</p>
        </div>
      ) : (
        <div>
          <h3>Recent Irrigation Events</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {events.map((event) => (
              <div
                key={event.id}
                style={{
                  border: '1px solid #ddd',
                  borderRadius: '8px',
                  padding: '12px',
                  backgroundColor: '#fff',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center'
                }}
              >
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 'bold', marginBottom: '5px' }}>
                    {new Date(event.irrigation_date).toLocaleString()}
                  </div>
                  <div style={{ fontSize: '0.9em', color: '#666' }}>
                    {event.garden_name || 'Garden'}
                    {event.plant_name && ` • ${event.plant_name}`}
                  </div>
                  <div style={{ fontSize: '0.9em', color: '#666', marginTop: '5px' }}>
                    Method: {formatMethod(event.irrigation_method)}
                    {event.water_volume_liters && ` • ${event.water_volume_liters.toFixed(1)}L`}
                    {event.duration_minutes && ` • ${event.duration_minutes} min`}
                  </div>
                  {event.notes && (
                    <div style={{ fontSize: '0.85em', color: '#555', marginTop: '5px', fontStyle: 'italic' }}>
                      {event.notes}
                    </div>
                  )}
                </div>
                <button
                  onClick={() => handleDelete(event.id)}
                  className="btn btn-secondary"
                  style={{ fontSize: '0.85em', padding: '4px 8px' }}
                >
                  Delete
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
