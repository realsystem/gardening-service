import { useState } from 'react';
import { api } from '../services/api';
import type { User, PlantVariety } from '../types';
import './Onboarding.css';

interface OnboardingProps {
  user: User;
  onComplete: (updatedUser: User) => void;
}

type OnboardingStep = 'welcome' | 'garden' | 'plants' | 'complete';

export function Onboarding({ user, onComplete }: OnboardingProps) {
  const [step, setStep] = useState<OnboardingStep>('welcome');
  const [gardenName, setGardenName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [createdGardenId, setCreatedGardenId] = useState<number | null>(null);
  const [availablePlants, setAvailablePlants] = useState<PlantVariety[]>([]);
  const [selectedPlants, setSelectedPlants] = useState<number[]>([]);

  // Load popular plants for user's zone
  const loadPopularPlants = async () => {
    try {
      const plants = await api.getPlantVarieties();

      // Deduplicate by common_name - show only one variety per plant
      const seenNames = new Set<string>();
      const uniquePlants = plants.filter(plant => {
        if (seenNames.has(plant.common_name)) {
          return false;
        }
        seenNames.add(plant.common_name);
        return true;
      });

      // Show first 8 unique plants as "popular"
      setAvailablePlants(uniquePlants.slice(0, 8));
    } catch (err) {
      console.error('Failed to load plants:', err);
      // Non-critical error, continue anyway
    }
  };

  const handleCreateGarden = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // Create outdoor garden with minimal fields
      const garden = await api.createGarden({
        name: gardenName || 'My Garden',
        garden_type: 'outdoor',
      });

      setCreatedGardenId(garden.id);

      // Load plants for next step
      await loadPopularPlants();

      setStep('plants');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create garden');
    } finally {
      setLoading(false);
    }
  };

  const togglePlant = (plantId: number) => {
    setSelectedPlants(prev =>
      prev.includes(plantId)
        ? prev.filter(id => id !== plantId)
        : [...prev, plantId]
    );
  };

  const handleFinish = async () => {
    setLoading(true);
    setError('');

    try {
      // Create planting events for selected plants
      if (createdGardenId && selectedPlants.length > 0) {
        await Promise.all(
          selectedPlants.map(plantId =>
            api.createPlantingEvent({
              garden_id: createdGardenId,
              plant_variety_id: plantId,
              planting_date: new Date().toISOString().split('T')[0],
              planting_method: 'transplant',
              plant_count: 1,
            })
          )
        );
      }

      // Mark onboarding as complete
      const updatedUser = await api.completeOnboarding();

      setStep('complete');

      // Wait a moment then redirect to dashboard
      setTimeout(() => {
        onComplete(updatedUser);
      }, 1500);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to complete setup');
      setLoading(false);
    }
  };

  const handleSkipPlants = async () => {
    setLoading(true);
    try {
      const updatedUser = await api.completeOnboarding();
      setStep('complete');
      setTimeout(() => {
        onComplete(updatedUser);
      }, 1500);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to complete setup');
      setLoading(false);
    }
  };

  // Customize content based on user group
  const getWelcomeContent = () => {
    switch (user.user_group) {
      case 'farmer':
        return {
          title: 'Welcome to Garden Tracker for Farmers!',
          subtitle: "Let's set up your farm tracking in just 2 quick steps.",
        };
      case 'scientific_researcher':
        return {
          title: 'Welcome to Garden Tracker Research Edition!',
          subtitle: "Let's configure your experimental plots in just 2 quick steps.",
        };
      default: // amateur_gardener
        return {
          title: 'Welcome to Garden Tracker!',
          subtitle: "Let's get your garden set up in just 2 quick steps.",
        };
    }
  };

  const getGardenStepContent = () => {
    switch (user.user_group) {
      case 'farmer':
        return {
          title: 'Create your first growing area',
          subtitle: 'Give it a name - you can add more details later like acreage and crop rotations.',
          placeholder: 'North Field A',
          hint: 'For example: "North Field", "Greenhouse 1", "High Tunnel", etc.',
        };
      case 'scientific_researcher':
        return {
          title: 'Create your first experimental plot',
          subtitle: 'Give it a name - you can add detailed parameters and controls later.',
          placeholder: 'Plot A - Control Group',
          hint: 'For example: "Plot A", "Greenhouse Trial 1", "Field Experiment", etc.',
        };
      default: // amateur_gardener
        return {
          title: 'Create your first garden',
          subtitle: 'Give it a name - you can add more details later if you want.',
          placeholder: 'My Backyard Garden',
          hint: 'For example: "Backyard", "Front Yard", "Patio", etc.',
        };
    }
  };

  const getPlantStepContent = () => {
    switch (user.user_group) {
      case 'farmer':
        return {
          title: 'What crops are you growing?',
          subtitle: 'Select crops to track. You can add more later and track yields.',
        };
      case 'scientific_researcher':
        return {
          title: 'What species are you studying?',
          subtitle: 'Select plants for your research. You can add controls and variants later.',
        };
      default: // amateur_gardener
        return {
          title: 'What are you growing?',
          subtitle: 'Select plants to track. You can add more later.',
        };
    }
  };

  if (step === 'welcome') {
    const content = getWelcomeContent();
    return (
      <div className="onboarding-container">
        <div className="onboarding-card">
          <h1>{content.title}</h1>
          <p className="subtitle">
            {content.subtitle}
          </p>

          <div className="climate-info">
            {user.usda_zone && (
              <div className="zone-badge">
                <strong>Your Climate Zone:</strong> USDA {user.usda_zone}
              </div>
            )}
            {user.zip_code && (
              <div className="location">
                📍 {user.zip_code}
              </div>
            )}
          </div>

          <button
            className="btn btn-primary btn-large"
            onClick={() => setStep('garden')}
          >
            Get Started →
          </button>
        </div>
      </div>
    );
  }

  if (step === 'garden') {
    const content = getGardenStepContent();
    return (
      <div className="onboarding-container">
        <div className="onboarding-card">
          <div className="progress-indicator">
            <span className="step active">1</span>
            <span className="step">2</span>
          </div>

          <h2>{content.title}</h2>
          <p className="subtitle">
            {content.subtitle}
          </p>

          {error && <div className="error">{error}</div>}

          <form onSubmit={handleCreateGarden}>
            <div className="form-group">
              <label>
                {user.user_group === 'farmer' ? 'Growing Area Name' :
                 user.user_group === 'scientific_researcher' ? 'Plot Name' :
                 'Garden Name'}
              </label>
              <input
                type="text"
                value={gardenName}
                onChange={(e) => setGardenName(e.target.value)}
                placeholder={content.placeholder}
                disabled={loading}
                autoFocus
              />
              <small className="hint">
                {content.hint}
              </small>
            </div>

            <button
              type="submit"
              className="btn btn-primary btn-large"
              disabled={loading}
            >
              {loading ? 'Creating...' : 'Continue →'}
            </button>
          </form>
        </div>
      </div>
    );
  }

  if (step === 'plants') {
    const content = getPlantStepContent();
    return (
      <div className="onboarding-container">
        <div className="onboarding-card">
          <div className="progress-indicator">
            <span className="step completed">✓</span>
            <span className="step active">2</span>
          </div>

          <h2>{content.title}</h2>
          <p className="subtitle">
            {content.subtitle}
          </p>

          {error && <div className="error">{error}</div>}

          {availablePlants.length > 0 ? (
            <>
              <div className="plant-grid">
                {availablePlants.map(plant => (
                  <div
                    key={plant.id}
                    className={`plant-card ${selectedPlants.includes(plant.id) ? 'selected' : ''}`}
                    onClick={() => togglePlant(plant.id)}
                  >
                    {plant.photo_url && (
                      <img src={plant.photo_url} alt={plant.common_name} />
                    )}
                    <div className="plant-name">{plant.common_name}</div>
                    {selectedPlants.includes(plant.id) && (
                      <div className="checkmark">✓</div>
                    )}
                  </div>
                ))}
              </div>

              <div className="button-group">
                <button
                  className="btn btn-secondary"
                  onClick={handleSkipPlants}
                  disabled={loading}
                >
                  Skip
                </button>
                <button
                  className="btn btn-primary btn-large"
                  onClick={handleFinish}
                  disabled={loading || selectedPlants.length === 0}
                >
                  {loading ? 'Setting up...' : 'Get Started →'}
                </button>
              </div>
            </>
          ) : (
            <div className="loading">Loading plants...</div>
          )}
        </div>
      </div>
    );
  }

  if (step === 'complete') {
    return (
      <div className="onboarding-container">
        <div className="onboarding-card text-center">
          <div className="success-icon">✓</div>
          <h2>All set!</h2>
          <p className="subtitle">
            Taking you to your garden dashboard...
          </p>
        </div>
      </div>
    );
  }

  return null;
}
