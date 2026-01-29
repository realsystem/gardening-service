import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { GardenList } from './GardenList';
import * as api from '../services/api';

vi.mock('../services/api');

describe('GardenList', () => {
  const mockOnSelectGarden = vi.fn();
  const mockOnRefresh = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders list of gardens', async () => {
    const mockGardens = [
      {
        id: 1,
        name: 'Main Garden',
        description: 'Outdoor vegetable garden',
        garden_type: 'outdoor' as const,
        is_hydroponic: false,
      },
      {
        id: 2,
        name: 'Indoor Setup',
        description: 'Indoor growing',
        garden_type: 'indoor' as const,
        location: 'Basement',
        is_hydroponic: false,
      },
    ];

    vi.spyOn(api, 'getGardens').mockResolvedValue(mockGardens);

    render(<GardenList onSelectGarden={mockOnSelectGarden} onRefresh={mockOnRefresh} />);

    await waitFor(() => {
      expect(screen.getByText('Main Garden')).toBeTruthy();
      expect(screen.getByText('Indoor Setup')).toBeTruthy();
    });
  });

  it('displays garden type icons correctly', async () => {
    const mockGardens = [
      { id: 1, name: 'Outdoor', garden_type: 'outdoor' as const, is_hydroponic: false },
      { id: 2, name: 'Indoor', garden_type: 'indoor' as const, is_hydroponic: false },
      { id: 3, name: 'Hydro', garden_type: 'indoor' as const, is_hydroponic: true },
    ];

    vi.spyOn(api, 'getGardens').mockResolvedValue(mockGardens);

    render(<GardenList onSelectGarden={mockOnSelectGarden} />);

    await waitFor(() => {
      expect(screen.getByText('Outdoor')).toBeTruthy();
      expect(screen.getByText('Hydroponic')).toBeTruthy();
    });
  });

  it('shows empty state when no gardens', async () => {
    vi.spyOn(api, 'getGardens').mockResolvedValue([]);

    render(<GardenList onSelectGarden={mockOnSelectGarden} />);

    await waitFor(() => {
      expect(screen.getByText(/no gardens yet/i)).toBeTruthy();
    });
  });

  it('calls onSelectGarden when view details is clicked', async () => {
    const user = userEvent.setup();
    const mockGardens = [
      { id: 1, name: 'Test Garden', garden_type: 'outdoor' as const, is_hydroponic: false },
    ];

    vi.spyOn(api, 'getGardens').mockResolvedValue(mockGardens);

    render(<GardenList onSelectGarden={mockOnSelectGarden} />);

    await waitFor(() => {
      expect(screen.getByText('Test Garden')).toBeTruthy();
    });

    const viewButton = screen.getByRole('button', { name: /view details/i });
    await user.click(viewButton);

    expect(mockOnSelectGarden).toHaveBeenCalledWith(1);
  });

  it('shows delete confirmation modal', async () => {
    const user = userEvent.setup();
    const mockGardens = [
      { id: 1, name: 'Test Garden', garden_type: 'outdoor' as const, is_hydroponic: false },
    ];

    vi.spyOn(api, 'getGardens').mockResolvedValue(mockGardens);

    render(<GardenList onSelectGarden={mockOnSelectGarden} />);

    await waitFor(() => {
      expect(screen.getByText('Test Garden')).toBeTruthy();
    });

    const deleteButton = screen.getByRole('button', { name: /delete/i });
    await user.click(deleteButton);

    await waitFor(() => {
      expect(screen.getByText(/delete garden/i)).toBeTruthy();
      expect(screen.getByText(/permanently delete/i)).toBeTruthy();
    });
  });

  it('deletes garden when confirmed', async () => {
    const user = userEvent.setup();
    const mockGardens = [
      { id: 1, name: 'Test Garden', garden_type: 'outdoor' as const, is_hydroponic: false },
    ];

    vi.spyOn(api, 'getGardens').mockResolvedValue(mockGardens);
    vi.spyOn(api, 'deleteGarden').mockResolvedValue();

    render(<GardenList onSelectGarden={mockOnSelectGarden} onRefresh={mockOnRefresh} />);

    await waitFor(() => {
      expect(screen.getByText('Test Garden')).toBeTruthy();
    });

    // Click delete button
    const deleteButton = screen.getByRole('button', { name: /delete/i });
    await user.click(deleteButton);

    // Confirm deletion
    await waitFor(() => {
      expect(screen.getByText(/delete garden/i)).toBeTruthy();
    });

    const confirmButton = screen.getByRole('button', { name: /delete garden/i });
    await user.click(confirmButton);

    await waitFor(() => {
      expect(api.deleteGarden).toHaveBeenCalledWith(1);
      expect(mockOnRefresh).toHaveBeenCalled();
    });
  });

  it('cancels deletion when cancel is clicked', async () => {
    const user = userEvent.setup();
    const mockGardens = [
      { id: 1, name: 'Test Garden', garden_type: 'outdoor' as const, is_hydroponic: false },
    ];

    vi.spyOn(api, 'getGardens').mockResolvedValue(mockGardens);
    vi.spyOn(api, 'deleteGarden').mockResolvedValue();

    render(<GardenList onSelectGarden={mockOnSelectGarden} />);

    await waitFor(() => {
      expect(screen.getByText('Test Garden')).toBeTruthy();
    });

    // Click delete button
    const deleteButton = screen.getByRole('button', { name: /^delete$/i });
    await user.click(deleteButton);

    // Cancel deletion
    await waitFor(() => {
      expect(screen.getByText(/delete garden/i)).toBeTruthy();
    });

    const cancelButton = screen.getByRole('button', { name: /cancel/i });
    await user.click(cancelButton);

    // Modal should close
    await waitFor(() => {
      expect(screen.queryByText(/permanently delete/i)).toBeNull();
    });

    expect(api.deleteGarden).not.toHaveBeenCalled();
  });

  it('displays error message on failure', async () => {
    vi.spyOn(api, 'getGardens').mockRejectedValue(new Error('Failed to load'));

    render(<GardenList onSelectGarden={mockOnSelectGarden} />);

    await waitFor(() => {
      expect(screen.getByText(/failed to load/i)).toBeTruthy();
    });
  });
});
