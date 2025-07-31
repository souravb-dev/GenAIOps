import React, { useState } from 'react';

interface Resource {
  id: string;
  name?: string;
  display_name?: string;
  lifecycle_state: string;
  [key: string]: any;
}

interface ResourceCardProps {
  title: string;
  icon: string;
  color: 'blue' | 'green' | 'purple' | 'orange' | 'indigo' | 'red';
  resources: Resource[];
  resourceType: string;
}

export function ResourceCard({ title, icon, color, resources, resourceType }: ResourceCardProps) {
  const [expanded, setExpanded] = useState(false);
  
  const colorClasses = {
    blue: {
      bg: 'bg-blue-500',
      text: 'text-blue-600 dark:text-blue-400',
      badge: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
    },
    green: {
      bg: 'bg-green-500',
      text: 'text-green-600 dark:text-green-400',
      badge: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
    },
    purple: {
      bg: 'bg-purple-500',
      text: 'text-purple-600 dark:text-purple-400',
      badge: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200'
    },
    orange: {
      bg: 'bg-orange-500',
      text: 'text-orange-600 dark:text-orange-400',
      badge: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200'
    },
    indigo: {
      bg: 'bg-indigo-500',
      text: 'text-indigo-600 dark:text-indigo-400',
      badge: 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200'
    },
    red: {
      bg: 'bg-red-500',
      text: 'text-red-600 dark:text-red-400',
      badge: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
    }
  };

  const getHealthStatus = (resource: Resource) => {
    if (resource.lifecycle_state === 'ACTIVE' || resource.lifecycle_state === 'RUNNING') {
      return { status: 'healthy', color: 'text-green-500', icon: 'fas fa-check-circle' };
    } else if (resource.lifecycle_state === 'STOPPED' || resource.lifecycle_state === 'INACTIVE') {
      return { status: 'stopped', color: 'text-yellow-500', icon: 'fas fa-pause-circle' };
    } else if (resource.lifecycle_state === 'FAILED' || resource.lifecycle_state === 'ERROR') {
      return { status: 'error', color: 'text-red-500', icon: 'fas fa-exclamation-circle' };
    } else {
      return { status: 'unknown', color: 'text-gray-500', icon: 'fas fa-question-circle' };
    }
  };

  const healthyCount = resources.filter(r => r.lifecycle_state === 'ACTIVE' || r.lifecycle_state === 'RUNNING').length;
  const stoppedCount = resources.filter(r => r.lifecycle_state === 'STOPPED' || r.lifecycle_state === 'INACTIVE').length;
  const errorCount = resources.filter(r => r.lifecycle_state === 'FAILED' || r.lifecycle_state === 'ERROR').length;

  const getMockMetrics = () => {
    const baseMetrics = {
      cpu: Math.floor(Math.random() * 100),
      memory: Math.floor(Math.random() * 100),
      network: Math.floor(Math.random() * 100)
    };
    return baseMetrics;
  };

  const metrics = getMockMetrics();

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow hover:shadow-lg transition-shadow duration-200">
      <div className="p-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <div className={`${colorClasses[color].bg} rounded-lg p-3`}>
              <i className={`${icon} text-white text-xl`}></i>
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                {title}
              </h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                {resources.length} {resources.length === 1 ? 'resource' : 'resources'}
              </p>
            </div>
          </div>
          <div className="text-right">
            <div className={`text-2xl font-bold ${colorClasses[color].text}`}>
              {resources.length}
            </div>
          </div>
        </div>

        {/* Health Status Summary */}
        <div className="mt-4 flex items-center space-x-4">
          {healthyCount > 0 && (
            <div className="flex items-center text-sm text-green-600 dark:text-green-400">
              <i className="fas fa-check-circle mr-1"></i>
              {healthyCount} healthy
            </div>
          )}
          {stoppedCount > 0 && (
            <div className="flex items-center text-sm text-yellow-600 dark:text-yellow-400">
              <i className="fas fa-pause-circle mr-1"></i>
              {stoppedCount} stopped
            </div>
          )}
          {errorCount > 0 && (
            <div className="flex items-center text-sm text-red-600 dark:text-red-400">
              <i className="fas fa-exclamation-circle mr-1"></i>
              {errorCount} error
            </div>
          )}
          {resources.length === 0 && (
            <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
              <i className="fas fa-info-circle mr-1"></i>
              No resources
            </div>
          )}
        </div>

        {/* Mock Metrics Display */}
        {resources.length > 0 && (
          <div className="mt-4 space-y-2">
            <div className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">
              Average Metrics
            </div>
            <div className="grid grid-cols-3 gap-3">
              <div className="text-center">
                <div className="text-sm font-medium text-gray-900 dark:text-white">
                  {metrics.cpu}%
                </div>
                <div className="text-xs text-gray-500 dark:text-gray-400">CPU</div>
              </div>
              <div className="text-center">
                <div className="text-sm font-medium text-gray-900 dark:text-white">
                  {metrics.memory}%
                </div>
                <div className="text-xs text-gray-500 dark:text-gray-400">Memory</div>
              </div>
              <div className="text-center">
                <div className="text-sm font-medium text-gray-900 dark:text-white">
                  {metrics.network}%
                </div>
                <div className="text-xs text-gray-500 dark:text-gray-400">Network</div>
              </div>
            </div>
          </div>
        )}

        {/* Resource List Toggle */}
        {resources.length > 0 && (
          <div className="mt-4">
            <button
              onClick={() => setExpanded(!expanded)}
              className="w-full flex items-center justify-between text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
            >
              <span>View {resources.length} resources</span>
              <i className={`fas fa-chevron-${expanded ? 'up' : 'down'}`}></i>
            </button>
            
            {expanded && (
              <div className="mt-3 space-y-2 max-h-48 overflow-y-auto">
                {resources.map((resource, index) => {
                  const health = getHealthStatus(resource);
                  return (
                    <div
                      key={resource.id || index}
                      className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-700 rounded"
                    >
                      <div className="flex items-center min-w-0 flex-1">
                        <i className={`${health.icon} ${health.color} mr-2 text-sm`}></i>
                        <span className="text-sm text-gray-900 dark:text-white truncate">
                          {resource.display_name || resource.name || 'Unnamed Resource'}
                        </span>
                      </div>
                      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                        resource.lifecycle_state === 'ACTIVE' || resource.lifecycle_state === 'RUNNING'
                          ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                          : resource.lifecycle_state === 'STOPPED' || resource.lifecycle_state === 'INACTIVE'
                          ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                          : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                      }`}>
                        {resource.lifecycle_state}
                      </span>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {/* Action Button */}
        <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
          <button className={`w-full text-sm font-medium ${colorClasses[color].text} hover:underline`}>
            Manage {title}
          </button>
        </div>
      </div>
    </div>
  );
} 