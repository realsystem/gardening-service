import { useState, useEffect } from 'react';
import { api } from '../services/api';
import type { GardenRuleInsights, RuleResult, RuleSeverity } from '../types';

interface RuleInsightsCardProps {
  gardenId?: number;
}

export function RuleInsightsCard({ gardenId }: RuleInsightsCardProps) {
  const [insights, setInsights] = useState<GardenRuleInsights | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedSeverity, setSelectedSeverity] = useState<RuleSeverity | 'all'>('all');
  const [expandedRules, setExpandedRules] = useState<Set<string>>(new Set());

  useEffect(() => {
    if (!gardenId) {
      setLoading(false);
      return;
    }

    const loadInsights = async () => {
      try {
        setLoading(true);
        const data = await api.getGardenRuleInsights(gardenId);
        setInsights(data);
        setError('');
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load rule insights');
        setInsights(null);
      } finally {
        setLoading(false);
      }
    };

    loadInsights();
  }, [gardenId]);

  const toggleRule = (ruleId: string) => {
    const newExpanded = new Set(expandedRules);
    if (newExpanded.has(ruleId)) {
      newExpanded.delete(ruleId);
    } else {
      newExpanded.add(ruleId);
    }
    setExpandedRules(newExpanded);
  };

  const getSeverityColor = (severity: RuleSeverity): string => {
    switch (severity) {
      case 'critical':
        return '#d32f2f';
      case 'warning':
        return '#f57c00';
      case 'info':
        return '#1976d2';
      default:
        return '#666';
    }
  };

  const getSeverityBackground = (severity: RuleSeverity): string => {
    switch (severity) {
      case 'critical':
        return '#ffebee';
      case 'warning':
        return '#fff3e0';
      case 'info':
        return '#e3f2fd';
      default:
        return '#f5f5f5';
    }
  };

  const getSeverityIcon = (severity: RuleSeverity): string => {
    switch (severity) {
      case 'critical':
        return '🚨';
      case 'warning':
        return '⚠️';
      case 'info':
        return 'ℹ️';
      default:
        return '';
    }
  };

  const getCategoryLabel = (category: string): string => {
    const labels: Record<string, string> = {
      water_stress: 'Water Stress',
      soil_chemistry: 'Soil Chemistry',
      temperature_stress: 'Temperature Stress',
      light_stress: 'Light Stress',
      growth_stage: 'Growth Stage',
      pest_disease: 'Pest/Disease',
      nutrient_timing: 'Nutrient Timing'
    };
    return labels[category] || category;
  };

  if (!gardenId) {
    return (
      <div>
        <h2>🧪 Scientific Insights</h2>
        <p style={{ color: '#666', fontStyle: 'italic' }}>
          Select a garden to view science-based growing recommendations.
        </p>
      </div>
    );
  }

  if (loading) {
    return (
      <div>
        <h2>🧪 Scientific Insights</h2>
        <div className="loading">Analyzing garden conditions...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div>
        <h2>🧪 Scientific Insights</h2>
        <div className="error">{error}</div>
      </div>
    );
  }

  if (!insights) {
    return (
      <div>
        <h2>🧪 Scientific Insights</h2>
        <p style={{ color: '#666', fontStyle: 'italic' }}>
          No insights available. Add soil samples, sensor readings, and irrigation data to get recommendations.
        </p>
      </div>
    );
  }

  // Ensure triggered_rules is an array
  const triggeredRules = Array.isArray(insights.triggered_rules) ? insights.triggered_rules : [];

  // Ensure rules_by_severity exists with defaults
  const severityCounts = insights.rules_by_severity || { critical: 0, warning: 0, info: 0 };

  const filteredRules = selectedSeverity === 'all'
    ? triggeredRules
    : triggeredRules.filter(r => r.severity === selectedSeverity);

  const sortedRules = [...filteredRules].sort((a, b) => {
    const severityOrder: Record<RuleSeverity, number> = { critical: 0, warning: 1, info: 2 };
    return severityOrder[a.severity] - severityOrder[b.severity];
  });

  return (
    <div>
      <h2>🧪 Scientific Insights</h2>
      <div style={{ fontSize: '0.9em', color: '#666', marginBottom: '15px' }}>
        {insights.garden_name} • Evaluated {new Date(insights.evaluation_time).toLocaleString()}
      </div>

      {triggeredRules.length === 0 ? (
        <div style={{
          padding: '20px',
          backgroundColor: '#e8f5e9',
          borderRadius: '8px',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '2em', marginBottom: '10px' }}>✅</div>
          <div style={{ fontSize: '1.1em', fontWeight: 'bold', color: '#388e3c', marginBottom: '5px' }}>
            All Systems Optimal
          </div>
          <div style={{ color: '#666' }}>
            Your garden conditions are within ideal ranges. Keep up the great work!
          </div>
        </div>
      ) : (
        <>
          {/* Stats Summary */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(100px, 1fr))',
            gap: '10px',
            marginBottom: '20px'
          }}>
            <div
              style={{
                padding: '12px',
                backgroundColor: getSeverityBackground('critical'),
                borderRadius: '4px',
                textAlign: 'center',
                cursor: 'pointer',
                border: selectedSeverity === 'critical' ? '2px solid ' + getSeverityColor('critical') : 'none'
              }}
              onClick={() => setSelectedSeverity(selectedSeverity === 'critical' ? 'all' : 'critical')}
            >
              <div style={{ fontSize: '1.5em', fontWeight: 'bold', color: getSeverityColor('critical') }}>
                {severityCounts.critical}
              </div>
              <div style={{ fontSize: '0.85em', color: '#666' }}>Critical</div>
            </div>
            <div
              style={{
                padding: '12px',
                backgroundColor: getSeverityBackground('warning'),
                borderRadius: '4px',
                textAlign: 'center',
                cursor: 'pointer',
                border: selectedSeverity === 'warning' ? '2px solid ' + getSeverityColor('warning') : 'none'
              }}
              onClick={() => setSelectedSeverity(selectedSeverity === 'warning' ? 'all' : 'warning')}
            >
              <div style={{ fontSize: '1.5em', fontWeight: 'bold', color: getSeverityColor('warning') }}>
                {severityCounts.warning}
              </div>
              <div style={{ fontSize: '0.85em', color: '#666' }}>Warnings</div>
            </div>
            <div
              style={{
                padding: '12px',
                backgroundColor: getSeverityBackground('info'),
                borderRadius: '4px',
                textAlign: 'center',
                cursor: 'pointer',
                border: selectedSeverity === 'info' ? '2px solid ' + getSeverityColor('info') : 'none'
              }}
              onClick={() => setSelectedSeverity(selectedSeverity === 'info' ? 'all' : 'info')}
            >
              <div style={{ fontSize: '1.5em', fontWeight: 'bold', color: getSeverityColor('info') }}>
                {severityCounts.info}
              </div>
              <div style={{ fontSize: '0.85em', color: '#666' }}>Info</div>
            </div>
            {selectedSeverity !== 'all' && (
              <button
                onClick={() => setSelectedSeverity('all')}
                style={{
                  padding: '12px',
                  backgroundColor: '#f5f5f5',
                  borderRadius: '4px',
                  textAlign: 'center',
                  border: 'none',
                  cursor: 'pointer',
                  fontSize: '0.9em',
                  fontWeight: 'bold'
                }}
              >
                Show All
              </button>
            )}
          </div>

          {/* Rule Results */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {sortedRules.map((rule: RuleResult) => {
              const isExpanded = expandedRules.has(rule.rule_id);
              return (
                <div
                  key={rule.rule_id}
                  style={{
                    border: `2px solid ${getSeverityColor(rule.severity)}`,
                    borderRadius: '8px',
                    backgroundColor: 'white',
                    overflow: 'hidden'
                  }}
                >
                  {/* Rule Header (always visible) */}
                  <div
                    onClick={() => toggleRule(rule.rule_id)}
                    style={{
                      padding: '12px',
                      backgroundColor: getSeverityBackground(rule.severity),
                      cursor: 'pointer',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'start'
                    }}
                  >
                    <div style={{ flex: 1 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                        <span style={{ fontSize: '1.2em' }}>{getSeverityIcon(rule.severity)}</span>
                        <span style={{ fontWeight: 'bold', color: getSeverityColor(rule.severity) }}>
                          {rule.title}
                        </span>
                        <span style={{
                          fontSize: '0.75em',
                          padding: '2px 6px',
                          backgroundColor: 'white',
                          borderRadius: '3px',
                          color: '#666'
                        }}>
                          {getCategoryLabel(rule.category)}
                        </span>
                        <span style={{
                          fontSize: '0.75em',
                          padding: '2px 6px',
                          backgroundColor: 'white',
                          borderRadius: '3px',
                          color: '#666'
                        }}>
                          {Math.round(rule.confidence * 100)}% confident
                        </span>
                      </div>
                      <div style={{ fontSize: '0.95em', color: '#444' }}>
                        {rule.explanation}
                      </div>
                      {rule.measured_value !== undefined && rule.optimal_range && (
                        <div style={{ fontSize: '0.85em', color: '#666', marginTop: '4px' }}>
                          Current: {rule.measured_value.toFixed(1)} • Optimal: {rule.optimal_range}
                        </div>
                      )}
                    </div>
                    <div style={{ marginLeft: '10px', fontSize: '1.2em', color: '#666' }}>
                      {isExpanded ? '▼' : '▶'}
                    </div>
                  </div>

                  {/* Expanded Details */}
                  {isExpanded && (
                    <div style={{ padding: '15px', backgroundColor: 'white' }}>
                      {/* Scientific Rationale */}
                      <div style={{ marginBottom: '12px' }}>
                        <div style={{ fontWeight: 'bold', fontSize: '0.9em', color: '#555', marginBottom: '4px' }}>
                          🔬 Scientific Rationale:
                        </div>
                        <div style={{ fontSize: '0.9em', color: '#666', lineHeight: '1.5' }}>
                          {rule.scientific_rationale}
                        </div>
                      </div>

                      {/* Recommended Action */}
                      {rule.recommended_action && (
                        <div style={{ marginBottom: '12px' }}>
                          <div style={{ fontWeight: 'bold', fontSize: '0.9em', color: '#555', marginBottom: '4px' }}>
                            ✅ Recommended Action:
                          </div>
                          <div style={{
                            fontSize: '0.9em',
                            color: '#444',
                            backgroundColor: '#f9f9f9',
                            padding: '10px',
                            borderRadius: '4px',
                            lineHeight: '1.5'
                          }}>
                            {rule.recommended_action}
                          </div>
                        </div>
                      )}

                      {/* References */}
                      {rule.references && rule.references.length > 0 && (
                        <div>
                          <div style={{ fontWeight: 'bold', fontSize: '0.9em', color: '#555', marginBottom: '4px' }}>
                            📚 References:
                          </div>
                          <ul style={{ fontSize: '0.8em', color: '#666', margin: '0', paddingLeft: '20px' }}>
                            {rule.references.map((ref, idx) => (
                              <li key={idx} style={{ marginBottom: '4px' }}>
                                {ref}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
}
