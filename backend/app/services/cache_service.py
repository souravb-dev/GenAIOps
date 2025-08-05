import json
import asyncio
import logging
from typing import Any, Optional, Dict, List, Union
from datetime import datetime, timedelta
import hashlib
import redis
from redis.exceptions import ConnectionError, TimeoutError
from app.core.config import settings

logger = logging.getLogger(__name__)

class CacheService:
    """Centralized caching service with Redis backend and fallback mechanisms"""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.local_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "errors": 0,
            "redis_available": False
        }
        
        # Cache configuration
        self.default_ttl = 300  # 5 minutes
        self.max_local_cache_size = 1000
        self.compression_threshold = 1024  # bytes
        
        self._initialize_redis()
    
    def _initialize_redis(self):
        """Initialize Redis connection with proper error handling"""
        if not settings.REDIS_ENABLED:
            logger.info("Redis caching disabled via configuration")
            return
            
        try:
            self.redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True,
                socket_timeout=5.0,
                socket_connect_timeout=5.0,
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            # Test connection
            self.redis_client.ping()
            self.cache_stats["redis_available"] = True
            logger.info("✅ Centralized cache service initialized with Redis")
            
        except Exception as e:
            logger.warning(f"⚠️ Redis unavailable, using local cache only: {e}")
            self.redis_client = None
            self.cache_stats["redis_available"] = False
    
    def _generate_cache_key(self, namespace: str, key: str, params: Optional[Dict] = None) -> str:
        """Generate a standardized cache key"""
        key_parts = [namespace, key]
        
        if params:
            # Sort params for consistent key generation
            sorted_params = sorted(params.items())
            params_str = json.dumps(sorted_params, default=str, sort_keys=True)
            params_hash = hashlib.md5(params_str.encode()).hexdigest()[:8]
            key_parts.append(params_hash)
        
        return ":".join(key_parts)
    
    async def get(self, namespace: str, key: str, params: Optional[Dict] = None) -> Optional[Any]:
        """Get cached data with fallback mechanisms"""
        cache_key = self._generate_cache_key(namespace, key, params)
        
        try:
            # Try Redis first
            if self.redis_client:
                try:
                    data = await asyncio.get_event_loop().run_in_executor(
                        None, self.redis_client.get, cache_key
                    )
                    if data:
                        self.cache_stats["hits"] += 1
                        return json.loads(data)
                except (ConnectionError, TimeoutError) as e:
                    logger.warning(f"Redis get failed: {e}")
                    self.cache_stats["errors"] += 1
            
            # Fallback to local cache
            if cache_key in self.local_cache:
                entry = self.local_cache[cache_key]
                if entry["expires_at"] > datetime.now():
                    self.cache_stats["hits"] += 1
                    return entry["data"]
                else:
                    # Expired entry
                    del self.local_cache[cache_key]
            
            self.cache_stats["misses"] += 1
            return None
            
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            self.cache_stats["errors"] += 1
            return None
    
    async def set(self, namespace: str, key: str, data: Any, ttl: Optional[int] = None, params: Optional[Dict] = None):
        """Set cached data with fallback mechanisms"""
        cache_key = self._generate_cache_key(namespace, key, params)
        ttl = ttl or self.default_ttl
        
        try:
            serialized_data = json.dumps(data, default=str)
            
            # Try Redis first
            if self.redis_client:
                try:
                    await asyncio.get_event_loop().run_in_executor(
                        None, self.redis_client.setex, cache_key, ttl, serialized_data
                    )
                except (ConnectionError, TimeoutError) as e:
                    logger.warning(f"Redis set failed: {e}")
                    self.cache_stats["errors"] += 1
            
            # Always store in local cache as backup
            self._set_local_cache(cache_key, data, ttl)
            
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            self.cache_stats["errors"] += 1
    
    def _set_local_cache(self, cache_key: str, data: Any, ttl: int):
        """Set data in local cache with size management"""
        # Clean up expired entries and manage size
        if len(self.local_cache) >= self.max_local_cache_size:
            self._cleanup_local_cache()
        
        self.local_cache[cache_key] = {
            "data": data,
            "expires_at": datetime.now() + timedelta(seconds=ttl),
            "created_at": datetime.now()
        }
    
    def _cleanup_local_cache(self):
        """Clean up expired entries and enforce size limits"""
        now = datetime.now()
        expired_keys = [
            key for key, entry in self.local_cache.items()
            if entry["expires_at"] <= now
        ]
        
        for key in expired_keys:
            del self.local_cache[key]
        
        # If still too large, remove oldest entries
        if len(self.local_cache) >= self.max_local_cache_size:
            sorted_entries = sorted(
                self.local_cache.items(),
                key=lambda x: x[1]["created_at"]
            )
            
            entries_to_remove = len(sorted_entries) - self.max_local_cache_size + 100
            for i in range(entries_to_remove):
                if i < len(sorted_entries):
                    del self.local_cache[sorted_entries[i][0]]
    
    async def delete(self, namespace: str, key: str, params: Optional[Dict] = None):
        """Delete cached data"""
        cache_key = self._generate_cache_key(namespace, key, params)
        
        try:
            # Delete from Redis
            if self.redis_client:
                try:
                    await asyncio.get_event_loop().run_in_executor(
                        None, self.redis_client.delete, cache_key
                    )
                except (ConnectionError, TimeoutError) as e:
                    logger.warning(f"Redis delete failed: {e}")
            
            # Delete from local cache
            if cache_key in self.local_cache:
                del self.local_cache[cache_key]
                
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
    
    async def clear_namespace(self, namespace: str):
        """Clear all cache entries for a namespace"""
        try:
            # Clear from Redis
            if self.redis_client:
                try:
                    pattern = f"{namespace}:*"
                    keys = await asyncio.get_event_loop().run_in_executor(
                        None, self.redis_client.keys, pattern
                    )
                    if keys:
                        await asyncio.get_event_loop().run_in_executor(
                            None, self.redis_client.delete, *keys
                        )
                except (ConnectionError, TimeoutError) as e:
                    logger.warning(f"Redis namespace clear failed: {e}")
            
            # Clear from local cache
            keys_to_delete = [
                key for key in self.local_cache.keys()
                if key.startswith(f"{namespace}:")
            ]
            for key in keys_to_delete:
                del self.local_cache[key]
                
        except Exception as e:
            logger.error(f"Cache namespace clear error: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_rate = (self.cache_stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            **self.cache_stats,
            "hit_rate_percent": round(hit_rate, 2),
            "local_cache_size": len(self.local_cache),
            "total_requests": total_requests
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on cache system"""
        health_status = {
            "redis_available": False,
            "local_cache_available": True,
            "redis_latency_ms": None,
            "status": "unhealthy"
        }
        
        # Test Redis
        if self.redis_client:
            try:
                start_time = datetime.now()
                await asyncio.get_event_loop().run_in_executor(
                    None, self.redis_client.ping
                )
                latency = (datetime.now() - start_time).total_seconds() * 1000
                
                health_status["redis_available"] = True
                health_status["redis_latency_ms"] = round(latency, 2)
                
            except Exception as e:
                logger.warning(f"Redis health check failed: {e}")
        
        # Overall status
        if health_status["redis_available"] or health_status["local_cache_available"]:
            health_status["status"] = "healthy"
        
        return health_status

# Global cache service instance
cache_service = CacheService() 