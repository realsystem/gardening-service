import { useState, useRef, useEffect } from 'react';
import { useUnitSystem } from '../contexts/UnitSystemContext';
import { convertDistance, getUnitLabels } from '../utils/units';
import './GardenPlantPlacer.css';

interface PlantPosition {
  x: number;
  y: number;
}

interface ExistingPlant {
  id: number;
  name: string;
  x: number;
  y: number;
  spacing?: number; // spacing in inches
}

interface GardenPlantPlacerProps {
  gardenWidth?: number;
  gardenHeight?: number;
  existingPlants?: ExistingPlant[];
  currentPosition?: PlantPosition;
  currentPlantSpacing?: number; // spacing in inches for the plant being placed
  onPositionChange: (position: PlantPosition) => void;
}

const CANVAS_WIDTH = 400;
const CANVAS_HEIGHT = 320;
const GRID_SIZE = 50; // pixels per meter
const GRID_CELL_SIZE = 0.3048; // 1 foot in meters (12 inches = 0.3048m)

export function GardenPlantPlacer({
  gardenWidth = 10,
  gardenHeight = 8,
  existingPlants = [],
  currentPosition,
  currentPlantSpacing,
  onPositionChange
}: GardenPlantPlacerProps) {
  const { unitSystem } = useUnitSystem();
  const unitLabels = getUnitLabels(unitSystem);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [hoveredPosition, setHoveredPosition] = useState<PlantPosition | null>(null);
  const [isValidPosition, setIsValidPosition] = useState(true);

  // Convert garden dimensions for display
  const displayWidth = convertDistance(gardenWidth, unitSystem);
  const displayHeight = convertDistance(gardenHeight, unitSystem);

  // Calculate scale to fit garden in canvas
  const scaleX = CANVAS_WIDTH / gardenWidth;
  const scaleY = CANVAS_HEIGHT / gardenHeight;
  const scale = Math.min(scaleX, scaleY, GRID_SIZE);

  const canvasDisplayWidth = gardenWidth * scale;
  const canvasDisplayHeight = gardenHeight * scale;

  // Helper function to snap position to cell centers (not grid lines)
  const snapToGrid = (x: number, y: number): PlantPosition => {
    // Find which cell we're in
    const cellX = Math.floor(x / GRID_CELL_SIZE);
    const cellY = Math.floor(y / GRID_CELL_SIZE);

    // Snap to the center of that cell
    const gridX = cellX * GRID_CELL_SIZE + GRID_CELL_SIZE / 2;
    const gridY = cellY * GRID_CELL_SIZE + GRID_CELL_SIZE / 2;

    return { x: gridX, y: gridY };
  };

  // Helper function to check if a position is valid (not too close to existing plants)
  const isPositionValid = (position: PlantPosition, plantSpacing?: number): boolean => {
    if (!plantSpacing) return true;

    const minDistanceMeters = (plantSpacing * 0.0254); // Convert inches to meters

    for (const plant of existingPlants) {
      const distance = Math.sqrt(
        Math.pow(position.x - plant.x, 2) + Math.pow(position.y - plant.y, 2)
      );

      // Check against the larger of the two plant spacings
      const requiredDistance = plant.spacing
        ? Math.max(minDistanceMeters, plant.spacing * 0.0254)
        : minDistanceMeters;

      if (distance < requiredDistance) {
        return false;
      }
    }

    return true;
  };

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw grid (1 foot = 0.3048m grid cells)
    ctx.strokeStyle = '#e0e0e0';
    ctx.lineWidth = 1;

    // Vertical lines (every 1 foot)
    for (let x = 0; x <= gardenWidth; x += GRID_CELL_SIZE) {
      const px = x * scale;
      ctx.beginPath();
      ctx.moveTo(px, 0);
      ctx.lineTo(px, canvasDisplayHeight);
      ctx.stroke();
    }

    // Horizontal lines (every 1 foot)
    for (let y = 0; y <= gardenHeight; y += GRID_CELL_SIZE) {
      const py = y * scale;
      ctx.beginPath();
      ctx.moveTo(0, py);
      ctx.lineTo(canvasDisplayWidth, py);
      ctx.stroke();
    }

    // Draw cell center dots to show where plants can be placed
    ctx.fillStyle = '#d0d0d0';
    for (let x = GRID_CELL_SIZE / 2; x < gardenWidth; x += GRID_CELL_SIZE) {
      for (let y = GRID_CELL_SIZE / 2; y < gardenHeight; y += GRID_CELL_SIZE) {
        const px = x * scale;
        const py = y * scale;
        ctx.beginPath();
        ctx.arc(px, py, 2, 0, Math.PI * 2);
        ctx.fill();
      }
    }

    // Draw blocked cells (where existing plants and their spacing radii are)
    existingPlants.forEach((plant) => {
      if (plant.spacing) {
        const radiusMeters = plant.spacing * 0.0254; // Convert inches to meters
        const px = plant.x * scale;
        const py = plant.y * scale;
        const radiusPx = radiusMeters * scale;

        // Draw spacing radius
        ctx.fillStyle = 'rgba(244, 67, 54, 0.1)';
        ctx.beginPath();
        ctx.arc(px, py, radiusPx, 0, Math.PI * 2);
        ctx.fill();

        ctx.strokeStyle = 'rgba(244, 67, 54, 0.2)';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.arc(px, py, radiusPx, 0, Math.PI * 2);
        ctx.stroke();
      }
    });

    // Draw garden border
    ctx.strokeStyle = '#4caf50';
    ctx.lineWidth = 2;
    ctx.strokeRect(0, 0, canvasDisplayWidth, canvasDisplayHeight);

    // Draw existing plants
    existingPlants.forEach((plant) => {
      const px = plant.x * scale;
      const py = plant.y * scale;

      // Plant marker (circle)
      ctx.fillStyle = '#8bc34a';
      ctx.beginPath();
      ctx.arc(px, py, 8, 0, Math.PI * 2);
      ctx.fill();

      // Plant label
      ctx.fillStyle = '#333';
      ctx.font = '10px sans-serif';
      ctx.fillText(plant.name, px + 12, py + 4);
    });

    // Draw hovered position
    if (hoveredPosition) {
      const px = hoveredPosition.x * scale;
      const py = hoveredPosition.y * scale;
      const valid = isPositionValid(hoveredPosition, currentPlantSpacing);

      // Draw grid cell highlight
      const cellX = Math.floor(hoveredPosition.x / GRID_CELL_SIZE) * GRID_CELL_SIZE * scale;
      const cellY = Math.floor(hoveredPosition.y / GRID_CELL_SIZE) * GRID_CELL_SIZE * scale;
      const cellSize = GRID_CELL_SIZE * scale;

      ctx.fillStyle = valid ? 'rgba(76, 175, 80, 0.15)' : 'rgba(244, 67, 54, 0.15)';
      ctx.fillRect(cellX, cellY, cellSize, cellSize);

      ctx.fillStyle = valid ? 'rgba(76, 175, 80, 0.3)' : 'rgba(244, 67, 54, 0.3)';
      ctx.beginPath();
      ctx.arc(px, py, 10, 0, Math.PI * 2);
      ctx.fill();

      ctx.strokeStyle = valid ? '#4caf50' : '#f44336';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(px, py, 10, 0, Math.PI * 2);
      ctx.stroke();
    }

    // Draw current position
    if (currentPosition) {
      const px = currentPosition.x * scale;
      const py = currentPosition.y * scale;

      // Outer glow
      ctx.fillStyle = 'rgba(33, 150, 243, 0.3)';
      ctx.beginPath();
      ctx.arc(px, py, 15, 0, Math.PI * 2);
      ctx.fill();

      // Plant marker
      ctx.fillStyle = '#2196f3';
      ctx.beginPath();
      ctx.arc(px, py, 10, 0, Math.PI * 2);
      ctx.fill();

      // White center
      ctx.fillStyle = 'white';
      ctx.beginPath();
      ctx.arc(px, py, 4, 0, Math.PI * 2);
      ctx.fill();

      // Label
      ctx.fillStyle = '#1976d2';
      ctx.font = 'bold 12px sans-serif';
      ctx.fillText('New Plant', px + 18, py + 4);
    }
  }, [gardenWidth, gardenHeight, scale, canvasDisplayWidth, canvasDisplayHeight, existingPlants, currentPosition, hoveredPosition, currentPlantSpacing]);

  const handleCanvasClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    // Convert to garden coordinates
    const gardenX = x / scale;
    const gardenY = y / scale;

    // Snap to grid
    const snappedPosition = snapToGrid(gardenX, gardenY);

    // Clamp to garden bounds
    const clampedX = Math.max(0, Math.min(gardenWidth, snappedPosition.x));
    const clampedY = Math.max(0, Math.min(gardenHeight, snappedPosition.y));

    const finalPosition = { x: clampedX, y: clampedY };

    // Check if position is valid
    const valid = isPositionValid(finalPosition, currentPlantSpacing);
    setIsValidPosition(valid);

    // Only update if valid
    if (valid) {
      onPositionChange(finalPosition);
    }
  };

  const handleCanvasMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const gardenX = x / scale;
    const gardenY = y / scale;

    // Snap to grid
    const snappedPosition = snapToGrid(gardenX, gardenY);

    const clampedX = Math.max(0, Math.min(gardenWidth, snappedPosition.x));
    const clampedY = Math.max(0, Math.min(gardenHeight, snappedPosition.y));

    setHoveredPosition({ x: clampedX, y: clampedY });
  };

  const handleCanvasMouseLeave = () => {
    setHoveredPosition(null);
  };

  return (
    <div className="garden-plant-placer">
      <div className="placer-header">
        <h4>Click to Place Plant</h4>
        <div className="garden-dimensions">
          Garden: {displayWidth.toFixed(1)} × {displayHeight.toFixed(1)} {unitLabels.distanceShort}
        </div>
      </div>

      <div className="canvas-container">
        <canvas
          ref={canvasRef}
          width={canvasDisplayWidth}
          height={canvasDisplayHeight}
          onClick={handleCanvasClick}
          onMouseMove={handleCanvasMouseMove}
          onMouseLeave={handleCanvasMouseLeave}
          style={{
            cursor: 'crosshair',
            border: '2px solid #ddd',
            borderRadius: '4px',
            background: '#fafafa'
          }}
        />
      </div>

      {!isValidPosition && (
        <div className="error" style={{ marginTop: '10px' }}>
          ⚠️ Cannot place plant here - too close to existing plants. Plants need proper spacing to grow healthy!
        </div>
      )}

      {currentPosition && (
        <div className="position-display">
          <strong>Selected Position:</strong> ({currentPosition.x.toFixed(2)}m, {currentPosition.y.toFixed(2)}m)
          {currentPlantSpacing && (
            <span style={{ marginLeft: '10px', color: '#666', fontSize: '0.9em' }}>
              (Requires {currentPlantSpacing}" spacing)
            </span>
          )}
        </div>
      )}

      {hoveredPosition && !currentPosition && (
        <div className="position-preview" style={{
          color: isPositionValid(hoveredPosition, currentPlantSpacing) ? '#666' : '#f44336'
        }}>
          Preview: ({hoveredPosition.x.toFixed(2)}m, {hoveredPosition.y.toFixed(2)}m)
          {!isPositionValid(hoveredPosition, currentPlantSpacing) && ' - Too close!'}
        </div>
      )}

      <div className="placer-instructions">
        <p><strong>🌱 How to use:</strong></p>
        <ul>
          <li>Click anywhere to snap plant to nearest cell center (gray dots)</li>
          <li>Grid cells are 1 foot (12 inches) apart - plants placed at cell centers only</li>
          <li>Green dots show existing plants with red spacing zones</li>
          <li>Cannot place plants too close - proper spacing prevents overcrowding!</li>
          {currentPlantSpacing && (
            <li><strong>Current plant needs {currentPlantSpacing}" spacing minimum</strong></li>
          )}
        </ul>
      </div>
    </div>
  );
}
