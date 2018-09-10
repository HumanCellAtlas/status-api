import functools
import json
import time

# hand-rolled cache to ensure storage in the global lambda execution context
GLOBAL_CACHE = dict()


def global_cache(ttl: int):
    """
    @global_cache stores cached values in the lambda context
    """
    def decorate(func):
        @functools.wraps(func)
        def call(*args, **kwargs):
            global GLOBAL_CACHE
            key = hash(json.dumps(args, sort_keys=True) + json.dumps(kwargs, sort_keys=True))
            if key in GLOBAL_CACHE:
                result, timeout_time = GLOBAL_CACHE[key]
                if timeout_time > time.time():
                    return result
            GLOBAL_CACHE[key] = (func(*args, **kwargs), time.time() + ttl)
            return GLOBAL_CACHE[key][0]
        return call
    return decorate
