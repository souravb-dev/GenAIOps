from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Dict, Any, List, Optional
from app.services.cloud_service import cloud_ops_service, k8s_service
from app.api.endpoints.auth import get_current_user
from app.models.user import User
from app.core.exceptions import ExternalServiceError, NotFoundError

router = APIRouter()

@router.get("/resources")
async def get_cloud_resources(
    provider: str = Query("oci", description="Cloud provider (oci, aws, azure)"),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get cloud resources from provider"""
    try:
        resources = await cloud_ops_service.get_cloud_resources(provider)
        return {
            "success": True,
            "data": resources,
            "user": current_user.username
        }
    except ExternalServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Cloud provider service unavailable: {e.message}"
        )

@router.post("/resources/analyze-costs")
async def analyze_resource_costs(
    resources: Dict[str, Any],
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Analyze costs for provided cloud resources"""
    try:
        cost_analysis = await cloud_ops_service.analyze_resource_costs(resources)
        return {
            "success": True,
            "data": cost_analysis,
            "analyzed_by": current_user.username
        }
    except ExternalServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Cost analysis service unavailable: {e.message}"
        )

@router.get("/security/alerts")
async def get_security_alerts(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get security alerts from monitoring systems"""
    try:
        alerts = await cloud_ops_service.get_security_alerts()
        return {
            "success": True,
            "data": {
                "alerts": alerts,
                "total_alerts": len(alerts),
                "high_severity": len([a for a in alerts if a["severity"] == "HIGH"]),
                "medium_severity": len([a for a in alerts if a["severity"] == "MEDIUM"]),
                "low_severity": len([a for a in alerts if a["severity"] == "LOW"])
            },
            "retrieved_by": current_user.username
        }
    except ExternalServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Security monitoring service unavailable: {e.message}"
        )

@router.post("/security/remediate")
async def execute_remediation(
    alert_id: str,
    action: str,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Execute automated remediation for a security alert"""
    try:
        result = await cloud_ops_service.execute_remediation(alert_id, action)
        return {
            "success": True,
            "data": result,
            "executed_by": current_user.username
        }
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except ExternalServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Remediation service unavailable: {e.message}"
        )

@router.get("/kubernetes/pods")
async def get_kubernetes_pods(
    namespace: str = Query("default", description="Kubernetes namespace"),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get Kubernetes pod status"""
    try:
        pod_status = await k8s_service.get_pod_status(namespace)
        return {
            "success": True,
            "data": pod_status,
            "retrieved_by": current_user.username
        }
    except ExternalServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Kubernetes API unavailable: {e.message}"
        )

@router.get("/dashboard/summary")
async def get_dashboard_summary(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get comprehensive dashboard summary combining all services"""
    try:
        # Run multiple async operations concurrently
        import asyncio
        
        resources_task = cloud_ops_service.get_cloud_resources("oci")
        alerts_task = cloud_ops_service.get_security_alerts()
        pods_task = k8s_service.get_pod_status("default")
        
        # Wait for all operations to complete
        resources, alerts, pods = await asyncio.gather(
            resources_task, alerts_task, pods_task
        )
        
        # Analyze costs for retrieved resources
        cost_analysis = await cloud_ops_service.analyze_resource_costs(resources)
        
        summary = {
            "cloud_resources": {
                "total_instances": len(resources.get("compute_instances", [])),
                "total_volumes": len(resources.get("storage_volumes", [])),
                "total_networks": len(resources.get("network_resources", []))
            },
            "security": {
                "total_alerts": len(alerts),
                "high_severity_alerts": len([a for a in alerts if a["severity"] == "HIGH"]),
                "open_alerts": len([a for a in alerts if a["status"] == "OPEN"])
            },
            "kubernetes": {
                "total_pods": pods["total_pods"],
                "running_pods": pods["running_pods"],
                "namespace": pods["namespace"]
            },
            "costs": {
                "monthly_estimate": cost_analysis["total_monthly_cost"],
                "currency": cost_analysis["currency"]
            },
            "last_updated": resources["last_updated"]
        }
        
        return {
            "success": True,
            "data": summary,
            "retrieved_by": current_user.username
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Dashboard summary generation failed: {str(e)}"
        ) 