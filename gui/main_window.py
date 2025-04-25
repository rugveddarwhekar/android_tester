# gui/main_window.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import threading # To run Appium tests without freezing GUI

# Need to ensure runner can be imported
project_root = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))
import sys
sys.path.insert(0, project_root) # Add project root to path

from runner.test_runner import run_test_case

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Android GUI Tester")
        self.geometry("800x600")

        # --- Basic Layout ---
        self.main_frame = ttk.Frame(self, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Placeholder Label
        self.label = ttk.Label(self.main_frame, text="GUI Test Builder Interface (Placeholder)")
        self.label.pack(pady=20)

        # --- Test Runner Section (Simple) ---
        self.runner_frame = ttk.LabelFrame(self.main_frame, text="Run Test Case", padding="10")
        self.runner_frame.pack(pady=10, fill=tk.X)

        self.selected_test_case_path = tk.StringVar()

        self.test_case_entry = ttk.Entry(self.runner_frame, textvariable=self.selected_test_case_path, width=60)
        self.test_case_entry.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.browse_button = ttk.Button(self.runner_frame, text="Browse...", command=self.browse_test_case)
        self.browse_button.grid(row=0, column=1, padx=5, pady=5)

        self.run_button = ttk.Button(self.runner_frame, text="Run Selected Test", command=self.run_selected_test_thread)
        self.run_button.grid(row=1, column=0, columnspan=2, pady=10)

        self.runner_frame.columnconfigure(0, weight=1) # Make entry expand

        # Status Area (Optional - for messages)
        self.status_label = ttk.Label(self.main_frame, text="Status: Ready")
        self.status_label.pack(pady=10, side=tk.BOTTOM, fill=tk.X)

        # TODO: Add frames/widgets for test building (Action List, Sequence View) later


    def browse_test_case(self):
        """Opens file dialog to select a test case JSON file."""
        # Define initial directory relative to project root
        initial_dir = os.path.join(project_root, "data", "test_cases")
        filepath = filedialog.askopenfilename(
            title="Select Test Case File",
            initialdir=initial_dir,
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filepath:
            self.selected_test_case_path.set(filepath)
            self.status_label.config(text=f"Selected: {os.path.basename(filepath)}")

    def run_selected_test_thread(self):
        """Runs the test case in a separate thread to avoid freezing the GUI."""
        test_path = self.selected_test_case_path.get()
        if not test_path or not os.path.exists(test_path):
            messagebox.showerror("Error", "Please select a valid test case file.")
            return

        # Disable run button during execution
        self.run_button.config(state=tk.DISABLED)
        self.status_label.config(text=f"Running: {os.path.basename(test_path)}...")

        # Run test_runner.run_test_case in a separate thread
        test_thread = threading.Thread(
            target=self.execute_test_and_update_gui,
            args=(test_path,),
            daemon=True # Allows closing main window even if thread is running (use carefully)
        )
        test_thread.start()

    def execute_test_and_update_gui(self, test_path):
        """Target function for the test thread."""
        try:
            success = run_test_case(test_path) # Call the runner function
            result_status = "Success" if success else "Failed"
            self.status_label.config(text=f"Finished: {os.path.basename(test_path)} - {result_status}")
        except Exception as e:
             print(f"Error in test thread: {e}") # Log error to console
             self.status_label.config(text=f"Error during test run: {os.path.basename(test_path)}")
             messagebox.showerror("Test Execution Error", f"An error occurred:\n{e}")
        finally:
            # Re-enable run button using thread-safe method if needed (simple update here)
             # If using complex GUI updates, would need queue or after() method
             self.run_button.config(state=tk.NORMAL)


if __name__ == '__main__':
    # This block is for testing the GUI directly (optional)
    app = App()
    app.mainloop()