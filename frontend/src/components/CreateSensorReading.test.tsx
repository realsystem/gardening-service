import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { CreateSensorReading } from './CreateSensorReading';
import * as api from '../services/api';

vi.mock('../services/api');

describe('CreateSensorReading', () => {
  const mockOnClose = vi.fn();
  const mockOnSuccess = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders sensor reading form', async () => {
    vi.spyOn(api, 'getGardens').mockResolvedValue([
      { id: 1, name: 'Indoor Garden', garden_type: 'indoor', is_hydroponic: false }
    ]);

    render(<CreateSensorReading onClose={mockOnClose} onSuccess={mockOnSuccess} />);

    await waitFor(() => {
      expect(screen.getByLabelText(/garden/i) || screen.getByText(/garden/i)).toBeTruthy();
    });
  });

  it('shows only indoor gardens in dropdown', async () => {
    const gardens = [
      { id: 1, name: 'Indoor Garden', garden_type: 'indoor', is_hydroponic: false },
      { id: 2, name: 'Outdoor Garden', garden_type: 'outdoor', is_hydroponic: false }
    ];

    vi.spyOn(api, 'getGardens').mockResolvedValue(gardens);

    render(<CreateSensorReading onClose={mockOnClose} onSuccess={mockOnSuccess} />);

    await waitFor(() => {
      expect(screen.getByText('Indoor Garden')).toBeTruthy();
      expect(screen.queryByText('Outdoor Garden')).toBeNull();
    });
  });

  it('shows hydroponics fields for hydroponic gardens', async () => {
    const user = userEvent.setup();
    const gardens = [
      { id: 1, name: 'Hydro Garden', garden_type: 'indoor', is_hydroponic: true }
    ];

    vi.spyOn(api, 'getGardens').mockResolvedValue(gardens);

    render(<CreateSensorReading onClose={mockOnClose} onSuccess={mockOnSuccess} />);

    await waitFor(async () => {
      const gardenSelect = screen.getByLabelText(/garden/i) as HTMLSelectElement;
      await user.selectOptions(gardenSelect, '1');
    });

    await waitFor(() => {
      expect(screen.getByLabelText(/ph/i) || screen.getByText(/ph level/i)).toBeTruthy();
      expect(screen.getByLabelText(/ec/i) || screen.getByText(/ec/i)).toBeTruthy();
    });
  });

  it('submits indoor sensor reading successfully', async () => {
    const user = userEvent.setup();
    const gardens = [
      { id: 1, name: 'Indoor Garden', garden_type: 'indoor', is_hydroponic: false }
    ];

    vi.spyOn(api, 'getGardens').mockResolvedValue(gardens);
    vi.spyOn(api, 'createSensorReading').mockResolvedValue({
      id: 1,
      garden_id: 1,
      reading_date: '2026-01-28',
      temperature_f: 72.0,
      humidity_percent: 55.0
    });

    render(<CreateSensorReading onClose={mockOnClose} onSuccess={mockOnSuccess} />);

    await waitFor(async () => {
      const gardenSelect = screen.getByLabelText(/garden/i) as HTMLSelectElement;
      await user.selectOptions(gardenSelect, '1');
    });

    const tempInput = screen.getByLabelText(/temperature/i);
    await user.type(tempInput, '72');

    const submitButton = screen.getByRole('button', { name: /add|submit/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(api.createSensorReading).toHaveBeenCalled();
      expect(mockOnSuccess).toHaveBeenCalled();
    });
  });

  it('submits hydroponic sensor reading with all fields', async () => {
    const user = userEvent.setup();
    const gardens = [
      { id: 1, name: 'Hydro Garden', garden_type: 'indoor', is_hydroponic: true }
    ];

    vi.spyOn(api, 'getGardens').mockResolvedValue(gardens);
    vi.spyOn(api, 'createSensorReading').mockResolvedValue({
      id: 1,
      garden_id: 1,
      reading_date: '2026-01-28',
      temperature_f: 72.0,
      ph_level: 6.0,
      ec_ms_cm: 1.5,
      ppm: 1050
    });

    render(<CreateSensorReading onClose={mockOnClose} onSuccess={mockOnSuccess} />);

    await waitFor(async () => {
      const gardenSelect = screen.getByLabelText(/garden/i) as HTMLSelectElement;
      await user.selectOptions(gardenSelect, '1');
    });

    const phInput = screen.getByLabelText(/ph/i);
    await user.type(phInput, '6.0');

    const submitButton = screen.getByRole('button', { name: /add|submit/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(api.createSensorReading).toHaveBeenCalledWith(
        expect.objectContaining({
          ph_level: 6.0
        })
      );
    });
  });

  it('shows warning when no indoor gardens exist', async () => {
    vi.spyOn(api, 'getGardens').mockResolvedValue([]);

    render(<CreateSensorReading onClose={mockOnClose} onSuccess={mockOnSuccess} />);

    await waitFor(() => {
      expect(screen.getByText(/no indoor gardens/i) || screen.getByText(/create.*indoor/i)).toBeTruthy();
    });
  });
});
