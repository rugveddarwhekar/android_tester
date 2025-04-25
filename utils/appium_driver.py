# utils/appium_driver.py
from appium import webdriver
from appium.options.android import UiAutomator2Options
from .config_loader import load_capabilities, get_appium_server_url
import sys
import time

_driver = None

def initialize_driver():
    """Initialize and return Appium driver instance"""
    global _driver
    if _driver is not None:
        return _driver

    capabilities = load_capabilities()
    appium_server_url = get_appium_server_url()

    if not capabilities:
        return None

    if 'appium:deviceName' not in capabilities or not capabilities.get('appium:deviceName'):
        return None

    options = UiAutomator2Options().load_capabilities(capabilities)

    try:
        _driver = webdriver.Remote(appium_server_url, options=options)
        _driver.implicitly_wait(5)
        time.sleep(2)
        return _driver
    except Exception as e:
        _driver = None
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
            _driver.quit()
        except Exception:
            pass
        finally:
            _driver = None