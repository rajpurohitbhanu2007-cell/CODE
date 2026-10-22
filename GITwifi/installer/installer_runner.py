import os
import sys
import tempfile
import subprocess
import tkinter as tk
from tkinter import messagebox

def install():
    root = tk.Tk()
    root.withdraw()

    resp = messagebox.askyesno(
        "GITwifi Setup",
        "Welcome to GITwifi Suite Setup!\n\n"
        "This installer will set up GITwifi on your computer, creating "
        "Desktop and Start Menu shortcuts.\n\n"
        "Do you want to continue?",
        icon="question"
    )
    if not resp:
        sys.exit(0)

    # Base path within PyInstaller extracted bundle
    base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    setup_bat = os.path.join(base_dir, "setup.bat")

    try:
        proc = subprocess.run(["cmd.exe", "/c", setup_bat], creationflags=subprocess.CREATE_NEW_CONSOLE, check=False)
    except Exception as e:
        messagebox.showerror("Installation Error", f"Failed to run installer: {e}")
        sys.exit(1)

if __name__ == "__main__":
    install()
