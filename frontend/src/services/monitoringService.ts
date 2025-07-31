import { api } from './apiClient';

// Types for monitoring data
export interface AlertSummary {
  compartment_id: string;
  total_alarms: number;
  active_alarms: number;
  severity_breakdown: {
    CRITICAL: number;
    HIGH: number;
    MEDIUM: number;
    LOW: number;
    INFO: number;
  };
  recent_activity: {
    last_24h_alerts: number;
    resolved_alerts: number;
    alert_rate: number;
  };
  top_alerts: Array<{
    id: string;
    display_name: string;
    severity: string;
    lifecycle_state: string;
    is_enabled: boolean;
  }>;
  timestamp: string;
  health_score: number;
}

export interface Alarm {
  id: string;
  display_name: string;
  severity: string;
  lifecycle_state: string;
  is_enabled: boolean;
  metric_compartment_id: string;
  namespace: string;
  query: string;
  rule_name: string;
  time_created: string;
  time_updated: string;
}

export interface AlarmHistory {
  alarm_id: string;
  alarm_name?: string;
  status: string;
  timestamp: string;
  summary: string;
  suppressed: boolean;
}

export interface MetricsData {
  namespace: string;
  metric_name: string;
  compartment_id: string;
  data_points: Array<{
    timestamp: string;
    value: number;
  }>;
  start_time: string;
  end_time: string;
}

export interface LogEntry {
  id: string;
  timestamp: string;
  message: any;
  source: string;
  compartment_id: string;
  log_group_id: string;
  fields: any;
}

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
  active_alarms: Alarm[];
  recent_history: AlarmHistory[];
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

// Request types
export interface MetricsRequest {
  namespace: string;
  metric_name: string;
  start_time: string;
  end_time: string;
  resource_group?: string;
}

export interface LogSearchRequest {
  search_query: string;
  start_time: string;
  end_time: string;
  limit?: number;
}

class MonitoringService {
  private baseUrl = '/monitoring';

  /**
   * Get comprehensive alert summary for a compartment
   */
  async getAlertSummary(compartmentId: string): Promise<AlertSummary> {
    const response = await api.get<AlertSummary>(`${this.baseUrl}/alerts/summary`, {
      params: { compartment_id: compartmentId }
    });
    return response.data;
  }

  /**
   * Get current alarm status from OCI Monitoring
   */
  async getAlarms(compartmentId: string): Promise<Alarm[]> {
    const response = await api.get<Alarm[]>(`${this.baseUrl}/alarms`, {
      params: { compartment_id: compartmentId }
    });
    return response.data;
  }

  /**
   * Get alarm history from OCI Monitoring
   */
  async getAlarmHistory(compartmentId: string, hoursBack: number = 24): Promise<AlarmHistory[]> {
    const response = await api.get<AlarmHistory[]>(`${this.baseUrl}/alarms/history`, {
      params: { 
        compartment_id: compartmentId,
        hours_back: hoursBack
      }
    });
    return response.data;
  }

  /**
   * Get metrics data from OCI Monitoring
   */
  async getMetricsData(compartmentId: string, request: MetricsRequest): Promise<MetricsData> {
    const response = await api.post<MetricsData>(`${this.baseUrl}/metrics`, request, {
      params: { compartment_id: compartmentId }
    });
    return response.data;
  }

  /**
   * Get available metric namespaces
   */
  async getMetricNamespaces(compartmentId: string): Promise<string[]> {
    const response = await api.get<string[]>(`${this.baseUrl}/metrics/namespaces`, {
      params: { compartment_id: compartmentId }
    });
    return response.data;
  }

  /**
   * Search logs using OCI Log Search API
   */
  async searchLogs(compartmentId: string, request: LogSearchRequest): Promise<LogEntry[]> {
    const response = await api.post<LogEntry[]>(`${this.baseUrl}/logs/search`, request, {
      params: { compartment_id: compartmentId }
    });
    return response.data;
  }

  /**
   * Get overall monitoring health status
   */
  async getHealthStatus(compartmentId: string): Promise<HealthStatus> {
    const response = await api.get<HealthStatus>(`${this.baseUrl}/health`, {
      params: { compartment_id: compartmentId }
    });
    return response.data;
  }

  /**
   * Get comprehensive monitoring dashboard data
   */
  async getDashboard(compartmentId: string): Promise<MonitoringDashboard> {
    const response = await api.get<MonitoringDashboard>(`${this.baseUrl}/dashboard`, {
      params: { compartment_id: compartmentId }
    });
    return response.data;
  }

  /**
   * Test monitoring integration
   */
  async testIntegration(compartmentId?: string): Promise<any> {
    // If no compartment ID provided, use the hardcoded test compartment
    const testCompartmentId = compartmentId || 'test-compartment';
    
    // Use the same alert summary endpoint as other components for consistency
    const summary = await this.getAlertSummary(testCompartmentId);
    
    return {
      status: 'success',
      monitoring_available: true,
      test_summary: summary,
      timestamp: new Date().toISOString(),
      compartment_id: testCompartmentId
    };
  }
}

// Export singleton instance
export const monitoringService = new MonitoringService();
export default monitoringService; 