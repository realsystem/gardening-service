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

  const getSeverityColor = (severity: string): string => {
    switch (severity) {
      case 'critical':
        return 'bg-red-100 border-red-300 text-red-800';
      case 'warning':
        return 'bg-yellow-100 border-yellow-300 text-yellow-800';
      default:
        return 'bg-blue-100 border-blue-300 text-blue-800';
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
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center gap-2 mb-4">
          <span className="text-2xl">💧</span>
          <h2 className="text-xl font-semibold">Irrigation Overview</h2>
        </div>
        <p className="text-gray-500">Loading irrigation data...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center gap-2 mb-4">
          <span className="text-2xl">💧</span>
          <h2 className="text-xl font-semibold">Irrigation Overview</h2>
        </div>
        <p className="text-red-600">{error}</p>
      </div>
    );
  }

  if (!summary || summary.total_events === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <span className="text-2xl">💧</span>
            <h2 className="text-xl font-semibold">Irrigation Overview</h2>
          </div>
          {onLogWatering && (
            <button
              onClick={onLogWatering}
              className="btn btn-primary"
              style={{ padding: '6px 12px', fontSize: '0.875rem' }}
            >
              + Log Watering
            </button>
          )}
        </div>
        <div className="text-center py-8">
          <p className="text-gray-500 mb-2">No irrigation events recorded yet</p>
          <p className="text-sm text-gray-400">Start tracking watering to monitor patterns</p>
          {onLogWatering && (
            <button
              onClick={onLogWatering}
              className="btn btn-primary"
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
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <span className="text-2xl">💧</span>
          <h2 className="text-xl font-semibold">Irrigation Overview</h2>
        </div>
        {onLogWatering && (
          <button
            onClick={onLogWatering}
            className="btn btn-primary"
            style={{ padding: '6px 12px', fontSize: '0.875rem' }}
          >
            + Log Watering
          </button>
        )}
      </div>

      {summary.garden_name && (
        <p className="text-sm text-gray-600 mb-4">Garden: {summary.garden_name}</p>
      )}

      {/* Recent Activity */}
      <div className="bg-gray-50 rounded-lg p-4 mb-6">
        <h3 className="text-sm font-medium text-gray-700 mb-3">Last Watering</h3>
        {summary.last_irrigation_date ? (
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Date</span>
              <span className="text-sm font-medium">
                {new Date(summary.last_irrigation_date).toLocaleDateString()}
              </span>
            </div>
            {summary.last_irrigation_volume && (
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Volume</span>
                <span className="text-sm font-medium">
                  {summary.last_irrigation_volume.toFixed(1)} L
                </span>
              </div>
            )}
            {summary.last_irrigation_method && (
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Method</span>
                <span className="text-sm font-medium">
                  {formatMethod(summary.last_irrigation_method)}
                </span>
              </div>
            )}
            {summary.days_since_last_watering !== undefined && summary.days_since_last_watering !== null && (
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Days ago</span>
                <span className={`text-sm font-medium ${
                  summary.days_since_last_watering >= 7 ? 'text-yellow-600' : 'text-gray-900'
                }`}>
                  {summary.days_since_last_watering}
                </span>
              </div>
            )}
          </div>
        ) : (
          <p className="text-sm text-gray-500">No recent data</p>
        )}
      </div>

      {/* Weekly Summary */}
      <div className="bg-blue-50 rounded-lg p-4 mb-6">
        <h3 className="text-sm font-medium text-gray-700 mb-3">Last 7 Days</h3>
        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Total water</span>
            <span className="text-sm font-medium">
              {summary.weekly.total_volume_liters.toFixed(1)} L
            </span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Events</span>
            <span className="text-sm font-medium">{summary.weekly.event_count}</span>
          </div>
          {summary.weekly.average_interval_days && (
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Avg interval</span>
              <span className="text-sm font-medium">
                {summary.weekly.average_interval_days.toFixed(1)} days
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Alerts */}
      {summary.alerts.length > 0 && (
        <div className="space-y-2 mb-4">
          <h3 className="text-sm font-medium text-gray-700">Alerts</h3>
          {summary.alerts.map((alert, idx) => (
            <div
              key={idx}
              className={`p-3 rounded border text-sm ${getSeverityColor(alert.severity)}`}
            >
              <div className="font-medium mb-1">
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
      <div className="border-t pt-4">
        <p className="text-xs text-gray-500">
          {summary.total_events} irrigation events recorded
        </p>
      </div>
    </div>
  );
}
