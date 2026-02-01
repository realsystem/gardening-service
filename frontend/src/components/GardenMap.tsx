import type { PlantingInGarden } from '../types';

interface GardenMapProps {
  plantings: PlantingInGarden[];
  gardenWidth?: number;
  gardenHeight?: number;
}

export function GardenMap({ plantings }: GardenMapProps) {
  const positionedPlantings = plantings.filter(p => p.x !== undefined && p.y !== undefined);

  if (positionedPlantings.length === 0) {
    return (
      <div style={{ padding: '20px', background: '#f5f5f5', borderRadius: '8px', margin: '20px 0' }}>
        <h3>🗺️ Garden Layout</h3>
        <p>No plants with positions yet. Use the visual placer when adding plants to see them on the map!</p>
      </div>
    );
  }

  return (
    <div style={{ padding: '20px', background: 'white', borderRadius: '8px', margin: '20px 0', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
      <h3>🗺️ Garden Layout</h3>
      <p>{positionedPlantings.length} plants positioned in your garden</p>
      <div style={{ marginTop: '15px' }}>
        {positionedPlantings.map((planting) => (
          <div key={planting.id} style={{ padding: '8px', borderBottom: '1px solid #eee' }}>
            <strong>{planting.plant_name}</strong> - Position: ({planting.x?.toFixed(1)}m, {planting.y?.toFixed(1)}m)
          </div>
        ))}
      </div>
    </div>
  );
}
