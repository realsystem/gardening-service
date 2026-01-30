/**
 * Irrigation Dashboard Component
 *
 * Displays irrigation overview with zones, upcoming waterings, and insights.
 * Models irrigation as a system (zones, not per-plant reminders).
 */
import { useState, useEffect } from 'react';
import { api } from '../services/api';
import type {
  IrrigationOverview,
  IrrigationInsightsResponse,
  IrrigationInsight,
  UpcomingWatering
} from '../types';
import { RecordWatering } from './RecordWatering';
import './IrrigationDashboard.css';

export function IrrigationDashboard() {
  const [overview, setOverview] = useState<IrrigationOverview | null>(null);
  const [insights, setInsights] = useState<IrrigationInsightsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedTab, setSelectedTab] = useState<'overview' | 'insights'>('overview');
  const [showRecordWatering, setShowRecordWatering] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [overviewData, insightsData] = await Promise.all([
        api.getIrrigationOverview(),
        api.getIrrigationInsights()
      ]);
      setOverview(overviewData);
      setInsights(insightsData);
      setError('');
    } catch (err) {
      setError((err as Error).message || 'Failed to load irrigation data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading irrigation system...</div>;
  }

  if (error) {
    return (
      <div className="card">
        <div className="error-message">{error}</div>
        <button onClick={loadData} className="btn-secondary">Retry</button>
      </div>
    );
  }

  if (!overview) {
    return null;
  }

  const handleWateringRecorded = () => {
    setShowRecordWatering(false);
    loadData();
  };

  return (
    <div className="irrigation-dashboard">
      <div className="irrigation-header">
        <h2>Irrigation System</h2>
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <button
            className="btn"
            onClick={() => setShowRecordWatering(true)}
            style={{ padding: '8px 16px', fontSize: '14px' }}
          >
            + Record Watering
          </button>
          <div className="tab-buttons">
            <button
              className={selectedTab === 'overview' ? 'active' : ''}
              onClick={() => setSelectedTab('overview')}
            >
              Overview
            </button>
            <button
              className={selectedTab === 'insights' ? 'active' : ''}
              onClick={() => setSelectedTab('insights')}
            >
              Insights
              {insights && insights.total_count > 0 && (
                <span className="badge">{insights.total_count}</span>
              )}
            </button>
          </div>
        </div>
      </div>

      {selectedTab === 'overview' && (
        <>
          {/* Upcoming Waterings */}
          {overview.upcoming_waterings && overview.upcoming_waterings.length > 0 && (
            <div className="card">
              <h3>Upcoming Waterings</h3>
              <div className="upcoming-list">
                {overview.upcoming_waterings.slice(0, 5).map((watering: UpcomingWatering) => (
                  <div key={watering.zone_id} className={`upcoming-item ${watering.status}`}>
                    <div className="upcoming-info">
                      <strong>{watering.zone_name}</strong>
                      <span className="upcoming-time">
                        {watering.status === 'overdue' && 'Overdue'}
                        {watering.status === 'today' && 'Due Today'}
                        {watering.status === 'upcoming' && `In ${watering.days_until} days`}
                      </span>
                    </div>
                    {watering.last_watered && (
                      <div className="last-watered">
                        Last: {new Date(watering.last_watered).toLocaleDateString()}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Irrigation Zones */}
          <div className="card">
            <h3>Irrigation Zones ({overview.zones.length})</h3>
            {overview.zones.length === 0 ? (
              <p className="empty-state">No irrigation zones yet. Create a zone to organize your watering.</p>
            ) : (
              <div className="zones-grid">
                {overview.zones.map(({ zone, garden_count }) => (
                  <div key={zone.id} className="zone-card">
                    <div className="zone-header">
                      <h4>{zone.name}</h4>
                      <span className={`delivery-badge ${zone.delivery_type}`}>
                        {zone.delivery_type}
                      </span>
                    </div>
                    <div className="zone-info">
                      <div className="info-row">
                        <span className="label">Gardens:</span>
                        <span>{garden_count}</span>
                      </div>
                      {zone.schedule && zone.schedule.frequency_days && (
                        <div className="info-row">
                          <span className="label">Schedule:</span>
                          <span>Every {zone.schedule.frequency_days} days</span>
                        </div>
                      )}
                      {zone.schedule && zone.schedule.duration_minutes && (
                        <div className="info-row">
                          <span className="label">Duration:</span>
                          <span>{zone.schedule.duration_minutes} min</span>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Water Sources */}
          {overview.sources && overview.sources.length > 0 && (
            <div className="card">
              <h3>Water Sources</h3>
              <div className="sources-list">
                {overview.sources.map(source => (
                  <div key={source.id} className="source-item">
                    <strong>{source.name}</strong>
                    <span className="source-type">{source.source_type}</span>
                    {source.flow_capacity_lpm && (
                      <span className="flow-capacity">{source.flow_capacity_lpm} L/min</span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recent Events */}
          {overview.recent_events && overview.recent_events.length > 0 && (
            <div className="card">
              <h3>Recent Watering Events</h3>
              <div className="events-list">
                {overview.recent_events.slice(0, 10).map(event => {
                  const zone = overview.zones.find(z => z.zone.id === event.irrigation_zone_id);
                  return (
                    <div key={event.id} className="event-item">
                      <div className="event-zone">{zone?.zone.name || 'Unknown Zone'}</div>
                      <div className="event-details">
                        <span>{new Date(event.watered_at).toLocaleString()}</span>
                        <span className="duration">{event.duration_minutes} min</span>
                        {event.is_manual && <span className="manual-badge">Manual</span>}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </>
      )}

      {selectedTab === 'insights' && insights && (
        <div className="insights-section">
          {insights.total_count === 0 ? (
            <div className="card">
              <div className="no-insights">
                <h3>No Irrigation Issues Detected</h3>
                <p>Your irrigation practices look good! Continue monitoring and recording watering events for ongoing analysis.</p>
              </div>
            </div>
          ) : (
            <>
              <div className="insights-summary">
                <div className="summary-card critical">
                  <div className="count">{insights.by_severity.critical}</div>
                  <div className="label">Critical</div>
                </div>
                <div className="summary-card warning">
                  <div className="count">{insights.by_severity.warning}</div>
                  <div className="label">Warnings</div>
                </div>
                <div className="summary-card info">
                  <div className="count">{insights.by_severity.info}</div>
                  <div className="label">Info</div>
                </div>
              </div>

              {insights.insights.map((insight: IrrigationInsight, index: number) => (
                <div key={`${insight.rule_id}-${index}`} className={`insight-card ${insight.severity}`}>
                  <div className="insight-header">
                    <h4>{insight.title}</h4>
                    <span className={`severity-badge ${insight.severity}`}>
                      {insight.severity}
                    </span>
                  </div>
                  <div className="insight-explanation">
                    {insight.explanation}
                  </div>
                  <div className="insight-action">
                    <strong>Suggested Action:</strong>
                    <p>{insight.suggested_action}</p>
                  </div>
                  {insight.affected_zones.length > 0 && (
                    <div className="affected">
                      <strong>Affected Zones:</strong> {insight.affected_zones.join(', ')}
                    </div>
                  )}
                </div>
              ))}
            </>
          )}
        </div>
      )}

      {showRecordWatering && (
        <RecordWatering
          onClose={() => setShowRecordWatering(false)}
          onSuccess={handleWateringRecorded}
        />
      )}
    </div>
  );
}
