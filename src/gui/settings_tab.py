"""
Settings Tab - Configuration and preferences
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from src.qrz import test_qrz_login
from src.theme_colors import get_error_color, get_info_color, get_muted_color, get_success_color, get_warning_color
from src.google_drive_backup import GoogleDriveBackup, format_file_size, format_timestamp


class SettingsTab:
    def __init__(self, parent, config, theme_manager=None, database=None):
        self.parent = parent
        self.config = config
        self.theme_manager = theme_manager
        self.database = database
        self.frame = ttk.Frame(parent)

        # Initialize SKCC roster managers
        from src.skcc_roster import get_roster_manager
        from src.skcc_award_rosters import get_award_roster_manager
        self.roster_manager = get_roster_manager()
        self.award_rosters = get_award_roster_manager(database=database) if database else None

        # Initialize Google Drive backup manager
        self.gdrive_backup = None
        if GoogleDriveBackup.is_available():
            try:
                self.gdrive_backup = GoogleDriveBackup(config, database.db_path if database else None)
            except Exception as e:
                print(f"Google Drive backup initialization failed: {e}")

        self.create_widgets()

        # CRITICAL: Auto-download rosters on EVERY startup for accurate award validation
        # Delay start until after main loop is running to avoid threading errors
        self.parent.after(100, self.auto_download_rosters_on_startup)

        # Start auto backup if enabled
        if self.gdrive_backup and self.config.get('google_drive.enabled', False):
            self.gdrive_backup.start_auto_backup()

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

        ttk.Label(row1, text="Operator Name:").pack(side='left', padx=(20, 0))
        self.operator_name_var = tk.StringVar(value=self.config.get('operator_name', ''))
        ttk.Entry(row1, textvariable=self.operator_name_var, width=25).pack(side='left', padx=5)
        ttk.Label(row1, text="(for award applications)", font=('', 8), foreground=get_muted_color(self.config)).pack(side='left')

        row2 = ttk.Frame(station_frame)
        row2.pack(fill='x', pady=5)
        ttk.Label(row2, text="Grid Square:").pack(side='left')
        self.grid_var = tk.StringVar(value=self.config.get('gridsquare', ''))
        ttk.Entry(row2, textvariable=self.grid_var, width=10).pack(side='left', padx=5)

        ttk.Label(row2, text="SKCC Number:").pack(side='left', padx=(20, 0))
        self.skcc_number_var = tk.StringVar(value=self.config.get('skcc_number', ''))
        ttk.Entry(row2, textvariable=self.skcc_number_var, width=12).pack(side='left', padx=5)

        row3 = ttk.Frame(station_frame)
        row3.pack(fill='x', pady=5)
        ttk.Label(row3, text="Default RST:").pack(side='left')
        self.rst_var = tk.StringVar(value=self.config.get('default_rst', '59'))
        ttk.Entry(row3, textvariable=self.rst_var, width=8).pack(side='left', padx=5)

        ttk.Label(row3, text="Default Power (W):").pack(side='left', padx=(20, 0))
        self.power_var = tk.StringVar(value=self.config.get('default_power', '100'))
        ttk.Entry(row3, textvariable=self.power_var, width=8).pack(side='left', padx=5)

        ttk.Label(row3, text="Zip Code:").pack(side='left', padx=(20, 0))
        self.zip_code_var = tk.StringVar(value=self.config.get('zip_code', ''))
        ttk.Entry(row3, textvariable=self.zip_code_var, width=10).pack(side='left', padx=5)
        ttk.Label(row3, text="(for weather)", font=('', 8), foreground=get_muted_color(self.config)).pack(side='left')

        # SKCC Roster Status section
        roster_frame = ttk.LabelFrame(scrollable_frame, text="SKCC Rosters Status", padding=10)
        roster_frame.pack(fill='x', padx=10, pady=5)

        roster_info_frame = ttk.Frame(roster_frame)
        roster_info_frame.pack(fill='x')

        ttk.Label(roster_info_frame, text="Membership Roster:", font=('', 10, 'bold'), width=20).pack(side='left')
        self.roster_status_label = ttk.Label(roster_info_frame, text="Loading...", font=('', 10))
        self.roster_status_label.pack(side='left', padx=10)

        roster_info_frame2 = ttk.Frame(roster_frame)
        roster_info_frame2.pack(fill='x', pady=(5, 0))

        ttk.Label(roster_info_frame2, text="Award Rosters:", font=('', 10, 'bold'), width=20).pack(side='left')
        self.award_roster_status_label = ttk.Label(roster_info_frame2, text="Loading...", font=('', 10))
        self.award_roster_status_label.pack(side='left', padx=10)

        ttk.Label(roster_frame,
                 text="Rosters are downloaded automatically on startup for accurate award validation.",
                 font=('', 9, 'italic'), foreground=get_muted_color(self.config)).pack(anchor='w', pady=(5, 0))

        # Update roster status display
        self.update_roster_status()

        # User's SKCC Information section
        user_skcc_frame = ttk.LabelFrame(scrollable_frame, text="SKCC Award Configuration", padding=10)
        user_skcc_frame.pack(fill='x', padx=10, pady=5)

        # SKCC Join Date
        join_date_row = ttk.Frame(user_skcc_frame)
        join_date_row.pack(fill='x', pady=2)

        ttk.Label(join_date_row, text="SKCC Join Date:", font=('', 10, 'bold'), width=20).pack(side='left')
        ttk.Label(join_date_row, text="(YYYYMMDD)", font=('', 9), foreground=get_muted_color(self.config)).pack(side='left', padx=5)

        self.join_date_var = tk.StringVar(value=self.config.get('skcc.join_date', ''))
        self.join_date_entry = ttk.Entry(join_date_row, textvariable=self.join_date_var, width=12)
        self.join_date_entry.pack(side='left', padx=5)

        ttk.Button(join_date_row, text="Save",
                  command=self.save_join_date).pack(side='left', padx=5)

        self.join_date_status = ttk.Label(join_date_row, text="", font=('', 9))
        self.join_date_status.pack(side='left', padx=10)

        # Centurion Achievement Date
        centurion_date_row = ttk.Frame(user_skcc_frame)
        centurion_date_row.pack(fill='x', pady=2)

        ttk.Label(centurion_date_row, text="Centurion Date:", font=('', 10, 'bold'), width=20).pack(side='left')
        ttk.Label(centurion_date_row, text="(YYYYMMDD)", font=('', 9), foreground=get_muted_color(self.config)).pack(side='left', padx=5)

        self.centurion_date_var = tk.StringVar(value=self.config.get('skcc.centurion_date', ''))
        self.centurion_date_entry = ttk.Entry(centurion_date_row, textvariable=self.centurion_date_var, width=12)
        self.centurion_date_entry.pack(side='left', padx=5)

        ttk.Button(centurion_date_row, text="Save",
                  command=self.save_centurion_date).pack(side='left', padx=5)

        self.centurion_date_status = ttk.Label(centurion_date_row, text="", font=('', 9))
        self.centurion_date_status.pack(side='left', padx=10)

        # Tribune x8 Achievement Date
        tribune_x8_date_row = ttk.Frame(user_skcc_frame)
        tribune_x8_date_row.pack(fill='x', pady=2)

        ttk.Label(tribune_x8_date_row, text="Tribune x8 Date:", font=('', 10, 'bold'), width=20).pack(side='left')
        ttk.Label(tribune_x8_date_row, text="(YYYYMMDD)", font=('', 9), foreground=get_muted_color(self.config)).pack(side='left', padx=5)

        self.tribune_x8_date_var = tk.StringVar(value=self.config.get('skcc.tribune_x8_date', ''))
        self.tribune_x8_date_entry = ttk.Entry(tribune_x8_date_row, textvariable=self.tribune_x8_date_var, width=12)
        self.tribune_x8_date_entry.pack(side='left', padx=5)

        ttk.Button(tribune_x8_date_row, text="Save",
                  command=self.save_tribune_x8_date).pack(side='left', padx=5)

        self.tribune_x8_date_status = ttk.Label(tribune_x8_date_row, text="", font=('', 9))
        self.tribune_x8_date_status.pack(side='left', padx=10)

        ttk.Label(user_skcc_frame,
                 text="⚠️ Critical: Join date required for all awards.",
                 font=('', 9, 'italic'), foreground=get_warning_color(self.config)).pack(anchor='w', pady=(5, 0))
        ttk.Label(user_skcc_frame,
                 text="Centurion date required for Tribune/Senator. Tribune x8 date required for Senator.",
                 font=('', 9, 'italic'), foreground=get_warning_color(self.config)).pack(anchor='w')
        ttk.Label(user_skcc_frame,
                 text="QSOs before these dates will not count toward respective awards.",
                 font=('', 9, 'italic'), foreground=get_warning_color(self.config)).pack(anchor='w')

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
                                            foreground=get_info_color(self.config))
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
                 font=('', 8), foreground=get_muted_color(self.config)).pack(anchor='w', pady=2)

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
                 font=('', 8), foreground=get_muted_color(self.config)).pack(anchor='w', pady=(0, 10))

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
                 font=('', 8), foreground=get_muted_color(self.config)).pack(anchor='w')

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
                 font=('', 8), foreground=get_error_color(self.config)).pack(anchor='w', pady=(0, 5))

        # NASA API Configuration
        nasa_frame = ttk.LabelFrame(scrollable_frame, text="NASA Space Weather API", padding=10)
        nasa_frame.pack(fill='x', padx=10, pady=5)

        nasa_row = ttk.Frame(nasa_frame)
        nasa_row.pack(fill='x', pady=5)
        ttk.Label(nasa_row, text="NASA API Key:").pack(side='left')
        self.nasa_api_key_var = tk.StringVar(value=self.config.get('nasa.api_key', 'DEMO_KEY'))
        ttk.Entry(nasa_row, textvariable=self.nasa_api_key_var, width=50).pack(side='left', padx=5)

        ttk.Label(nasa_frame, text="Get your free API key from https://api.nasa.gov/ (no rate limits)",
                 font=('', 8), foreground=get_muted_color(self.config)).pack(anchor='w', pady=2)

        ttk.Label(nasa_frame, text="Used for NASA DONKI space weather event alerts in the Space Weather tab.",
                 font=('', 8), foreground=get_muted_color(self.config)).pack(anchor='w', pady=(0, 2))

        # Cache duration
        cache_row = ttk.Frame(nasa_frame)
        cache_row.pack(fill='x', pady=5)
        ttk.Label(cache_row, text="Cache DONKI data for:").pack(side='left')
        self.nasa_cache_hours_var = tk.StringVar(value=str(self.config.get('nasa.donki_cache_hours', 24)))
        ttk.Entry(cache_row, textvariable=self.nasa_cache_hours_var, width=5).pack(side='left', padx=5)
        ttk.Label(cache_row, text="hours").pack(side='left')
        ttk.Label(cache_row, text="(reduces API calls)", font=('', 8), foreground=get_muted_color(self.config)).pack(side='left', padx=10)

        # Google Drive Backup Settings
        self.create_google_drive_section(scrollable_frame)

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

USA RBN/Skimmer Clusters (Reverse Beacon Network):
• AE5E (Thief River Falls, MN) - DX Spider +RBN - dxspots.com:7300
• K1AX-11 (N. Virginia) - DX Spider +RBN - dxdata.io:7300
• AI9T (Marshall, IL) - DX Spider +RBN - dxc.ai9t.com:7300
• K7TJ-1 (Spokane, WA) - DX Spider +RBN - k7tj.ewarg.org:7300
• AI6W-1 (Newcastle, CA) - DX Spider +RBN - ai6w.net:7300
• KB8PMY-3 (Hamilton, OH) - DX Spider +RBN - kb8pmy.net:7300
• K9LC (Rockford, IL) - DX Spider +RBN - k9lc.ddns.net:7300
• AE3N-2 (Virginia) - DX Spider +RBN - dxc.ae3n.us:7300
• K4GSO-2 (Ocala, FL) - AR-Cluster +RBN - dxc.k4gso.com:7373
• K2CAN (Oswego, NY) - AR-Cluster +RBN - k2can.us:7373
• NC7J (Syracuse, UT) - CW/RTTY Skimmer - dxc.nc7j.com:7373

International RBN Clusters:
• G6NHU-2 (Essex, UK) - DX Spider with RBN - dxspider.co.uk:7300
• DL8LAS (Kiel, Germany) - Skimmer Server - dl8las.dyndns.org:7300
• S50CLX (Slovenia) - Multi-mode Skimmer - s50clx.infrax.si:41112

Traditional DX Clusters (USA):
• W1NR (Marlborough, MA) - DXSpider - dx.w1nr.net:7300
• W1NR-9 (Marlborough, MA) - DXSpider zones 1-8 - usdx.w1nr.net:7300
• K1TTT (Peru, MA) - AR-Cluster - k1ttt.net:7373
• W3LPL (Glenwood, MD) - AR-Cluster v.6 - w3lpl.net:7373
• W6RFU (Santa Barbara, CA) - DX Spider - ucsbdx.ece.ucsb.edu:7300

Traditional DX Clusters (International):
• ZL2ARN-10 (New Zealand) - DXSpider - zl2arn.ddns.net:7300

💡 RBN/Skimmer clusters provide automated CW spot detection via remote receivers.
   Traditional clusters rely on manual user-submitted spots.

Cluster list sources:
• https://www.ng3k.com/Misc/cluster.html
• https://www.dxcluster.info/telnet/index.php
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
        """Manually trigger a backup of both database and ADIF export"""
        try:
            # Import here to avoid circular dependency
            from src.adif import export_contacts_to_adif
            from datetime import datetime
            import os
            import shutil

            # Check if database is available
            if not self.database:
                messagebox.showerror("Error", "Could not access database")
                return

            # Get all contacts
            contacts = self.database.get_all_contacts(limit=999999)

            if not contacts:
                messagebox.showinfo("No Contacts", "No contacts to backup.")
                return

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            db_filename = f"w4gns_log_{timestamp}.db"
            adif_filename = f"w4gns_log_{timestamp}.adi"

            # Backup to local logs directory
            logs_dir = "logs"
            os.makedirs(logs_dir, exist_ok=True)

            # Backup database file
            local_db_path = os.path.join(logs_dir, db_filename)
            shutil.copy2(self.database.db_path, local_db_path)

            # Export to ADIF
            local_adif_path = os.path.join(logs_dir, adif_filename)
            export_contacts_to_adif(contacts, local_adif_path)

            backup_message = f"Backed up {len(contacts)} contacts:\n\n"
            backup_message += f"Database: {local_db_path}\n"
            backup_message += f"ADIF: {local_adif_path}"

            # Backup to external path if configured
            external_path = self.backup_path_var.get().strip()
            if external_path and os.path.exists(external_path):
                external_db_file = os.path.join(external_path, db_filename)
                external_adif_file = os.path.join(external_path, adif_filename)

                shutil.copy2(self.database.db_path, external_db_file)
                export_contacts_to_adif(contacts, external_adif_file)

                backup_message += f"\n\nAlso backed up to external path:\n"
                backup_message += f"Database: {external_db_file}\n"
                backup_message += f"ADIF: {external_adif_file}"

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

            # Check if database is available
            if not self.database:
                messagebox.showerror("Error", "Could not access database")
                return

            # Close the current database connection
            import shutil
            import os

            db_path = self.database.db_path
            self.database.close()

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
                f"⚠️ The application will now close.\n"
                f"Please restart it to use the restored database."
            )

            # Close the application to prevent operating on a closed database
            root = self.parent.winfo_toplevel()
            root.destroy()  # This will close the application cleanly

        except Exception as e:
            messagebox.showerror("Restore Failed", f"Error during restore:\n{str(e)}")

    def save_settings(self):
        """Save settings to config"""
        self.config.set('callsign', self.callsign_var.get().strip().upper())
        self.config.set('operator_name', self.operator_name_var.get().strip())
        self.config.set('gridsquare', self.grid_var.get().strip().upper())
        self.config.set('skcc_number', self.skcc_number_var.get().strip().upper())
        self.config.set('default_rst', self.rst_var.get())
        self.config.set('default_power', self.power_var.get())
        self.config.set('zip_code', self.zip_code_var.get().strip())

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

        # NASA API settings
        self.config.set('nasa.api_key', self.nasa_api_key_var.get().strip())
        try:
            cache_hours = int(self.nasa_cache_hours_var.get())
            self.config.set('nasa.donki_cache_hours', cache_hours)
        except ValueError:
            pass  # Keep existing value if invalid

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

    # SKCC Configuration Methods

    def save_join_date(self):
        """Save user's SKCC join date to config"""
        join_date = self.join_date_var.get().strip().replace('-', '')

        # Validate format
        if join_date and (len(join_date) != 8 or not join_date.isdigit()):
            self.join_date_status.config(
                text="❌ Invalid format (use YYYYMMDD)",
                foreground=get_error_color(self.config)
            )
            return

        # Save to config
        self.config.set('skcc.join_date', join_date)

        # Update status
        if join_date:
            self.join_date_status.config(
                text="✅ Saved",
                foreground=get_success_color(self.config)
            )
        else:
            self.join_date_status.config(
                text="⚠️ Join date cleared",
                foreground=get_warning_color(self.config)
            )

        # Clear status after 3 seconds
        self.parent.after(3000, lambda: self.join_date_status.config(text=""))

    def save_centurion_date(self):
        """Save user's Centurion achievement date to config"""
        centurion_date = self.centurion_date_var.get().strip().replace('-', '')

        # Validate format
        if centurion_date and (len(centurion_date) != 8 or not centurion_date.isdigit()):
            self.centurion_date_status.config(
                text="❌ Invalid format (use YYYYMMDD)",
                foreground=get_error_color(self.config)
            )
            return

        # Validate it's not before join date
        join_date = self.config.get('skcc.join_date', '')
        if centurion_date and join_date and centurion_date < join_date:
            self.centurion_date_status.config(
                text="❌ Cannot be before join date",
                foreground=get_error_color(self.config)
            )
            return

        # Save to config
        self.config.set('skcc.centurion_date', centurion_date)

        # Update status
        if centurion_date:
            self.centurion_date_status.config(
                text="✅ Saved",
                foreground=get_success_color(self.config)
            )
        else:
            self.centurion_date_status.config(
                text="⚠️ Centurion date cleared",
                foreground=get_warning_color(self.config)
            )

        # Clear status after 3 seconds
        self.parent.after(3000, lambda: self.centurion_date_status.config(text=""))

    def save_tribune_x8_date(self):
        """Save user's Tribune x8 achievement date to config"""
        tribune_x8_date = self.tribune_x8_date_var.get().strip().replace('-', '')

        # Validate format
        if tribune_x8_date and (len(tribune_x8_date) != 8 or not tribune_x8_date.isdigit()):
            self.tribune_x8_date_status.config(
                text="❌ Invalid format (use YYYYMMDD)",
                foreground=get_error_color(self.config)
            )
            return

        # Validate it's not before Centurion date
        centurion_date = self.config.get('skcc.centurion_date', '')
        if tribune_x8_date and centurion_date and tribune_x8_date < centurion_date:
            self.tribune_x8_date_status.config(
                text="❌ Cannot be before Centurion date",
                foreground=get_error_color(self.config)
            )
            return

        # Save to config
        self.config.set('skcc.tribune_x8_date', tribune_x8_date)

        # Update status
        if tribune_x8_date:
            self.tribune_x8_date_status.config(
                text="✅ Saved",
                foreground=get_success_color(self.config)
            )
        else:
            self.tribune_x8_date_status.config(
                text="⚠️ Tribune x8 date cleared",
                foreground=get_warning_color(self.config)
            )

        # Clear status after 3 seconds
        self.parent.after(3000, lambda: self.tribune_x8_date_status.config(text=""))

    def update_roster_status(self):
        """Update the roster status labels"""
        # Membership roster status
        if self.roster_manager.has_local_roster():
            count = self.roster_manager.get_member_count()
            age = self.roster_manager.get_roster_age()
            self.roster_status_label.config(
                text=f"{count:,} members | Updated: {age}",
                foreground=get_success_color(self.config)
            )
        else:
            self.roster_status_label.config(
                text="Not downloaded",
                foreground=get_warning_color(self.config)
            )

        # Award rosters status
        if self.award_rosters:
            award_info = self.award_rosters.get_roster_info()
            centurion_count = award_info['centurion']['count']
            tribune_count = award_info['tribune']['count']
            senator_count = award_info['senator']['count']

            if centurion_count > 0 and tribune_count > 0 and senator_count > 0:
                self.award_roster_status_label.config(
                    text=f"C:{centurion_count:,} T:{tribune_count:,} S:{senator_count:,}",
                    foreground=get_success_color(self.config)
                )
            else:
                self.award_roster_status_label.config(
                    text="Not downloaded",
                    foreground=get_warning_color(self.config)
                )
        else:
            self.award_roster_status_label.config(
                text="Database not available",
                foreground=get_warning_color(self.config)
            )

    def auto_download_rosters_on_startup(self):
        """
        Auto-download all rosters on EVERY startup.

        CRITICAL: Rosters MUST be updated on every startup to ensure contacts
        are validated with current membership data and award dates.

        This downloads:
        1. Membership roster (SKCC member numbers and join dates)
        2. Award rosters (Centurion, Tribune, Senator award dates)
        """
        import threading

        def download_membership_roster():
            """Download membership roster in background thread"""
            try:
                self.parent.after(0, lambda: self.roster_status_label.config(
                    text="Downloading membership roster...",
                    foreground=get_info_color(self.config)
                ))

                # Download membership roster
                success = self.roster_manager.download_roster()

                if success:
                    # Show completion message
                    count = self.roster_manager.get_member_count()

                    def show_success():
                        self.roster_status_label.config(
                            text=f"✓ Download complete: {count:,} members",
                            foreground=get_success_color(self.config)
                        )
                        # After 5 seconds, revert to normal status display
                        self.parent.after(5000, self.update_roster_status)

                    self.parent.after(0, show_success)
                    print(f"✓ SKCC membership roster updated: {count:,} members")
                else:
                    # Download failed
                    def show_failure():
                        self.roster_status_label.config(
                            text="⚠ Download failed - using cached data if available",
                            foreground=get_warning_color(self.config)
                        )
                        # After 5 seconds, show current status
                        self.parent.after(5000, self.update_roster_status)

                    self.parent.after(0, show_failure)
                    print(f"⚠ SKCC membership roster download failed")

            except Exception as e:
                print(f"Error downloading membership roster: {e}")
                import traceback
                traceback.print_exc()

                def show_error():
                    self.roster_status_label.config(
                        text=f"❌ Error: {str(e)[:50]}",
                        foreground=get_error_color(self.config)
                    )
                    # After 5 seconds, try to show what we have
                    self.parent.after(5000, self.update_roster_status)

                self.parent.after(0, show_error)

        def download_award_rosters():
            """Download award rosters in background thread"""
            try:
                if not self.award_rosters:
                    return

                self.parent.after(0, lambda: self.award_roster_status_label.config(
                    text="Downloading award rosters...",
                    foreground=get_info_color(self.config)
                ))

                # Download Centurion, Tribune, and Senator rosters
                results = self.award_rosters.download_all_rosters(force=False)

                # Get roster info for display
                info = self.award_rosters.get_roster_info()

                # Update UI on completion
                if all(results.values()):
                    # All rosters downloaded successfully
                    def show_success():
                        self.award_roster_status_label.config(
                            text=f"✓ Download complete: C:{info['centurion']['count']:,} T:{info['tribune']['count']:,} S:{info['senator']['count']:,}",
                            foreground=get_success_color(self.config)
                        )
                        # After 5 seconds, revert to normal status display
                        self.parent.after(5000, self.update_roster_status)

                    self.parent.after(0, show_success)

                    print(f"✓ SKCC award rosters updated:")
                    print(f"  Centurion: {info['centurion']['count']:,} members")
                    print(f"  Tribune: {info['tribune']['count']:,} members")
                    print(f"  Senator: {info['senator']['count']:,} members")
                else:
                    # Some rosters failed
                    failed_rosters = [name for name, success in results.items() if not success]

                    def show_partial_failure():
                        self.award_roster_status_label.config(
                            text=f"⚠ Partial download - failed: {', '.join(failed_rosters)}",
                            foreground=get_warning_color(self.config)
                        )
                        # After 5 seconds, revert to normal status display
                        self.parent.after(5000, self.update_roster_status)

                    self.parent.after(0, show_partial_failure)
                    print(f"⚠ Some award rosters failed to download: {results}")

            except Exception as e:
                print(f"Error downloading award rosters: {e}")
                import traceback
                traceback.print_exc()

                def show_error():
                    self.award_roster_status_label.config(
                        text=f"❌ Download failed: {str(e)[:50]}",
                        foreground=get_error_color(self.config)
                    )
                    # After 5 seconds, try to show what we have
                    self.parent.after(5000, self.update_roster_status)

                self.parent.after(0, show_error)

        # Start both downloads in parallel background threads
        membership_thread = threading.Thread(target=download_membership_roster, daemon=True)
        award_thread = threading.Thread(target=download_award_rosters, daemon=True)

        membership_thread.start()
        award_thread.start()

    def get_frame(self):
        """Return the frame widget"""
        return self.frame

    def create_google_drive_section(self, parent):
        """Create Google Drive backup configuration section"""
        gdrive_frame = ttk.LabelFrame(parent, text="Google Drive Auto-Backup", padding=10)
        gdrive_frame.pack(fill='x', padx=10, pady=5)

        # Check if Google Drive API is available
        if not GoogleDriveBackup.is_available():
            warning_label = ttk.Label(gdrive_frame,
                                     text="⚠️ Google Drive API not installed. Run: pip install -r requirements.txt",
                                     foreground=get_warning_color(self.config))
            warning_label.pack(anchor='w', pady=5)
            return

        if not self.gdrive_backup:
            error_label = ttk.Label(gdrive_frame,
                                   text="❌ Google Drive backup initialization failed",
                                   foreground=get_error_color(self.config))
            error_label.pack(anchor='w', pady=5)
            return

        # Enable/Disable Google Drive backups
        self.gdrive_enabled_var = tk.BooleanVar(value=self.config.get('google_drive.enabled', False))
        enable_check = ttk.Checkbutton(gdrive_frame, text="Enable automatic Google Drive backups",
                                      variable=self.gdrive_enabled_var,
                                      command=self.toggle_gdrive_backup)
        enable_check.pack(anchor='w', pady=5)

        # Authentication status
        auth_frame = ttk.Frame(gdrive_frame)
        auth_frame.pack(fill='x', pady=5)

        ttk.Label(auth_frame, text="Status:", font=('', 10, 'bold')).pack(side='left')
        self.gdrive_status_label = ttk.Label(auth_frame, text="Not authenticated", foreground=get_warning_color(self.config))
        self.gdrive_status_label.pack(side='left', padx=10)

        auth_btn_frame = ttk.Frame(auth_frame)
        auth_btn_frame.pack(side='left', padx=10)

        ttk.Button(auth_btn_frame, text="Connect to Google Drive",
                  command=self.authenticate_gdrive).pack(side='left', padx=2)
        ttk.Button(auth_btn_frame, text="Disconnect",
                  command=self.disconnect_gdrive).pack(side='left', padx=2)

        # Backup configuration
        config_frame = ttk.LabelFrame(gdrive_frame, text="Backup Settings", padding=5)
        config_frame.pack(fill='x', pady=10)

        # Backup interval
        interval_row = ttk.Frame(config_frame)
        interval_row.pack(fill='x', pady=2)

        ttk.Label(interval_row, text="Backup interval:").pack(side='left')
        self.gdrive_interval_var = tk.IntVar(value=self.config.get('google_drive.backup_interval_hours', 24))
        interval_spin = ttk.Spinbox(interval_row, from_=1, to=168, increment=1,
                                   textvariable=self.gdrive_interval_var, width=8)
        interval_spin.pack(side='left', padx=5)
        ttk.Label(interval_row, text="hours").pack(side='left')

        # Max backups to keep
        retention_row = ttk.Frame(config_frame)
        retention_row.pack(fill='x', pady=2)

        ttk.Label(retention_row, text="Keep last:").pack(side='left')
        self.gdrive_max_backups_var = tk.IntVar(value=self.config.get('google_drive.max_backups', 30))
        max_spin = ttk.Spinbox(retention_row, from_=5, to=100, increment=5,
                              textvariable=self.gdrive_max_backups_var, width=8)
        max_spin.pack(side='left', padx=5)
        ttk.Label(retention_row, text="backups (older backups are automatically deleted)").pack(side='left')

        # Include config option
        self.gdrive_include_config_var = tk.BooleanVar(value=self.config.get('google_drive.include_config', True))
        ttk.Checkbutton(config_frame, text="Include configuration file (config.json) in backup",
                       variable=self.gdrive_include_config_var).pack(anchor='w', pady=2)

        # Last backup info
        last_backup_frame = ttk.Frame(gdrive_frame)
        last_backup_frame.pack(fill='x', pady=5)

        ttk.Label(last_backup_frame, text="Last backup:", font=('', 10, 'bold')).pack(side='left')
        self.gdrive_last_backup_label = ttk.Label(last_backup_frame, text="Never", foreground=get_muted_color(self.config))
        self.gdrive_last_backup_label.pack(side='left', padx=10)

        # Manual backup buttons
        manual_frame = ttk.Frame(gdrive_frame)
        manual_frame.pack(fill='x', pady=5)

        ttk.Button(manual_frame, text="Backup Now", command=self.gdrive_backup_now).pack(side='left', padx=5)
        ttk.Button(manual_frame, text="View Backups", command=self.gdrive_view_backups).pack(side='left', padx=5)
        ttk.Button(manual_frame, text="Open Google Drive Folder", command=self.gdrive_open_folder).pack(side='left', padx=5)

        # Instructions
        ttk.Label(gdrive_frame,
                 text="Note: First-time setup requires Google OAuth authentication in your browser.",
                 font=('', 8, 'italic'), foreground=get_muted_color(self.config)).pack(anchor='w', pady=(5, 0))

        # Update status
        self.update_gdrive_status()

    def update_gdrive_status(self):
        """Update Google Drive status display"""
        if not self.gdrive_backup:
            return

        if self.gdrive_backup.is_authenticated:
            self.gdrive_status_label.config(text="✓ Connected", foreground=get_success_color(self.config))
        else:
            self.gdrive_status_label.config(text="Not authenticated", foreground=get_warning_color(self.config))

        # Update last backup time
        last_backup = self.config.get('google_drive.last_backup')
        if last_backup:
            self.gdrive_last_backup_label.config(text=format_timestamp(last_backup))
        else:
            self.gdrive_last_backup_label.config(text="Never")

    def authenticate_gdrive(self):
        """Authenticate with Google Drive"""
        if not self.gdrive_backup:
            messagebox.showerror("Error", "Google Drive backup not initialized")
            return

        try:
            messagebox.showinfo("Google Drive Authentication",
                              "A browser window will open for Google authentication.\n\n"
                              "Please:\n"
                              "1. Sign in to your Google account\n"
                              "2. Grant permissions to access Google Drive\n"
                              "3. Complete the authorization")

            self.gdrive_backup.authenticate()
            messagebox.showinfo("Success", "Successfully authenticated with Google Drive!")
            self.update_gdrive_status()

        except FileNotFoundError as e:
            messagebox.showerror("Credentials Not Found",
                               f"{str(e)}\n\n"
                               "To use Google Drive backup:\n"
                               "1. Go to Google Cloud Console\n"
                               "2. Create OAuth 2.0 credentials\n"
                               "3. Download credentials as 'gdrive_credentials.json'\n"
                               "4. Place in project root directory")
        except Exception as e:
            messagebox.showerror("Authentication Failed", f"Error: {str(e)}")

    def disconnect_gdrive(self):
        """Disconnect from Google Drive"""
        if not self.gdrive_backup:
            return

        if messagebox.askyesno("Disconnect", "Disconnect from Google Drive?\n\nYou will need to re-authenticate to use backups again."):
            self.gdrive_backup.disconnect()
            self.update_gdrive_status()
            messagebox.showinfo("Disconnected", "Disconnected from Google Drive")

    def toggle_gdrive_backup(self):
        """Toggle Google Drive auto-backup"""
        enabled = self.gdrive_enabled_var.get()
        self.config.set('google_drive.enabled', enabled)

        if enabled and self.gdrive_backup:
            if not self.gdrive_backup.is_authenticated:
                messagebox.showwarning("Not Authenticated",
                                     "Please authenticate with Google Drive first")
                self.gdrive_enabled_var.set(False)
                self.config.set('google_drive.enabled', False)
                return

            self.gdrive_backup.start_auto_backup()
            messagebox.showinfo("Auto-Backup Enabled", "Google Drive auto-backup is now enabled")
        elif self.gdrive_backup:
            self.gdrive_backup.stop_auto_backup_thread()
            messagebox.showinfo("Auto-Backup Disabled", "Google Drive auto-backup is now disabled")

    def gdrive_backup_now(self):
        """Perform manual backup to Google Drive"""
        if not self.gdrive_backup:
            messagebox.showerror("Error", "Google Drive backup not initialized")
            return

        if not self.gdrive_backup.is_authenticated:
            messagebox.showwarning("Not Authenticated",
                                 "Please authenticate with Google Drive first")
            return

        # Save current config settings
        self.config.set('google_drive.backup_interval_hours', self.gdrive_interval_var.get())
        self.config.set('google_drive.max_backups', self.gdrive_max_backups_var.get())
        self.config.set('google_drive.include_config', self.gdrive_include_config_var.get())

        try:
            result = self.gdrive_backup.create_backup(include_config=self.gdrive_include_config_var.get())

            if result['success']:
                msg = f"Backup completed successfully!\n\n"
                msg += f"Timestamp: {result['timestamp']}\n"
                if 'database' in result:
                    msg += f"Database: {result['database'].get('name', 'N/A')}\n"
                if 'config' in result and result['config']['success']:
                    msg += f"Config: {result['config'].get('name', 'N/A')}\n"

                messagebox.showinfo("Backup Complete", msg)
                self.update_gdrive_status()
            else:
                messagebox.showerror("Backup Failed", f"Error: {result.get('error', 'Unknown error')}")

        except Exception as e:
            messagebox.showerror("Backup Failed", f"Error: {str(e)}")

    def gdrive_view_backups(self):
        """View list of backups in Google Drive"""
        if not self.gdrive_backup or not self.gdrive_backup.is_authenticated:
            messagebox.showwarning("Not Authenticated", "Please authenticate with Google Drive first")
            return

        try:
            backups = self.gdrive_backup.list_backups()

            if not backups:
                messagebox.showinfo("No Backups", "No backups found in Google Drive")
                return

            # Create window to display backups
            backup_window = tk.Toplevel(self.parent)
            backup_window.title("Google Drive Backups")
            backup_window.geometry("700x400")

            # Add scrollable list
            frame = ttk.Frame(backup_window)
            frame.pack(fill='both', expand=True, padx=10, pady=10)

            # Treeview for backups
            columns = ('name', 'size', 'created')
            tree = ttk.Treeview(frame, columns=columns, show='headings', height=15)

            tree.heading('name', text='Filename')
            tree.heading('size', text='Size')
            tree.heading('created', text='Created')

            tree.column('name', width=350)
            tree.column('size', width=100)
            tree.column('created', width=200)

            scrollbar = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)

            tree.pack(side='left', fill='both', expand=True)
            scrollbar.pack(side='right', fill='y')

            # Populate with backups
            for backup in backups:
                tree.insert('', 'end', values=(
                    backup['name'],
                    format_file_size(backup.get('size', 0)),
                    format_timestamp(backup.get('createdTime', ''))
                ))

            ttk.Label(backup_window, text=f"Total backups: {len(backups)}").pack(pady=5)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to list backups: {str(e)}")

    def gdrive_open_folder(self):
        """Open Google Drive backup folder in browser"""
        if not self.gdrive_backup or not self.gdrive_backup.backup_folder_id:
            messagebox.showwarning("Not Authenticated", "Please authenticate with Google Drive first")
            return

        import webbrowser
        folder_url = f"https://drive.google.com/drive/folders/{self.gdrive_backup.backup_folder_id}"
        webbrowser.open(folder_url)
