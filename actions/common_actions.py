# actions/common_actions.py
import time
import os
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from appium.webdriver.extensions.android.nativekey import AndroidKey

def get_by_mapping(selector_value: str = None, include_text: bool = True):
    """Helper function to create consistent by_mapping dictionaries"""
    mapping = {
        "ACCESSIBILITY_ID": AppiumBy.ACCESSIBILITY_ID,
        "ID": AppiumBy.ID, 
        "XPATH": AppiumBy.XPATH,
        "CLASS_NAME": AppiumBy.CLASS_NAME,
        "UIAUTOMATOR": AppiumBy.ANDROID_UIAUTOMATOR
    }
    if include_text and selector_value:
        mapping["TEXT"] = (AppiumBy.XPATH, f"//*[@text='{selector_value}']")
    return mapping

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

def close_app(driver, package_name: str):
    """Close the specified application"""
    try:
        driver.terminate_app(package_name)
        time.sleep(1)
        return True, f"App '{package_name}' closed successfully"
    except Exception as e:
        return False, f"Error closing app {package_name}: {e}"

def click_element(driver, selector_type: str, selector_value: str, timeout: int = 10):
    """Find and click an element using specified selector"""
    by_mapping = get_by_mapping(selector_value)
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

def long_click_element(driver, selector_type: str, selector_value: str, duration_ms: int = 1000, timeout: int = 10):
    """Perform a long press on an element"""
    try:
        wait = WebDriverWait(driver, timeout)
        by_mapping = get_by_mapping(selector_value)
        selector_type_upper = selector_type.upper()

        if selector_type_upper not in by_mapping and selector_type_upper != "TEXT":
            return False, f"Invalid selector_type '{selector_type}'"

        if selector_type_upper == "TEXT":
            by = by_mapping["TEXT"][0]
            value = by_mapping["TEXT"][1]
        else:
            by = by_mapping[selector_type_upper]
            value = selector_value

        element = wait.until(EC.presence_of_element_located((by, value)))
        driver.execute_script('mobile: longClickGesture', {
            'elementId': element.id,
            'duration': duration_ms
        })
        time.sleep(0.5)
        return True, f"Long clicked element ({selector_type}='{selector_value}')"
    except TimeoutException:
        return False, f"Element not found within {timeout}s"
    except Exception as e:
        return False, f"Error long clicking element: {e}"

def input_text(driver, selector_type: str, selector_value: str, text_to_input: str, clear_first: bool = True, timeout: int = 10):
    """Input text into an element using specified selector"""
    try:
        wait = WebDriverWait(driver, timeout)
        by_mapping = get_by_mapping(selector_value)
        selector_type_upper = selector_type.upper()

        if selector_type_upper not in by_mapping:
            return False, f"Selector type {selector_type} not implemented for input_text"

        element = wait.until(EC.visibility_of_element_located((by_mapping[selector_type_upper], selector_value)))
        
        if clear_first:
            element.clear()
            time.sleep(0.2)
            
        element.send_keys(text_to_input)
        time.sleep(0.5)
        return True, f"Input text into element ({selector_type}='{selector_value}')"
    except TimeoutException:
        return False, f"Element not found within {timeout}s"
    except Exception as e:
        return False, f"Error inputting text: {e}"

def clear_text_input(driver, selector_type: str, selector_value: str, timeout: int = 10):
    """Clear text from an input element"""
    try:
        wait = WebDriverWait(driver, timeout)
        by_mapping = get_by_mapping(selector_value)
        selector_type_upper = selector_type.upper()

        if selector_type_upper not in by_mapping:
            return False, f"Selector type {selector_type} not implemented for clear_text_input"

        element = wait.until(EC.presence_of_element_located((by_mapping[selector_type_upper], selector_value)))
        element.clear()
        time.sleep(0.5)
        return True, f"Cleared text from element ({selector_type}='{selector_value}')"
    except TimeoutException:
        return False, f"Element not found within {timeout}s"
    except Exception as e:
        return False, f"Error clearing text: {e}"

def get_element_text(driver, selector_type: str, selector_value: str, timeout: int = 10):
    """Get the text content of an element"""
    try:
        wait = WebDriverWait(driver, timeout)
        by_mapping = get_by_mapping(selector_value)
        selector_type_upper = selector_type.upper()

        if selector_type_upper not in by_mapping and selector_type_upper != "TEXT":
            return False, f"Invalid selector_type '{selector_type}'"

        if selector_type_upper == "TEXT":
            by = by_mapping["TEXT"][0]
            value = by_mapping["TEXT"][1]
        else:
            by = by_mapping[selector_type_upper]
            value = selector_value

        element = wait.until(EC.presence_of_element_located((by, value)))
        text = element.text
        return True, f"Element text: {text}"
    except TimeoutException:
        return False, f"Element not found within {timeout}s"
    except Exception as e:
        return False, f"Error getting element text: {e}"

def get_element_attribute(driver, selector_type: str, selector_value: str, attribute_name: str, timeout: int = 10):
    """Get the value of a specific attribute of an element"""
    try:
        wait = WebDriverWait(driver, timeout)
        by_mapping = get_by_mapping(selector_value)
        selector_type_upper = selector_type.upper()

        if selector_type_upper not in by_mapping and selector_type_upper != "TEXT":
            return False, f"Invalid selector_type '{selector_type}'"

        if selector_type_upper == "TEXT":
            by = by_mapping["TEXT"][0]
            value = by_mapping["TEXT"][1]
        else:
            by = by_mapping[selector_type_upper]
            value = selector_value

        element = wait.until(EC.presence_of_element_located((by, value)))
        attribute_value = element.get_attribute(attribute_name)
        return True, f"Element {attribute_name}: {attribute_value}"
    except TimeoutException:
        return False, f"Element not found within {timeout}s"
    except Exception as e:
        return False, f"Error getting element attribute: {e}"

def swipe_screen(driver, direction: str, percent: int = 75, duration_ms: int = 400):
    """Swipe the screen in a specified direction"""
    try:
        screen_size = driver.get_window_size()
        width = screen_size['width']
        height = screen_size['height']
        
        if direction.upper() == "UP":
            start_x, start_y = width // 2, int(height * (1 - percent/100))
            end_x, end_y = width // 2, int(height * (percent/100))
        elif direction.upper() == "DOWN":
            start_x, start_y = width // 2, int(height * (percent/100))
            end_x, end_y = width // 2, int(height * (1 - percent/100))
        elif direction.upper() == "LEFT":
            start_x, start_y = int(width * (1 - percent/100)), height // 2
            end_x, end_y = int(width * (percent/100)), height // 2
        elif direction.upper() == "RIGHT":
            start_x, start_y = int(width * (percent/100)), height // 2
            end_x, end_y = int(width * (1 - percent/100)), height // 2
        else:
            return False, f"Invalid direction: {direction}"
            
        driver.swipe(start_x, start_y, end_x, end_y, duration_ms)
        time.sleep(0.5)
        return True, f"Swiped screen {direction.lower()}"
    except Exception as e:
        return False, f"Error swiping screen: {e}"

def swipe_on_element(driver, selector_type: str, selector_value: str, direction: str, percent: int = 75, duration_ms: int = 400, timeout: int = 10):
    """Swipe starting from the center of an element"""
    try:
        wait = WebDriverWait(driver, timeout)
        by_mapping = get_by_mapping(selector_value)
        selector_type_upper = selector_type.upper()

        if selector_type_upper not in by_mapping and selector_type_upper != "TEXT":
            return False, f"Invalid selector_type '{selector_type}'"

        if selector_type_upper == "TEXT":
            by = by_mapping["TEXT"][0]
            value = by_mapping["TEXT"][1]
        else:
            by = by_mapping[selector_type_upper]
            value = selector_value

        element = wait.until(EC.presence_of_element_located((by, value)))
        element_location = element.location
        element_size = element.size
        
        # Calculate center of element
        center_x = element_location['x'] + element_size['width'] // 2
        center_y = element_location['y'] + element_size['height'] // 2
        
        # Calculate swipe distance based on screen size
        screen_size = driver.get_window_size()
        width = screen_size['width']
        height = screen_size['height']
        
        if direction.upper() == "UP":
            start_x, start_y = center_x, center_y
            end_x, end_y = center_x, int(center_y - height * percent / 100)
        elif direction.upper() == "DOWN":
            start_x, start_y = center_x, center_y
            end_x, end_y = center_x, int(center_y + height * percent / 100)
        elif direction.upper() == "LEFT":
            start_x, start_y = center_x, center_y
            end_x, end_y = int(center_x - width * percent / 100), center_y
        elif direction.upper() == "RIGHT":
            start_x, start_y = center_x, center_y
            end_x, end_y = int(center_x + width * percent / 100), center_y
        else:
            return False, f"Invalid direction: {direction}"
            
        driver.swipe(start_x, start_y, end_x, end_y, duration_ms)
        time.sleep(0.5)
        return True, f"Swiped {direction.lower()} on element ({selector_type}='{selector_value}')"
    except TimeoutException:
        return False, f"Element not found within {timeout}s"
    except Exception as e:
        return False, f"Error swiping on element: {e}"

def scroll_to_element(driver, target_selector_type: str, target_selector_value: str, scrollable_selector_type: str = None, scrollable_selector_value: str = None, direction: str = "VERTICAL", max_swipes: int = 5):
    """Scroll until an element is visible"""
    try:
        by_mapping = get_by_mapping(target_selector_value)
        target_selector_type_upper = target_selector_type.upper()

        if target_selector_type_upper not in by_mapping and target_selector_type_upper != "TEXT":
            return False, f"Invalid target selector_type '{target_selector_type}'"

        if target_selector_type_upper == "TEXT":
            target_by = by_mapping["TEXT"][0]
            target_value = by_mapping["TEXT"][1]
        else:
            target_by = by_mapping[target_selector_type_upper]
            target_value = target_selector_value

        # Try to find the element first
        try:
            WebDriverWait(driver, 2).until(EC.presence_of_element_located((target_by, target_value)))
            return True, "Element already visible"
        except TimeoutException:
            pass

        # If not found, scroll to find it
        for i in range(max_swipes):
            try:
                # Try to find element after each swipe
                WebDriverWait(driver, 1).until(EC.presence_of_element_located((target_by, target_value)))
                return True, f"Element found after {i+1} swipes"
            except TimeoutException:
                # Perform swipe
                if direction.upper() == "VERTICAL":
                    swipe_screen(driver, "UP", 75, 400)
                else:
                    swipe_screen(driver, "LEFT", 75, 400)
                time.sleep(0.5)

        return False, f"Element not found after {max_swipes} swipes"
    except Exception as e:
        return False, f"Error scrolling to element: {e}"

def pinch_zoom(driver, percent: int = 200, steps: int = 50):
    """Perform a pinch (zoom out) or zoom (pinch open) gesture"""
    try:
        screen_size = driver.get_window_size()
        center_x = screen_size['width'] // 2
        center_y = screen_size['height'] // 2
        
        if percent > 100:  # Zoom in
            driver.execute_script('mobile: pinchOpenGesture', {
                'left': center_x - 100,
                'top': center_y - 100,
                'width': 200,
                'height': 200,
                'percent': percent / 100,
                'steps': steps
            })
        else:  # Zoom out
            driver.execute_script('mobile: pinchCloseGesture', {
                'left': center_x - 100,
                'top': center_y - 100,
                'width': 200,
                'height': 200,
                'percent': percent / 100,
                'steps': steps
            })
        
        time.sleep(0.5)
        return True, f"Pinch/zoom gesture completed ({percent}%)"
    except Exception as e:
        return False, f"Error performing pinch/zoom: {e}"

def press_android_key(driver, key_code_name: str):
    """Press a standard Android key (BACK, HOME, ENTER, etc.)"""
    key_code_upper = key_code_name.upper()
    key_mapping = {
        "BACK": AndroidKey.BACK,
        "HOME": AndroidKey.HOME,
        "ENTER": AndroidKey.ENTER,
        "SEARCH": AndroidKey.SEARCH,
        "DPAD_UP": AndroidKey.DPAD_UP,
        "DPAD_DOWN": AndroidKey.DPAD_DOWN,
        "DPAD_LEFT": AndroidKey.DPAD_LEFT,
        "DPAD_RIGHT": AndroidKey.DPAD_RIGHT,
        "DPAD_CENTER": AndroidKey.DPAD_CENTER,
        "VOLUME_UP": AndroidKey.VOLUME_UP,
        "VOLUME_DOWN": AndroidKey.VOLUME_DOWN,
        "POWER": AndroidKey.POWER,
        "CAMERA": AndroidKey.CAMERA,
        "MENU": AndroidKey.MENU
    }
    
    if key_code_upper not in key_mapping:
        return False, f"Unsupported key: '{key_code_name}'"

    try:
        driver.press_keycode(key_mapping[key_code_upper])
        time.sleep(0.5)
        return True, f"Pressed key '{key_code_upper}'"
    except Exception as e:
        return False, f"Error pressing key: {e}"

def hide_keyboard(driver):
    """Attempts to hide the software keyboard"""
    try:
        driver.hide_keyboard()
        time.sleep(0.5)
        return True, "Keyboard hidden"
    except Exception as e:
        return False, f"Error hiding keyboard: {e}"

def open_notifications(driver):
    """Opens the Android notification shade"""
    try:
        driver.open_notifications()
        time.sleep(1)
        return True, "Notifications opened"
    except Exception as e:
        return False, f"Error opening notifications: {e}"

def open_quick_settings(driver):
    """Opens the Android quick settings panel"""
    try:
        # Swipe down twice to open quick settings
        swipe_screen(driver, "DOWN", 25, 200)
        time.sleep(0.5)
        swipe_screen(driver, "DOWN", 25, 200)
        time.sleep(1)
        return True, "Quick settings opened"
    except Exception as e:
        return False, f"Error opening quick settings: {e}"

def lock_device(driver, seconds: int = 0):
    """Locks the device screen"""
    try:
        if seconds > 0:
            driver.lock(seconds)
        else:
            driver.lock()
        time.sleep(1)
        return True, f"Device locked for {seconds} seconds" if seconds > 0 else "Device locked"
    except Exception as e:
        return False, f"Error locking device: {e}"

def unlock_device(driver):
    """Attempts to unlock the device"""
    try:
        driver.unlock()
        time.sleep(1)
        return True, "Device unlocked"
    except Exception as e:
        return False, f"Error unlocking device: {e}"

def set_rotation(driver, orientation: str):
    """Sets the device screen orientation"""
    try:
        orientation = orientation.upper()
        if orientation not in ["PORTRAIT", "LANDSCAPE"]:
            return False, f"Invalid orientation: {orientation}"
        
        driver.orientation = orientation
        time.sleep(1)
        return True, f"Device orientation set to {orientation}"
    except Exception as e:
        return False, f"Error setting device orientation: {e}"

def shake_device(driver):
    """Simulates shaking the device (emulator feature)"""
    try:
        driver.execute_script('mobile: shake')
        time.sleep(0.5)
        return True, "Device shaken"
    except Exception as e:
        return False, f"Error shaking device: {e}"

def fingerprint_auth(driver, finger_id: int = 1):
    """Simulates successful fingerprint auth (emulator feature)"""
    try:
        driver.execute_script('mobile: fingerprint', {'fingerprintId': finger_id})
        time.sleep(0.5)
        return True, f"Fingerprint authentication simulated (ID: {finger_id})"
    except Exception as e:
        return False, f"Error simulating fingerprint auth: {e}"

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
        by_mapping = get_by_mapping(selector_value)
        selector_type_upper = selector_type.upper()

        if selector_type_upper not in by_mapping and selector_type_upper != "TEXT":
            return False, f"Invalid selector_type '{selector_type}'"

        if selector_type_upper == "TEXT":
            by = by_mapping["TEXT"][0]
            value = by_mapping["TEXT"][1]
        else:
            by = by_mapping[selector_type_upper]
            value = selector_value

        if visible:
            wait.until(EC.visibility_of_element_located((by, value)))
        else:
            wait.until(EC.presence_of_element_located((by, value)))
        return True, f"Element ({selector_type}='{selector_value}') is {'visible' if visible else 'present'}"
    except TimeoutException:
        return False, f"Element not found within {timeout}s"
    except Exception as e:
        return False, f"Error waiting for element: {e}"

def wait_for_element_to_disappear(driver, selector_type: str, selector_value: str, timeout: int = 10):
    """Wait for element to become invisible or not present"""
    try:
        wait = WebDriverWait(driver, timeout)
        by_mapping = get_by_mapping(selector_value)
        selector_type_upper = selector_type.upper()

        if selector_type_upper not in by_mapping and selector_type_upper != "TEXT":
            return False, f"Invalid selector_type '{selector_type}'"

        if selector_type_upper == "TEXT":
            by = by_mapping["TEXT"][0]
            value = by_mapping["TEXT"][1]
        else:
            by = by_mapping[selector_type_upper]
            value = selector_value

        wait.until_not(EC.presence_of_element_located((by, value)))
        return True, f"Element ({selector_type}='{selector_value}') disappeared"
    except TimeoutException:
        return False, f"Element still present after {timeout}s"
    except Exception as e:
        return False, f"Error waiting for element to disappear: {e}"

def verify_element_visible(driver, selector_type: str, selector_value: str, fail_test_if_not: bool = True):
    """Check if an element is currently visible on screen"""
    try:
        by_mapping = get_by_mapping(selector_value)
        selector_type_upper = selector_type.upper()

        if selector_type_upper not in by_mapping and selector_type_upper != "TEXT":
            return False, f"Invalid selector_type '{selector_type}'"

        if selector_type_upper == "TEXT":
            by = by_mapping["TEXT"][0]
            value = by_mapping["TEXT"][1]
        else:
            by = by_mapping[selector_type_upper]
            value = selector_value

        element = driver.find_element(by, value)
        is_visible = element.is_displayed()
        
        if is_visible:
            return True, f"Element ({selector_type}='{selector_value}') is visible"
        else:
            message = f"Element ({selector_type}='{selector_value}') is not visible"
            return not fail_test_if_not, message
    except NoSuchElementException:
        message = f"Element ({selector_type}='{selector_value}') not found"
        return not fail_test_if_not, message
    except Exception as e:
        message = f"Error checking element visibility: {e}"
        return not fail_test_if_not, message

def verify_element_text(driver, selector_type: str, selector_value: str, expected_text: str, match_type: str = "EXACT", fail_test_if_not: bool = True):
    """Check if an element's text matches expected value"""
    try:
        by_mapping = get_by_mapping(selector_value)
        selector_type_upper = selector_type.upper()

        if selector_type_upper not in by_mapping and selector_type_upper != "TEXT":
            return False, f"Invalid selector_type '{selector_type}'"

        if selector_type_upper == "TEXT":
            by = by_mapping["TEXT"][0]
            value = by_mapping["TEXT"][1]
        else:
            by = by_mapping[selector_type_upper]
            value = selector_value

        element = driver.find_element(by, value)
        actual_text = element.text
        
        if match_type.upper() == "EXACT":
            matches = actual_text == expected_text
        elif match_type.upper() == "CONTAINS":
            matches = expected_text in actual_text
        else:
            return False, f"Invalid match_type: {match_type}"
        
        if matches:
            return True, f"Element text matches: '{actual_text}'"
        else:
            message = f"Element text mismatch. Expected: '{expected_text}', Actual: '{actual_text}'"
            return not fail_test_if_not, message
    except NoSuchElementException:
        message = f"Element ({selector_type}='{selector_value}') not found"
        return not fail_test_if_not, message
    except Exception as e:
        message = f"Error checking element text: {e}"
        return not fail_test_if_not, message

def verify_element_attribute(driver, selector_type: str, selector_value: str, attribute_name: str, expected_value: str, fail_test_if_not: bool = True):
    """Check if an element's attribute matches expected value"""
    try:
        by_mapping = get_by_mapping(selector_value)
        selector_type_upper = selector_type.upper()

        if selector_type_upper not in by_mapping and selector_type_upper != "TEXT":
            return False, f"Invalid selector_type '{selector_type}'"

        if selector_type_upper == "TEXT":
            by = by_mapping["TEXT"][0]
            value = by_mapping["TEXT"][1]
        else:
            by = by_mapping[selector_type_upper]
            value = selector_value

        element = driver.find_element(by, value)
        actual_value = element.get_attribute(attribute_name)
        
        if actual_value == expected_value:
            return True, f"Element {attribute_name} matches: '{actual_value}'"
        else:
            message = f"Element {attribute_name} mismatch. Expected: '{expected_value}', Actual: '{actual_value}'"
            return not fail_test_if_not, message
    except NoSuchElementException:
        message = f"Element ({selector_type}='{selector_value}') not found"
        return not fail_test_if_not, message
    except Exception as e:
        message = f"Error checking element attribute: {e}"
        return not fail_test_if_not, message

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

def execute_adb_shell(driver, command: str):
    """Execute an arbitrary ADB shell command"""
    try:
        result = driver.execute_script('mobile: shell', {'command': command})
        return True, f"ADB command output: {result}"
    except Exception as e:
        return False, f"Error executing ADB command: {e}"

def get_page_source(driver):
    """Retrieves the XML source of the current screen"""
    try:
        page_source = driver.page_source
        return True, f"Page source retrieved ({len(page_source)} characters)"
    except Exception as e:
        return False, f"Error getting page source: {e}"

def scroll(driver, mode: str, selector_type: str = None, selector_value: str = None, max_attempts: int = 10, timeout: int = 10):
    """Scroll the screen in different modes.
    
    Args:
        mode: One of 'to_element', 'to_end', 'up', 'down'
        selector_type, selector_value: Required for 'to_element' mode
        max_attempts: Maximum number of scroll attempts
        timeout: Timeout for element search
    """
    try:
        screen_size = driver.get_window_size()
        x = screen_size['width'] // 2
        start_y = screen_size['height'] * 0.8
        end_y = screen_size['height'] * 0.2
        
        if mode == 'to_element':
            if not (selector_type and selector_value):
                return False, "Selector type and value required for 'to_element' mode"
            
            for _ in range(max_attempts):
                try:
                    by_mapping = get_by_mapping(selector_value)
                    selector_type_upper = selector_type.upper()

                    if selector_type_upper not in by_mapping and selector_type_upper != "TEXT":
                        return False, f"Invalid selector_type '{selector_type}'"

                    if selector_type_upper == "TEXT":
                        by = by_mapping["TEXT"][0]
                        value = by_mapping["TEXT"][1]
                    else:
                        by = by_mapping[selector_type_upper]
                        value = selector_value

                    element = WebDriverWait(driver, 1).until(
                        EC.presence_of_element_located((by, value))
                    )
                    return True, "Element found after scrolling"
                except TimeoutException:
                    driver.swipe(x, start_y, x, end_y, 800)
                    time.sleep(0.5)
                    continue
                except Exception as e:
                    return False, f"Error during scroll: {e}"
            
            return False, f"Element not found after {max_attempts} attempts"
            
        elif mode == 'to_end':
            last_page_source = None
            for i in range(max_attempts):
                current_page_source = driver.page_source
                if last_page_source == current_page_source:
                    return True, f"Reached end of scrollable view after {i} attempts"
                
                last_page_source = current_page_source
                driver.swipe(x, start_y, x, end_y, 800)
                time.sleep(0.5)
            
            return True, f"Completed {max_attempts} scroll attempts"
            
        elif mode in ['up', 'down']:
            for _ in range(max_attempts):
                if mode == 'up':
                    driver.swipe(x, start_y, x, end_y, 800)
                else:  # down
                    driver.swipe(x, end_y, x, start_y, 800)
                time.sleep(0.5)
            
            return True, f"Completed {max_attempts} {mode} scrolls"
            
        else:
            return False, f"Invalid scroll mode: {mode}"
            
    except Exception as e:
        return False, f"Error during scroll: {e}"

def assert_element_visible(driver, selector_type: str, selector_value: str, timeout: int = 10):
    """Assert that an element is visible on screen"""
    try:
        wait = WebDriverWait(driver, timeout)
        by_mapping = get_by_mapping(selector_value)
        selector_type_upper = selector_type.upper()

        if selector_type_upper not in by_mapping and selector_type_upper != "TEXT":
            return False, f"Invalid selector_type '{selector_type}'"

        if selector_type_upper == "TEXT":
            by = by_mapping["TEXT"][0]
            value = by_mapping["TEXT"][1]
        else:
            by = by_mapping[selector_type_upper]
            value = selector_value

        element = wait.until(EC.visibility_of_element_located((by, value)))
        return True, "Element is visible"
    except TimeoutException:
        return False, f"Element not visible within {timeout}s"
    except Exception as e:
        return False, f"Error checking element visibility: {e}"

def clear_text_field(driver, selector_type: str, selector_value: str, timeout: int = 10):
    """Clear text from an input field"""
    try:
        wait = WebDriverWait(driver, timeout)
        by_mapping = get_by_mapping(selector_value)
        selector_type_upper = selector_type.upper()

        if selector_type_upper not in by_mapping and selector_type_upper != "TEXT":
            return False, f"Invalid selector_type '{selector_type}'"

        if selector_type_upper == "TEXT":
            by = by_mapping["TEXT"][0]
            value = by_mapping["TEXT"][1]
        else:
            by = by_mapping[selector_type_upper]
            value = selector_value

        element = wait.until(EC.presence_of_element_located((by, value)))
        element.clear()
        time.sleep(0.5)
        return True, f"Text field cleared"
    except TimeoutException:
        return False, f"Element not found within {timeout}s"
    except Exception as e:
        return False, f"Error clearing text field: {e}"

def long_press(driver, selector_type: str, selector_value: str, duration: int = 1000, timeout: int = 10):
    """Perform a long press on an element"""
    try:
        wait = WebDriverWait(driver, timeout)
        by_mapping = get_by_mapping(selector_value)
        selector_type_upper = selector_type.upper()

        if selector_type_upper not in by_mapping and selector_type_upper != "TEXT":
            return False, f"Invalid selector_type '{selector_type}'"

        if selector_type_upper == "TEXT":
            by = by_mapping["TEXT"][0]
            value = by_mapping["TEXT"][1]
        else:
            by = by_mapping[selector_type_upper]
            value = selector_value

        element = wait.until(EC.presence_of_element_located((by, value)))
        driver.execute_script('mobile: longClickGesture', {
            'elementId': element.id,
            'duration': duration
        })
        time.sleep(0.5)
        return True, f"Long press performed on element"
    except TimeoutException:
        return False, f"Element not found within {timeout}s"
    except Exception as e:
        return False, f"Error performing long press: {e}"

def double_tap(driver, selector_type: str, selector_value: str, timeout: int = 10):
    """Perform a double tap on an element"""
    try:
        wait = WebDriverWait(driver, timeout)
        by_mapping = get_by_mapping(selector_value)
        selector_type_upper = selector_type.upper()

        if selector_type_upper not in by_mapping and selector_type_upper != "TEXT":
            return False, f"Invalid selector_type '{selector_type}'"

        if selector_type_upper == "TEXT":
            by = by_mapping["TEXT"][0]
            value = by_mapping["TEXT"][1]
        else:
            by = by_mapping[selector_type_upper]
            value = selector_value

        element = wait.until(EC.presence_of_element_located((by, value)))
        driver.execute_script('mobile: doubleClickGesture', {
            'elementId': element.id
        })
        time.sleep(0.5)
        return True, f"Double tap performed on element"
    except TimeoutException:
        return False, f"Element not found within {timeout}s"
    except Exception as e:
        return False, f"Error performing double tap: {e}"

def get_current_activity(driver):
    """Get the current activity name"""
    try:
        current_activity = driver.current_activity
        return True, f"Current activity: {current_activity}"
    except Exception as e:
        return False, f"Error getting current activity: {e}"

def get_device_orientation(driver):
    """Get the current device orientation"""
    try:
        orientation = driver.orientation
        return True, f"Device orientation: {orientation}"
    except Exception as e:
        return False, f"Error getting device orientation: {e}"

def set_device_orientation(driver, orientation: str):
    """Set the device orientation (PORTRAIT or LANDSCAPE)"""
    try:
        orientation = orientation.upper()
        if orientation not in ["PORTRAIT", "LANDSCAPE"]:
            return False, f"Invalid orientation: {orientation}"
        
        driver.orientation = orientation
        time.sleep(1)  # Wait for orientation change to complete
        return True, f"Device orientation set to {orientation}"
    except Exception as e:
        return False, f"Error setting device orientation: {e}"

def get_element_property(driver, selector_type: str, selector_value: str, property_name: str, timeout: int = 10):
    """Get various properties of an element.
    
    Args:
        property_name: One of 'text', 'enabled', or any valid attribute name
    """
    try:
        wait = WebDriverWait(driver, timeout)
        by_mapping = get_by_mapping(selector_value)
        selector_type_upper = selector_type.upper()

        if selector_type_upper not in by_mapping and selector_type_upper != "TEXT":
            return False, f"Invalid selector_type '{selector_type}'"

        if selector_type_upper == "TEXT":
            by = by_mapping["TEXT"][0]
            value = by_mapping["TEXT"][1]
        else:
            by = by_mapping[selector_type_upper]
            value = selector_value

        element = wait.until(EC.presence_of_element_located((by, value)))
        
        if property_name.lower() == 'text':
            value = element.text
        elif property_name.lower() == 'enabled':
            value = element.is_enabled()
        else:
            value = element.get_attribute(property_name)
        
        return True, f"Element {property_name}: {value}"
    except TimeoutException:
        return False, f"Element not found within {timeout}s"
    except Exception as e:
        return False, f"Error getting element property: {e}"

# New App and System Interaction Actions

def is_app_installed(driver, package_name: str):
    """Check if an app is installed on the device"""
    try:
        is_installed = driver.is_app_installed(package_name)
        return True, f"App {package_name} is {'installed' if is_installed else 'not installed'}"
    except Exception as e:
        return False, f"Error checking app installation: {e}"

def install_app(driver, app_path: str):
    """Install an app from the specified path"""
    try:
        driver.install_app(app_path)
        return True, f"App installed from {app_path}"
    except Exception as e:
        return False, f"Error installing app: {e}"

def uninstall_app(driver, package_name: str):
    """Uninstall an app by package name"""
    try:
        driver.remove_app(package_name)
        return True, f"App {package_name} uninstalled"
    except Exception as e:
        return False, f"Error uninstalling app: {e}"

def clear_app_data(driver, package_name: str):
    """Clear app data and cache"""
    try:
        driver.execute_script('mobile: clearApp', {'appId': package_name})
        return True, f"App data cleared for {package_name}"
    except Exception as e:
        return False, f"Error clearing app data: {e}"

def get_app_version(driver, package_name: str):
    """Get the version of an installed app"""
    try:
        version = driver.execute_script('mobile: getAppVersion', {'appId': package_name})
        return True, f"App version: {version}"
    except Exception as e:
        return False, f"Error getting app version: {e}"

def drag_and_drop(driver, source_selector_type: str, source_selector_value: str, 
                 target_selector_type: str, target_selector_value: str, timeout: int = 10):
    """Drag an element to another element"""
    try:
        wait = WebDriverWait(driver, timeout)
        
        # Get source element
        source_by_mapping = get_by_mapping(source_selector_value)
        source_selector_type_upper = source_selector_type.upper()

        if source_selector_type_upper not in source_by_mapping and source_selector_type_upper != "TEXT":
            return False, f"Invalid source selector_type '{source_selector_type}'"

        if source_selector_type_upper == "TEXT":
            source_by = source_by_mapping["TEXT"][0]
            source_value = source_by_mapping["TEXT"][1]
        else:
            source_by = source_by_mapping[source_selector_type_upper]
            source_value = source_selector_value

        source_element = wait.until(EC.presence_of_element_located((source_by, source_value)))
            
        # Get target element
        target_by_mapping = get_by_mapping(target_selector_value)
        target_selector_type_upper = target_selector_type.upper()

        if target_selector_type_upper not in target_by_mapping and target_selector_type_upper != "TEXT":
            return False, f"Invalid target selector_type '{target_selector_type}'"

        if target_selector_type_upper == "TEXT":
            target_by = target_by_mapping["TEXT"][0]
            target_value = target_by_mapping["TEXT"][1]
        else:
            target_by = target_by_mapping[target_selector_type_upper]
            target_value = target_selector_value

        target_element = wait.until(EC.presence_of_element_located((target_by, target_value)))
            
        # Perform drag and drop
        driver.drag_and_drop(source_element, target_element)
        time.sleep(0.5)
        return True, "Drag and drop performed successfully"
    except TimeoutException:
        return False, f"Source or target element not found within {timeout}s"
    except Exception as e:
        return False, f"Error performing drag and drop: {e}"

def pinch_to_zoom(driver, selector_type: str, selector_value: str, scale: float = 0.5, 
                 velocity: float = 0.5, timeout: int = 10):
    """Perform pinch to zoom gesture on an element"""
    try:
        wait = WebDriverWait(driver, timeout)
        by_mapping = get_by_mapping(selector_value)
        selector_type_upper = selector_type.upper()

        if selector_type_upper not in by_mapping and selector_type_upper != "TEXT":
            return False, f"Invalid selector_type '{selector_type}'"

        if selector_type_upper == "TEXT":
            by = by_mapping["TEXT"][0]
            value = by_mapping["TEXT"][1]
        else:
            by = by_mapping[selector_type_upper]
            value = selector_value

        element = wait.until(EC.presence_of_element_located((by, value)))
        driver.execute_script('mobile: pinchCloseGesture', {
            'elementId': element.id,
            'scale': scale,
            'velocity': velocity
        })
        time.sleep(0.5)
        return True, "Pinch to zoom performed"
    except TimeoutException:
        return False, f"Element not found within {timeout}s"
    except Exception as e:
        return False, f"Error performing pinch to zoom: {e}"

def check_toast_message(driver, expected_text: str, timeout: int = 5):
    """Check for a toast message with specific text"""
    try:
        # Toast messages in Android are typically in a specific view
        toast_xpath = f"//android.widget.Toast[contains(@text, '{expected_text}')]"
        wait = WebDriverWait(driver, timeout)
        toast = wait.until(EC.presence_of_element_located((AppiumBy.XPATH, toast_xpath)))
        return True, f"Toast message found: {expected_text}"
    except TimeoutException:
        return False, f"Toast message not found within {timeout}s"
    except Exception as e:
        return False, f"Error checking toast message: {e}"

def check_notification(driver, expected_text: str, timeout: int = 10):
    """Check for a notification with specific text"""
    try:
        # Open notification shade
        driver.open_notifications()
        time.sleep(1)
        
        # Look for notification
        notification_xpath = f"//android.widget.TextView[contains(@text, '{expected_text}')]"
        wait = WebDriverWait(driver, timeout)
        notification = wait.until(EC.presence_of_element_located((AppiumBy.XPATH, notification_xpath)))
        
        # Close notification shade
        press_android_key(driver, "BACK")
        return True, f"Notification found: {expected_text}"
    except TimeoutException:
        press_android_key(driver, "BACK")
        return False, f"Notification not found within {timeout}s"
    except Exception as e:
        press_android_key(driver, "BACK")
        return False, f"Error checking notification: {e}"

def check_app_permission(driver, package_name: str, permission: str):
    """Check if an app has a specific permission"""
    try:
        result = driver.execute_script('mobile: getPermissions', {
            'appId': package_name
        })
        has_permission = permission in result
        return True, f"Permission {permission} is {'granted' if has_permission else 'not granted'}"
    except Exception as e:
        return False, f"Error checking app permission: {e}"

def get_network_state(driver):
    """Get the current network state (WiFi, Mobile Data, Airplane Mode)"""
    try:
        network_info = driver.execute_script('mobile: getNetworkConnection')
        return True, f"Network state: {network_info}"
    except Exception as e:
        return False, f"Error getting network state: {e}"

def get_battery_level(driver):
    """Get the current battery level"""
    try:
        battery_info = driver.execute_script('mobile: batteryInfo')
        level = battery_info.get('level', 'unknown')
        return True, f"Battery level: {level}%"
    except Exception as e:
        return False, f"Error getting battery level: {e}"

def get_storage_state(driver):
    """Get the current storage state (total, used, free space)"""
    try:
        storage_info = driver.execute_script('mobile: getStorageInfo')
        return True, f"Storage info: {storage_info}"
    except Exception as e:
        return False, f"Error getting storage state: {e}"

# App State Management Actions

def is_app_in_foreground(driver, package_name: str):
    """Check if the app is in foreground"""
    try:
        current_package = driver.current_package
        is_foreground = current_package == package_name
        return True, f"App is {'in foreground' if is_foreground else 'in background'}"
    except Exception as e:
        return False, f"Error checking app state: {e}"

def move_app_to_background(driver, seconds: int = 5):
    """Move app to background for specified duration"""
    try:
        driver.background_app(seconds)
        return True, f"App moved to background for {seconds} seconds"
    except Exception as e:
        return False, f"Error moving app to background: {e}"

def reset_app(driver):
    """Reset app state (equivalent to force stop and clear data)"""
    try:
        driver.reset()
        return True, "App reset successfully"
    except Exception as e:
        return False, f"Error resetting app: {e}"

def get_app_state(driver, package_name: str):
    """Get detailed app state (running, stopped, etc.)"""
    try:
        state = driver.query_app_state(package_name)
        state_map = {
            0: "not installed",
            1: "not running",
            2: "running in background",
            3: "running in background suspended",
            4: "running in foreground"
        }
        return True, f"App state: {state_map.get(state, 'unknown')}"
    except Exception as e:
        return False, f"Error getting app state: {e}"

# App Permission Actions

def grant_app_permission(driver, package_name: str, permission: str):
    """Grant a specific permission to an app"""
    try:
        driver.execute_script('mobile: grantPermissions', {
            'appId': package_name,
            'permissions': [permission]
        })
        return True, f"Permission {permission} granted to {package_name}"
    except Exception as e:
        return False, f"Error granting permission: {e}"

def revoke_app_permission(driver, package_name: str, permission: str):
    """Revoke a specific permission from an app"""
    try:
        driver.execute_script('mobile: revokePermissions', {
            'appId': package_name,
            'permissions': [permission]
        })
        return True, f"Permission {permission} revoked from {package_name}"
    except Exception as e:
        return False, f"Error revoking permission: {e}"

def get_all_app_permissions(driver, package_name: str):
    """Get all permissions of an app"""
    try:
        permissions = driver.execute_script('mobile: getPermissions', {
            'appId': package_name
        })
        return True, f"App permissions: {permissions}"
    except Exception as e:
        return False, f"Error getting app permissions: {e}"

# App Data Actions

def get_shared_preferences(driver, package_name: str, preference_name: str = None):
    """Get shared preferences of an app"""
    try:
        if preference_name:
            value = driver.execute_script('mobile: getSharedPreferences', {
                'appId': package_name,
                'preferenceName': preference_name
            })
            return True, f"Preference {preference_name}: {value}"
        else:
            prefs = driver.execute_script('mobile: getSharedPreferences', {
                'appId': package_name
            })
            return True, f"All preferences: {prefs}"
    except Exception as e:
        return False, f"Error getting shared preferences: {e}"

def set_shared_preference(driver, package_name: str, preference_name: str, value: str):
    """Set a shared preference value"""
    try:
        driver.execute_script('mobile: setSharedPreferences', {
            'appId': package_name,
            'preferenceName': preference_name,
            'value': value
        })
        return True, f"Preference {preference_name} set to {value}"
    except Exception as e:
        return False, f"Error setting shared preference: {e}"

def clear_shared_preferences(driver, package_name: str):
    """Clear all shared preferences"""
    try:
        driver.execute_script('mobile: clearSharedPreferences', {
            'appId': package_name
        })
        return True, "Shared preferences cleared"
    except Exception as e:
        return False, f"Error clearing shared preferences: {e}"

def get_app_data_dir(driver, package_name: str):
    """Get the app's data directory path"""
    try:
        data_dir = driver.execute_script('mobile: getAppDataDir', {
            'appId': package_name
        })
        return True, f"App data directory: {data_dir}"
    except Exception as e:
        return False, f"Error getting app data directory: {e}"

# App Resource Actions

def push_file(driver, remote_path: str, file_data: bytes):
    """Push a file to the device"""
    try:
        driver.push_file(remote_path, file_data)
        return True, f"File pushed to {remote_path}"
    except Exception as e:
        return False, f"Error pushing file: {e}"

def pull_file(driver, remote_path: str):
    """Pull a file from the device"""
    try:
        file_data = driver.pull_file(remote_path)
        return True, f"File pulled from {remote_path}"
    except Exception as e:
        return False, f"Error pulling file: {e}"

def list_files(driver, remote_path: str):
    """List files in a directory on the device"""
    try:
        files = driver.execute_script('mobile: listFiles', {
            'path': remote_path
        })
        return True, f"Files in {remote_path}: {files}"
    except Exception as e:
        return False, f"Error listing files: {e}"

def delete_file(driver, remote_path: str):
    """Delete a file from the device"""
    try:
        driver.execute_script('mobile: deleteFile', {
            'path': remote_path
        })
        return True, f"File deleted: {remote_path}"
    except Exception as e:
        return False, f"Error deleting file: {e}"

def get_app_resources(driver, package_name: str, resource_type: str = None):
    """Get app resources information"""
    try:
        if resource_type:
            result = driver.execute_script('mobile: shell', {
                'command': f'pm dump {package_name} | grep -A 10 "{resource_type}"'
            })
        else:
            result = driver.execute_script('mobile: shell', {
                'command': f'pm dump {package_name}'
            })
        return True, f"App resources for {package_name}: {result}"
    except Exception as e:
        return False, f"Error getting app resources: {e}"

# Advanced Gesture and Multi-touch Actions

def multi_tap(driver, selector_type: str, selector_value: str, tap_count: int = 3, interval_ms: int = 100, timeout: int = 10):
    """Perform multiple taps on an element with specified interval"""
    try:
        wait = WebDriverWait(driver, timeout)
        by_mapping = get_by_mapping(selector_value)
        selector_type_upper = selector_type.upper()

        if selector_type_upper not in by_mapping and selector_type_upper != "TEXT":
            return False, f"Invalid selector_type '{selector_type}'"

        if selector_type_upper == "TEXT":
            by = by_mapping["TEXT"][0]
            value = by_mapping["TEXT"][1]
        else:
            by = by_mapping[selector_type_upper]
            value = selector_value

        element = wait.until(EC.presence_of_element_located((by, value)))
        
        for i in range(tap_count):
            element.click()
            if i < tap_count - 1:  # Don't sleep after last tap
                time.sleep(interval_ms / 1000.0)
        
        return True, f"Multi-tapped element ({selector_type}='{selector_value}') {tap_count} times"
    except TimeoutException:
        return False, f"Element not found within {timeout}s"
    except Exception as e:
        return False, f"Error performing multi-tap: {e}"

def flick_gesture(driver, selector_type: str, selector_value: str, direction: str, velocity: int = 1000, timeout: int = 10):
    """Perform a flick gesture on an element"""
    try:
        wait = WebDriverWait(driver, timeout)
        by_mapping = get_by_mapping(selector_value)
        selector_type_upper = selector_type.upper()

        if selector_type_upper not in by_mapping and selector_type_upper != "TEXT":
            return False, f"Invalid selector_type '{selector_type}'"

        if selector_type_upper == "TEXT":
            by = by_mapping["TEXT"][0]
            value = by_mapping["TEXT"][1]
        else:
            by = by_mapping[selector_type_upper]
            value = selector_value

        element = wait.until(EC.presence_of_element_located((by, value)))
        
        driver.execute_script('mobile: flickGesture', {
            'elementId': element.id,
            'direction': direction.upper(),
            'velocity': velocity
        })
        
        return True, f"Flicked element ({selector_type}='{selector_value}') in {direction} direction"
    except TimeoutException:
        return False, f"Element not found within {timeout}s"
    except Exception as e:
        return False, f"Error performing flick gesture: {e}"

def scroll_gesture(driver, selector_type: str, selector_value: str, direction: str, percent: float = 0.75, timeout: int = 10):
    """Perform a scroll gesture on an element"""
    try:
        wait = WebDriverWait(driver, timeout)
        by_mapping = get_by_mapping(selector_value)
        selector_type_upper = selector_type.upper()

        if selector_type_upper not in by_mapping and selector_type_upper != "TEXT":
            return False, f"Invalid selector_type '{selector_type}'"

        if selector_type_upper == "TEXT":
            by = by_mapping["TEXT"][0]
            value = by_mapping["TEXT"][1]
        else:
            by = by_mapping[selector_type_upper]
            value = selector_value

        element = wait.until(EC.presence_of_element_located((by, value)))
        
        driver.execute_script('mobile: scrollGesture', {
            'elementId': element.id,
            'direction': direction.upper(),
            'percent': percent
        })
        
        return True, f"Scrolled element ({selector_type}='{selector_value}') in {direction} direction"
    except TimeoutException:
        return False, f"Element not found within {timeout}s"
    except Exception as e:
        return False, f"Error performing scroll gesture: {e}"

def hover_gesture(driver, selector_type: str, selector_value: str, timeout: int = 10):
    """Perform a hover gesture on an element"""
    try:
        wait = WebDriverWait(driver, timeout)
        by_mapping = get_by_mapping(selector_value)
        selector_type_upper = selector_type.upper()

        if selector_type_upper not in by_mapping and selector_type_upper != "TEXT":
            return False, f"Invalid selector_type '{selector_type}'"

        if selector_type_upper == "TEXT":
            by = by_mapping["TEXT"][0]
            value = by_mapping["TEXT"][1]
        else:
            by = by_mapping[selector_type_upper]
            value = selector_value

        element = wait.until(EC.presence_of_element_located((by, value)))
        
        driver.execute_script('mobile: hoverGesture', {
            'elementId': element.id
        })
        
        return True, f"Hovered over element ({selector_type}='{selector_value}')"
    except TimeoutException:
        return False, f"Element not found within {timeout}s"
    except Exception as e:
        return False, f"Error performing hover gesture: {e}"

def w3c_actions(driver, actions_list: list):
    """Perform W3C Actions (advanced gesture sequences)"""
    try:
        from selenium.webdriver.common.action_chains import ActionChains
        from selenium.webdriver.common.actions import interaction
        from selenium.webdriver.common.actions.action_builder import ActionBuilder
        from selenium.webdriver.common.actions.pointer_input import PointerInput
        
        actions = ActionChains(driver)
        
        for action in actions_list:
            action_type = action.get('type', '')
            if action_type == 'pointer_move':
                actions = actions.move_by_offset(action.get('x', 0), action.get('y', 0))
            elif action_type == 'pointer_down':
                actions = actions.click_and_hold()
            elif action_type == 'pointer_up':
                actions = actions.release()
            elif action_type == 'pause':
                actions = actions.pause(action.get('duration', 0.1))
        
        actions.perform()
        return True, "W3C Actions performed successfully"
    except Exception as e:
        return False, f"Error performing W3C actions: {e}"

def touch_action(driver, action_sequence: list):
    """Perform touch actions using the legacy TouchAction API"""
    try:
        from appium.webdriver.common.touch_action import TouchAction
        
        touch = TouchAction(driver)
        
        for action in action_sequence:
            action_type = action.get('type', '')
            if action_type == 'tap':
                touch = touch.tap(x=action.get('x'), y=action.get('y'), count=action.get('count', 1))
            elif action_type == 'press':
                touch = touch.press(x=action.get('x'), y=action.get('y'))
            elif action_type == 'long_press':
                touch = touch.long_press(x=action.get('x'), y=action.get('y'), duration=action.get('duration', 1000))
            elif action_type == 'move_to':
                touch = touch.move_to(x=action.get('x'), y=action.get('y'))
            elif action_type == 'release':
                touch = touch.release()
            elif action_type == 'wait':
                touch = touch.wait(ms=action.get('ms', 100))
        
        touch.perform()
        return True, "Touch actions performed successfully"
    except Exception as e:
        return False, f"Error performing touch actions: {e}"

def multi_finger_gesture(driver, gesture_type: str, fingers: int = 2, duration_ms: int = 1000):
    """Perform multi-finger gestures"""
    try:
        if gesture_type.upper() == "PINCH":
            driver.execute_script('mobile: pinchGesture', {
                'scale': 0.5,
                'velocity': 2.0
            })
        elif gesture_type.upper() == "SPREAD":
            driver.execute_script('mobile: pinchGesture', {
                'scale': 2.0,
                'velocity': 2.0
            })
        elif gesture_type.upper() == "ROTATE":
            driver.execute_script('mobile: rotateGesture', {
                'rotation': 90,
                'velocity': 2.0
            })
        else:
            return False, f"Unsupported gesture type: {gesture_type}"
        
        return True, f"Multi-finger {gesture_type.lower()} gesture performed"
    except Exception as e:
        return False, f"Error performing multi-finger gesture: {e}"

def gesture_sequence(driver, gestures: list):
    """Perform a sequence of gestures"""
    try:
        results = []
        for gesture in gestures:
            gesture_type = gesture.get('type', '')
            
            if gesture_type == 'tap':
                success, msg = multi_tap(driver, gesture.get('selector_type'), gesture.get('selector_value'), 
                                       gesture.get('tap_count', 1), gesture.get('interval_ms', 100))
            elif gesture_type == 'long_press':
                success, msg = long_click_element(driver, gesture.get('selector_type'), gesture.get('selector_value'),
                                                gesture.get('duration_ms', 1000))
            elif gesture_type == 'swipe':
                success, msg = swipe_on_element(driver, gesture.get('selector_type'), gesture.get('selector_value'),
                                              gesture.get('direction'), gesture.get('percent', 75))
            elif gesture_type == 'flick':
                success, msg = flick_gesture(driver, gesture.get('selector_type'), gesture.get('selector_value'),
                                           gesture.get('direction'), gesture.get('velocity', 1000))
            else:
                success, msg = False, f"Unknown gesture type: {gesture_type}"
            
            results.append(f"{gesture_type}: {msg}")
            if not success:
                return False, f"Gesture sequence failed at {gesture_type}: {msg}"
            
            # Wait between gestures
            time.sleep(gesture.get('delay', 0.5))
        
        return True, f"Gesture sequence completed: {'; '.join(results)}"
    except Exception as e:
        return False, f"Error performing gesture sequence: {e}"

# Advanced Element Interaction and Validation

def find_all_elements(driver, selector_type: str, selector_value: str, timeout: int = 10):
    """Find all elements matching the selector"""
    try:
        wait = WebDriverWait(driver, timeout)
        by_mapping = get_by_mapping(selector_value)
        selector_type_upper = selector_type.upper()

        if selector_type_upper not in by_mapping and selector_type_upper != "TEXT":
            return False, f"Invalid selector_type '{selector_type}'"

        if selector_type_upper == "TEXT":
            by = by_mapping["TEXT"][0]
            value = by_mapping["TEXT"][1]
        else:
            by = by_mapping[selector_type_upper]
            value = selector_value

        elements = driver.find_elements(by, value)
        return True, f"Found {len(elements)} elements matching ({selector_type}='{selector_value}')"
    except Exception as e:
        return False, f"Error finding elements: {e}"

def get_element_count(driver, selector_type: str, selector_value: str, timeout: int = 10):
    """Get the count of elements matching the selector"""
    try:
        success, result = find_all_elements(driver, selector_type, selector_value, timeout)
        if success:
            count = len(driver.find_elements(get_by_mapping(selector_value)[selector_type.upper()], selector_value))
            return True, f"Element count: {count}"
        return False, result
    except Exception as e:
        return False, f"Error getting element count: {e}"

def verify_element_count(driver, selector_type: str, selector_value: str, expected_count: int, timeout: int = 10):
    """Verify that the number of elements matches the expected count"""
    try:
        success, result = get_element_count(driver, selector_type, selector_value, timeout)
        if success:
            actual_count = int(result.split(": ")[1])
            if actual_count == expected_count:
                return True, f"Element count verified: {actual_count} (expected: {expected_count})"
            else:
                return False, f"Element count mismatch: {actual_count} (expected: {expected_count})"
        return False, result
    except Exception as e:
        return False, f"Error verifying element count: {e}"

def get_element_location(driver, selector_type: str, selector_value: str, timeout: int = 10):
    """Get the location (x, y coordinates) of an element"""
    try:
        wait = WebDriverWait(driver, timeout)
        by_mapping = get_by_mapping(selector_value)
        selector_type_upper = selector_type.upper()

        if selector_type_upper not in by_mapping and selector_type_upper != "TEXT":
            return False, f"Invalid selector_type '{selector_type}'"

        if selector_type_upper == "TEXT":
            by = by_mapping["TEXT"][0]
            value = by_mapping["TEXT"][1]
        else:
            by = by_mapping[selector_type_upper]
            value = selector_value

        element = wait.until(EC.presence_of_element_located((by, value)))
        location = element.location
        return True, f"Element location: x={location['x']}, y={location['y']}"
    except TimeoutException:
        return False, f"Element not found within {timeout}s"
    except Exception as e:
        return False, f"Error getting element location: {e}"

def get_element_size(driver, selector_type: str, selector_value: str, timeout: int = 10):
    """Get the size (width, height) of an element"""
    try:
        wait = WebDriverWait(driver, timeout)
        by_mapping = get_by_mapping(selector_value)
        selector_type_upper = selector_type.upper()

        if selector_type_upper not in by_mapping and selector_type_upper != "TEXT":
            return False, f"Invalid selector_type '{selector_type}'"

        if selector_type_upper == "TEXT":
            by = by_mapping["TEXT"][0]
            value = by_mapping["TEXT"][1]
        else:
            by = by_mapping[selector_type_upper]
            value = selector_value

        element = wait.until(EC.presence_of_element_located((by, value)))
        size = element.size
        return True, f"Element size: width={size['width']}, height={size['height']}"
    except TimeoutException:
        return False, f"Element not found within {timeout}s"
    except Exception as e:
        return False, f"Error getting element size: {e}"

def is_element_enabled(driver, selector_type: str, selector_value: str, timeout: int = 10):
    """Check if an element is enabled"""
    try:
        wait = WebDriverWait(driver, timeout)
        by_mapping = get_by_mapping(selector_value)
        selector_type_upper = selector_type.upper()

        if selector_type_upper not in by_mapping and selector_type_upper != "TEXT":
            return False, f"Invalid selector_type '{selector_type}'"

        if selector_type_upper == "TEXT":
            by = by_mapping["TEXT"][0]
            value = by_mapping["TEXT"][1]
        else:
            by = by_mapping[selector_type_upper]
            value = selector_value

        element = wait.until(EC.presence_of_element_located((by, value)))
        enabled = element.is_enabled()
        return True, f"Element enabled: {enabled}"
    except TimeoutException:
        return False, f"Element not found within {timeout}s"
    except Exception as e:
        return False, f"Error checking element enabled state: {e}"

def is_element_selected(driver, selector_type: str, selector_value: str, timeout: int = 10):
    """Check if an element is selected (checkbox, radio button, etc.)"""
    try:
        wait = WebDriverWait(driver, timeout)
        by_mapping = get_by_mapping(selector_value)
        selector_type_upper = selector_type.upper()

        if selector_type_upper not in by_mapping and selector_type_upper != "TEXT":
            return False, f"Invalid selector_type '{selector_type}'"

        if selector_type_upper == "TEXT":
            by = by_mapping["TEXT"][0]
            value = by_mapping["TEXT"][1]
        else:
            by = by_mapping[selector_type_upper]
            value = selector_value

        element = wait.until(EC.presence_of_element_located((by, value)))
        selected = element.is_selected()
        return True, f"Element selected: {selected}"
    except TimeoutException:
        return False, f"Element not found within {timeout}s"
    except Exception as e:
        return False, f"Error checking element selected state: {e}"

def is_element_displayed(driver, selector_type: str, selector_value: str, timeout: int = 10):
    """Check if an element is displayed (visible)"""
    try:
        wait = WebDriverWait(driver, timeout)
        by_mapping = get_by_mapping(selector_value)
        selector_type_upper = selector_type.upper()

        if selector_type_upper not in by_mapping and selector_type_upper != "TEXT":
            return False, f"Invalid selector_type '{selector_type}'"

        if selector_type_upper == "TEXT":
            by = by_mapping["TEXT"][0]
            value = by_mapping["TEXT"][1]
        else:
            by = by_mapping[selector_type_upper]
            value = selector_value

        element = wait.until(EC.presence_of_element_located((by, value)))
        displayed = element.is_displayed()
        return True, f"Element displayed: {displayed}"
    except TimeoutException:
        return False, f"Element not found within {timeout}s"
    except Exception as e:
        return False, f"Error checking element displayed state: {e}"

def get_element_css_value(driver, selector_type: str, selector_value: str, css_property: str, timeout: int = 10):
    """Get the CSS value of an element property"""
    try:
        wait = WebDriverWait(driver, timeout)
        by_mapping = get_by_mapping(selector_value)
        selector_type_upper = selector_type.upper()

        if selector_type_upper not in by_mapping and selector_type_upper != "TEXT":
            return False, f"Invalid selector_type '{selector_type}'"

        if selector_type_upper == "TEXT":
            by = by_mapping["TEXT"][0]
            value = by_mapping["TEXT"][1]
        else:
            by = by_mapping[selector_type_upper]
            value = selector_value

        element = wait.until(EC.presence_of_element_located((by, value)))
        css_value = element.value_of_css_property(css_property)
        return True, f"CSS {css_property}: {css_value}"
    except TimeoutException:
        return False, f"Element not found within {timeout}s"
    except Exception as e:
        return False, f"Error getting CSS value: {e}"

def get_element_tag_name(driver, selector_type: str, selector_value: str, timeout: int = 10):
    """Get the tag name of an element"""
    try:
        wait = WebDriverWait(driver, timeout)
        by_mapping = get_by_mapping(selector_value)
        selector_type_upper = selector_type.upper()

        if selector_type_upper not in by_mapping and selector_type_upper != "TEXT":
            return False, f"Invalid selector_type '{selector_type}'"

        if selector_type_upper == "TEXT":
            by = by_mapping["TEXT"][0]
            value = by_mapping["TEXT"][1]
        else:
            by = by_mapping[selector_type_upper]
            value = selector_value

        element = wait.until(EC.presence_of_element_located((by, value)))
        tag_name = element.tag_name
        return True, f"Element tag name: {tag_name}"
    except TimeoutException:
        return False, f"Element not found within {timeout}s"
    except Exception as e:
        return False, f"Error getting element tag name: {e}"

def get_element_rect(driver, selector_type: str, selector_value: str, timeout: int = 10):
    """Get the rectangle (location and size) of an element"""
    try:
        wait = WebDriverWait(driver, timeout)
        by_mapping = get_by_mapping(selector_value)
        selector_type_upper = selector_type.upper()

        if selector_type_upper not in by_mapping and selector_type_upper != "TEXT":
            return False, f"Invalid selector_type '{selector_type}'"

        if selector_type_upper == "TEXT":
            by = by_mapping["TEXT"][0]
            value = by_mapping["TEXT"][1]
        else:
            by = by_mapping[selector_type_upper]
            value = selector_value

        element = wait.until(EC.presence_of_element_located((by, value)))
        rect = element.rect
        return True, f"Element rect: x={rect['x']}, y={rect['y']}, width={rect['width']}, height={rect['height']}"
    except TimeoutException:
        return False, f"Element not found within {timeout}s"
    except Exception as e:
        return False, f"Error getting element rect: {e}"

def submit_form(driver, selector_type: str, selector_value: str, timeout: int = 10):
    """Submit a form element"""
    try:
        wait = WebDriverWait(driver, timeout)
        by_mapping = get_by_mapping(selector_value)
        selector_type_upper = selector_type.upper()

        if selector_type_upper not in by_mapping and selector_type_upper != "TEXT":
            return False, f"Invalid selector_type '{selector_type}'"

        if selector_type_upper == "TEXT":
            by = by_mapping["TEXT"][0]
            value = by_mapping["TEXT"][1]
        else:
            by = by_mapping[selector_type_upper]
            value = selector_value

        element = wait.until(EC.presence_of_element_located((by, value)))
        element.submit()
        time.sleep(0.5)
        return True, f"Form submitted successfully"
    except TimeoutException:
        return False, f"Form element not found within {timeout}s"
    except Exception as e:
        return False, f"Error submitting form: {e}"

def clear_element(driver, selector_type: str, selector_value: str, timeout: int = 10):
    """Clear the content of an element"""
    try:
        wait = WebDriverWait(driver, timeout)
        by_mapping = get_by_mapping(selector_value)
        selector_type_upper = selector_type.upper()

        if selector_type_upper not in by_mapping and selector_type_upper != "TEXT":
            return False, f"Invalid selector_type '{selector_type}'"

        if selector_type_upper == "TEXT":
            by = by_mapping["TEXT"][0]
            value = by_mapping["TEXT"][1]
        else:
            by = by_mapping[selector_type_upper]
            value = selector_value

        element = wait.until(EC.presence_of_element_located((by, value)))
        element.clear()
        time.sleep(0.5)
        return True, f"Element cleared successfully"
    except TimeoutException:
        return False, f"Element not found within {timeout}s"
    except Exception as e:
        return False, f"Error clearing element: {e}"

def send_keys_to_element(driver, selector_type: str, selector_value: str, keys: str, timeout: int = 10):
    """Send keys to an element (alternative to input_text)"""
    try:
        wait = WebDriverWait(driver, timeout)
        by_mapping = get_by_mapping(selector_value)
        selector_type_upper = selector_type.upper()

        if selector_type_upper not in by_mapping and selector_type_upper != "TEXT":
            return False, f"Invalid selector_type '{selector_type}'"

        if selector_type_upper == "TEXT":
            by = by_mapping["TEXT"][0]
            value = by_mapping["TEXT"][1]
        else:
            by = by_mapping[selector_type_upper]
            value = selector_value

        element = wait.until(EC.presence_of_element_located((by, value)))
        element.send_keys(keys)
        time.sleep(0.5)
        return True, f"Keys sent to element: {keys}"
    except TimeoutException:
        return False, f"Element not found within {timeout}s"
    except Exception as e:
        return False, f"Error sending keys to element: {e}"

# Advanced System and Device Interaction

def toggle_airplane_mode(driver):
    """Toggle airplane mode on/off"""
    try:
        driver.execute_script('mobile: shell', {
            'command': 'settings put global airplane_mode_on 1'
        })
        driver.execute_script('mobile: shell', {
            'command': 'am broadcast -a android.intent.action.AIRPLANE_MODE'
        })
        time.sleep(2)
        return True, "Airplane mode toggled"
    except Exception as e:
        return False, f"Error toggling airplane mode: {e}"

def toggle_wifi(driver, enable: bool = True):
    """Toggle WiFi on/off"""
    try:
        state = "1" if enable else "0"
        driver.execute_script('mobile: shell', {
            'command': f'settings put global wifi_on {state}'
        })
        time.sleep(2)
        return True, f"WiFi {'enabled' if enable else 'disabled'}"
    except Exception as e:
        return False, f"Error toggling WiFi: {e}"

def toggle_bluetooth(driver, enable: bool = True):
    """Toggle Bluetooth on/off"""
    try:
        state = "1" if enable else "0"
        driver.execute_script('mobile: shell', {
            'command': f'settings put global bluetooth_on {state}'
        })
        time.sleep(2)
        return True, f"Bluetooth {'enabled' if enable else 'disabled'}"
    except Exception as e:
        return False, f"Error toggling Bluetooth: {e}"

def set_screen_brightness(driver, brightness: int):
    """Set screen brightness (0-255)"""
    try:
        if not 0 <= brightness <= 255:
            return False, "Brightness must be between 0 and 255"
        
        driver.execute_script('mobile: shell', {
            'command': f'settings put system screen_brightness {brightness}'
        })
        time.sleep(1)
        return True, f"Screen brightness set to {brightness}"
    except Exception as e:
        return False, f"Error setting screen brightness: {e}"

def set_volume(driver, stream_type: str, volume: int):
    """Set volume for a specific stream type"""
    try:
        stream_map = {
            "MUSIC": "3",
            "RING": "2", 
            "NOTIFICATION": "5",
            "ALARM": "4",
            "SYSTEM": "1"
        }
        
        if stream_type.upper() not in stream_map:
            return False, f"Invalid stream type. Use: {', '.join(stream_map.keys())}"
        
        if not 0 <= volume <= 100:
            return False, "Volume must be between 0 and 100"
        
        stream_id = stream_map[stream_type.upper()]
        driver.execute_script('mobile: shell', {
            'command': f'media volume --show --stream {stream_id} --set {volume}'
        })
        time.sleep(1)
        return True, f"{stream_type} volume set to {volume}"
    except Exception as e:
        return False, f"Error setting volume: {e}"

def set_system_language(driver, language_code: str):
    """Set system language"""
    try:
        driver.execute_script('mobile: shell', {
            'command': f'setprop persist.sys.language {language_code}'
        })
        time.sleep(2)
        return True, f"System language set to {language_code}"
    except Exception as e:
        return False, f"Error setting system language: {e}"

def set_system_time(driver, time_string: str):
    """Set system time (format: YYYYMMDD.HHMMSS)"""
    try:
        driver.execute_script('mobile: shell', {
            'command': f'date -s {time_string}'
        })
        time.sleep(1)
        return True, f"System time set to {time_string}"
    except Exception as e:
        return False, f"Error setting system time: {e}"

def enable_developer_options(driver):
    """Enable developer options"""
    try:
        driver.execute_script('mobile: shell', {
            'command': 'settings put global development_settings_enabled 1'
        })
        time.sleep(1)
        return True, "Developer options enabled"
    except Exception as e:
        return False, f"Error enabling developer options: {e}"

def enable_usb_debugging(driver):
    """Enable USB debugging"""
    try:
        driver.execute_script('mobile: shell', {
            'command': 'settings put global adb_enabled 1'
        })
        time.sleep(1)
        return True, "USB debugging enabled"
    except Exception as e:
        return False, f"Error enabling USB debugging: {e}"

def clear_app_cache(driver, package_name: str):
    """Clear app cache"""
    try:
        driver.execute_script('mobile: shell', {
            'command': f'pm clear {package_name}'
        })
        time.sleep(2)
        return True, f"Cache cleared for {package_name}"
    except Exception as e:
        return False, f"Error clearing app cache: {e}"

def force_stop_app(driver, package_name: str):
    """Force stop an app"""
    try:
        driver.execute_script('mobile: shell', {
            'command': f'am force-stop {package_name}'
        })
        time.sleep(1)
        return True, f"App {package_name} force stopped"
    except Exception as e:
        return False, f"Error force stopping app: {e}"

def kill_all_background_apps(driver):
    """Kill all background apps"""
    try:
        driver.execute_script('mobile: shell', {
            'command': 'am kill-all'
        })
        time.sleep(2)
        return True, "All background apps killed"
    except Exception as e:
        return False, f"Error killing background apps: {e}"

def get_running_services(driver):
    """Get list of running services"""
    try:
        result = driver.execute_script('mobile: shell', {
            'command': 'dumpsys activity services | grep -E "ServiceRecord|package="'
        })
        return True, f"Running services: {result}"
    except Exception as e:
        return False, f"Error getting running services: {e}"

def get_running_processes(driver):
    """Get list of running processes"""
    try:
        result = driver.execute_script('mobile: shell', {
            'command': 'ps | grep -E "u0_a[0-9]+"'
        })
        return True, f"Running processes: {result}"
    except Exception as e:
        return False, f"Error getting running processes: {e}"

def get_system_properties(driver, property_name: str = None):
    """Get system properties"""
    try:
        if property_name:
            result = driver.execute_script('mobile: shell', {
                'command': f'getprop {property_name}'
            })
        else:
            result = driver.execute_script('mobile: shell', {
                'command': 'getprop'
            })
        return True, f"System properties: {result}"
    except Exception as e:
        return False, f"Error getting system properties: {e}"

def set_system_property(driver, property_name: str, value: str):
    """Set a system property"""
    try:
        driver.execute_script('mobile: shell', {
            'command': f'setprop {property_name} {value}'
        })
        time.sleep(1)
        return True, f"System property {property_name} set to {value}"
    except Exception as e:
        return False, f"Error setting system property: {e}"

def get_device_info(driver):
    """Get comprehensive device information"""
    try:
        info = {}
        
        # Get device model
        model = driver.execute_script('mobile: shell', {
            'command': 'getprop ro.product.model'
        })
        info['model'] = model.strip()
        
        # Get Android version
        version = driver.execute_script('mobile: shell', {
            'command': 'getprop ro.build.version.release'
        })
        info['android_version'] = version.strip()
        
        # Get build number
        build = driver.execute_script('mobile: shell', {
            'command': 'getprop ro.build.version.incremental'
        })
        info['build_number'] = build.strip()
        
        # Get device ID
        device_id = driver.execute_script('mobile: shell', {
            'command': 'settings get secure android_id'
        })
        info['device_id'] = device_id.strip()
        
        return True, f"Device info: {info}"
    except Exception as e:
        return False, f"Error getting device info: {e}"

def get_screen_resolution(driver):
    """Get screen resolution"""
    try:
        width = driver.execute_script('mobile: shell', {
            'command': 'wm size'
        })
        return True, f"Screen resolution: {width.strip()}"
    except Exception as e:
        return False, f"Error getting screen resolution: {e}"

def set_screen_resolution(driver, width: int, height: int):
    """Set screen resolution"""
    try:
        driver.execute_script('mobile: shell', {
            'command': f'wm size {width}x{height}'
        })
        time.sleep(2)
        return True, f"Screen resolution set to {width}x{height}"
    except Exception as e:
        return False, f"Error setting screen resolution: {e}"

def get_screen_density(driver):
    """Get screen density"""
    try:
        density = driver.execute_script('mobile: shell', {
            'command': 'wm density'
        })
        return True, f"Screen density: {density.strip()}"
    except Exception as e:
        return False, f"Error getting screen density: {e}"

def set_screen_density(driver, density: int):
    """Set screen density"""
    try:
        driver.execute_script('mobile: shell', {
            'command': f'wm density {density}'
        })
        time.sleep(2)
        return True, f"Screen density set to {density}"
    except Exception as e:
        return False, f"Error setting screen density: {e}"

def take_screenshot_with_timestamp(driver, filename_prefix: str = "screenshot"):
    """Take a screenshot with timestamp in filename"""
    try:
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename_prefix}_{timestamp}.png"
        
        if not os.path.exists("reports"):
            os.makedirs("reports")
        
        filepath = os.path.join("reports", filename)
        driver.save_screenshot(filepath)
        return True, f"Screenshot saved: {filepath}"
    except Exception as e:
        return False, f"Error taking screenshot: {e}"

def record_screen(driver, duration_seconds: int = 10, filename: str = "screen_recording.mp4"):
    """Record screen for specified duration"""
    try:
        if not os.path.exists("reports"):
            os.makedirs("reports")
        
        filepath = os.path.join("reports", filename)
        
        # Start recording
        driver.execute_script('mobile: startRecordingScreen', {
            'videoType': 'libx264',
            'videoQuality': 'medium',
            'videoFps': 10
        })
        
        # Wait for specified duration
        time.sleep(duration_seconds)
        
        # Stop recording
        result = driver.execute_script('mobile: stopRecordingScreen')
        
        # Save the recording
        with open(filepath, 'wb') as f:
            f.write(result)
        
        return True, f"Screen recording saved: {filepath}"
    except Exception as e:
        return False, f"Error recording screen: {e}"

def get_logcat(driver, log_level: str = "V", max_lines: int = 100):
    """Get logcat output"""
    try:
        result = driver.execute_script('mobile: shell', {
            'command': f'logcat -d -v {log_level} | tail -n {max_lines}'
        })
        return True, f"Logcat output: {result}"
    except Exception as e:
        return False, f"Error getting logcat: {e}"

def clear_logcat(driver):
    """Clear logcat buffer"""
    try:
        driver.execute_script('mobile: shell', {
            'command': 'logcat -c'
        })
        return True, "Logcat buffer cleared"
    except Exception as e:
        return False, f"Error clearing logcat: {e}"

def get_cpu_usage(driver):
    """Get CPU usage information"""
    try:
        result = driver.execute_script('mobile: shell', {
            'command': 'top -n 1 | head -20'
        })
        return True, f"CPU usage: {result}"
    except Exception as e:
        return False, f"Error getting CPU usage: {e}"

def get_memory_usage(driver):
    """Get memory usage information"""
    try:
        result = driver.execute_script('mobile: shell', {
            'command': 'dumpsys meminfo | head -30'
        })
        return True, f"Memory usage: {result}"
    except Exception as e:
        return False, f"Error getting memory usage: {e}"

def get_battery_info(driver):
    """Get detailed battery information"""
    try:
        result = driver.execute_script('mobile: shell', {
            'command': 'dumpsys battery'
        })
        return True, f"Battery info: {result}"
    except Exception as e:
        return False, f"Error getting battery info: {e}"

def get_network_info(driver):
    """Get network information"""
    try:
        result = driver.execute_script('mobile: shell', {
            'command': 'dumpsys connectivity'
        })
        return True, f"Network info: {result}"
    except Exception as e:
        return False, f"Error getting network info: {e}"

def get_wifi_info(driver):
    """Get WiFi information"""
    try:
        result = driver.execute_script('mobile: shell', {
            'command': 'dumpsys wifi'
        })
        return True, f"WiFi info: {result}"
    except Exception as e:
        return False, f"Error getting WiFi info: {e}"

def get_bluetooth_info(driver):
    """Get Bluetooth information"""
    try:
        result = driver.execute_script('mobile: shell', {
            'command': 'dumpsys bluetooth'
        })
        return True, f"Bluetooth info: {result}"
    except Exception as e:
        return False, f"Error getting Bluetooth info: {e}"

# Advanced UI Testing and Validation Actions

def wait_for_text_change(driver, selector_type: str, selector_value: str, original_text: str, timeout: int = 30):
    """Wait for element text to change from original value"""
    try:
        wait = WebDriverWait(driver, timeout)
        by_mapping = get_by_mapping(selector_value)
        selector_type_upper = selector_type.upper()

        if selector_type_upper not in by_mapping and selector_type_upper != "TEXT":
            return False, f"Invalid selector_type '{selector_type}'"

        if selector_type_upper == "TEXT":
            by = by_mapping["TEXT"][0]
            value = by_mapping["TEXT"][1]
        else:
            by = by_mapping[selector_type_upper]
            value = selector_value

        def text_changed(driver):
            try:
                element = driver.find_element(by, value)
                return element.text != original_text
            except:
                return False

        wait.until(text_changed)
        element = driver.find_element(by, value)
        return True, f"Text changed from '{original_text}' to '{element.text}'"
    except TimeoutException:
        return False, f"Text did not change within {timeout}s"
    except Exception as e:
        return False, f"Error waiting for text change: {e}"

def wait_for_attribute_change(driver, selector_type: str, selector_value: str, attribute_name: str, original_value: str, timeout: int = 30):
    """Wait for element attribute to change from original value"""
    try:
        wait = WebDriverWait(driver, timeout)
        by_mapping = get_by_mapping(selector_value)
        selector_type_upper = selector_type.upper()

        if selector_type_upper not in by_mapping and selector_type_upper != "TEXT":
            return False, f"Invalid selector_type '{selector_type}'"

        if selector_type_upper == "TEXT":
            by = by_mapping["TEXT"][0]
            value = by_mapping["TEXT"][1]
        else:
            by = by_mapping[selector_type_upper]
            value = selector_value

        def attribute_changed(driver):
            try:
                element = driver.find_element(by, value)
                return element.get_attribute(attribute_name) != original_value
            except:
                return False

        wait.until(attribute_changed)
        element = driver.find_element(by, value)
        new_value = element.get_attribute(attribute_name)
        return True, f"Attribute '{attribute_name}' changed from '{original_value}' to '{new_value}'"
    except TimeoutException:
        return False, f"Attribute did not change within {timeout}s"
    except Exception as e:
        return False, f"Error waiting for attribute change: {e}"

def wait_for_element_count_change(driver, selector_type: str, selector_value: str, original_count: int, timeout: int = 30):
    """Wait for the number of elements to change"""
    try:
        wait = WebDriverWait(driver, timeout)
        by_mapping = get_by_mapping(selector_value)
        selector_type_upper = selector_type.upper()

        if selector_type_upper not in by_mapping and selector_type_upper != "TEXT":
            return False, f"Invalid selector_type '{selector_type}'"

        if selector_type_upper == "TEXT":
            by = by_mapping["TEXT"][0]
            value = by_mapping["TEXT"][1]
        else:
            by = by_mapping[selector_type_upper]
            value = selector_value

        def count_changed(driver):
            try:
                elements = driver.find_elements(by, value)
                return len(elements) != original_count
            except:
                return False

        wait.until(count_changed)
        elements = driver.find_elements(by, value)
        new_count = len(elements)
        return True, f"Element count changed from {original_count} to {new_count}"
    except TimeoutException:
        return False, f"Element count did not change within {timeout}s"
    except Exception as e:
        return False, f"Error waiting for element count change: {e}"

def verify_element_contains_text(driver, selector_type: str, selector_value: str, expected_text: str, timeout: int = 10):
    """Verify that element contains the expected text"""
    try:
        wait = WebDriverWait(driver, timeout)
        by_mapping = get_by_mapping(selector_value)
        selector_type_upper = selector_type.upper()

        if selector_type_upper not in by_mapping and selector_type_upper != "TEXT":
            return False, f"Invalid selector_type '{selector_type}'"

        if selector_type_upper == "TEXT":
            by = by_mapping["TEXT"][0]
            value = by_mapping["TEXT"][1]
        else:
            by = by_mapping[selector_type_upper]
            value = selector_value

        element = wait.until(EC.presence_of_element_located((by, value)))
        actual_text = element.text
        
        if expected_text.lower() in actual_text.lower():
            return True, f"Element contains text '{expected_text}' (actual: '{actual_text}')"
        else:
            return False, f"Element does not contain text '{expected_text}' (actual: '{actual_text}')"
    except TimeoutException:
        return False, f"Element not found within {timeout}s"
    except Exception as e:
        return False, f"Error verifying element text: {e}"

def verify_element_matches_regex(driver, selector_type: str, selector_value: str, regex_pattern: str, timeout: int = 10):
    """Verify that element text matches a regex pattern"""
    try:
        import re
        wait = WebDriverWait(driver, timeout)
        by_mapping = get_by_mapping(selector_value)
        selector_type_upper = selector_type.upper()

        if selector_type_upper not in by_mapping and selector_type_upper != "TEXT":
            return False, f"Invalid selector_type '{selector_type}'"

        if selector_type_upper == "TEXT":
            by = by_mapping["TEXT"][0]
            value = by_mapping["TEXT"][1]
        else:
            by = by_mapping[selector_type_upper]
            value = selector_value

        element = wait.until(EC.presence_of_element_located((by, value)))
        actual_text = element.text
        
        if re.search(regex_pattern, actual_text):
            return True, f"Element text matches regex '{regex_pattern}' (actual: '{actual_text}')"
        else:
            return False, f"Element text does not match regex '{regex_pattern}' (actual: '{actual_text}')"
    except TimeoutException:
        return False, f"Element not found within {timeout}s"
    except Exception as e:
        return False, f"Error verifying element regex: {e}"

def verify_element_has_class(driver, selector_type: str, selector_value: str, expected_class: str, timeout: int = 10):
    """Verify that element has the expected CSS class"""
    try:
        wait = WebDriverWait(driver, timeout)
        by_mapping = get_by_mapping(selector_value)
        selector_type_upper = selector_type.upper()

        if selector_type_upper not in by_mapping and selector_type_upper != "TEXT":
            return False, f"Invalid selector_type '{selector_type}'"

        if selector_type_upper == "TEXT":
            by = by_mapping["TEXT"][0]
            value = by_mapping["TEXT"][1]
        else:
            by = by_mapping[selector_type_upper]
            value = selector_value

        element = wait.until(EC.presence_of_element_located((by, value)))
        class_attribute = element.get_attribute("class")
        
        if expected_class in class_attribute:
            return True, f"Element has class '{expected_class}' (classes: '{class_attribute}')"
        else:
            return False, f"Element does not have class '{expected_class}' (classes: '{class_attribute}')"
    except TimeoutException:
        return False, f"Element not found within {timeout}s"
    except Exception as e:
        return False, f"Error verifying element class: {e}"

def verify_element_is_focused(driver, selector_type: str, selector_value: str, timeout: int = 10):
    """Verify that element is focused"""
    try:
        wait = WebDriverWait(driver, timeout)
        by_mapping = get_by_mapping(selector_value)
        selector_type_upper = selector_type.upper()

        if selector_type_upper not in by_mapping and selector_type_upper != "TEXT":
            return False, f"Invalid selector_type '{selector_type}'"

        if selector_type_upper == "TEXT":
            by = by_mapping["TEXT"][0]
            value = by_mapping["TEXT"][1]
        else:
            by = by_mapping[selector_type_upper]
            value = selector_value

        element = wait.until(EC.presence_of_element_located((by, value)))
        focused_element = driver.switch_to.active_element
        
        if element.id == focused_element.id:
            return True, "Element is focused"
        else:
            return False, "Element is not focused"
    except TimeoutException:
        return False, f"Element not found within {timeout}s"
    except Exception as e:
        return False, f"Error verifying element focus: {e}"

def get_element_screenshot(driver, selector_type: str, selector_value: str, filename: str = "element_screenshot.png", timeout: int = 10):
    """Take a screenshot of a specific element"""
    try:
        wait = WebDriverWait(driver, timeout)
        by_mapping = get_by_mapping(selector_value)
        selector_type_upper = selector_type.upper()

        if selector_type_upper not in by_mapping and selector_type_upper != "TEXT":
            return False, f"Invalid selector_type '{selector_type}'"

        if selector_type_upper == "TEXT":
            by = by_mapping["TEXT"][0]
            value = by_mapping["TEXT"][1]
        else:
            by = by_mapping[selector_type_upper]
            value = selector_value

        element = wait.until(EC.presence_of_element_located((by, value)))
        
        if not os.path.exists("reports"):
            os.makedirs("reports")
        
        filepath = os.path.join("reports", filename)
        element.screenshot(filepath)
        return True, f"Element screenshot saved: {filepath}"
    except TimeoutException:
        return False, f"Element not found within {timeout}s"
    except Exception as e:
        return False, f"Error taking element screenshot: {e}"

def scroll_element_into_view(driver, selector_type: str, selector_value: str, timeout: int = 10):
    """Scroll element into view"""
    try:
        wait = WebDriverWait(driver, timeout)
        by_mapping = get_by_mapping(selector_value)
        selector_type_upper = selector_type.upper()

        if selector_type_upper not in by_mapping and selector_type_upper != "TEXT":
            return False, f"Invalid selector_type '{selector_type}'"

        if selector_type_upper == "TEXT":
            by = by_mapping["TEXT"][0]
            value = by_mapping["TEXT"][1]
        else:
            by = by_mapping[selector_type_upper]
            value = selector_value

        element = wait.until(EC.presence_of_element_located((by, value)))
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(1)
        return True, "Element scrolled into view"
    except TimeoutException:
        return False, f"Element not found within {timeout}s"
    except Exception as e:
        return False, f"Error scrolling element into view: {e}"

def highlight_element(driver, selector_type: str, selector_value: str, color: str = "red", duration_ms: int = 2000, timeout: int = 10):
    """Highlight an element with a colored border"""
    try:
        wait = WebDriverWait(driver, timeout)
        by_mapping = get_by_mapping(selector_value)
        selector_type_upper = selector_type.upper()

        if selector_type_upper not in by_mapping and selector_type_upper != "TEXT":
            return False, f"Invalid selector_type '{selector_type}'"

        if selector_type_upper == "TEXT":
            by = by_mapping["TEXT"][0]
            value = by_mapping["TEXT"][1]
        else:
            by = by_mapping[selector_type_upper]
            value = selector_value

        element = wait.until(EC.presence_of_element_located((by, value)))
        
        # Store original style
        original_style = element.get_attribute("style")
        
        # Apply highlight
        driver.execute_script(
            f"arguments[0].style.border = '3px solid {color}'; "
            f"arguments[0].style.backgroundColor = 'yellow';", 
            element
        )
        
        # Wait for highlight duration
        time.sleep(duration_ms / 1000.0)
        
        # Restore original style
        driver.execute_script(f"arguments[0].style = '{original_style}';", element)
        
        return True, f"Element highlighted with {color} border for {duration_ms}ms"
    except TimeoutException:
        return False, f"Element not found within {timeout}s"
    except Exception as e:
        return False, f"Error highlighting element: {e}"

def get_element_coordinates(driver, selector_type: str, selector_value: str, timeout: int = 10):
    """Get the center coordinates of an element"""
    try:
        wait = WebDriverWait(driver, timeout)
        by_mapping = get_by_mapping(selector_value)
        selector_type_upper = selector_type.upper()

        if selector_type_upper not in by_mapping and selector_type_upper != "TEXT":
            return False, f"Invalid selector_type '{selector_type}'"

        if selector_type_upper == "TEXT":
            by = by_mapping["TEXT"][0]
            value = by_mapping["TEXT"][1]
        else:
            by = by_mapping[selector_type_upper]
            value = selector_value

        element = wait.until(EC.presence_of_element_located((by, value)))
        location = element.location
        size = element.size
        
        center_x = location['x'] + size['width'] // 2
        center_y = location['y'] + size['height'] // 2
        
        return True, f"Element center coordinates: x={center_x}, y={center_y}"
    except TimeoutException:
        return False, f"Element not found within {timeout}s"
    except Exception as e:
        return False, f"Error getting element coordinates: {e}"

def tap_at_coordinates(driver, x: int, y: int):
    """Tap at specific screen coordinates"""
    try:
        driver.execute_script('mobile: shell', {
            'command': f'input tap {x} {y}'
        })
        time.sleep(0.5)
        return True, f"Tapped at coordinates: x={x}, y={y}"
    except Exception as e:
        return False, f"Error tapping at coordinates: {e}"

def swipe_between_coordinates(driver, start_x: int, start_y: int, end_x: int, end_y: int, duration_ms: int = 500):
    """Swipe between two coordinate points"""
    try:
        driver.execute_script('mobile: shell', {
            'command': f'input swipe {start_x} {start_y} {end_x} {end_y} {duration_ms}'
        })
        time.sleep(0.5)
        return True, f"Swiped from ({start_x},{start_y}) to ({end_x},{end_y})"
    except Exception as e:
        return False, f"Error swiping between coordinates: {e}"

def type_text_at_coordinates(driver, x: int, y: int, text: str):
    """Type text at specific screen coordinates"""
    try:
        # First tap to focus
        driver.execute_script('mobile: shell', {
            'command': f'input tap {x} {y}'
        })
        time.sleep(0.5)
        
        # Then type the text
        driver.execute_script('mobile: shell', {
            'command': f'input text "{text}"'
        })
        time.sleep(0.5)
        
        return True, f"Typed '{text}' at coordinates: x={x}, y={y}"
    except Exception as e:
        return False, f"Error typing text at coordinates: {e}"

def get_current_focused_element(driver):
    """Get information about the currently focused element"""
    try:
        focused_element = driver.switch_to.active_element
        tag_name = focused_element.tag_name
        text = focused_element.text
        element_id = focused_element.id
        
        return True, f"Focused element: tag={tag_name}, text='{text}', id={element_id}"
    except Exception as e:
        return False, f"Error getting focused element: {e}"

def get_all_visible_elements(driver, element_type: str = None):
    """Get all visible elements of a specific type"""
    try:
        if element_type:
            elements = driver.find_elements(AppiumBy.CLASS_NAME, element_type)
        else:
            elements = driver.find_elements(AppiumBy.XPATH, "//*")
        
        visible_elements = []
        for element in elements:
            try:
                if element.is_displayed():
                    visible_elements.append({
                        'tag': element.tag_name,
                        'text': element.text,
                        'id': element.get_attribute('resource-id')
                    })
            except:
                continue
        
        return True, f"Found {len(visible_elements)} visible elements"
    except Exception as e:
        return False, f"Error getting visible elements: {e}"

def get_page_title(driver):
    """Get the current page title"""
    try:
        title = driver.title
        return True, f"Page title: {title}"
    except Exception as e:
        return False, f"Error getting page title: {e}"

def get_current_url(driver):
    """Get the current URL (for web views)"""
    try:
        url = driver.current_url
        return True, f"Current URL: {url}"
    except Exception as e:
        return False, f"Error getting current URL: {e}"

def navigate_back(driver):
    """Navigate back in the app"""
    try:
        driver.back()
        time.sleep(1)
        return True, "Navigated back"
    except Exception as e:
        return False, f"Error navigating back: {e}"

def navigate_forward(driver):
    """Navigate forward in the app"""
    try:
        driver.forward()
        time.sleep(1)
        return True, "Navigated forward"
    except Exception as e:
        return False, f"Error navigating forward: {e}"

def refresh_page(driver):
    """Refresh the current page (for web views)"""
    try:
        driver.refresh()
        time.sleep(2)
        return True, "Page refreshed"
    except Exception as e:
        return False, f"Error refreshing page: {e}"

def get_window_handles(driver):
    """Get all window handles (for web views)"""
    try:
        handles = driver.window_handles
        return True, f"Found {len(handles)} window handles"
    except Exception as e:
        return False, f"Error getting window handles: {e}"

def switch_to_window(driver, window_handle: str):
    """Switch to a specific window (for web views)"""
    try:
        driver.switch_to.window(window_handle)
        time.sleep(1)
        return True, f"Switched to window: {window_handle}"
    except Exception as e:
        return False, f"Error switching to window: {e}"

def close_current_window(driver):
    """Close the current window (for web views)"""
    try:
        driver.close()
        time.sleep(1)
        return True, "Current window closed"
    except Exception as e:
        return False, f"Error closing current window: {e}"

def maximize_window(driver):
    """Maximize the current window (for web views)"""
    try:
        driver.maximize_window()
        time.sleep(1)
        return True, "Window maximized"
    except Exception as e:
        return False, f"Error maximizing window: {e}"

def get_window_size(driver):
    """Get the current window size (for web views)"""
    try:
        size = driver.get_window_size()
        return True, f"Window size: width={size['width']}, height={size['height']}"
    except Exception as e:
        return False, f"Error getting window size: {e}"

def set_window_size(driver, width: int, height: int):
    """Set the window size (for web views)"""
    try:
        driver.set_window_size(width, height)
        time.sleep(1)
        return True, f"Window size set to {width}x{height}"
    except Exception as e:
        return False, f"Error setting window size: {e}"