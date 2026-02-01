import { useState, useEffect } from 'react';
import { api } from '../services/api';
import type { CompanionAnalysisResponse } from '../types';
import './CompanionPlantingInsights.css';

interface CompanionPlantingInsightsProps {
  gardenId: number;
}

export function CompanionPlantingInsights({ gardenId }: CompanionPlantingInsightsProps) {
  const [analysis, setAnalysis] = useState<CompanionAnalysisResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadAnalysis = async () => {
      try {
        setLoading(true);
        const data = await api.getCompanionAnalysis(gardenId);
        setAnalysis(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load companion analysis');
      } finally {
        setLoading(false);
      }
    };

    loadAnalysis();
  }, [gardenId]);

  if (loading) {
    return (
      <div className="companion-insights">
        <h3>🌿 Companion Planting Analysis</h3>
        <p>Loading companion insights...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="companion-insights">
        <h3>🌿 Companion Planting Analysis</h3>
        <div className="error">{error}</div>
      </div>
    );
  }

  if (!analysis) {
    return null;
  }

  const { beneficial_pairs, conflicts, suggestions, summary, message } = analysis;

  if (analysis.planting_count < 2) {
    return (
      <div className="companion-insights">
        <h3>🌿 Companion Planting Analysis</h3>
        <div className="info-message">
          {message || 'Add at least 2 plants to see companion planting insights.'}
        </div>
      </div>
    );
  }

  return (
    <div className="companion-insights">
      <h3>🌿 Companion Planting Analysis</h3>

      {/* Summary Stats */}
      <div className="companion-summary">
        <div className="summary-stat beneficial">
          <div className="stat-value">{summary.beneficial_count}</div>
          <div className="stat-label">Beneficial Pairs</div>
        </div>
        <div className="summary-stat conflicts">
          <div className="stat-value">{summary.conflict_count}</div>
          <div className="stat-label">Conflicts</div>
        </div>
        <div className="summary-stat suggestions">
          <div className="stat-value">{summary.suggestion_count}</div>
          <div className="stat-label">Suggestions</div>
        </div>
      </div>

      {/* Beneficial Pairs */}
      {beneficial_pairs.length > 0 && (
        <div className="companion-section">
          <h4>✅ Beneficial Companion Pairs</h4>
          <div className="companion-list">
            {beneficial_pairs.map((pair, index) => (
              <div key={index} className="companion-card beneficial-card">
                <div className="companion-header">
                  <div className="plant-names">
                    <span className="plant-name">{pair.plant_a.common_name}</span>
                    <span className="separator">+</span>
                    <span className="plant-name">{pair.plant_b.common_name}</span>
                  </div>
                  <div className="companion-badges">
                    <span className={`status-badge ${pair.status}`}>
                      {pair.status === 'optimal' ? '⭐ Optimal' : '✓ Active'}
                    </span>
                    <span className={`confidence-badge ${pair.confidence_level}`}>
                      {pair.confidence_level.toUpperCase()}
                    </span>
                  </div>
                </div>
                <div className="companion-details">
                  <p className="mechanism">{pair.mechanism}</p>
                  <div className="distance-info">
                    <span>Distance: {(pair.distance_m ?? 0).toFixed(1)}m</span>
                    {pair.optimal_distance_m && (
                      <span className="optimal-note">
                        (Optimal: {(pair.optimal_distance_m ?? 0).toFixed(1)}m)
                      </span>
                    )}
                  </div>
                  <p className="source">
                    <strong>Source:</strong> {pair.source_reference}
                  </p>
                  {pair.notes && <p className="notes">{pair.notes}</p>}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Conflicts */}
      {conflicts.length > 0 && (
        <div className="companion-section">
          <h4>⚠️ Planting Conflicts</h4>
          <div className="companion-list">
            {conflicts.map((conflict, index) => (
              <div key={index} className="companion-card conflict-card">
                <div className="companion-header">
                  <div className="plant-names">
                    <span className="plant-name">{conflict.plant_a.common_name}</span>
                    <span className="separator">×</span>
                    <span className="plant-name">{conflict.plant_b.common_name}</span>
                  </div>
                  <div className="companion-badges">
                    <span className="status-badge conflict">⚠️ Conflict</span>
                    <span className={`confidence-badge ${conflict.confidence_level}`}>
                      {conflict.confidence_level.toUpperCase()}
                    </span>
                  </div>
                </div>
                <div className="companion-details">
                  <p className="problem-description">{conflict.problem_description}</p>
                  <p className="mechanism">{conflict.mechanism}</p>
                  <div className="distance-info">
                    <span>Current distance: {(conflict.distance_m ?? 0).toFixed(1)}m</span>
                    <span className="separation-note">
                      (Recommended separation: {(conflict.recommended_separation_m ?? 0).toFixed(1)}m)
                    </span>
                  </div>
                  <p className="source">
                    <strong>Source:</strong> {conflict.source_reference}
                  </p>
                  {conflict.notes && <p className="notes">{conflict.notes}</p>}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Suggestions */}
      {suggestions.length > 0 && (
        <div className="companion-section">
          <h4>💡 Suggestions</h4>
          <div className="suggestion-list">
            {suggestions.map((suggestion, index) => (
              <div key={index} className="suggestion-card">
                <div className="suggestion-header">
                  <span className="suggestion-type">
                    {suggestion.type === 'move_closer' ? '📏 Move Closer' : '📏 Increase Distance'}
                  </span>
                  <span className={`confidence-badge ${suggestion.confidence}`}>
                    {suggestion.confidence.toUpperCase()}
                  </span>
                </div>
                <div className="suggestion-details">
                  <p className="plant-pair">
                    <strong>{suggestion.plant_a}</strong> and <strong>{suggestion.plant_b}</strong>
                  </p>
                  <p className="reason">{suggestion.reason}</p>
                  <div className="distance-recommendation">
                    <span>Current: {(suggestion.current_distance_m ?? 0).toFixed(1)}m</span>
                    <span className="arrow">→</span>
                    <span className="recommended">Recommended: {(suggestion.recommended_distance_m ?? 0).toFixed(1)}m</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {beneficial_pairs.length === 0 && conflicts.length === 0 && suggestions.length === 0 && (
        <div className="info-message">
          No companion planting relationships detected for current plants.
          Try planting complementary vegetables together!
        </div>
      )}
    </div>
  );
}
