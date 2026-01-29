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
        return 'text-green-600';
      case 'low':
      case 'high':
        return 'text-yellow-600';
      default:
        return 'text-gray-400';
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

  const getHealthBadgeColor = (health: string): string => {
    switch (health) {
      case 'good':
        return 'bg-green-100 text-green-800';
      case 'fair':
        return 'bg-yellow-100 text-yellow-800';
      case 'poor':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-600';
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
      <div className="flex justify-between items-center py-2 border-b border-gray-100" title={tooltip}>
        <span className="text-sm text-gray-600">{label}</span>
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium">
            {param.value.toFixed(1)} {param.unit}
          </span>
          <span className={`text-lg ${getStatusColor(param.status)}`}>
            {getStatusIcon(param.status)}
          </span>
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center gap-2 mb-4">
          <span className="text-2xl">🌱</span>
          <h2 className="text-xl font-semibold">Soil Health</h2>
        </div>
        <p className="text-gray-500">Loading soil data...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center gap-2 mb-4">
          <span className="text-2xl">🌱</span>
          <h2 className="text-xl font-semibold">Soil Health</h2>
        </div>
        <p className="text-red-600">{error}</p>
      </div>
    );
  }

  if (!summary || summary.total_samples === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <span className="text-2xl">🌱</span>
            <h2 className="text-xl font-semibold">Soil Health</h2>
          </div>
          {onAddSample && (
            <button
              onClick={onAddSample}
              className="btn btn-primary"
              style={{ padding: '6px 12px', fontSize: '0.875rem' }}
            >
              + Add Sample
            </button>
          )}
        </div>
        <div className="text-center py-8">
          <p className="text-gray-500 mb-2">No soil samples recorded yet</p>
          <p className="text-sm text-gray-400">Add soil samples to track soil health</p>
          {onAddSample && (
            <button
              onClick={onAddSample}
              className="btn btn-primary"
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
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <span className="text-2xl">🌱</span>
          <h2 className="text-xl font-semibold">Soil Health</h2>
        </div>
        <div className="flex items-center gap-2">
          <span className={`px-3 py-1 rounded-full text-xs font-medium ${getHealthBadgeColor(summary.overall_health)}`}>
            {summary.overall_health.toUpperCase()}
          </span>
          {onAddSample && (
            <button
              onClick={onAddSample}
              className="btn btn-primary"
              style={{ padding: '6px 12px', fontSize: '0.875rem' }}
            >
              + Add Sample
            </button>
          )}
        </div>
      </div>

      {summary.garden_name && (
        <p className="text-sm text-gray-600 mb-4">Garden: {summary.garden_name}</p>
      )}

      {summary.last_sample_date && (
        <p className="text-xs text-gray-500 mb-4">
          Last sampled: {new Date(summary.last_sample_date).toLocaleDateString()}
        </p>
      )}

      <div className="space-y-1 mb-6">
        {renderParameter('pH Level', summary.ph, 'Optimal: 6.0-7.0 for most plants')}
        {renderParameter('Nitrogen (N)', summary.nitrogen, 'Optimal: 20-50 ppm')}
        {renderParameter('Phosphorus (P)', summary.phosphorus, 'Optimal: 15-40 ppm')}
        {renderParameter('Potassium (K)', summary.potassium, 'Optimal: 80-200 ppm')}
        {renderParameter('Organic Matter', summary.organic_matter, 'Optimal: >3%')}
        {renderParameter('Moisture', summary.moisture, 'Optimal: 40-60%')}
      </div>

      {summary.recommendations.length > 0 && (
        <div className="space-y-2 mb-4">
          <h3 className="text-sm font-medium text-gray-700">Recommendations</h3>
          {summary.recommendations.map((rec, idx) => (
            <div
              key={idx}
              className={`p-3 rounded border text-sm ${getSeverityColor(rec.severity)}`}
            >
              <strong>{rec.parameter.toUpperCase()}:</strong> {rec.message}
            </div>
          ))}
        </div>
      )}

      {(summary.ph_trend.length > 1 || summary.moisture_trend.length > 1) && (
        <div className="border-t pt-4">
          <p className="text-xs text-gray-500">
            {summary.total_samples} samples collected • Trends available for pH and moisture
          </p>
        </div>
      )}
    </div>
  );
}
