# gui/main_window.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import json
import os
import threading
import sys
import time
import subprocess # Needed for running ADB
import shlex # For safe command splitting

# Add project root to path for sibling imports
project_root = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import runner only when needed to avoid potential circular imports if runner imports GUI elements later
# from runner.test_runner import run_test_case

# Define path for action library definition
ACTION_LIB_PATH = os.path.join(project_root, "data", "action_library.json")
TEST_CASE_DIR = os.path.join(project_root, "data", "test_cases")


# --- ADB Helper Function ---
def get_installed_packages():
    packages = []
    adb_command = "adb shell pm list packages"
    
    try:
        result = subprocess.run(
            shlex.split(adb_command),
            capture_output=True,
            text=True,
            check=False,
            timeout=15
        )

        if result.returncode == 0 and result.stdout:
            output_lines = result.stdout.strip().splitlines()
            for line in output_lines:
                if line.startswith("package:"):
                    packages.append(line.split(":", 1)[1])
            packages.sort()

    except FileNotFoundError:
        print("'adb' command not found. Is Android SDK platform-tools in your PATH?")
    except subprocess.TimeoutExpired:
        print("ADB command timed out. Is the device responsive?")
    except Exception as e:
        print(f"Error getting packages: {e}")

    return packages


# --- App Class Definition ---
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
        self.main_frame.grid_columnconfigure(2, weight=2) # Params column

        # --- Left Pane: Action Library ---
        self.setup_action_library()

        # --- Center Pane: Test Sequence ---
        self.setup_test_sequence()

        # --- Right Pane: Parameter Editor ---
        self.setup_parameter_editor()

        # --- Bottom Controls ---
        self.setup_controls()

    def setup_action_library(self):
        """Initialize the action library panel"""
        self.action_lib_frame = ttk.LabelFrame(self.main_frame, text="Action Library", padding="5")
        self.action_lib_frame.grid(row=0, column=0, padx=(0, 5), pady=(0, 5), sticky="nsew")
        self.action_lib_frame.rowconfigure(0, weight=1)
        self.action_lib_frame.columnconfigure(0, weight=1)

        # Action Listbox with Scrollbar
        action_lib_scroll_y = ttk.Scrollbar(self.action_lib_frame, orient=tk.VERTICAL)
        self.action_listbox = tk.Listbox(self.action_lib_frame, exportselection=False, yscrollcommand=action_lib_scroll_y.set)
        action_lib_scroll_y.config(command=self.action_listbox.yview)
        self.action_listbox.grid(row=0, column=0, sticky="nsew")
        action_lib_scroll_y.grid(row=0, column=1, sticky="ns")

        # Populate Action Listbox
        for action in self.available_actions:
            self.action_listbox.insert(tk.END, action['display_name'])

        self.add_action_button = ttk.Button(self.action_lib_frame, text="Add Action >>", command=self.add_selected_action)
        self.add_action_button.grid(row=1, column=0, columnspan=2, pady=5)

    def setup_test_sequence(self):
        """Initialize the test sequence panel"""
        self.sequence_frame = ttk.LabelFrame(self.main_frame, text="Test Case Sequence", padding="5")
        self.sequence_frame.grid(row=0, column=1, padx=5, pady=(0, 5), sticky="nsew")
        self.sequence_frame.rowconfigure(0, weight=1) # Listbox expands
        self.sequence_frame.columnconfigure(0, weight=1) # Listbox expands
        self.sequence_frame.columnconfigure(1, weight=0) # Buttons don't expand

        # Sequence Listbox with Scrollbar
        seq_list_scroll_y = ttk.Scrollbar(self.sequence_frame, orient=tk.VERTICAL)
        self.sequence_listbox = tk.Listbox(self.sequence_frame, exportselection=False, yscrollcommand=seq_list_scroll_y.set)
        seq_list_scroll_y.config(command=self.sequence_listbox.yview)
        self.sequence_listbox.grid(row=0, column=0, rowspan=4, sticky="nsew", padx=(0,5))
        seq_list_scroll_y.grid(row=0, column=1, rowspan=4, sticky="ns")
        self.sequence_listbox.bind('<<ListboxSelect>>', self.on_sequence_select) # Bind selection change

        # Sequence Control Buttons Frame
        seq_button_frame = ttk.Frame(self.sequence_frame)
        seq_button_frame.grid(row=0, column=2, rowspan=4, sticky="ns", padx=(5,0))

        self.remove_button = ttk.Button(seq_button_frame, text="Remove Sel.", command=self.remove_selected_action)
        self.remove_button.pack(fill=tk.X, pady=2)
        self.up_button = ttk.Button(seq_button_frame, text="Move Up", command=self.move_action_up)
        self.up_button.pack(fill=tk.X, pady=2)
        self.down_button = ttk.Button(seq_button_frame, text="Move Down", command=self.move_action_down)
        self.down_button.pack(fill=tk.X, pady=2)
        self.clear_button = ttk.Button(seq_button_frame, text="Clear All", command=self.clear_sequence)
        self.clear_button.pack(fill=tk.X, pady=2)

    def setup_parameter_editor(self):
        """Initialize the parameter editor panel"""
        self.param_outer_frame = ttk.LabelFrame(self.main_frame, text="Step Parameters", padding="10")
        self.param_outer_frame.grid(row=0, column=2, padx=(5, 0), pady=(0, 5), sticky="nsew")
        # Add a Canvas and Frame for scrolling parameters if needed
        self.param_canvas = tk.Canvas(self.param_outer_frame, borderwidth=0)
        self.param_scrollbar = ttk.Scrollbar(self.param_outer_frame, orient="vertical", command=self.param_canvas.yview)
        # This frame goes *inside* the canvas and holds the actual param widgets
        self.param_inner_frame = ttk.Frame(self.param_canvas)

        self.param_canvas.configure(yscrollcommand=self.param_scrollbar.set)

        self.param_scrollbar.pack(side="right", fill="y")
        self.param_canvas.pack(side="left", fill="both", expand=True)
        self.param_canvas_window = self.param_canvas.create_window((0,0), window=self.param_inner_frame, anchor="nw")

        # Adjust scrollregion when inner frame size changes
        self.param_inner_frame.bind("<Configure>", self.on_param_frame_configure)
        # Bind canvas scrolling
        self.param_canvas.bind('<Configure>', self.on_param_canvas_configure)

    def setup_controls(self):
        """Initialize the bottom control panel"""
        self.controls_frame = ttk.Frame(self.main_frame, padding="5")
        self.controls_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(5,0))

        self.load_button = ttk.Button(self.controls_frame, text="Load Test Case", command=self.load_test_case_from_file)
        self.load_button.pack(side=tk.LEFT, padx=5)
        self.save_button = ttk.Button(self.controls_frame, text="Save Test Case", command=self.save_test_case_to_file)
        self.save_button.pack(side=tk.LEFT, padx=5)
        self.run_button = ttk.Button(self.controls_frame, text="Run This Test Case", command=self.run_current_test_thread)
        self.run_button.pack(side=tk.RIGHT, padx=5)

        # Status Bar
        self.status_var = tk.StringVar(value="Status: Ready")
        self.status_label = ttk.Label(self, textvariable=self.status_var, anchor=tk.W, relief=tk.SUNKEN) # Added relief
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X, padx=2, pady=2)

    # --- GUI Logic Methods ---

    def on_param_frame_configure(self, event):
        """Update scroll region when parameter frame size changes"""
        self.param_canvas.configure(scrollregion=self.param_canvas.bbox("all"))

    def on_param_canvas_configure(self, event):
        """Adjust inner frame width to match canvas"""
        self.param_canvas.itemconfig(self.param_canvas_window, width=event.width)

    def load_action_library(self):
        """Load and sort action definitions from JSON file"""
        try:
            with open(ACTION_LIB_PATH, 'r') as f:
                actions = json.load(f)
            actions.sort(key=lambda x: x['display_name'])
            return actions
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load action library:\n{e}")
            return []

    def add_selected_action(self):
        """Add selected action to test sequence"""
        selected_indices = self.action_listbox.curselection()
        if not selected_indices:
            return

        action_name = self.action_listbox.get(selected_indices[0])
        action_def = next((a for a in self.available_actions if a['display_name'] == action_name), None)

        if not action_def:
            messagebox.showerror("Error", f"Action not found: {action_name}")
            return

        new_step = {
            "action": action_def['action_id'],
            "params": {p['name']: p.get('default', '') for p in action_def.get('params', [])},
            "notes": "",
            "_display_name": action_def['display_name']
        }
        self.current_test_sequence.append(new_step)
        self.update_sequence_listbox()
        self.sequence_listbox.selection_clear(0, tk.END)
        self.sequence_listbox.selection_set(tk.END)
        self.sequence_listbox.activate(tk.END)
        self.sequence_listbox.see(tk.END)
        self.on_sequence_select(None)

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
         if step_index >= len(self.current_test_sequence): # Check index validity
             print("Warning: Selected index out of bounds.")
             self.clear_param_editor()
             return

         step_data = self.current_test_sequence[step_index]
         action_id = step_data['action']

         # Find the action definition
         action_def = next((a for a in self.available_actions if a['action_id'] == action_id), None)

         self.display_parameter_editor(step_index, step_data, action_def)

    def display_parameter_editor(self, step_index, step_data, action_def):
         """Dynamically creates widgets to edit parameters for the selected step."""
         self.clear_param_editor() # Clear previous widgets

         if not action_def:
             ttk.Label(self.param_inner_frame, text=f"Action definition not found for '{step_data.get('action', 'N/A')}'").pack()
             return
         if not action_def.get('params'):
             ttk.Label(self.param_inner_frame, text="No parameters for this action.").pack()
             return

         # Store references to entry/combo widgets to retrieve values later
         self.param_widgets = {}

         for param_def in action_def['params']:
             param_name = param_def['name']
             label_text = param_def.get('label', param_name) + (":" if param_def.get('required') else " (Optional):")
             current_value = step_data['params'].get(param_name, param_def.get('default', ''))
             param_desc = param_def.get('description') # Get description

             frame = ttk.Frame(self.param_inner_frame) # Add widgets to inner frame now
             frame.pack(fill=tk.X, pady=3, padx=5)

             lbl = ttk.Label(frame, text=label_text, width=20, anchor=tk.W)
             lbl.pack(side=tk.LEFT, padx=5)

             param_type = param_def.get('type', 'string')
             widget = None
             var = None # Define var outside conditional blocks

             # --- Special Handling for Package Name ---
             is_package_param = (action_def.get('action_id') == 'launch_app_by_package' and param_name == 'package_name') # Safer check

             if is_package_param:
                  # --- Debug Print ---
                  print("DEBUG: Displaying editor for package_name parameter.")
                  var = tk.StringVar(value=current_value)
                  package_list = get_installed_packages() # Fetch packages
                  # --- Debug Print ---
                  print(f"DEBUG: Package list received in GUI: {package_list[:5]}...")

                  try:
                       widget = ttk.Combobox(frame, textvariable=var, values=package_list, state="normal" if package_list else "disabled", width=35)
                       self.param_widgets[param_name] = {'widget': widget, 'var': var, 'type': 'package_choice'}
                       # --- Debug Print ---
                       print("DEBUG: Combobox created/updated for packages.")
                  except Exception as e:
                       # --- Debug Print ---
                       print(f"ERROR: Failed to create/update Combobox: {e}")
                       # Fallback to Entry maybe? Show error state
                       var = tk.StringVar(value="Error loading packages!")
                       widget = ttk.Entry(frame, textvariable=var, state="readonly", width=35)
                       self.param_widgets[param_name] = {'widget': widget, 'var': var, 'type': 'string'} # Fallback type

                  if not package_list:
                       warning_lbl = ttk.Label(frame, text=" (No packages found)", foreground="orange")
                       warning_lbl.pack(side=tk.LEFT, padx=2)


             # --- Standard Parameter Widget Creation ---
             elif param_type == "string":
                 var = tk.StringVar(value=current_value)
                 widget = ttk.Entry(frame, textvariable=var, width=35) # Added width
                 self.param_widgets[param_name] = {'widget': widget, 'var': var, 'type': 'string'}
             elif param_type == "integer":
                  # Use try-except for robust default setting
                  try: int_val = int(current_value)
                  except (ValueError, TypeError): int_val = param_def.get('default', 0)
                  var = tk.IntVar(value=int_val)
                  widget = ttk.Spinbox(frame, from_=0, to=9999, textvariable=var, width=8)
                  self.param_widgets[param_name] = {'widget': widget, 'var': var, 'type': 'integer'}
             elif param_type == "float":
                  try: float_val = float(current_value)
                  except (ValueError, TypeError): float_val = param_def.get('default', 0.0)
                  var = tk.DoubleVar(value=float_val)
                  widget = ttk.Spinbox(frame, from_=0.0, to=999.0, increment=0.1, textvariable=var, width=8)
                  self.param_widgets[param_name] = {'widget': widget, 'var': var, 'type': 'float'}
             elif param_type == "boolean":
                 # Handle various ways booleans might be stored (str, int, bool)
                 bool_val = str(current_value).lower() in ['true', '1', 'yes', 'on']
                 var = tk.BooleanVar(value=bool_val)
                 widget = ttk.Checkbutton(frame, variable=var, onvalue=True, offvalue=False)
                 self.param_widgets[param_name] = {'widget': widget, 'var': var, 'type': 'boolean'}
             elif param_type == "choice":
                 options = param_def.get('options', [])
                 var = tk.StringVar(value=current_value)
                 widget = ttk.Combobox(frame, textvariable=var, values=options, state="readonly", width=33) # Added width
                 self.param_widgets[param_name] = {'widget': widget, 'var': var, 'type': 'choice'}
             # Add more types (e.g., filepath with browse button) if needed

             if widget:
                 widget.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
                 # Add description as a tooltip (basic example)
                 if param_desc:
                     # Simple tooltip implementation (can use libraries like tktooltip for better ones)
                     def enter(event, text=param_desc):
                         self.status_var.set(f"Hint: {text}")
                     def leave(event):
                         self.status_var.set(f"Status: Ready") # Or restore previous status
                     widget.bind("<Enter>", enter)
                     widget.bind("<Leave>", leave)

                 # Add trace to update internal data when GUI value changes
                 if var:
                     # Wrap callback args properly using lambda default arguments
                     callback = lambda name, index, mode, sv=var, s_idx=step_index, p_name=param_name: self.update_step_param(s_idx, p_name, sv)
                     var.trace_add("write", callback)

         # Update canvas scroll region after adding widgets
         self.param_inner_frame.update_idletasks()
         self.param_canvas.config(scrollregion=self.param_canvas.bbox("all"))

    def update_step_param(self, step_index, param_name, tk_var):
        """Callback to update the internal sequence data when a param widget changes."""
        # Ensure index is still valid (user might delete steps)
        if step_index < len(self.current_test_sequence):
            try:
                new_value = tk_var.get() # Get value from Tkinter variable

                # Find the widget type to attempt conversion if needed
                widget_info = self.param_widgets.get(param_name)
                target_type = widget_info.get('type') if widget_info else None

                # Perform type conversion based on expected type
                if target_type == 'integer':
                    new_value = int(new_value)
                elif target_type == 'float':
                    new_value = float(new_value)
                elif target_type == 'boolean':
                    # BooleanVar handles its own value correctly
                    new_value = bool(new_value)

                self.current_test_sequence[step_index]['params'][param_name] = new_value
                # print(f"DEBUG: Updated step {step_index}, param {param_name} to {new_value} ({type(new_value).__name__})")

            except ValueError:
                print(f"Warning: Invalid input format for parameter {param_name}. Could not convert '{tk_var.get()}'.")
            except Exception as e:
                 print(f"Error updating param via trace: {e}")

    def clear_param_editor(self):
        """Removes all widgets from the parameter editor frame."""
        for widget in self.param_inner_frame.winfo_children(): # Destroy widgets in inner frame
            widget.destroy()
        self.param_widgets = {}

    def remove_selected_action(self):
        """Removes the selected step from the sequence."""
        selected_indices = self.sequence_listbox.curselection()
        if not selected_indices:
            return
        step_index = selected_indices[0]
        try:
             del self.current_test_sequence[step_index]
             self.update_sequence_listbox()
             # Select next item or previous if last one was deleted
             if self.current_test_sequence:
                 select_idx = min(step_index, len(self.current_test_sequence) - 1)
                 self.sequence_listbox.selection_set(select_idx)
                 self.on_sequence_select(None)
             else:
                 self.clear_param_editor()
        except IndexError:
             print("Error: Index out of range during remove.")

    def move_action_up(self):
        """Moves the selected step one position up."""
        selected_indices = self.sequence_listbox.curselection()
        if not selected_indices or selected_indices[0] == 0:
            return
        idx = selected_indices[0]
        # Swap items
        self.current_test_sequence[idx], self.current_test_sequence[idx-1] = \
            self.current_test_sequence[idx-1], self.current_test_sequence[idx]
        self.update_sequence_listbox()
        # Reselect the moved item
        self.sequence_listbox.selection_set(idx - 1)
        self.sequence_listbox.activate(idx - 1)
        self.on_sequence_select(None) # Update params for selected item

    def move_action_down(self):
        """Moves the selected step one position down."""
        selected_indices = self.sequence_listbox.curselection()
        last_index = len(self.current_test_sequence) - 1
        if not selected_indices or selected_indices[0] == last_index:
            return
        idx = selected_indices[0]
        # Swap items
        self.current_test_sequence[idx], self.current_test_sequence[idx+1] = \
            self.current_test_sequence[idx+1], self.current_test_sequence[idx]
        self.update_sequence_listbox()
        # Reselect the moved item
        self.sequence_listbox.selection_set(idx + 1)
        self.sequence_listbox.activate(idx + 1)
        self.on_sequence_select(None) # Update params for selected item

    def clear_sequence(self):
        if messagebox.askyesno("Confirm", "Clear the entire test sequence? This cannot be undone."):
            self.current_test_sequence = []
            self.update_sequence_listbox()
            self.clear_param_editor()

    def save_test_case_to_file(self):
        if not self.current_test_sequence:
            messagebox.showwarning("Warning", "Test sequence is empty, nothing to save.")
            return

        current_selection = self.sequence_listbox.curselection()
        if current_selection:
            self.force_update_params_from_widgets(current_selection[0])

        if not os.path.exists(TEST_CASE_DIR):
            os.makedirs(TEST_CASE_DIR)

        filepath = filedialog.asksaveasfilename(
            title="Save Test Case As",
            initialdir=TEST_CASE_DIR,
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if not filepath:
            return

        test_name = os.path.splitext(os.path.basename(filepath))[0]
        test_description = simpledialog.askstring("Description", "Enter a brief test case description:", parent=self)
        if test_description is None: 
            test_description = "Test case created with GUI Tester"

        test_data_to_save = {
            "name": test_name,
            "description": test_description,
            "steps": self.current_test_sequence
        }

        try:
            with open(filepath, 'w') as f:
                json.dump(test_data_to_save, f, indent=2)
            self.status_var.set(f"Status: Saved test case to {os.path.basename(filepath)}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save test case:\n{e}")

    def load_test_case_from_file(self):
        filepath = filedialog.askopenfilename(
            title="Load Test Case File",
            initialdir=TEST_CASE_DIR,
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if not filepath:
            return

        try:
            with open(filepath, 'r') as f:
                loaded_data = json.load(f)

            if "steps" not in loaded_data or not isinstance(loaded_data["steps"], list):
                raise ValueError("Invalid test case file format: 'steps' array missing or invalid.")

            for step in loaded_data["steps"]:
                if "_display_name" not in step:
                    action_def = next((a for a in self.available_actions if a['action_id'] == step['action']), None)
                    step["_display_name"] = action_def['display_name'] if action_def else step['action']

            self.current_test_sequence = loaded_data["steps"]
            self.update_sequence_listbox()
            self.clear_param_editor()
            
            if self.current_test_sequence:
                self.sequence_listbox.selection_set(0)
                self.on_sequence_select(None)

            self.status_var.set(f"Status: Loaded test case {os.path.basename(filepath)}")

        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load test case:\n{e}")

    def run_current_test_thread(self):
        if not self.current_test_sequence:
            messagebox.showwarning("Warning", "Test sequence is empty. Add steps first.")
            return

        current_selection = self.sequence_listbox.curselection()
        if current_selection:
            self.force_update_params_from_widgets(current_selection[0])

        test_data = {
            "name": "GUI Generated Test",
            "description": "Test case run from GUI builder",
            "steps": self.current_test_sequence
        }

        self.run_button.config(state=tk.DISABLED)
        self.status_var.set(f"Status: Running test '{test_data['name']}'...")

        from runner.test_runner import run_test_case

        test_thread = threading.Thread(
            target=self.execute_test_and_update_gui,
            args=(test_data, run_test_case),
            daemon=True
        )
        test_thread.start()

    def force_update_params_from_widgets(self, step_index):
        if step_index < len(self.current_test_sequence):
            for param_name, widget_info in self.param_widgets.items():
                var = widget_info.get('var')
                if var:
                    try:
                        new_value = var.get()
                        target_type = widget_info.get('type')
                        if target_type == 'integer': new_value = int(new_value)
                        elif target_type == 'float': new_value = float(new_value)
                        elif target_type == 'boolean': new_value = bool(new_value)
                        self.current_test_sequence[step_index]['params'][param_name] = new_value
                    except (ValueError, tk.TclError) as e:
                        print(f"Warning: Error updating param {param_name}: {e}")
                    except Exception as e:
                        print(f"Warning: Unexpected error updating param {param_name}: {e}")

    def execute_test_and_update_gui(self, test_data_to_run, runner_func):
        test_name = test_data_to_run.get("name", "Unnamed")
        start_time = time.time()
        final_status_text = f"Status: Finished: {test_name} - Unknown"
        results_log = []
        
        try:
            success, results_log = runner_func(test_data_to_run)
            result_status = "Success" if success else "Failed"
            duration = time.time() - start_time
            final_status_text = f"Status: Finished: {test_name} - {result_status} ({duration:.2f}s)"
            
            for entry in results_log:
                print(f"  Step {entry.get('step', '?')}: [{entry.get('action', 'N/A')}] - {entry.get('status', 'Unknown')} - {entry.get('message', '')}")

        except Exception as e:
            duration = time.time() - start_time
            print(f"Error in test thread: {e}")
            final_status_text = f"Status: Error during test run: {test_name} ({duration:.2f}s)"
            self.after(0, lambda: messagebox.showerror("Test Execution Error", f"An error occurred:\n{e}"))
            
        finally:
            self.after(0, self.status_var.set, final_status_text)
            self.after(0, self.run_button.config, {"state": tk.NORMAL})


# --- Main execution logic moved to main.py ---
# if __name__ == '__main__':
#    app = App()
#    app.mainloop()