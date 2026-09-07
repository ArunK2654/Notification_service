import time
from functools import wraps

def log_execution(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"{func.__name__} started")
        start = time.perf_counter()

        result = func(*args, **kwargs)

        end = time.perf_counter()
        print(f"{func.__name__} finished " f"in {end - start:.4f} seconds")
        return result
    return wrapper

