import { useState, useEffect } from 'react';
import { api } from '../services/api';
import type { SensorReading } from '../types';

interface GardenSensorReadingsProps {
  gardenId: number;
}

export function GardenSensorReadings({ gardenId }: GardenSensorReadingsProps) {
  const [readings, setReadings] = useState<SensorReading[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filterType, setFilterType] = useState<string>('all');

  useEffect(() => {
    loadReadings();
  }, [gardenId]);

  const loadReadings = async () => {
    try {
      setLoading(true);
      const data = await api.getGardenSensorReadings(gardenId);
      setReadings(data);
      setError('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load sensor readings');
    } finally {
      setLoading(false);
    }
  };

  const getSensorTypes = (): string[] => {
    const types = new Set<string>();
    readings.forEach(reading => {
      if (reading.temperature_f !== null && reading.temperature_f !== undefined) types.add('temperature');
      if (reading.humidity_percent !== null && reading.humidity_percent !== undefined) types.add('humidity');
      if (reading.light_hours !== null && reading.light_hours !== undefined) types.add('light');
      if (reading.ph_level !== null && reading.ph_level !== undefined) types.add('ph');
      if (reading.ec_ms_cm !== null && reading.ec_ms_cm !== undefined) types.add('ec');
      if (reading.ppm !== null && reading.ppm !== undefined) types.add('ppm');
      if (reading.water_temp_f !== null && reading.water_temp_f !== undefined) types.add('water_temp');
    });
    return Array.from(types);
  };

  const filteredReadings = readings.filter(reading => {
    if (filterType === 'all') return true;
    switch (filterType) {
      case 'temperature':
        return reading.temperature_f !== null && reading.temperature_f !== undefined;
      case 'humidity':
        return reading.humidity_percent !== null && reading.humidity_percent !== undefined;
      case 'light':
        return reading.light_hours !== null && reading.light_hours !== undefined;
      case 'ph':
        return reading.ph_level !== null && reading.ph_level !== undefined;
      case 'ec':
        return reading.ec_ms_cm !== null && reading.ec_ms_cm !== undefined;
      case 'ppm':
        return reading.ppm !== null && reading.ppm !== undefined;
      case 'water_temp':
        return reading.water_temp_f !== null && reading.water_temp_f !== undefined;
      default:
        return true;
    }
  });

  if (loading) {
    return <div style={{ padding: '15px' }}>Loading sensor readings...</div>;
  }

  if (error) {
    return <div className="error" style={{ margin: '15px' }}>{error}</div>;
  }

  const sensorTypes = getSensorTypes();

  return (
    <div style={{ marginTop: '30px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
        <h2>Sensor Readings</h2>
        {sensorTypes.length > 0 && (
          <div>
            <label style={{ marginRight: '10px' }}>Filter by Type:</label>
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              style={{ padding: '5px 10px' }}
            >
              <option value="all">All Types</option>
              {sensorTypes.map(type => (
                <option key={type} value={type}>
                  {type.replace('_', ' ').toUpperCase()}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {filteredReadings.length === 0 ? (
        <div style={{ padding: '30px', textAlign: 'center', backgroundColor: '#f5f5f5', borderRadius: '8px' }}>
          <p style={{ color: '#666', margin: 0 }}>
            {readings.length === 0
              ? 'No sensor readings yet. Add readings to track environmental conditions.'
              : 'No readings match the selected filter.'}
          </p>
        </div>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ backgroundColor: '#f5f5f5' }}>
                <th style={{ padding: '12px', textAlign: 'left', borderBottom: '2px solid #ddd' }}>Date</th>
                <th style={{ padding: '12px', textAlign: 'right', borderBottom: '2px solid #ddd' }}>Temp (°F)</th>
                <th style={{ padding: '12px', textAlign: 'right', borderBottom: '2px solid #ddd' }}>Humidity (%)</th>
                <th style={{ padding: '12px', textAlign: 'right', borderBottom: '2px solid #ddd' }}>Light (hrs)</th>
                <th style={{ padding: '12px', textAlign: 'right', borderBottom: '2px solid #ddd' }}>pH</th>
                <th style={{ padding: '12px', textAlign: 'right', borderBottom: '2px solid #ddd' }}>EC (mS/cm)</th>
                <th style={{ padding: '12px', textAlign: 'right', borderBottom: '2px solid #ddd' }}>PPM</th>
                <th style={{ padding: '12px', textAlign: 'right', borderBottom: '2px solid #ddd' }}>Water Temp (°F)</th>
              </tr>
            </thead>
            <tbody>
              {filteredReadings.map((reading) => (
                <tr key={reading.id} style={{ borderBottom: '1px solid #eee' }}>
                  <td style={{ padding: '12px' }}>
                    {new Date(reading.reading_date).toLocaleDateString()}
                  </td>
                  <td style={{ padding: '12px', textAlign: 'right' }}>
                    {reading.temperature_f !== null && reading.temperature_f !== undefined
                      ? reading.temperature_f.toFixed(1)
                      : '-'}
                  </td>
                  <td style={{ padding: '12px', textAlign: 'right' }}>
                    {reading.humidity_percent !== null && reading.humidity_percent !== undefined
                      ? reading.humidity_percent.toFixed(1)
                      : '-'}
                  </td>
                  <td style={{ padding: '12px', textAlign: 'right' }}>
                    {reading.light_hours !== null && reading.light_hours !== undefined
                      ? reading.light_hours.toFixed(1)
                      : '-'}
                  </td>
                  <td style={{ padding: '12px', textAlign: 'right' }}>
                    {reading.ph_level !== null && reading.ph_level !== undefined
                      ? reading.ph_level.toFixed(2)
                      : '-'}
                  </td>
                  <td style={{ padding: '12px', textAlign: 'right' }}>
                    {reading.ec_ms_cm !== null && reading.ec_ms_cm !== undefined
                      ? reading.ec_ms_cm.toFixed(2)
                      : '-'}
                  </td>
                  <td style={{ padding: '12px', textAlign: 'right' }}>
                    {reading.ppm !== null && reading.ppm !== undefined
                      ? reading.ppm
                      : '-'}
                  </td>
                  <td style={{ padding: '12px', textAlign: 'right' }}>
                    {reading.water_temp_f !== null && reading.water_temp_f !== undefined
                      ? reading.water_temp_f.toFixed(1)
                      : '-'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
