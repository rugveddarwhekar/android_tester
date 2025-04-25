# utils/config_loader.py
import json
import os

def load_capabilities():
    """Loads Appium capabilities from the JSON file."""
    # Construct path relative to this file's location
    config_dir = os.path.dirname(__file__) # utils directory
    capabilities_path = os.path.join(config_dir, '..', 'config', 'capabilities.json')
    # Normalize path for consistency
    capabilities_path = os.path.normpath(capabilities_path)

    try:
        with open(capabilities_path, 'r') as f:
            caps = json.load(f)
        print(f"Loaded capabilities from: {capabilities_path}")

        # Optional: Add logic here later to load device name or other
        # overrides from environment variables or another config file if needed.
        # env_device_name = os.getenv('APPIUM_DEVICE_NAME')
        # if env_device_name:
        #     caps['appium:deviceName'] = env_device_name

        if 'platformName' not in caps:
             caps['platformName'] = 'Android' # Default if missing

        return caps

    except FileNotFoundError:
        print(f"Error: capabilities.json not found at {capabilities_path}")
        return None
    except json.JSONDecodeError:
        print(f"Error: {capabilities_path} contains invalid JSON.")
        return None
    except Exception as e:
        print(f"Error loading capabilities: {e}")
        return None

def get_appium_server_url():
    """Gets the Appium server URL (can be extended later)."""
    # For now, hardcode the default. Can be loaded from config/env later.
    url = 'http://localhost:4723'
    # print(f"Using Appium Server URL: {url}") # Can be noisy
    return url