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
                    if selector_type.upper() == "ID":
                        element = WebDriverWait(driver, 1).until(
                            EC.presence_of_element_located((AppiumBy.ID, selector_value))
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
        if selector_type.upper() == "ID":
            element = wait.until(EC.visibility_of_element_located((AppiumBy.ID, selector_value)))
            return True, "Element is visible"
        return False, f"Selector type {selector_type} not implemented for assert_element_visible"
    except TimeoutException:
        return False, f"Element not visible within {timeout}s"
    except Exception as e:
        return False, f"Error checking element visibility: {e}"

def clear_text_field(driver, selector_type: str, selector_value: str, timeout: int = 10):
    """Clear text from an input field"""
    try:
        wait = WebDriverWait(driver, timeout)
        if selector_type.upper() == "ID":
            element = wait.until(EC.presence_of_element_located((AppiumBy.ID, selector_value)))
            element.clear()
            time.sleep(0.5)
            return True, f"Text field cleared"
        return False, f"Selector type {selector_type} not implemented for clear_text_field"
    except TimeoutException:
        return False, f"Element not found within {timeout}s"
    except Exception as e:
        return False, f"Error clearing text field: {e}"

def long_press(driver, selector_type: str, selector_value: str, duration: int = 1000, timeout: int = 10):
    """Perform a long press on an element"""
    try:
        wait = WebDriverWait(driver, timeout)
        if selector_type.upper() == "ID":
            element = wait.until(EC.presence_of_element_located((AppiumBy.ID, selector_value)))
            driver.execute_script('mobile: longClickGesture', {
                'elementId': element.id,
                'duration': duration
            })
            time.sleep(0.5)
            return True, f"Long press performed on element"
        return False, f"Selector type {selector_type} not implemented for long_press"
    except TimeoutException:
        return False, f"Element not found within {timeout}s"
    except Exception as e:
        return False, f"Error performing long press: {e}"

def double_tap(driver, selector_type: str, selector_value: str, timeout: int = 10):
    """Perform a double tap on an element"""
    try:
        wait = WebDriverWait(driver, timeout)
        if selector_type.upper() == "ID":
            element = wait.until(EC.presence_of_element_located((AppiumBy.ID, selector_value)))
            driver.execute_script('mobile: doubleClickGesture', {
                'elementId': element.id
            })
            time.sleep(0.5)
            return True, f"Double tap performed on element"
        return False, f"Selector type {selector_type} not implemented for double_tap"
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
        if selector_type.upper() == "ID":
            element = wait.until(EC.presence_of_element_located((AppiumBy.ID, selector_value)))
            
            if property_name.lower() == 'text':
                value = element.text
            elif property_name.lower() == 'enabled':
                value = element.is_enabled()
            else:
                value = element.get_attribute(property_name)
            
            return True, f"Element {property_name}: {value}"
        return False, f"Selector type {selector_type} not implemented for get_element_property"
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
        if source_selector_type.upper() == "ID":
            source_element = wait.until(EC.presence_of_element_located((AppiumBy.ID, source_selector_value)))
        else:
            return False, f"Source selector type {source_selector_type} not implemented"
            
        # Get target element
        if target_selector_type.upper() == "ID":
            target_element = wait.until(EC.presence_of_element_located((AppiumBy.ID, target_selector_value)))
        else:
            return False, f"Target selector type {target_selector_type} not implemented"
            
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
        if selector_type.upper() == "ID":
            element = wait.until(EC.presence_of_element_located((AppiumBy.ID, selector_value)))
            driver.execute_script('mobile: pinchCloseGesture', {
                'elementId': element.id,
                'scale': scale,
                'velocity': velocity
            })
            time.sleep(0.5)
            return True, "Pinch to zoom performed"
        return False, f"Selector type {selector_type} not implemented for pinch_to_zoom"
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
    """Get app resources (images, strings, etc.)"""
    try:
        if resource_type:
            resources = driver.execute_script('mobile: getResources', {
                'appId': package_name,
                'type': resource_type
            })
            return True, f"{resource_type} resources: {resources}"
        else:
            resources = driver.execute_script('mobile: getResources', {
                'appId': package_name
            })
            return True, f"All resources: {resources}"
    except Exception as e:
        return False, f"Error getting app resources: {e}"

# Add more common actions: swipe, get_text, assert_element_visible etc.