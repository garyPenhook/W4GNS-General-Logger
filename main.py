#!/usr/bin/env python3
"""
W4GNS General Logger
Amateur Radio Contact Logging and DX Cluster Integration
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import sys
import os
import sqlite3

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
from src.gui.weather_tab import WeatherTab
from src.gui.settings_tab import SettingsTab
from src.gui.contest_tab import ContestTab
from src.gui.date_range_dialog import DateRangeDialog
from src.gui.monthly_brag_dialog import MonthlyBragDialog
from src.gui.help_dialog import HelpDialog
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

        # Download SKCC award rosters in background (for Tribune/Senator validation)
        self.download_skcc_rosters_background()

        # Auto-save disabled - backups only on shutdown
        # if self.config.get('backup.auto_save', False):
        #     interval = self.config.get('backup.interval_minutes', 30) * 60 * 1000
        #     self.root.after(interval, self.auto_save_timer)

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
        file_menu.add_command(label="Export by Date/Time Range (ADIF)...", command=self.export_adif_by_date_range)
        file_menu.add_command(label="Export SKCC Contacts (ADIF)...", command=self.export_skcc_adif)
        file_menu.add_command(label="Import Log (ADIF)...", command=self.import_adif)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)

        # Reports menu
        reports_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Reports", menu=reports_menu)
        reports_menu.add_command(label="SKCC Monthly Brag Report...", command=self.show_monthly_brag_report)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Help Topics", command=self.show_help)
        help_menu.add_separator()
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
        self.weather_tab = WeatherTab(self.notebook, self.config)
        self.space_weather_tab = SpaceWeatherTab(self.notebook, self.database, self.config)
        self.contest_tab = ContestTab(self.notebook, self.database, self.config)
        self.settings_tab = SettingsTab(self.notebook, self.config, self.theme_manager, self.database)

        # Wire DX cluster to logging tab for DX spot display
        self.dx_cluster_tab.set_logging_tab(self.logging_tab)

        # Wire contacts tab to logging tab for auto-refresh after logging
        self.logging_tab.set_contacts_tab(self.contacts_tab)

        # Add tabs to notebook
        self.notebook.add(self.logging_tab.get_frame(), text="  Log Contacts  ")
        self.notebook.add(self.contacts_tab.get_frame(), text="  Contacts  ")
        self.notebook.add(self.dx_cluster_tab.get_frame(), text="  DX Clusters  ")
        self.notebook.add(self.awards_tab.get_frame(), text="  ARRL Awards  ")
        self.notebook.add(self.skcc_awards_tab.get_frame(), text="  SKCC Awards  ")
        self.notebook.add(self.contest_tab.get_frame(), text="  Contest  ")
        self.notebook.add(self.weather_tab.get_frame(), text="  Weather  ")
        self.notebook.add(self.space_weather_tab.get_frame(), text="  Space Weather  ")
        self.notebook.add(self.settings_tab.get_frame(), text="  Settings  ")

        # Status bar
        self.status_bar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def export_adif(self):
        """Export contacts to ADIF format"""
        # Ask user for save location first
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

        # Create progress dialog
        progress_dialog = tk.Toplevel(self.root)
        progress_dialog.title("Exporting ADIF")
        progress_dialog.geometry("400x100")
        progress_dialog.transient(self.root)
        progress_dialog.grab_set()

        ttk.Label(progress_dialog, text="Exporting contacts to ADIF...").pack(pady=10)
        progress_label = ttk.Label(progress_dialog, text="Loading contacts...")
        progress_label.pack(pady=5)

        # Run export in background thread
        threading.Thread(
            target=self._export_adif_background,
            args=(filename, progress_dialog, progress_label),
            daemon=True
        ).start()

    def _export_adif_background(self, filename, progress_dialog, progress_label):
        """Background thread for ADIF export"""
        try:
            # Update progress (main loop is guaranteed to be running)
            self.root.after(0, lambda: progress_label.config(text="Loading contacts from database..."))

            # Get all contacts from database
            contacts = self.database.get_all_contacts(limit=999999)

            if not contacts:
                self.root.after(0, lambda: self._export_no_contacts(progress_dialog))
                return

            contacts_list = list(contacts)
            contact_count = len(contacts_list)

            # Update progress
            self.root.after(0, lambda: progress_label.config(text=f"Exporting {contact_count} contacts..."))

            # Export to ADIF
            export_contacts_to_adif(contacts_list, filename)

            # Schedule success message on main thread
            self.root.after(0, lambda: self._export_success(progress_dialog, contact_count, filename))

        except Exception as e:
            # Handle errors gracefully
            self.root.after(0, lambda: self._export_error(progress_dialog, str(e)))

    def _export_success(self, progress_dialog, count, filename):
        """Handle successful export (runs on main thread)"""
        progress_dialog.destroy()
        messagebox.showinfo(
            "Export Successful",
            f"Successfully exported {count} contacts to:\n{filename}"
        )
        self.status_bar.config(text=f"Exported {count} contacts to ADIF")

    def _export_no_contacts(self, progress_dialog):
        """Handle no contacts case (runs on main thread)"""
        progress_dialog.destroy()
        messagebox.showwarning("No Contacts", "No contacts found to export.")

    def _export_error(self, progress_dialog, error_msg):
        """Handle export errors (runs on main thread)"""
        progress_dialog.destroy()
        messagebox.showerror("Export Failed", f"Failed to export log:\n{error_msg}")

    def export_adif_by_date_range(self):
        """Export contacts to ADIF format filtered by date/time range"""
        # Show date range selection dialog
        dialog = DateRangeDialog(self.root)
        result = dialog.show()

        if not result:
            return  # User cancelled

        # Get contacts within the specified date/time range
        contacts = self.database.get_contacts_by_date_range(
            result['start_date'],
            result['end_date'],
            result['start_time'],
            result['end_time']
        )

        if not contacts:
            # Build a friendly date range string for the message
            start_str = result['start_date']
            if result['start_time']:
                start_str += f" {result['start_time']}"
            end_str = result['end_date']
            if result['end_time']:
                end_str += f" {result['end_time']}"

            messagebox.showwarning(
                "No Contacts",
                f"No contacts found in the specified date/time range:\n\n"
                f"From: {start_str}\n"
                f"To: {end_str}"
            )
            return

        # Build default filename with date range
        from datetime import datetime
        start_date_formatted = result['start_date'].replace('-', '')
        end_date_formatted = result['end_date'].replace('-', '')
        default_filename = f"contacts_{start_date_formatted}_{end_date_formatted}.adi"

        # Ask user for save location
        filename = filedialog.asksaveasfilename(
            defaultextension=".adi",
            initialfile=default_filename,
            filetypes=[
                ("ADIF files", "*.adi"),
                ("ADIF files", "*.adif"),
                ("All files", "*.*")
            ],
            title="Export Contacts by Date/Time Range to ADIF"
        )

        if not filename:
            return  # User cancelled

        try:
            # Export to ADIF
            export_contacts_to_adif(contacts, filename)

            # Build a friendly date range string for the message
            start_str = result['start_date']
            if result['start_time']:
                start_str += f" {result['start_time']}"
            end_str = result['end_date']
            if result['end_time']:
                end_str += f" {result['end_time']}"

            messagebox.showinfo(
                "Export Successful",
                f"Successfully exported {len(contacts)} contacts to:\n{filename}\n\n"
                f"Date/Time Range:\n"
                f"From: {start_str}\n"
                f"To: {end_str}"
            )
            self.status_bar.config(text=f"Exported {len(contacts)} contacts from date/time range to ADIF")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Failed to export log:\n{str(e)}")

    def export_skcc_adif(self):
        """Export SKCC contacts only to ADIF format"""
        # Get SKCC contacts from database (contacts with SKCC numbers)
        cursor = self.database.conn.cursor()
        cursor.execute('''
            SELECT
                callsign, date, time_on, time_off, frequency, band, mode,
                rst_sent, rst_rcvd, power, name, qth, gridsquare, county,
                state, country, continent, cq_zone, itu_zone, dxcc,
                my_gridsquare, comment, skcc_number, my_skcc_number,
                dxcc_entity
            FROM contacts
            WHERE skcc_number IS NOT NULL AND skcc_number != ''
            ORDER BY date, time_on
        ''')

        contacts = cursor.fetchall()

        if not contacts:
            messagebox.showwarning(
                "No SKCC Contacts",
                "No SKCC contacts found to export.\n\n"
                "Make sure your contacts have SKCC numbers populated.\n"
                "You may need to run:\n"
                "  • extract_skcc_from_comments.py\n"
                "  • set_default_key_type.py"
            )
            return

        # Ask user for save location
        from datetime import datetime, timezone
        default_filename = f"skcc_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.adi"

        filename = filedialog.asksaveasfilename(
            defaultextension=".adi",
            initialfile=default_filename,
            filetypes=[
                ("ADIF files", "*.adi"),
                ("ADIF files", "*.adif"),
                ("All files", "*.*")
            ],
            title="Export SKCC Contacts to ADIF"
        )

        if not filename:
            return  # User cancelled

        try:
            # Get user's callsign and SKCC number from config
            user_callsign = self.config.get('callsign', '')
            user_skcc = self.config.get('skcc_number', '')

            # Write ADIF file
            with open(filename, 'w', encoding='utf-8') as f:
                # Write header
                f.write("ADIF Log Created by W4GNS General Logger\n")
                f.write("SKCC Contacts Export\n")
                f.write("Version: 1.0.0\n\n")
                if user_callsign:
                    f.write(f"Callsign: {user_callsign}\n")
                if user_skcc:
                    f.write(f"SKCC Nr.: {user_skcc}\n")
                f.write(f"Log Created: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}Z\n")
                f.write(f"Record Count: {len(contacts)}\n")
                f.write(f"Log Filename: {filename}\n\n")
                f.write("<EOH>\n\n")

                # Column indices (matching the SELECT query)
                for contact in contacts:
                    fields = []

                    # Band
                    if contact[5]:  # band
                        band = contact[5].upper()
                        fields.append(f"<BAND:{len(band)}>{band}")

                    # Callsign
                    callsign = contact[0].upper()
                    fields.append(f"<CALL:{len(callsign)}>{callsign}")

                    # Comment
                    if contact[21]:  # comment
                        comment = contact[21]
                        fields.append(f"<COMMENT:{len(comment)}>{comment}")

                    # Country
                    if contact[15]:  # country
                        country = contact[15]
                        fields.append(f"<COUNTRY:{len(country)}>{country}")

                    # DXCC
                    if contact[19]:  # dxcc
                        dxcc = str(contact[19])
                        fields.append(f"<DXCC:{len(dxcc)}>{dxcc}")

                    # Frequency
                    if contact[4]:  # frequency
                        freq = contact[4]
                        fields.append(f"<FREQ:{len(freq)}>{freq}")

                    # Gridsquare
                    if contact[12]:  # gridsquare
                        grid = contact[12].upper()
                        fields.append(f"<GRIDSQUARE:{len(grid)}>{grid}")

                    # Mode
                    mode = contact[6].upper()
                    fields.append(f"<MODE:{len(mode)}>{mode}")

                    # My Gridsquare
                    if contact[20]:  # my_gridsquare
                        my_grid = contact[20].upper()
                        fields.append(f"<MY_GRIDSQUARE:{len(my_grid)}>{my_grid}")

                    # Name
                    if contact[10]:  # name
                        name = contact[10]
                        fields.append(f"<NAME:{len(name)}>{name}")

                    # Operator
                    if user_callsign:
                        fields.append(f"<OPERATOR:{len(user_callsign)}>{user_callsign}")

                    # QSO Date - format as YYYYMMDD
                    date = contact[1].replace('-', '')
                    fields.append(f"<QSO_DATE:{len(date)}>{date}")

                    # QTH
                    if contact[11]:  # qth
                        qth = contact[11]
                        fields.append(f"<QTH:{len(qth)}>{qth}")

                    # RST Received
                    if contact[8]:  # rst_rcvd
                        rst_rcvd = contact[8]
                        fields.append(f"<RST_RCVD:{len(rst_rcvd)}>{rst_rcvd}")

                    # RST Sent
                    if contact[7]:  # rst_sent
                        rst_sent = contact[7]
                        fields.append(f"<RST_SENT:{len(rst_sent)}>{rst_sent}")

                    # SKCC Number (CRITICAL for SKCC Logger)
                    skcc = contact[22]
                    fields.append(f"<SKCC:{len(skcc)}>{skcc}")

                    # State
                    if contact[14]:  # state
                        state = contact[14].upper()
                        fields.append(f"<STATE:{len(state)}>{state}")

                    # Station Callsign
                    if user_callsign:
                        fields.append(f"<STATION_CALLSIGN:{len(user_callsign)}>{user_callsign}")

                    # Time Off - format as HHMMSS
                    if contact[3]:  # time_off
                        time_off = contact[3].replace(':', '') + '00'
                        fields.append(f"<TIME_OFF:{len(time_off)}>{time_off}")

                    # Time On - format as HHMMSS
                    time_on = contact[2].replace(':', '') + '00'
                    fields.append(f"<TIME_ON:{len(time_on)}>{time_on}")

                    # TX Power
                    if contact[9]:  # power
                        power = str(contact[9])
                        fields.append(f"<TX_PWR:{len(power)}>{power}")

                    # End of record
                    fields.append("<EOR>")

                    # Write record
                    f.write('\n'.join(fields))
                    f.write('\n\n')

            messagebox.showinfo(
                "Export Successful",
                f"Successfully exported {len(contacts)} SKCC contacts to:\n{filename}\n\n"
                f"You can now import this file into SKCC Logger."
            )
            self.status_bar.config(text=f"Exported {len(contacts)} SKCC contacts to ADIF")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Failed to export SKCC contacts:\n{str(e)}")

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

    def show_monthly_brag_report(self):
        """Show SKCC Monthly Brag Report dialog"""
        MonthlyBragDialog(self.root, self.database, self.config)

    def show_help(self):
        """Show comprehensive help dialog"""
        HelpDialog(self.root)

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

    def cleanup_old_backups(self, directory, keep_count=5):
        """Keep only the most recent backup files, delete older ones"""
        try:
            import glob

            # Get all backup database files
            db_pattern = os.path.join(directory, "w4gns_log_*.db")
            db_files = sorted(glob.glob(db_pattern), key=os.path.getmtime, reverse=True)

            # Get all backup ADIF files
            adif_pattern = os.path.join(directory, "w4gns_log_*.adi")
            adif_files = sorted(glob.glob(adif_pattern), key=os.path.getmtime, reverse=True)

            # Delete old database backups (keep only most recent 5)
            if len(db_files) > keep_count:
                for old_file in db_files[keep_count:]:
                    os.remove(old_file)
                    print(f"Deleted old backup: {os.path.basename(old_file)}")

            # Delete old ADIF backups (keep only most recent 5)
            if len(adif_files) > keep_count:
                for old_file in adif_files[keep_count:]:
                    os.remove(old_file)
                    print(f"Deleted old backup: {os.path.basename(old_file)}")

        except Exception as e:
            print(f"Error cleaning up old backups: {e}")

    def backup_on_shutdown(self):
        """Backup log to local and external locations on shutdown"""
        try:
            from datetime import datetime
            import shutil

            # Check if database connection is still open
            if not self.database or not self.database.conn:
                print("Database connection is closed, skipping shutdown backup")
                return

            # Get all contacts
            contacts = self.database.get_all_contacts(limit=999999)

            if not contacts:
                return  # Nothing to backup

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            adif_filename = f"w4gns_log_{timestamp}.adi"
            db_filename = f"w4gns_log_{timestamp}.db"

            # Always backup to local logs directory
            logs_dir = "logs"
            os.makedirs(logs_dir, exist_ok=True)

            # Backup ADIF
            local_adif_path = os.path.join(logs_dir, adif_filename)
            export_contacts_to_adif(contacts, local_adif_path)
            print(f"Backed up {len(contacts)} contacts to {local_adif_path}")

            # Backup database using SQLite's backup API (prevents corruption)
            local_db_path = os.path.join(logs_dir, db_filename)
            if self.database and self.database.conn:
                backup_conn = sqlite3.connect(local_db_path)
                with backup_conn:
                    self.database.conn.backup(backup_conn)
                backup_conn.close()
                print(f"Backed up database to {local_db_path}")

            # Clean up old backups in local logs directory (keep last 5)
            self.cleanup_old_backups(logs_dir, keep_count=5)

            # Backup to external path if configured
            external_path = self.config.get('backup.external_path', '').strip()
            if external_path and os.path.exists(external_path):
                # Backup ADIF to external
                external_adif_file = os.path.join(external_path, adif_filename)
                export_contacts_to_adif(contacts, external_adif_file)
                print(f"Also backed up ADIF to {external_adif_file}")

                # Backup database to external using SQLite's backup API
                external_db_file = os.path.join(external_path, db_filename)
                if self.database and self.database.conn:
                    backup_conn = sqlite3.connect(external_db_file)
                    with backup_conn:
                        self.database.conn.backup(backup_conn)
                    backup_conn.close()
                    print(f"Also backed up database to {external_db_file}")

                # Clean up old backups in external directory (keep last 5)
                self.cleanup_old_backups(external_path, keep_count=5)

        except Exception as e:
            print(f"Error during shutdown backup: {e}")

    # AUTO-SAVE DISABLED - Backups only on shutdown
    # def auto_save_timer(self):
    #     """Periodic auto-save timer"""
    #     if self.config.get('backup.auto_save', False):
    #         external_path = self.config.get('backup.external_path', '').strip()
    #
    #         if external_path and os.path.exists(external_path):
    #             try:
    #                 from datetime import datetime
    #                 import shutil
    #
    #                 contacts = self.database.get_all_contacts(limit=999999)
    #
    #                 if contacts:
    #                     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    #                     adif_filename = f"w4gns_log_autosave_{timestamp}.adi"
    #                     db_filename = f"w4gns_log_autosave_{timestamp}.db"
    #
    #                     # Backup ADIF
    #                     external_adif_file = os.path.join(external_path, adif_filename)
    #                     export_contacts_to_adif(contacts, external_adif_file)
    #
    #                     # Backup database
    #                     external_db_file = os.path.join(external_path, db_filename)
    #                     if os.path.exists(self.database.db_path):
    #                         shutil.copy2(self.database.db_path, external_db_file)
    #                         self.status_bar.config(text=f"Auto-saved {len(contacts)} contacts + database to external backup")
    #                         print(f"Auto-save: {len(contacts)} contacts to {external_adif_file}")
    #                         print(f"Auto-save: database to {external_db_file}")
    #                     else:
    #                         self.status_bar.config(text=f"Auto-saved {len(contacts)} contacts to external backup")
    #                         print(f"Auto-save: {len(contacts)} contacts to {external_adif_file}")
    #
    #             except Exception as e:
    #                 print(f"Error during auto-save: {e}")
    #
    #     # Schedule next auto-save
    #     interval = self.config.get('backup.interval_minutes', 30) * 60 * 1000  # Convert to milliseconds
    #     self.root.after(interval, self.auto_save_timer)

    def download_skcc_rosters_background(self):
        """
        Download SKCC award rosters in background thread.

        These rosters are needed for Tribune and Senator award validation.
        They contain the dates when members achieved each award level.
        """
        import threading

        def download_rosters():
            try:
                from src.skcc_award_rosters import get_award_roster_manager

                roster_mgr = get_award_roster_manager(database=self.database)

                # Download all rosters fresh on every startup for precise validation
                results = roster_mgr.download_all_rosters(force=True)

                # Log results
                success_count = sum(1 for success in results.values() if success)
                if success_count > 0:
                    print(f"SKCC Rosters: Downloaded/loaded {success_count}/3 rosters")

                    # Show roster info
                    roster_info = roster_mgr.get_roster_info()
                    for award_type, info in roster_info.items():
                        if info['loaded']:
                            print(f"  {award_type.title()}: {info['count']} members (age: {info['age_days']} days)")
                else:
                    print("SKCC Rosters: Failed to download rosters (will use fallback validation)")

            except Exception as e:
                print(f"SKCC Rosters: Error downloading rosters: {e}")
                print("  Tribune/Senator validation will use fallback mode (T/S suffix)")

        # Start download in background thread
        thread = threading.Thread(target=download_rosters, daemon=True)
        thread.start()

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
