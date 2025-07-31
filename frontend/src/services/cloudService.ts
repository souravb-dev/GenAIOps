import { useQuery, useMutation, UseQueryResult, UseMutationResult } from '@tanstack/react-query';
import { api } from './apiClient';

// Type definitions for cloud resources
export interface Compartment {
  id: string;
  name: string;
  description: string;
  lifecycle_state: string;
}

export interface CloudResource {
  id: string;
  display_name?: string;
  name?: string;
  lifecycle_state: string;
  resource_type: string;
  compartment_id: string;
  availability_domain?: string;
  shape?: string;
  time_created?: string;
  region?: string;
}

export interface ResourceMetrics {
  resource_id: string;
  metrics: {
    cpu_utilization: number;
    memory_utilization: number;
    network_bytes_in: number;
    network_bytes_out: number;
  };
  timestamp: string;
  health_status: string;
}

export interface AllResourcesResponse {
  compartment_id: string;
  resources: {
    compute_instances: CloudResource[];
    databases: CloudResource[];
    oke_clusters: CloudResource[];
    api_gateways: CloudResource[];
    load_balancers: CloudResource[];
  };
  total_resources: number;
  last_updated: string;
}

// Query Keys
export const cloudQueryKeys = {
  all: ['cloud'] as const,
  compartments: () => [...cloudQueryKeys.all, 'compartments'] as const,
  compartment: (id: string) => [...cloudQueryKeys.all, 'compartment', id] as const,
  resources: (compartmentId: string) => [...cloudQueryKeys.compartment(compartmentId), 'resources'] as const,
  computeInstances: (compartmentId: string) => [...cloudQueryKeys.compartment(compartmentId), 'compute'] as const,
  databases: (compartmentId: string) => [...cloudQueryKeys.compartment(compartmentId), 'databases'] as const,
  okeClusters: (compartmentId: string) => [...cloudQueryKeys.compartment(compartmentId), 'oke'] as const,
  apiGateways: (compartmentId: string) => [...cloudQueryKeys.compartment(compartmentId), 'api-gateways'] as const,
  loadBalancers: (compartmentId: string) => [...cloudQueryKeys.compartment(compartmentId), 'load-balancers'] as const,
  metrics: (resourceId: string) => [...cloudQueryKeys.all, 'metrics', resourceId] as const,
};

// API Functions
const cloudApi = {
  // Get all compartments
  getCompartments: async (): Promise<Compartment[]> => {
    const response = await api.get<Compartment[]>('/cloud/compartments');
    return response.data;
  },

  // Get all resources in a compartment
  getAllResources: async (compartmentId: string, resourceFilter?: string[]): Promise<AllResourcesResponse> => {
    const params = resourceFilter ? { resource_filter: resourceFilter.join(',') } : {};
    const response = await api.get<AllResourcesResponse>(`/cloud/compartments/${compartmentId}/resources`, { params });
    return response.data;
  },

  // Get compute instances
  getComputeInstances: async (compartmentId: string): Promise<CloudResource[]> => {
    const response = await api.get<CloudResource[]>(`/cloud/compartments/${compartmentId}/compute-instances`);
    return response.data;
  },

  // Get databases
  getDatabases: async (compartmentId: string): Promise<CloudResource[]> => {
    const response = await api.get<CloudResource[]>(`/cloud/compartments/${compartmentId}/databases`);
    return response.data;
  },

  // Get OKE clusters
  getOKEClusters: async (compartmentId: string): Promise<CloudResource[]> => {
    const response = await api.get<CloudResource[]>(`/cloud/compartments/${compartmentId}/oke-clusters`);
    return response.data;
  },

  // Get API gateways
  getAPIGateways: async (compartmentId: string): Promise<CloudResource[]> => {
    const response = await api.get<CloudResource[]>(`/cloud/compartments/${compartmentId}/api-gateways`);
    return response.data;
  },

  // Get load balancers
  getLoadBalancers: async (compartmentId: string): Promise<CloudResource[]> => {
    const response = await api.get<CloudResource[]>(`/cloud/compartments/${compartmentId}/load-balancers`);
    return response.data;
  },

  // Get resource metrics
  getResourceMetrics: async (resourceId: string, resourceType: string): Promise<ResourceMetrics> => {
    const response = await api.get<ResourceMetrics>(`/cloud/resources/${resourceId}/metrics`, {
      params: { resource_type: resourceType }
    });
    return response.data;
  },

  // Execute resource action
  executeResourceAction: async (resourceId: string, action: string): Promise<any> => {
    const response = await api.post(`/cloud/resources/${resourceId}/actions/${action}`);
    return response.data;
  },
};

// React Query Hooks

// Get compartments
export function useCompartments(): UseQueryResult<Compartment[], Error> {
  return useQuery({
    queryKey: cloudQueryKeys.compartments(),
    queryFn: cloudApi.getCompartments,
    staleTime: 10 * 60 * 1000, // 10 minutes (compartments don't change often)
  });
}

// Get all resources in a compartment
export function useAllResources(
  compartmentId: string, 
  resourceFilter?: string[]
): UseQueryResult<AllResourcesResponse, Error> {
  return useQuery({
    queryKey: [...cloudQueryKeys.resources(compartmentId), resourceFilter],
    queryFn: () => cloudApi.getAllResources(compartmentId, resourceFilter),
    enabled: !!compartmentId,
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
}

// Get compute instances
export function useComputeInstances(compartmentId: string): UseQueryResult<CloudResource[], Error> {
  return useQuery({
    queryKey: cloudQueryKeys.computeInstances(compartmentId),
    queryFn: () => cloudApi.getComputeInstances(compartmentId),
    enabled: !!compartmentId,
  });
}

// Get databases
export function useDatabases(compartmentId: string): UseQueryResult<CloudResource[], Error> {
  return useQuery({
    queryKey: cloudQueryKeys.databases(compartmentId),
    queryFn: () => cloudApi.getDatabases(compartmentId),
    enabled: !!compartmentId,
  });
}

// Get OKE clusters
export function useOKEClusters(compartmentId: string): UseQueryResult<CloudResource[], Error> {
  return useQuery({
    queryKey: cloudQueryKeys.okeClusters(compartmentId),
    queryFn: () => cloudApi.getOKEClusters(compartmentId),
    enabled: !!compartmentId,
  });
}

// Get resource metrics
export function useResourceMetrics(
  resourceId: string, 
  resourceType: string
): UseQueryResult<ResourceMetrics, Error> {
  return useQuery({
    queryKey: cloudQueryKeys.metrics(resourceId),
    queryFn: () => cloudApi.getResourceMetrics(resourceId, resourceType),
    enabled: !!resourceId && !!resourceType,
    staleTime: 30 * 1000, // 30 seconds for metrics
    refetchInterval: 60 * 1000, // Refetch every minute for real-time data
  });
}

// Execute resource action mutation
export function useResourceAction(): UseMutationResult<any, Error, { resourceId: string; action: string }> {
  return useMutation({
    mutationFn: ({ resourceId, action }) => cloudApi.executeResourceAction(resourceId, action),
  });
} 