import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Auth } from './Auth';
import * as api from '../services/api';

vi.mock('../services/api');

describe('Auth', () => {
  const mockOnLogin = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it('renders login form by default', () => {
    render(<Auth onLogin={mockOnLogin} />);

    expect(screen.getByLabelText(/email/i)).toBeTruthy();
    expect(screen.getByLabelText(/password/i)).toBeTruthy();
    expect(screen.getByRole('button', { name: /log.*in/i })).toBeTruthy();
  });

  it('allows user to login successfully', async () => {
    const user = userEvent.setup();
    vi.spyOn(api, 'login').mockResolvedValue({
      access_token: 'test_token',
      token_type: 'bearer'
    });

    render(<Auth onLogin={mockOnLogin} />);

    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const loginButton = screen.getByRole('button', { name: /log.*in/i });

    await user.type(emailInput, 'test@example.com');
    await user.type(passwordInput, 'password123');
    await user.click(loginButton);

    await waitFor(() => {
      expect(api.login).toHaveBeenCalledWith('test@example.com', 'password123');
      expect(mockOnLogin).toHaveBeenCalled();
    });
  });

  it('displays error message on login failure', async () => {
    const user = userEvent.setup();
    vi.spyOn(api, 'login').mockRejectedValue(new Error('Invalid credentials'));

    render(<Auth onLogin={mockOnLogin} />);

    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const loginButton = screen.getByRole('button', { name: /log.*in/i });

    await user.type(emailInput, 'test@example.com');
    await user.type(passwordInput, 'wrongpassword');
    await user.click(loginButton);

    await waitFor(() => {
      expect(screen.getByText(/error|invalid|failed/i)).toBeTruthy();
    });
  });

  it('switches to registration form', async () => {
    const user = userEvent.setup();
    render(<Auth onLogin={mockOnLogin} />);

    const switchButton = screen.getByRole('button', { name: /register|sign up/i });
    await user.click(switchButton);

    await waitFor(() => {
      expect(screen.getByLabelText(/full name/i) || screen.getByLabelText(/name/i)).toBeTruthy();
    });
  });

  it('allows user to register successfully', async () => {
    const user = userEvent.setup();
    vi.spyOn(api, 'register').mockResolvedValue({
      id: 1,
      email: 'newuser@example.com',
      full_name: 'New User'
    });
    vi.spyOn(api, 'login').mockResolvedValue({
      access_token: 'test_token',
      token_type: 'bearer'
    });

    render(<Auth onLogin={mockOnLogin} />);

    // Switch to register
    const switchButton = screen.getByRole('button', { name: /register|sign up/i });
    await user.click(switchButton);

    await waitFor(() => {
      expect(screen.getByLabelText(/full name/i) || screen.getByLabelText(/name/i)).toBeTruthy();
    });

    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const nameInput = screen.getByLabelText(/full name/i) || screen.getByLabelText(/name/i);
    const registerButton = screen.getByRole('button', { name: /register|sign up/i });

    await user.type(emailInput, 'newuser@example.com');
    await user.type(passwordInput, 'password123');
    await user.type(nameInput, 'New User');
    await user.click(registerButton);

    await waitFor(() => {
      expect(api.register).toHaveBeenCalledWith('newuser@example.com', 'password123', 'New User');
    });
  });

  it('validates required fields', async () => {
    const user = userEvent.setup();
    render(<Auth onLogin={mockOnLogin} />);

    const loginButton = screen.getByRole('button', { name: /log.*in/i });
    await user.click(loginButton);

    // Should not call API without fields filled
    expect(api.login).not.toHaveBeenCalled();
  });
});
