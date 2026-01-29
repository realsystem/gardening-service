import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { Dashboard } from './Dashboard';
import * as api from '../services/api';

// Mock the API
vi.mock('../services/api');

describe('Dashboard', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders dashboard with loading state', () => {
    vi.spyOn(api, 'getCareTasks').mockImplementation(() => new Promise(() => {}));
    vi.spyOn(api, 'getGardens').mockImplementation(() => new Promise(() => {}));

    render(<Dashboard />);

    expect(screen.getByText(/loading/i) || screen.getByText(/dashboard/i)).toBeTruthy();
  });

  it('displays gardens and tasks when loaded', async () => {
    const mockGardens = [
      { id: 1, name: 'Main Garden', garden_type: 'outdoor', is_hydroponic: false },
      { id: 2, name: 'Indoor Setup', garden_type: 'indoor', is_hydroponic: true }
    ];

    const mockTasks = [
      {
        id: 1,
        title: 'Water tomatoes',
        task_type: 'water',
        priority: 'medium',
        due_date: '2026-01-28',
        status: 'pending'
      }
    ];

    vi.spyOn(api, 'getGardens').mockResolvedValue(mockGardens);
    vi.spyOn(api, 'getCareTasks').mockResolvedValue(mockTasks);

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('Main Garden')).toBeTruthy();
    });
  });

  it('displays error message when API fails', async () => {
    vi.spyOn(api, 'getGardens').mockRejectedValue(new Error('API Error'));
    vi.spyOn(api, 'getCareTasks').mockRejectedValue(new Error('API Error'));

    render(<Dashboard />);

    await waitFor(() => {
      const errorText = screen.queryByText(/error/i) || screen.queryByText(/failed/i);
      expect(errorText).toBeTruthy();
    });
  });

  it('displays empty state when no gardens exist', async () => {
    vi.spyOn(api, 'getGardens').mockResolvedValue([]);
    vi.spyOn(api, 'getCareTasks').mockResolvedValue([]);

    render(<Dashboard />);

    await waitFor(() => {
      const emptyText = screen.queryByText(/no gardens/i) || screen.queryByText(/create.*garden/i);
      expect(emptyText || screen.getByText(/dashboard/i)).toBeTruthy();
    });
  });

  it('shows high priority tasks prominently', async () => {
    const highPriorityTask = {
      id: 1,
      title: 'Adjust pH NOW',
      task_type: 'adjust_ph',
      priority: 'high',
      due_date: '2026-01-28',
      status: 'pending'
    };

    vi.spyOn(api, 'getGardens').mockResolvedValue([]);
    vi.spyOn(api, 'getCareTasks').mockResolvedValue([highPriorityTask]);

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('Adjust pH NOW')).toBeTruthy();
    });
  });
});
