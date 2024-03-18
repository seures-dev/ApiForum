
import time
from functools import wraps

def time_tracker(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        s = time.time()
        result = func(*args, **kwargs)
        print(f"{func.__name__}: {time.time()-s}")
        return result
    return wrapper
