# main.py
import sys
import os

# Setup project root for module imports
project_root = os.path.dirname(__file__)
sys.path.insert(0, project_root)

from gui.main_window import App

def launch_gui():
    """Initialize and run the main application window"""
    try:
        app = App()
        app.mainloop()
    except Exception as e:
        print(f"Error launching GUI: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    launch_gui()