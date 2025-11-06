#!/usr/bin/env python3
"""
W4GNS General Logger
Amateur Radio Contact Logging and DX Cluster Integration
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database import Database
from src.config import Config
from src.theme import ThemeManager
from src.gui.logging_tab_enhanced import EnhancedLoggingTab
from src.gui.contacts_tab import ContactsTab
from src.gui.dx_cluster_tab import DXClusterTab
from src.gui.awards_tab import AwardsTab
from src.gui.skcc_awards_tab import SKCCAwardsTab
from src.gui.space_weather_tab import SpaceWeatherTab
from src.gui.settings_tab import SettingsTab
from src.adif import export_contacts_to_adif, import_contacts_from_adif, validate_adif_file


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

        # Initialize theme manager
        self.theme_manager = ThemeManager(self.root, self.config)

        # Create UI
        self.create_menu()
        self.create_main_interface()

        # Apply saved theme
        saved_theme = self.config.get('theme', 'light')
        self.theme_manager.apply_theme(saved_theme)

        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Center window
        self.center_window()

        # Start auto-save timer if enabled
        if self.config.get('backup.auto_save', False):
            interval = self.config.get('backup.interval_minutes', 30) * 60 * 1000
            self.root.after(interval, self.auto_save_timer)

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
        file_menu.add_command(label="Export Log (ADIF)...", command=self.export_adif)
        file_menu.add_command(label="Import Log (ADIF)...", command=self.import_adif)
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
        self.logging_tab = EnhancedLoggingTab(self.notebook, self.database, self.config)
        self.contacts_tab = ContactsTab(self.notebook, self.database, self.config)
        self.dx_cluster_tab = DXClusterTab(self.notebook, self.database, self.config)
        self.awards_tab = AwardsTab(self.notebook, self.database, self.config)
        self.skcc_awards_tab = SKCCAwardsTab(self.notebook, self.database, self.config)
        self.space_weather_tab = SpaceWeatherTab(self.notebook, self.database, self.config)
        self.settings_tab = SettingsTab(self.notebook, self.config, self.theme_manager)

        # Wire DX cluster to logging tab for DX spot display
        self.dx_cluster_tab.set_logging_tab(self.logging_tab)

        # Add tabs to notebook
        self.notebook.add(self.logging_tab.get_frame(), text="  Log Contacts  ")
        self.notebook.add(self.contacts_tab.get_frame(), text="  Contacts  ")
        self.notebook.add(self.dx_cluster_tab.get_frame(), text="  DX Clusters  ")
        self.notebook.add(self.awards_tab.get_frame(), text="  ARRL Awards  ")
        self.notebook.add(self.skcc_awards_tab.get_frame(), text="  SKCC Awards  ")
        self.notebook.add(self.space_weather_tab.get_frame(), text="  Space Weather  ")
        self.notebook.add(self.settings_tab.get_frame(), text="  Settings  ")

        # Status bar
        self.status_bar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def export_adif(self):
        """Export contacts to ADIF format"""
        # Get all contacts from database
        contacts = self.database.get_all_contacts(limit=999999)

        if not contacts:
            messagebox.showwarning("No Contacts", "No contacts found to export.")
            return

        # Ask user for save location
        filename = filedialog.asksaveasfilename(
            defaultextension=".adi",
            filetypes=[
                ("ADIF files", "*.adi"),
                ("ADIF files", "*.adif"),
                ("All files", "*.*")
            ],
            title="Export Log to ADIF"
        )

        if not filename:
            return  # User cancelled

        try:
            # Export to ADIF
            export_contacts_to_adif(contacts, filename)
            messagebox.showinfo(
                "Export Successful",
                f"Successfully exported {len(contacts)} contacts to:\n{filename}"
            )
            self.status_bar.config(text=f"Exported {len(contacts)} contacts to ADIF")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Failed to export log:\n{str(e)}")

    def import_adif(self):
        """Import contacts from ADIF format"""
        # Ask user for file to import
        filename = filedialog.askopenfilename(
            filetypes=[
                ("ADIF files", "*.adi"),
                ("ADIF files", "*.adif"),
                ("All files", "*.*")
            ],
            title="Import Log from ADIF"
        )

        if not filename:
            return  # User cancelled

        try:
            # Validate ADIF file
            is_valid, message = validate_adif_file(filename)
            if not is_valid:
                messagebox.showerror("Invalid ADIF File", message)
                return

            # Import contacts
            contacts = import_contacts_from_adif(filename)

            if not contacts:
                messagebox.showwarning("No Contacts", "No contacts found in ADIF file.")
                return

            # Ask for confirmation
            response = messagebox.askyesno(
                "Confirm Import",
                f"Found {len(contacts)} contacts in file.\n\n"
                f"Import these contacts into your log?\n\n"
                f"Note: Duplicates within 10 minutes will be skipped."
            )

            if not response:
                return

            # Create progress dialog
            progress_window = tk.Toplevel(self.root)
            progress_window.title("Importing Contacts")
            progress_window.geometry("400x150")
            progress_window.transient(self.root)
            progress_window.grab_set()

            progress_frame = ttk.Frame(progress_window, padding=20)
            progress_frame.pack(fill='both', expand=True)

            progress_label = ttk.Label(progress_frame, text="Preparing import...", wraplength=350)
            progress_label.pack(pady=10)

            progress_bar = ttk.Progressbar(progress_frame, length=350, mode='determinate')
            progress_bar.pack(pady=10)

            progress_detail = ttk.Label(progress_frame, text="", font=('', 9))
            progress_detail.pack()

            # Progress callback for batch import
            def update_progress(current, total, message):
                progress_bar['maximum'] = total
                progress_bar['value'] = current
                progress_label.config(text=message)
                progress_detail.config(text=f"{current} / {total}")
                progress_window.update()

            # Use fast batch import method
            try:
                result = self.database.add_contacts_batch(
                    contacts,
                    skip_duplicates=True,
                    window_minutes=10,
                    progress_callback=update_progress
                )

                imported_count = result['imported']
                duplicate_count = result['duplicates']
                error_count = result['errors']
                error_details = result.get('error_details', [])

            except Exception as e:
                progress_window.destroy()
                raise e

            # Close progress window
            progress_window.destroy()

            # Refresh the contacts log display
            self.contacts_tab.refresh_log()

            # Refresh awards calculations
            self.awards_tab.refresh_awards()
            self.skcc_awards_tab.refresh_awards()

            # Show results
            result_message = f"Successfully imported {imported_count} contacts"
            if duplicate_count > 0:
                result_message += f"\nSkipped {duplicate_count} duplicates"
            if error_count > 0:
                result_message += f"\nFailed to import {error_count} contacts"
                if error_details:
                    result_message += f"\n\nFirst errors:\n" + "\n".join(error_details[:5])

            if error_count == 0:
                messagebox.showinfo("Import Successful", result_message)
            else:
                messagebox.showwarning("Import Completed with Errors", result_message)

            status_text = f"Imported {imported_count} contacts"
            if duplicate_count > 0:
                status_text += f", skipped {duplicate_count} duplicates"
            self.status_bar.config(text=status_text)

        except Exception as e:
            messagebox.showerror("Import Failed", f"Failed to import log:\n{str(e)}")

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

    def backup_on_shutdown(self):
        """Backup log to local and external locations on shutdown"""
        try:
            from datetime import datetime
            import os

            # Get all contacts
            contacts = self.database.get_all_contacts(limit=999999)

            if not contacts:
                return  # Nothing to backup

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"w4gns_log_{timestamp}.adi"

            # Always backup to local logs directory
            logs_dir = "logs"
            os.makedirs(logs_dir, exist_ok=True)
            local_path = os.path.join(logs_dir, filename)
            export_contacts_to_adif(contacts, local_path)
            print(f"Backed up {len(contacts)} contacts to {local_path}")

            # Backup to external path if configured
            external_path = self.config.get('backup.external_path', '').strip()
            if external_path and os.path.exists(external_path):
                external_file = os.path.join(external_path, filename)
                export_contacts_to_adif(contacts, external_file)
                print(f"Also backed up to {external_file}")

        except Exception as e:
            print(f"Error during shutdown backup: {e}")

    def auto_save_timer(self):
        """Periodic auto-save timer"""
        if self.config.get('backup.auto_save', False):
            external_path = self.config.get('backup.external_path', '').strip()

            if external_path and os.path.exists(external_path):
                try:
                    from datetime import datetime
                    import os

                    contacts = self.database.get_all_contacts(limit=999999)

                    if contacts:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"w4gns_log_autosave_{timestamp}.adi"
                        external_file = os.path.join(external_path, filename)
                        export_contacts_to_adif(contacts, external_file)
                        self.status_bar.config(text=f"Auto-saved {len(contacts)} contacts to external backup")
                        print(f"Auto-save: {len(contacts)} contacts to {external_file}")

                except Exception as e:
                    print(f"Error during auto-save: {e}")

        # Schedule next auto-save
        interval = self.config.get('backup.interval_minutes', 30) * 60 * 1000  # Convert to milliseconds
        self.root.after(interval, self.auto_save_timer)

    def on_closing(self):
        """Handle window closing"""
        # Disconnect from cluster if connected
        if hasattr(self.dx_cluster_tab, 'client') and self.dx_cluster_tab.client:
            self.dx_cluster_tab.disconnect()

        # Save window size
        self.config.set('window.width', self.root.winfo_width())
        self.config.set('window.height', self.root.winfo_height())

        # Auto-backup on shutdown if enabled
        if self.config.get('backup.auto_backup', True):
            self.backup_on_shutdown()

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
