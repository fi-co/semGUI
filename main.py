#!/usr/bin/env python3
#       ================   entry point for the application   ===================
#       Run this file to start the GUI

import tkinter as tk
from entry_window import EntryWindow
import logging


logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    
    try:
        entry_app = EntryWindow(root)
        root.mainloop()
    except Exception as e:
        logger.exception("Unexpected error")
        tk.messagebox.showerror("Error", f"Something went wrong:\n{e}")
    finally:
        root.destroy()