from functools import wraps
from ..shared import HELP_STORAGE

def get_string(command:str):
    def decorator(func):
        HELP_STORAGE.data.update({command:func.__doc__})
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        return wrapper
    return decorator