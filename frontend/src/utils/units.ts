/**
 * Unit conversion utilities for imperial/metric systems
 */

export type UnitSystem = 'metric' | 'imperial';

export interface UnitLabel {
  distance: string;
  distanceShort: string;
  temperature: string;
  area: string;
}

/**
 * Get unit labels for a unit system
 */
export function getUnitLabels(unitSystem: UnitSystem): UnitLabel {
  if (unitSystem === 'imperial') {
    return {
      distance: 'feet',
      distanceShort: 'ft',
      temperature: '°F',
      area: 'sq ft',
    };
  } else {
    return {
      distance: 'meters',
      distanceShort: 'm',
      temperature: '°C',
      area: 'm²',
    };
  }
}

/**
 * Convert meters to the user's preferred unit system
 */
export function convertDistance(meters: number, unitSystem: UnitSystem): number {
  if (unitSystem === 'imperial') {
    // 1 meter = 3.28084 feet
    return meters * 3.28084;
  }
  return meters;
}

/**
 * Convert from user's unit system back to meters (for API calls)
 */
export function convertToMeters(value: number, unitSystem: UnitSystem): number {
  if (unitSystem === 'imperial') {
    // 1 foot = 0.3048 meters
    return value * 0.3048;
  }
  return value;
}

/**
 * Convert area from square meters to user's preferred unit
 */
export function convertArea(squareMeters: number, unitSystem: UnitSystem): number {
  if (unitSystem === 'imperial') {
    // 1 m² = 10.7639 sq ft
    return squareMeters * 10.7639;
  }
  return squareMeters;
}

/**
 * Convert temperature from Celsius to user's preferred unit
 */
export function convertTemperature(celsius: number, unitSystem: UnitSystem): number {
  if (unitSystem === 'imperial') {
    // °F = (°C × 9/5) + 32
    return (celsius * 9 / 5) + 32;
  }
  return celsius;
}

/**
 * Format a distance value with appropriate unit label
 */
export function formatDistance(
  meters: number,
  unitSystem: UnitSystem,
  decimals: number = 1
): string {
  const converted = convertDistance(meters, unitSystem);
  const label = getUnitLabels(unitSystem).distanceShort;
  return `${converted.toFixed(decimals)} ${label}`;
}

/**
 * Format an area value with appropriate unit label
 */
export function formatArea(
  squareMeters: number,
  unitSystem: UnitSystem,
  decimals: number = 1
): string {
  const converted = convertArea(squareMeters, unitSystem);
  const label = getUnitLabels(unitSystem).area;
  return `${converted.toFixed(decimals)} ${label}`;
}

/**
 * Format a temperature value with appropriate unit label
 */
export function formatTemperature(
  celsius: number,
  unitSystem: UnitSystem,
  decimals: number = 1
): string {
  const converted = convertTemperature(celsius, unitSystem);
  const label = getUnitLabels(unitSystem).temperature;
  return `${converted.toFixed(decimals)}${label}`;
}

/**
 * Parse a distance input from user (in their unit system) and convert to meters
 */
export function parseDistanceInput(
  input: string | number,
  unitSystem: UnitSystem
): number {
  const value = typeof input === 'string' ? parseFloat(input) : input;
  if (isNaN(value)) {
    return 0;
  }
  return convertToMeters(value, unitSystem);
}
