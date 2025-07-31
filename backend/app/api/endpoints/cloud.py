from fastapi import APIRouter, Depends, Query, HTTPException, Path
from typing import List, Dict, Any, Optional
from app.services.cloud_service import oci_service, cloud_ops_service
from app.core.permissions import require_permissions
from app.schemas.auth import UserResponse
from app.models.user import User
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Response models
class CompartmentResponse(BaseModel):
    id: str
    name: str
    description: str
    lifecycle_state: str

class ResourceResponse(BaseModel):
    id: str
    display_name: str
    lifecycle_state: str
    resource_type: str
    compartment_id: str

class MetricsResponse(BaseModel):
    resource_id: str
    metrics: Dict[str, Any]
    timestamp: str
    health_status: str

class ResourceSummaryResponse(BaseModel):
    compartment_id: str
    resources: Dict[str, List[Dict[str, Any]]]
    total_resources: int
    last_updated: str

@router.get("/compartments", response_model=List[CompartmentResponse])
async def get_compartments(
    current_user: User = Depends(require_permissions(["viewer", "operator", "admin"]))
) -> List[CompartmentResponse]:
    """
    Get all accessible OCI compartments.
    
    **Required permissions:** viewer, operator, or admin
    
    Returns a list of compartments the user has access to view.
    """
    try:
        compartments = await oci_service.get_compartments()
        return [CompartmentResponse(**comp) for comp in compartments]
    except Exception as e:
        logger.warning(f"OCI not configured, returning mock data: {e}")
        # Return mock compartments when OCI is not configured
        return [
            CompartmentResponse(
                id="ocid1.compartment.oc1..demo",
                name="Demo Compartment",
                description="Demo compartment - OCI not configured",
                lifecycle_state="ACTIVE",
                time_created="2024-01-01T00:00:00Z",
                resource_count=0
            )
        ]

@router.get("/compartments/{compartment_id}/resources", response_model=ResourceSummaryResponse)
async def get_compartment_resources(
    compartment_id: str = Path(..., description="OCI Compartment ID"),
    resource_types: Optional[str] = Query(None, description="Comma-separated list of resource types to filter"),
    current_user: UserResponse = Depends(require_permissions(["viewer", "operator", "admin"]))
) -> ResourceSummaryResponse:
    """
    Get all resources in a specific compartment.
    
    **Required permissions:** viewer, operator, or admin
    
    **Parameters:**
    - **compartment_id**: OCI compartment OCID
    - **resource_types**: Optional filter for specific resource types (compute,databases,oke_clusters,api_gateways,load_balancers)
    
    Returns comprehensive resource information for the specified compartment.
    """
    try:
        resource_filter = None
        if resource_types:
            resource_filter = [rt.strip() for rt in resource_types.split(",")]
        
        resources = await oci_service.get_all_resources(compartment_id, resource_filter)
        return ResourceSummaryResponse(**resources)
    except Exception as e:
        logger.error(f"Failed to get compartment resources: {e}")
        raise HTTPException(status_code=500, detail="Unable to retrieve compartment resources")

@router.get("/compartments/{compartment_id}/compute-instances")
async def get_compute_instances(
    compartment_id: str = Path(..., description="OCI Compartment ID"),
    current_user: UserResponse = Depends(require_permissions(["viewer", "operator", "admin"]))
) -> List[Dict[str, Any]]:
    """
    Get compute instances in a compartment.
    
    **Required permissions:** viewer, operator, or admin
    """
    try:
        instances = await oci_service.get_compute_instances(compartment_id)
        return instances
    except Exception as e:
        logger.error(f"Failed to get compute instances: {e}")
        raise HTTPException(status_code=500, detail="Unable to retrieve compute instances")

@router.get("/compartments/{compartment_id}/databases")
async def get_databases(
    compartment_id: str = Path(..., description="OCI Compartment ID"),
    current_user: UserResponse = Depends(require_permissions(["viewer", "operator", "admin"]))
) -> List[Dict[str, Any]]:
    """
    Get database services in a compartment.
    
    **Required permissions:** viewer, operator, or admin
    """
    try:
        databases = await oci_service.get_databases(compartment_id)
        return databases
    except Exception as e:
        logger.error(f"Failed to get databases: {e}")
        raise HTTPException(status_code=500, detail="Unable to retrieve databases")

@router.get("/compartments/{compartment_id}/oke-clusters")
async def get_oke_clusters(
    compartment_id: str = Path(..., description="OCI Compartment ID"),
    current_user: UserResponse = Depends(require_permissions(["viewer", "operator", "admin"]))
) -> List[Dict[str, Any]]:
    """
    Get OKE clusters in a compartment.
    
    **Required permissions:** viewer, operator, or admin
    """
    try:
        clusters = await oci_service.get_oke_clusters(compartment_id)
        return clusters
    except Exception as e:
        logger.error(f"Failed to get OKE clusters: {e}")
        raise HTTPException(status_code=500, detail="Unable to retrieve OKE clusters")

@router.get("/compartments/{compartment_id}/api-gateways")
async def get_api_gateways(
    compartment_id: str = Path(..., description="OCI Compartment ID"),
    current_user: UserResponse = Depends(require_permissions(["viewer", "operator", "admin"]))
) -> List[Dict[str, Any]]:
    """
    Get API Gateways in a compartment.
    
    **Required permissions:** viewer, operator, or admin
    """
    try:
        gateways = await oci_service.get_api_gateways(compartment_id)
        return gateways
    except Exception as e:
        logger.error(f"Failed to get API gateways: {e}")
        raise HTTPException(status_code=500, detail="Unable to retrieve API gateways")

@router.get("/compartments/{compartment_id}/load-balancers")
async def get_load_balancers(
    compartment_id: str = Path(..., description="OCI Compartment ID"),
    current_user: UserResponse = Depends(require_permissions(["viewer", "operator", "admin"]))
) -> List[Dict[str, Any]]:
    """
    Get load balancers in a compartment.
    
    **Required permissions:** viewer, operator, or admin
    """
    try:
        load_balancers = await oci_service.get_load_balancers(compartment_id)
        return load_balancers
    except Exception as e:
        logger.error(f"Failed to get load balancers: {e}")
        raise HTTPException(status_code=500, detail="Unable to retrieve load balancers")

@router.get("/resources/{resource_id}/metrics", response_model=MetricsResponse)
async def get_resource_metrics(
    resource_id: str = Path(..., description="OCI Resource ID"),
    resource_type: str = Query(..., description="Type of resource (compute_instance, database, etc.)"),
    current_user: UserResponse = Depends(require_permissions(["viewer", "operator", "admin"]))
) -> MetricsResponse:
    """
    Get real-time metrics for a specific resource.
    
    **Required permissions:** viewer, operator, or admin
    
    **Parameters:**
    - **resource_id**: OCI resource OCID
    - **resource_type**: Type of resource to get metrics for
    
    Returns CPU, memory, network metrics and health status.
    """
    try:
        metrics = await oci_service.get_resource_metrics(resource_id, resource_type)
        return MetricsResponse(**metrics)
    except Exception as e:
        logger.error(f"Failed to get resource metrics: {e}")
        raise HTTPException(status_code=500, detail="Unable to retrieve resource metrics")

# Legacy endpoints for backward compatibility
@router.get("/resources")
async def get_cloud_resources(
    provider: str = Query("oci", description="Cloud provider"),
    compartment_id: Optional[str] = Query(None, description="OCI Compartment ID"),
    current_user: UserResponse = Depends(require_permissions(["viewer", "operator", "admin"]))
) -> Dict[str, Any]:
    """
    Legacy endpoint: Get cloud resources from specified provider.
    
    **Required permissions:** viewer, operator, or admin
    
    **Note:** This endpoint is maintained for backward compatibility.
    Use the new compartment-specific endpoints for better performance.
    """
    try:
        resources = await cloud_ops_service.get_cloud_resources(provider, compartment_id)
        return resources
    except Exception as e:
        logger.error(f"Failed to get cloud resources: {e}")
        raise HTTPException(status_code=500, detail="Unable to retrieve cloud resources")

@router.post("/resources/{resource_id}/actions/{action}")
async def execute_resource_action(
    resource_id: str = Path(..., description="OCI Resource ID"),
    action: str = Path(..., description="Action to execute"),
    current_user: UserResponse = Depends(require_permissions(["operator", "admin"]))
) -> Dict[str, Any]:
    """
    Execute an action on a specific resource.
    
    **Required permissions:** operator or admin
    
    **Supported actions:**
    - start: Start a stopped resource
    - stop: Stop a running resource  
    - restart: Restart a resource
    - terminate: Terminate a resource (admin only)
    
    **Note:** This is a placeholder for future implementation.
    """
    if action == "terminate" and "admin" not in current_user.roles:
        raise HTTPException(status_code=403, detail="Terminate action requires admin role")
    
    try:
        # Placeholder implementation
        result = {
            "resource_id": resource_id,
            "action": action,
            "status": "PENDING",
            "message": f"Action '{action}' initiated for resource {resource_id}",
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        logger.info(f"Resource action executed: {action} on {resource_id} by {current_user.username}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to execute resource action: {e}")
        raise HTTPException(status_code=500, detail="Unable to execute resource action") 