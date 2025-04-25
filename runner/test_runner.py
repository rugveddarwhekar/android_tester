# runner/test_runner.py
import json
import sys
import os
import importlib
import time # Add time import if needed for pauses

# Assuming utils and actions are sibling directories to runner
project_root = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
     sys.path.insert(0, project_root)

from utils.appium_driver import initialize_driver, quit_driver, get_driver

# --- Mapping from simple action names to functions ---
# This helps dynamically call functions based on the 'action' string
# Assumes all actions are currently in 'common_actions'
# TODO: Make this more dynamic later if using app_specific actions
ACTION_MAPPING = {}
try:
    common_actions_module = importlib.import_module("actions.common_actions")
    # Inspect the module and add functions to the mapping
    # This avoids manually listing every function
    import inspect
    for name, func in inspect.getmembers(common_actions_module, inspect.isfunction):
         ACTION_MAPPING[name] = func
    print(f"Loaded Actions: {list(ACTION_MAPPING.keys())}")
except ImportError as e:
    print(f"FATAL ERROR: Could not load actions.common_actions: {e}")
    ACTION_MAPPING = {} # Ensure it's empty if import fails


def run_test_case(test_data: dict): # Accepts the test data dict directly
    """Runs a test case defined by the provided data structure."""
    test_name = test_data.get('name', 'Unnamed Test')
    print(f"\n======= Running Test Case: {test_name} =======")

    steps = test_data.get("steps")
    if not steps or not isinstance(steps, list):
        print("Error: No valid 'steps' array found in the test data.")
        return False # Indicate failure to run

    driver = None
    overall_status = "Success"
    results_log = [] # Store results per step

    try:
        # --- Initialize Driver ---
        print("\n--- Initializing Driver for Test Run ---")
        driver = initialize_driver()
        if driver is None:
            print("Driver initialization failed. Aborting test run.")
            results_log.append({"step": "Setup", "status": "Failed", "message": "Driver initialization failed"})
            return False, results_log # Indicate failure and return logs

        print("\n--- Starting Test Execution ---")
        # --- Execute Steps ---
        for i, step in enumerate(steps):
            step_number = i + 1
            action_name = step.get("action")
            params = step.get("params", {})
            notes = step.get("notes", "")
            step_status = "Failed" # Default status for the step
            result_message = "Action not found or not executed." # Default message

            print(f"\n--- Step {step_number}/{len(steps)} ---")
            print(f"Action: {action_name}")
            if notes: print(f"Notes: {notes}")
            print(f"Params: {params}")

            if not action_name:
                print("Error: Step is missing 'action' name. Skipping.")
                result_message = "Step missing 'action' name."
                overall_status = "Failed"
                results_log.append({"step": step_number, "action": action_name, "status": step_status, "message": result_message})
                continue

            # --- Find and Call Action Function ---
            action_function = ACTION_MAPPING.get(action_name)

            if not action_function:
                result_message = f"Action '{action_name}' not found in available actions."
                print(f"Error: {result_message}")
                overall_status = "Failed"
                # Decide if test should stop if action not found
                # break
            else:
                try:
                    # Call the function, passing the driver and unpacking params
                    # Expecting (bool_success, result_message_from_action)
                    print(f"Executing: {action_function.__name__}(driver=..., **{params})")
                    success, result_message_from_action = action_function(driver, **params)
                    result_message = result_message_from_action # Use message from action

                    if success:
                        step_status = "Success"
                        print(f"Result: {step_status} - {result_message}")
                    else:
                        step_status = "Failed"
                        print(f"Result: {step_status} - {result_message}")
                        overall_status = "Failed"
                        # Decide if test should stop on first failure
                        # print("Stopping test run due to step failure.")
                        # break

                except TypeError as te:
                     # Catch errors if params don't match function signature
                     err_msg = f"Parameter mismatch calling action '{action_name}' with params {params}. Error: {te}"
                     print(f"CRITICAL STEP ERROR: {err_msg}")
                     result_message = err_msg
                     overall_status = "Failed"
                     break # Stop on critical error
                except Exception as step_err:
                     # Catch unexpected errors during the action's execution
                     err_msg = f"Unexpected error during action '{action_name}': {step_err}"
                     print(f"CRITICAL STEP ERROR: {err_msg}")
                     import traceback
                     traceback.print_exc() # Print full traceback for debugging
                     result_message = err_msg
                     overall_status = "Failed"
                     break # Stop on critical error

            # Log result for this step
            results_log.append({"step": step_number, "action": action_name, "status": step_status, "message": result_message})

        print("\n--- Test Execution Finished ---")

    except Exception as run_err:
         print(f"An unexpected error occurred during the test run orchestration: {run_err}")
         overall_status = "Failed"
         results_log.append({"step": "Orchestration", "status": "Failed", "message": str(run_err)})
         import traceback
         traceback.print_exc()

    finally:
        # --- Quit Driver ---
        print("\n--- Quitting Driver ---")
        quit_driver()

    print(f"\n======= Test Run Summary: {test_name} =======")
    print(f"Overall Status: {overall_status}")
    print("Detailed Log:")
    for log_entry in results_log:
         print(f"  Step {log_entry.get('step', '?')}: [{log_entry.get('action', 'N/A')}] - {log_entry.get('status', 'Unknown')} - {log_entry.get('message', '')}")
    print(f"==================================================")

    return overall_status == "Success", results_log # Return status and detailed logs