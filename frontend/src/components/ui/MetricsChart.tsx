import React from 'react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { LoadingSpinner } from './LoadingSpinner';
import { AllResourcesResponse } from '../../services/cloudService';

interface MetricsChartProps {
  title: string;
  type: 'health' | 'distribution';
  data: AllResourcesResponse | null | undefined;
  loading: boolean;
}

export function MetricsChart({ title, type, data, loading }: MetricsChartProps) {
  if (loading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">{title}</h3>
        <div className="h-64 flex items-center justify-center">
          <LoadingSpinner size="lg" message="Loading metrics..." />
        </div>
      </div>
    );
  }

  if (!data || !data.resources) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">{title}</h3>
        <div className="h-64 flex items-center justify-center">
          <div className="text-center text-gray-500 dark:text-gray-400">
            <i className="fas fa-chart-pie text-4xl mb-2"></i>
            <p>No data available</p>
          </div>
        </div>
      </div>
    );
  }

  const generateHealthData = () => {
    const allResources = Object.values(data.resources).flat();
    const healthyCount = allResources.filter(r => r.lifecycle_state === 'ACTIVE' || r.lifecycle_state === 'RUNNING' || r.lifecycle_state === 'AVAILABLE').length;
    const stoppedCount = allResources.filter(r => r.lifecycle_state === 'STOPPED' || r.lifecycle_state === 'INACTIVE').length;
    const errorCount = allResources.filter(r => r.lifecycle_state === 'FAILED' || r.lifecycle_state === 'ERROR').length;
    const otherCount = allResources.length - healthyCount - stoppedCount - errorCount;

    const healthData = [];
    if (healthyCount > 0) healthData.push({ name: 'Healthy', value: healthyCount, color: '#10B981' });
    if (stoppedCount > 0) healthData.push({ name: 'Stopped', value: stoppedCount, color: '#F59E0B' });
    if (errorCount > 0) healthData.push({ name: 'Error', value: errorCount, color: '#EF4444' });
    if (otherCount > 0) healthData.push({ name: 'Other', value: otherCount, color: '#6B7280' });

    return healthData;
  };

  const generateDistributionData = () => {
    return Object.entries(data.resources).map(([type, resources]) => ({
      name: type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
      count: resources.length,
      healthy: resources.filter(r => r.lifecycle_state === 'ACTIVE' || r.lifecycle_state === 'RUNNING' || r.lifecycle_state === 'AVAILABLE').length,
      stopped: resources.filter(r => r.lifecycle_state === 'STOPPED' || r.lifecycle_state === 'INACTIVE').length,
      error: resources.filter(r => r.lifecycle_state === 'FAILED' || r.lifecycle_state === 'ERROR').length,
    }));
  };

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-lg shadow-lg p-3">
          <p className="text-sm font-medium text-gray-900 dark:text-white">{label}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              {entry.name}: {entry.value}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  const renderHealthChart = () => {
    const healthData = generateHealthData();
    
    if (healthData.length === 0) {
      return (
        <div className="h-64 flex items-center justify-center">
          <div className="text-center text-gray-500 dark:text-gray-400">
            <i className="fas fa-heartbeat text-4xl mb-2"></i>
            <p>No health data available</p>
          </div>
        </div>
      );
    }

    return (
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={healthData}
            cx="50%"
            cy="50%"
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
            label={({ name, value, percent }) => `${name} ${value} (${((percent || 0) * 100).toFixed(0)}%)`}
          >
            {healthData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    );
  };

  const renderDistributionChart = () => {
    const distributionData = generateDistributionData();
    
    if (distributionData.length === 0) {
      return (
        <div className="h-64 flex items-center justify-center">
          <div className="text-center text-gray-500 dark:text-gray-400">
            <i className="fas fa-chart-bar text-4xl mb-2"></i>
            <p>No distribution data available</p>
          </div>
        </div>
      );
    }

    return (
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={distributionData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis 
            dataKey="name" 
            stroke="#6B7280"
            fontSize={12}
            angle={-45}
            textAnchor="end"
            height={80}
          />
          <YAxis stroke="#6B7280" />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          <Bar dataKey="healthy" stackId="a" fill="#10B981" name="Healthy" />
          <Bar dataKey="stopped" stackId="a" fill="#F59E0B" name="Stopped" />
          <Bar dataKey="error" stackId="a" fill="#EF4444" name="Error" />
        </BarChart>
      </ResponsiveContainer>
    );
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white">{title}</h3>
        <div className="text-sm text-gray-500 dark:text-gray-400">
          Total: {data.total_resources} resources
        </div>
      </div>
      
      {type === 'health' ? renderHealthChart() : renderDistributionChart()}
      
      <div className="mt-4 text-xs text-gray-500 dark:text-gray-400 text-center">
        Last updated: {new Date(data.last_updated).toLocaleString()}
      </div>
    </div>
  );
} 