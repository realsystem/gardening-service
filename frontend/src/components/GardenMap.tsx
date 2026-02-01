import { useState, useRef, useEffect } from 'react';
import type { PlantingInGarden } from '../types';
import { useUnitSystem } from '../contexts/UnitSystemContext';
import { convertDistance, getUnitLabels } from '../utils/units';
import './GardenMap.css';

interface GardenMapProps {
  plantings: PlantingInGarden[];
  gardenWidth?: number;
  gardenHeight?: number;
}

const CANVAS_WIDTH = 600;
const CANVAS_HEIGHT = 400;
const MIN_SCALE = 30; // Minimum pixels per meter

export function GardenMap({ plantings, gardenWidth = 10, gardenHeight = 8 }: GardenMapProps) {
  const { unitSystem } = useUnitSystem();
  const unitLabels = getUnitLabels(unitSystem);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [hoveredPlant, setHoveredPlant] = useState<number | null>(null);

  // Filter plantings that have positions
  const positionedPlantings = plantings.filter(p => p.x !== undefined && p.y !== undefined);

  // Calculate canvas scale to fit garden
  const scaleX = CANVAS_WIDTH / gardenWidth;
  const scaleY = CANVAS_HEIGHT / gardenHeight;
  const scale = Math.max(MIN_SCALE, Math.min(scaleX, scaleY));

  const canvasDisplayWidth = gardenWidth * scale;
  const canvasDisplayHeight = gardenHeight * scale;

  // Convert dimensions for display
  const displayWidth = convertDistance(gardenWidth, unitSystem);
  const displayHeight = convertDistance(gardenHeight, unitSystem);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw grid background
    ctx.strokeStyle = '#e8e8e8';
    ctx.lineWidth = 1;

    // Vertical grid lines (every 0.5m)
    for (let x = 0; x <= gardenWidth; x += 0.5) {
      const px = x * scale;
      ctx.beginPath();
      ctx.moveTo(px, 0);
      ctx.lineTo(px, canvasDisplayHeight);
      ctx.stroke();
    }

    // Horizontal grid lines (every 0.5m)
    for (let y = 0; y <= gardenHeight; y += 0.5) {
      const py = y * scale;
      ctx.beginPath();
      ctx.moveTo(0, py);
      ctx.lineTo(canvasDisplayWidth, py);
      ctx.stroke();
    }

    // Draw garden border
    ctx.strokeStyle = '#4caf50';
    ctx.lineWidth = 3;
    ctx.strokeRect(0, 0, canvasDisplayWidth, canvasDisplayHeight);

    // Draw axis labels
    ctx.fillStyle = '#666';
    ctx.font = '11px sans-serif';

    // X-axis labels (every meter)
    for (let x = 0; x <= gardenWidth; x += 1) {
      const px = x * scale;
      ctx.fillText(`${x}m`, px - 8, canvasDisplayHeight + 15);
    }

    // Y-axis labels (every meter)
    for (let y = 0; y <= gardenHeight; y += 1) {
      const py = y * scale;
      ctx.fillText(`${y}m`, -20, py + 4);
    }

    // Draw plants
    positionedPlantings.forEach((planting) => {
      const px = (planting.x || 0) * scale;
      const py = (planting.y || 0) * scale;
      const isHovered = hoveredPlant === planting.id;

      // Plant marker (circle)
      ctx.fillStyle = isHovered ? '#2196f3' : '#66bb6a';
      ctx.beginPath();
      ctx.arc(px, py, isHovered ? 12 : 10, 0, Math.PI * 2);
      ctx.fill();

      // White border
      ctx.strokeStyle = 'white';
      ctx.lineWidth = 2;
      ctx.stroke();

      // Plant label
      const plantName = planting.plant_name || 'Plant';
      ctx.fillStyle = isHovered ? '#1976d2' : '#333';
      ctx.font = isHovered ? 'bold 12px sans-serif' : '11px sans-serif';

      // Background for label
      const textMetrics = ctx.measureText(plantName);
      const textWidth = textMetrics.width;
      const textX = px + 15;
      const textY = py + 4;

      if (isHovered) {
        ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
        ctx.fillRect(textX - 2, textY - 12, textWidth + 4, 16);
        ctx.strokeStyle = '#2196f3';
        ctx.lineWidth = 1;
        ctx.strokeRect(textX - 2, textY - 12, textWidth + 4, 16);
      }

      ctx.fillStyle = isHovered ? '#1976d2' : '#333';
      ctx.fillText(plantName, textX, textY);

      // Show position on hover
      if (isHovered) {
        const posText = `(${planting.x?.toFixed(1)}m, ${planting.y?.toFixed(1)}m)`;
        ctx.fillStyle = '#666';
        ctx.font = '10px sans-serif';
        ctx.fillText(posText, textX, textY + 12);
      }
    });
  }, [gardenWidth, gardenHeight, scale, canvasDisplayWidth, canvasDisplayHeight, positionedPlantings, hoveredPlant]);

  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    // Check if mouse is near any plant
    let foundPlant: number | null = null;
    for (const planting of positionedPlantings) {
      const px = (planting.x || 0) * scale;
      const py = (planting.y || 0) * scale;
      const distance = Math.sqrt((x - px) ** 2 + (y - py) ** 2);

      if (distance < 15) {
        foundPlant = planting.id;
        break;
      }
    }

    setHoveredPlant(foundPlant);
  };

  const handleMouseLeave = () => {
    setHoveredPlant(null);
  };

  if (positionedPlantings.length === 0) {
    return (
      <div className="garden-map">
        <div className="map-header">
          <h3>🗺️ Garden Layout</h3>
          <div className="garden-dimensions">
            {displayWidth.toFixed(1)} × {displayHeight.toFixed(1)} {unitLabels.distanceShort}
          </div>
        </div>
        <div className="no-plants-message">
          No plants with positions yet. Use the visual placer when adding plants to see them on the map!
        </div>
      </div>
    );
  }

  return (
    <div className="garden-map">
      <div className="map-header">
        <h3>🗺️ Garden Layout</h3>
        <div className="garden-info">
          <span className="garden-dimensions">
            {displayWidth.toFixed(1)} × {displayHeight.toFixed(1)} {unitLabels.distanceShort}
          </span>
          <span className="plant-count">
            {positionedPlantings.length} {positionedPlantings.length === 1 ? 'plant' : 'plants'} positioned
          </span>
        </div>
      </div>

      <div className="canvas-container">
        <canvas
          ref={canvasRef}
          width={canvasDisplayWidth}
          height={canvasDisplayHeight}
          onMouseMove={handleMouseMove}
          onMouseLeave={handleMouseLeave}
          style={{
            border: '1px solid #ddd',
            borderRadius: '4px',
            background: '#fafafa',
            cursor: hoveredPlant ? 'pointer' : 'default'
          }}
        />
      </div>

      <div className="map-legend">
        <div className="legend-item">
          <div className="legend-marker plant-marker"></div>
          <span>Planted crops</span>
        </div>
        <div className="legend-item">
          <div className="legend-marker grid-marker"></div>
          <span>Grid: 0.5m spacing</span>
        </div>
      </div>

      {hoveredPlant && (
        <div className="hovered-plant-info">
          {(() => {
            const plant = positionedPlantings.find(p => p.id === hoveredPlant);
            if (!plant) return null;
            return (
              <>
                <strong>{plant.plant_name || 'Plant'}</strong>
                <span className="plant-details">
                  Position: ({plant.x?.toFixed(1)}m, {plant.y?.toFixed(1)}m)
                  {plant.planting_date && ` • Planted: ${new Date(plant.planting_date).toLocaleDateString()}`}
                  {plant.plant_count && ` • Count: ${plant.plant_count}`}
                </span>
              </>
            );
          })()}
        </div>
      )}
    </div>
  );
}
