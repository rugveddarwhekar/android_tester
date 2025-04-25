# utils/appium_driver.py
from appium import webdriver
from appium.options.android import UiAutomator2Options
from .config_loader import load_capabilities, get_appium_server_url # Use local import
import sys
import time

_driver = None # Singleton instance for the current test run

def initialize_driver():
    """Initializes and returns the Appium driver instance."""
    global _driver
    if _driver is not None:
        print("Driver already initialized.")
        return _driver

    print("Initializing Appium driver...")
    capabilities = load_capabilities()
    appium_server_url = get_appium_server_url()

    if not capabilities:
        print("Error: Failed to load capabilities. Cannot initialize driver.")
        return None # Return None on failure

    if 'appium:deviceName' not in capabilities or not capabilities.get('appium:deviceName'):
         print("Error: 'appium:deviceName' not set in capabilities.json")
         return None

    print(f"Attempting connection to Appium server: {appium_server_url}")
    print(f"Using capabilities: {capabilities}")

    options = UiAutomator2Options().load_capabilities(capabilities)

    try:
        _driver = webdriver.Remote(appium_server_url, options=options)
        # Set a default implicit wait - adjust as needed
        _driver.implicitly_wait(5)
        print("Appium driver initialized successfully.")
        # Add a small pause after initialization
        time.sleep(2)
        return _driver
    except Exception as e:
        print(f"\n!!! Error initializing Appium driver: {e} !!!")
        print("Please check: Appium server status, device connection, capabilities.")
        _driver = None # Ensure driver is None on failure
        return None

def get_driver():
    """Returns the current driver instance, initializing if needed."""
    # This ensures driver is initialized only once when first requested
    if _driver is None:
        return initialize_driver()
    return _driver

def quit_driver():
    """Quits the Appium driver session."""
    global _driver
    if _driver:
        print("Quitting Appium driver session...")
        try:
            _driver.quit()
            print("Appium driver session quit.")
        except Exception as e:
            print(f"Error quitting Appium driver: {e}")
        finally:
             _driver = None # Reset driver variable
    else:
        print("Driver not initialized or already quit.")