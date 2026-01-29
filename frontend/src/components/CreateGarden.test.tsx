import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { CreateGarden } from './CreateGarden';
import * as api from '../services/api';

vi.mock('../services/api');

describe('CreateGarden', () => {
  const mockOnClose = vi.fn();
  const mockOnSuccess = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders create garden form', () => {
    render(<CreateGarden onClose={mockOnClose} onSuccess={mockOnSuccess} />);

    expect(screen.getByLabelText(/name/i)).toBeTruthy();
    expect(screen.getByText(/cancel/i)).toBeTruthy();
  });

  it('allows creating an outdoor garden', async () => {
    const user = userEvent.setup();
    vi.spyOn(api, 'createGarden').mockResolvedValue({
      id: 1,
      name: 'Test Garden',
      garden_type: 'outdoor',
      is_hydroponic: false
    });

    render(<CreateGarden onClose={mockOnClose} onSuccess={mockOnSuccess} />);

    const nameInput = screen.getByLabelText(/name/i);
    await user.type(nameInput, 'Test Garden');

    const submitButton = screen.getByRole('button', { name: /add|create/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(api.createGarden).toHaveBeenCalled();
      expect(mockOnSuccess).toHaveBeenCalled();
    });
  });

  it('shows indoor garden fields when indoor type selected', async () => {
    const user = userEvent.setup();
    render(<CreateGarden onClose={mockOnClose} onSuccess={mockOnSuccess} />);

    // Select indoor type
    const gardenTypeSelect = screen.getByLabelText(/type/i) as HTMLSelectElement;
    await user.selectOptions(gardenTypeSelect, 'indoor');

    await waitFor(() => {
      expect(screen.getByLabelText(/location/i)).toBeTruthy();
      expect(screen.getByLabelText(/light source/i)).toBeTruthy();
    });
  });

  it('shows hydroponics fields when hydroponic checkbox is checked', async () => {
    const user = userEvent.setup();
    render(<CreateGarden onClose={mockOnClose} onSuccess={mockOnSuccess} />);

    // First select indoor
    const gardenTypeSelect = screen.getByLabelText(/type/i) as HTMLSelectElement;
    await user.selectOptions(gardenTypeSelect, 'indoor');

    // Then check hydroponic
    const hydroCheckbox = screen.getByLabelText(/hydroponic/i);
    await user.click(hydroCheckbox);

    await waitFor(() => {
      expect(screen.getByLabelText(/system type/i) || screen.getByLabelText(/hydro/i)).toBeTruthy();
      expect(screen.getByLabelText(/ph min/i) || screen.getByText(/ph/i)).toBeTruthy();
    });
  });

  it('validates required fields', async () => {
    const user = userEvent.setup();
    render(<CreateGarden onClose={mockOnClose} onSuccess={mockOnSuccess} />);

    const submitButton = screen.getByRole('button', { name: /add|create/i });
    await user.click(submitButton);

    // Should not call API without required fields
    expect(api.createGarden).not.toHaveBeenCalled();
  });

  it('displays error message when API fails', async () => {
    const user = userEvent.setup();
    vi.spyOn(api, 'createGarden').mockRejectedValue(new Error('Failed to create garden'));

    render(<CreateGarden onClose={mockOnClose} onSuccess={mockOnSuccess} />);

    const nameInput = screen.getByLabelText(/name/i);
    await user.type(nameInput, 'Test Garden');

    const submitButton = screen.getByRole('button', { name: /add|create/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/failed|error/i)).toBeTruthy();
    });
  });

  it('closes modal when cancel is clicked', async () => {
    const user = userEvent.setup();
    render(<CreateGarden onClose={mockOnClose} onSuccess={mockOnSuccess} />);

    const cancelButton = screen.getByRole('button', { name: /cancel/i });
    await user.click(cancelButton);

    expect(mockOnClose).toHaveBeenCalled();
  });
});
