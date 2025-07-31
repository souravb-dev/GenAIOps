import React from 'react';
import { LoadingSpinner } from './LoadingSpinner';

interface Compartment {
  id: string;
  name: string;
  description?: string;
  lifecycle_state: string;
  compartment_id?: string; // Parent compartment ID
  time_created?: string;
}

interface CompartmentSelectorProps {
  compartments: Compartment[];
  selectedCompartmentId: string;
  onCompartmentChange: (compartmentId: string) => void;
  loading?: boolean;
}

export function CompartmentSelector({ 
  compartments, 
  selectedCompartmentId, 
  onCompartmentChange, 
  loading 
}: CompartmentSelectorProps) {
  const selectedCompartment = compartments.find(c => c.id === selectedCompartmentId);

  // Build hierarchical structure
  const buildHierarchy = (compartments: Compartment[]) => {
    const compartmentMap = new Map(compartments.map(c => [c.id, c]));
    const hierarchy: (Compartment & { level: number })[] = [];
    
    // Find root compartments (those without parent or with null parent)
    const roots = compartments.filter(c => !c.compartment_id || c.name.includes('(root)'));
    
    const addToHierarchy = (comp: Compartment, level: number = 0) => {
      hierarchy.push({ ...comp, level });
      
      // Find children
      const children = compartments.filter(c => c.compartment_id === comp.id);
      children.forEach(child => addToHierarchy(child, level + 1));
    };
    
    // Start with root compartments
    roots.forEach(root => addToHierarchy(root, 0));
    
    // Add any orphaned compartments at level 0
    const processedIds = new Set(hierarchy.map(h => h.id));
    compartments.forEach(comp => {
      if (!processedIds.has(comp.id)) {
        addToHierarchy(comp, 0);
      }
    });
    
    return hierarchy;
  };

  const hierarchicalCompartments = buildHierarchy(compartments);

  if (loading) {
    return (
      <div className="flex items-center space-x-2">
        <LoadingSpinner size="sm" />
        <span className="text-sm text-gray-500 dark:text-gray-400">Loading compartments...</span>
      </div>
    );
  }

  return (
    <div className="relative">
      <label htmlFor="compartment-select" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        Select Compartment
      </label>
      <div className="relative">
        <select
          id="compartment-select"
          value={selectedCompartmentId}
          onChange={(e) => onCompartmentChange(e.target.value)}
          className="block w-full pl-3 pr-10 py-2 text-base border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
        >
          {hierarchicalCompartments.length === 0 ? (
            <option value="">No compartments available</option>
          ) : (
            hierarchicalCompartments.map((compartment) => (
              <option key={compartment.id} value={compartment.id}>
                {'│  '.repeat(compartment.level)}{compartment.level > 0 ? '├─ ' : ''}{compartment.name} ({compartment.lifecycle_state})
              </option>
            ))
          )}
        </select>
        <div className="absolute inset-y-0 right-0 flex items-center pr-2 pointer-events-none">
          <i className="fas fa-chevron-down text-gray-400"></i>
        </div>
      </div>
      
      {selectedCompartment && selectedCompartment.description && (
        <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
          {selectedCompartment.description}
        </p>
      )}
      
      <div className="mt-2 flex items-center space-x-4 text-xs text-gray-500 dark:text-gray-400">
        <span className="flex items-center">
          <i className="fas fa-cube mr-1"></i>
          {compartments.length} compartments
        </span>
        {selectedCompartment && (
          <span className={`flex items-center ${
            selectedCompartment.lifecycle_state === 'ACTIVE' 
              ? 'text-green-600 dark:text-green-400' 
              : 'text-gray-500 dark:text-gray-400'
          }`}>
            <div className={`w-2 h-2 rounded-full mr-1 ${
              selectedCompartment.lifecycle_state === 'ACTIVE'
                ? 'bg-green-500'
                : 'bg-gray-400'
            }`}></div>
            {selectedCompartment.lifecycle_state}
          </span>
        )}
      </div>
    </div>
  );
} 