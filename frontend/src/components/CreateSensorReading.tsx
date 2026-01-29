import { useState, useEffect } from 'react';
import { api } from '../services/api';
import type { Garden } from '../types';

interface CreateSensorReadingProps {
  onClose: () => void;
  onSuccess: () => void;
}

export function CreateSensorReading({ onClose, onSuccess }: CreateSensorReadingProps) {
  const [gardens, setGardens] = useState<Garden[]>([]);
  const [gardenId, setGardenId] = useState('');
  const [readingDate, setReadingDate] = useState(new Date().toISOString().split('T')[0]);
  const [temperatureF, setTemperatureF] = useState('');
  const [humidityPercent, setHumidityPercent] = useState('');
  const [lightHours, setLightHours] = useState('');
  const [phLevel, setPhLevel] = useState('');
  const [ecMsCm, setEcMsCm] = useState('');
  const [ppm, setPpm] = useState('');
  const [waterTempF, setWaterTempF] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadGardens = async () => {
      try {
        const data = await api.getGardens();
        const indoorGardens = data.filter(g => g.garden_type === 'indoor');
        setGardens(indoorGardens);
      } catch (err) {
        setError('Failed to load gardens');
      }
    };
    loadGardens();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await api.createSensorReading({
        garden_id: parseInt(gardenId),
        reading_date: readingDate,
        temperature_f: temperatureF ? parseFloat(temperatureF) : undefined,
        humidity_percent: humidityPercent ? parseFloat(humidityPercent) : undefined,
        light_hours: lightHours ? parseFloat(lightHours) : undefined,
        ph_level: phLevel ? parseFloat(phLevel) : undefined,
        ec_ms_cm: ecMsCm ? parseFloat(ecMsCm) : undefined,
        ppm: ppm ? parseInt(ppm) : undefined,
        water_temp_f: waterTempF ? parseFloat(waterTempF) : undefined,
      });
      onSuccess();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create sensor reading');
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h2>Add Sensor Reading</h2>

        {error && <div className="error">{error}</div>}

        {gardens.length === 0 ? (
          <div style={{ padding: '15px', backgroundColor: '#fff3cd', borderRadius: '4px', marginBottom: '15px' }}>
            <p style={{ margin: 0 }}>
              No indoor gardens found. Create an indoor garden first to add sensor readings.
            </p>
          </div>
        ) : (
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Indoor Garden *</label>
              <select
                value={gardenId}
                onChange={(e) => setGardenId(e.target.value)}
                required
                disabled={loading}
              >
                <option value="">Select an indoor garden...</option>
                {gardens.map((g) => (
                  <option key={g.id} value={g.id}>
                    {g.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Reading Date *</label>
              <input
                type="date"
                value={readingDate}
                onChange={(e) => setReadingDate(e.target.value)}
                required
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label>Temperature (F)</label>
              <input
                type="number"
                value={temperatureF}
                onChange={(e) => setTemperatureF(e.target.value)}
                placeholder="e.g. 72"
                min="-50"
                max="150"
                step="0.1"
                disabled={loading}
              />
              <small style={{ color: '#666', fontSize: '0.85em' }}>
                Optional: Temperature in Fahrenheit
              </small>
            </div>

            <div className="form-group">
              <label>Humidity (%)</label>
              <input
                type="number"
                value={humidityPercent}
                onChange={(e) => setHumidityPercent(e.target.value)}
                placeholder="e.g. 55"
                min="0"
                max="100"
                step="0.1"
                disabled={loading}
              />
              <small style={{ color: '#666', fontSize: '0.85em' }}>
                Optional: Relative humidity percentage
              </small>
            </div>

            <div className="form-group">
              <label>Light Hours</label>
              <input
                type="number"
                value={lightHours}
                onChange={(e) => setLightHours(e.target.value)}
                placeholder="e.g. 16"
                min="0"
                max="24"
                step="0.5"
                disabled={loading}
              />
              <small style={{ color: '#666', fontSize: '0.85em' }}>
                Optional: Hours of light received today
              </small>
            </div>

            {gardenId && gardens.find(g => g.id === parseInt(gardenId))?.is_hydroponic && (
              <>
                <div style={{ padding: '15px', backgroundColor: '#e3f2fd', borderRadius: '4px', marginBottom: '15px' }}>
                  <h3 style={{ margin: '0 0 10px 0', fontSize: '1.1em', color: '#1976d2' }}>Hydroponics Readings</h3>

                  <div className="form-group">
                    <label>pH Level</label>
                    <input
                      type="number"
                      value={phLevel}
                      onChange={(e) => setPhLevel(e.target.value)}
                      placeholder="e.g. 6.0"
                      min="0"
                      max="14"
                      step="0.1"
                      disabled={loading}
                    />
                    <small style={{ color: '#666', fontSize: '0.85em' }}>
                      Optional: pH level (0-14)
                    </small>
                  </div>

                  <div className="form-group">
                    <label>EC (mS/cm)</label>
                    <input
                      type="number"
                      value={ecMsCm}
                      onChange={(e) => setEcMsCm(e.target.value)}
                      placeholder="e.g. 1.5"
                      min="0"
                      step="0.1"
                      disabled={loading}
                    />
                    <small style={{ color: '#666', fontSize: '0.85em' }}>
                      Optional: Electrical Conductivity in mS/cm
                    </small>
                  </div>

                  <div className="form-group">
                    <label>PPM</label>
                    <input
                      type="number"
                      value={ppm}
                      onChange={(e) => setPpm(e.target.value)}
                      placeholder="e.g. 1000"
                      min="0"
                      disabled={loading}
                    />
                    <small style={{ color: '#666', fontSize: '0.85em' }}>
                      Optional: Parts Per Million
                    </small>
                  </div>

                  <div className="form-group">
                    <label>Water Temperature (F)</label>
                    <input
                      type="number"
                      value={waterTempF}
                      onChange={(e) => setWaterTempF(e.target.value)}
                      placeholder="e.g. 70"
                      min="-50"
                      max="150"
                      step="0.1"
                      disabled={loading}
                    />
                    <small style={{ color: '#666', fontSize: '0.85em' }}>
                      Optional: Water temperature in Fahrenheit
                    </small>
                  </div>
                </div>
              </>
            )}

            <div className="form-actions">
              <button type="button" onClick={onClose} className="btn btn-secondary" disabled={loading}>
                Cancel
              </button>
              <button type="submit" className="btn" disabled={loading}>
                {loading ? 'Saving...' : 'Add Reading'}
              </button>
            </div>
          </form>
        )}

        {gardens.length === 0 && (
          <div className="form-actions">
            <button type="button" onClick={onClose} className="btn">
              Close
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
