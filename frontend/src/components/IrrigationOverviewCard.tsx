import { useEffect, useState } from 'react';
import { api } from '../services/api';
import type { IrrigationOverviewSummary } from '../types';

interface IrrigationOverviewCardProps {
  gardenId?: number;
  onLogWatering?: () => void;
}

export function IrrigationOverviewCard({ gardenId, onLogWatering }: IrrigationOverviewCardProps) {
  const [summary, setSummary] = useState<IrrigationOverviewSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadSummary();
  }, [gardenId]);

  const loadSummary = async () => {
    try {
      setLoading(true);
      const data = await api.getIrrigationOverviewSummary(gardenId);
      setSummary(data);
      setError('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load irrigation data');
    } finally {
      setLoading(false);
    }
  };

  const getSeverityStyle = (severity: string): React.CSSProperties => {
    switch (severity) {
      case 'critical':
        return { backgroundColor: '#fee2e2', borderColor: '#fca5a5', color: '#991b1b' };
      case 'warning':
        return { backgroundColor: '#fef3c7', borderColor: '#fcd34d', color: '#92400e' };
      default:
        return { backgroundColor: '#dbeafe', borderColor: '#93c5fd', color: '#1e40af' };
    }
  };

  const formatMethod = (method: string): string => {
    return method
      .split('_')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  if (loading) {
    return (
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
          <span style={{ fontSize: '1.5rem' }}>💧</span>
          <h2 style={{ fontSize: '1.25rem', fontWeight: '600', margin: 0 }}>Irrigation Overview</h2>
        </div>
        <div className="loading">Loading irrigation data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
          <span style={{ fontSize: '1.5rem' }}>💧</span>
          <h2 style={{ fontSize: '1.25rem', fontWeight: '600', margin: 0 }}>Irrigation Overview</h2>
        </div>
        <div className="error">{error}</div>
      </div>
    );
  }

  if (!summary || summary.total_events === 0) {
    return (
      <div>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '1.5rem' }}>💧</span>
            <h2 style={{ fontSize: '1.25rem', fontWeight: '600', margin: 0 }}>Irrigation Overview</h2>
          </div>
          {onLogWatering && (
            <button
              onClick={onLogWatering}
              className="btn"
              style={{ padding: '6px 12px', fontSize: '0.875rem' }}
            >
              + Log Watering
            </button>
          )}
        </div>
        <div style={{ textAlign: 'center', padding: '32px 0' }}>
          <p style={{ color: '#6b7280', marginBottom: '8px' }}>No irrigation events recorded yet</p>
          <p style={{ fontSize: '0.875rem', color: '#9ca3af' }}>Start tracking watering to monitor patterns</p>
          {onLogWatering && (
            <button
              onClick={onLogWatering}
              className="btn"
              style={{ marginTop: '16px' }}
            >
              Log Your First Watering
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
          <span style={{ fontSize: '1.5rem' }}>💧</span>
          <h2 style={{ fontSize: '1.25rem', fontWeight: '600', margin: 0 }}>Irrigation Overview</h2>
        </div>
        {onLogWatering && (
          <button
            onClick={onLogWatering}
            className="btn"
            style={{ padding: '6px 12px', fontSize: '0.875rem' }}
          >
            + Log Watering
          </button>
        )}
      </div>

      {summary.garden_name && (
        <p style={{ fontSize: '0.875rem', color: '#4b5563', marginBottom: '16px' }}>Garden: {summary.garden_name}</p>
      )}

      {/* Recent Activity */}
      <div style={{ backgroundColor: '#f9fafb', borderRadius: '8px', padding: '16px', marginBottom: '24px' }}>
        <h3 style={{ fontSize: '0.875rem', fontWeight: '500', color: '#374151', marginBottom: '12px' }}>Last Watering</h3>
        {summary.last_irrigation_date ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '0.875rem', color: '#4b5563' }}>Date</span>
              <span style={{ fontSize: '0.875rem', fontWeight: '500' }}>
                {new Date(summary.last_irrigation_date).toLocaleDateString()}
              </span>
            </div>
            {summary.last_irrigation_volume && (
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '0.875rem', color: '#4b5563' }}>Volume</span>
                <span style={{ fontSize: '0.875rem', fontWeight: '500' }}>
                  {summary.last_irrigation_volume.toFixed(1)} L
                </span>
              </div>
            )}
            {summary.last_irrigation_method && (
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '0.875rem', color: '#4b5563' }}>Method</span>
                <span style={{ fontSize: '0.875rem', fontWeight: '500' }}>
                  {formatMethod(summary.last_irrigation_method)}
                </span>
              </div>
            )}
            {summary.days_since_last_watering !== undefined && summary.days_since_last_watering !== null && (
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '0.875rem', color: '#4b5563' }}>Days ago</span>
                <span style={{ fontSize: '0.875rem', fontWeight: '500', color: summary.days_since_last_watering >= 7 ? '#ca8a04' : '#111827' }}>
                  {summary.days_since_last_watering}
                </span>
              </div>
            )}
          </div>
        ) : (
          <p style={{ fontSize: '0.875rem', color: '#6b7280' }}>No recent data</p>
        )}
      </div>

      {/* Weekly Summary */}
      <div style={{ backgroundColor: '#eff6ff', borderRadius: '8px', padding: '16px', marginBottom: '24px' }}>
        <h3 style={{ fontSize: '0.875rem', fontWeight: '500', color: '#374151', marginBottom: '12px' }}>Last 7 Days</h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.875rem', color: '#4b5563' }}>Total water</span>
            <span style={{ fontSize: '0.875rem', fontWeight: '500' }}>
              {summary.weekly.total_volume_liters.toFixed(1)} L
            </span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.875rem', color: '#4b5563' }}>Events</span>
            <span style={{ fontSize: '0.875rem', fontWeight: '500' }}>{summary.weekly.event_count}</span>
          </div>
          {summary.weekly.average_interval_days && (
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '0.875rem', color: '#4b5563' }}>Avg interval</span>
              <span style={{ fontSize: '0.875rem', fontWeight: '500' }}>
                {summary.weekly.average_interval_days.toFixed(1)} days
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Alerts */}
      {summary.alerts.length > 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '16px' }}>
          <h3 style={{ fontSize: '0.875rem', fontWeight: '500', color: '#374151' }}>Alerts</h3>
          {summary.alerts.map((alert, idx) => (
            <div
              key={idx}
              style={{ ...getSeverityStyle(alert.severity), padding: '12px', borderRadius: '4px', border: '1px solid', fontSize: '0.875rem' }}
            >
              <div style={{ fontWeight: '500', marginBottom: '4px' }}>
                {alert.type === 'under_watering' && '⚠️ Under-watering'}
                {alert.type === 'over_watering' && '💦 Over-watering'}
                {alert.type === 'moisture_mismatch' && 'ℹ️ Moisture Mismatch'}
              </div>
              {alert.message}
            </div>
          ))}
        </div>
      )}

      {/* Summary footer */}
      <div style={{ borderTop: '1px solid #e5e7eb', paddingTop: '16px' }}>
        <p style={{ fontSize: '0.75rem', color: '#6b7280' }}>
          {summary.total_events} irrigation events recorded
        </p>
      </div>
    </div>
  );
}
