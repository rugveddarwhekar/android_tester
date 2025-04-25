# runner/test_runner.py
import json
import sys
import os
import importlib

# Assuming utils and actions are sibling directories to runner
project_root = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root) # Ensure project root is in path

from utils.appium_driver import initialize_driver, quit_driver, get_driver

def run_test_case(test_case_path: str):
    """Loads and runs a test case defined in a JSON file."""
    print(f"\n======= Loading Test Case: {test_case_path} =======")
    try:
        with open(test_case_path, 'r') as f:
            test_data = json.load(f)
        print(f"Test Case '{test_data.get('name', 'Unnamed')}' loaded.")
    except FileNotFoundError:
        print(f"Error: Test case file not found: {test_case_path}")
        return False
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in test case file: {test_case_path}")
        return False
    except Exception as e:
        print(f"Error loading test case file {test_case_path}: {e}")
        return False

    steps = test_data.get("steps")
    if not steps or not isinstance(steps, list):
        print("Error: No valid 'steps' array found in the test case file.")
        return False

    driver = None
    overall_status = "Success" # Assume success initially
    try:
        # --- Initialize Driver ---
        print("\n--- Initializing Driver for Test Run ---")
        driver = initialize_driver()
        if driver is None:
            print("Driver initialization failed. Aborting test run.")
            return False # Indicate failure

        print("\n--- Starting Test Execution ---")
        # --- Execute Steps ---
        for i, step in enumerate(steps):
            step_number = i + 1
            action_name = step.get("action")
            params = step.get("params", {})
            notes = step.get("notes", "")

            print(f"\n--- Step {step_number}/{len(steps)} ---")
            print(f"Action: {action_name}")
            if notes: print(f"Notes: {notes}")
            print(f"Params: {params}")

            if not action_name:
                print("Error: Step is missing 'action' name. Skipping.")
                overall_status = "Failed"
                continue # Skip to next step

            try:
                # --- Find and Call Action Function ---
                # Assuming actions are in actions.common_actions for now
                # TODO: Make module loading more dynamic if using app_specific actions
                action_module_name = "actions.common_actions"
                try:
                    action_module = importlib.import_module(action_module_name)
                    action_function = getattr(action_module, action_name)
                except (ImportError, AttributeError) as find_err:
                     print(f"Error finding action '{action_name}' in '{action_module_name}': {find_err}")
                     raise find_err # Re-raise to be caught by outer try

                # Call the function, passing the driver and unpacking params
                # The action function should return (bool_success, result_message)
                success, result_message = action_function(driver, **params)

                print(f"Result: {'Success' if success else 'Failed'} - {result_message}")
                if not success:
                    overall_status = "Failed"
                    # Decide if test should stop on first failure
                    # print("Stopping test run due to step failure.")
                    # break

            except Exception as step_err:
                print(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                print(f"Critical Error during Step {step_number} ('{action_name}'): {step_err}")
                import traceback
                traceback.print_exc()
                print(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                overall_status = "Failed"
                break # Stop test run on critical error within a step

        print("\n--- Test Execution Finished ---")

    except Exception as run_err:
         print(f"An unexpected error occurred during the test run: {run_err}")
         overall_status = "Failed"
         import traceback
         traceback.print_exc()

    finally:
        # --- Quit Driver ---
        print("\n--- Quitting Driver ---")
        quit_driver()

    print(f"\n======= Test Run Summary: {test_case_path} =======")
    print(f"Overall Status: {overall_status}")
    print(f"==================================================")
    return overall_status == "Success"