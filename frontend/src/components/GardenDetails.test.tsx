import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { GardenDetails } from './GardenDetails';
import * as api from '../services/api';

vi.mock('../services/api');

describe('GardenDetails', () => {
  const mockOnBack = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders garden details with stats', async () => {
    const mockDetails = {
      garden: {
        id: 1,
        name: 'Main Garden',
        description: 'My outdoor garden',
        garden_type: 'outdoor' as const,
        is_hydroponic: false,
      },
      plantings: [],
      tasks: [],
      stats: {
        total_plantings: 5,
        active_plantings: 4,
        total_tasks: 10,
        pending_tasks: 7,
        high_priority_tasks: 2,
        upcoming_harvests: 1,
      },
    };

    vi.spyOn(api, 'getGardenDetails').mockResolvedValue(mockDetails);

    render(<GardenDetails gardenId={1} onBack={mockOnBack} />);

    await waitFor(() => {
      expect(screen.getByText('Main Garden')).toBeTruthy();
      expect(screen.getByText('My outdoor garden')).toBeTruthy();
    });

    // Check stats are displayed
    expect(screen.getByText('5')).toBeTruthy(); // Total plantings
    expect(screen.getByText('4')).toBeTruthy(); // Active plantings
    expect(screen.getByText('7')).toBeTruthy(); // Pending tasks
  });

  it('displays plantings list', async () => {
    const mockDetails = {
      garden: {
        id: 1,
        name: 'Test Garden',
        garden_type: 'outdoor' as const,
        is_hydroponic: false,
      },
      plantings: [
        {
          id: 1,
          plant_variety_id: 1,
          plant_name: 'Tomato',
          variety_name: 'Beefsteak',
          planting_date: '2026-01-20',
          planting_method: 'direct_sow',
          plant_count: 6,
          location_in_garden: 'Bed 1',
          status: 'growing',
          expected_harvest_date: '2026-04-10',
        },
      ],
      tasks: [],
      stats: {
        total_plantings: 1,
        active_plantings: 1,
        total_tasks: 0,
        pending_tasks: 0,
        high_priority_tasks: 0,
        upcoming_harvests: 0,
      },
    };

    vi.spyOn(api, 'getGardenDetails').mockResolvedValue(mockDetails);

    render(<GardenDetails gardenId={1} onBack={mockOnBack} />);

    await waitFor(() => {
      expect(screen.getByText('Tomato - Beefsteak')).toBeTruthy();
      expect(screen.getByText(/bed 1/i)).toBeTruthy();
      expect(screen.getByText(/growing/i)).toBeTruthy();
    });
  });

  it('displays tasks list with priorities', async () => {
    const mockDetails = {
      garden: {
        id: 1,
        name: 'Test Garden',
        garden_type: 'outdoor' as const,
        is_hydroponic: false,
      },
      plantings: [],
      tasks: [
        {
          id: 1,
          title: 'Water tomatoes',
          task_type: 'water',
          priority: 'high',
          due_date: '2026-01-29',
          status: 'pending',
          planting_event_id: 1,
        },
        {
          id: 2,
          title: 'Fertilize plants',
          task_type: 'fertilize',
          priority: 'medium',
          due_date: '2026-02-01',
          status: 'pending',
          planting_event_id: 1,
        },
      ],
      stats: {
        total_plantings: 0,
        active_plantings: 0,
        total_tasks: 2,
        pending_tasks: 2,
        high_priority_tasks: 1,
        upcoming_harvests: 0,
      },
    };

    vi.spyOn(api, 'getGardenDetails').mockResolvedValue(mockDetails);

    render(<GardenDetails gardenId={1} onBack={mockOnBack} />);

    await waitFor(() => {
      expect(screen.getByText('Water tomatoes')).toBeTruthy();
      expect(screen.getByText('Fertilize plants')).toBeTruthy();
    });

    // Check priority badges
    const highPriorityBadges = screen.getAllByText('high');
    expect(highPriorityBadges.length).toBeGreaterThan(0);
  });

  it('displays hydroponic garden details', async () => {
    const mockDetails = {
      garden: {
        id: 1,
        name: 'Hydro Setup',
        garden_type: 'indoor' as const,
        is_hydroponic: true,
        hydro_system_type: 'nft' as const,
        reservoir_size_liters: 100,
        ph_min: 5.5,
        ph_max: 6.5,
        ec_min: 1.2,
        ec_max: 2.0,
      },
      plantings: [],
      tasks: [],
      stats: {
        total_plantings: 0,
        active_plantings: 0,
        total_tasks: 0,
        pending_tasks: 0,
        high_priority_tasks: 0,
        upcoming_harvests: 0,
      },
    };

    vi.spyOn(api, 'getGardenDetails').mockResolvedValue(mockDetails);

    render(<GardenDetails gardenId={1} onBack={mockOnBack} />);

    await waitFor(() => {
      expect(screen.getByText('Hydro Setup')).toBeTruthy();
      expect(screen.getByText(/nft/i)).toBeTruthy();
      expect(screen.getByText(/100l/i)).toBeTruthy();
    });
  });

  it('shows empty states for no plantings and tasks', async () => {
    const mockDetails = {
      garden: {
        id: 1,
        name: 'Empty Garden',
        garden_type: 'outdoor' as const,
        is_hydroponic: false,
      },
      plantings: [],
      tasks: [],
      stats: {
        total_plantings: 0,
        active_plantings: 0,
        total_tasks: 0,
        pending_tasks: 0,
        high_priority_tasks: 0,
        upcoming_harvests: 0,
      },
    };

    vi.spyOn(api, 'getGardenDetails').mockResolvedValue(mockDetails);

    render(<GardenDetails gardenId={1} onBack={mockOnBack} />);

    await waitFor(() => {
      expect(screen.getByText('Empty Garden')).toBeTruthy();
      expect(screen.getByText(/no plants in this garden yet/i)).toBeTruthy();
      expect(screen.getByText(/no tasks for this garden/i)).toBeTruthy();
    });
  });

  it('calls onBack when back button is clicked', async () => {
    const user = userEvent.setup();
    const mockDetails = {
      garden: {
        id: 1,
        name: 'Test Garden',
        garden_type: 'outdoor' as const,
        is_hydroponic: false,
      },
      plantings: [],
      tasks: [],
      stats: {
        total_plantings: 0,
        active_plantings: 0,
        total_tasks: 0,
        pending_tasks: 0,
        high_priority_tasks: 0,
        upcoming_harvests: 0,
      },
    };

    vi.spyOn(api, 'getGardenDetails').mockResolvedValue(mockDetails);

    render(<GardenDetails gardenId={1} onBack={mockOnBack} />);

    await waitFor(() => {
      expect(screen.getByText('Test Garden')).toBeTruthy();
    });

    const backButton = screen.getByRole('button', { name: /back to gardens/i });
    await user.click(backButton);

    expect(mockOnBack).toHaveBeenCalled();
  });

  it('displays error message on failure', async () => {
    vi.spyOn(api, 'getGardenDetails').mockRejectedValue(new Error('Failed to load details'));

    render(<GardenDetails gardenId={1} onBack={mockOnBack} />);

    await waitFor(() => {
      expect(screen.getByText(/failed to load/i)).toBeTruthy();
    });
  });
});
