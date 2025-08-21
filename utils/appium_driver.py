from appium import webdriver
from appium.options.android import UiAutomator2Options
from .config_loader import load_capabilities, get_appium_server_url
import sys
import time
import subprocess
import shlex
import requests

_driver = None

def check_device_connection():
    """Check if Android device is connected and accessible via ADB"""
    try:
        result = subprocess.run(
            shlex.split("adb devices"),
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            return False, "ADB command failed. Is Android SDK platform-tools installed and in PATH?"
        
        lines = result.stdout.strip().splitlines()
        if len(lines) <= 1:
            return False, "No devices found. Connect your Android device via USB and enable USB debugging."
        
        authorized_devices = [line for line in lines[1:] if line.strip() and 'device' in line and 'unauthorized' not in line]
        if not authorized_devices:
            return False, "No authorized devices found. Check USB debugging authorization on your device."
        
        return True, f"Found {len(authorized_devices)} device(s): {[dev.split()[0] for dev in authorized_devices]}"
        
    except FileNotFoundError:
        return False, "ADB not found. Install Android SDK platform-tools and add to PATH."
    except subprocess.TimeoutExpired:
        return False, "ADB command timed out. Check device connection."
    except Exception as e:
        return False, f"Error checking device connection: {e}"

def check_appium_server():
    """Check if Appium server is running"""
    try:
        appium_url = get_appium_server_url()
        response = requests.get(f"{appium_url}/status", timeout=5)
        if response.status_code == 200:
            return True, "Appium server is running"
        else:
            return False, f"Appium server responded with status {response.status_code}"
    except requests.exceptions.ConnectionError:
        return False, "Cannot connect to Appium server. Start Appium server first (default: http://localhost:4723)"
    except requests.exceptions.Timeout:
        return False, "Appium server connection timed out"
    except Exception as e:
        return False, f"Error checking Appium server: {e}"

def validate_capabilities(capabilities):
    """Validate that required capabilities are present and valid"""
    required_caps = ['appium:deviceName']
    
    for cap in required_caps:
        if cap not in capabilities:
            return False, f"Missing required capability: {cap}"
        if not capabilities[cap] or capabilities[cap] == "YOUR_DEVICE_ID":
            return False, f"Invalid capability value for {cap}. Please configure it in config/capabilities.json"
    
    return True, "Capabilities are valid"

def initialize_driver():
    """Initialize and return Appium driver instance with comprehensive error checking"""
    global _driver
    if _driver is not None:
        return _driver

    print("Checking system requirements...")
    
    device_ok, device_msg = check_device_connection()
    if not device_ok:
        print(f"Device check failed: {device_msg}")
        return None
    print(f"Device check: {device_msg}")
    
    server_ok, server_msg = check_appium_server()
    if not server_ok:
        print(f"Appium server check failed: {server_msg}")
        return None
    print(f"Server check: {server_msg}")
    
    print("Loading capabilities...")
    capabilities = load_capabilities()
    if not capabilities:
        print("Failed to load capabilities from config/capabilities.json")
        return None
    
    caps_ok, caps_msg = validate_capabilities(capabilities)
    if not caps_ok:
        print(f"Capabilities validation failed: {caps_msg}")
        return None
    print(f"Capabilities: {caps_msg}")
    
    appium_server_url = get_appium_server_url()
    print(f"Initializing Appium driver...")
    print(f"Server URL: {appium_server_url}")
    print(f"Device: {capabilities.get('appium:deviceName')}")
    print(f"Package: {capabilities.get('appium:appPackage', 'Not specified')}")

    options = UiAutomator2Options().load_capabilities(capabilities)

    try:
        print("Connecting to Appium server...")
        _driver = webdriver.Remote(appium_server_url, options=options)
        _driver.implicitly_wait(5)
        time.sleep(2)
        
        try:
            device_info = _driver.capabilities
            print(f"Driver initialized successfully!")
            print(f"Connected to: {device_info.get('deviceName', 'Unknown device')}")
            print(f"Platform: {device_info.get('platformName', 'Unknown')}")
            print(f"Automation: {device_info.get('automationName', 'Unknown')}")
            return _driver
        except Exception as e:
            print(f"Driver created but verification failed: {e}")
            return _driver
            
    except Exception as e:
        _driver = None
        error_msg = str(e)
        
        if "ECONNREFUSED" in error_msg:
            print(f"Connection refused. Make sure Appium server is running on {appium_server_url}")
        elif "timeout" in error_msg.lower():
            print(f"Connection timeout. Check if Appium server is running and device is connected")
        elif "device" in error_msg.lower() and "not found" in error_msg.lower():
            print(f"Device not found. Check device connection and capabilities configuration")
        elif "capabilities" in error_msg.lower():
            print(f"Invalid capabilities: {error_msg}")
        else:
            print(f"Driver initialization failed: {error_msg}")
        
        return None

def get_driver():
    """Get current driver instance, initialize if needed"""
    if _driver is None:
        return initialize_driver()
    return _driver

def quit_driver():
    """Quit Appium driver session"""
    global _driver
    if _driver:
        try:
            print("Closing Appium driver session...")
            _driver.quit()
            print("Driver session closed")
        except Exception as e:
            print(f"Error closing driver: {e}")
        finally:
            _driver = None