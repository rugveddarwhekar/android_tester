# Android GUI Tester

A powerful desktop application for creating and running automated tests for Android applications. Built with Python and Tkinter, this tool provides a user-friendly interface for test case creation and execution.

## Features

- **Visual Test Case Builder**: Create test sequences through an intuitive drag-and-drop interface
- **Action Library**: Pre-defined set of common Android testing actions
- **Parameter Editor**: Configure action parameters with a dynamic UI
- **Test Case Management**: Save and load test cases in JSON format
- **Real-time Execution**: Run tests and view results immediately
- **ADB Integration**: Built-in support for Android Debug Bridge commands
- **Package Detection**: Automatically detect installed packages on connected devices

## Prerequisites

- Python 3.x
- Android SDK with platform-tools (ADB)
- Appium-Python-Client (v2.x)
- A connected Android device or emulator with USB debugging enabled

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd android_tester
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Ensure ADB is in your system PATH or update the configuration accordingly

## Usage

1. Launch the application:
```bash
python main.py
```

2. Connect your Android device and ensure USB debugging is enabled

3. Create a new test case:
   - Select actions from the Action Library
   - Configure parameters for each action
   - Arrange the sequence using the move up/down buttons

4. Save your test case:
   - Click "Save Test Case" to store your configuration

5. Run the test:
   - Click "Run This Test Case" to execute the sequence
   - Monitor the status bar for execution progress

## Project Structure

```
android_tester/
├── actions/         # Action definitions and implementations
├── config/          # Configuration files
├── data/           # Test cases and action library
├── gui/            # Tkinter-based user interface
├── reports/        # Test execution reports
├── runner/         # Test execution engine
├── utils/          # Utility functions
├── main.py         # Application entry point
└── requirements.txt # Project dependencies
```

## Technical Architecture

### Core Components

1. **GUI Layer (Tkinter)**
   - Implements Model-View-Controller (MVC) pattern
   - Custom widgets for test case building
   - Dynamic parameter editors with validation
   - Real-time status updates and progress tracking

2. **Test Runner Engine**
   - Asynchronous test execution using threading
   - Robust error handling and recovery mechanisms
   - Support for parallel test execution
   - Comprehensive logging system

3. **Action Framework**
   - Modular action definitions in JSON
   - Extensible action library system
   - Parameter validation and type checking
   - Action chaining and dependency management

4. **ADB Integration Layer**
   - Secure command execution
   - Device state management
   - Package and activity detection
   - Screen capture and analysis

### Workflow

1. **Test Case Creation**
   ```
   User Interface -> Action Selection -> Parameter Configuration -> Sequence Building -> JSON Serialization
   ```

2. **Test Execution**
   ```
   JSON Deserialization -> Action Validation -> ADB Command Generation -> Execution -> Result Processing
   ```

3. **Error Handling Flow**
   ```
   Error Detection -> Error Classification -> Recovery Attempt -> User Notification -> Logging
   ```

## Screenshots

![Android GUI Tester Interface](android_gui_tester_1.png)

## Future Scope

### Planned Features
- **Multi-device Testing**: Support for running tests across multiple devices simultaneously
- **Test Case Templates**: Pre-built templates for common testing scenarios
- **Enhanced Reporting**: Detailed test execution reports with screenshots and logs
- **Cloud Integration**: Store and share test cases in the cloud
- **CI/CD Integration**: Support for continuous integration pipelines

### Upcoming Improvements
- **Action Recorder**: Record user interactions and convert them to test steps
- **Variable Support**: Use variables in test cases for dynamic values
- **Conditional Logic**: Add if/else and loop constructs to test cases
- **Performance Metrics**: Track and report app performance during tests
- **Cross-platform Support**: Extend support for iOS testing

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[Add your license information here]

## Support

For support, please [create an issue]([your-issues-link]) in the repository. 