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

  // Build hierarchical structure with proper parent-child relationships
  const buildHierarchy = (compartments: Compartment[]) => {
    if (!compartments || compartments.length === 0) {
      return [];
    }

    console.log('🏗️ Building compartment hierarchy from data:', compartments);
    console.log('🔍 Compartment details:', compartments.map(c => `${c.name} (id: ${c.id}, parent: ${c.compartment_id || 'none'})`));

    const hierarchy: (Compartment & { level: number; hasChildren: boolean })[] = [];
    
    // Create a map of compartment IDs for quick lookup
    const compartmentMap = new Map(compartments.map(c => [c.id, c]));
    
    // Find root compartments - those with no compartment_id or where compartment_id doesn't exist in our list
    const roots = compartments.filter(c => {
      if (!c.compartment_id) return true; // No parent = root
      
      // If parent doesn't exist in our compartment list, treat as root
      const parentExists = compartmentMap.has(c.compartment_id);
      return !parentExists;
    });
    
    console.log('🌳 Found root compartments:', roots.map(r => `${r.name} (${r.id})`));
    
    const addToHierarchy = (comp: Compartment, level: number = 0) => {
      // Find direct children for this compartment
      const children = compartments.filter(c => c.compartment_id === comp.id);
      const hasChildren = children.length > 0;
      
      hierarchy.push({ ...comp, level, hasChildren });
      
      // Recursively add children, sorted by name for consistent ordering
      children
        .sort((a, b) => a.name.localeCompare(b.name))
        .forEach(child => addToHierarchy(child, level + 1));
    };
    
    // Start with root compartments, sorted by name
    roots
      .sort((a, b) => a.name.localeCompare(b.name))
      .forEach(root => addToHierarchy(root, 0));
    
    // Handle orphaned compartments (safety net)
    const processedIds = new Set(hierarchy.map(h => h.id));
    const orphaned = compartments
      .filter(comp => !processedIds.has(comp.id))
      .sort((a, b) => a.name.localeCompare(b.name));
    
    if (orphaned.length > 0) {
      console.warn('Found orphaned compartments (no valid parent-child relationship):', orphaned);
      orphaned.forEach(comp => addToHierarchy(comp, 0));
    }
    
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
                    className={`w-full text-left py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors duration-150 ${
                      isSelected ? 'bg-blue-50 dark:bg-blue-900 text-blue-700 dark:text-blue-300' : 'text-gray-900 dark:text-white'
                    }`}
                    style={{ paddingLeft: `${8}px`, paddingRight: `${12}px` }}
                  >
                    <div className="flex items-center">
                      {/* Enhanced hierarchy indicators with tree-like structure */}
                      {compartment.level > 0 && (
                        <div className="flex items-center text-gray-400 mr-1">
                          {/* Create indentation lines for deeper levels */}
                          {Array.from({ length: compartment.level - 1 }).map((_, i) => (
                            <span key={i} className="w-4 text-center">│</span>
                          ))}
                          <span className="w-4">├─</span>
                        </div>
                      )}
                      
                      {/* Parent/Child type indicator */}
                      <div className="flex items-center mr-2">
                        {compartment.level === 0 ? (
                          <i className="fas fa-home text-blue-500 w-4 text-center" title="Root Tenancy"></i>
                        ) : compartment.hasChildren ? (
                          <i className="fas fa-folder text-yellow-500 w-4 text-center" title="Parent Compartment"></i>
                        ) : (
                          <i className="fas fa-cube text-gray-500 w-4 text-center" title="Child Compartment"></i>
                        )}
                      </div>
                      
                      {/* Status indicator */}
                      <span className={`inline-block w-2 h-2 rounded-full mr-2 ${
                        compartment.lifecycle_state === 'ACTIVE' ? 'bg-green-500' : 'bg-gray-400'
                      }`}></span>
                      
                      {/* Compartment name with level styling */}
                      <span className={`flex-1 ${
                        compartment.level === 0 
                          ? 'font-semibold text-blue-700 dark:text-blue-300' 
                          : compartment.hasChildren 
                            ? 'font-medium' 
                            : 'font-normal'
                      }`}>
                        {compartment.name}
                      </span>
                      
                      {/* Children count indicator */}
                      {compartment.hasChildren && (
                        <span className="text-xs text-gray-500 ml-2 bg-gray-100 dark:bg-gray-600 px-1 rounded">
                          {compartments.filter(c => c.compartment_id === compartment.id).length}
                        </span>
                      )}
                      
                      {/* State indicator for non-active */}
                      {compartment.lifecycle_state !== 'ACTIVE' && (
                        <span className="text-xs text-orange-500 ml-2 font-medium">({compartment.lifecycle_state})</span>
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