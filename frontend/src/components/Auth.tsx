import { useState } from 'react';
import { api } from '../services/api';

interface AuthProps {
  onLogin: (token: string) => void;
  onForgotPassword?: () => void;
}

export function Auth({ onLogin, onForgotPassword }: AuthProps) {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [zipCode, setZipCode] = useState('');
  const [userGroup, setUserGroup] = useState('amateur_gardener');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (isLogin) {
        const response = await api.login(email, password);
        onLogin(response.access_token);
      } else {
        await api.register(email, password, zipCode, userGroup);
        const response = await api.login(email, password);
        onLogin(response.access_token);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <h2>{isLogin ? 'Login' : 'Register'}</h2>

      {error && (
        <div className="error">
          {error}
          {isLogin && onForgotPassword && (
            <div style={{ marginTop: '10px' }}>
              <button
                type="button"
                className="btn-link"
                onClick={onForgotPassword}
                style={{ fontSize: '14px', background: 'none', border: 'none', color: '#007bff', cursor: 'pointer', textDecoration: 'underline', fontWeight: 'bold' }}
              >
                Forgot your password? Click here to reset it
              </button>
            </div>
          )}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            disabled={loading}
          />
        </div>

        <div className="form-group">
          <label>Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            disabled={loading}
          />
          {isLogin && onForgotPassword && (
            <div style={{ textAlign: 'right', marginTop: '5px' }}>
              <button
                type="button"
                className="btn-link"
                onClick={onForgotPassword}
                disabled={loading}
                style={{ fontSize: '14px', background: 'none', border: 'none', color: '#007bff', cursor: 'pointer', textDecoration: 'underline' }}
              >
                Forgot password?
              </button>
            </div>
          )}
        </div>

        {!isLogin && (
          <>
            <div className="form-group">
              <label>ZIP Code</label>
              <input
                type="text"
                value={zipCode}
                onChange={(e) => setZipCode(e.target.value)}
                required
                disabled={loading}
                placeholder="e.g. 94102"
              />
            </div>

            <div className="form-group">
              <label>I am a...</label>
              <select
                value={userGroup}
                onChange={(e) => setUserGroup(e.target.value)}
                disabled={loading}
              >
                <option value="amateur_gardener">Amateur Gardener (Home Gardening)</option>
                <option value="farmer">Farmer (Commercial Growing)</option>
                <option value="scientific_researcher">Scientific Researcher (Full Features)</option>
              </select>
              <div style={{ fontSize: '0.85em', color: '#666', marginTop: '5px' }}>
                This determines which features you'll see in the app.
              </div>
            </div>
          </>
        )}

        <button type="submit" className="btn" disabled={loading} style={{ width: '100%' }}>
          {loading ? 'Loading...' : isLogin ? 'Login' : 'Register'}
        </button>
      </form>

      <p style={{ marginTop: '20px', textAlign: 'center' }}>
        {isLogin ? "Don't have an account? " : 'Already have an account? '}
        <button
          className="btn-link"
          onClick={() => setIsLogin(!isLogin)}
          disabled={loading}
        >
          {isLogin ? 'Register' : 'Login'}
        </button>
      </p>
    </div>
  );
}
