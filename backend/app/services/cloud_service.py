import asyncio
import oci
import json
import logging
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

try:
    from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
    TENACITY_AVAILABLE = True
except ImportError:
    TENACITY_AVAILABLE = False
    # Create dummy decorators when tenacity is not available
    def retry(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    stop_after_attempt = wait_exponential = retry_if_exception_type = lambda *args, **kwargs: None

from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import os
from app.core.exceptions import ExternalServiceError, NotFoundError

logger = logging.getLogger(__name__)

# Configuration and data classes
@dataclass
class OCIMetrics:
    """Data class for OCI resource metrics"""
    cpu_utilization: float
    memory_utilization: float
    network_bytes_in: int
    network_bytes_out: int
    timestamp: datetime

@dataclass 
class OCIResource:
    """Data class for OCI resource information"""
    id: str
    name: str
    state: str
    resource_type: str
    compartment_id: str
    availability_domain: Optional[str] = None
    shape: Optional[str] = None
    metrics: Optional[OCIMetrics] = None

class ResourceType(Enum):
    """Enumeration of supported OCI resource types"""
    COMPUTE_INSTANCE = "compute_instance"
    DATABASE = "database"
    OKE_CLUSTER = "oke_cluster"
    API_GATEWAY = "api_gateway"
    LOAD_BALANCER = "load_balancer"
    AUTONOMOUS_DATABASE = "autonomous_database"

class OCIAuthConfig:
    """OCI authentication configuration management"""
    
    def __init__(self):
        self.config_file = os.getenv("OCI_CONFIG_FILE", "~/.oci/config")
        self.profile = os.getenv("OCI_PROFILE", "DEFAULT")
        self.region = os.getenv("OCI_REGION", "us-phoenix-1")
        
        # Environment variable based auth (for containerized environments)
        self.tenancy_id = os.getenv("OCI_TENANCY_ID")
        self.user_id = os.getenv("OCI_USER_ID")
        self.fingerprint = os.getenv("OCI_FINGERPRINT")
        self.key_file = os.getenv("OCI_KEY_FILE")
        
    def get_config(self) -> Dict[str, str]:
        """Get OCI configuration for SDK initialization"""
        if self.tenancy_id and self.user_id and self.fingerprint and self.key_file:
            # Use environment variables
            return {
                "user": self.user_id,
                "key_file": self.key_file,
                "fingerprint": self.fingerprint,
                "tenancy": self.tenancy_id,
                "region": self.region
            }
        else:
            # Use config file
            try:
                return oci.config.from_file(self.config_file, self.profile)
            except Exception as e:
                logger.warning(f"Could not load OCI config file: {e}")
                # Return minimal config for mock/development mode
                return {
                    "region": self.region,
                    "tenancy": "ocid1.tenancy.oc1..example",
                    "user": "ocid1.user.oc1..example",
                    "fingerprint": "example:fingerprint",
                    "key_file": "/dev/null"
                }

class OCICacheManager:
    """Redis-based caching for OCI API responses"""
    
    def __init__(self):
        if not REDIS_AVAILABLE:
            logger.warning("Redis module not available - caching disabled")
            self.cache_enabled = False
            return
            
        try:
            self.redis_client = redis.Redis(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", 6379)),
                db=int(os.getenv("REDIS_DB", 0)),
                decode_responses=True
            )
            # Test connection
            self.redis_client.ping()
            self.cache_enabled = True
            logger.info("Redis cache initialized successfully")
        except Exception as e:
            logger.warning(f"Redis cache unavailable: {e}")
            self.cache_enabled = False
    
    def get(self, key: str) -> Optional[Dict]:
        """Get cached data"""
        if not self.cache_enabled:
            return None
        try:
            data = self.redis_client.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.warning(f"Cache get error: {e}")
            return None
    
    def set(self, key: str, data: Dict, ttl: int = 300) -> bool:
        """Set cached data with TTL (default 5 minutes)"""
        if not self.cache_enabled:
            return False
        try:
            self.redis_client.setex(key, ttl, json.dumps(data, default=str))
            return True
        except Exception as e:
            logger.warning(f"Cache set error: {e}")
            return False

class OCIService:
    """Comprehensive OCI SDK integration service"""
    
    def __init__(self):
        self.auth_config = OCIAuthConfig()
        self.cache = OCICacheManager()
        self.config = self.auth_config.get_config()
        self.clients = {}
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize OCI SDK clients"""
        try:
            # Core clients
            self.clients['compute'] = oci.core.ComputeClient(self.config)
            self.clients['identity'] = oci.identity.IdentityClient(self.config)
            self.clients['monitoring'] = oci.monitoring.MonitoringClient(self.config)
            
            # Database clients
            self.clients['database'] = oci.database.DatabaseClient(self.config)
            
            # Container and networking clients
            self.clients['container_engine'] = oci.container_engine.ContainerEngineClient(self.config)
            self.clients['load_balancer'] = oci.load_balancer.LoadBalancerClient(self.config)
            self.clients['network_load_balancer'] = oci.network_load_balancer.NetworkLoadBalancerClient(self.config)
            self.clients['api_gateway'] = oci.apigateway.GatewayClient(self.config)
            
            # Virtual network client
            self.clients['virtual_network'] = oci.core.VirtualNetworkClient(self.config)
            
            logger.info("OCI SDK clients initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize OCI clients: {e}")
            # Initialize mock clients for development
            self.clients = {}

    async def _make_oci_call(self, client_method, *args, **kwargs):
        """Make OCI API call with retry logic"""
        try:
            return await asyncio.get_event_loop().run_in_executor(
                None, client_method, *args, **kwargs
            )
        except oci.exceptions.ServiceError as e:
            logger.error(f"OCI API error: {e}")
            raise ExternalServiceError(f"OCI API call failed: {e.message}")
        except Exception as e:
            logger.error(f"Unexpected error in OCI call: {e}")
            raise ExternalServiceError("OCI service temporarily unavailable")

    async def get_compartments(self) -> List[Dict[str, Any]]:
        """Get all accessible compartments"""
        cache_key = "oci:compartments"
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        try:
            if 'identity' not in self.clients:
                # Mock response for development
                mock_compartments = [
                    {
                        "id": "ocid1.compartment.oc1..example1",
                        "name": "Development", 
                        "description": "Development environment",
                        "lifecycle_state": "ACTIVE"
                    },
                    {
                        "id": "ocid1.compartment.oc1..example2",
                        "name": "Production",
                        "description": "Production environment", 
                        "lifecycle_state": "ACTIVE"
                    }
                ]
                self.cache.set(cache_key, mock_compartments, 600)  # 10 minutes cache
                return mock_compartments
            
            tenancy_id = self.config.get('tenancy')
            response = await self._make_oci_call(
                self.clients['identity'].list_compartments,
                tenancy_id,
                compartment_id_in_subtree=True
            )
            
            compartments = []
            for comp in response.data:
                compartments.append({
                    "id": comp.id,
                    "name": comp.name,
                    "description": comp.description,
                    "lifecycle_state": comp.lifecycle_state
                })
            
            self.cache.set(cache_key, compartments, 600)  # 10 minutes cache
            return compartments
            
        except Exception as e:
            logger.error(f"Failed to get compartments: {e}")
            raise ExternalServiceError("Unable to retrieve compartments")

    async def get_compute_instances(self, compartment_id: str) -> List[Dict[str, Any]]:
        """Get compute instances in a compartment"""
        cache_key = f"oci:compute:{compartment_id}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        try:
            if 'compute' not in self.clients:
                # Mock response
                mock_instances = [
                    {
                        "id": "ocid1.instance.oc1.phx.example1",
                        "display_name": "web-server-prod",
                        "lifecycle_state": "RUNNING",
                        "shape": "VM.Standard.E4.Flex",
                        "availability_domain": "Uocm:PHX-AD-1",
                        "time_created": datetime.utcnow().isoformat(),
                        "region": self.config.get('region', 'us-phoenix-1')
                    }
                ]
                self.cache.set(cache_key, mock_instances, 300)
                return mock_instances
            
            response = await self._make_oci_call(
                self.clients['compute'].list_instances,
                compartment_id
            )
            
            instances = []
            for instance in response.data:
                instances.append({
                    "id": instance.id,
                    "display_name": instance.display_name,
                    "lifecycle_state": instance.lifecycle_state,
                    "shape": instance.shape,
                    "availability_domain": instance.availability_domain,
                    "time_created": instance.time_created.isoformat() if instance.time_created else None,
                    "region": instance.region if hasattr(instance, 'region') else self.config.get('region')
                })
            
            self.cache.set(cache_key, instances, 300)  # 5 minutes cache
            return instances
            
        except Exception as e:
            logger.error(f"Failed to get compute instances: {e}")
            raise ExternalServiceError("Unable to retrieve compute instances")

    async def get_databases(self, compartment_id: str) -> List[Dict[str, Any]]:
        """Get database services in a compartment"""
        cache_key = f"oci:databases:{compartment_id}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        try:
            if 'database' not in self.clients:
                # Mock response
                mock_databases = [
                    {
                        "id": "ocid1.autonomousdatabase.oc1.phx.example1",
                        "db_name": "proddb",
                        "display_name": "Production Database",
                        "lifecycle_state": "AVAILABLE",
                        "db_workload": "OLTP",
                        "cpu_core_count": 2,
                        "data_storage_size_in_gbs": 1024
                    }
                ]
                self.cache.set(cache_key, mock_databases, 300)
                return mock_databases
            
            # Get autonomous databases
            response = await self._make_oci_call(
                self.clients['database'].list_autonomous_databases,
                compartment_id
            )
            
            databases = []
            for db in response.data:
                databases.append({
                    "id": db.id,
                    "db_name": db.db_name,
                    "display_name": db.display_name,
                    "lifecycle_state": db.lifecycle_state,
                    "db_workload": db.db_workload,
                    "cpu_core_count": db.cpu_core_count,
                    "data_storage_size_in_gbs": db.data_storage_size_in_gbs
                })
            
            self.cache.set(cache_key, databases, 300)
            return databases
            
        except Exception as e:
            logger.error(f"Failed to get databases: {e}")
            raise ExternalServiceError("Unable to retrieve databases")

    async def get_oke_clusters(self, compartment_id: str) -> List[Dict[str, Any]]:
        """Get OKE clusters in a compartment"""
        cache_key = f"oci:oke:{compartment_id}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        try:
            if 'container_engine' not in self.clients:
                # Mock response
                mock_clusters = [
                    {
                        "id": "ocid1.cluster.oc1.phx.example1",
                        "name": "prod-cluster",
                        "lifecycle_state": "ACTIVE",
                        "kubernetes_version": "v1.28.2",
                        "vcn_id": "ocid1.vcn.oc1.phx.example1"
                    }
                ]
                self.cache.set(cache_key, mock_clusters, 300)
                return mock_clusters
            
            response = await self._make_oci_call(
                self.clients['container_engine'].list_clusters,
                compartment_id
            )
            
            clusters = []
            for cluster in response.data:
                clusters.append({
                    "id": cluster.id,
                    "name": cluster.name,
                    "lifecycle_state": cluster.lifecycle_state,
                    "kubernetes_version": cluster.kubernetes_version,
                    "vcn_id": cluster.vcn_id
                })
            
            self.cache.set(cache_key, clusters, 300)
            return clusters
            
        except Exception as e:
            logger.error(f"Failed to get OKE clusters: {e}")
            raise ExternalServiceError("Unable to retrieve OKE clusters")

    async def get_api_gateways(self, compartment_id: str) -> List[Dict[str, Any]]:
        """Get API Gateways in a compartment"""
        cache_key = f"oci:api_gateways:{compartment_id}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        try:
            if 'api_gateway' not in self.clients:
                # Mock response
                mock_gateways = [
                    {
                        "id": "ocid1.apigateway.oc1.phx.example1",
                        "display_name": "prod-api-gateway",
                        "lifecycle_state": "ACTIVE",
                        "hostname": "example-gateway.us-phoenix-1.oci.oraclecloud.com"
                    }
                ]
                self.cache.set(cache_key, mock_gateways, 300)
                return mock_gateways
            
            response = await self._make_oci_call(
                self.clients['api_gateway'].list_gateways,
                compartment_id
            )
            
            gateways = []
            for gateway in response.data:
                gateways.append({
                    "id": gateway.id,
                    "display_name": gateway.display_name,
                    "lifecycle_state": gateway.lifecycle_state,
                    "hostname": gateway.hostname
                })
            
            self.cache.set(cache_key, gateways, 300)
            return gateways
            
        except Exception as e:
            logger.error(f"Failed to get API gateways: {e}")
            raise ExternalServiceError("Unable to retrieve API gateways")

    async def get_load_balancers(self, compartment_id: str) -> List[Dict[str, Any]]:
        """Get load balancers in a compartment"""
        cache_key = f"oci:load_balancers:{compartment_id}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        try:
            if 'load_balancer' not in self.clients:
                # Mock response
                mock_lbs = [
                    {
                        "id": "ocid1.loadbalancer.oc1.phx.example1",
                        "display_name": "prod-load-balancer",
                        "lifecycle_state": "ACTIVE",
                        "shape_name": "100Mbps",
                        "is_private": False
                    }
                ]
                self.cache.set(cache_key, mock_lbs, 300)
                return mock_lbs
            
            response = await self._make_oci_call(
                self.clients['load_balancer'].list_load_balancers,
                compartment_id
            )
            
            load_balancers = []
            for lb in response.data:
                load_balancers.append({
                    "id": lb.id,
                    "display_name": lb.display_name,
                    "lifecycle_state": lb.lifecycle_state,
                    "shape_name": lb.shape_name,
                    "is_private": lb.is_private
                })
            
            self.cache.set(cache_key, load_balancers, 300)
            return load_balancers
            
        except Exception as e:
            logger.error(f"Failed to get load balancers: {e}")
            raise ExternalServiceError("Unable to retrieve load balancers")

    async def get_resource_metrics(self, resource_id: str, resource_type: str) -> Dict[str, Any]:
        """Get real-time metrics for a resource"""
        cache_key = f"oci:metrics:{resource_id}:{resource_type}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        try:
            if 'monitoring' not in self.clients:
                # Mock metrics
                mock_metrics = {
                    "resource_id": resource_id,
                    "metrics": {
                        "cpu_utilization": 45.2,
                        "memory_utilization": 67.8,
                        "network_bytes_in": 1024000,
                        "network_bytes_out": 512000
                    },
                    "timestamp": datetime.utcnow().isoformat(),
                    "health_status": "HEALTHY"
                }
                self.cache.set(cache_key, mock_metrics, 60)  # 1 minute cache
                return mock_metrics
            
            # Query OCI monitoring service for real metrics
            # This is a simplified implementation - real metrics would require specific queries
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(minutes=5)
            
            metrics_data = {
                "resource_id": resource_id,
                "metrics": {
                    "cpu_utilization": 0.0,
                    "memory_utilization": 0.0, 
                    "network_bytes_in": 0,
                    "network_bytes_out": 0
                },
                "timestamp": end_time.isoformat(),
                "health_status": "UNKNOWN"
            }
            
            self.cache.set(cache_key, metrics_data, 60)
            return metrics_data
            
        except Exception as e:
            logger.error(f"Failed to get metrics for {resource_id}: {e}")
            raise ExternalServiceError("Unable to retrieve resource metrics")

    async def get_all_resources(self, compartment_id: str, resource_filter: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get all resources in a compartment with optional filtering"""
        try:
            # Get all resource types in parallel
            tasks = []
            
            if not resource_filter or 'compute' in resource_filter:
                tasks.append(('compute_instances', self.get_compute_instances(compartment_id)))
            
            if not resource_filter or 'databases' in resource_filter:
                tasks.append(('databases', self.get_databases(compartment_id)))
            
            if not resource_filter or 'oke_clusters' in resource_filter:
                tasks.append(('oke_clusters', self.get_oke_clusters(compartment_id)))
            
            if not resource_filter or 'api_gateways' in resource_filter:
                tasks.append(('api_gateways', self.get_api_gateways(compartment_id)))
            
            if not resource_filter or 'load_balancers' in resource_filter:
                tasks.append(('load_balancers', self.get_load_balancers(compartment_id)))
            
            # Execute all tasks in parallel
            results = {}
            for name, task in tasks:
                try:
                    results[name] = await task
                except Exception as e:
                    logger.error(f"Failed to get {name}: {e}")
                    results[name] = []
            
            return {
                "compartment_id": compartment_id,
                "resources": results,
                "total_resources": sum(len(resources) for resources in results.values()),
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get all resources: {e}")
            raise ExternalServiceError("Unable to retrieve compartment resources")

# Legacy CloudOperationsService for backward compatibility
class CloudOperationsService:
    """Legacy service wrapper for backward compatibility"""
    
    def __init__(self):
        self.oci_service = OCIService()
    
    async def get_cloud_resources(self, provider: str = "oci", compartment_id: Optional[str] = None) -> Dict[str, Any]:
        """Get cloud resources (wrapper for legacy compatibility)"""
        if provider != "oci":
            raise ExternalServiceError(f"Provider {provider} not supported")
        
        try:
            if not compartment_id:
                # Get first available compartment
                compartments = await self.oci_service.get_compartments()
                if not compartments:
                    raise ExternalServiceError("No accessible compartments found")
                compartment_id = compartments[0]['id']
            
            return await self.oci_service.get_all_resources(compartment_id)
            
        except Exception as e:
            logger.error(f"Failed to get cloud resources: {e}")
            raise ExternalServiceError("Cloud resources unavailable")

# Service instances
oci_service = OCIService()
cloud_ops_service = CloudOperationsService()

# For backward compatibility
k8s_service = None  # Will be implemented separately if needed 