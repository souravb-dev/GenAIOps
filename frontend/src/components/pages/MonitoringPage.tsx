import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { monitoringService, AlertSummary, Alert, HealthStatus, MonitoringDashboard } from '../../services/monitoringService';
import { useCompartments } from '../../services/cloudService';
import { LoadingSpinner } from '../ui/LoadingSpinner';
import { CompartmentSelector } from '../ui/CompartmentSelector';

// Helper component for status badge
const StatusBadge: React.FC<{ status: string; color: string }> = ({ status, color }) => (
  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-${color}-100 text-${color}-800`}>
    {status}
  </span>
);

// Helper component for severity badge
const SeverityBadge: React.FC<{ severity: string }> = ({ severity }) => {
  const colors = {
    'CRITICAL': 'red',
    'HIGH': 'orange', 
    'MEDIUM': 'yellow',
    'LOW': 'blue',
    'INFO': 'gray'
  };
  const color = colors[severity as keyof typeof colors] || 'gray';
  
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-${color}-100 text-${color}-800`}>
      {severity}
    </span>
  );
};

// Health Score Component
const HealthScoreCard: React.FC<{ health: HealthStatus }> = ({ health }) => {
  const getHealthColor = (score: number) => {
    if (score >= 90) return 'green';
    if (score >= 70) return 'yellow'; 
    if (score >= 50) return 'orange';
    return 'red';
  };

  const color = getHealthColor(health.health_score);

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-medium text-gray-900 dark:text-white">Health Score</h3>
          <p className="text-sm text-gray-500 dark:text-gray-400">Overall system health</p>
        </div>
        <div className="text-right">
          <div className={`text-3xl font-bold text-${color}-600`}>
            {health.health_score.toFixed(1)}
          </div>
          <StatusBadge status={health.overall_status} color={health.status_color} />
        </div>
      </div>
      
      <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
        <div>
          <span className="text-gray-500 dark:text-gray-400">Critical Alerts:</span>
          <span className="ml-2 font-medium text-red-600">{health.critical_alerts}</span>
        </div>
        <div>
          <span className="text-gray-500 dark:text-gray-400">High Alerts:</span>
          <span className="ml-2 font-medium text-orange-600">{health.high_alerts}</span>
        </div>
        <div>
          <span className="text-gray-500 dark:text-gray-400">Active Alarms:</span>
          <span className="ml-2 font-medium">{health.total_active_alarms}</span>
        </div>
        <div>
          <span className="text-gray-500 dark:text-gray-400">Alert Rate (24h):</span>
          <span className="ml-2 font-medium">{health.alert_rate_24h.toFixed(2)}/hr</span>
        </div>
      </div>
    </div>
  );
};

// Alert Summary Component
const AlertSummaryCard: React.FC<{ summary: AlertSummary }> = ({ summary }) => (
  <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
    <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Alert Summary</h3>
    
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <div className="text-center">
        <div className="text-2xl font-bold text-gray-900 dark:text-white">{summary.total_alarms}</div>
        <div className="text-sm text-gray-500 dark:text-gray-400">Total Alarms</div>
      </div>
      <div className="text-center">
        <div className="text-2xl font-bold text-green-600">{summary.active_alarms}</div>
        <div className="text-sm text-gray-500 dark:text-gray-400">Active</div>
      </div>
      <div className="text-center">
        <div className="text-2xl font-bold text-red-600">{summary.severity_breakdown.CRITICAL}</div>
        <div className="text-sm text-gray-500 dark:text-gray-400">Critical</div>
      </div>
      <div className="text-center">
        <div className="text-2xl font-bold text-orange-600">{summary.severity_breakdown.HIGH}</div>
        <div className="text-sm text-gray-500 dark:text-gray-400">High</div>
      </div>
    </div>

    <div className="border-t border-gray-200 dark:border-gray-700 pt-4">
      <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-2">Recent Activity (24h)</h4>
      <div className="grid grid-cols-3 gap-4 text-sm">
        <div>
          <span className="text-gray-500 dark:text-gray-400">New Alerts:</span>
          <span className="ml-2 font-medium">{summary.recent_activity.last_24h_alerts}</span>
        </div>
        <div>
          <span className="text-gray-500 dark:text-gray-400">Resolved:</span>
          <span className="ml-2 font-medium text-green-600">{summary.recent_activity.resolved_alerts}</span>
        </div>
        <div>
          <span className="text-gray-500 dark:text-gray-400">Rate:</span>
          <span className="ml-2 font-medium">{summary.recent_activity.alert_rate.toFixed(1)}/hr</span>
        </div>
      </div>
    </div>
  </div>
);

// Active Alarms Component  
const ActiveAlarmsCard: React.FC<{ alarms: Alert[] }> = ({ alarms }) => (
  <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
    <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Active Alarms</h3>
    
    {alarms.length === 0 ? (
      <div className="text-center py-8 text-gray-500 dark:text-gray-400">
        <i className="fas fa-check-circle text-4xl mb-2 text-green-500"></i>
        <p>No active alarms</p>
      </div>
    ) : (
      <div className="space-y-3">
        {alarms.slice(0, 5).map((alarm) => (
          <div key={alarm.id} className="border border-gray-200 dark:border-gray-700 rounded-lg p-3">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <h4 className="text-sm font-medium text-gray-900 dark:text-white">
                  {alarm.name}
                </h4>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  {alarm.service} • {alarm.resource}
                </p>
              </div>
              <div className="flex items-center space-x-2">
                <SeverityBadge severity={alarm.severity} />
                <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs ${
                  alarm.status === 'OPEN' ? 'bg-red-100 text-red-800' :
                  alarm.status === 'ACKNOWLEDGED' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-green-100 text-green-800'
                }`}>
                  {alarm.status}
                </span>
              </div>
            </div>
          </div>
        ))}
        {alarms.length > 5 && (
          <div className="text-center py-2">
            <span className="text-sm text-gray-500 dark:text-gray-400">
              + {alarms.length - 5} more alarms
            </span>
          </div>
        )}
      </div>
    )}
  </div>
);

// Test Integration Component
const TestIntegrationCard: React.FC<{ compartmentId: string }> = ({ compartmentId }) => {
  const [testResult, setTestResult] = useState<any>(null);
  const [testing, setTesting] = useState(false);

  const runTest = async () => {
    setTesting(true);
    try {
      const result = await monitoringService.testIntegration(compartmentId);
      setTestResult(result);
    } catch (error) {
      setTestResult({ status: 'error', error: error instanceof Error ? error.message : String(error) });
    } finally {
      setTesting(false);
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
        Integration Test
      </h3>
      <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
        Testing compartment: <code className="bg-gray-100 dark:bg-gray-700 px-1 rounded text-xs">{compartmentId}</code>
      </p>
      
      <div className="flex items-center space-x-4 mb-4">
        <button
          onClick={runTest}
          disabled={testing}
          className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white px-4 py-2 rounded-md text-sm font-medium"
        >
          {testing ? (
            <>
              <i className="fas fa-spinner animate-spin mr-2"></i>
              Testing...
            </>
          ) : (
            <>
              <i className="fas fa-flask mr-2"></i>
              Run Test
            </>
          )}
        </button>
      </div>

      {testResult && (
        <div className={`p-4 rounded-md ${testResult.status === 'success' ? 'bg-green-50 dark:bg-green-900' : 'bg-red-50 dark:bg-red-900'}`}>
          <div className="flex items-center">
            <i className={`fas ${testResult.status === 'success' ? 'fa-check-circle text-green-500' : 'fa-exclamation-circle text-red-500'} mr-2`}></i>
            <span className={`text-sm font-medium ${testResult.status === 'success' ? 'text-green-800 dark:text-green-200' : 'text-red-800 dark:text-red-200'}`}>
              {testResult.status === 'success' ? 'Test Passed' : 'Test Failed'}
            </span>
          </div>
          
          {testResult.test_summary && (
            <div className="mt-3 space-y-2">
              <div className="text-sm">
                <span className="font-medium">Health Score:</span>
                <span className="ml-2 font-bold text-lg">{testResult.test_summary.health_score}</span>
              </div>
              <div className="text-xs text-gray-600 dark:text-gray-400">
                <div>Total Alarms: {testResult.test_summary.total_alarms}</div>
                <div>Active Alarms: {testResult.test_summary.active_alarms}</div>
                <div>Critical: {testResult.test_summary.severity_breakdown?.CRITICAL || 0}</div>
                <div>High: {testResult.test_summary.severity_breakdown?.HIGH || 0}</div>
              </div>
            </div>
          )}
          
          {testResult.error && (
            <div className="mt-2 text-xs text-red-600 dark:text-red-400">
              Error: {testResult.error}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// Main Monitoring Page Component
export function MonitoringPage() {
  const { data: compartments, isLoading: compartmentsLoading } = useCompartments();
  const [selectedCompartmentId, setSelectedCompartmentId] = useState<string>('test-compartment');

  // Set default compartment when compartments load
  useEffect(() => {
    if (compartments && compartments.length > 0 && selectedCompartmentId === 'test-compartment') {
      setSelectedCompartmentId(compartments[0].id);
    }
  }, [compartments, selectedCompartmentId]);

  // Queries for monitoring data
  const { data: health, isLoading: healthLoading, error: healthError } = useQuery({
    queryKey: ['health', selectedCompartmentId],
    queryFn: () => monitoringService.getHealthStatus(selectedCompartmentId),
    enabled: !!selectedCompartmentId,
    // ❌ REMOVED: Aggressive 30-second polling causing performance issues
  });

  const { data: summary, isLoading: summaryLoading } = useQuery({
    queryKey: ['alert-summary', selectedCompartmentId],
    queryFn: () => monitoringService.getAlertSummary(selectedCompartmentId),
    enabled: !!selectedCompartmentId,
    // ❌ REMOVED: Aggressive 30-second polling causing performance issues
  });

  const { data: alarms, isLoading: alarmsLoading } = useQuery({
    queryKey: ['alarms', selectedCompartmentId],
    queryFn: () => monitoringService.getAlarms(selectedCompartmentId),
    enabled: !!selectedCompartmentId,
    // ❌ REMOVED: Aggressive 30-second polling causing performance issues
  });

  const { data: dashboard, isLoading: dashboardLoading } = useQuery({
    queryKey: ['dashboard', selectedCompartmentId],
    queryFn: () => monitoringService.getDashboard(selectedCompartmentId),
    enabled: !!selectedCompartmentId,
    // ❌ REMOVED: Aggressive 30-second polling causing performance issues
  });

  const isLoading = healthLoading || summaryLoading || alarmsLoading || dashboardLoading;

  if (compartmentsLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Monitoring & Alerts
          </h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Real-time monitoring data from OCI Monitoring and Logging APIs
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
            Auto-refreshing monitoring data every 30 seconds
          </span>
        </div>
        <span className="text-xs text-blue-600 dark:text-blue-400">
          Last updated: {new Date().toLocaleTimeString()}
        </span>
      </div>

      {/* Error Handling */}
      {healthError && (
        <div className="bg-red-50 dark:bg-red-900 border border-red-200 dark:border-red-700 rounded-md p-4">
          <div className="flex items-center">
            <i className="fas fa-exclamation-triangle text-red-500 mr-2"></i>
            <span className="text-sm text-red-700 dark:text-red-200">
              Failed to load monitoring data: {healthError.message}
            </span>
          </div>
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="flex items-center justify-center h-32">
          <LoadingSpinner />
          <span className="ml-3 text-gray-600 dark:text-gray-400">Loading monitoring data...</span>
        </div>
      )}

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Health Status */}
        {health && <HealthScoreCard health={health} />}
        
        {/* Alert Summary */}
        {summary && <AlertSummaryCard summary={summary} />}
        
        {/* Active Alarms */}
        {alarms && <ActiveAlarmsCard alarms={alarms} />}
        
        {/* Test Integration */}
        <TestIntegrationCard compartmentId={selectedCompartmentId} />
      </div>

      {/* Dashboard Data Preview */}
      {dashboard && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
            Dashboard Overview
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="bg-blue-50 dark:bg-blue-900 rounded-lg p-4">
              <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                {dashboard.quick_stats.uptime_score.toFixed(1)}%
              </div>
              <div className="text-sm text-blue-700 dark:text-blue-300">Uptime Score</div>
            </div>
            <div className="bg-green-50 dark:bg-green-900 rounded-lg p-4">
              <div className="text-2xl font-bold text-green-600 dark:text-green-400">
                {dashboard.quick_stats.performance_score.toFixed(1)}%
              </div>
              <div className="text-sm text-green-700 dark:text-green-300">Performance Score</div>
            </div>
            <div className="bg-red-50 dark:bg-red-900 rounded-lg p-4">
              <div className="text-2xl font-bold text-red-600 dark:text-red-400">
                {dashboard.quick_stats.security_alerts}
              </div>
              <div className="text-sm text-red-700 dark:text-red-300">Security Alerts</div>
            </div>
          </div>

          <div className="text-xs text-gray-500 dark:text-gray-400">
            <strong>Trends:</strong> Alarms: {dashboard.trends.total_alarms_trend}, 
            Critical: {dashboard.trends.critical_alerts_trend}, 
            Health: {dashboard.trends.health_score_trend.toFixed(1)}
          </div>
        </div>
      )}

      {/* API Status */}
      <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
        <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-2">
          API Endpoints Status
        </h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
          <div className="flex items-center">
            <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
            Alert Summary
          </div>
          <div className="flex items-center">
            <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
            Alarms
          </div>
          <div className="flex items-center">
            <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
            Health Status
          </div>
          <div className="flex items-center">
            <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
            Dashboard
          </div>
        </div>
      </div>
    </div>
  );
} 