import { useEffect, useState } from 'react';
import { api } from '../services/api';
import type { SoilHealthSummary, SoilParameterStatus } from '../types';

interface SoilHealthCardProps {
  gardenId?: number;
  onAddSample?: () => void;
}

export function SoilHealthCard({ gardenId, onAddSample }: SoilHealthCardProps) {
  const [summary, setSummary] = useState<SoilHealthSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadSummary();
  }, [gardenId]);

  const loadSummary = async () => {
    try {
      setLoading(true);
      const data = await api.getSoilHealthSummary(gardenId);
      setSummary(data);
      setError('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load soil data');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'in_range':
        return '#16a34a';
      case 'low':
      case 'high':
        return '#ca8a04';
      default:
        return '#9ca3af';
    }
  };

  const getStatusIcon = (status: string): string => {
    switch (status) {
      case 'in_range':
        return '✓';
      case 'low':
        return '↓';
      case 'high':
        return '↑';
      default:
        return '?';
    }
  };

  const getHealthBadgeStyle = (health: string): React.CSSProperties => {
    switch (health) {
      case 'good':
        return { backgroundColor: '#dcfce7', color: '#166534' };
      case 'fair':
        return { backgroundColor: '#fef3c7', color: '#92400e' };
      case 'poor':
        return { backgroundColor: '#fee2e2', color: '#991b1b' };
      default:
        return { backgroundColor: '#f3f4f6', color: '#4b5563' };
    }
  };

  const renderParameter = (
    label: string,
    param: SoilParameterStatus | undefined,
    tooltip: string
  ) => {
    if (!param || param.value === undefined || param.value === null) {
      return null;
    }

    return (
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px 0', borderBottom: '1px solid #f3f4f6' }} title={tooltip}>
        <span style={{ fontSize: '0.875rem', color: '#4b5563' }}>{label}</span>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '0.875rem', fontWeight: '500' }}>
            {param.value.toFixed(1)} {param.unit}
          </span>
          <span style={{ fontSize: '1.125rem', color: getStatusColor(param.status) }}>
            {getStatusIcon(param.status)}
          </span>
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
          <span style={{ fontSize: '1.5rem' }}>🌱</span>
          <h2 style={{ fontSize: '1.25rem', fontWeight: '600', margin: 0 }}>Soil Health</h2>
        </div>
        <div className="loading">Loading soil data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
          <span style={{ fontSize: '1.5rem' }}>🌱</span>
          <h2 style={{ fontSize: '1.25rem', fontWeight: '600', margin: 0 }}>Soil Health</h2>
        </div>
        <div className="error">{error}</div>
      </div>
    );
  }

  if (!summary || summary.total_samples === 0) {
    return (
      <div>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '1.5rem' }}>🌱</span>
            <h2 style={{ fontSize: '1.25rem', fontWeight: '600', margin: 0 }}>Soil Health</h2>
          </div>
          {onAddSample && (
            <button
              onClick={onAddSample}
              className="btn"
              style={{ padding: '6px 12px', fontSize: '0.875rem' }}
            >
              + Add Sample
            </button>
          )}
        </div>
        <div style={{ textAlign: 'center', padding: '32px 0' }}>
          <p style={{ color: '#6b7280', marginBottom: '8px' }}>No soil samples recorded yet</p>
          <p style={{ fontSize: '0.875rem', color: '#9ca3af' }}>Add soil samples to track soil health</p>
          {onAddSample && (
            <button
              onClick={onAddSample}
              className="btn"
              style={{ marginTop: '16px' }}
            >
              Add Your First Sample
            </button>
          )}
        </div>
      </div>
    );
  }

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '1.5rem' }}>🌱</span>
          <h2 style={{ fontSize: '1.25rem', fontWeight: '600', margin: 0 }}>Soil Health</h2>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ ...getHealthBadgeStyle(summary.overall_health), padding: '4px 12px', borderRadius: '9999px', fontSize: '0.75rem', fontWeight: '500' }}>
            {summary.overall_health.toUpperCase()}
          </span>
          {onAddSample && (
            <button
              onClick={onAddSample}
              className="btn"
              style={{ padding: '6px 12px', fontSize: '0.875rem' }}
            >
              + Add Sample
            </button>
          )}
        </div>
      </div>

      {summary.garden_name && (
        <p style={{ fontSize: '0.875rem', color: '#4b5563', marginBottom: '16px' }}>Garden: {summary.garden_name}</p>
      )}

      {summary.last_sample_date && (
        <p style={{ fontSize: '0.75rem', color: '#6b7280', marginBottom: '16px' }}>
          Last sampled: {new Date(summary.last_sample_date).toLocaleDateString()}
        </p>
      )}

      <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', marginBottom: '24px' }}>
        {renderParameter('pH Level', summary.ph, 'Optimal: 6.0-7.0 for most plants')}
        {renderParameter('Nitrogen (N)', summary.nitrogen, 'Optimal: 20-50 ppm')}
        {renderParameter('Phosphorus (P)', summary.phosphorus, 'Optimal: 15-40 ppm')}
        {renderParameter('Potassium (K)', summary.potassium, 'Optimal: 80-200 ppm')}
        {renderParameter('Organic Matter', summary.organic_matter, 'Optimal: >3%')}
        {renderParameter('Moisture', summary.moisture, 'Optimal: 40-60%')}
      </div>

      {/* Summary footer */}
      <div style={{ borderTop: '1px solid #e5e7eb', paddingTop: '16px', marginTop: '8px' }}>
        <p style={{ fontSize: '0.75rem', color: '#6b7280' }}>
          {summary.total_samples} sample{summary.total_samples !== 1 ? 's' : ''} collected
          {(summary.ph_trend.length > 1 || summary.moisture_trend.length > 1) && ' • Trends available for pH and moisture'}
        </p>
        {summary.recommendations.length > 0 && (
          <p style={{ fontSize: '0.75rem', color: '#f59e0b', marginTop: '4px' }}>
            💡 See Scientific Insights below for detailed recommendations
          </p>
        )}
      </div>
    </div>
  );
}
