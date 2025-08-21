# Android GUI Tester

A modern, user-friendly desktop application for creating and running automated tests on Android devices. Built with Python and Tkinter, featuring a beautiful pastel-colored interface and comprehensive testing capabilities.

![Android GUI Tester Screenshot](docs/images/android_gui_tester_1.png)

## 🏗️ Architecture Overview

```mermaid
graph TB
    subgraph "User Interface Layer"
        GUI[Modern GUI<br/>Pastel Design]
        HELP[Interactive Help<br/>Tooltips & Guides]
    end
    
    subgraph "Application Layer"
        TEST_BUILDER[Test Case Builder]
        ACTION_LIB[Action Library<br/>100+ Actions]
        PARAM_EDITOR[Parameter Editor]
    end
    
    subgraph "Execution Layer"
        TEST_RUNNER[Test Runner]
        DRIVER_MGR[Driver Manager]
        LOGGER[Real-time Logger]
    end
    
    subgraph "Device Layer"
        ADB[ADB Commands]
        APPIUM[Appium Server]
        ANDROID[Android Device]
    end
    
    GUI --> TEST_BUILDER
    GUI --> ACTION_LIB
    GUI --> PARAM_EDITOR
    TEST_BUILDER --> TEST_RUNNER
    TEST_RUNNER --> DRIVER_MGR
    DRIVER_MGR --> ADB
    DRIVER_MGR --> APPIUM
    APPIUM --> ANDROID
    TEST_RUNNER --> LOGGER
```

## 🔄 Test Execution Workflow

```mermaid
sequenceDiagram
    participant User
    participant GUI
    participant Builder
    participant Runner
    participant Appium
    participant Device
    
    User->>GUI: Create Test Sequence
    GUI->>Builder: Add Actions & Parameters
    Builder->>GUI: Validate Configuration
    User->>GUI: Run Test
    GUI->>Runner: Execute Test Case
    Runner->>Appium: Initialize Driver
    Appium->>Device: Connect to Device
    loop For Each Action
        Runner->>Appium: Execute Action
        Appium->>Device: Perform Action
        Device->>Appium: Return Result
        Appium->>Runner: Action Status
        Runner->>GUI: Update Progress
    end
    Runner->>GUI: Test Complete
    GUI->>User: Display Results
```

## 🎯 Key Features & Capabilities

```mermaid
mindmap
  root((Android GUI Tester))
    User Experience
      Modern Pastel UI
      Interactive Help System
      Real-time Status Updates
      Drag & Drop Test Building
    Testing Capabilities
      100+ Pre-built Actions
      Element Interaction
      Gesture Support
      Screenshot Capture
      Performance Monitoring
    Device Management
      ADB Integration
      Package Discovery
      Device Status Monitoring
      Multi-device Ready
    Test Management
      Save/Load Test Cases
      Parameter Configuration
      Test Validation
      Result Logging
    Technical Features
      Thread-safe Execution
      Error Handling
      Extensible Architecture
      Cross-platform Support
```

## 📊 Technology Stack

```mermaid
graph LR
    subgraph "Frontend"
        TKINTER[Tkinter<br/>GUI Framework]
        CUSTOM[Custom Widgets<br/>Modern Styling]
    end
    
    subgraph "Backend"
        PYTHON[Python 3.x<br/>Core Logic]
        THREADING[Threading<br/>Async Execution]
        JSON[JSON<br/>Configuration]
    end
    
    subgraph "Testing"
        APPIUM[Appium<br/>Mobile Automation]
        ADB[Android Debug Bridge<br/>Device Communication]
        SELENIUM[Selenium<br/>Web Elements]
    end
    
    subgraph "Infrastructure"
        GIT[Git<br/>Version Control]
        PIP[Pip<br/>Dependency Management]
        LOGGING[Logging<br/>Debugging]
    end
    
    TKINTER --> CUSTOM
    CUSTOM --> PYTHON
    PYTHON --> THREADING
    PYTHON --> JSON
    PYTHON --> APPIUM
    APPIUM --> ADB
    APPIUM --> SELENIUM
    PYTHON --> LOGGING
```

## 🚀 Development & Deployment Pipeline

```mermaid
graph TD
    A[Local Development] --> B[Code Review]
    B --> C[Testing]
    C --> D[Documentation]
    D --> E[Git Commit]
    E --> F[Push to GitHub]
    F --> G[Issue Tracking]
    G --> H[Feature Planning]
    H --> A
    
    subgraph "Quality Assurance"
        C1[Unit Tests]
        C2[Integration Tests]
        C3[UI Testing]
        C4[Device Testing]
    end
    
    C --> C1
    C --> C2
    C --> C3
    C --> C4
```

## 📈 Project Metrics & Impact

```mermaid
pie title Lines of Code Distribution
    "GUI Components" : 800
    "Test Actions" : 1200
    "Core Logic" : 600
    "Configuration" : 200
    "Documentation" : 400
    "Utilities" : 300
```

## 🎨 UI/UX Design Philosophy

```mermaid
graph TB
    subgraph "Design Principles"
        MINIMAL[Minimalist Design]
        ACCESSIBLE[Accessibility First]
        RESPONSIVE[Responsive Layout]
        INTUITIVE[Intuitive Navigation]
    end
    
    subgraph "Color Palette"
        PASTEL[Pastel Colors]
        SOFT[Soft Contrasts]
        EYE_FRIENDLY[Eye-friendly]
        PROFESSIONAL[Professional Look]
    end
    
    subgraph "User Experience"
        HOVER[Hover Effects]
        TOOLTIPS[Contextual Help]
        STATUS[Real-time Status]
        FEEDBACK[Visual Feedback]
    end
    
    MINIMAL --> PASTEL
    ACCESSIBLE --> SOFT
    RESPONSIVE --> EYE_FRIENDLY
    INTUITIVE --> PROFESSIONAL
    PASTEL --> HOVER
    SOFT --> TOOLTIPS
    EYE_FRIENDLY --> STATUS
    PROFESSIONAL --> FEEDBACK
```

## Main Features

- 🎨 **Modern UI**: Beautiful pastel-colored interface with hover effects and responsive design
- 🧪 **Test Builder**: Create test sequences by selecting from 100+ pre-built Android actions
- ⚙️ **Parameter Configuration**: Intuitive parameter editor with real-time validation
- 💾 **Test Management**: Save and load test cases in JSON format
- 🔄 **Real-time Execution**: Run tests with live progress updates and detailed logging
- 📱 **Device Integration**: Seamless connection to Android devices via ADB and Appium
- ❓ **Interactive Help**: Comprehensive help system with tooltips and detailed guides
- 📊 **Result Logging**: Detailed test execution logs and error reporting

## What You'll Need

- Python 3.x
- Android SDK with ADB
- Appium-Python-Client
- An Android device with USB debugging enabled

## Quick Start

1. **Get the code:**
```bash
git clone https://github.com/rugveddarwhekar/android_tester.git
cd android_tester
```

2. **Install requirements:**
```bash
pip install -r requirements.txt
```

3. **Run the setup script** (recommended for first-time users):
```bash
python3 setup.py
```

4. **Configure your environment:**
   - Connect your Android device via USB
   - Enable USB Debugging in Developer Options
   - Start Appium Server: `appium`
   - Run setup script again to verify everything is working

5. **Launch the GUI:**
```bash
python3 main.py
```

## Basic Usage

1. **Connect your Android device** and enable USB debugging
2. **Start Appium Server** (default: http://localhost:4723)
3. **Launch the GUI** by running `python3 main.py`
4. **Create a test case**:
   - Select actions from the left panel
   - Configure parameters using the right panel
   - Arrange the sequence using the center panel
5. **Save your test case** for later use
6. **Run the test** and view results

### New User-Friendly Features

- **Interactive Help**: Hover over actions and parameters for detailed explanations
- **Help Button**: Comprehensive help dialog with getting started guide, selector explanations, and troubleshooting tips
- **Welcome Message**: Helpful introduction for new users
- **Visual Guidance**: Clear instructions in each panel
- **Enhanced Descriptions**: Detailed explanations for Android-specific terms and concepts

### Quick Tips for New Users

- Start with simple actions like "Click Element" and "Input Text"
- Use the "Help" button for detailed guidance
- Hover over any field to see helpful hints
- Use TEXT selectors for visible elements (easiest to start with)
- Add "Wait For Element" steps before clicking elements that might not be immediately visible

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

1. **Modern Interface**
   - Beautiful pastel-colored design
   - Responsive layout with hover effects
   - Intuitive navigation and user experience

2. **Comprehensive Testing**
   - 100+ pre-built Android actions
   - Real-time test execution
   - Detailed logging and error reporting

3. **Device Integration**
   - ADB command support
   - Appium server integration
   - Package discovery and management

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

## Troubleshooting

### Common Issues

#### "Driver initialization failed"
This is the most common error. Here's how to fix it:

1. **Check device connection:**
   ```bash
   adb devices
   ```
   You should see your device listed as "device" (not "unauthorized")

2. **Verify Appium server:**
   ```bash
   appium
   ```
   Start Appium server in a separate terminal

3. **Check capabilities configuration:**
   - Edit `config/capabilities.json`
   - Set `appium:deviceName` to your device ID
   - Verify other settings are correct

4. **Run the setup script:**
   ```bash
   python3 setup.py
   ```
   This will diagnose and help fix common issues

#### "ADB not found"
Install Android SDK platform-tools and add to PATH:
- **macOS/Linux:** `export PATH=$PATH:$ANDROID_HOME/platform-tools`
- **Windows:** Add `%ANDROID_HOME%\platform-tools` to PATH

#### "Cannot connect to Appium server"
Start Appium server:
```bash
npm install -g appium
appium
```

#### "No devices found"
- Connect device via USB
- Enable USB Debugging in Developer Options
- Authorize USB debugging on device when prompted

### Getting Help

Found an issue or have a question? [Open an issue](https://github.com/rugveddarwhekar/android_tester/issues) and I'll take a look. 