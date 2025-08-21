# gui/modern_window.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import json
import os
import threading
import sys
import time
import subprocess
import shlex
from typing import Dict, List, Any

project_root = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

ACTION_LIB_PATH = os.path.join(project_root, "data", "action_library.json")
TEST_CASE_DIR = os.path.join(project_root, "data", "test_cases")

# Pastel color palette
COLORS = {
    'primary': '#E8F4FD',      # Soft blue
    'secondary': '#F0F8FF',    # Alice blue
    'accent': '#B8E6B8',       # Soft green
    'accent_hover': '#A8D8A8', # Darker green
    'text': '#2C3E50',         # Dark blue-gray
    'text_light': '#7F8C8D',   # Light gray
    'border': '#D5DBDB',       # Light gray border
    'success': '#D5F4E6',      # Soft mint
    'warning': '#FDEBD0',      # Soft orange
    'error': '#FADBD8',        # Soft red
    'white': '#FFFFFF',
    'shadow': '#E8E8E8'
}

def get_installed_packages():
    """Get list of installed packages from Android device"""
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

class ModernButton(tk.Button):
    """Custom button with modern styling"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(
            relief="flat",
            borderwidth=0,
            font=("Segoe UI", 9),
            cursor="hand2",
            bg=COLORS['accent'],
            fg=COLORS['text'],
            activebackground=COLORS['accent_hover'],
            activeforeground=COLORS['text'],
            padx=12,
            pady=6
        )
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
    
    def _on_enter(self, event):
        self.configure(bg=COLORS['accent_hover'])
    
    def _on_leave(self, event):
        self.configure(bg=COLORS['accent'])

class ModernFrame(tk.Frame):
    """Custom frame with modern styling"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(
            bg=COLORS['white'],
            relief="flat",
            borderwidth=1,
            highlightbackground=COLORS['border'],
            highlightthickness=1
        )

class ModernListbox(tk.Listbox):
    """Custom listbox with modern styling"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(
            relief="flat",
            borderwidth=1,
            font=("Segoe UI", 9),
            bg=COLORS['white'],
            fg=COLORS['text'],
            selectbackground=COLORS['accent'],
            selectforeground=COLORS['text'],
            highlightbackground=COLORS['border'],
            highlightthickness=1,
            activestyle="none"
        )

class ModernEntry(tk.Entry):
    """Custom entry with modern styling"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(
            relief="flat",
            borderwidth=1,
            font=("Segoe UI", 9),
            bg=COLORS['white'],
            fg=COLORS['text'],
            insertbackground=COLORS['text'],
            highlightbackground=COLORS['border'],
            highlightthickness=1,
            highlightcolor=COLORS['accent']
        )

class App(tk.Tk):
    """Modern Android GUI Tester Application"""
    
    def __init__(self):
        super().__init__()
        
        # Configure main window
        self.title("Android GUI Tester")
        self.geometry("1200x800")
        self.configure(bg=COLORS['primary'])
        
        # Set minimum window size
        self.minsize(1000, 600)
        
        # Initialize data
        self.available_actions = self.load_action_library()
        self.current_test_sequence = []
        self.param_widgets = {}
        
        # Setup modern styling
        self.setup_styles()
        
        # Create main layout
        self.create_layout()
        
        # Initialize components
        self.setup_action_library()
        self.setup_test_sequence()
        self.setup_parameter_editor()
        self.setup_controls()
        
        # Show welcome message
        self.show_welcome_message()

    def setup_styles(self):
        """Configure modern ttk styles"""
        style = ttk.Style()
        
        # Configure common styles
        style.configure('Modern.TFrame', background=COLORS['white'])
        style.configure('Modern.TLabel', 
                       background=COLORS['white'], 
                       foreground=COLORS['text'],
                       font=("Segoe UI", 9))
        style.configure('Modern.TButton',
                       background=COLORS['accent'],
                       foreground=COLORS['text'],
                       font=("Segoe UI", 9),
                       relief="flat",
                       borderwidth=0)
        style.configure('Modern.TLabelframe',
                       background=COLORS['white'],
                       foreground=COLORS['text'],
                       font=("Segoe UI", 10, "bold"))
        style.configure('Modern.TLabelframe.Label',
                       background=COLORS['white'],
                       foreground=COLORS['text'],
                       font=("Segoe UI", 10, "bold"))

    def create_layout(self):
        """Create the main application layout"""
        # Main container
        self.main_container = ModernFrame(self)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Configure grid weights
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(1, weight=3)
        self.main_container.grid_columnconfigure(2, weight=2)

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

    def setup_action_library(self):
        """Initialize the action library panel"""
        # Create frame
        self.action_lib_frame = ttk.LabelFrame(
            self.main_container, 
            text="Action Library", 
            padding="15",
            style='Modern.TLabelframe'
        )
        self.action_lib_frame.grid(row=0, column=0, padx=(0, 10), pady=(0, 10), sticky="nsew")
        self.action_lib_frame.rowconfigure(1, weight=1)
        self.action_lib_frame.columnconfigure(0, weight=1)

        # Help text
        help_text = "Select an action from the list below, then click 'Add Action' to add it to your test sequence."
        help_label = ttk.Label(
            self.action_lib_frame, 
            text=help_text, 
            foreground=COLORS['text_light'], 
            wraplength=250,
            style='Modern.TLabel'
        )
        help_label.grid(row=0, column=0, pady=(0, 10), sticky="ew")

        # Action listbox
        self.action_listbox = ModernListbox(self.action_lib_frame, height=20)
        self.action_listbox.grid(row=1, column=0, sticky="nsew", padx=(0, 5))
        self.action_listbox.bind("<Enter>", lambda e: self.status_var.set("Hover over an action to see its description"))
        self.action_listbox.bind("<Leave>", lambda e: self.status_var.set("Ready"))
        self.action_listbox.bind("<Motion>", self.on_action_hover)

        # Scrollbar
        action_scrollbar = ttk.Scrollbar(self.action_lib_frame, orient="vertical", command=self.action_listbox.yview)
        action_scrollbar.grid(row=1, column=1, sticky="ns")
        self.action_listbox.configure(yscrollcommand=action_scrollbar.set)

        # Add button
        add_button = ModernButton(
            self.action_lib_frame, 
            text="➕ Add Action", 
            command=self.add_action_to_sequence
        )
        add_button.grid(row=2, column=0, columnspan=2, pady=(10, 0), sticky="ew")

        # Populate actions
        self.populate_action_list()

    def setup_test_sequence(self):
        """Initialize the test sequence panel"""
        # Create frame
        self.sequence_frame = ttk.LabelFrame(
            self.main_container, 
            text="Test Case Sequence", 
            padding="15",
            style='Modern.TLabelframe'
        )
        self.sequence_frame.grid(row=0, column=1, padx=5, pady=(0, 10), sticky="nsew")
        self.sequence_frame.rowconfigure(1, weight=1)
        self.sequence_frame.columnconfigure(0, weight=1)

        # Help text
        help_text = "Your test steps will appear here. Select a step to configure its parameters on the right."
        help_label = ttk.Label(
            self.sequence_frame, 
            text=help_text, 
            foreground=COLORS['text_light'], 
            wraplength=350,
            style='Modern.TLabel'
        )
        help_label.grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky="ew")

        # Sequence listbox
        self.sequence_listbox = ModernListbox(self.sequence_frame, height=20)
        self.sequence_listbox.grid(row=1, column=0, sticky="nsew", padx=(0, 5))
        self.sequence_listbox.bind("<<ListboxSelect>>", self.on_sequence_select)

        # Scrollbar
        sequence_scrollbar = ttk.Scrollbar(self.sequence_frame, orient="vertical", command=self.sequence_listbox.yview)
        sequence_scrollbar.grid(row=1, column=1, sticky="ns")
        self.sequence_listbox.configure(yscrollcommand=sequence_scrollbar.set)

        # Button frame
        button_frame = ModernFrame(self.sequence_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(10, 0), sticky="ew")
        button_frame.configure(bg=COLORS['white'])

        # Control buttons
        move_up_btn = ModernButton(button_frame, text="⬆️ Move Up", command=self.move_step_up)
        move_up_btn.pack(side="left", padx=(0, 5))

        move_down_btn = ModernButton(button_frame, text="⬇️ Move Down", command=self.move_step_down)
        move_down_btn.pack(side="left", padx=(0, 5))

        remove_btn = ModernButton(button_frame, text="🗑️ Remove", command=self.remove_step)
        remove_btn.pack(side="left", padx=(0, 5))

        clear_btn = ModernButton(button_frame, text="🗑️ Clear All", command=self.clear_sequence)
        clear_btn.pack(side="left")

    def setup_parameter_editor(self):
        """Initialize the parameter editor panel"""
        # Create frame
        self.param_frame = ttk.LabelFrame(
            self.main_container, 
            text="Step Parameters", 
            padding="15",
            style='Modern.TLabelframe'
        )
        self.param_frame.grid(row=0, column=2, padx=(10, 0), pady=(0, 10), sticky="nsew")
        self.param_frame.rowconfigure(1, weight=1)
        self.param_frame.columnconfigure(0, weight=1)

        # Help text
        help_text = "Configure parameters for the selected step. Hover over fields for help."
        help_label = ttk.Label(
            self.param_frame, 
            text=help_text, 
            foreground=COLORS['text_light'], 
            wraplength=250,
            style='Modern.TLabel'
        )
        help_label.grid(row=0, column=0, pady=(0, 10), sticky="ew")

        # Canvas for scrolling
        self.param_canvas = tk.Canvas(
            self.param_frame, 
            bg=COLORS['white'],
            highlightthickness=0
        )
        self.param_canvas.grid(row=1, column=0, sticky="nsew", padx=(0, 5))

        # Scrollbar
        param_scrollbar = ttk.Scrollbar(self.param_frame, orient="vertical", command=self.param_canvas.yview)
        param_scrollbar.grid(row=1, column=1, sticky="ns")
        self.param_canvas.configure(yscrollcommand=param_scrollbar.set)

        # Inner frame for parameters
        self.param_inner_frame = ModernFrame(self.param_canvas)
        self.param_canvas.create_window((0, 0), window=self.param_inner_frame, anchor="nw")

        # Configure canvas scrolling
        self.param_inner_frame.bind(
            "<Configure>", 
            lambda e: self.param_canvas.configure(scrollregion=self.param_canvas.bbox("all"))
        )

    def setup_controls(self):
        """Initialize the control buttons and status bar"""
        # Control frame
        self.controls_frame = ModernFrame(self.main_container)
        self.controls_frame.grid(row=1, column=0, columnspan=3, pady=(10, 0), sticky="ew")
        self.controls_frame.configure(bg=COLORS['white'])

        # Left side buttons
        left_buttons = ModernFrame(self.controls_frame)
        left_buttons.pack(side="left", fill="x", expand=True)
        left_buttons.configure(bg=COLORS['white'])

        self.help_button = ModernButton(left_buttons, text="❓ Help", command=self.show_help_dialog)
        self.help_button.pack(side="left", padx=(0, 10))

        save_btn = ModernButton(left_buttons, text="💾 Save Test", command=self.save_test_case)
        save_btn.pack(side="left", padx=(0, 10))

        load_btn = ModernButton(left_buttons, text="📂 Load Test", command=self.load_test_case)
        load_btn.pack(side="left", padx=(0, 10))

        run_btn = ModernButton(left_buttons, text="▶️ Run Test", command=self.run_test)
        run_btn.pack(side="left", padx=(0, 10))

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(
            self.controls_frame, 
            textvariable=self.status_var, 
            foreground=COLORS['text_light'],
            style='Modern.TLabel'
        )
        status_label.pack(side="right", padx=(10, 0))

    def populate_action_list(self):
        """Populate the action listbox with available actions"""
        for action in self.available_actions:
            self.action_listbox.insert(tk.END, action['display_name'])

    def add_action_to_sequence(self):
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
        """Refreshes the sequence listbox from the internal data"""
        self.sequence_listbox.delete(0, tk.END)
        for i, step in enumerate(self.current_test_sequence):
            display_text = f"{i+1}. {step.get('_display_name', step['action'])}"
            self.sequence_listbox.insert(tk.END, display_text)

    def on_sequence_select(self, event):
        """Called when an item in the sequence listbox is selected"""
        selected_indices = self.sequence_listbox.curselection()
        if not selected_indices:
            self.clear_param_editor()
            return

        step_index = selected_indices[0]
        if step_index >= len(self.current_test_sequence):
            print("Warning: Selected index out of bounds.")
            self.clear_param_editor()
            return

        step_data = self.current_test_sequence[step_index]
        action_id = step_data['action']

        action_def = next((a for a in self.available_actions if a['action_id'] == action_id), None)
        self.display_parameter_editor(step_index, step_data, action_def)

    def display_parameter_editor(self, step_index, step_data, action_def):
        """Dynamically creates widgets to edit parameters for the selected step"""
        self.clear_param_editor()

        if not action_def:
            ttk.Label(
                self.param_inner_frame, 
                text=f"Action definition not found for '{step_data.get('action', 'N/A')}'",
                style='Modern.TLabel'
            ).pack()
            return
            
        if not action_def.get('params'):
            ttk.Label(
                self.param_inner_frame, 
                text="No parameters for this action.",
                style='Modern.TLabel'
            ).pack()
            return

        self.param_widgets = {}

        for param_def in action_def['params']:
            param_name = param_def['name']
            label_text = param_def.get('label', param_name) + (":" if param_def.get('required') else " (Optional):")
            current_value = step_data['params'].get(param_name, param_def.get('default', ''))
            param_desc = param_def.get('description')

            # Parameter frame
            frame = ModernFrame(self.param_inner_frame)
            frame.pack(fill=tk.X, pady=8, padx=10)
            frame.configure(bg=COLORS['white'])

            # Label
            lbl = ttk.Label(frame, text=label_text, width=20, anchor=tk.W, style='Modern.TLabel')
            lbl.pack(side=tk.LEFT, padx=5)

            param_type = param_def.get('type', 'string')
            widget = None
            var = None

            is_package_param = (action_def.get('action_id') == 'launch_app_by_package' and param_name == 'package_name')

            if is_package_param:
                var = tk.StringVar(value=current_value)
                package_list = get_installed_packages()

                try:
                    widget = ttk.Combobox(
                        frame, 
                        textvariable=var, 
                        values=package_list, 
                        state="normal" if package_list else "disabled", 
                        width=35
                    )
                    self.param_widgets[param_name] = {'widget': widget, 'var': var, 'type': 'package_choice'}
                except Exception as e:
                    print(f"ERROR: Failed to create/update Combobox: {e}")
                    var = tk.StringVar(value="Error loading packages!")
                    widget = ttk.Entry(frame, textvariable=var, state="readonly", width=35)
                    self.param_widgets[param_name] = {'widget': widget, 'var': var, 'type': 'string'}

                if not package_list:
                    warning_lbl = ttk.Label(frame, text=" (No packages found)", foreground="orange")
                    warning_lbl.pack(side=tk.LEFT, padx=2)

            elif param_type == "string":
                var = tk.StringVar(value=current_value)
                widget = ModernEntry(frame, width=35)
                widget.configure(textvariable=var)
                self.param_widgets[param_name] = {'widget': widget, 'var': var, 'type': 'string'}
                
            elif param_type == "integer":
                try:
                    int_val = int(current_value)
                except (ValueError, TypeError):
                    int_val = param_def.get('default', 0)
                var = tk.IntVar(value=int_val)
                widget = ttk.Spinbox(frame, from_=0, to=9999, textvariable=var, width=8)
                self.param_widgets[param_name] = {'widget': widget, 'var': var, 'type': 'integer'}
                
            elif param_type == "float":
                try:
                    float_val = float(current_value)
                except (ValueError, TypeError):
                    float_val = param_def.get('default', 0.0)
                var = tk.DoubleVar(value=float_val)
                widget = ttk.Spinbox(frame, from_=0.0, to=999.0, increment=0.1, textvariable=var, width=8)
                self.param_widgets[param_name] = {'widget': widget, 'var': var, 'type': 'float'}
                
            elif param_type == "boolean":
                bool_val = str(current_value).lower() in ['true', '1', 'yes', 'on']
                var = tk.BooleanVar(value=bool_val)
                widget = ttk.Checkbutton(frame, variable=var, onvalue=True, offvalue=False)
                self.param_widgets[param_name] = {'widget': widget, 'var': var, 'type': 'boolean'}
                
            elif param_type == "choice":
                options = param_def.get('options', [])
                var = tk.StringVar(value=current_value)
                widget = ttk.Combobox(frame, textvariable=var, values=options, state="readonly", width=33)
                self.param_widgets[param_name] = {'widget': widget, 'var': var, 'type': 'choice'}
                
            elif param_type == "filepath":
                var = tk.StringVar(value=current_value)
                entry_widget = ModernEntry(frame, width=25)
                entry_widget.configure(textvariable=var)
                browse_button = ModernButton(frame, text="Browse", command=lambda v=var: self.browse_file(v))
                entry_widget.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
                browse_button.pack(side=tk.LEFT, padx=2)
                self.param_widgets[param_name] = {'widget': entry_widget, 'var': var, 'type': 'filepath'}
                widget = entry_widget

            if widget:
                widget.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
                
                if param_desc:
                    help_frame = ModernFrame(frame)
                    help_frame.pack(side=tk.RIGHT, padx=2)
                    help_frame.configure(bg=COLORS['white'])
                    
                    help_icon = ttk.Label(help_frame, text="❓", foreground=COLORS['accent'], cursor="hand2")
                    help_icon.pack()
                    
                    def enter(event, text=param_desc):
                        formatted_text = text.replace(". ", ".\n• ").replace(" (", "\n• (")
                        self.status_var.set(f"{formatted_text}")
                    def leave(event):
                        self.status_var.set("Ready")
                    
                    widget.bind("<Enter>", enter)
                    widget.bind("<Leave>", leave)
                    help_icon.bind("<Enter>", enter)
                    help_icon.bind("<Leave>", leave)

                if var:
                    callback = lambda name, index, mode, sv=var, s_idx=step_index, p_name=param_name: self.update_step_param(s_idx, p_name, sv)
                    var.trace_add("write", callback)

        self.param_inner_frame.update_idletasks()
        self.param_canvas.config(scrollregion=self.param_canvas.bbox("all"))

    def update_step_param(self, step_index, param_name, tk_var):
        """Callback to update the internal sequence data when a param widget changes"""
        if step_index < len(self.current_test_sequence):
            try:
                new_value = tk_var.get()

                widget_info = self.param_widgets.get(param_name)
                target_type = widget_info.get('type') if widget_info else None

                if target_type == 'integer':
                    new_value = int(new_value)
                elif target_type == 'float':
                    new_value = float(new_value)
                elif target_type == 'boolean':
                    new_value = bool(new_value)

                self.current_test_sequence[step_index]['params'][param_name] = new_value

            except ValueError:
                print(f"Warning: Invalid input format for parameter {param_name}. Could not convert '{tk_var.get()}'.")
            except Exception as e:
                print(f"Error updating param via trace: {e}")

    def clear_param_editor(self):
        """Removes all widgets from the parameter editor frame"""
        for widget in self.param_inner_frame.winfo_children():
            widget.destroy()
        self.param_widgets = {}

    def move_step_up(self):
        """Moves the selected step one position up"""
        selected_indices = self.sequence_listbox.curselection()
        if not selected_indices or selected_indices[0] == 0:
            return
        idx = selected_indices[0]
        self.current_test_sequence[idx], self.current_test_sequence[idx-1] = \
            self.current_test_sequence[idx-1], self.current_test_sequence[idx]
        self.update_sequence_listbox()
        self.sequence_listbox.selection_set(idx - 1)
        self.sequence_listbox.activate(idx - 1)
        self.on_sequence_select(None)

    def move_step_down(self):
        """Moves the selected step one position down"""
        selected_indices = self.sequence_listbox.curselection()
        last_index = len(self.current_test_sequence) - 1
        if not selected_indices or selected_indices[0] == last_index:
            return
        idx = selected_indices[0]
        self.current_test_sequence[idx], self.current_test_sequence[idx+1] = \
            self.current_test_sequence[idx+1], self.current_test_sequence[idx]
        self.update_sequence_listbox()
        self.sequence_listbox.selection_set(idx + 1)
        self.sequence_listbox.activate(idx + 1)
        self.on_sequence_select(None)

    def remove_step(self):
        """Removes the selected step from the sequence"""
        selected_indices = self.sequence_listbox.curselection()
        if not selected_indices:
            return
        step_index = selected_indices[0]
        try:
            del self.current_test_sequence[step_index]
            self.update_sequence_listbox()
            if self.current_test_sequence:
                select_idx = min(step_index, len(self.current_test_sequence) - 1)
                self.sequence_listbox.selection_set(select_idx)
                self.on_sequence_select(None)
            else:
                self.clear_param_editor()
        except IndexError:
            print("Error: Index out of range during remove.")

    def clear_sequence(self):
        """Clear the entire test sequence"""
        if messagebox.askyesno("Confirm", "Clear the entire test sequence? This cannot be undone."):
            self.current_test_sequence = []
            self.update_sequence_listbox()
            self.clear_param_editor()

    def save_test_case(self):
        """Save the current test case to a file"""
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
            self.status_var.set(f"Saved test case to {os.path.basename(filepath)}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save test case:\n{e}")

    def load_test_case(self):
        """Load a test case from a file"""
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

            self.status_var.set(f"Loaded test case {os.path.basename(filepath)}")

        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load test case:\n{e}")

    def run_test(self):
        """Run the current test case"""
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

        self.status_var.set(f"Running test '{test_data['name']}'...")

        from runner.test_runner import run_test_case

        test_thread = threading.Thread(
            target=self.execute_test_and_update_gui,
            args=(test_data, run_test_case),
            daemon=True
        )
        test_thread.start()

    def browse_file(self, var):
        """Open file dialog to select a file path"""
        filepath = filedialog.askopenfilename(
            title="Select File",
            filetypes=[("All files", "*.*"), ("APK files", "*.apk"), ("Text files", "*.txt")]
        )
        if filepath:
            var.set(filepath)

    def force_update_params_from_widgets(self, step_index):
        """Force update parameters from widget values"""
        if step_index < len(self.current_test_sequence):
            for param_name, widget_info in self.param_widgets.items():
                var = widget_info.get('var')
                if var:
                    try:
                        new_value = var.get()
                        target_type = widget_info.get('type')
                        if target_type == 'integer':
                            new_value = int(new_value)
                        elif target_type == 'float':
                            new_value = float(new_value)
                        elif target_type == 'boolean':
                            new_value = bool(new_value)
                        self.current_test_sequence[step_index]['params'][param_name] = new_value
                    except (ValueError, tk.TclError) as e:
                        print(f"Warning: Error updating param {param_name}: {e}")
                    except Exception as e:
                        print(f"Warning: Unexpected error updating param {param_name}: {e}")

    def execute_test_and_update_gui(self, test_data_to_run, runner_func):
        """Execute test in background thread and update GUI"""
        test_name = test_data_to_run.get("name", "Unnamed")
        start_time = time.time()
        final_status_text = f"Finished: {test_name} - Unknown"
        results_log = []
        
        try:
            success, results_log = runner_func(test_data_to_run)
            result_status = "Success" if success else "Failed"
            duration = time.time() - start_time
            final_status_text = f"Finished: {test_name} - {result_status} ({duration:.2f}s)"
            
            for entry in results_log:
                print(f"  Step {entry.get('step', '?')}: [{entry.get('action', 'N/A')}] - {entry.get('status', 'Unknown')} - {entry.get('message', '')}")

        except Exception as e:
            duration = time.time() - start_time
            print(f"Error in test thread: {e}")
            final_status_text = f"Error during test run: {test_name} ({duration:.2f}s)"
            self.after(0, lambda: messagebox.showerror("Test Execution Error", f"An error occurred:\n{e}"))
            
        finally:
            self.after(0, self.status_var.set, final_status_text)

    def show_help_dialog(self):
        """Show comprehensive help dialog"""
        help_window = tk.Toplevel(self)
        help_window.title("Android GUI Tester - Help")
        help_window.geometry("800x600")
        help_window.resizable(True, True)
        help_window.configure(bg=COLORS['primary'])
        
        notebook = ttk.Notebook(help_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Getting Started Tab
        getting_started_frame = ttk.Frame(notebook)
        notebook.add(getting_started_frame, text="Getting Started")
        
        getting_started_text = """
Getting Started with Android GUI Tester

1. SETUP YOUR DEVICE:
   • Connect your Android device via USB
   • Enable USB Debugging in Developer Options
   • Install Android SDK platform-tools (for ADB)
   • Start Appium Server (default: http://localhost:4723)

2. CONFIGURE YOUR DEVICE:
   • Edit config/capabilities.json
   • Set your device ID (find with 'adb devices')
   • Set your app package name (optional)

3. CREATE YOUR FIRST TEST:
   • Select actions from the left panel
   • Configure parameters for each step
   • Save your test case
   • Run the test!

TIP: Start with simple actions like "Click Element" and "Input Text"
        """
        
        text_widget = tk.Text(getting_started_frame, wrap=tk.WORD, padx=10, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert(tk.END, getting_started_text)
        text_widget.config(state=tk.DISABLED)
        
        # Selectors Tab
        selectors_frame = ttk.Frame(notebook)
        notebook.add(selectors_frame, text="Element Selectors")
        
        selectors_text = """
Understanding Element Selectors

Element selectors help you find UI elements on the screen. Choose the best one for your needs:

ACCESSIBILITY_ID (Recommended):
   • Best for accessibility and reliability
   • Use content descriptions or hint text
   • Example: "Login Button" or "Username field"

ID (Resource ID):
   • Use Android resource IDs
   • Find in Android Studio or app inspection tools
   • Example: "com.example.app:id/login_button"

TEXT:
   • Use exact text shown on screen
   • Most intuitive but can break if text changes
   • Example: "Login" or "Submit"

XPATH:
   • Advanced XML path expressions
   • Most flexible but complex
   • Example: "//android.widget.Button[@text='Login']"

CLASS_NAME:
   • Use element type names
   • Less specific, use with other selectors
   • Example: "android.widget.Button"

UIAUTOMATOR:
   • Android UI Automator expressions
   • Advanced Android-specific selectors
   • Example: "new UiSelector().text(\"Login\")"

TIP: Use Android Studio's Layout Inspector or Appium Inspector to find selectors!
        """
        
        text_widget2 = tk.Text(selectors_frame, wrap=tk.WORD, padx=10, pady=10)
        text_widget2.pack(fill=tk.BOTH, expand=True)
        text_widget2.insert(tk.END, selectors_text)
        text_widget2.config(state=tk.DISABLED)
        
        # Common Actions Tab
        actions_frame = ttk.Frame(notebook)
        notebook.add(actions_frame, text="Common Actions")
        
        actions_text = """
Most Common Test Actions

CLICK ELEMENT:
   • Clicks buttons, links, menu items
   • Most common action for navigation
   • Use TEXT selector for visible buttons

INPUT TEXT:
   • Types text into input fields
   • Use for usernames, passwords, search terms
   • Clear first option removes existing text

WAIT FOR ELEMENT:
   • Waits for elements to appear
   • Essential for dynamic content
   • Use before clicking elements that load slowly

SWIPE SCREEN:
   • Scrolls up/down/left/right
   • Use for navigation in lists or pages
   • Percent controls how far to swipe

TAKE SCREENSHOT:
   • Captures current screen
   • Useful for debugging and documentation
   • Saves to reports/ folder

LAUNCH APP:
   • Starts or switches to an app
   • Use package name (e.g., com.example.app)
   • Dropdown shows installed apps

TIP: Build tests step by step, testing each action before adding the next!
        """
        
        text_widget3 = tk.Text(actions_frame, wrap=tk.WORD, padx=10, pady=10)
        text_widget3.pack(fill=tk.BOTH, expand=True)
        text_widget3.insert(tk.END, actions_text)
        text_widget3.config(state=tk.DISABLED)
        
        # Troubleshooting Tab
        troubleshooting_frame = ttk.Frame(notebook)
        notebook.add(troubleshooting_frame, text="Troubleshooting")
        
        troubleshooting_text = """
Common Issues and Solutions

"Element not found" Error:
   • Check if selector value is correct
   • Try different selector types (TEXT vs ID)
   • Increase timeout value
   • Use "Wait for Element" before clicking

"Driver initialization failed":
   • Check if device is connected (adb devices)
   • Verify Appium server is running
   • Check capabilities.json configuration
   • Ensure USB debugging is enabled

"Package not found":
   • Verify app is installed on device
   • Check package name spelling
   • Use dropdown to see available packages

"Test fails randomly":
   • Add wait steps between actions
   • Use "Wait for Element" instead of immediate clicks
   • Increase timeout values
   • Check if app UI changes between runs

TIP: Use screenshots to debug what the app looks like when tests fail!

USEFUL COMMANDS:
   • adb devices - List connected devices
   • adb shell pm list packages - List installed apps
   • adb logcat - View device logs
        """
        
        text_widget4 = tk.Text(troubleshooting_frame, wrap=tk.WORD, padx=10, pady=10)
        text_widget4.pack(fill=tk.BOTH, expand=True)
        text_widget4.insert(tk.END, troubleshooting_text)
        text_widget4.config(state=tk.DISABLED)

    def show_welcome_message(self):
        """Show welcome message for new users"""
        welcome_text = """Welcome to Android GUI Tester!

This tool helps you create and run automated tests on Android devices.

Quick Start:
1. Select an action from the left panel
2. Click 'Add Action' to add it to your test sequence
3. Select a step and configure its parameters on the right
4. Click 'Run Test' to execute your test case

Click the "Help" button for detailed guidance.
Hover over actions and parameters for helpful hints.

Ready to start testing?"""
        
        self.status_var.set(welcome_text)
        self.after(8000, lambda: self.status_var.set("Ready"))

    def on_action_hover(self, event):
        """Show action description when hovering over action listbox"""
        try:
            index = self.action_listbox.nearest(event.y)
            if 0 <= index < len(self.available_actions):
                action = self.available_actions[index]
                description = action.get('description', 'No description available')
                self.status_var.set(f"{action['display_name']}: {description}")
        except:
            pass
