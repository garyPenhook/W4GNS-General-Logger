"""
Settings Tab - Configuration and preferences
"""

import tkinter as tk
from tkinter import ttk, messagebox


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

    def save_settings(self):
        """Save settings to config"""
        self.config.set('callsign', self.callsign_var.get().strip().upper())
        self.config.set('gridsquare', self.grid_var.get().strip().upper())
        self.config.set('default_rst', self.rst_var.get())
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
            self.auto_connect_var.set(defaults['dx_cluster']['auto_connect'])
            self.show_cw_var.set(defaults['dx_cluster']['show_cw_spots'])
            self.show_ssb_var.set(defaults['dx_cluster']['show_ssb_spots'])
            self.show_digital_var.set(defaults['dx_cluster']['show_digital_spots'])

    def get_frame(self):
        """Return the frame widget"""
        return self.frame
