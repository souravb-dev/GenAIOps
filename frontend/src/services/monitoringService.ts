import apiClient from './apiClient';

export interface AlertSummary {
  compartment_id: string;
  total_alarms: number;
  active_alarms: number;
  severity_breakdown: Record<string, number>;
  recent_activity: any;
  top_alerts: any[];
  timestamp: string;
  health_score: number;
}

export interface Alert {
  id: string;
  name: string; // display_name from OCI
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'INFO';
  status: 'OPEN' | 'ACKNOWLEDGED' | 'RESOLVED';
  description: string; // query from OCI
  service: string; // namespace from OCI
  resource: string; // extracted from query or metric_compartment_id
  timestamp: string; // time_created from OCI
  lastUpdate: string; // time_updated from OCI
  category: string; // derived from namespace
  // OCI-specific fields for reference
  display_name?: string;
  namespace?: string;
  query?: string;
  lifecycle_state?: string;
  is_enabled?: boolean;
  metric_compartment_id?: string;
  time_created?: string;
  time_updated?: string;
}



// Legacy types for backward compatibility
export interface HealthStatus {
  compartment_id: string;
  overall_status: 'HEALTHY' | 'WARNING' | 'DEGRADED' | 'CRITICAL';
  status_color: string;
  health_score: number;
  critical_alerts: number;
  high_alerts: number;
  total_active_alarms: number;
  alert_rate_24h: number;
  last_updated: string;
}

export interface MonitoringDashboard {
  compartment_id: string;
  summary: AlertSummary;
  active_alarms: Alert[];
  recent_history: any[];
  trends: {
    total_alarms_trend: number;
    critical_alerts_trend: number;
    health_score_trend: number;
  };
  quick_stats: {
    uptime_score: number;
    performance_score: number;
    security_alerts: number;
  };
  last_updated: string;
}

class MonitoringService {
  async getAlertSummary(compartmentId: string): Promise<AlertSummary> {
    const response = await apiClient.get(`/monitoring/alerts/summary?compartment_id=${compartmentId}`);
    const summary = response.data;
    
    // Fix health score calculation (convert from 0-1 to 0-100 percentage)
    if (summary.health_score && summary.health_score > 1) {
      summary.health_score = summary.health_score / 100; // Convert if it's already in percentage
    }
    
    // Ensure health score is between 0-1
    summary.health_score = Math.min(1, Math.max(0, summary.health_score || 0.7));
    
    return summary;
  }

  async getAlarms(compartmentId: string): Promise<Alert[]> {
    const response = await apiClient.get(`/monitoring/alarms?compartment_id=${compartmentId}`);
    const rawAlarms = response.data;
    
    // Transform OCI alarm data to user-friendly format
    return rawAlarms.map((alarm: any) => ({
      id: alarm.id,
      name: alarm.display_name || 'Unnamed Alert',
      severity: alarm.severity || 'MEDIUM',
      status: alarm.is_enabled ? (alarm.lifecycle_state === 'ACTIVE' ? 'OPEN' : 'ACKNOWLEDGED') : 'RESOLVED',
      description: alarm.query || 'No monitoring query specified',
      service: alarm.namespace || 'Unknown Service',
      resource: this.extractResourceFromQuery(alarm.query) || alarm.metric_compartment_id || 'Unknown Resource',
      timestamp: alarm.time_created || new Date().toISOString(),
      lastUpdate: alarm.time_updated || alarm.time_created || new Date().toISOString(),
      category: this.deriveCategoryFromNamespace(alarm.namespace),
      // Keep OCI fields for reference
      display_name: alarm.display_name,
      namespace: alarm.namespace,
      query: alarm.query,
      lifecycle_state: alarm.lifecycle_state,
      is_enabled: alarm.is_enabled,
      metric_compartment_id: alarm.metric_compartment_id,
      time_created: alarm.time_created,
      time_updated: alarm.time_updated
    }));
  }

  private extractResourceFromQuery(query: string): string {
    if (!query) return 'Unknown Resource';
    
    // Try to extract resource name from OCI monitoring query
    const resourceMatches = query.match(/resourceDisplayName\s*=\s*"([^"]+)"/);
    if (resourceMatches) return resourceMatches[1];
    
    const idMatches = query.match(/resourceId\s*=\s*"([^"]+)"/);
    if (idMatches) return idMatches[1].split('.').pop() || idMatches[1];
    
    // Extract metric name as fallback
    const metricMatches = query.match(/(\w+)\[/);
    if (metricMatches) return `${metricMatches[1]} metrics`;
    
    return 'Resource from query';
  }

  private deriveCategoryFromNamespace(namespace: string): string {
    if (!namespace) return 'General';
    
    const ns = namespace.toLowerCase();
    if (ns.includes('database') || ns.includes('mysql') || ns.includes('oracle')) return 'Database';
    if (ns.includes('compute') || ns.includes('instance')) return 'Compute';
    if (ns.includes('network') || ns.includes('vcn') || ns.includes('load')) return 'Network';
    if (ns.includes('storage') || ns.includes('block') || ns.includes('file')) return 'Storage';
    if (ns.includes('oke') || ns.includes('kubernetes')) return 'Kubernetes';
    
    return 'Infrastructure';
  }

  async getAlarmHistory(compartmentId: string): Promise<any[]> {
    const response = await apiClient.get(`/monitoring/alarms/history?compartment_id=${compartmentId}`);
    return response.data;
  }

  async acknowledgeAlert(alertId: string): Promise<void> {
    await apiClient.post(`/monitoring/alerts/${alertId}/acknowledge`);
  }

  async resolveAlert(alertId: string, resolution: string): Promise<void> {
    await apiClient.post(`/monitoring/alerts/${alertId}/resolve`, { resolution });
  }

  async getMetrics(
    compartmentId: string,
    namespace: string,
    metricName: string,
    startTime: string,
    endTime: string
  ): Promise<any> {
    const response = await apiClient.post('/monitoring/metrics', {
      compartment_id: compartmentId,
      namespace,
      metric_name: metricName,
      start_time: startTime,
      end_time: endTime
    });
    return response.data;
  }

  async searchLogs(
    compartmentId: string,
    searchQuery: string,
    startTime: string,
    endTime: string,
    limit: number = 1000
  ): Promise<any[]> {
    const response = await apiClient.post('/monitoring/logs/search', {
      compartment_id: compartmentId,
      search_query: searchQuery,
      start_time: startTime,
      end_time: endTime,
      limit
    });
    return response.data;
  }

  async getRealTimeNotifications(
    compartmentId: string,
    severityFilter?: string,
    hoursBack: number = 24
  ): Promise<any[]> {
    const params = new URLSearchParams({
      compartment_id: compartmentId,
      hours_back: hoursBack.toString()
    });
    
    if (severityFilter) {
      params.append('severity_filter', severityFilter);
    }

    const response = await apiClient.get(`/notifications/real-time?${params}`);
    return response.data;
  }

  // Legacy methods for backward compatibility
  async testIntegration(compartmentId?: string): Promise<any> {
    const testCompartmentId = compartmentId || 'test-compartment';
    const summary = await this.getAlertSummary(testCompartmentId);
    return {
      status: 'success',
      monitoring_available: true,
      test_summary: summary,
      timestamp: new Date().toISOString(),
      compartment_id: testCompartmentId
    };
  }

  async getHealthStatus(compartmentId: string): Promise<HealthStatus> {
    const summary = await this.getAlertSummary(compartmentId);
    return {
      compartment_id: compartmentId,
      overall_status: summary.severity_breakdown.CRITICAL > 0 ? 'CRITICAL' : 
                     summary.severity_breakdown.HIGH > 0 ? 'WARNING' : 'HEALTHY',
      status_color: summary.severity_breakdown.CRITICAL > 0 ? 'red' : 
                   summary.severity_breakdown.HIGH > 0 ? 'yellow' : 'green',
      health_score: summary.health_score,
      critical_alerts: summary.severity_breakdown.CRITICAL || 0,
      high_alerts: summary.severity_breakdown.HIGH || 0,
      total_active_alarms: summary.active_alarms,
      alert_rate_24h: 0, // Placeholder
      last_updated: summary.timestamp
    };
  }

  async getDashboard(compartmentId: string): Promise<MonitoringDashboard> {
    const summary = await this.getAlertSummary(compartmentId);
    const alarms = await this.getAlarms(compartmentId);
    const history = await this.getAlarmHistory(compartmentId);
    
    return {
      compartment_id: compartmentId,
      summary: summary,
      active_alarms: alarms,
      recent_history: history,
      trends: {
        total_alarms_trend: 0,
        critical_alerts_trend: 0,
        health_score_trend: 0
      },
      quick_stats: {
        uptime_score: 95,
        performance_score: 90,
        security_alerts: summary.severity_breakdown.HIGH || 0
      },
      last_updated: summary.timestamp
    };
  }
}

export const monitoringService = new MonitoringService(); 
export default monitoringService; 