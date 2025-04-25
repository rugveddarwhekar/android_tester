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
    """
    Launches or brings the specified application to the foreground.
    Uses Appium's activate_app, which is generally preferred over setting
    capabilities for each launch within a test.
    """
    print(f"Action: Launching App - Package: {package_name}, Activity: {activity_name}")
    try:
        # Construct the app_id (package name)
        app_id = package_name
        # Note: activate_app doesn't directly take activity. It launches the main activity
        # or resumes the current one. If specific activity needed, other methods exist.
        driver.activate_app(app_id)
        # Add a pause for app to load
        time.sleep(5)
        # Verify current package? (Optional)
        current_pkg = driver.current_package
        if current_pkg == package_name:
             print(f"App '{package_name}' launched/activated successfully.")
             return True, f"App '{package_name}' launched/activated."
        else:
             print(f"Warning: Launched '{package_name}' but current package is '{current_pkg}'.")
             return False, f"Launched '{package_name}' but current package is '{current_pkg}'."

    except Exception as e:
        print(f"Error launching app {package_name}: {e}")
        return False, f"Error launching app {package_name}: {e}"

def click_element(driver, selector_type: str, selector_value: str, timeout: int = 10):
    """Finds and clicks an element based on selector type and value."""
    print(f"Action: Clicking Element - Type: {selector_type}, Value: '{selector_value}', Timeout: {timeout}")
    by_mapping = {
        "ACCESSIBILITY_ID": AppiumBy.ACCESSIBILITY_ID,
        "ID": AppiumBy.ID, "XPATH": AppiumBy.XPATH,
        "CLASS_NAME": AppiumBy.CLASS_NAME,
        "TEXT": (AppiumBy.XPATH, f"//*[@text='{selector_value}']")
    }
    selector_type_upper = selector_type.upper()

    if selector_type_upper not in by_mapping and selector_type_upper != "TEXT":
         msg = f"Invalid selector_type '{selector_type}'"
         print(f"Error: {msg}")
         return False, msg

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
        print("Element clicked successfully.")
        time.sleep(0.5) # Small pause after click
        return True, f"Clicked element ({selector_type}='{selector_value}')"
    except TimeoutException:
        msg = f"Element not found or not clickable within {timeout}s ({selector_type}='{selector_value}')"
        print(f"Error: {msg}")
        # take_screenshot(driver, f"error_click_timeout_{selector_value[:20]}.png") # Optionally take screenshot on error
        return False, msg
    except Exception as e:
        msg = f"Error clicking element ({selector_type}='{selector_value}'): {e}"
        print(f"Error: {msg}")
        # take_screenshot(driver, f"error_click_exception_{selector_value[:20]}.png")
        return False, msg

def input_text(driver, selector_type: str, selector_value: str, text_to_input: str, timeout: int = 10):
    """Finds an element and inputs text into it."""
    print(f"Action: Input Text - Type: {selector_type}, Value: '{selector_value}', Text: '{text_to_input}'")
    # (Implementation similar to click_element to find the element first)
    # ... find element logic using WebDriverWait and EC.visibility_of_element_located ...
    try:
        # Find element first (example using ID)
        wait = WebDriverWait(driver, timeout)
        if selector_type.upper() == "ID": # Example, add mapping like click_element
             element = wait.until(EC.visibility_of_element_located((AppiumBy.ID, selector_value)))
        else: # Add other selector types
             # Placeholder for other types
             print(f"Error: input_text only supports ID selector type in this example.")
             return False, f"Selector type {selector_type} not implemented yet for input_text"

        element.send_keys(text_to_input)
        print("Text input successful.")
        # Optionally hide keyboard if needed: driver.hide_keyboard()
        time.sleep(0.5)
        return True, f"Input '{text_to_input}' into element ({selector_type}='{selector_value}')"
    except TimeoutException:
        msg = f"Element not found within {timeout}s ({selector_type}='{selector_value}') for text input"
        print(f"Error: {msg}")
        return False, msg
    except Exception as e:
        msg = f"Error inputting text into ({selector_type}='{selector_value}'): {e}"
        print(f"Error: {msg}")
        return False, msg

def take_screenshot(driver, filename: str):
    """Takes a screenshot and saves it to the reports directory."""
    print(f"Action: Taking Screenshot - Filename: '{filename}'")
    # Construct path relative to the project root
    project_root = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))
    reports_dir = os.path.join(project_root, 'reports')
    if not os.path.exists(reports_dir):
        try:
            os.makedirs(reports_dir)
        except OSError as e:
             print(f"Error creating reports directory {reports_dir}: {e}")
             return False, f"Error creating reports directory: {e}"

    safe_filename = filename.replace("..", "").replace("/", "_").replace("\\", "_")
    filepath = os.path.join(reports_dir, safe_filename)
    try:
        success = driver.save_screenshot(filepath)
        if success:
            print(f"Screenshot saved to: {filepath}")
            return True, f"Screenshot saved to {filepath}"
        else:
             msg = f"Failed to save screenshot {safe_filename} (driver returned false)"
             print(f"Warning: {msg}")
             return False, msg
    except Exception as e:
        msg = f"Failed to save screenshot {safe_filename}: {e}"
        print(f"Error: {msg}")
        return False, msg

def wait_seconds(driver, seconds: float):
    """Pauses execution for a specified number of seconds."""
    print(f"Action: Waiting for {seconds} seconds...")
    try:
        time.sleep(float(seconds))
        print("Wait complete.")
        return True, f"Waited for {seconds} seconds."
    except ValueError:
        msg = f"Invalid number of seconds provided: {seconds}"
        print(f"Error: {msg}")
        return False, msg
    except Exception as e:
        msg = f"Error during wait: {e}"
        print(f"Error: {msg}")
        return False, msg


def wait_for_element(driver, selector_type: str, selector_value: str, timeout: int = 10, visible: bool = True):
    """Waits for an element to be present or visible."""
    state = "visible" if visible else "present"
    print(f"Action: Waiting for Element {state} - Type: {selector_type}, Value: '{selector_value}', Timeout: {timeout}")
    # (Implementation similar to click_element using WebDriverWait)
    # Use EC.presence_of_element_located or EC.visibility_of_element_located
    # ...
    try:
         # Placeholder: Implement actual wait logic here based on 'visible' flag
         wait = WebDriverWait(driver, timeout)
         if visible:
             wait.until(EC.visibility_of_element_located((AppiumBy.ACCESSIBILITY_ID, selector_value))) # Example
         else:
             wait.until(EC.presence_of_element_located((AppiumBy.ACCESSIBILITY_ID, selector_value))) # Example
         print(f"Element found and {state}.")
         return True, f"Element ({selector_type}='{selector_value}') is {state}."

    except TimeoutException:
        msg = f"Element not {state} within {timeout}s ({selector_type}='{selector_value}')"
        print(f"Error: {msg}")
        return False, msg
    except Exception as e:
         msg = f"Error waiting for element ({selector_type}='{selector_value}'): {e}"
         print(f"Error: {msg}")
         return False, msg


def press_android_key(driver, key_code_name: str):
     """Presses a standard Android key (e.g., BACK, HOME, ENTER)."""
     print(f"Action: Pressing Android Key - Key: {key_code_name}")
     key_code_upper = key_code_name.upper()
     # Map common names to AndroidKey enum values
     key_mapping = {
         "BACK": AndroidKey.BACK,
         "HOME": AndroidKey.HOME,
         "ENTER": AndroidKey.ENTER,
         "SEARCH": AndroidKey.SEARCH,
         # Add more as needed: VOLUME_UP, VOLUME_DOWN, POWER, etc.
     }
     if key_code_upper not in key_mapping:
         msg = f"Unsupported key_code_name: '{key_code_name}'. Supported: {list(key_mapping.keys())}"
         print(f"Error: {msg}")
         return False, msg
     try:
         driver.press_keycode(key_mapping[key_code_upper])
         print(f"Key '{key_code_upper}' pressed.")
         time.sleep(0.5)
         return True, f"Pressed key '{key_code_upper}'."
     except Exception as e:
         msg = f"Error pressing key '{key_code_upper}': {e}"
         print(f"Error: {msg}")
         return False, msg

# Add more common actions: swipe, get_text, assert_element_visible etc.