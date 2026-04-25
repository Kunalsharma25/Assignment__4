import yaml
from typing import Dict

def load_config(path="config.yaml") -> Dict:
    """Loads configuration from a YAML file."""
    try:
        with open(path, "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: {path} not found. Using default empty config.")
        return {}
    except Exception as e:
        print(f"Error loading config: {e}")
        return {}
