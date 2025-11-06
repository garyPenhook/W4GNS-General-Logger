"""
Settings Tab - Configuration and preferences
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from src.qrz import test_qrz_login


class SettingsTab:
    def __init__(self, parent, config, theme_manager=None):
        self.parent = parent
        self.config = config
        self.theme_manager = theme_manager
        self.frame = ttk.Frame(parent)
        self.create_widgets()

    def create_widgets(self):
        """Create the settings interface"""

        # Create a canvas with scrollbar for the settings content
        canvas = tk.Canvas(self.frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Pack the canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Enable mousewheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Station Information
        station_frame = ttk.LabelFrame(scrollable_frame, text="Station Information", padding=10)
        station_frame.pack(fill='x', padx=10, pady=5)

        row1 = ttk.Frame(station_frame)
        row1.pack(fill='x', pady=5)
        ttk.Label(row1, text="Your Callsign:").pack(side='left')
        self.callsign_var = tk.StringVar(value=self.config.get('callsign', ''))
        ttk.Entry(row1, textvariable=self.callsign_var, width=15).pack(side='left', padx=5)

        row2 = ttk.Frame(station_frame)
        row2.pack(fill='x', pady=5)
        ttk.Label(row2, text="Grid Square:").pack(side='left')
        self.grid_var = tk.StringVar(value=self.config.get('gridsquare', ''))
        ttk.Entry(row2, textvariable=self.grid_var, width=10).pack(side='left', padx=5)

        row3 = ttk.Frame(station_frame)
        row3.pack(fill='x', pady=5)
        ttk.Label(row3, text="Default RST:").pack(side='left')
        self.rst_var = tk.StringVar(value=self.config.get('default_rst', '59'))
        ttk.Entry(row3, textvariable=self.rst_var, width=8).pack(side='left', padx=5)

        ttk.Label(row3, text="Default Power (W):").pack(side='left', padx=(20, 0))
        self.power_var = tk.StringVar(value=self.config.get('default_power', '100'))
        ttk.Entry(row3, textvariable=self.power_var, width=8).pack(side='left', padx=5)

        # Appearance Settings
        appearance_frame = ttk.LabelFrame(scrollable_frame, text="Appearance", padding=10)
        appearance_frame.pack(fill='x', padx=10, pady=5)

        theme_row = ttk.Frame(appearance_frame)
        theme_row.pack(fill='x', pady=5)

        ttk.Label(theme_row, text="Color Theme:").pack(side='left')

        current_theme = self.config.get('theme', 'light')
        theme_text = "Dark Mode" if current_theme == 'light' else "Light Mode"

        self.theme_button = ttk.Button(theme_row, text=f"Switch to {theme_text}",
                                      command=self.toggle_theme)
        self.theme_button.pack(side='left', padx=10)

        # Show current theme
        self.current_theme_label = ttk.Label(theme_row,
                                            text=f"(Currently: {current_theme.capitalize()})",
                                            foreground="blue")
        self.current_theme_label.pack(side='left', padx=5)

        # QRZ.com Integration
        qrz_frame = ttk.LabelFrame(scrollable_frame, text="QRZ.com Integration", padding=10)
        qrz_frame.pack(fill='x', padx=10, pady=5)

        qrz_row1 = ttk.Frame(qrz_frame)
        qrz_row1.pack(fill='x', pady=5)
        ttk.Label(qrz_row1, text="QRZ Username:").pack(side='left')
        self.qrz_username_var = tk.StringVar(value=self.config.get('qrz.username', ''))
        ttk.Entry(qrz_row1, textvariable=self.qrz_username_var, width=20).pack(side='left', padx=5)

        qrz_row2 = ttk.Frame(qrz_frame)
        qrz_row2.pack(fill='x', pady=5)
        ttk.Label(qrz_row2, text="QRZ Password:").pack(side='left')
        self.qrz_password_var = tk.StringVar(value=self.config.get('qrz.password', ''))
        self.qrz_password_entry = ttk.Entry(qrz_row2, textvariable=self.qrz_password_var, width=20, show='*')
        self.qrz_password_entry.pack(side='left', padx=5)

        # Show/hide password button
        self.password_visible = False
        self.toggle_password_btn = ttk.Button(qrz_row2, text="👁", width=3, command=self.toggle_password_visibility)
        self.toggle_password_btn.pack(side='left', padx=2)

        qrz_row3 = ttk.Frame(qrz_frame)
        qrz_row3.pack(fill='x', pady=5)
        ttk.Label(qrz_row3, text="QRZ API Key:").pack(side='left')
        self.qrz_apikey_var = tk.StringVar(value=self.config.get('qrz.api_key', ''))
        ttk.Entry(qrz_row3, textvariable=self.qrz_apikey_var, width=40).pack(side='left', padx=5)

        ttk.Label(qrz_frame, text="(Get your API key from QRZ.com Logbook settings)",
                 font=('', 8), foreground='gray').pack(anchor='w', pady=2)

        self.qrz_auto_upload_var = tk.BooleanVar(value=self.config.get('qrz.auto_upload', False))
        ttk.Checkbutton(qrz_frame, text="Automatically upload contacts to QRZ Logbook after logging",
                       variable=self.qrz_auto_upload_var).pack(anchor='w', pady=5)

        self.qrz_lookup_var = tk.BooleanVar(value=self.config.get('qrz.enable_lookup', True))
        ttk.Checkbutton(qrz_frame, text="Enable callsign lookup (XML subscription required)",
                       variable=self.qrz_lookup_var).pack(anchor='w', pady=2)

        qrz_test_frame = ttk.Frame(qrz_frame)
        qrz_test_frame.pack(fill='x', pady=5)
        ttk.Button(qrz_test_frame, text="Test QRZ Connection (GET)",
                  command=self.test_qrz_connection).pack(side='left', padx=2)
        ttk.Button(qrz_test_frame, text="Test with POST",
                  command=self.test_qrz_connection_post).pack(side='left', padx=2)

        # Logging Preferences
        logging_frame = ttk.LabelFrame(scrollable_frame, text="Logging Preferences", padding=10)
        logging_frame.pack(fill='x', padx=10, pady=5)

        self.auto_lookup_var = tk.BooleanVar(value=self.config.get('logging.auto_lookup', True))
        ttk.Checkbutton(logging_frame, text="Auto-lookup callsign information when entering callsign",
                       variable=self.auto_lookup_var).pack(anchor='w', pady=2)

        self.warn_dupes_var = tk.BooleanVar(value=self.config.get('logging.warn_duplicates', True))
        ttk.Checkbutton(logging_frame, text="Warn about duplicate contacts",
                       variable=self.warn_dupes_var).pack(anchor='w', pady=2)

        self.auto_timeoff_var = tk.BooleanVar(value=self.config.get('logging.auto_time_off', True))
        ttk.Checkbutton(logging_frame, text="Auto-fill Time OFF when logging contact",
                       variable=self.auto_timeoff_var).pack(anchor='w', pady=2)

        # Backup Settings
        backup_frame = ttk.LabelFrame(scrollable_frame, text="Backup & Auto-Save", padding=10)
        backup_frame.pack(fill='x', padx=10, pady=5)

        self.auto_backup_var = tk.BooleanVar(value=self.config.get('backup.auto_backup', True))
        ttk.Checkbutton(backup_frame, text="Automatically backup log on shutdown",
                       variable=self.auto_backup_var).pack(anchor='w', pady=2)

        ttk.Label(backup_frame, text="Local logs are always saved to: ./logs/",
                 font=('', 8), foreground='gray').pack(anchor='w', pady=(0, 10))

        # External backup path
        external_frame = ttk.Frame(backup_frame)
        external_frame.pack(fill='x', pady=5)

        ttk.Label(external_frame, text="External Backup Path:").pack(anchor='w')
        path_row = ttk.Frame(external_frame)
        path_row.pack(fill='x', pady=2)

        self.backup_path_var = tk.StringVar(value=self.config.get('backup.external_path', ''))
        backup_path_entry = ttk.Entry(path_row, textvariable=self.backup_path_var, width=50)
        backup_path_entry.pack(side='left', padx=(0, 5))

        ttk.Button(path_row, text="Browse...", command=self.browse_backup_path).pack(side='left')

        ttk.Label(external_frame, text="(Leave blank to disable external backup, e.g., USB: /media/usb/ham_logs)",
                 font=('', 8), foreground='gray').pack(anchor='w')

        self.auto_save_var = tk.BooleanVar(value=self.config.get('backup.auto_save', False))
        auto_save_check = ttk.Checkbutton(backup_frame, text="Enable auto-save to external path",
                       variable=self.auto_save_var, command=self.toggle_auto_save)
        auto_save_check.pack(anchor='w', pady=(10, 2))

        # Auto-save interval
        interval_frame = ttk.Frame(backup_frame)
        interval_frame.pack(fill='x', pady=2, padx=20)

        ttk.Label(interval_frame, text="Auto-save interval:").pack(side='left')
        self.auto_save_interval_var = tk.IntVar(value=self.config.get('backup.interval_minutes', 30))
        interval_spin = ttk.Spinbox(interval_frame, from_=5, to=120, increment=5,
                                    textvariable=self.auto_save_interval_var, width=8)
        interval_spin.pack(side='left', padx=5)
        ttk.Label(interval_frame, text="minutes").pack(side='left')

        # Backup and Restore buttons
        backup_buttons_frame = ttk.Frame(backup_frame)
        backup_buttons_frame.pack(pady=10)

        ttk.Button(backup_buttons_frame, text="Backup Log Now", command=self.backup_now).pack(side='left', padx=5)
        ttk.Button(backup_buttons_frame, text="Restore Database", command=self.restore_database).pack(side='left', padx=5)

        ttk.Label(backup_frame, text="Restore will replace current database with a backup file",
                 font=('', 8), foreground='red').pack(anchor='w', pady=(0, 5))

        # DX Cluster Settings
        cluster_frame = ttk.LabelFrame(scrollable_frame, text="DX Cluster Preferences", padding=10)
        cluster_frame.pack(fill='x', padx=10, pady=5)

        self.auto_connect_var = tk.BooleanVar(value=self.config.get('dx_cluster.auto_connect', False))
        ttk.Checkbutton(cluster_frame, text="Auto-connect to cluster on startup",
                       variable=self.auto_connect_var).pack(anchor='w', pady=2)

        # Spot filters
        filter_label = ttk.Label(cluster_frame, text="Show spots for:")
        filter_label.pack(anchor='w', pady=(10, 2))

        self.show_cw_var = tk.BooleanVar(value=self.config.get('dx_cluster.show_cw_spots', True))
        ttk.Checkbutton(cluster_frame, text="CW",
                       variable=self.show_cw_var).pack(anchor='w', padx=20)

        self.show_ssb_var = tk.BooleanVar(value=self.config.get('dx_cluster.show_ssb_spots', True))
        ttk.Checkbutton(cluster_frame, text="SSB/Phone",
                       variable=self.show_ssb_var).pack(anchor='w', padx=20)

        self.show_digital_var = tk.BooleanVar(value=self.config.get('dx_cluster.show_digital_spots', True))
        ttk.Checkbutton(cluster_frame, text="Digital modes",
                       variable=self.show_digital_var).pack(anchor='w', padx=20)

        # Available Clusters Info
        info_frame = ttk.LabelFrame(scrollable_frame, text="Available DX Clusters", padding=10)
        info_frame.pack(fill='both', expand=True, padx=10, pady=5)

        info_text = """
The following DX clusters are configured:

• NC7J (Syracuse, UT) - CW/RTTY Skimmer - dxc.nc7j.com:7373
• DL8LAS (Kiel, Germany) - Skimmer Server - dl8las.dyndns.org:7300
• W1NR (Marlborough, MA) - DXSpider - dx.w1nr.net:7300
• W1NR-9 (Marlborough, MA) - DXSpider zones 1-8 - usdx.w1nr.net:7300
• K1TTT (Peru, MA) - AR-Cluster - k1ttt.net:7373
• W3LPL (Glenwood, MD) - AR-Cluster v.6 - w3lpl.net:7373
• W6RFU (Santa Barbara, CA) - DX Spider - ucsbdx.ece.ucsb.edu:7300
• G6NHU-2 (Essex, UK) - DX Spider with RBN - dxspider.co.uk:7300
• S50CLX (Slovenia) - Multi-mode Skimmer - s50clx.infrax.si:41112
• ZL2ARN-10 (New Zealand) - DXSpider - zl2arn.ddns.net:7300

Cluster list source: https://www.ng3k.com/Misc/cluster.html
        """

        info_label = ttk.Label(info_frame, text=info_text, justify='left')
        info_label.pack(anchor='w')

        # Save button
        btn_frame = ttk.Frame(scrollable_frame)
        btn_frame.pack(fill='x', padx=10, pady=10)

        ttk.Button(btn_frame, text="Save Settings", command=self.save_settings).pack(side='left')
        ttk.Button(btn_frame, text="Reset to Defaults", command=self.reset_settings).pack(side='left', padx=5)

        # Add debug button for QRZ issues
        ttk.Button(btn_frame, text="Debug QRZ", command=self.debug_qrz_raw).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Verify Password", command=self.verify_qrz_password).pack(side='left', padx=5)

    def toggle_password_visibility(self):
        """Toggle password visibility"""
        if self.password_visible:
            self.qrz_password_entry.config(show='*')
            self.password_visible = False
        else:
            self.qrz_password_entry.config(show='')
            self.password_visible = True

    def verify_qrz_password(self):
        """Verify what password is being sent to QRZ"""
        import urllib.parse

        username = self.qrz_username_var.get().strip()
        password = self.qrz_password_var.get()  # Don't strip password - spaces might be intentional

        if not username or not password:
            messagebox.showwarning("Missing Credentials", "Please enter QRZ username and password")
            return

        # Show what's being sent
        info = "Password Verification\n"
        info += "=" * 50 + "\n\n"
        info += f"Username: {username}\n"
        info += f"Password length: {len(password)} characters\n"
        info += f"Password (visible): {password}\n\n"

        # Show URL encoded versions
        encoded_user = urllib.parse.quote(username)
        encoded_pass = urllib.parse.quote(password)

        info += "URL-Encoded Values:\n"
        info += f"Username: {encoded_user}\n"
        info += f"Password: {encoded_pass}\n\n"

        # Check for special characters
        special_chars = ['&', '=', '?', '#', '%', '+', ' ', '@', '!', '$', '*']
        found_special = [c for c in special_chars if c in password]

        if found_special:
            info += f"⚠️  Special characters found: {', '.join(found_special)}\n"
            info += "These are automatically URL-encoded when sent to QRZ.\n\n"

        # Check for leading/trailing spaces
        if password != password.strip():
            info += "⚠️  WARNING: Password has leading or trailing spaces!\n\n"

        info += "Tips:\n"
        info += "• Try logging into https://www.qrz.com with these credentials\n"
        info += "• If login fails on QRZ website, reset your password there\n"
        info += "• Special characters are handled automatically\n"
        info += "• Check for typos by clicking the 👁 button to show password"

        # Show in message box
        messagebox.showinfo("QRZ Password Verification", info)

    def debug_qrz_raw(self):
        """Show raw QRZ XML response for debugging"""
        import urllib.request
        import urllib.parse

        username = self.qrz_username_var.get().strip()
        password = self.qrz_password_var.get().strip()

        if not username or not password:
            messagebox.showwarning("Missing Credentials", "Please enter QRZ username and password")
            return

        try:
            # Build request exactly as the code does
            params = urllib.parse.urlencode({
                'username': username,
                'password': password,
                'agent': 'W4GNS-General-Logger-1.0'
            })

            url = f"https://xmldata.qrz.com/xml/current/?{params}"

            request = urllib.request.Request(url)
            request.add_header('User-Agent', 'W4GNS-General-Logger/1.0')

            with urllib.request.urlopen(request, timeout=10) as response:
                xml_data = response.read().decode('utf-8')

            # Show the raw response in a new window
            debug_window = tk.Toplevel(self.parent)
            debug_window.title("QRZ Raw XML Response")
            debug_window.geometry("800x600")

            # Add scrolled text widget
            from tkinter import scrolledtext
            text_widget = scrolledtext.ScrolledText(debug_window, wrap=tk.WORD)
            text_widget.pack(fill='both', expand=True, padx=10, pady=10)
            text_widget.insert('1.0', xml_data)
            text_widget.config(state='disabled')

            # Add close button
            ttk.Button(debug_window, text="Close", command=debug_window.destroy).pack(pady=5)

        except Exception as e:
            messagebox.showerror("Debug Error", f"Error fetching QRZ response:\n{type(e).__name__}: {str(e)}")

    def test_qrz_connection(self):
        """Test QRZ.com connection using GET method"""
        self._test_qrz_connection(use_post=False)

    def test_qrz_connection_post(self):
        """Test QRZ.com connection using POST method (better for special characters)"""
        self._test_qrz_connection(use_post=True)

    def _test_qrz_connection(self, use_post=False):
        """Internal method to test QRZ connection"""
        username = self.qrz_username_var.get().strip()
        password = self.qrz_password_var.get()  # Don't strip - preserve exact password

        if not username or not password:
            messagebox.showwarning("Missing Credentials", "Please enter QRZ username and password")
            return

        # Show a message that we're testing
        self.parent.config(cursor="watch")
        self.parent.update()

        method_name = "POST" if use_post else "GET"

        try:
            # Test the connection
            success, message = test_qrz_login(username, password, use_post=use_post)

            if success:
                messagebox.showinfo("QRZ Test Successful",
                    f"{message}\n\n"
                    f"✅ Your QRZ credentials are working!\n\n"
                    f"Method used: {method_name}\n"
                    f"Username: {username}")
            else:
                # Show detailed error with troubleshooting tips
                error_msg = f"Method: {method_name}\n\n{message}\n\n"
                error_msg += "Troubleshooting steps:\n"
                error_msg += "1. Click 'Verify Password' to check what's being sent\n"
                error_msg += "2. Click 👁 button to show password and verify it's correct\n"
                error_msg += "3. Try 'Test with POST' if GET fails (better for special chars)\n"
                error_msg += "4. Log into https://www.qrz.com to verify credentials\n"
                error_msg += "5. Check if you have an active QRZ XML subscription\n\n"
                error_msg += "Note: QRZ XML lookups require a separate XML Data subscription."

                messagebox.showerror("QRZ Test Failed", error_msg)
        finally:
            self.parent.config(cursor="")

    def browse_backup_path(self):
        """Browse for external backup directory"""
        current_path = self.backup_path_var.get()
        initial_dir = current_path if current_path else "/"

        directory = filedialog.askdirectory(
            title="Select Backup Directory",
            initialdir=initial_dir
        )

        if directory:
            self.backup_path_var.set(directory)

    def toggle_auto_save(self):
        """Handle auto-save checkbox toggle"""
        if self.auto_save_var.get() and not self.backup_path_var.get():
            messagebox.showwarning(
                "No Backup Path",
                "Please set an external backup path before enabling auto-save."
            )
            self.auto_save_var.set(False)

    def backup_now(self):
        """Manually trigger a backup"""
        try:
            # Import here to avoid circular dependency
            from src.adif import export_contacts_to_adif
            from datetime import datetime
            import os

            # Get the main app database
            # We need to access this from parent chain
            app_window = self.parent.winfo_toplevel()

            # Find the main app instance
            for widget in app_window.winfo_children():
                if hasattr(widget, 'master') and hasattr(widget.master, 'database'):
                    database = widget.master.database
                    break
            else:
                messagebox.showerror("Error", "Could not access database")
                return

            # Get all contacts
            contacts = database.get_all_contacts(limit=999999)

            if not contacts:
                messagebox.showinfo("No Contacts", "No contacts to backup.")
                return

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"w4gns_log_{timestamp}.adi"

            # Backup to local logs directory
            logs_dir = "logs"
            os.makedirs(logs_dir, exist_ok=True)
            local_path = os.path.join(logs_dir, filename)
            export_contacts_to_adif(contacts, local_path)

            backup_message = f"Backed up {len(contacts)} contacts to:\n{local_path}"

            # Backup to external path if configured
            external_path = self.backup_path_var.get().strip()
            if external_path and os.path.exists(external_path):
                external_file = os.path.join(external_path, filename)
                export_contacts_to_adif(contacts, external_file)
                backup_message += f"\n\nAlso backed up to:\n{external_file}"

            messagebox.showinfo("Backup Complete", backup_message)

        except Exception as e:
            messagebox.showerror("Backup Failed", f"Error during backup:\n{str(e)}")

    def restore_database(self):
        """Restore database from a backup file"""
        try:
            # Warn user about the implications
            warning = messagebox.askyesno(
                "Restore Database",
                "⚠️ WARNING ⚠️\n\n"
                "This will REPLACE your current database with a backup file.\n"
                "All current contacts and data will be OVERWRITTEN.\n\n"
                "It is recommended to backup your current database first.\n\n"
                "Do you want to continue?",
                icon='warning'
            )

            if not warning:
                return

            # Ask user to select a database backup file
            file_path = filedialog.askopenfilename(
                title="Select Database Backup File",
                filetypes=[
                    ("Database files", "*.db"),
                    ("All files", "*.*")
                ],
                initialdir="./logs"
            )

            if not file_path:
                return  # User cancelled

            # Verify it's a valid SQLite database
            import sqlite3
            try:
                # Test if we can open it as a database
                test_conn = sqlite3.connect(file_path)
                cursor = test_conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='contacts'")
                result = cursor.fetchone()
                test_conn.close()

                if not result:
                    messagebox.showerror(
                        "Invalid Database",
                        "The selected file does not appear to be a valid W4GNS logger database.\n"
                        "Missing 'contacts' table."
                    )
                    return

            except sqlite3.Error as e:
                messagebox.showerror(
                    "Invalid File",
                    f"The selected file is not a valid SQLite database:\n{str(e)}"
                )
                return

            # Get database instance
            app_window = self.parent.winfo_toplevel()
            database = None

            for widget in app_window.winfo_children():
                if hasattr(widget, 'master') and hasattr(widget.master, 'database'):
                    database = widget.master.database
                    break

            if not database:
                messagebox.showerror("Error", "Could not access database")
                return

            # Close the current database connection
            import shutil
            import os

            db_path = database.db_path
            database.close()

            # Create a backup of the current database before replacing
            backup_current = db_path + ".before_restore"
            if os.path.exists(db_path):
                shutil.copy2(db_path, backup_current)

            # Replace with the backup file
            shutil.copy2(file_path, db_path)

            messagebox.showinfo(
                "Restore Complete",
                f"Database restored successfully!\n\n"
                f"Your previous database was backed up to:\n{backup_current}\n\n"
                f"⚠️ You MUST restart the application now for changes to take effect."
            )

        except Exception as e:
            messagebox.showerror("Restore Failed", f"Error during restore:\n{str(e)}")

    def save_settings(self):
        """Save settings to config"""
        self.config.set('callsign', self.callsign_var.get().strip().upper())
        self.config.set('gridsquare', self.grid_var.get().strip().upper())
        self.config.set('default_rst', self.rst_var.get())
        self.config.set('default_power', self.power_var.get())

        # QRZ settings
        self.config.set('qrz.username', self.qrz_username_var.get().strip())
        self.config.set('qrz.password', self.qrz_password_var.get().strip())
        self.config.set('qrz.api_key', self.qrz_apikey_var.get().strip())
        self.config.set('qrz.auto_upload', self.qrz_auto_upload_var.get())
        self.config.set('qrz.enable_lookup', self.qrz_lookup_var.get())

        # Logging preferences
        self.config.set('logging.auto_lookup', self.auto_lookup_var.get())
        self.config.set('logging.warn_duplicates', self.warn_dupes_var.get())
        self.config.set('logging.auto_time_off', self.auto_timeoff_var.get())

        # Backup settings
        self.config.set('backup.auto_backup', self.auto_backup_var.get())
        self.config.set('backup.external_path', self.backup_path_var.get().strip())
        self.config.set('backup.auto_save', self.auto_save_var.get())
        self.config.set('backup.interval_minutes', self.auto_save_interval_var.get())

        # DX Cluster settings
        self.config.set('dx_cluster.auto_connect', self.auto_connect_var.get())
        self.config.set('dx_cluster.show_cw_spots', self.show_cw_var.get())
        self.config.set('dx_cluster.show_ssb_spots', self.show_ssb_var.get())
        self.config.set('dx_cluster.show_digital_spots', self.show_digital_var.get())

        messagebox.showinfo("Settings Saved", "Your settings have been saved successfully!")

    def reset_settings(self):
        """Reset to default settings"""
        if messagebox.askyesno("Reset Settings", "Are you sure you want to reset all settings to defaults?"):
            defaults = self.config.get_defaults()
            self.callsign_var.set(defaults['callsign'])
            self.grid_var.set(defaults['gridsquare'])
            self.rst_var.set(defaults['default_rst'])
            self.power_var.set(defaults['default_power'])

            # QRZ defaults
            self.qrz_username_var.set(defaults['qrz']['username'])
            self.qrz_password_var.set(defaults['qrz']['password'])
            self.qrz_apikey_var.set(defaults['qrz']['api_key'])
            self.qrz_auto_upload_var.set(defaults['qrz']['auto_upload'])
            self.qrz_lookup_var.set(defaults['qrz']['enable_lookup'])

            # Logging defaults
            self.auto_lookup_var.set(defaults['logging']['auto_lookup'])
            self.warn_dupes_var.set(defaults['logging']['warn_duplicates'])
            self.auto_timeoff_var.set(defaults['logging']['auto_time_off'])

            # DX Cluster defaults
            self.auto_connect_var.set(defaults['dx_cluster']['auto_connect'])
            self.show_cw_var.set(defaults['dx_cluster']['show_cw_spots'])
            self.show_ssb_var.set(defaults['dx_cluster']['show_ssb_spots'])
            self.show_digital_var.set(defaults['dx_cluster']['show_digital_spots'])

    def toggle_theme(self):
        """Toggle between light and dark themes"""
        if not self.theme_manager:
            messagebox.showwarning("Theme Not Available",
                                 "Theme manager not initialized")
            return

        # Toggle the theme
        new_theme = self.theme_manager.toggle_theme()

        # Update button text and label
        theme_text = "Dark Mode" if new_theme == 'light' else "Light Mode"
        self.theme_button.config(text=f"Switch to {theme_text}")
        self.current_theme_label.config(text=f"(Currently: {new_theme.capitalize()})")

        messagebox.showinfo("Theme Changed",
                          f"Switched to {new_theme.capitalize()} theme!")

    def get_frame(self):
        """Return the frame widget"""
        return self.frame
