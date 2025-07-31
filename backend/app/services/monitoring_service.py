import asyncio
import logging
import oci
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import json

from app.core.exceptions import ExternalServiceError
from app.services.cloud_service import oci_service

logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    """Alert severity levels"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH" 
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"

class AlertStatus(Enum):
    """Alert status types"""
    OPEN = "OPEN"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVED = "RESOLVED"
    SUPPRESSED = "SUPPRESSED"

@dataclass
class OCIAlert:
    """Data class for OCI alert information"""
    id: str
    title: str
    description: str
    severity: AlertSeverity
    status: AlertStatus
    timestamp: datetime
    compartment_id: str
    resource_id: Optional[str] = None
    resource_type: Optional[str] = None
    metric_name: Optional[str] = None
    threshold_value: Optional[float] = None
    current_value: Optional[float] = None
    namespace: Optional[str] = None
    dimensions: Optional[Dict[str, str]] = None

@dataclass
class LogEntry:
    """Data class for log entry information"""
    id: str
    timestamp: datetime
    level: str
    message: str
    source: str
    compartment_id: str
    resource_id: Optional[str] = None
    log_group_id: Optional[str] = None
    fields: Optional[Dict[str, Any]] = None

class MonitoringService:
    """OCI Monitoring and Alerting Integration Service"""
    
    def __init__(self):
        self.oci_service = oci_service
        self.cache_ttl = 300  # 5 minutes default cache
        
    def _get_monitoring_client(self):
        """Get OCI monitoring client"""
        if not self.oci_service.oci_available:
            raise ExternalServiceError("OCI service not available")
        return self.oci_service.clients.get('monitoring')
    
    def _get_logging_client(self):
        """Get OCI logging management client"""
        if not self.oci_service.oci_available:
            raise ExternalServiceError("OCI service not available")
        return self.oci_service.clients.get('logging')
    
    def _get_log_search_client(self):
        """Get OCI log search client"""
        if not self.oci_service.oci_available:
            raise ExternalServiceError("OCI service not available")
        return self.oci_service.clients.get('log_search')

    async def get_alarm_status(self, compartment_id: str) -> List[Dict[str, Any]]:
        """Get alarm status from OCI Monitoring"""
        try:
            cache_key = f"alarm_status_{compartment_id}"
            cached_data = self.oci_service.cache.get(cache_key)
            if cached_data:
                logger.info(f"🔄 Using cached alarm status for compartment {compartment_id}")
                return cached_data

            if not self.oci_service.oci_available:
                logger.warning("⚠️ OCI not available, returning mock alarm data")
                return self._get_mock_alarm_data(compartment_id)

            monitoring_client = self._get_monitoring_client()
            
            # Get alarm status
            response = await self.oci_service._make_oci_call(
                monitoring_client.list_alarms,
                compartment_id=compartment_id,
                lifecycle_state=oci.monitoring.models.Alarm.LIFECYCLE_STATE_ACTIVE
            )
            
            alarms = []
            for alarm in response.data:
                alarm_data = {
                    "id": alarm.id,
                    "display_name": alarm.display_name,
                    "severity": alarm.severity or "MEDIUM",
                    "lifecycle_state": alarm.lifecycle_state,
                    "is_enabled": alarm.is_enabled,
                    "metric_compartment_id": alarm.metric_compartment_id,
                    "namespace": alarm.namespace,
                    "query": alarm.query,
                    "rule_name": getattr(alarm, 'rule_name', ''),
                    "time_created": alarm.time_created.isoformat() if alarm.time_created else None,
                    "time_updated": alarm.time_updated.isoformat() if alarm.time_updated else None
                }
                alarms.append(alarm_data)
            
            # Cache the results
            self.oci_service.cache.set(cache_key, alarms, self.cache_ttl)
            logger.info(f"✅ Retrieved {len(alarms)} alarms for compartment {compartment_id}")
            return alarms
            
        except Exception as e:
            logger.error(f"❌ Failed to get alarm status: {e}")
            return self._get_mock_alarm_data(compartment_id)

    async def get_alarm_history(self, compartment_id: str, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Get alarm history from OCI Monitoring"""
        try:
            cache_key = f"alarm_history_{compartment_id}_{start_time.isoformat()}_{end_time.isoformat()}"
            cached_data = self.oci_service.cache.get(cache_key)
            if cached_data:
                return cached_data

            if not self.oci_service.oci_available:
                return self._get_mock_alarm_history(compartment_id)

            monitoring_client = self._get_monitoring_client()
            
            # Get alarm history - using list_alarms and check timestamps
            response = await self.oci_service._make_oci_call(
                monitoring_client.list_alarms,
                compartment_id=compartment_id,
                lifecycle_state=oci.monitoring.models.Alarm.LIFECYCLE_STATE_ACTIVE
            )
            
            history = []
            for alarm in response.data:
                # Filter alarms updated within the time range
                if alarm.time_updated and start_time <= alarm.time_updated <= end_time:
                    history_entry = {
                        "alarm_id": alarm.id,
                        "alarm_name": alarm.display_name,
                        "status": "ACTIVE" if alarm.is_enabled else "DISABLED",
                        "timestamp": alarm.time_updated.isoformat() if alarm.time_updated else None,
                        "summary": f"Alarm {alarm.display_name} - {alarm.severity}",
                        "suppressed": not alarm.is_enabled
                    }
                    history.append(history_entry)
            
            # Cache the results
            self.oci_service.cache.set(cache_key, history, self.cache_ttl)
            logger.info(f"✅ Retrieved {len(history)} alarm history entries")
            return history
            
        except Exception as e:
            logger.error(f"❌ Failed to get alarm history: {e}")
            return self._get_mock_alarm_history(compartment_id)

    async def get_metrics_data(self, compartment_id: str, namespace: str, metric_name: str, 
                              start_time: datetime, end_time: datetime, 
                              resource_group: Optional[str] = None) -> Dict[str, Any]:
        """Get metrics data from OCI Monitoring"""
        try:
            cache_key = f"metrics_{compartment_id}_{namespace}_{metric_name}_{start_time.isoformat()}"
            cached_data = self.oci_service.cache.get(cache_key)
            if cached_data:
                return cached_data

            if not self.oci_service.oci_available:
                return self._get_mock_metrics_data(namespace, metric_name)

            monitoring_client = self._get_monitoring_client()
            
            # Build query
            query = f"'{metric_name}'[1m].mean()"
            if resource_group:
                query = f"'{metric_name}'[1m]{{resourceGroup=\"{resource_group}\"}}.mean()"
            
            # Get metrics data
            metrics_request = oci.monitoring.models.SummarizeMetricsDataDetails(
                namespace=namespace,
                query=query,
                compartment_id=compartment_id,
                start_time=start_time,
                end_time=end_time,
                resolution="1m"
            )
            
            response = await self.oci_service._make_oci_call(
                monitoring_client.summarize_metrics_data,
                summarize_metrics_data_details=metrics_request
            )
            
            metrics_data = {
                "namespace": namespace,
                "metric_name": metric_name,
                "compartment_id": compartment_id,
                "data_points": [],
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat()
            }
            
            for metric in response.data:
                for data_point in metric.aggregated_datapoints:
                    metrics_data["data_points"].append({
                        "timestamp": data_point.timestamp.isoformat(),
                        "value": data_point.value
                    })
            
            # Cache the results
            self.oci_service.cache.set(cache_key, metrics_data, self.cache_ttl)
            logger.info(f"✅ Retrieved {len(metrics_data['data_points'])} metrics data points")
            return metrics_data
            
        except Exception as e:
            logger.error(f"❌ Failed to get metrics data: {e}")
            return self._get_mock_metrics_data(namespace, metric_name)

    async def search_logs(self, compartment_id: str, search_query: str, 
                         start_time: datetime, end_time: datetime, 
                         limit: int = 1000) -> List[Dict[str, Any]]:
        """Search logs using OCI Log Search API"""
        try:
            cache_key = f"logs_{compartment_id}_{hash(search_query)}_{start_time.isoformat()}"
            cached_data = self.oci_service.cache.get(cache_key)
            if cached_data:
                return cached_data

            if not self.oci_service.oci_available:
                return self._get_mock_logs_data(compartment_id)

            log_search_client = self._get_log_search_client()
            
            # Search logs
            search_request = oci.loggingsearch.models.SearchLogsDetails(
                time_start=start_time,
                time_end=end_time,
                search_query=search_query,
                is_return_field_info=True
            )
            
            response = await self.oci_service._make_oci_call(
                log_search_client.search_logs,
                search_logs_details=search_request,
                limit=limit
            )
            
            logs = []
            for log_entry in response.data.results:
                log_data = {
                    "id": getattr(log_entry.data, 'id', ''),
                    "timestamp": getattr(log_entry.data, 'datetime', ''),
                    "message": getattr(log_entry.data, 'logContent', {}),
                    "source": getattr(log_entry.data, 'source', ''),
                    "compartment_id": compartment_id,
                    "log_group_id": getattr(log_entry.data, 'logGroup', ''),
                    "fields": log_entry.data.__dict__ if hasattr(log_entry.data, '__dict__') else {}
                }
                logs.append(log_data)
            
            # Cache the results
            self.oci_service.cache.set(cache_key, logs, self.cache_ttl)
            logger.info(f"✅ Retrieved {len(logs)} log entries")
            return logs
            
        except Exception as e:
            logger.error(f"❌ Failed to search logs: {e}")
            return self._get_mock_logs_data(compartment_id)

    async def get_alert_summary(self, compartment_id: str) -> Dict[str, Any]:
        """Get comprehensive alert summary for a compartment"""
        try:
            # Get current alarms
            alarms = await self.get_alarm_status(compartment_id)
            
            # Get recent alarm history (last 24 hours)
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=24)
            history = await self.get_alarm_history(compartment_id, start_time, end_time)
            
            # Classify alerts by severity
            severity_counts = {
                "CRITICAL": 0,
                "HIGH": 0,
                "MEDIUM": 0,
                "LOW": 0,
                "INFO": 0
            }
            
            active_alarms = []
            for alarm in alarms:
                if alarm.get("is_enabled") and alarm.get("lifecycle_state") == "ACTIVE":
                    severity = alarm.get("severity", "MEDIUM")
                    severity_counts[severity] = severity_counts.get(severity, 0) + 1
                    active_alarms.append(alarm)
            
            # Calculate trends
            recent_alerts = len([h for h in history if h.get("status") == "FIRING"])
            resolved_alerts = len([h for h in history if h.get("status") == "OK"])
            
            summary = {
                "compartment_id": compartment_id,
                "total_alarms": len(alarms),
                "active_alarms": len(active_alarms),
                "severity_breakdown": severity_counts,
                "recent_activity": {
                    "last_24h_alerts": recent_alerts,
                    "resolved_alerts": resolved_alerts,
                    "alert_rate": recent_alerts / 24 if recent_alerts > 0 else 0
                },
                "top_alerts": active_alarms[:5],  # Top 5 active alarms
                "timestamp": datetime.utcnow().isoformat(),
                "health_score": self._calculate_health_score(severity_counts, recent_alerts)
            }
            
            logger.info(f"✅ Generated alert summary for compartment {compartment_id}")
            return summary
            
        except Exception as e:
            logger.error(f"❌ Failed to generate alert summary: {e}")
            raise ExternalServiceError("Unable to generate alert summary")

    def _calculate_health_score(self, severity_counts: Dict[str, int], recent_alerts: int) -> float:
        """Calculate a health score based on alert severity and frequency"""
        try:
            # Base score starts at 100
            score = 100.0
            
            # Deduct points based on severity
            score -= severity_counts.get("CRITICAL", 0) * 20
            score -= severity_counts.get("HIGH", 0) * 10
            score -= severity_counts.get("MEDIUM", 0) * 5
            score -= severity_counts.get("LOW", 0) * 2
            
            # Deduct points for high alert frequency
            if recent_alerts > 10:
                score -= (recent_alerts - 10) * 2
            
            # Ensure score doesn't go below 0
            calculated_score = max(0.0, score)
            
            # Log for debugging consistency
            logger.debug(f"Health score calculation: CRITICAL={severity_counts.get('CRITICAL', 0)}, "
                        f"HIGH={severity_counts.get('HIGH', 0)}, recent_alerts={recent_alerts}, "
                        f"final_score={calculated_score}")
            
            return calculated_score
            
        except Exception as e:
            logger.warning(f"Health score calculation failed: {e}, using default")
            return 75.0  # Default moderate health score

    def _get_mock_alarm_data(self, compartment_id: str) -> List[Dict[str, Any]]:
        """Return mock alarm data for development - CONSISTENT DATA FOR ALL COMPARTMENTS"""
        # Always return the same mock data regardless of compartment ID for consistency
        logger.debug(f"Generating consistent mock alarm data for compartment: {compartment_id}")
        return [
            {
                "id": "ocid1.alarm.oc1..mock1",
                "display_name": "High CPU Usage - Web Server",
                "severity": "HIGH",
                "lifecycle_state": "ACTIVE",
                "is_enabled": True,
                "metric_compartment_id": compartment_id,
                "namespace": "oci_computeagent",
                "query": "CpuUtilization[1m].mean() > 80",
                "rule_name": "high-cpu-web-server",
                "time_created": (datetime.utcnow() - timedelta(days=1)).isoformat(),
                "time_updated": datetime.utcnow().isoformat()
            },
            {
                "id": "ocid1.alarm.oc1..mock2", 
                "display_name": "Database Connection Pool Full",
                "severity": "CRITICAL",
                "lifecycle_state": "ACTIVE",
                "is_enabled": True,
                "metric_compartment_id": compartment_id,
                "namespace": "oci_database",
                "query": "ConnectionPoolUtilization[1m].mean() > 95",
                "rule_name": "db-connection-pool-full",
                "time_created": (datetime.utcnow() - timedelta(hours=6)).isoformat(),
                "time_updated": datetime.utcnow().isoformat()
            }
        ]
        # This should always result in: 100 - 20 (CRITICAL) - 10 (HIGH) = 70 health score

    def _get_mock_alarm_history(self, compartment_id: str) -> List[Dict[str, Any]]:
        """Return mock alarm history for development"""
        return [
            {
                "alarm_id": "high-cpu-web-server",
                "status": "FIRING",
                "timestamp": (datetime.utcnow() - timedelta(minutes=30)).isoformat(),
                "summary": "CPU utilization exceeded 80% threshold",
                "suppressed": False
            },
            {
                "alarm_id": "db-connection-pool-full",
                "status": "OK",
                "timestamp": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
                "summary": "Connection pool utilization returned to normal",
                "suppressed": False
            }
        ]

    def _get_mock_metrics_data(self, namespace: str, metric_name: str) -> Dict[str, Any]:
        """Return mock metrics data for development"""
        return {
            "namespace": namespace,
            "metric_name": metric_name,
            "compartment_id": "mock-compartment",
            "data_points": [
                {
                    "timestamp": (datetime.utcnow() - timedelta(minutes=i*5)).isoformat(),
                    "value": 50 + (i * 5) + (i % 3 * 10)  # Generate some varying data
                }
                for i in range(12)  # Last hour of data points every 5 minutes
            ],
            "start_time": (datetime.utcnow() - timedelta(hours=1)).isoformat(),
            "end_time": datetime.utcnow().isoformat()
        }

    def _get_mock_logs_data(self, compartment_id: str) -> List[Dict[str, Any]]:
        """Return mock log data for development"""
        return [
            {
                "id": "log-entry-1",
                "timestamp": (datetime.utcnow() - timedelta(minutes=10)).isoformat(),
                "message": {"text": "Application started successfully", "level": "INFO"},
                "source": "web-server-01",
                "compartment_id": compartment_id,
                "log_group_id": "web-server-logs",
                "fields": {"service": "web", "version": "1.0.0"}
            },
            {
                "id": "log-entry-2",
                "timestamp": (datetime.utcnow() - timedelta(minutes=5)).isoformat(),
                "message": {"text": "Database connection timeout", "level": "ERROR"},
                "source": "web-server-01",
                "compartment_id": compartment_id,
                "log_group_id": "web-server-logs",
                "fields": {"service": "web", "error_code": "DB_TIMEOUT"}
            }
        ]

# Service instance
monitoring_service = MonitoringService() 