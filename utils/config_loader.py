# utils/config_loader.py
import json
import os

def load_capabilities():
    """Load Appium capabilities from JSON file"""
    config_dir = os.path.dirname(__file__)
    capabilities_path = os.path.normpath(os.path.join(config_dir, '..', 'config', 'capabilities.json'))

    try:
        with open(capabilities_path, 'r') as f:
            caps = json.load(f)

        if 'platformName' not in caps:
            caps['platformName'] = 'Android'

        return caps

    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return None
    except Exception:
        return None

def get_appium_server_url():
    """Get Appium server URL"""
    return 'http://localhost:4723'