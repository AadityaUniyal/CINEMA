from functools import wraps
import time
import hashlib
import json

class CacheManager:
    def __init__(self):
        self.cache = {}
        self.cache_times = {}
    
    def get(self, key):
        """Get cached value"""
        if key in self.cache:
            return self.cache[key]
        return None
    
    def set(self, key, value, ttl=300):
        """Set cached value with TTL (time to live in seconds)"""
        self.cache[key] = value
        self.cache_times[key] = time.time() + ttl
    
    def is_valid(self, key):
        """Check if cache is still valid"""
        if key not in self.cache_times:
            return False
        return time.time() < self.cache_times[key]
    
    def clear(self):
        """Clear all cache"""
        self.cache.clear()
        self.cache_times.clear()
    
    def clear_expired(self):
        """Remove expired cache entries"""
        current_time = time.time()
        expired_keys = [k for k, v in self.cache_times.items() if current_time >= v]
        for key in expired_keys:
            del self.cache[key]
            del self.cache_times[key]

# Global cache instance
cache = CacheManager()

def cached(ttl=300):
    """Decorator for caching function results"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{f.__name__}:{hashlib.md5(str(args).encode() + str(kwargs).encode()).hexdigest()}"
            
            if cache.is_valid(cache_key):
                return cache.get(cache_key)
            
            result = f(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result
        
        return decorated
    return decorator
