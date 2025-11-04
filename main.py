#!/usr/bin/env python3
"""
W4GNS General Logger
Amateur Radio Contact Logging and DX Cluster Integration
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database import Database
from src.config import Config
from src.gui.logging_tab import LoggingTab
from src.gui.dx_cluster_tab import DXClusterTab
from src.gui.settings_tab import SettingsTab


class W4GNSLogger:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("W4GNS General Logger")

        # Load configuration
        self.config = Config()

        # Set window size
        width = self.config.get('window.width', 1000)
        height = self.config.get('window.height', 700)
        self.root.geometry(f"{width}x{height}")

        # Initialize database
        self.database = Database()

        # Create UI
        self.create_menu()
        self.create_main_interface()

        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Center window
        self.center_window()

    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export Log (ADIF)...", command=self.export_adif, state='disabled')
        file_menu.add_command(label="Import Log (ADIF)...", command=self.import_adif, state='disabled')
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def create_main_interface(self):
        """Create the main tabbed interface"""
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)

        # Create tabs
        self.logging_tab = LoggingTab(self.notebook, self.database, self.config)
        self.dx_cluster_tab = DXClusterTab(self.notebook, self.database, self.config)
        self.settings_tab = SettingsTab(self.notebook, self.config)

        # Add tabs to notebook
        self.notebook.add(self.logging_tab.get_frame(), text="  Log Contacts  ")
        self.notebook.add(self.dx_cluster_tab.get_frame(), text="  DX Clusters  ")
        self.notebook.add(self.settings_tab.get_frame(), text="  Settings  ")

        # Status bar
        self.status_bar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def export_adif(self):
        """Export contacts to ADIF format"""
        # TODO: Implement ADIF export
        pass

    def import_adif(self):
        """Import contacts from ADIF format"""
        # TODO: Implement ADIF import
        pass

    def show_about(self):
        """Show about dialog"""
        about_text = """
W4GNS General Logger
Version 1.0.0

Amateur Radio Contact Logging
with DX Cluster Integration

Python 3.12+
Tkinter GUI

DX Cluster list from:
https://www.ng3k.com/Misc/cluster.html

© 2024
        """
        tk.messagebox.showinfo("About W4GNS Logger", about_text.strip())

    def on_closing(self):
        """Handle window closing"""
        # Disconnect from cluster if connected
        if hasattr(self.dx_cluster_tab, 'client') and self.dx_cluster_tab.client:
            self.dx_cluster_tab.disconnect()

        # Save window size
        self.config.set('window.width', self.root.winfo_width())
        self.config.set('window.height', self.root.winfo_height())

        # Close database
        self.database.close()

        # Destroy window
        self.root.destroy()

    def run(self):
        """Start the application"""
        self.root.mainloop()


def main():
    """Main entry point"""
    app = W4GNSLogger()
    app.run()


if __name__ == "__main__":
    main()
