import { useState, useEffect } from 'react';
import { api } from '../services/api';

interface ResetPasswordProps {
  token: string | null;
  onSuccess: () => void;
  onBackToLogin: () => void;
}

export function ResetPassword({ token, onSuccess, onBackToLogin }: ResetPasswordProps) {
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');
  const [requirements, setRequirements] = useState<string[]>([]);
  const [showRequirements, setShowRequirements] = useState(false);

  useEffect(() => {
    // Load password requirements
    const loadRequirements = async () => {
      try {
        const response = await api.getPasswordRequirements();
        setRequirements(response.requirements);
      } catch (err) {
        console.error('Failed to load password requirements:', err);
      }
    };

    loadRequirements();
  }, []);

  useEffect(() => {
    // Check if token is missing
    if (!token) {
      setError('Invalid or missing reset token. Please request a new password reset.');
    }
  }, [token]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess(false);

    // Validate passwords match
    if (newPassword !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (!token) {
      setError('Invalid or missing reset token');
      return;
    }

    setLoading(true);

    try {
      const response = await api.confirmPasswordReset(token, newPassword);

      if (response.success) {
        setSuccess(true);
        setNewPassword('');
        setConfirmPassword('');

        // Redirect to login after 2 seconds
        setTimeout(() => {
          onSuccess();
        }, 2000);
      } else {
        setError(response.message || 'Failed to reset password');
      }
    } catch (err) {
      if (err instanceof Error) {
        // Parse error message for better UX
        if (err.message.includes('expired')) {
          setError('This reset link has expired. Please request a new one.');
        } else if (err.message.includes('already been used')) {
          setError('This reset link has already been used. Please request a new one.');
        } else if (err.message.includes('invalid')) {
          setError('Invalid reset link. Please request a new one.');
        } else {
          setError(err.message);
        }
      } else {
        setError('Failed to reset password. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <h2>Reset Password</h2>

      {success && (
        <div className="success" style={{ marginBottom: '20px', padding: '10px', backgroundColor: '#d4edda', color: '#155724', borderRadius: '4px' }}>
          Password reset successful! Redirecting to login...
        </div>
      )}

      {error && <div className="error">{error}</div>}

      {!success && token && (
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>New Password</label>
            <input
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              required
              disabled={loading}
              placeholder="Enter new password"
              onFocus={() => setShowRequirements(true)}
            />
          </div>

          <div className="form-group">
            <label>Confirm New Password</label>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              disabled={loading}
              placeholder="Confirm new password"
            />
          </div>

          {showRequirements && requirements.length > 0 && (
            <div style={{
              marginBottom: '15px',
              padding: '10px',
              backgroundColor: '#f8f9fa',
              borderRadius: '4px',
              fontSize: '14px'
            }}>
              <strong>Password Requirements:</strong>
              <ul style={{ marginTop: '5px', marginBottom: '0', paddingLeft: '20px' }}>
                {requirements.map((req, index) => (
                  <li key={index} style={{ marginBottom: '3px' }}>{req}</li>
                ))}
              </ul>
            </div>
          )}

          <button
            type="submit"
            className="btn"
            disabled={loading}
            style={{ width: '100%', marginBottom: '10px' }}
          >
            {loading ? 'Resetting...' : 'Reset Password'}
          </button>
        </form>
      )}

      {!token && (
        <p style={{ marginTop: '20px', textAlign: 'center' }}>
          <button
            className="btn-link"
            onClick={onBackToLogin}
            style={{ background: 'none', border: 'none', color: '#007bff', cursor: 'pointer', textDecoration: 'underline' }}
          >
            Back to Login
          </button>
        </p>
      )}

      {success && (
        <p style={{ marginTop: '20px', textAlign: 'center' }}>
          <button
            className="btn-link"
            onClick={onSuccess}
            style={{ background: 'none', border: 'none', color: '#007bff', cursor: 'pointer', textDecoration: 'underline' }}
          >
            Go to Login
          </button>
        </p>
      )}
    </div>
  );
}
