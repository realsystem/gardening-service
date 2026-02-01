import { useState, useRef, useEffect } from 'react';
import { api } from '../services/api';
import type { LandWithGardens, Garden, GardenSpatialInfo, Tree } from '../types';
import './LandCanvas.css';

interface LandCanvasProps {
  land: LandWithGardens;
  gardens: Garden[];
  trees?: Tree[];
  onUpdate: () => void;
}

interface DragState {
  gardenId: number;
  offsetX: number;
  offsetY: number;
  initialX: number;
  initialY: number;
  currentX?: number;
  currentY?: number;
}

// Grid configuration
const GRID_SIZE = 50; // 50px per unit (for visualization)
const GRID_RESOLUTION = 0.1; // 0.1 units per grid cell (10× finer than 1 unit)
const GRID_CELLS_PER_UNIT = 10; // Number of minor grid cells per major unit

// Snap helper function
const snapToGrid = (value: number, resolution: number): number => {
  return Math.round(value / resolution) * resolution;
};

export function LandCanvas({ land, gardens, trees = [], onUpdate }: LandCanvasProps) {
  const [dragState, setDragState] = useState<DragState | null>(null);
  const [selectedGarden, setSelectedGarden] = useState<number | null>(null);
  const [errorMessage, setErrorMessage] = useState<string>('');
  const [placingGarden, setPlacingGarden] = useState<number | null>(null);
  const [snapEnabled, setSnapEnabled] = useState<boolean>(true); // Snap enabled by default
  const [altKeyPressed, setAltKeyPressed] = useState<boolean>(false); // Track Alt key
  const canvasRef = useRef<HTMLDivElement>(null);

  // Calculate canvas dimensions
  const canvasWidth = land.width * GRID_SIZE;
  const canvasHeight = land.height * GRID_SIZE;

  // Get unplaced gardens (not on this land)
  const unplacedGardens = gardens.filter(g => !g.land_id || g.land_id !== land.id);

  const handleMouseDown = (e: React.MouseEvent, garden: GardenSpatialInfo) => {
    if (garden.x == null || garden.y == null) return;

    const rect = canvasRef.current?.getBoundingClientRect();
    if (!rect) return;

    const offsetX = e.clientX - rect.left - garden.x * GRID_SIZE;
    const offsetY = e.clientY - rect.top - garden.y * GRID_SIZE;

    setDragState({
      gardenId: garden.id,
      offsetX,
      offsetY,
      initialX: garden.x,
      initialY: garden.y,
    });
    setSelectedGarden(garden.id);
    setErrorMessage('');
  };

  const handleMouseMove = (e: MouseEvent) => {
    if (!dragState || !canvasRef.current) return;

    const garden = land.gardens.find(g => g.id === dragState.gardenId);
    if (!garden || garden.width == null || garden.height == null) return;

    const rect = canvasRef.current.getBoundingClientRect();
    let x = (e.clientX - rect.left - dragState.offsetX) / GRID_SIZE;
    let y = (e.clientY - rect.top - dragState.offsetY) / GRID_SIZE;

    // Constrain to land boundaries
    x = Math.max(0, Math.min(x, land.width - garden.width));
    y = Math.max(0, Math.min(y, land.height - garden.height));

    // Update drag state to trigger re-render with current position
    setDragState({
      ...dragState,
      currentX: x,
      currentY: y,
    });
  };

  const handleMouseUp = async (e: MouseEvent) => {
    if (!dragState || !canvasRef.current) return;

    const garden = land.gardens.find(g => g.id === dragState.gardenId);
    if (!garden || garden.width == null || garden.height == null) {
      setDragState(null);
      return;
    }

    const rect = canvasRef.current.getBoundingClientRect();
    let newX = (e.clientX - rect.left - dragState.offsetX) / GRID_SIZE;
    let newY = (e.clientY - rect.top - dragState.offsetY) / GRID_SIZE;

    // Constrain to land boundaries
    newX = Math.max(0, Math.min(newX, land.width - garden.width));
    newY = Math.max(0, Math.min(newY, land.height - garden.height));

    // Apply snap-to-grid if enabled and Alt key not pressed
    const shouldSnap = snapEnabled && !altKeyPressed;
    const snappedX = shouldSnap ? snapToGrid(newX, GRID_RESOLUTION) : newX;
    const snappedY = shouldSnap ? snapToGrid(newY, GRID_RESOLUTION) : newY;

    try {
      await api.updateGardenLayout(dragState.gardenId, {
        land_id: land.id,
        x: snappedX,
        y: snappedY,
        width: garden.width,
        height: garden.height,
        snap_to_grid: shouldSnap,
      });
      // Update local state optimistically
      garden.x = snappedX;
      garden.y = snappedY;
      setErrorMessage('');
      // Don't reload - position is already updated locally
    } catch (error) {
      // Revert to original position on error
      garden.x = dragState.initialX;
      garden.y = dragState.initialY;
      setErrorMessage((error as Error).message || 'Failed to update garden position');
    } finally {
      setDragState(null);
    }
  };

  useEffect(() => {
    if (dragState) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
      return () => {
        window.removeEventListener('mousemove', handleMouseMove);
        window.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [dragState]);

  // Keyboard event listeners for Alt key (temporary snap disable)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.altKey) {
        setAltKeyPressed(true);
      }
    };

    const handleKeyUp = (e: KeyboardEvent) => {
      if (!e.altKey) {
        setAltKeyPressed(false);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('keyup', handleKeyUp);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('keyup', handleKeyUp);
    };
  }, []);

  const handlePlaceGarden = async (garden: Garden) => {
    // Prevent double-click placement
    if (placingGarden) {
      console.log('Placement already in progress, ignoring click');
      return;
    }

    console.log('Placing garden:', {
      id: garden.id,
      name: garden.name,
      landId: land.id,
      landName: land.name
    });
    setPlacingGarden(garden.id);

    // Place in center with default size
    let defaultWidth = 2;
    let defaultHeight = 2;
    let centerX = Math.max(0, (land.width - defaultWidth) / 2);
    let centerY = Math.max(0, (land.height - defaultHeight) / 2);

    // Apply snap if enabled
    if (snapEnabled) {
      centerX = snapToGrid(centerX, GRID_RESOLUTION);
      centerY = snapToGrid(centerY, GRID_RESOLUTION);
      defaultWidth = snapToGrid(defaultWidth, GRID_RESOLUTION);
      defaultHeight = snapToGrid(defaultHeight, GRID_RESOLUTION);
    }

    console.log('Position:', { centerX, centerY, defaultWidth, defaultHeight });

    try {
      console.log('Calling API with:', {
        gardenId: garden.id,
        payload: {
          land_id: land.id,
          x: centerX,
          y: centerY,
          width: defaultWidth,
          height: defaultHeight,
          snap_to_grid: snapEnabled,
        }
      });
      const result = await api.updateGardenLayout(garden.id, {
        land_id: land.id,
        x: centerX,
        y: centerY,
        width: defaultWidth,
        height: defaultHeight,
        snap_to_grid: snapEnabled,
      });
      console.log('Garden placed successfully:', result);
      setErrorMessage('');
      await onUpdate();
    } catch (error) {
      console.error('Failed to place garden - full error:', error);
      console.error('Error type:', error instanceof Error ? 'Error' : typeof error);
      console.error('Error message:', error instanceof Error ? error.message : String(error));
      const errorMessage = error instanceof Error ? error.message : 'Failed to place garden';
      setErrorMessage(errorMessage);
    } finally {
      setPlacingGarden(null);
    }
  };

  const handleRemoveGarden = async (gardenId: number) => {
    try {
      await api.updateGardenLayout(gardenId, {
        land_id: undefined,
        x: undefined,
        y: undefined,
        width: undefined,
        height: undefined,
      });
      setErrorMessage('');
      setSelectedGarden(null);
      onUpdate();
    } catch (error) {
      setErrorMessage((error as Error).message || 'Failed to remove garden');
    }
  };

  return (
    <div className="land-canvas-container">
      <div className="land-header">
        <h3>{land.name}</h3>
        <p className="land-dimensions">
          {land.width} × {land.height} units
        </p>
      </div>

      {errorMessage && (
        <div className="error-message">{errorMessage}</div>
      )}

      {/* Grid controls */}
      <div style={{ padding: '10px', backgroundColor: '#f9f9f9', borderRadius: '4px', marginBottom: '10px' }}>
        <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer', fontSize: '0.9em' }}>
          <input
            type="checkbox"
            checked={snapEnabled}
            onChange={(e) => setSnapEnabled(e.target.checked)}
            style={{ marginRight: '8px', cursor: 'pointer' }}
          />
          <span>Snap to grid (0.1 unit precision)</span>
        </label>
        <p style={{ margin: '5px 0 0 24px', fontSize: '0.8em', color: '#666' }}>
          Hold Alt key to temporarily disable snapping while dragging
        </p>
      </div>

      <div className="canvas-wrapper">
        <div
          ref={canvasRef}
          className="land-canvas"
          style={{
            width: `${canvasWidth}px`,
            height: `${canvasHeight}px`,
          }}
        >
          {/* Grid lines - Minor and Major */}
          <svg className="grid-overlay" width={canvasWidth} height={canvasHeight}>
            <defs>
              {/* Minor grid (0.1 unit cells) - subtle */}
              <pattern
                id="minor-grid"
                width={GRID_SIZE / GRID_CELLS_PER_UNIT}
                height={GRID_SIZE / GRID_CELLS_PER_UNIT}
                patternUnits="userSpaceOnUse"
              >
                <path
                  d={`M ${GRID_SIZE / GRID_CELLS_PER_UNIT} 0 L 0 0 0 ${GRID_SIZE / GRID_CELLS_PER_UNIT}`}
                  fill="none"
                  stroke="#f0f0f0"
                  strokeWidth="0.5"
                />
              </pattern>
              {/* Major grid (1 unit cells) - more visible */}
              <pattern
                id="major-grid"
                width={GRID_SIZE}
                height={GRID_SIZE}
                patternUnits="userSpaceOnUse"
              >
                <path
                  d={`M ${GRID_SIZE} 0 L 0 0 0 ${GRID_SIZE}`}
                  fill="none"
                  stroke="#d0d0d0"
                  strokeWidth="1"
                />
              </pattern>
            </defs>
            {/* Render both grids */}
            <rect width="100%" height="100%" fill="url(#minor-grid)" />
            <rect width="100%" height="100%" fill="url(#major-grid)" />
          </svg>

          {/* Trees (render first, so they appear behind gardens) */}
          {trees.map((tree) => {
            const canopyDiameter = tree.canopy_radius * 2 * GRID_SIZE;
            const centerX = tree.x * GRID_SIZE;
            const centerY = tree.y * GRID_SIZE;

            return (
              <div key={`tree-${tree.id}`} className="tree-canopy-group">
                {/* Tree canopy (shade area) */}
                <div
                  className="tree-canopy"
                  style={{
                    left: `${centerX - tree.canopy_radius * GRID_SIZE}px`,
                    top: `${centerY - tree.canopy_radius * GRID_SIZE}px`,
                    width: `${canopyDiameter}px`,
                    height: `${canopyDiameter}px`,
                  }}
                  title={`${tree.name} (canopy: ${tree.canopy_radius} units)`}
                >
                  <span className="tree-label">{tree.name}</span>
                </div>
                {/* Tree trunk marker */}
                <div
                  className="tree-trunk"
                  style={{
                    left: `${centerX - 6}px`,
                    top: `${centerY - 6}px`,
                  }}
                />
              </div>
            );
          })}

          {/* Placed gardens */}
          {land.gardens.map((garden) => {
            if (garden.x == null || garden.y == null || garden.width == null || garden.height == null) return null;

            // Use drag position if this garden is being dragged
            const isDragging = dragState?.gardenId === garden.id;
            const displayX = isDragging && dragState.currentX !== undefined ? dragState.currentX : garden.x;
            const displayY = isDragging && dragState.currentY !== undefined ? dragState.currentY : garden.y;

            return (
              <div
                key={garden.id}
                className={`garden-plot ${selectedGarden === garden.id ? 'selected' : ''} ${isDragging ? 'dragging' : ''}`}
                style={{
                  left: `${displayX * GRID_SIZE}px`,
                  top: `${displayY * GRID_SIZE}px`,
                  width: `${garden.width * GRID_SIZE}px`,
                  height: `${garden.height * GRID_SIZE}px`,
                }}
                onMouseDown={(e) => handleMouseDown(e, garden)}
                onClick={() => setSelectedGarden(garden.id)}
              >
                <span className="garden-label">{garden.name}</span>
                {selectedGarden === garden.id && (
                  <button
                    className="remove-button"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleRemoveGarden(garden.id);
                    }}
                  >
                    ×
                  </button>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Unplaced gardens */}
      {unplacedGardens.length > 0 && (
        <div className="unplaced-gardens">
          <h4>Available Gardens</h4>
          <p className="help-text">Click to place on land</p>
          <div className="garden-chips">
            {unplacedGardens.map((garden) => (
              <button
                key={garden.id}
                className="garden-chip"
                onClick={() => handlePlaceGarden(garden)}
                disabled={placingGarden === garden.id}
              >
                {placingGarden === garden.id ? 'Placing...' : garden.name}
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="canvas-legend">
        <p><strong>Instructions:</strong></p>
        <ul>
          <li>Click unplaced gardens to add them to the land</li>
          <li>Drag gardens to reposition them</li>
          <li>Click × to remove a garden from the land</li>
          <li>Gardens cannot overlap</li>
          <li>Grid: Minor lines = 0.1 units, Major lines = 1 unit</li>
        </ul>
      </div>
    </div>
  );
}
