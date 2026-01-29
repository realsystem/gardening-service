import { useState, useEffect } from 'react';
import { api } from '../services/api';
import type { SoilSample } from '../types';

interface SoilSampleListProps {
  gardenId?: number;
  plantingEventId?: number;
  onRefresh?: () => void;
}

export function SoilSampleList({ gardenId, plantingEventId, onRefresh }: SoilSampleListProps) {
  const [samples, setSamples] = useState<SoilSample[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [expandedId, setExpandedId] = useState<number | null>(null);

  useEffect(() => {
    loadSamples();
  }, [gardenId, plantingEventId]);

  const loadSamples = async () => {
    try {
      setLoading(true);
      const data = await api.getSoilSamples({ garden_id: gardenId, planting_event_id: plantingEventId });
      setSamples(data.samples);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load soil samples');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (sampleId: number) => {
    if (!confirm('Delete this soil sample?')) return;

    try {
      await api.deleteSoilSample(sampleId);
      setSamples(samples.filter(s => s.id !== sampleId));
      if (onRefresh) onRefresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete sample');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'optimal': return '#4caf50';
      case 'low': return '#ff9800';
      case 'high': return '#ff9800';
      case 'critical': return '#d32f2f';
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

  if (loading) {
    return <div style={{ padding: '20px' }}>Loading soil samples...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  if (samples.length === 0) {
    return (
      <div style={{ padding: '20px', textAlign: 'center', color: '#666' }}>
        <p>No soil samples recorded yet.</p>
        <p>Start by taking a soil sample to get science-based recommendations!</p>
      </div>
    );
  }

  return (
    <div style={{ padding: '20px' }}>
      <h2>Soil Sample History</h2>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
        {samples.map((sample) => (
          <div
            key={sample.id}
            style={{
              border: '1px solid #ddd',
              borderRadius: '8px',
              padding: '15px',
              backgroundColor: '#fff'
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '10px' }}>
              <div>
                <h3 style={{ margin: '0 0 5px 0' }}>
                  {sample.garden_name || 'Garden'} - {new Date(sample.date_collected).toLocaleDateString()}
                </h3>
                {sample.plant_name && (
                  <div style={{ fontSize: '0.9em', color: '#666' }}>
                    Plant: {sample.plant_name}
                  </div>
                )}
              </div>
              <button
                onClick={() => handleDelete(sample.id)}
                className="btn btn-secondary"
                style={{ fontSize: '0.85em', padding: '4px 8px' }}
              >
                Delete
              </button>
            </div>

            {/* Soil Chemistry Data */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
              gap: '10px',
              padding: '10px',
              backgroundColor: '#f5f5f5',
              borderRadius: '4px',
              marginBottom: '10px'
            }}>
              <div>
                <div style={{ fontSize: '0.85em', color: '#666' }}>pH</div>
                <div style={{ fontWeight: 'bold' }}>{sample.ph.toFixed(1)}</div>
              </div>
              {sample.nitrogen_ppm !== undefined && (
                <div>
                  <div style={{ fontSize: '0.85em', color: '#666' }}>Nitrogen</div>
                  <div style={{ fontWeight: 'bold' }}>{sample.nitrogen_ppm.toFixed(0)} ppm</div>
                </div>
              )}
              {sample.phosphorus_ppm !== undefined && (
                <div>
                  <div style={{ fontSize: '0.85em', color: '#666' }}>Phosphorus</div>
                  <div style={{ fontWeight: 'bold' }}>{sample.phosphorus_ppm.toFixed(0)} ppm</div>
                </div>
              )}
              {sample.potassium_ppm !== undefined && (
                <div>
                  <div style={{ fontSize: '0.85em', color: '#666' }}>Potassium</div>
                  <div style={{ fontWeight: 'bold' }}>{sample.potassium_ppm.toFixed(0)} ppm</div>
                </div>
              )}
              {sample.organic_matter_percent !== undefined && (
                <div>
                  <div style={{ fontSize: '0.85em', color: '#666' }}>Organic Matter</div>
                  <div style={{ fontWeight: 'bold' }}>{sample.organic_matter_percent.toFixed(1)}%</div>
                </div>
              )}
              {sample.moisture_percent !== undefined && (
                <div>
                  <div style={{ fontSize: '0.85em', color: '#666' }}>Moisture</div>
                  <div style={{ fontWeight: 'bold' }}>{sample.moisture_percent.toFixed(1)}%</div>
                </div>
              )}
            </div>

            {sample.notes && (
              <div style={{ fontSize: '0.9em', color: '#555', marginBottom: '10px', fontStyle: 'italic' }}>
                {sample.notes}
              </div>
            )}

            {/* Scientific Recommendations */}
            {sample.recommendations && sample.recommendations.length > 0 && (
              <div>
                <button
                  onClick={() => setExpandedId(expandedId === sample.id ? null : sample.id)}
                  style={{
                    background: 'none',
                    border: 'none',
                    color: '#2196f3',
                    cursor: 'pointer',
                    padding: '5px 0',
                    fontSize: '0.95em',
                    fontWeight: 'bold'
                  }}
                >
                  {expandedId === sample.id ? '▼' : '▶'} Scientific Recommendations ({sample.recommendations.length})
                </button>

                {expandedId === sample.id && (
                  <div style={{ marginTop: '10px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
                    {sample.recommendations
                      .sort((a, b) => {
                        const priorityOrder: Record<string, number> = { critical: 0, high: 1, medium: 2, low: 3 };
                        return priorityOrder[a.priority] - priorityOrder[b.priority];
                      })
                      .map((rec, idx) => (
                        <div
                          key={idx}
                          style={{
                            padding: '12px',
                            borderLeft: `4px solid ${getStatusColor(rec.status)}`,
                            backgroundColor: '#f9f9f9',
                            borderRadius: '4px'
                          }}
                        >
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                            <strong style={{ color: getStatusColor(rec.status) }}>
                              {rec.parameter}: {rec.current_value.toFixed(1)}
                            </strong>
                            {getPriorityBadge(rec.priority)}
                          </div>
                          <div style={{ fontSize: '0.85em', color: '#666', marginBottom: '5px' }}>
                            Optimal range: {rec.optimal_range}
                          </div>
                          <div style={{ fontSize: '0.9em', lineHeight: '1.5' }}>
                            {rec.recommendation}
                          </div>
                        </div>
                      ))}
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
