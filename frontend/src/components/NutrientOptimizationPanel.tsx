import { useState, useEffect } from 'react';
import { api } from '../services/api';
import type { NutrientOptimization } from '../types';
import './NutrientOptimizationPanel.css';

interface NutrientOptimizationPanelProps {
  gardenId: number;
}

export function NutrientOptimizationPanel({ gardenId }: NutrientOptimizationPanelProps) {
  const [data, setData] = useState<NutrientOptimization | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadOptimization = async () => {
      try {
        setLoading(true);
        const result = await api.getNutrientOptimization(gardenId);
        setData(result);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load nutrient optimization');
      } finally {
        setLoading(false);
      }
    };

    loadOptimization();
  }, [gardenId]);

  if (loading) {
    return (
      <div className="nutrient-optimization-panel">
        <h3>💧 Nutrient Optimization</h3>
        <p>Loading nutrient recommendations...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="nutrient-optimization-panel">
        <h3>💧 Nutrient Optimization</h3>
        <div className="error">{error}</div>
      </div>
    );
  }

  if (!data) {
    return null;
  }

  // Calculate percentage positions for visual bars (only after data is confirmed non-null)
  const ecMinPercent = ((data.ec_recommendation?.min_ms_cm ?? 0) / 4.0) * 100;
  const ecMaxPercent = ((data.ec_recommendation?.max_ms_cm ?? 0) / 4.0) * 100;
  const ecWidth = ecMaxPercent - ecMinPercent;

  const phMinPercent = ((data.ph_recommendation?.min_ph ?? 0) / 14.0) * 100;
  const phMaxPercent = ((data.ph_recommendation?.max_ph ?? 0) / 14.0) * 100;
  const phWidth = phMaxPercent - phMinPercent;

  // Additional safety checks for required data
  if (!data.ec_recommendation || !data.ph_recommendation || !data.replacement_schedule) {
    return (
      <div className="nutrient-optimization-panel">
        <h3>💧 Nutrient Optimization</h3>
        <div className="error">Incomplete optimization data received</div>
      </div>
    );
  }

  return (
    <div className="nutrient-optimization-panel">
      <h3>💧 Nutrient Optimization</h3>

      {/* System Info */}
      <div className="system-info">
        <span className="system-type">{data.system_type?.toUpperCase() ?? 'UNKNOWN'}</span>
        {data.active_plantings && data.active_plantings.length > 0 && (
          <span className="plant-count">
            {data.active_plantings.length} active plant{data.active_plantings.length !== 1 ? 's' : ''}
          </span>
        )}
      </div>

      {/* EC Range Visualization */}
      <div className="metric-section">
        <h4>EC Range (Electrical Conductivity)</h4>
        <div className="range-bar-container">
          <div className="range-bar">
            <div
              className="optimal-band ec-band"
              style={{
                left: `${ecMinPercent}%`,
                width: `${ecWidth}%`
              }}
            />
          </div>
          <div className="range-labels">
            <span className="label-min">0.0</span>
            <span className="label-optimal">
              {(data.ec_recommendation?.min_ms_cm ?? 0).toFixed(1)} - {(data.ec_recommendation?.max_ms_cm ?? 0).toFixed(1)} mS/cm
            </span>
            <span className="label-max">4.0</span>
          </div>
        </div>
        <p className="rationale">{data.ec_recommendation.rationale}</p>
      </div>

      {/* pH Range Visualization */}
      <div className="metric-section">
        <h4>pH Range</h4>
        <div className="range-bar-container">
          <div className="range-bar ph-bar">
            <div
              className="optimal-band ph-band"
              style={{
                left: `${phMinPercent}%`,
                width: `${phWidth}%`
              }}
            />
          </div>
          <div className="range-labels">
            <span className="label-min">0.0</span>
            <span className="label-optimal">
              {(data.ph_recommendation?.min_ph ?? 0).toFixed(1)} - {(data.ph_recommendation?.max_ph ?? 0).toFixed(1)}
            </span>
            <span className="label-max">14.0</span>
          </div>
        </div>
        <p className="rationale">{data.ph_recommendation.rationale}</p>
      </div>

      {/* Replacement Schedule */}
      <div className="schedule-section">
        <h4>Solution Management</h4>
        <div className="schedule-timeline">
          <div className="schedule-item">
            <div className="schedule-icon">💧</div>
            <div className="schedule-content">
              <strong>Top-off:</strong> Every {data.replacement_schedule.topoff_interval_days} day{data.replacement_schedule.topoff_interval_days !== 1 ? 's' : ''}
              <span className="help-text">Replace evaporated water</span>
            </div>
          </div>
          <div className="schedule-item">
            <div className="schedule-icon">🔄</div>
            <div className="schedule-content">
              <strong>Full Change:</strong> Every {data.replacement_schedule.full_replacement_days} days
              <span className="help-text">Prevent salt buildup</span>
            </div>
          </div>
        </div>
        <p className="rationale">{data.replacement_schedule.rationale}</p>
      </div>

      {/* Active Plantings */}
      {data.active_plantings && data.active_plantings.length > 0 && (
        <div className="plantings-section">
          <h4>Active Plantings</h4>
          <div className="planting-list">
            {data.active_plantings.map((planting, index) => (
              <div key={index} className="planting-item">
                <span className="plant-name">{planting.plant_name ?? 'Unknown'}</span>
                <span className={`growth-stage stage-${planting.growth_stage ?? 'unknown'}`}>
                  {planting.growth_stage ?? 'unknown'}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Warnings/Alerts */}
      {data.warnings && data.warnings.length > 0 && (
        <div className="warnings-section">
          <h4>Alerts & Warnings</h4>
          {data.warnings.map((warning, warnIndex) => (
            <div key={warning.warning_id ?? `warning-${warnIndex}`} className={`alert alert-${warning.severity ?? 'info'}`}>
              <div className="alert-icon">
                {warning.severity === 'critical' ? '🔴' : warning.severity === 'warning' ? '⚠️' : 'ℹ️'}
              </div>
              <div className="alert-content">
                <strong>{warning.message ?? 'Warning'}</strong>
                <p>{warning.mitigation ?? ''}</p>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Footer */}
      <div className="panel-footer">
        <span className="timestamp">
          Updated: {new Date(data.generated_at).toLocaleString()}
        </span>
      </div>
    </div>
  );
}