# task_interceptor.py
from processor_manager import should_offload
from remote_executor import execute_remotely

def offload_if_needed(func):
    def wrapper(*args, **kwargs):
        if should_offload():
            return execute_remotely(func.__name__, args, kwargs)
        return func(*args, **kwargs)
    return wrapper

