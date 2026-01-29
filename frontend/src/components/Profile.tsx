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
  const [activeTab, setActiveTab] = useState<'profile' | 'security'>('profile');

  // Password change state
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [passwordSuccess, setPasswordSuccess] = useState('');
  const [passwordLoading, setPasswordLoading] = useState(false);
  const [resetEmailSuccess, setResetEmailSuccess] = useState('');

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

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setPasswordError('');
    setPasswordSuccess('');

    // Validate passwords match
    if (newPassword !== confirmPassword) {
      setPasswordError('New passwords do not match');
      return;
    }

    // Validate password length
    if (newPassword.length < 8) {
      setPasswordError('Password must be at least 8 characters');
      return;
    }

    setPasswordLoading(true);

    try {
      await api.changePassword(currentPassword, newPassword);
      setPasswordSuccess('Password changed successfully!');
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
      setTimeout(() => {
        setPasswordSuccess('');
      }, 5000);
    } catch (err) {
      setPasswordError(err instanceof Error ? err.message : 'Failed to change password');
    } finally {
      setPasswordLoading(false);
    }
  };

  const handleRequestResetEmail = async () => {
    setPasswordError('');
    setResetEmailSuccess('');
    setPasswordLoading(true);

    try {
      await api.requestPasswordResetAuthenticated();
      setResetEmailSuccess('Password reset link sent to your email. Check your inbox (or backend logs in dev mode).');
      setTimeout(() => {
        setResetEmailSuccess('');
      }, 10000);
    } catch (err) {
      setPasswordError(err instanceof Error ? err.message : 'Failed to send reset email');
    } finally {
      setPasswordLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h2>Profile Settings</h2>

        {/* Tabs */}
        <div style={{ display: 'flex', borderBottom: '2px solid #ddd', marginBottom: '20px' }}>
          <button
            onClick={() => setActiveTab('profile')}
            style={{
              flex: 1,
              padding: '10px',
              border: 'none',
              background: activeTab === 'profile' ? '#4CAF50' : 'transparent',
              color: activeTab === 'profile' ? 'white' : '#666',
              fontWeight: activeTab === 'profile' ? 'bold' : 'normal',
              cursor: 'pointer',
              borderRadius: '4px 4px 0 0',
            }}
          >
            Profile
          </button>
          <button
            onClick={() => setActiveTab('security')}
            style={{
              flex: 1,
              padding: '10px',
              border: 'none',
              background: activeTab === 'security' ? '#4CAF50' : 'transparent',
              color: activeTab === 'security' ? 'white' : '#666',
              fontWeight: activeTab === 'security' ? 'bold' : 'normal',
              cursor: 'pointer',
              borderRadius: '4px 4px 0 0',
            }}
          >
            Security
          </button>
        </div>

        {/* Profile Tab */}
        {activeTab === 'profile' && (
          <>
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
          </>
        )}

        {/* Security Tab */}
        {activeTab === 'security' && (
          <>
            <div style={{ marginBottom: '30px' }}>
              <h3 style={{ marginBottom: '15px', fontSize: '1.1em' }}>Change Password</h3>
              <p style={{ color: '#666', fontSize: '0.9em', marginBottom: '15px' }}>
                Update your password by providing your current password and a new one.
              </p>

              {passwordError && <div className="error" style={{ marginBottom: '15px' }}>{passwordError}</div>}
              {passwordSuccess && <div style={{ padding: '10px', backgroundColor: '#d4edda', color: '#155724', borderRadius: '4px', marginBottom: '15px' }}>
                {passwordSuccess}
              </div>}

              <form onSubmit={handleChangePassword}>
                <div className="form-group">
                  <label>Current Password</label>
                  <input
                    type="password"
                    value={currentPassword}
                    onChange={(e) => setCurrentPassword(e.target.value)}
                    required
                    disabled={passwordLoading}
                    minLength={1}
                  />
                </div>

                <div className="form-group">
                  <label>New Password</label>
                  <input
                    type="password"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    required
                    disabled={passwordLoading}
                    minLength={8}
                  />
                  <small style={{ color: '#666', fontSize: '0.85em' }}>
                    At least 8 characters, including uppercase, lowercase, number, and special character
                  </small>
                </div>

                <div className="form-group">
                  <label>Confirm New Password</label>
                  <input
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    required
                    disabled={passwordLoading}
                    minLength={8}
                  />
                </div>

                <button type="submit" className="btn" disabled={passwordLoading} style={{ width: '100%' }}>
                  {passwordLoading ? 'Changing...' : 'Change Password'}
                </button>
              </form>
            </div>

            <div style={{ borderTop: '1px solid #ddd', paddingTop: '20px' }}>
              <h3 style={{ marginBottom: '15px', fontSize: '1.1em' }}>Reset Password via Email</h3>
              <p style={{ color: '#666', fontSize: '0.9em', marginBottom: '15px' }}>
                Prefer to reset your password via email? We'll send you a secure reset link to <strong>{user.email}</strong>.
              </p>

              {resetEmailSuccess && <div style={{ padding: '10px', backgroundColor: '#d4edda', color: '#155724', borderRadius: '4px', marginBottom: '15px' }}>
                {resetEmailSuccess}
              </div>}

              <button
                onClick={handleRequestResetEmail}
                className="btn btn-secondary"
                disabled={passwordLoading}
                style={{ width: '100%' }}
              >
                {passwordLoading ? 'Sending...' : 'Send Password Reset Email'}
              </button>
            </div>

            <div className="form-actions" style={{ marginTop: '20px' }}>
              <button type="button" onClick={onClose} className="btn btn-secondary">
                Close
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
