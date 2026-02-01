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
}

interface GardenPlantPlacerProps {
  gardenWidth?: number;
  gardenHeight?: number;
  existingPlants?: ExistingPlant[];
  currentPosition?: PlantPosition;
  onPositionChange: (position: PlantPosition) => void;
}

const CANVAS_WIDTH = 500;
const CANVAS_HEIGHT = 400;
const GRID_SIZE = 50; // pixels per meter

export function GardenPlantPlacer({
  gardenWidth = 10,
  gardenHeight = 8,
  existingPlants = [],
  currentPosition,
  onPositionChange
}: GardenPlantPlacerProps) {
  const { unitSystem } = useUnitSystem();
  const unitLabels = getUnitLabels(unitSystem);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [hoveredPosition, setHoveredPosition] = useState<PlantPosition | null>(null);

  // Convert garden dimensions for display
  const displayWidth = convertDistance(gardenWidth, unitSystem);
  const displayHeight = convertDistance(gardenHeight, unitSystem);

  // Calculate scale to fit garden in canvas
  const scaleX = CANVAS_WIDTH / gardenWidth;
  const scaleY = CANVAS_HEIGHT / gardenHeight;
  const scale = Math.min(scaleX, scaleY, GRID_SIZE);

  const canvasDisplayWidth = gardenWidth * scale;
  const canvasDisplayHeight = gardenHeight * scale;

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw grid
    ctx.strokeStyle = '#e0e0e0';
    ctx.lineWidth = 1;

    // Vertical lines (every 0.5m)
    for (let x = 0; x <= gardenWidth; x += 0.5) {
      const px = x * scale;
      ctx.beginPath();
      ctx.moveTo(px, 0);
      ctx.lineTo(px, canvasDisplayHeight);
      ctx.stroke();
    }

    // Horizontal lines (every 0.5m)
    for (let y = 0; y <= gardenHeight; y += 0.5) {
      const py = y * scale;
      ctx.beginPath();
      ctx.moveTo(0, py);
      ctx.lineTo(canvasDisplayWidth, py);
      ctx.stroke();
    }

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

      ctx.fillStyle = 'rgba(76, 175, 80, 0.2)';
      ctx.beginPath();
      ctx.arc(px, py, 10, 0, Math.PI * 2);
      ctx.fill();

      ctx.strokeStyle = '#4caf50';
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
  }, [gardenWidth, gardenHeight, scale, canvasDisplayWidth, canvasDisplayHeight, existingPlants, currentPosition, hoveredPosition]);

  const handleCanvasClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    // Convert to garden coordinates
    const gardenX = Math.round((x / scale) * 10) / 10; // Round to 0.1m
    const gardenY = Math.round((y / scale) * 10) / 10;

    // Clamp to garden bounds
    const clampedX = Math.max(0, Math.min(gardenWidth, gardenX));
    const clampedY = Math.max(0, Math.min(gardenHeight, gardenY));

    onPositionChange({ x: clampedX, y: clampedY });
  };

  const handleCanvasMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const gardenX = Math.round((x / scale) * 10) / 10;
    const gardenY = Math.round((y / scale) * 10) / 10;

    const clampedX = Math.max(0, Math.min(gardenWidth, gardenX));
    const clampedY = Math.max(0, Math.min(gardenHeight, gardenY));

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

      {currentPosition && (
        <div className="position-display">
          <strong>Selected Position:</strong> ({currentPosition.x.toFixed(1)}m, {currentPosition.y.toFixed(1)}m)
        </div>
      )}

      {hoveredPosition && !currentPosition && (
        <div className="position-preview">
          Preview: ({hoveredPosition.x.toFixed(1)}m, {hoveredPosition.y.toFixed(1)}m)
        </div>
      )}

      <div className="placer-instructions">
        <p><strong>🌱 How to use:</strong></p>
        <ul>
          <li>Click anywhere in the garden to place your plant</li>
          <li>Green dots show existing plants</li>
          <li>Grid lines are 0.5m apart</li>
          <li>Place plants close together for companion benefits!</li>
        </ul>
      </div>
    </div>
  );
}
