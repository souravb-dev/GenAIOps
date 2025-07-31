import React, { useState } from 'react';
import { useCompartments, useAllResources } from '../../services/cloudService';
import { LoadingSpinner } from '../ui/LoadingSpinner';
import { CompartmentSelector } from '../ui/CompartmentSelector';
import { ResourceCard } from '../ui/ResourceCard';
import { MetricsChart } from '../ui/MetricsChart';
import { ResourceFilter } from '../ui/ResourceFilter';

export function DashboardPage() {
  const { data: compartments, isLoading: compartmentsLoading, error: compartmentsError } = useCompartments();
  const [selectedCompartmentId, setSelectedCompartmentId] = useState<string>('');
  
  // Filter states
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [selectedStatus, setSelectedStatus] = useState<string>('');
  const [selectedResourceType, setSelectedResourceType] = useState<string>('');
  
  // Set default compartment when compartments load
  React.useEffect(() => {
    if (compartments && compartments.length > 0 && !selectedCompartmentId) {
      setSelectedCompartmentId(compartments[0].id);
    }
  }, [compartments, selectedCompartmentId]);
  
  const selectedCompartment = compartments?.find(c => c.id === selectedCompartmentId);
  const { 
    data: allResources, 
    isLoading: resourcesLoading, 
    error: resourcesError 
  } = useAllResources(selectedCompartmentId || '', undefined);

  // Filter resources based on search and filter criteria
  const filterResources = (resources: any[], resourceType: string) => {
    if (!resources) return [];

    return resources.filter(resource => {
      // Search filter
      const matchesSearch = !searchTerm || 
        (resource.display_name && resource.display_name.toLowerCase().includes(searchTerm.toLowerCase())) ||
        (resource.name && resource.name.toLowerCase().includes(searchTerm.toLowerCase())) ||
        (resource.id && resource.id.toLowerCase().includes(searchTerm.toLowerCase()));

      // Status filter
      const matchesStatus = !selectedStatus || resource.lifecycle_state === selectedStatus;

      // Resource type filter
      const matchesResourceType = !selectedResourceType || resourceType === selectedResourceType;

      return matchesSearch && matchesStatus && matchesResourceType;
    });
  };

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
      {/* Header with Compartment Selector */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Dashboard Overview
          </h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Real-time view of your cloud infrastructure and operations
          </p>
        </div>
        <div className="mt-4 lg:mt-0 lg:ml-6">
          <CompartmentSelector
            compartments={compartments || []}
            selectedCompartmentId={selectedCompartmentId}
            onCompartmentChange={setSelectedCompartmentId}
            loading={compartmentsLoading}
          />
        </div>
      </div>

      {/* Auto-refresh indicator */}
      <div className="flex items-center justify-between bg-blue-50 dark:bg-blue-900 border border-blue-200 dark:border-blue-700 rounded-md p-3">
        <div className="flex items-center">
          <i className="fas fa-sync-alt text-blue-600 dark:text-blue-400 mr-2 animate-spin"></i>
          <span className="text-sm text-blue-700 dark:text-blue-300">
            Auto-refreshing every 30 seconds
          </span>
        </div>
        <button 
          className="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-200"
          onClick={() => window.location.reload()}
        >
          Refresh Now
        </button>
      </div>

      {/* Resource Filter */}
      <ResourceFilter
        searchTerm={searchTerm}
        selectedStatus={selectedStatus}
        selectedResourceType={selectedResourceType}
        onSearchChange={setSearchTerm}
        onStatusFilter={setSelectedStatus}
        onResourceTypeFilter={setSelectedResourceType}
      />

      {/* Quick Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Resources"
          value={allResources?.total_resources || 0}
          icon="fas fa-cube"
          color="blue"
          isLoading={resourcesLoading}
          trend={"+12%"}
        />
        <StatCard
          title="Compute Instances"
          value={allResources?.resources?.compute_instances?.length || 0}
          icon="fas fa-server"
          color="green"
          isLoading={resourcesLoading}
          trend={"+5%"}
        />
        <StatCard
          title="Databases"
          value={allResources?.resources?.databases?.length || 0}
          icon="fas fa-database"
          color="purple"
          isLoading={resourcesLoading}
          trend="+2"
        />
        <StatCard
          title="OKE Clusters"
          value={allResources?.resources?.oke_clusters?.length || 0}
          icon="fas fa-dharmachakra"
          color="orange"
          isLoading={resourcesLoading}
          trend="stable"
        />
      </div>

      {/* Real-time Metrics Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <MetricsChart
          title="Resource Health Overview"
          type="health"
          data={allResources}
          loading={resourcesLoading}
        />
        <MetricsChart
          title="Resource Distribution"
          type="distribution"
          data={allResources}
          loading={resourcesLoading}
        />
      </div>

      {/* OCI Service Status Cards */}
      {selectedCompartment && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
              OCI Services in {selectedCompartment.name}
            </h2>
            <span className="text-sm text-gray-500 dark:text-gray-400">
              {allResources?.last_updated ? 
                `Updated ${new Date(allResources.last_updated).toLocaleTimeString()}` : 
                'Loading...'
              }
            </span>
          </div>

          {resourcesLoading ? (
            <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
              {[1, 2, 3, 4, 5, 6].map(i => (
                <div key={i} className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 animate-pulse">
                  <div className="h-4 bg-gray-300 dark:bg-gray-600 rounded w-3/4 mb-2"></div>
                  <div className="h-8 bg-gray-300 dark:bg-gray-600 rounded w-1/2"></div>
                </div>
              ))}
            </div>
          ) : resourcesError ? (
            <div className="bg-yellow-50 dark:bg-yellow-900 border border-yellow-200 dark:border-yellow-700 rounded-md p-4">
              <div className="flex">
                <i className="fas fa-exclamation-triangle text-yellow-400 mr-3 mt-0.5"></i>
                <div>
                  <h3 className="text-sm font-medium text-yellow-800 dark:text-yellow-200">
                    Unable to load resources
                  </h3>
                  <p className="mt-1 text-sm text-yellow-700 dark:text-yellow-300">
                    This might be expected if OCI credentials are not configured. 
                    The dashboard is showing mock data for demonstration.
                  </p>
                </div>
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
              {/* Compute Instances */}
              <ResourceCard
                title="Compute Instances"
                icon="fas fa-server"
                color="blue"
                resources={filterResources(allResources?.resources?.compute_instances || [], 'compute_instances')}
                resourceType="compute"
              />
              
              {/* Databases */}
              <ResourceCard
                title="Database Services"
                icon="fas fa-database"
                color="purple"
                resources={filterResources(allResources?.resources?.databases || [], 'databases')}
                resourceType="database"
              />
              
              {/* OKE Clusters */}
              <ResourceCard
                title="OKE Clusters"
                icon="fas fa-dharmachakra"
                color="green"
                resources={filterResources(allResources?.resources?.oke_clusters || [], 'oke_clusters')}
                resourceType="kubernetes"
              />
              
              {/* API Gateways */}
              <ResourceCard
                title="API Gateways"
                icon="fas fa-route"
                color="orange"
                resources={filterResources(allResources?.resources?.api_gateways || [], 'api_gateways')}
                resourceType="api_gateway"
              />
              
              {/* Load Balancers */}
              <ResourceCard
                title="Load Balancers"
                icon="fas fa-balance-scale"
                color="indigo"
                resources={filterResources(allResources?.resources?.load_balancers || [], 'load_balancers')}
                resourceType="load_balancer"
              />
              
              {/* Network Security */}
              <ResourceCard
                title="Network Security"
                icon="fas fa-shield-alt"
                color="red"
                resources={[]}
                resourceType="security"
              />
            </div>
          )}
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
  trend?: string;
}

function StatCard({ title, value, icon, color, isLoading, trend }: StatCardProps) {
  const colorClasses = {
    blue: 'bg-blue-500',
    green: 'bg-green-500',
    purple: 'bg-purple-500',
    orange: 'bg-orange-500',
  };

  return (
    <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg hover:shadow-lg transition-shadow duration-200">
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
              <dd className="flex items-baseline">
                {isLoading ? (
                  <div className="h-8 flex items-center">
                    <LoadingSpinner size="sm" />
                  </div>
                ) : (
                  <>
                    <div className="text-lg font-medium text-gray-900 dark:text-white">
                      {value.toLocaleString()}
                    </div>
                    {trend && (
                      <span className="ml-2 text-sm font-medium text-green-600 dark:text-green-400">
                        {trend}
                      </span>
                    )}
                  </>
                )}
              </dd>
            </dl>
          </div>
        </div>
      </div>
    </div>
  );
} 