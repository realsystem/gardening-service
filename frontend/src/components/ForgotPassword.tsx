import { useState } from 'react';
import { api } from '../services/api';

interface ForgotPasswordProps {
  onBackToLogin: () => void;
}

export function ForgotPassword({ onBackToLogin }: ForgotPasswordProps) {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess(false);
    setLoading(true);

    try {
      const response = await api.requestPasswordReset(email);

      if (response.success) {
        setSuccess(true);
        setEmail(''); // Clear form
      } else {
        setError(response.message || 'Failed to send reset email');
      }
    } catch (err) {
      if (err instanceof Error && err.message.includes('429')) {
        setError('Too many reset requests. Please try again later.');
      } else {
        setError(err instanceof Error ? err.message : 'Failed to send reset email');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <h2>Forgot Password</h2>

      <p style={{ marginBottom: '20px', color: '#666' }}>
        Enter your email address and we'll send you a link to reset your password.
      </p>

      {success && (
        <div className="success" style={{ marginBottom: '20px', padding: '10px', backgroundColor: '#d4edda', color: '#155724', borderRadius: '4px' }}>
          Password reset email sent! Please check your email (or backend console in dev mode) for the reset link.
        </div>
      )}

      {error && <div className="error">{error}</div>}

      {!success && (
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Email Address</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              disabled={loading}
              placeholder="your@email.com"
            />
          </div>

          <button
            type="submit"
            className="btn"
            disabled={loading}
            style={{ width: '100%', marginBottom: '10px' }}
          >
            {loading ? 'Sending...' : 'Send Reset Link'}
          </button>
        </form>
      )}

      <p style={{ marginTop: '20px', textAlign: 'center' }}>
        <button
          className="btn-link"
          onClick={onBackToLogin}
          disabled={loading}
          style={{ background: 'none', border: 'none', color: '#007bff', cursor: 'pointer', textDecoration: 'underline' }}
        >
          Back to Login
        </button>
      </p>
    </div>
  );
}
