from functools import wraps
from ..shared import HELP_STORAGE

def get_string(command:str):
    def decorator(func):
        if command in HELP_STORAGE.data:
            HELP_STORAGE.data[command] += f"\n{func.__doc__}"
        else:
            HELP_STORAGE.data.update({command:func.__doc__})
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        return wrapper
    return decorator