import os


def required_env(key) -> str:
    """
    Retrieves the key from the os.getenv() method. If
    the value is None, raises an Exception.
    """
    value = os.getenv(key)
    if value is None:
        raise Exception(f'{key} is a required environment variable. Cannot be None')
    
    return value
