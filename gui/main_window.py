# gui/main_window.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import json
import os
import threading
import sys

# Add project root to path for sibling imports
project_root = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from runner.test_runner import run_test_case # Import the modified runner

# Define path for action library definition
ACTION_LIB_PATH = os.path.join(project_root, "data", "action_library.json")
TEST_CASE_DIR = os.path.join(project_root, "data", "test_cases")


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Android GUI Tester")
        self.geometry("1000x700") # Increased size

        # --- Data Structures ---
        self.available_actions = self.load_action_library() # Load actions from JSON
        self.current_test_sequence = [] # List to hold step dictionaries
        self.param_widgets = {} # To hold currently displayed param widgets

        # --- Main Layout ---
        self.main_frame = ttk.Frame(self, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.main_frame.grid_rowconfigure(0, weight=1) # Make builder area expand
        self.main_frame.grid_columnconfigure(1, weight=3) # Make sequence/params expand

        # --- Left Pane: Action Library ---
        self.action_lib_frame = ttk.LabelFrame(self.main_frame, text="Action Library", padding="5")
        self.action_lib_frame.grid(row=0, column=0, padx=(0, 5), pady=(0, 5), sticky="nsew")
        self.action_lib_frame.rowconfigure(0, weight=1)
        self.action_lib_frame.columnconfigure(0, weight=1)

        self.action_listbox = tk.Listbox(self.action_lib_frame, exportselection=False)
        self.action_listbox.grid(row=0, column=0, sticky="nsew")
        # Populate Action Listbox
        for action in self.available_actions:
            self.action_listbox.insert(tk.END, action['display_name'])

        self.add_action_button = ttk.Button(self.action_lib_frame, text="Add Action >>", command=self.add_selected_action)
        self.add_action_button.grid(row=1, column=0, pady=5)

        # --- Center Pane: Test Sequence ---
        self.sequence_frame = ttk.LabelFrame(self.main_frame, text="Test Case Sequence", padding="5")
        self.sequence_frame.grid(row=0, column=1, padx=5, pady=(0, 5), sticky="nsew")
        self.sequence_frame.rowconfigure(0, weight=1) # Listbox expands
        self.sequence_frame.columnconfigure(0, weight=1) # Listbox expands
        self.sequence_frame.columnconfigure(1, weight=0) # Buttons don't expand

        self.sequence_listbox = tk.Listbox(self.sequence_frame, exportselection=False)
        self.sequence_listbox.grid(row=0, column=0, rowspan=4, sticky="nsew", padx=(0,5))
        self.sequence_listbox.bind('<<ListboxSelect>>', self.on_sequence_select) # Bind selection change

        # Sequence Control Buttons
        self.remove_button = ttk.Button(self.sequence_frame, text="Remove Selected", command=self.remove_selected_action)
        self.remove_button.grid(row=0, column=1, sticky="ew", pady=2)
        self.up_button = ttk.Button(self.sequence_frame, text="Move Up", command=self.move_action_up)
        self.up_button.grid(row=1, column=1, sticky="ew", pady=2)
        self.down_button = ttk.Button(self.sequence_frame, text="Move Down", command=self.move_action_down)
        self.down_button.grid(row=2, column=1, sticky="ew", pady=2)
        self.clear_button = ttk.Button(self.sequence_frame, text="Clear All", command=self.clear_sequence)
        self.clear_button.grid(row=3, column=1, sticky="ew", pady=2)

        # --- Right Pane: Parameter Editor ---
        self.param_frame = ttk.LabelFrame(self.main_frame, text="Step Parameters", padding="10")
        self.param_frame.grid(row=0, column=2, padx=(5, 0), pady=(0, 5), sticky="nsew")
        # Parameter widgets will be added dynamically here by on_sequence_select

        # --- Bottom Controls ---
        self.controls_frame = ttk.Frame(self.main_frame, padding="5")
        self.controls_frame.grid(row=1, column=0, columnspan=3, sticky="ew")

        self.load_button = ttk.Button(self.controls_frame, text="Load Test Case", command=self.load_test_case_from_file)
        self.load_button.pack(side=tk.LEFT, padx=5)
        self.save_button = ttk.Button(self.controls_frame, text="Save Test Case", command=self.save_test_case_to_file)
        self.save_button.pack(side=tk.LEFT, padx=5)
        self.run_button = ttk.Button(self.controls_frame, text="Run This Test Case", command=self.run_current_test_thread)
        self.run_button.pack(side=tk.RIGHT, padx=5)

        # Status Bar
        self.status_var = tk.StringVar(value="Status: Ready")
        self.status_label = ttk.Label(self, textvariable=self.status_var, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=2)

    # --- GUI Logic Methods ---

    def load_action_library(self):
        """Loads action definitions from the JSON file."""
        try:
            with open(ACTION_LIB_PATH, 'r') as f:
                actions = json.load(f)
            print(f"Loaded {len(actions)} actions from {ACTION_LIB_PATH}")
            return actions
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load action library {ACTION_LIB_PATH}:\n{e}")
            return []

    def add_selected_action(self):
        """Adds the selected action from the library to the sequence."""
        selected_indices = self.action_listbox.curselection()
        if not selected_indices:
            return # Nothing selected

        action_index = selected_indices[0]
        action_def = self.available_actions[action_index]

        # Create a new step entry with default/empty params
        new_step = {
            "action": action_def['action_id'],
            "params": {p['name']: p.get('default', '') for p in action_def.get('params', [])},
            "notes": "", # Add notes later if needed
            "_display_name": action_def['display_name'] # Store for display
        }
        self.current_test_sequence.append(new_step)
        self.update_sequence_listbox()
        # Select the newly added item
        self.sequence_listbox.selection_clear(0, tk.END)
        self.sequence_listbox.selection_set(tk.END)
        self.sequence_listbox.activate(tk.END)
        self.on_sequence_select(None) # Trigger param editor update


    def update_sequence_listbox(self):
        """Refreshes the sequence listbox from the internal data."""
        self.sequence_listbox.delete(0, tk.END)
        for i, step in enumerate(self.current_test_sequence):
            display_text = f"{i+1}. {step.get('_display_name', step['action'])}"
            self.sequence_listbox.insert(tk.END, display_text)

    def on_sequence_select(self, event):
         """Called when an item in the sequence listbox is selected."""
         selected_indices = self.sequence_listbox.curselection()
         if not selected_indices:
             self.clear_param_editor()
             return

         step_index = selected_indices[0]
         step_data = self.current_test_sequence[step_index]
         action_id = step_data['action']

         # Find the action definition
         action_def = next((a for a in self.available_actions if a['action_id'] == action_id), None)

         self.display_parameter_editor(step_index, step_data, action_def)


    def display_parameter_editor(self, step_index, step_data, action_def):
         """Dynamically creates widgets to edit parameters for the selected step."""
         self.clear_param_editor() # Clear previous widgets

         if not action_def or not action_def.get('params'):
             ttk.Label(self.param_frame, text="No parameters for this action.").pack()
             return

         # Store references to entry/combo widgets to retrieve values later
         self.param_widgets = {}

         for param_def in action_def['params']:
             param_name = param_def['name']
             label_text = param_def.get('label', param_name) + (":" if param_def.get('required') else " (Optional):")
             current_value = step_data['params'].get(param_name, param_def.get('default', ''))

             frame = ttk.Frame(self.param_frame)
             frame.pack(fill=tk.X, pady=2)

             lbl = ttk.Label(frame, text=label_text, width=15, anchor=tk.W)
             lbl.pack(side=tk.LEFT, padx=5)

             param_type = param_def.get('type', 'string')
             widget = None

             if param_type == "string":
                 var = tk.StringVar(value=current_value)
                 widget = ttk.Entry(frame, textvariable=var)
                 self.param_widgets[param_name] = {'widget': widget, 'var': var, 'type': 'string'}
             elif param_type == "integer":
                  var = tk.IntVar(value=current_value if isinstance(current_value, int) else param_def.get('default', 0))
                  widget = ttk.Spinbox(frame, from_=0, to=9999, textvariable=var, width=8) # Example range
                  self.param_widgets[param_name] = {'widget': widget, 'var': var, 'type': 'integer'}
             elif param_type == "float":
                  var = tk.DoubleVar(value=current_value if isinstance(current_value, float) else param_def.get('default', 0.0))
                  widget = ttk.Spinbox(frame, from_=0.0, to=999.0, increment=0.1, textvariable=var, width=8) # Example range
                  self.param_widgets[param_name] = {'widget': widget, 'var': var, 'type': 'float'}
             elif param_type == "boolean":
                 var = tk.BooleanVar(value=bool(current_value))
                 widget = ttk.Checkbutton(frame, variable=var, onvalue=True, offvalue=False)
                 self.param_widgets[param_name] = {'widget': widget, 'var': var, 'type': 'boolean'}
             elif param_type == "choice":
                 options = param_def.get('options', [])
                 var = tk.StringVar(value=current_value)
                 widget = ttk.Combobox(frame, textvariable=var, values=options, state="readonly")
                 self.param_widgets[param_name] = {'widget': widget, 'var': var, 'type': 'choice'}
             # Add more types as needed (e.g., file path)

             if widget:
                 widget.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
                 # Add trace to update internal data when GUI value changes
                 var.trace_add("write", lambda name, index, mode, sv=var, s_idx=step_index, p_name=param_name: self.update_step_param(s_idx, p_name, sv))


    def update_step_param(self, step_index, param_name, string_var):
        """Callback to update the internal sequence data when a param widget changes."""
        if step_index < len(self.current_test_sequence):
            try:
                new_value = string_var.get()
                # Attempt type conversion based on widget info if needed
                widget_info = self.param_widgets.get(param_name)
                if widget_info:
                    if widget_info['type'] == 'integer': new_value = int(new_value)
                    elif widget_info['type'] == 'float': new_value = float(new_value)
                    elif widget_info['type'] == 'boolean': new_value = bool(new_value) # Checkbutton handles this
                self.current_test_sequence[step_index]['params'][param_name] = new_value
                # print(f"DEBUG: Updated step {step_index}, param {param_name} to {new_value}") # For debugging
            except ValueError:
                print(f"Warning: Invalid input for parameter {param_name}") # Handle type errors later
            except Exception as e:
                 print(f"Error updating param: {e}")


    def clear_param_editor(self):
        """Removes all widgets from the parameter editor frame."""
        for widget in self.param_frame.winfo_children():
            widget.destroy()
        self.param_widgets = {}


    def remove_selected_action(self):
        """Removes the selected step from the sequence."""
        selected_indices = self.sequence_listbox.curselection()
        if not selected_indices:
            return
        step_index = selected_indices[0]
        del self.current_test_sequence[step_index]
        self.update_sequence_listbox()
        self.clear_param_editor()

    def move_action_up(self):
         """Moves the selected step one position up."""
         selected_indices = self.sequence_listbox.curselection()
         if not selected_indices or selected_indices[0] == 0:
             return
         idx = selected_indices[0]
         item = self.current_test_sequence.pop(idx)
         self.current_test_sequence.insert(idx - 1, item)
         self.update_sequence_listbox()
         self.sequence_listbox.selection_set(idx - 1)
         self.sequence_listbox.activate(idx - 1)
         self.on_sequence_select(None)


    def move_action_down(self):
        """Moves the selected step one position down."""
        selected_indices = self.sequence_listbox.curselection()
        last_index = len(self.current_test_sequence) - 1
        if not selected_indices or selected_indices[0] == last_index:
            return
        idx = selected_indices[0]
        item = self.current_test_sequence.pop(idx)
        self.current_test_sequence.insert(idx + 1, item)
        self.update_sequence_listbox()
        self.sequence_listbox.selection_set(idx + 1)
        self.sequence_listbox.activate(idx + 1)
        self.on_sequence_select(None)


    def clear_sequence(self):
         if messagebox.askyesno("Confirm", "Clear the entire test sequence?"):
            self.current_test_sequence = []
            self.update_sequence_listbox()
            self.clear_param_editor()

    def save_test_case_to_file(self):
        """Saves the current sequence to a JSON file."""
        if not self.current_test_sequence:
            messagebox.showwarning("Warning", "Test sequence is empty, nothing to save.")
            return

        filepath = filedialog.asksaveasfilename(
            title="Save Test Case As",
            initialdir=TEST_CASE_DIR,
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if not filepath:
            return # User cancelled

        # Prepare data to save (including name/description if added later)
        test_name = os.path.splitext(os.path.basename(filepath))[0] # Use filename as default name
        test_data_to_save = {
            "name": test_name,
            "description": "Test case created with GUI Tester", # Add description field later
            "steps": self.current_test_sequence # Save the sequence built in GUI
        }

        try:
            with open(filepath, 'w') as f:
                json.dump(test_data_to_save, f, indent=2)
            self.status_var.set(f"Status: Saved test case to {os.path.basename(filepath)}")
            messagebox.showinfo("Success", f"Test case saved successfully!")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save test case:\n{e}")


    def load_test_case_from_file(self):
        """Loads a test sequence from a JSON file."""
        filepath = filedialog.askopenfilename(
            title="Load Test Case File",
            initialdir=TEST_CASE_DIR,
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if not filepath:
            return # User cancelled

        try:
            with open(filepath, 'r') as f:
                loaded_data = json.load(f)

            if "steps" not in loaded_data or not isinstance(loaded_data["steps"], list):
                raise ValueError("Invalid test case file format: 'steps' array missing or invalid.")

            # Add display name back if missing (for older saves)
            for step in loaded_data["steps"]:
                 if "_display_name" not in step:
                     action_def = next((a for a in self.available_actions if a['action_id'] == step['action']), None)
                     step["_display_name"] = action_def['display_name'] if action_def else step['action']

            self.current_test_sequence = loaded_data["steps"]
            self.update_sequence_listbox()
            self.clear_param_editor()
            self.status_var.set(f"Status: Loaded test case {os.path.basename(filepath)}")
            messagebox.showinfo("Success", "Test case loaded.")

        except Exception as e:
             messagebox.showerror("Load Error", f"Failed to load test case:\n{e}")


    def run_current_test_thread(self):
        """Runs the test case currently built in the GUI."""
        if not self.current_test_sequence:
            messagebox.showwarning("Warning", "Test sequence is empty. Add steps first.")
            return

        # --- Important: Update params from GUI just before running ---
        # This ensures the latest values from the editor are used,
        # even if the trace callbacks didn't catch everything perfectly.
        current_selection = self.sequence_listbox.curselection()
        if current_selection:
             self.force_update_params_from_widgets(current_selection[0])
        # ---

        # Create the test data structure
        test_data = {
            "name": "GUI Generated Test", # Add name field later
            "description": "Test case run from GUI builder",
            "steps": self.current_test_sequence # Use the sequence built in GUI
        }

        self.run_button.config(state=tk.DISABLED)
        self.status_var.set(f"Status: Running test '{test_data['name']}'...")
        print(f"--- Preparing to run test: {test_data['name']} ---")
        print(f"Steps Data: {json.dumps(test_data['steps'], indent=2)}") # Log the data being sent


        # Run in thread
        test_thread = threading.Thread(
            target=self.execute_test_and_update_gui,
            args=(test_data,), # Pass the data structure directly
            daemon=True
        )
        test_thread.start()

    def force_update_params_from_widgets(self, step_index):
         """Manually read values from param widgets for the selected step."""
         if step_index < len(self.current_test_sequence):
             print(f"DEBUG: Forcing param update for step {step_index}")
             for param_name, widget_info in self.param_widgets.items():
                 var = widget_info.get('var')
                 if var:
                     try:
                         new_value = var.get()
                         # Type conversion (same as in trace callback)
                         if widget_info['type'] == 'integer': new_value = int(new_value)
                         elif widget_info['type'] == 'float': new_value = float(new_value)
                         elif widget_info['type'] == 'boolean': new_value = bool(new_value)
                         self.current_test_sequence[step_index]['params'][param_name] = new_value
                     except Exception as e:
                          print(f"Warning: Error force updating param {param_name}: {e}")


    def execute_test_and_update_gui(self, test_data_to_run):
        """Target function for the test thread - calls the runner."""
        test_name = test_data_to_run.get("name", "Unnamed")
        final_status_text = f"Status: Finished: {test_name} - Unknown"
        try:
            # Call the modified runner function
            success, results_log = run_test_case(test_data_to_run)
            result_status = "Success" if success else "Failed"
            final_status_text = f"Status: Finished: {test_name} - {result_status}"
            # Optionally display results_log in a popup or text area
            print("--- Test Run Detailed Log ---")
            for entry in results_log:
                 print(f"  Step {entry.get('step', '?')}: [{entry.get('action', 'N/A')}] - {entry.get('status', 'Unknown')} - {entry.get('message', '')}")
            print("---------------------------")

        except Exception as e:
             print(f"Error in test thread: {e}")
             final_status_text = f"Status: Error during test run: {test_name}"
             # Show error in GUI too
             # Note: Directly calling messagebox from thread can sometimes be unstable in Tkinter.
             # A safer way involves using root.after() or queues, but this might work for simple cases.
             messagebox.showerror("Test Execution Error", f"An error occurred:\n{e}")
        finally:
            # Update GUI from the main thread if possible, or directly if simple
            self.status_var.set(final_status_text)
            self.run_button.config(state=tk.NORMAL)

# Main execution moved to main.py