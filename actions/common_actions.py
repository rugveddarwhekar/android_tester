# actions/common_actions.py
import time
import os
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from appium.webdriver.extensions.android.nativekey import AndroidKey

# --- Action Functions ---
# Each function takes the driver object as the first argument,
# followed by parameters specific to the action.

def launch_app_by_package(driver, package_name: str, activity_name: str = None):
    """Launch or bring an app to foreground using package name"""
    try:
        driver.activate_app(package_name)
        time.sleep(5)
        current_pkg = driver.current_package
        if current_pkg == package_name:
            return True, f"App '{package_name}' launched successfully"
        return False, f"Launched '{package_name}' but current package is '{current_pkg}'"
    except Exception as e:
        return False, f"Error launching app {package_name}: {e}"

def click_element(driver, selector_type: str, selector_value: str, timeout: int = 10):
    """Find and click an element using specified selector"""
    by_mapping = {
        "ACCESSIBILITY_ID": AppiumBy.ACCESSIBILITY_ID,
        "ID": AppiumBy.ID, 
        "XPATH": AppiumBy.XPATH,
        "CLASS_NAME": AppiumBy.CLASS_NAME,
        "TEXT": (AppiumBy.XPATH, f"//*[@text='{selector_value}']")
    }
    selector_type_upper = selector_type.upper()

    if selector_type_upper not in by_mapping and selector_type_upper != "TEXT":
        return False, f"Invalid selector_type '{selector_type}'"

    try:
        wait = WebDriverWait(driver, timeout)
        if selector_type_upper == "TEXT":
            by = by_mapping["TEXT"][0]
            value = by_mapping["TEXT"][1]
        else:
            by = by_mapping[selector_type_upper]
            value = selector_value

        element = wait.until(EC.element_to_be_clickable((by, value)))
        element.click()
        time.sleep(0.5)
        return True, f"Clicked element ({selector_type}='{selector_value}')"
    except TimeoutException:
        return False, f"Element not found or not clickable within {timeout}s"
    except Exception as e:
        return False, f"Error clicking element: {e}"

def input_text(driver, selector_type: str, selector_value: str, text_to_input: str, timeout: int = 10):
    """Input text into an element using specified selector"""
    try:
        wait = WebDriverWait(driver, timeout)
        if selector_type.upper() == "ID":
            element = wait.until(EC.visibility_of_element_located((AppiumBy.ID, selector_value)))
        else:
            return False, f"Selector type {selector_type} not implemented for input_text"

        element.send_keys(text_to_input)
        time.sleep(0.5)
        return True, f"Input text into element ({selector_type}='{selector_value}')"
    except TimeoutException:
        return False, f"Element not found within {timeout}s"
    except Exception as e:
        return False, f"Error inputting text: {e}"

def take_screenshot(driver, filename: str):
    """Save screenshot to reports directory"""
    project_root = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))
    reports_dir = os.path.join(project_root, 'reports')
    
    if not os.path.exists(reports_dir):
        try:
            os.makedirs(reports_dir)
        except OSError as e:
            return False, f"Error creating reports directory: {e}"

    safe_filename = filename.replace("..", "").replace("/", "_").replace("\\", "_")
    filepath = os.path.join(reports_dir, safe_filename)
    
    try:
        success = driver.save_screenshot(filepath)
        if success:
            return True, f"Screenshot saved to {filepath}"
        return False, f"Failed to save screenshot {safe_filename}"
    except Exception as e:
        return False, f"Failed to save screenshot: {e}"

def wait_seconds(driver, seconds: float):
    """Pause execution for specified duration"""
    try:
        time.sleep(float(seconds))
        return True, f"Waited for {seconds} seconds"
    except ValueError:
        return False, f"Invalid wait duration: {seconds}"
    except Exception as e:
        return False, f"Error during wait: {e}"

def wait_for_element(driver, selector_type: str, selector_value: str, timeout: int = 10, visible: bool = True):
    """Wait for element to be present or visible"""
    try:
        wait = WebDriverWait(driver, timeout)
        if visible:
            wait.until(EC.visibility_of_element_located((AppiumBy.ACCESSIBILITY_ID, selector_value)))
        else:
            wait.until(EC.presence_of_element_located((AppiumBy.ACCESSIBILITY_ID, selector_value)))
        return True, f"Element ({selector_type}='{selector_value}') is {'visible' if visible else 'present'}"
    except TimeoutException:
        return False, f"Element not found within {timeout}s"
    except Exception as e:
        return False, f"Error waiting for element: {e}"

def press_android_key(driver, key_code_name: str):
    """Press a standard Android key (BACK, HOME, ENTER, etc.)"""
    key_code_upper = key_code_name.upper()
    key_mapping = {
        "BACK": AndroidKey.BACK,
        "HOME": AndroidKey.HOME,
        "ENTER": AndroidKey.ENTER,
        "SEARCH": AndroidKey.SEARCH,
    }
    
    if key_code_upper not in key_mapping:
        return False, f"Unsupported key: '{key_code_name}'"

    try:
        driver.press_keycode(key_mapping[key_code_upper])
        time.sleep(0.5)
        return True, f"Pressed key '{key_code_upper}'"
    except Exception as e:
        return False, f"Error pressing key: {e}"

# Add more common actions: swipe, get_text, assert_element_visible etc.