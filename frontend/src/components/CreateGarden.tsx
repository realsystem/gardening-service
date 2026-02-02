import { useState } from 'react';
import { api } from '../services/api';
import type { User } from '../types';

interface CreateGardenProps {
  user: User;
  onClose: () => void;
  onSuccess: () => void;
}

export function CreateGarden({ user, onClose, onSuccess }: CreateGardenProps) {
  // Check if user has access to advanced features
  const isResearcher = user.user_group === 'scientific_researcher';
  const canUseHydroponics = user.feature_flags?.hydroponics || false;
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [gardenType, setGardenType] = useState<'outdoor' | 'indoor'>('outdoor');
  const [location, setLocation] = useState('');
  const [lightSourceType, setLightSourceType] = useState<'led' | 'fluorescent' | 'natural_supplement' | 'hps' | 'mh'>('led');
  const [lightHoursPerDay, setLightHoursPerDay] = useState('');
  const [tempMinF, setTempMinF] = useState('');
  const [tempMaxF, setTempMaxF] = useState('');
  const [humidityMinPercent, setHumidityMinPercent] = useState('');
  const [humidityMaxPercent, setHumidityMaxPercent] = useState('');
  const [containerType, setContainerType] = useState('');
  const [growMedium, setGrowMedium] = useState('');
  const [isHydroponic, setIsHydroponic] = useState(false);
  const [hydroSystemType, setHydroSystemType] = useState<'nft' | 'dwc' | 'ebb_flow' | 'aeroponics' | 'drip' | 'wick'>('dwc');
  const [reservoirSizeLiters, setReservoirSizeLiters] = useState('');
  const [nutrientSchedule, setNutrientSchedule] = useState('');
  const [phMin, setPhMin] = useState('');
  const [phMax, setPhMax] = useState('');
  const [ecMin, setEcMin] = useState('');
  const [ecMax, setEcMax] = useState('');
  const [ppmMin, setPpmMin] = useState('');
  const [ppmMax, setPpmMax] = useState('');
  const [waterTempMinF, setWaterTempMinF] = useState('');
  const [waterTempMaxF, setWaterTempMaxF] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await api.createGarden({
        name,
        description: description || undefined,
        garden_type: gardenType,
        location: location || undefined,
        light_source_type: gardenType === 'indoor' && lightSourceType ? lightSourceType : undefined,
        light_hours_per_day: gardenType === 'indoor' && lightHoursPerDay ? parseFloat(lightHoursPerDay) : undefined,
        temp_min_f: gardenType === 'indoor' && tempMinF ? parseFloat(tempMinF) : undefined,
        temp_max_f: gardenType === 'indoor' && tempMaxF ? parseFloat(tempMaxF) : undefined,
        humidity_min_percent: gardenType === 'indoor' && humidityMinPercent ? parseFloat(humidityMinPercent) : undefined,
        humidity_max_percent: gardenType === 'indoor' && humidityMaxPercent ? parseFloat(humidityMaxPercent) : undefined,
        container_type: gardenType === 'indoor' && containerType ? containerType : undefined,
        grow_medium: gardenType === 'indoor' && growMedium ? growMedium : undefined,
        is_hydroponic: isHydroponic,
        hydro_system_type: isHydroponic && hydroSystemType ? hydroSystemType : undefined,
        reservoir_size_liters: isHydroponic && reservoirSizeLiters ? parseFloat(reservoirSizeLiters) : undefined,
        nutrient_schedule: isHydroponic && nutrientSchedule ? nutrientSchedule : undefined,
        ph_min: isHydroponic && phMin ? parseFloat(phMin) : undefined,
        ph_max: isHydroponic && phMax ? parseFloat(phMax) : undefined,
        ec_min: isHydroponic && ecMin ? parseFloat(ecMin) : undefined,
        ec_max: isHydroponic && ecMax ? parseFloat(ecMax) : undefined,
        ppm_min: isHydroponic && ppmMin ? parseInt(ppmMin) : undefined,
        ppm_max: isHydroponic && ppmMax ? parseInt(ppmMax) : undefined,
        water_temp_min_f: isHydroponic && waterTempMinF ? parseFloat(waterTempMinF) : undefined,
        water_temp_max_f: isHydroponic && waterTempMaxF ? parseFloat(waterTempMaxF) : undefined,
      });
      onSuccess();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create garden');
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h2>Create Garden</h2>

        {error && <div className="error">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Garden Name *</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. My Backyard Garden"
              required
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label>Description</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Optional description"
              disabled={loading}
              rows={2}
            />
          </div>

          {/* Amateur users: Simple form with outdoor only */}
          {!isResearcher ? (
            <div className="form-group">
              <small className="hint" style={{ color: '#999', fontSize: '0.9em' }}>
                Creating outdoor garden. More options available with Scientific Researcher account.
              </small>
            </div>
          ) : (
            /* Researchers: Full form with indoor/hydroponic */
            <div className="form-group">
              <label>Garden Type *</label>
              <select
                value={gardenType}
                onChange={(e) => setGardenType(e.target.value as 'outdoor' | 'indoor')}
                required
                disabled={loading}
              >
                <option value="outdoor">Outdoor Garden</option>
                <option value="indoor">Indoor Garden</option>
              </select>
            </div>
          )}

          {isResearcher && gardenType === 'indoor' && (
            <>
              <div className="form-group">
                <label>Location</label>
                <input
                  type="text"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  placeholder="e.g. Basement, Spare Room"
                  disabled={loading}
                />
              </div>

              <div className="form-group">
                <label>Light Source Type</label>
                <select
                  value={lightSourceType}
                  onChange={(e) => setLightSourceType(e.target.value as typeof lightSourceType)}
                  disabled={loading}
                >
                  <option value="led">LED</option>
                  <option value="fluorescent">Fluorescent</option>
                  <option value="natural_supplement">Natural + Supplement</option>
                  <option value="hps">HPS (High-Pressure Sodium)</option>
                  <option value="mh">MH (Metal Halide)</option>
                </select>
              </div>

              <div className="form-group">
                <label>Light Hours Per Day</label>
                <input
                  type="number"
                  value={lightHoursPerDay}
                  onChange={(e) => setLightHoursPerDay(e.target.value)}
                  placeholder="e.g. 16"
                  min="0"
                  max="24"
                  step="0.5"
                  disabled={loading}
                />
                <small style={{ color: '#666', fontSize: '0.85em' }}>
                  Hours of light per day (0-24)
                </small>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                <div className="form-group">
                  <label>Min Temperature (F)</label>
                  <input
                    type="number"
                    value={tempMinF}
                    onChange={(e) => setTempMinF(e.target.value)}
                    placeholder="e.g. 65"
                    disabled={loading}
                  />
                </div>

                <div className="form-group">
                  <label>Max Temperature (F)</label>
                  <input
                    type="number"
                    value={tempMaxF}
                    onChange={(e) => setTempMaxF(e.target.value)}
                    placeholder="e.g. 75"
                    disabled={loading}
                  />
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                <div className="form-group">
                  <label>Min Humidity (%)</label>
                  <input
                    type="number"
                    value={humidityMinPercent}
                    onChange={(e) => setHumidityMinPercent(e.target.value)}
                    placeholder="e.g. 40"
                    min="0"
                    max="100"
                    disabled={loading}
                  />
                </div>

                <div className="form-group">
                  <label>Max Humidity (%)</label>
                  <input
                    type="number"
                    value={humidityMaxPercent}
                    onChange={(e) => setHumidityMaxPercent(e.target.value)}
                    placeholder="e.g. 60"
                    min="0"
                    max="100"
                    disabled={loading}
                  />
                </div>
              </div>

              <div className="form-group">
                <label>Container Type</label>
                <input
                  type="text"
                  value={containerType}
                  onChange={(e) => setContainerType(e.target.value)}
                  placeholder="e.g. 5-gallon pots, grow bags"
                  disabled={loading}
                />
              </div>

              <div className="form-group">
                <label>Grow Medium</label>
                <input
                  type="text"
                  value={growMedium}
                  onChange={(e) => setGrowMedium(e.target.value)}
                  placeholder="e.g. coco coir, hydroponics"
                  disabled={loading}
                />
              </div>

              <div className="form-group" style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <input
                  type="checkbox"
                  id="isHydroponic"
                  checked={isHydroponic}
                  onChange={(e) => setIsHydroponic(e.target.checked)}
                  disabled={loading}
                />
                <label htmlFor="isHydroponic" style={{ margin: 0, fontWeight: 'bold' }}>
                  This is a hydroponic garden
                </label>
              </div>

              {isHydroponic && (
                <>
                  <div style={{ padding: '15px', backgroundColor: '#e3f2fd', borderRadius: '4px', marginBottom: '15px' }}>
                    <h3 style={{ margin: '0 0 10px 0', fontSize: '1.1em', color: '#1976d2' }}>Hydroponics Setup</h3>

                    <div className="form-group">
                      <label>System Type *</label>
                      <select
                        value={hydroSystemType}
                        onChange={(e) => setHydroSystemType(e.target.value as typeof hydroSystemType)}
                        disabled={loading}
                      >
                        <option value="dwc">Deep Water Culture (DWC)</option>
                        <option value="nft">Nutrient Film Technique (NFT)</option>
                        <option value="ebb_flow">Ebb and Flow</option>
                        <option value="aeroponics">Aeroponics</option>
                        <option value="drip">Drip System</option>
                        <option value="wick">Wick System</option>
                      </select>
                    </div>

                    <div className="form-group">
                      <label>Reservoir Size (liters)</label>
                      <input
                        type="number"
                        value={reservoirSizeLiters}
                        onChange={(e) => setReservoirSizeLiters(e.target.value)}
                        placeholder="e.g. 50"
                        min="0"
                        disabled={loading}
                      />
                    </div>

                    <div className="form-group">
                      <label>Nutrient Schedule / Notes</label>
                      <textarea
                        value={nutrientSchedule}
                        onChange={(e) => setNutrientSchedule(e.target.value)}
                        placeholder="e.g. General Hydroponics Flora series, 1/4 strength for seedlings"
                        disabled={loading}
                        rows={3}
                      />
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                      <div className="form-group">
                        <label>Min pH</label>
                        <input
                          type="number"
                          value={phMin}
                          onChange={(e) => setPhMin(e.target.value)}
                          placeholder="e.g. 5.5"
                          min="0"
                          max="14"
                          step="0.1"
                          disabled={loading}
                        />
                      </div>

                      <div className="form-group">
                        <label>Max pH</label>
                        <input
                          type="number"
                          value={phMax}
                          onChange={(e) => setPhMax(e.target.value)}
                          placeholder="e.g. 6.5"
                          min="0"
                          max="14"
                          step="0.1"
                          disabled={loading}
                        />
                      </div>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                      <div className="form-group">
                        <label>Min EC (mS/cm)</label>
                        <input
                          type="number"
                          value={ecMin}
                          onChange={(e) => setEcMin(e.target.value)}
                          placeholder="e.g. 1.2"
                          min="0"
                          step="0.1"
                          disabled={loading}
                        />
                      </div>

                      <div className="form-group">
                        <label>Max EC (mS/cm)</label>
                        <input
                          type="number"
                          value={ecMax}
                          onChange={(e) => setEcMax(e.target.value)}
                          placeholder="e.g. 2.0"
                          min="0"
                          step="0.1"
                          disabled={loading}
                        />
                      </div>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                      <div className="form-group">
                        <label>Min PPM</label>
                        <input
                          type="number"
                          value={ppmMin}
                          onChange={(e) => setPpmMin(e.target.value)}
                          placeholder="e.g. 800"
                          min="0"
                          disabled={loading}
                        />
                      </div>

                      <div className="form-group">
                        <label>Max PPM</label>
                        <input
                          type="number"
                          value={ppmMax}
                          onChange={(e) => setPpmMax(e.target.value)}
                          placeholder="e.g. 1400"
                          min="0"
                          disabled={loading}
                        />
                      </div>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                      <div className="form-group">
                        <label>Min Water Temp (F)</label>
                        <input
                          type="number"
                          value={waterTempMinF}
                          onChange={(e) => setWaterTempMinF(e.target.value)}
                          placeholder="e.g. 65"
                          disabled={loading}
                        />
                      </div>

                      <div className="form-group">
                        <label>Max Water Temp (F)</label>
                        <input
                          type="number"
                          value={waterTempMaxF}
                          onChange={(e) => setWaterTempMaxF(e.target.value)}
                          placeholder="e.g. 75"
                          disabled={loading}
                        />
                      </div>
                    </div>
                  </div>
                </>
              )}
            </>
          )}

          <div className="form-actions">
            <button type="button" onClick={onClose} className="btn btn-secondary" disabled={loading}>
              Cancel
            </button>
            <button type="submit" className="btn" disabled={loading}>
              {loading ? 'Creating...' : 'Create Garden'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
