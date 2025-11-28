from functools import wraps
import time
import hashlib
import json

class CacheManager:
    def __init__(self):
        self.cache = {}
        self.cache_times = {}
    
    def get(self, key):
        if key in self.cache:
            return self.cache[key]
        return None
    
    def set(self, key, value, ttl=300):
        self.cache[key] = value
        self.cache_times[key] = time.time() + ttl
    
    def is_valid(self, key):
        if key not in self.cache_times:
            return False
        return time.time() < self.cache_times[key]
    
    def clear(self):
        self.cache.clear()
        self.cache_times.clear()
    
    def clear_expired(self):
        current_time = time.time()
        expired_keys = [k for k, v in self.cache_times.items() if current_time >= v]
        for key in expired_keys:
            del self.cache[key]
            del self.cache_times[key]

cache = CacheManager()

def cached(ttl=300):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            cache_key = f"{f.__name__}:{hashlib.md5(str(args).encode() + str(kwargs).encode()).hexdigest()}"
            
            if cache.is_valid(cache_key):
                return cache.get(cache_key)
            
            result = f(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result
        
        return decorated
    return decorator
