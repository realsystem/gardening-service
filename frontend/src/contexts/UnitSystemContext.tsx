import { createContext, useContext, ReactNode } from 'react';
import { UnitSystem } from '../types';

interface UnitSystemContextType {
  unitSystem: UnitSystem;
}

const UnitSystemContext = createContext<UnitSystemContextType | undefined>(undefined);

interface UnitSystemProviderProps {
  children: ReactNode;
  unitSystem: UnitSystem;
}

export function UnitSystemProvider({ children, unitSystem }: UnitSystemProviderProps) {
  return (
    <UnitSystemContext.Provider value={{ unitSystem }}>
      {children}
    </UnitSystemContext.Provider>
  );
}

export function useUnitSystem(): UnitSystemContextType {
  const context = useContext(UnitSystemContext);
  if (context === undefined) {
    // Default to metric if context is not available
    return { unitSystem: 'metric' };
  }
  return context;
}
