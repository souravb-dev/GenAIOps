import React, { useState, useRef, useEffect } from 'react';
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
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const selectedCompartment = compartments.find(c => c.id === selectedCompartmentId);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  // Build hierarchical structure with better organization
  const buildHierarchy = (compartments: Compartment[]) => {
    if (!compartments || compartments.length === 0) {
      return [];
    }

    const hierarchy: (Compartment & { level: number; hasChildren: boolean })[] = [];
    
    // Find root compartments (those without parent_id or where compartment_id equals tenancy_id)
    const roots = compartments.filter(c => 
      !c.compartment_id || 
      c.name.toLowerCase().includes('root') ||
      c.name.toLowerCase().includes('tenancy')
    );
    
    const addToHierarchy = (comp: Compartment, level: number = 0) => {
      // Find children for this compartment
      const children = compartments.filter(c => c.compartment_id === comp.id);
      const hasChildren = children.length > 0;
      
      hierarchy.push({ ...comp, level, hasChildren });
      
      // Recursively add children, sorted by name
      children
        .sort((a, b) => a.name.localeCompare(b.name))
        .forEach(child => addToHierarchy(child, level + 1));
    };
    
    // Start with root compartments, sorted by name
    roots
      .sort((a, b) => a.name.localeCompare(b.name))
      .forEach(root => addToHierarchy(root, 0));
    
    // Add any orphaned compartments at level 0
    const processedIds = new Set(hierarchy.map(h => h.id));
    const orphaned = compartments
      .filter(comp => !processedIds.has(comp.id))
      .sort((a, b) => a.name.localeCompare(b.name));
    
    orphaned.forEach(comp => addToHierarchy(comp, 0));
    
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
    <div className="relative" ref={dropdownRef}>
      <label htmlFor="compartment-select" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        Select Compartment
      </label>
      <div className="relative">
        {/* Custom Dropdown Button */}
        <button
          type="button"
          onClick={() => setIsOpen(!isOpen)}
          className="block w-full pl-3 pr-10 py-2 text-base border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm text-left"
        >
          {selectedCompartment ? (
            <span className="flex items-center">
              <span className={`inline-block w-2 h-2 rounded-full mr-2 ${
                selectedCompartment.lifecycle_state === 'ACTIVE' ? 'bg-green-500' : 'bg-gray-400'
              }`}></span>
              {selectedCompartment.name}
              {selectedCompartment.lifecycle_state !== 'ACTIVE' && ` (${selectedCompartment.lifecycle_state})`}
            </span>
          ) : (
            <span className="text-gray-500">Select a compartment...</span>
          )}
        </button>
        
        {/* Dropdown Arrow */}
        <div className="absolute inset-y-0 right-0 flex items-center pr-2 pointer-events-none">
          <i className={`fas fa-chevron-${isOpen ? 'up' : 'down'} text-gray-400 transition-transform duration-200`}></i>
        </div>

        {/* Custom Dropdown Menu */}
        {isOpen && (
          <div className="absolute z-50 mt-1 w-full bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-lg max-h-60 overflow-auto">
            {hierarchicalCompartments.length === 0 ? (
              <div className="px-3 py-2 text-gray-500 dark:text-gray-400 text-sm">
                {compartments.length === 0 ? "No compartments found (check OCI configuration)" : "No compartments available"}
              </div>
            ) : (
              hierarchicalCompartments.map((compartment) => {
                const isSelected = compartment.id === selectedCompartmentId;
                
                return (
                  <button
                    key={compartment.id}
                    type="button"
                    onClick={() => {
                      onCompartmentChange(compartment.id);
                      setIsOpen(false);
                    }}
                    className={`w-full text-left px-3 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors duration-150 ${
                      isSelected ? 'bg-blue-50 dark:bg-blue-900 text-blue-700 dark:text-blue-300' : 'text-gray-900 dark:text-white'
                    }`}
                    style={{ paddingLeft: `${12 + (compartment.level * 16)}px` }}
                  >
                    <div className="flex items-center">
                      {/* Hierarchy indicators */}
                      {compartment.level > 0 && (
                        <span className="text-gray-400 mr-2">└─</span>
                      )}
                      
                      {/* Status indicator */}
                      <span className={`inline-block w-2 h-2 rounded-full mr-2 ${
                        compartment.lifecycle_state === 'ACTIVE' ? 'bg-green-500' : 'bg-gray-400'
                      }`}></span>
                      
                      {/* Compartment name */}
                      <span className="flex-1">{compartment.name}</span>
                      
                      {/* Children indicator */}
                      {compartment.hasChildren && (
                        <span className="text-gray-400 ml-2">📁</span>
                      )}
                      
                      {/* State indicator for non-active */}
                      {compartment.lifecycle_state !== 'ACTIVE' && (
                        <span className="text-xs text-gray-500 ml-2">({compartment.lifecycle_state})</span>
                      )}
                    </div>
                  </button>
                );
              })
            )}
          </div>
        )}
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