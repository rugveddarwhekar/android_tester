#!/usr/bin/env python3
"""
Android GUI Tester Setup Script
Helps users configure their environment and diagnose common issues
"""

import os
import sys
import subprocess
import shlex
import json
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    print("Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print(f"Python {version.major}.{version.minor} detected. Python 3.7+ is required.")
        return False
    print(f"Python {version.major}.{version.minor}.{version.micro} - Compatible")
    return True

def check_dependencies():
    """Check if required dependencies are installed"""
    print("\nChecking dependencies...")
    
    required_packages = [
        ('Appium-Python-Client', 'appium'),
        ('requests', 'requests')
    ]
    
    missing_packages = []
    
    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
            print(f"{package_name} - Installed")
        except ImportError:
            print(f"{package_name} - Missing")
            missing_packages.append(package_name)
    
    if missing_packages:
        print(f"\nInstall missing packages with:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_adb():
    """Check if ADB is available"""
    print("\nChecking ADB (Android Debug Bridge)...")
    
    try:
        result = subprocess.run(
            shlex.split("adb version"),
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            version_line = result.stdout.splitlines()[0]
            print(f"ADB - {version_line}")
            return True
        else:
            print("ADB command failed")
            return False
            
    except FileNotFoundError:
        print("ADB not found in PATH")
        print("Install Android SDK platform-tools and add to PATH")
        return False
    except Exception as e:
        print(f"Error checking ADB: {e}")
        return False

def check_connected_devices():
    """Check for connected Android devices"""
    print("\nChecking for connected devices...")
    
    try:
        result = subprocess.run(
            shlex.split("adb devices"),
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            print("Failed to list devices")
            return False
        
        lines = result.stdout.strip().splitlines()
        if len(lines) <= 1:
            print("No devices found")
            print("Connect your Android device via USB and enable USB debugging")
            return False
        
        authorized_devices = [line for line in lines[1:] if line.strip() and 'device' in line and 'unauthorized' not in line]
        
        if not authorized_devices:
            print("No authorized devices found")
            print("Check USB debugging authorization on your device")
            return False
        
        print(f"Found {len(authorized_devices)} authorized device(s):")
        for device in authorized_devices:
            device_id = device.split()[0]
            print(f"  {device_id}")
        
        return True
        
    except Exception as e:
        print(f"Error checking devices: {e}")
        return False

def check_appium_server():
    """Check if Appium server is running"""
    print("\nChecking Appium server...")
    
    try:
        import requests
        response = requests.get("http://localhost:4723/status", timeout=5)
        if response.status_code == 200:
            print("Appium server is running")
            return True
        else:
            print(f"Appium server responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("Cannot connect to Appium server")
        print("Start Appium server: appium")
        return False
    except ImportError:
        print("Requests library not available")
        return False
    except Exception as e:
        print(f"Error checking Appium server: {e}")
        return False

def check_config_files():
    """Check if configuration files exist and are valid"""
    print("\nChecking configuration files...")
    
    config_dir = Path("config")
    capabilities_file = config_dir / "capabilities.json"
    
    if not config_dir.exists():
        print("Config directory not found")
        return False
    
    if not capabilities_file.exists():
        print("capabilities.json not found")
        print("Creating default capabilities file...")
        return create_default_capabilities()
    
    try:
        with open(capabilities_file, 'r') as f:
            caps = json.load(f)
        
        print("capabilities.json - Valid JSON")
        
        if 'appium:deviceName' not in caps:
            print("Missing appium:deviceName in capabilities")
        elif caps['appium:deviceName'] == "YOUR_DEVICE_ID":
            print("Device ID not configured (still set to YOUR_DEVICE_ID)")
        else:
            print(f"Device ID configured: {caps['appium:deviceName']}")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"Invalid JSON in capabilities.json: {e}")
        return False
    except Exception as e:
        print(f"Error reading capabilities.json: {e}")
        return False

def create_default_capabilities():
    """Create a default capabilities.json file"""
    config_dir = Path("config")
    capabilities_file = config_dir / "capabilities.json"
    
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
        config_dir.mkdir(exist_ok=True)
        with open(capabilities_file, 'w') as f:
            json.dump(default_caps, f, indent=4)
        print("Created default capabilities.json")
        print("Edit config/capabilities.json with your device ID")
        return True
    except Exception as e:
        print(f"Failed to create capabilities.json: {e}")
        return False

def get_device_id():
    """Get the first connected device ID"""
    try:
        result = subprocess.run(
            shlex.split("adb devices"),
            capture_output=True,
            text=True,
            timeout=10
        )
        
        lines = result.stdout.strip().splitlines()
        authorized_devices = [line for line in lines[1:] if line.strip() and 'device' in line and 'unauthorized' not in line]
        
        if authorized_devices:
            return authorized_devices[0].split()[0]
        return None
    except:
        return None

def update_capabilities_with_device():
    """Update capabilities.json with the connected device ID"""
    device_id = get_device_id()
    if not device_id:
        print("No authorized device found")
        return False
    
    capabilities_file = Path("config/capabilities.json")
    
    try:
        with open(capabilities_file, 'r') as f:
            caps = json.load(f)
        
        caps['appium:deviceName'] = device_id
        
        with open(capabilities_file, 'w') as f:
            json.dump(caps, f, indent=4)
        
        print(f"Updated capabilities.json with device ID: {device_id}")
        return True
    except Exception as e:
        print(f"Failed to update capabilities.json: {e}")
        return False

def main():
    """Main setup function"""
    print("Android GUI Tester Setup")
    print("=" * 40)
    
    all_checks_passed = True
    
    if not check_python_version():
        all_checks_passed = False
    
    if not check_dependencies():
        all_checks_passed = False
    
    if not check_adb():
        all_checks_passed = False
    
    if not check_connected_devices():
        all_checks_passed = False
    
    if not check_appium_server():
        all_checks_passed = False
    
    if not check_config_files():
        all_checks_passed = False
    
    print("\n" + "=" * 40)
    
    if all_checks_passed:
        print("All checks passed! Your environment is ready.")
        print("\nNext steps:")
        print("1. Run: python3 main.py")
        print("2. Create your first test case")
        print("3. Run the test!")
    else:
        print("Some checks failed. Please fix the issues above.")
        print("\nQuick fixes:")
        print("1. Install missing dependencies: pip install -r requirements.txt")
        print("2. Connect Android device and enable USB debugging")
        print("3. Start Appium server: appium")
        print("4. Run this setup script again: python3 setup.py")
    
    if all_checks_passed:
        device_id = get_device_id()
        if device_id:
            response = input(f"\nUpdate capabilities.json with device ID '{device_id}'? (y/n): ")
            if response.lower() in ['y', 'yes']:
                update_capabilities_with_device()

if __name__ == "__main__":
    main()
