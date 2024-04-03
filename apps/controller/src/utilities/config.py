import os
import json
import yaml


def required_env(key: str, default = None) -> str:
    """
    Retrieves the key from the os.getenv() method. If
    the value is None, raises an Exception.
    """
    value = os.getenv(key, default)
    if value is None:
        raise Exception(f'{key} is a required environment variable. Cannot be None')

    return value


def load_schema(file: str) -> dict:
    """
    Loads the json schema as a dictionary
    """
    with open(file, 'r') as f:
        return json.load(f)


def convert_to_seconds(interval: str) -> int:
    """
    Converts a string interval to seconds
    For example: '30s' => 30, '1m' => 60,  '5m' => 300
    """
    seconds_per_unit = {
        "s": 1,
        "m": 60,
        "h": 3600,
        "d": 86400,
        "w": 604800
    }
    return int(interval[:-1]) * seconds_per_unit[interval[-1]]
