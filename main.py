# main.py
import sys
import os

# Add project root to Python path to allow imports between modules
project_root = os.path.dirname(__file__)
sys.path.insert(0, project_root)

from gui.main_window import App # Import the main App class

def launch_gui():
    """Launches the main Tkinter GUI application."""
    print("Launching Android GUI Tester...")
    try:
        app = App()
        app.mainloop()
    except Exception as e:
        print(f"Error launching GUI: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    launch_gui()