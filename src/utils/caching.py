"""
Caching utilities for BasicChat application
"""

import hashlib
import json
import time
from typing import Optional, Any, Dict
from abc import ABC, abstractmethod
import logging

from cachetools import TTLCache
from src.config import config

logger = logging.getLogger(__name__)

class CacheInterface(ABC):
    """Abstract base class for cache implementations"""
    
    @abstractmethod
    def get(self, key: str) -> Optional[str]:
        """Get value from cache"""
        pass
    
    @abstractmethod
    def set(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        pass
    
    @abstractmethod
    def clear(self) -> bool:
        """Clear all cache entries"""
        pass

class MemoryCache(CacheInterface):
    """In-memory cache implementation using TTLCache"""
    
    def __init__(self, ttl: int = 3600, maxsize: int = 1000):
        self.cache = TTLCache(maxsize=maxsize, ttl=ttl)
        self.ttl = ttl
    
    def get(self, key: str) -> Optional[str]:
        """Get value from memory cache"""
        try:
            return self.cache.get(key)
        except Exception as e:
            logger.warning(f"Error getting from memory cache: {e}")
            return None
    
    def set(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        """Set value in memory cache"""
        try:
            self.cache[key] = value
            return True
        except Exception as e:
            logger.warning(f"Error setting in memory cache: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from memory cache"""
        try:
            if key in self.cache:
                del self.cache[key]
            return True
        except Exception as e:
            logger.warning(f"Error deleting from memory cache: {e}")
            return False
    
    def clear(self) -> bool:
        """Clear all cache entries"""
        try:
            self.cache.clear()
            return True
        except Exception as e:
            logger.warning(f"Error clearing memory cache: {e}")
            return False

class RedisCache(CacheInterface):
    """Redis cache implementation"""
    
    def __init__(self, redis_url: str):
        try:
            import redis
            self.redis_client = redis.from_url(redis_url)
            self.redis_client.ping()  # Test connection
            self.connected = True
        except Exception as e:
            logger.warning(f"Failed to connect to Redis: {e}")
            self.connected = False
    
    def get(self, key: str) -> Optional[str]:
        """Get value from Redis cache"""
        if not self.connected:
            return None
        
        try:
            value = self.redis_client.get(key)
            return value.decode('utf-8') if value else None
        except Exception as e:
            logger.warning(f"Error getting from Redis cache: {e}")
            return None
    
    def set(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        """Set value in Redis cache"""
        if not self.connected:
            return False
        
        try:
            self.redis_client.set(key, value, ex=ttl or config.cache_ttl)
            return True
        except Exception as e:
            logger.warning(f"Error setting in Redis cache: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from Redis cache"""
        if not self.connected:
            return False
        
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.warning(f"Error deleting from Redis cache: {e}")
            return False
    
    def clear(self) -> bool:
        """Clear all cache entries"""
        if not self.connected:
            return False
        
        try:
            self.redis_client.flushdb()
            return True
        except Exception as e:
            logger.warning(f"Error clearing Redis cache: {e}")
            return False

class ResponseCache:
    """Main cache manager with fallback support"""
    
    def __init__(self):
        self.primary_cache: Optional[CacheInterface] = None
        self.fallback_cache: Optional[CacheInterface] = None
        self._initialize_caches()
    
    def _initialize_caches(self):
        """Initialize primary and fallback caches"""
        # Try Redis first if enabled
        if config.redis_enabled and config.redis_url:
            try:
                self.primary_cache = RedisCache(config.redis_url)
                if self.primary_cache.connected:
                    logger.info("Using Redis as primary cache")
                else:
                    self.primary_cache = None
            except Exception as e:
                logger.warning(f"Failed to initialize Redis cache: {e}")
                self.primary_cache = None
        
        # Always initialize memory cache as fallback
        self.fallback_cache = MemoryCache(
            ttl=config.cache_ttl,
            maxsize=config.cache_maxsize
        )
        
        # If no primary cache, use memory cache as primary
        if not self.primary_cache:
            self.primary_cache = self.fallback_cache
            logger.info("Using memory cache as primary cache")
    
    def get_cache_key(self, query: str, model: str, **kwargs) -> str:
        """Generate cache key from query and parameters"""
        # Create a hash of the query and parameters
        key_data = {
            "query": query,
            "model": model,
            **kwargs
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[str]:
        """Get value from cache with fallback"""
        if not config.enable_caching:
            return None
        
        # Try primary cache first
        if self.primary_cache:
            value = self.primary_cache.get(key)
            if value:
                logger.debug(f"Cache hit on primary cache for key: {key[:8]}...")
                return value
        
        # Try fallback cache if different from primary
        if self.fallback_cache and self.fallback_cache != self.primary_cache:
            value = self.fallback_cache.get(key)
            if value:
                logger.debug(f"Cache hit on fallback cache for key: {key[:8]}...")
                return value
        
        logger.debug(f"Cache miss for key: {key[:8]}...")
        return None
    
    def set(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        """Set value in cache with fallback"""
        if not config.enable_caching:
            return False
        
        success = False
        
        # Set in primary cache
        if self.primary_cache:
            success = self.primary_cache.set(key, value, ttl) or success
        
        # Set in fallback cache if different from primary
        if self.fallback_cache and self.fallback_cache != self.primary_cache:
            success = self.fallback_cache.set(key, value, ttl) or success
        
        if success:
            logger.debug(f"Cached value for key: {key[:8]}...")
        
        return success
    
    def delete(self, key: str) -> bool:
        """Delete value from all caches"""
        success = False
        
        if self.primary_cache:
            success = self.primary_cache.delete(key) or success
        
        if self.fallback_cache and self.fallback_cache != self.primary_cache:
            success = self.fallback_cache.delete(key) or success
        
        return success
    
    def clear(self) -> bool:
        """Clear all caches"""
        success = False
        
        if self.primary_cache:
            success = self.primary_cache.clear() or success
        
        if self.fallback_cache and self.fallback_cache != self.primary_cache:
            success = self.fallback_cache.clear() or success
        
        return success
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        stats = {
            "caching_enabled": config.enable_caching,
            "primary_cache_type": type(self.primary_cache).__name__ if self.primary_cache else None,
            "fallback_cache_type": type(self.fallback_cache).__name__ if self.fallback_cache else None,
        }
        
        # Add memory cache stats if available
        if isinstance(self.primary_cache, MemoryCache):
            stats["memory_cache_size"] = len(self.primary_cache.cache)
            stats["memory_cache_maxsize"] = self.primary_cache.cache.maxsize
        
        return stats

# Global cache instance
response_cache = ResponseCache() 