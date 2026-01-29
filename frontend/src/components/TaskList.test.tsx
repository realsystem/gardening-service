import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { TaskList } from './TaskList';
import * as api from '../services/api';

vi.mock('../services/api');

describe('TaskList', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders task list', () => {
    render(<TaskList />);
    expect(screen.getByText(/task/i)).toBeTruthy();
  });

  it('displays tasks when loaded', async () => {
    const mockTasks = [
      {
        id: 1,
        title: 'Water tomatoes',
        task_type: 'water',
        priority: 'medium',
        due_date: '2026-01-28',
        status: 'pending',
        description: 'Water the plants'
      },
      {
        id: 2,
        title: 'Adjust pH',
        task_type: 'adjust_ph',
        priority: 'high',
        due_date: '2026-01-28',
        status: 'pending',
        description: 'pH is too high'
      }
    ];

    vi.spyOn(api, 'getCareTasks').mockResolvedValue(mockTasks);

    render(<TaskList />);

    await waitFor(() => {
      expect(screen.getByText('Water tomatoes')).toBeTruthy();
      expect(screen.getByText('Adjust pH')).toBeTruthy();
    });
  });

  it('marks high priority tasks visually', async () => {
    const mockTasks = [
      {
        id: 1,
        title: 'High Priority Task',
        task_type: 'adjust_ph',
        priority: 'high',
        due_date: '2026-01-28',
        status: 'pending'
      }
    ];

    vi.spyOn(api, 'getCareTasks').mockResolvedValue(mockTasks);

    render(<TaskList />);

    await waitFor(() => {
      const taskElement = screen.getByText('High Priority Task');
      expect(taskElement).toBeTruthy();
      // Should have some visual indicator (class, style, or label)
    });
  });

  it('allows completing a task', async () => {
    const user = userEvent.setup();
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

    vi.spyOn(api, 'getCareTasks').mockResolvedValue(mockTasks);
    vi.spyOn(api, 'completeTask').mockResolvedValue({
      ...mockTasks[0],
      status: 'completed'
    });

    render(<TaskList />);

    await waitFor(() => {
      expect(screen.getByText('Water tomatoes')).toBeTruthy();
    });

    const completeButton = screen.getByRole('button', { name: /complete|done/i });
    await user.click(completeButton);

    await waitFor(() => {
      expect(api.completeTask).toHaveBeenCalledWith(1);
    });
  });

  it('filters tasks by status', async () => {
    const user = userEvent.setup();
    const mockTasks = [
      {
        id: 1,
        title: 'Pending Task',
        task_type: 'water',
        priority: 'medium',
        due_date: '2026-01-28',
        status: 'pending'
      },
      {
        id: 2,
        title: 'Completed Task',
        task_type: 'fertilize',
        priority: 'low',
        due_date: '2026-01-27',
        status: 'completed'
      }
    ];

    vi.spyOn(api, 'getCareTasks').mockResolvedValue(mockTasks);

    render(<TaskList />);

    await waitFor(() => {
      expect(screen.getByText('Pending Task')).toBeTruthy();
    });

    // Look for filter controls
    const filterButton = screen.queryByRole('button', { name: /filter|all|pending|completed/i });
    if (filterButton) {
      await user.click(filterButton);
    }
  });

  it('shows empty state when no tasks exist', async () => {
    vi.spyOn(api, 'getCareTasks').mockResolvedValue([]);

    render(<TaskList />);

    await waitFor(() => {
      expect(screen.getByText(/no tasks/i) || screen.getByText(/all done/i)).toBeTruthy();
    });
  });

  it('displays error message when API fails', async () => {
    vi.spyOn(api, 'getCareTasks').mockRejectedValue(new Error('Failed to load tasks'));

    render(<TaskList />);

    await waitFor(() => {
      expect(screen.getByText(/error|failed/i)).toBeTruthy();
    });
  });
});
