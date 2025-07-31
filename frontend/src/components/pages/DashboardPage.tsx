import React from 'react';
import { useCompartments, useAllResources } from '../../services/cloudService';
import { LoadingSpinner } from '../ui/LoadingSpinner';

export function DashboardPage() {
  const { data: compartments, isLoading: compartmentsLoading, error: compartmentsError } = useCompartments();
  
  // Use the first compartment for demo purposes
  const selectedCompartment = compartments?.[0];
  const { 
    data: allResources, 
    isLoading: resourcesLoading, 
    error: resourcesError 
  } = useAllResources(selectedCompartment?.id || '', undefined);

  if (compartmentsLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" message="Loading compartments..." />
      </div>
    );
  }

  if (compartmentsError) {
    return (
      <div className="p-6">
        <div className="bg-red-50 dark:bg-red-900 border border-red-200 dark:border-red-700 rounded-md p-4">
          <div className="flex">
            <i className="fas fa-exclamation-circle text-red-400 mr-3 mt-0.5"></i>
            <div>
              <h3 className="text-sm font-medium text-red-800 dark:text-red-200">
                Error loading compartments
              </h3>
              <p className="mt-1 text-sm text-red-700 dark:text-red-300">
                {compartmentsError.message || 'Failed to load compartments'}
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          Dashboard Overview
        </h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Real-time view of your cloud infrastructure and operations
        </p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Resources"
          value={allResources?.total_resources || 0}
          icon="fas fa-cube"
          color="blue"
          isLoading={resourcesLoading}
        />
        <StatCard
          title="Compute Instances"
          value={allResources?.resources?.compute_instances?.length || 0}
          icon="fas fa-server"
          color="green"
          isLoading={resourcesLoading}
        />
        <StatCard
          title="Databases"
          value={allResources?.resources?.databases?.length || 0}
          icon="fas fa-database"
          color="purple"
          isLoading={resourcesLoading}
        />
        <StatCard
          title="OKE Clusters"
          value={allResources?.resources?.oke_clusters?.length || 0}
          icon="fas fa-dharmachakra"
          color="orange"
          isLoading={resourcesLoading}
        />
      </div>

      {/* Compartments */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-white">
            Available Compartments
          </h3>
          <div className="mt-5">
            {compartments && compartments.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {compartments.map((compartment) => (
                  <div
                    key={compartment.id}
                    className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-700"
                  >
                    <h4 className="font-medium text-gray-900 dark:text-white">
                      {compartment.name}
                    </h4>
                    <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                      {compartment.description}
                    </p>
                    <div className="mt-2">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        compartment.lifecycle_state === 'ACTIVE'
                          ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                          : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
                      }`}>
                        {compartment.lifecycle_state}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 dark:text-gray-400">
                No compartments available
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Resources Overview */}
      {selectedCompartment && (
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-white">
              Resources in {selectedCompartment.name}
            </h3>
            {resourcesLoading ? (
              <div className="mt-5">
                <LoadingSpinner message="Loading resources..." />
              </div>
            ) : resourcesError ? (
              <div className="mt-5 bg-yellow-50 dark:bg-yellow-900 border border-yellow-200 dark:border-yellow-700 rounded-md p-4">
                <p className="text-sm text-yellow-700 dark:text-yellow-200">
                  Unable to load resources. This might be expected if OCI credentials are not configured.
                </p>
              </div>
            ) : allResources ? (
              <div className="mt-5">
                <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
                  Last updated: {new Date(allResources.last_updated).toLocaleString()}
                </p>
                <div className="space-y-4">
                  {Object.entries(allResources.resources).map(([resourceType, resources]) => (
                    <div key={resourceType}>
                      <h4 className="font-medium text-gray-900 dark:text-white capitalize">
                        {resourceType.replace('_', ' ')} ({resources.length})
                      </h4>
                      {resources.length > 0 ? (
                        <div className="mt-2 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                          {resources.slice(0, 3).map((resource) => (
                            <div
                              key={resource.id}
                              className="border border-gray-200 dark:border-gray-700 rounded p-3"
                            >
                              <p className="font-medium text-sm text-gray-900 dark:text-white">
                                {resource.display_name || resource.name || 'Unnamed'}
                              </p>
                              <p className="text-xs text-gray-500 dark:text-gray-400">
                                {resource.lifecycle_state}
                              </p>
                            </div>
                          ))}
                          {resources.length > 3 && (
                            <div className="border border-gray-200 dark:border-gray-700 rounded p-3 flex items-center justify-center">
                              <p className="text-sm text-gray-500 dark:text-gray-400">
                                +{resources.length - 3} more
                              </p>
                            </div>
                          )}
                        </div>
                      ) : (
                        <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
                          No {resourceType.replace('_', ' ')} found
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            ) : null}
          </div>
        </div>
      )}
    </div>
  );
}

interface StatCardProps {
  title: string;
  value: number;
  icon: string;
  color: 'blue' | 'green' | 'purple' | 'orange';
  isLoading?: boolean;
}

function StatCard({ title, value, icon, color, isLoading }: StatCardProps) {
  const colorClasses = {
    blue: 'bg-blue-500',
    green: 'bg-green-500',
    purple: 'bg-purple-500',
    orange: 'bg-orange-500',
  };

  return (
    <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
      <div className="p-5">
        <div className="flex items-center">
          <div className="flex-shrink-0">
            <div className={`${colorClasses[color]} rounded-md p-3`}>
              <i className={`${icon} text-white text-xl`}></i>
            </div>
          </div>
          <div className="ml-5 w-0 flex-1">
            <dl>
              <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                {title}
              </dt>
              <dd>
                {isLoading ? (
                  <div className="h-8 flex items-center">
                    <LoadingSpinner size="sm" />
                  </div>
                ) : (
                  <div className="text-lg font-medium text-gray-900 dark:text-white">
                    {value.toLocaleString()}
                  </div>
                )}
              </dd>
            </dl>
          </div>
        </div>
      </div>
    </div>
  );
} 