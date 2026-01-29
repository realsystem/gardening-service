import { useState, useEffect } from 'react';
import { Auth } from './components/Auth';
import { Dashboard } from './components/Dashboard';
import { ForgotPassword } from './components/ForgotPassword';
import { ResetPassword } from './components/ResetPassword';
import { api } from './services/api';
import type { User } from './types';
import './App.css';

type AuthPage = 'login' | 'forgot-password' | 'reset-password';

function App() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [authPage, setAuthPage] = useState<AuthPage>('login');
  const [resetToken, setResetToken] = useState<string | null>(null);

  const handleLogin = async (token: string) => {
    api.setToken(token);
    try {
      const userData = await api.getCurrentUser();
      setUser(userData);
    } catch (err) {
      console.error('Failed to load user:', err);
      handleLogout();
    }
  };

  const handleLogout = () => {
    api.clearToken();
    setUser(null);
  };

  useEffect(() => {
    // Check URL for reset token
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');

    if (token) {
      setResetToken(token);
      setAuthPage('reset-password');
      // Clean URL without refreshing
      window.history.replaceState({}, '', window.location.pathname);
    }

    // On app load, just show login (no persistent auth)
    setLoading(false);
  }, []);

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  if (!user) {
    if (authPage === 'forgot-password') {
      return (
        <ForgotPassword
          onBackToLogin={() => setAuthPage('login')}
        />
      );
    }

    if (authPage === 'reset-password') {
      return (
        <ResetPassword
          token={resetToken}
          onSuccess={() => {
            setAuthPage('login');
            setResetToken(null);
          }}
          onBackToLogin={() => {
            setAuthPage('login');
            setResetToken(null);
          }}
        />
      );
    }

    return (
      <Auth
        onLogin={handleLogin}
        onForgotPassword={() => setAuthPage('forgot-password')}
      />
    );
  }

  return <Dashboard user={user} onLogout={handleLogout} />;
}

export default App;
