import { useState, useRef, useEffect } from 'react';
import { api } from '../services/api';
import type { LandWithGardens, Garden, GardenSpatialInfo, Tree, TreeShadowExtent, GardenSunExposure } from '../types';
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
  const [showSeasonalShadows, setShowSeasonalShadows] = useState<boolean>(false);
  const [selectedSeason, setSelectedSeason] = useState<'winter' | 'equinox' | 'summer'>('summer');
  const [gardenSunExposure, setGardenSunExposure] = useState<Map<number, GardenSunExposure>>(new Map());
  const [treeShadows, setTreeShadows] = useState<Map<number, TreeShadowExtent>>(new Map());
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

  // Fetch sun exposure data for gardens and trees
  useEffect(() => {
    const fetchSunExposureData = async () => {
      // Fetch garden sun exposure
      const gardenExposureMap = new Map<number, GardenSunExposure>();
      for (const garden of land.gardens) {
        if (garden.x != null && garden.y != null) {
          try {
            const exposure = await api.getGardenSunExposure(garden.id);
            gardenExposureMap.set(garden.id, exposure);
          } catch (error) {
            console.error(`Failed to fetch sun exposure for garden ${garden.id}:`, error);
          }
        }
      }
      setGardenSunExposure(gardenExposureMap);

      // Fetch tree shadow extents (default latitude 40.0 for temperate zone)
      const treeShadowMap = new Map<number, TreeShadowExtent>();
      for (const tree of trees) {
        if (tree.x != null && tree.y != null && tree.height != null) {
          try {
            const shadowExtent = await api.getTreeShadowExtent(tree.id, 40.0);
            treeShadowMap.set(tree.id, shadowExtent);
          } catch (error) {
            console.error(`Failed to fetch shadow extent for tree ${tree.id}:`, error);
          }
        }
      }
      setTreeShadows(treeShadowMap);
    };

    if (showSeasonalShadows) {
      fetchSunExposureData();
    }
  }, [land.gardens, trees, showSeasonalShadows]);

  const findFreePosition = (width: number, height: number): { x: number; y: number } | null => {
    const tolerance = 0.01; // Small tolerance for floating-point precision

    // Helper to check if a position overlaps with any existing garden
    const checkOverlap = (x: number, y: number, w: number, h: number): boolean => {
      for (const g of land.gardens) {
        if (g.x == null || g.y == null || g.width == null || g.height == null) continue;

        // AABB overlap detection with tolerance for floating-point precision
        const noOverlap = (
          x + w <= g.x + tolerance ||
          g.x + g.width <= x + tolerance ||
          y + h <= g.y + tolerance ||
          g.y + g.height <= y + tolerance
        );

        if (!noOverlap) return true; // Overlap found
      }
      return false; // No overlap
    };

    // Use grid resolution for snapping, ensuring positions align with backend
    const stepSize = GRID_RESOLUTION;

    // Try positions from top-left, moving right then down
    for (let y = 0; y <= land.height - height; y += stepSize) {
      for (let x = 0; x <= land.width - width; x += stepSize) {
        // Snap position to grid to ensure exact alignment
        const snappedX = snapToGrid(x, GRID_RESOLUTION);
        const snappedY = snapToGrid(y, GRID_RESOLUTION);

        if (!checkOverlap(snappedX, snappedY, width, height)) {
          return { x: snappedX, y: snappedY };
        }
      }
    }

    // No free space found
    return null;
  };

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

    // Default size
    let defaultWidth = 2;
    let defaultHeight = 2;

    // Apply snap to default size if enabled
    if (snapEnabled) {
      defaultWidth = snapToGrid(defaultWidth, GRID_RESOLUTION);
      defaultHeight = snapToGrid(defaultHeight, GRID_RESOLUTION);
    }

    // Find first available position starting from top-left
    const position = findFreePosition(defaultWidth, defaultHeight);

    if (!position) {
      setErrorMessage('No space available on this land for a new garden');
      setPlacingGarden(null);
      return;
    }

    let { x: posX, y: posY } = position;

    console.log('Position:', { posX, posY, defaultWidth, defaultHeight });

    try {
      console.log('Calling API with:', {
        gardenId: garden.id,
        payload: {
          land_id: land.id,
          x: posX,
          y: posY,
          width: defaultWidth,
          height: defaultHeight,
          snap_to_grid: snapEnabled,
        }
      });
      const result = await api.updateGardenLayout(garden.id, {
        land_id: land.id,
        x: posX,
        y: posY,
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

      {/* Seasonal shadow controls */}
      <div style={{ padding: '10px', backgroundColor: '#fff3cd', borderRadius: '4px', marginBottom: '10px', border: '1px solid #ffc107' }}>
        <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer', fontSize: '0.9em', marginBottom: '8px' }}>
          <input
            type="checkbox"
            checked={showSeasonalShadows}
            onChange={(e) => setShowSeasonalShadows(e.target.checked)}
            style={{ marginRight: '8px', cursor: 'pointer' }}
          />
          <span><strong>Show Seasonal Shadows</strong></span>
        </label>
        {showSeasonalShadows && (
          <div style={{ marginLeft: '24px' }}>
            <label style={{ display: 'block', fontSize: '0.85em', marginBottom: '4px', color: '#666' }}>
              Season:
            </label>
            <select
              value={selectedSeason}
              onChange={(e) => setSelectedSeason(e.target.value as 'winter' | 'equinox' | 'summer')}
              style={{
                padding: '4px 8px',
                borderRadius: '3px',
                border: '1px solid #ccc',
                fontSize: '0.85em',
                cursor: 'pointer'
              }}
            >
              <option value="winter">Winter (Longest shadows)</option>
              <option value="equinox">Equinox (Medium shadows)</option>
              <option value="summer">Summer (Shortest shadows)</option>
            </select>
            <p style={{ margin: '6px 0 0 0', fontSize: '0.75em', color: '#856404' }}>
              Shadow projection based on sun altitude at solar noon
            </p>
          </div>
        )}
      </div>

      <div className="canvas-wrapper">
        <div
          ref={canvasRef}
          className="land-canvas"
          style={{
            width: `${canvasWidth}px`,
            height: `${canvasHeight}px`,
            position: 'relative',
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

            // Get sun exposure data for color-coding
            const exposure = gardenSunExposure.get(garden.id);
            let backgroundColor = '';
            let borderColor = '';
            if (showSeasonalShadows && exposure?.exposure_category) {
              if (exposure.exposure_category === 'Full Sun') {
                backgroundColor = 'rgba(144, 238, 144, 0.6)'; // Light green
                borderColor = 'rgba(34, 139, 34, 0.8)'; // Forest green
              } else if (exposure.exposure_category === 'Partial Sun') {
                backgroundColor = 'rgba(255, 223, 128, 0.6)'; // Light yellow-orange
                borderColor = 'rgba(255, 165, 0, 0.8)'; // Orange
              } else if (exposure.exposure_category === 'Shade') {
                backgroundColor = 'rgba(200, 200, 200, 0.6)'; // Light gray
                borderColor = 'rgba(128, 128, 128, 0.8)'; // Gray
              }
            }

            return (
              <div
                key={garden.id}
                className={`garden-plot ${selectedGarden === garden.id ? 'selected' : ''} ${isDragging ? 'dragging' : ''}`}
                style={{
                  left: `${displayX * GRID_SIZE}px`,
                  top: `${displayY * GRID_SIZE}px`,
                  width: `${garden.width * GRID_SIZE}px`,
                  height: `${garden.height * GRID_SIZE}px`,
                  ...(backgroundColor && { backgroundColor }),
                  ...(borderColor && { borderColor }),
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

          {/* Seasonal shadows overlay (on top of gardens) */}
          {showSeasonalShadows && treeShadows.size > 0 && (
            <div className="shadow-overlay">
              <svg
                width={canvasWidth}
                height={canvasHeight}
                style={{ display: 'block' }}
              >
                {Array.from(treeShadows.entries()).map(([treeId, shadowExtent]) => {
                  if (!shadowExtent.seasonal_shadows) return null;
                  const shadowRect = shadowExtent.seasonal_shadows[selectedSeason];
                  if (!shadowRect) return null;

                  return (
                    <rect
                      key={`shadow-${treeId}-${selectedSeason}`}
                      x={shadowRect.x * GRID_SIZE}
                      y={shadowRect.y * GRID_SIZE}
                      width={shadowRect.width * GRID_SIZE}
                      height={shadowRect.height * GRID_SIZE}
                      fill="rgba(100, 100, 150, 0.3)"
                      stroke="rgba(100, 100, 150, 0.6)"
                      strokeWidth="1"
                      strokeDasharray="4 2"
                    >
                      <title>{`Shadow from tree ${treeId} in ${selectedSeason}`}</title>
                    </rect>
                  );
                })}
              </svg>
            </div>
          )}
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

      {/* Sun Exposure Details Panel */}
      {showSeasonalShadows && selectedGarden && (() => {
        const selectedGardenData = land.gardens.find(g => g.id === selectedGarden);
        const exposure = gardenSunExposure.get(selectedGarden);

        if (!selectedGardenData || !exposure) return null;

        return (
          <div style={{
            padding: '12px',
            backgroundColor: '#f0f8ff',
            borderRadius: '6px',
            marginBottom: '10px',
            border: '1px solid #4682b4'
          }}>
            <h4 style={{ margin: '0 0 10px 0', color: '#2c5282', fontSize: '1em' }}>
              ☀️ Sun Exposure: {selectedGardenData.name}
            </h4>

            {exposure.seasonal_exposure_score !== null && (
              <div style={{ marginBottom: '8px' }}>
                <strong>Overall Exposure Score:</strong> {(exposure.seasonal_exposure_score * 100).toFixed(0)}%
                <div style={{
                  width: '100%',
                  height: '8px',
                  backgroundColor: '#e0e0e0',
                  borderRadius: '4px',
                  marginTop: '4px',
                  overflow: 'hidden'
                }}>
                  <div style={{
                    width: `${exposure.seasonal_exposure_score * 100}%`,
                    height: '100%',
                    backgroundColor: exposure.exposure_category === 'Full Sun' ? '#4caf50' :
                                   exposure.exposure_category === 'Partial Sun' ? '#ffa726' : '#9e9e9e',
                    transition: 'width 0.3s ease'
                  }} />
                </div>
              </div>
            )}

            {exposure.exposure_category && (
              <div style={{ marginBottom: '8px' }}>
                <strong>Category:</strong>{' '}
                <span style={{
                  padding: '2px 8px',
                  borderRadius: '3px',
                  backgroundColor: exposure.exposure_category === 'Full Sun' ? '#c8e6c9' :
                                 exposure.exposure_category === 'Partial Sun' ? '#ffe0b2' : '#e0e0e0',
                  color: exposure.exposure_category === 'Full Sun' ? '#2e7d32' :
                         exposure.exposure_category === 'Partial Sun' ? '#e65100' : '#616161',
                  fontWeight: 'bold',
                  fontSize: '0.85em'
                }}>
                  {exposure.exposure_category}
                </span>
              </div>
            )}

            {exposure.seasonal_shading && (
              <div style={{ marginBottom: '8px' }}>
                <strong>Seasonal Shading:</strong>
                <table style={{ width: '100%', marginTop: '6px', fontSize: '0.85em', borderCollapse: 'collapse' }}>
                  <thead>
                    <tr style={{ backgroundColor: '#e3f2fd' }}>
                      <th style={{ padding: '4px 8px', textAlign: 'left', borderBottom: '1px solid #90caf9' }}>Season</th>
                      <th style={{ padding: '4px 8px', textAlign: 'right', borderBottom: '1px solid #90caf9' }}>Shaded</th>
                      <th style={{ padding: '4px 8px', textAlign: 'left', borderBottom: '1px solid #90caf9' }}>Category</th>
                    </tr>
                  </thead>
                  <tbody>
                    {exposure.seasonal_shading.winter && (
                      <tr>
                        <td style={{ padding: '4px 8px', borderBottom: '1px solid #e0e0e0' }}>Winter</td>
                        <td style={{ padding: '4px 8px', textAlign: 'right', borderBottom: '1px solid #e0e0e0' }}>
                          {exposure.seasonal_shading.winter.shaded_percentage.toFixed(0)}%
                        </td>
                        <td style={{ padding: '4px 8px', borderBottom: '1px solid #e0e0e0', fontSize: '0.8em' }}>
                          {exposure.seasonal_shading.winter.exposure_category}
                        </td>
                      </tr>
                    )}
                    {exposure.seasonal_shading.equinox && (
                      <tr>
                        <td style={{ padding: '4px 8px', borderBottom: '1px solid #e0e0e0' }}>Equinox</td>
                        <td style={{ padding: '4px 8px', textAlign: 'right', borderBottom: '1px solid #e0e0e0' }}>
                          {exposure.seasonal_shading.equinox.shaded_percentage.toFixed(0)}%
                        </td>
                        <td style={{ padding: '4px 8px', borderBottom: '1px solid #e0e0e0', fontSize: '0.8em' }}>
                          {exposure.seasonal_shading.equinox.exposure_category}
                        </td>
                      </tr>
                    )}
                    {exposure.seasonal_shading.summer && (
                      <tr>
                        <td style={{ padding: '4px 8px' }}>Summer</td>
                        <td style={{ padding: '4px 8px', textAlign: 'right' }}>
                          {exposure.seasonal_shading.summer.shaded_percentage.toFixed(0)}%
                        </td>
                        <td style={{ padding: '4px 8px', fontSize: '0.8em' }}>
                          {exposure.seasonal_shading.summer.exposure_category}
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            )}

            {exposure.warnings && exposure.warnings.length > 0 && (
              <div style={{
                padding: '8px',
                backgroundColor: '#fff3e0',
                borderRadius: '4px',
                border: '1px solid #ff9800',
                marginTop: '8px'
              }}>
                <strong style={{ color: '#e65100', fontSize: '0.85em' }}>⚠️ Warnings:</strong>
                <ul style={{ margin: '4px 0 0 0', paddingLeft: '20px', fontSize: '0.8em' }}>
                  {exposure.warnings.map((warning, idx) => (
                    <li key={idx} style={{ color: '#bf360c', marginBottom: '2px' }}>{warning}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        );
      })()}

      <div className="canvas-legend">
        <p><strong>Instructions:</strong></p>
        <ul>
          <li>Click unplaced gardens to add them to the land</li>
          <li>Drag gardens to reposition them</li>
          <li>Click × to remove a garden from the land</li>
          <li>Gardens cannot overlap</li>
          <li>Grid: Minor lines = 0.1 units, Major lines = 1 unit</li>
          {showSeasonalShadows && (
            <>
              <li style={{ marginTop: '8px', color: '#1976d2' }}>
                <strong>Seasonal Shadows:</strong> Blue shaded areas show tree shadow projection
              </li>
              <li style={{ color: '#1976d2' }}>
                <strong>Garden Colors:</strong>{' '}
                <span style={{ color: '#2e7d32' }}>Green = Full Sun</span>,{' '}
                <span style={{ color: '#e65100' }}>Orange = Partial Sun</span>,{' '}
                <span style={{ color: '#616161' }}>Gray = Shade</span>
              </li>
            </>
          )}
        </ul>
      </div>
    </div>
  );
}
