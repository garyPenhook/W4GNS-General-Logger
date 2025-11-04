"""
Settings Tab - Configuration and preferences
"""

import tkinter as tk
from tkinter import ttk, messagebox
from src.qrz import test_qrz_login


class SettingsTab:
    def __init__(self, parent, config):
        self.parent = parent
        self.config = config
        self.frame = ttk.Frame(parent)
        self.create_widgets()

    def create_widgets(self):
        """Create the settings interface"""

        # Station Information
        station_frame = ttk.LabelFrame(self.frame, text="Station Information", padding=10)
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

        # QRZ.com Integration
        qrz_frame = ttk.LabelFrame(self.frame, text="QRZ.com Integration", padding=10)
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
        ttk.Entry(qrz_row2, textvariable=self.qrz_password_var, width=20, show='*').pack(side='left', padx=5)

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
        ttk.Button(qrz_test_frame, text="Test QRZ Connection",
                  command=self.test_qrz_connection).pack(side='left')

        # Logging Preferences
        logging_frame = ttk.LabelFrame(self.frame, text="Logging Preferences", padding=10)
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

        # DX Cluster Settings
        cluster_frame = ttk.LabelFrame(self.frame, text="DX Cluster Preferences", padding=10)
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
        info_frame = ttk.LabelFrame(self.frame, text="Available DX Clusters", padding=10)
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
        btn_frame = ttk.Frame(self.frame)
        btn_frame.pack(fill='x', padx=10, pady=10)

        ttk.Button(btn_frame, text="Save Settings", command=self.save_settings).pack(side='left')
        ttk.Button(btn_frame, text="Reset to Defaults", command=self.reset_settings).pack(side='left', padx=5)

    def test_qrz_connection(self):
        """Test QRZ.com connection"""
        username = self.qrz_username_var.get().strip()
        password = self.qrz_password_var.get().strip()

        if not username or not password:
            messagebox.showwarning("Missing Credentials", "Please enter QRZ username and password")
            return

        # Test the connection
        success, message = test_qrz_login(username, password)

        if success:
            messagebox.showinfo("QRZ Test Successful", message)
        else:
            messagebox.showerror("QRZ Test Failed", message)

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

    def get_frame(self):
        """Return the frame widget"""
        return self.frame
