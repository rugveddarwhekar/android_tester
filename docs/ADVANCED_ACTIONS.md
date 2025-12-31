# Advanced Actions Documentation

This document describes the new advanced actions added to the Android Tester project, including Play Store automation, advanced app management, and performance testing capabilities.

## Table of Contents

1. [Play Store Automation](#play-store-automation)
2. [Advanced App Management](#advanced-app-management)
3. [Performance Testing](#performance-testing)
4. [App Backup and Restore](#app-backup-and-restore)
5. [App Analysis and Monitoring](#app-analysis-and-monitoring)
6. [Batch Operations](#batch-operations)
7. [Usage Examples](#usage-examples)

## Play Store Automation

### Open Play Store
Opens the Google Play Store app on the device.

**Action ID:** `open_play_store`

**Parameters:** None

**Example:**
```json
{
  "action": "open_play_store",
  "params": {}
}
```

### Search Play Store
Searches for an app in the Google Play Store.

**Action ID:** `search_play_store`

**Parameters:**
- `app_name` (string, required): The name of the app to search for
- `timeout` (integer, optional): Maximum time to wait for search results (default: 30s)

**Example:**
```json
{
  "action": "search_play_store",
  "params": {
    "app_name": "WhatsApp",
    "timeout": 30
  }
}
```

### Install App from Play Store
Finds and installs an app from the Google Play Store automatically.

**Action ID:** `install_app_from_play_store`

**Parameters:**
- `app_name` (string, required): The name of the app to install
- `timeout` (integer, optional): Maximum time to wait for installation (default: 120s)

**Example:**
```json
{
  "action": "install_app_from_play_store",
  "params": {
    "app_name": "WhatsApp",
    "timeout": 120
  }
}
```

### Uninstall App via Play Store
Uninstalls an app through the Google Play Store interface.

**Action ID:** `uninstall_app_via_play_store`

**Parameters:**
- `app_name` (string, required): The name of the app to uninstall

**Example:**
```json
{
  "action": "uninstall_app_via_play_store",
  "params": {
    "app_name": "WhatsApp"
  }
}
```

## Advanced App Management

### Get Installed Apps
Retrieves a list of all installed third-party apps on the device.

**Action ID:** `get_installed_apps`

**Parameters:** None

**Returns:** List of installed app package names

### Get System Apps
Retrieves a list of all system apps on the device.

**Action ID:** `get_system_apps`

**Parameters:** None

**Returns:** List of system app package names

### Get App Info
Gets detailed information about an installed app including version, size, and permissions.

**Action ID:** `get_app_info`

**Parameters:**
- `package_name` (string, required): The package name of the app

**Returns:** Object containing app information

**Example:**
```json
{
  "action": "get_app_info",
  "params": {
    "package_name": "com.whatsapp"
  }
}
```

### Get App Permissions
Gets all permissions for an app.

**Action ID:** `get_app_permissions`

**Parameters:**
- `package_name` (string, required): The package name of the app

**Returns:** List of app permissions

### Enable/Disable App Permissions
Enables or disables specific permissions for an app.

**Action ID:** `enable_app_permissions` / `disable_app_permissions`

**Parameters:**
- `package_name` (string, required): The package name of the app
- `permissions` (list, required): List of permissions to enable/disable

**Example:**
```json
{
  "action": "enable_app_permissions",
  "params": {
    "package_name": "com.whatsapp",
    "permissions": ["android.permission.CAMERA", "android.permission.MICROPHONE"]
  }
}
```

### Freeze/Unfreeze App
Freezes or unfreezes an app (requires root access).

**Action ID:** `freeze_app` / `unfreeze_app`

**Parameters:**
- `package_name` (string, required): The package name of the app

## Performance Testing

### Get App Launch Time
Measures the time it takes for an app to launch.

**Action ID:** `get_app_launch_time`

**Parameters:**
- `package_name` (string, required): The package name of the app
- `activity_name` (string, optional): Specific activity to launch

**Returns:** Launch time in seconds

### Monitor App Performance
Monitors app performance metrics over time.

**Action ID:** `monitor_app_performance`

**Parameters:**
- `package_name` (string, required): The package name of the app
- `duration_seconds` (integer, optional): How long to monitor (default: 30s)

**Returns:** Performance monitoring data

### Stress Test App
Performs stress testing on an app by repeatedly launching and closing it.

**Action ID:** `stress_test_app`

**Parameters:**
- `package_name` (string, required): The package name of the app
- `cycles` (integer, optional): Number of launch/close cycles (default: 10)

**Returns:** Stress test results and statistics

### Analyze App Performance
Analyzes app performance over time and saves data to a file.

**Action ID:** `analyze_app_performance`

**Parameters:**
- `package_name` (string, required): The package name of the app
- `duration_minutes` (integer, optional): How long to analyze (default: 5 minutes)

**Returns:** Path to performance analysis file

## App Backup and Restore

### Backup App Data
Creates a backup of an app's data and files.

**Action ID:** `backup_app_data`

**Parameters:**
- `package_name` (string, required): The package name of the app
- `backup_path` (string, optional): Path where to save the backup

### Restore App Data
Restores app data from a backup file.

**Action ID:** `restore_app_data`

**Parameters:**
- `package_name` (string, required): The package name of the app
- `backup_path` (string, required): Path to the backup file

### Create App Backup
Creates a comprehensive backup of an app including data and APK.

**Action ID:** `create_app_backup`

**Parameters:**
- `package_name` (string, required): The package name of the app
- `backup_name` (string, optional): Name for the backup

### Restore App from Backup
Restores an app from a backup.

**Action ID:** `restore_app_from_backup`

**Parameters:**
- `backup_name` (string, required): Name of the backup to restore from
- `package_name` (string, optional): Package name (will be extracted from backup)

## App Analysis and Monitoring

### Get App Dependencies
Gets app dependencies and shared libraries.

**Action ID:** `get_app_dependencies`

**Parameters:**
- `package_name` (string, required): The package name of the app

**Returns:** App dependencies information

### Detect App Crashes
Monitors for app crashes over a period of time.

**Action ID:** `detect_app_crashes`

**Parameters:**
- `package_name` (string, required): The package name of the app
- `monitoring_duration_minutes` (integer, optional): How long to monitor (default: 10 minutes)

**Returns:** Crash detection results

### Get App Crash Logs
Retrieves crash logs for a specific app.

**Action ID:** `get_app_crash_logs`

**Parameters:**
- `package_name` (string, required): The package name of the app

**Returns:** Crash logs for the app

### Get App Usage Stats
Gets usage statistics for an app.

**Action ID:** `get_app_usage_stats`

**Parameters:**
- `package_name` (string, required): The package name of the app
- `days` (integer, optional): Number of days to get stats for (default: 7)

**Returns:** App usage statistics

### Optimize App Performance
Applies performance optimizations to an app.

**Action ID:** `optimize_app_performance`

**Parameters:**
- `package_name` (string, required): The package name of the app

**Returns:** List of optimizations applied

### Create App Test Report
Creates a comprehensive test report for an app.

**Action ID:** `create_app_test_report`

**Parameters:**
- `package_name` (string, required): The package name of the app

**Returns:** Path to test report file

## Batch Operations

### Batch Install Apps
Installs multiple apps in batch from APK files.

**Action ID:** `batch_install_apps`

**Parameters:**
- `app_paths` (list, required): List of APK file paths to install

**Returns:** Batch installation results

### Batch Uninstall Apps
Uninstalls multiple apps in batch.

**Action ID:** `batch_uninstall_apps`

**Parameters:**
- `package_names` (list, required): List of package names to uninstall

**Returns:** Batch uninstallation results

### Verify App Installation
Verifies that an app is properly installed and can be launched.

**Action ID:** `verify_app_installation`

**Parameters:**
- `package_name` (string, required): The package name of the app
- `expected_version` (string, optional): Expected version to verify

**Returns:** Boolean indicating if app is properly installed

## Usage Examples

### Example 1: Install App from Play Store
```json
{
  "test_name": "Install WhatsApp from Play Store",
  "test_steps": [
    {
      "step_number": 1,
      "action": "open_play_store",
      "params": {}
    },
    {
      "step_number": 2,
      "action": "search_play_store",
      "params": {
        "app_name": "WhatsApp"
      }
    },
    {
      "step_number": 3,
      "action": "install_app_from_play_store",
      "params": {
        "app_name": "WhatsApp"
      }
    },
    {
      "step_number": 4,
      "action": "verify_app_installation",
      "params": {
        "package_name": "com.whatsapp"
      }
    }
  ]
}
```

### Example 2: Performance Testing
```json
{
  "test_name": "Performance Test Settings App",
  "test_steps": [
    {
      "step_number": 1,
      "action": "get_app_launch_time",
      "params": {
        "package_name": "com.android.settings"
      }
    },
    {
      "step_number": 2,
      "action": "stress_test_app",
      "params": {
        "package_name": "com.android.settings",
        "cycles": 5
      }
    },
    {
      "step_number": 3,
      "action": "analyze_app_performance",
      "params": {
        "package_name": "com.android.settings",
        "duration_minutes": 2
      }
    }
  ]
}
```

### Example 3: App Backup and Restore
```json
{
  "test_name": "Backup and Restore Test",
  "test_steps": [
    {
      "step_number": 1,
      "action": "create_app_backup",
      "params": {
        "package_name": "com.example.myapp",
        "backup_name": "myapp_backup"
      }
    },
    {
      "step_number": 2,
      "action": "uninstall_app",
      "params": {
        "package_name": "com.example.myapp"
      }
    },
    {
      "step_number": 3,
      "action": "restore_app_from_backup",
      "params": {
        "backup_name": "myapp_backup"
      }
    }
  ]
}
```

## Notes and Considerations

1. **Root Access**: Some operations (like freezing apps) require root access on the device.

2. **Play Store Requirements**: Play Store automation requires:
   - Google Play Store to be installed on the device
   - Internet connectivity
   - Google account signed in (for some operations)

3. **Performance Impact**: Performance monitoring and stress testing can be resource-intensive and may affect device performance.

4. **Time Requirements**: Some operations (like app installation, performance analysis) may take several minutes to complete.

5. **Device Compatibility**: Some features may not work on all Android versions or device types.

6. **Error Handling**: The actions include comprehensive error handling and will return detailed error messages if operations fail.

## Troubleshooting

### Common Issues

1. **Play Store not found**: Ensure Google Play Store is installed and accessible on the device.

2. **Installation fails**: Check internet connectivity and ensure the app name is correct.

3. **Permission denied**: Some operations require root access or specific permissions.

4. **Timeout errors**: Increase timeout values for slow operations or slow network connections.

5. **App not found**: Verify the package name is correct and the app is installed.

### Debug Tips

1. Use `take_screenshot` actions to capture the current state during test execution.

2. Check the test runner logs for detailed error messages.

3. Use `get_page_source` to inspect the current screen layout.

4. Add `wait_seconds` actions to allow more time for operations to complete.

5. Use `verify_app_installation` to confirm apps are properly installed before proceeding.
