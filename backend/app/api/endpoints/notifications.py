from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

from app.core.permissions import require_permissions
from app.core.exceptions import ExternalServiceError
from app.models.user import User
from app.services.monitoring_service import MonitoringService

# Lazy-load OCI service to avoid startup hangs
def get_oci_service():
    from app.services.cloud_service import oci_service
    return oci_service

router = APIRouter(prefix="/notifications", tags=["notifications"])
logger = logging.getLogger(__name__)

@router.get("/real-time")
async def get_real_time_notifications(
    compartment_id: str = Query(..., description="OCI Compartment ID"),
    severity_filter: Optional[str] = Query(None, description="Filter by severity: CRITICAL, HIGH, MEDIUM, LOW"),
    hours_back: int = Query(24, description="Hours of history to retrieve", ge=1, le=168),
    current_user: User = Depends(require_permissions("viewer"))
) -> List[Dict[str, Any]]:
    """
    Get real-time notifications from OCI monitoring and alarms.
    
    **Required permissions:** viewer, operator, or admin
    """
    try:
        monitoring_service = MonitoringService()
        
        # Calculate time range
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours_back)
        
        # Get active alarms (these become notifications)
        alarms = await monitoring_service.get_alarm_status(compartment_id)
        
        # Get alarm history for recent triggered alerts
        alarm_history = await monitoring_service.get_alarm_history(compartment_id, start_time, end_time)
        
        notifications = []
        
        # Convert active alarms to notifications
        for alarm in alarms:
            if alarm.get('is_enabled', False):
                severity = alarm.get('severity', 'MEDIUM').upper()
                
                # Apply severity filter if specified
                if severity_filter and severity != severity_filter.upper():
                    continue
                    
                notification = {
                    "id": f"alarm_{alarm['id']}",
                    "type": _map_severity_to_type(severity),
                    "title": alarm.get('display_name', 'OCI Alarm'),
                    "message": f"Monitoring alarm in namespace: {alarm.get('namespace', 'Unknown')}",
                    "timestamp": alarm.get('time_updated', alarm.get('time_created', datetime.utcnow().isoformat())),
                    "read": False,
                    "actionable": True,
                    "resourceType": "monitoring",
                    "severity": severity,
                    "alarm_id": alarm['id'],
                    "compartment_id": compartment_id,
                    "query": alarm.get('query', ''),
                    "namespace": alarm.get('namespace', ''),
                    "lifecycle_state": alarm.get('lifecycle_state', 'UNKNOWN')
                }
                notifications.append(notification)
        
        # Convert recent alarm history to notifications (recent triggers)
        for event in alarm_history:
            notification = {
                "id": f"history_{event.get('alarm_id', 'unknown')}_{event.get('timestamp', '')}",
                "type": _map_severity_to_type(event.get('severity', 'MEDIUM')),
                "title": f"Alarm Triggered: {event.get('alarm_name', 'Unknown')}",
                "message": event.get('summary', 'Monitoring alarm was triggered'),
                "timestamp": event.get('timestamp', datetime.utcnow().isoformat()),
                "read": False,
                "actionable": True,
                "resourceType": "monitoring",
                "severity": event.get('severity', 'MEDIUM'),
                "alarm_id": event.get('alarm_id'),
                "compartment_id": compartment_id,
                "status": event.get('status', 'UNKNOWN')
            }
            notifications.append(notification)
        
        # Sort by timestamp (newest first)
        notifications.sort(key=lambda x: x['timestamp'], reverse=True)
        
        logger.info(f"Retrieved {len(notifications)} real-time notifications for compartment {compartment_id}")
        return notifications
        
    except Exception as e:
        logger.error(f"Failed to get real-time notifications: {e}")
        raise HTTPException(status_code=500, detail="Unable to retrieve real-time notifications")

@router.post("/system")
async def create_system_notification(
    notification_data: Dict[str, Any],
    current_user: User = Depends(require_permissions("operator"))
) -> Dict[str, str]:
    """
    Create a system notification (for deployment events, errors, etc.)
    
    **Required permissions:** operator or admin
    """
    try:
        # Validate required fields
        required_fields = ['type', 'title', 'message']
        for field in required_fields:
            if field not in notification_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Create system notification
        system_notification = {
            "id": f"system_{int(datetime.utcnow().timestamp())}_{current_user.id}",
            "type": notification_data['type'],  # success, error, warning, info
            "title": notification_data['title'],
            "message": notification_data['message'],
            "timestamp": datetime.utcnow().isoformat(),
            "read": False,
            "actionable": notification_data.get('actionable', False),
            "resourceType": notification_data.get('resourceType', 'system'),
            "resourceId": notification_data.get('resourceId'),
            "created_by": current_user.username,
            "severity": notification_data.get('severity', 'MEDIUM')
        }
        
        # Here you would typically:
        # 1. Store in database
        # 2. Send via WebSocket to connected clients
        # 3. Send to external notification systems
        
        logger.info(f"System notification created by {current_user.username}: {notification_data['title']}")
        
        return {
            "status": "success",
            "notification_id": system_notification["id"],
            "message": "System notification created successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create system notification: {e}")
        raise HTTPException(status_code=500, detail="Unable to create system notification")

@router.get("/health")
async def get_notification_health(
    current_user: User = Depends(require_permissions("viewer"))
) -> Dict[str, Any]:
    """
    Get notification system health status
    """
    try:
        oci_service = get_oci_service()
        
        health_status = {
            "oci_monitoring_available": oci_service.oci_available and 'monitoring' in oci_service.clients,
            "last_check": datetime.utcnow().isoformat(),
            "status": "healthy" if oci_service.oci_available else "degraded",
            "capabilities": {
                "real_time_alarms": oci_service.oci_available and 'monitoring' in oci_service.clients,
                "system_notifications": True,
                "alarm_history": oci_service.oci_available and 'monitoring' in oci_service.clients,
                "metrics_integration": oci_service.oci_available and 'monitoring' in oci_service.clients
            }
        }
        
        return health_status
        
    except Exception as e:
        logger.error(f"Failed to get notification health: {e}")
        raise HTTPException(status_code=500, detail="Unable to retrieve notification health status")

def _map_severity_to_type(severity: str) -> str:
    """Map OCI alarm severity to notification type"""
    severity_map = {
        'CRITICAL': 'error',
        'HIGH': 'error', 
        'MEDIUM': 'warning',
        'LOW': 'info'
    }
    return severity_map.get(severity.upper(), 'info') 