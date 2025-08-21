import json
import os

def load_capabilities():
    """Load Appium capabilities from JSON file with enhanced error handling"""
    config_dir = os.path.dirname(__file__)
    capabilities_path = os.path.normpath(os.path.join(config_dir, '..', 'config', 'capabilities.json'))

    try:
        with open(capabilities_path, 'r') as f:
            caps = json.load(f)

        if 'platformName' not in caps:
            caps['platformName'] = 'Android'

        return caps

    except FileNotFoundError:
        print(f"Capabilities file not found: {capabilities_path}")
        print("Create config/capabilities.json with your device configuration")
        return None
    except json.JSONDecodeError as e:
        print(f"Invalid JSON in capabilities file: {e}")
        print("Check the syntax of config/capabilities.json")
        return None
    except Exception as e:
        print(f"Error loading capabilities: {e}")
        return None

def get_appium_server_url():
    """Get Appium server URL with validation"""
    return 'http://localhost:4723'

def create_default_capabilities():
    """Create a default capabilities.json file with instructions"""
    config_dir = os.path.dirname(__file__)
    capabilities_path = os.path.normpath(os.path.join(config_dir, '..', 'config', 'capabilities.json'))
    
    default_caps = {
        "platformName": "Android",
        "appium:automationName": "UiAutomator2",
        "appium:deviceName": "YOUR_DEVICE_ID",
        "appium:appPackage": None,
        "appium:appActivity": None,
        "appium:noReset": True,
        "appium:newCommandTimeout": 3600
    }
    
    try:
        with open(capabilities_path, 'w') as f:
            json.dump(default_caps, f, indent=4)
        print(f"Created default capabilities file: {capabilities_path}")
        print("Edit this file with your device ID and app package")
        return True
    except Exception as e:
        print(f"Failed to create capabilities file: {e}")
        return False