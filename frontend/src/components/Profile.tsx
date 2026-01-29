import { useState } from 'react';
import { api } from '../services/api';
import type { User } from '../types';

interface ProfileProps {
  user: User;
  onUpdate: (user: User) => void;
  onClose: () => void;
}

export function Profile({ user, onUpdate, onClose }: ProfileProps) {
  const [displayName, setDisplayName] = useState(user.display_name || '');
  const [avatarUrl, setAvatarUrl] = useState(user.avatar_url || '');
  const [city, setCity] = useState(user.city || '');
  const [gardeningPreferences, setGardeningPreferences] = useState(user.gardening_preferences || '');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess(false);
    setLoading(true);

    try {
      const updatedUser = await api.updateProfile({
        display_name: displayName || undefined,
        avatar_url: avatarUrl || undefined,
        city: city || undefined,
        gardening_preferences: gardeningPreferences || undefined,
      });
      onUpdate(updatedUser);
      setSuccess(true);
      setTimeout(() => {
        onClose();
      }, 1500);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h2>Edit Profile</h2>

        {error && <div className="error">{error}</div>}
        {success && <div style={{ padding: '10px', backgroundColor: '#d4edda', color: '#155724', borderRadius: '4px', marginBottom: '15px' }}>
          Profile updated successfully!
        </div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Display Name</label>
            <input
              type="text"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              placeholder="Your name"
              disabled={loading}
              maxLength={100}
            />
          </div>

          <div className="form-group">
            <label>Avatar URL</label>
            <input
              type="url"
              value={avatarUrl}
              onChange={(e) => setAvatarUrl(e.target.value)}
              placeholder="https://example.com/avatar.jpg"
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label>City</label>
            <input
              type="text"
              value={city}
              onChange={(e) => setCity(e.target.value)}
              placeholder="Your city"
              disabled={loading}
              maxLength={100}
            />
          </div>

          <div className="form-group">
            <label>Gardening Preferences</label>
            <textarea
              value={gardeningPreferences}
              onChange={(e) => setGardeningPreferences(e.target.value)}
              placeholder="E.g., organic only, container gardening, native plants"
              disabled={loading}
              rows={4}
            />
            <small style={{ color: '#666', fontSize: '0.85em' }}>
              Share your gardening style, preferences, or goals
            </small>
          </div>

          <div style={{ marginBottom: '15px', padding: '10px', backgroundColor: '#f0f0f0', borderRadius: '4px' }}>
            <div style={{ fontSize: '0.9em', color: '#666' }}>
              <strong>Current Info:</strong>
            </div>
            <div style={{ fontSize: '0.85em', color: '#666', marginTop: '5px' }}>
              Email: {user.email}<br />
              {user.usda_zone && `Climate Zone: ${user.usda_zone}`}
              {user.zip_code && ` (ZIP: ${user.zip_code})`}
            </div>
          </div>

          <div className="form-actions">
            <button type="button" onClick={onClose} className="btn btn-secondary" disabled={loading}>
              Cancel
            </button>
            <button type="submit" className="btn" disabled={loading}>
              {loading ? 'Saving...' : 'Save Profile'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
