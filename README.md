# Android GUI Tester

A simple desktop tool I built for running automated tests on Android devices. It helps you create and execute basic test sequences through a straightforward interface.

![Android GUI Tester Screenshot](docs/images/android_gui_tester_1.png)

## Main Features

- Create test sequences by selecting from common Android actions
- Configure basic parameters for each action
- Save and load test cases
- Run tests on connected Android devices
- View test results in real-time

## What You'll Need

- Python 3.x
- Android SDK with ADB
- Appium-Python-Client
- An Android device with USB debugging enabled

## Quick Start

1. Get the code:
```bash
git clone https://github.com/rugveddarwhekar/android_tester.git
cd android_tester
```

2. Install requirements:
```bash
pip install -r requirements.txt
```

3. Run the app:
```bash
python main.py
```

## Basic Usage

1. Connect your Android device
2. Create a test case:
   - Add actions from the list
   - Set their parameters
   - Arrange the sequence
3. Save your test case
4. Run it and see the results

## Project Structure

```
android_tester/
├── actions/     # Test actions
├── config/      # Settings
├── data/        # Test cases
├── gui/         # Interface
├── reports/     # Results
├── runner/      # Test execution
├── utils/       # Helpers
└── main.py      # Start here
```

## Current Features

1. **Basic Interface**
   - Simple action selection
   - Parameter configuration
   - Test sequence management

2. **Test Execution**
   - Run tests in background
   - Basic error handling
   - Simple logging

3. **Device Integration**
   - ADB command support
   - Device connection
   - Package listing

## Known Limitations

- Works with one device at a time
- Basic error handling
- Limited action types
- No cloud features
- No CI/CD integration

## Planned Updates

I'm working on:
- Adding more test actions
- Improving error handling
- Better test reporting
- Basic multi-device support

## Getting Help

Found an issue or have a question? [Open an issue](https://github.com/rugveddarwhekar/android_tester/issues) and I'll take a look. 