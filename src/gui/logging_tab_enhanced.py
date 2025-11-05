"""
Enhanced Logging Tab - Log4OM-style contact logging interface
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import threading
from src.dxcc import lookup_dxcc
from src.qrz import QRZSession, upload_to_qrz_logbook
from src.pota_client import POTAClient


class EnhancedLoggingTab:
    def __init__(self, parent, database, config):
        self.parent = parent
        self.database = database
        self.config = config
        self.frame = ttk.Frame(parent)
        self.qrz_session = None

        # POTA client and state
        self.pota_client = POTAClient()
        self.auto_refresh = False
        self.refresh_interval = 60
        self.current_pota_spots = []

        # Time tracking for QSO
        self.time_on_captured = False  # Track if time_on has been set for current contact

        self.create_widgets()

        # Set up callsign lookup callback
        self.callsign_entry.bind('<FocusOut>', self.on_callsign_changed)
        self.callsign_entry.bind('<Return>', lambda e: self.freq_entry.focus())
        self.callsign_entry.bind('<KeyRelease>', self.on_callsign_keypress)

        # Set up frequency/band correlation
        self.freq_entry.bind('<FocusOut>', self.on_frequency_changed)

        # Start the UTC clock
        self.update_clock()

        # Focus on callsign field
        self.callsign_entry.focus()

        # Do initial POTA fetch
        self.refresh_pota_spots()

        # Start auto-refresh if it was enabled
        if self.auto_refresh:
            self.auto_refresh_timer()

    def create_widgets(self):
        """Create the enhanced logging interface"""

        # Top section - QSO Entry
        entry_frame = ttk.LabelFrame(self.frame, text="New Contact", padding=10)
        entry_frame.pack(fill='x', padx=10, pady=5)

        # UTC Clock Display
        clock_frame = ttk.Frame(entry_frame)
        clock_frame.pack(fill='x', pady=(0, 10))

        ttk.Label(clock_frame, text="UTC Time:", font=('TkDefaultFont', 10)).pack(side='left')
        self.clock_label = ttk.Label(clock_frame, text="--:--:--",
                                     font=('TkDefaultFont', 16, 'bold'),
                                     foreground='#1976d2')
        self.clock_label.pack(side='left', padx=10)

        ttk.Label(clock_frame, text="(Start time captured when callsign entered)",
                 font=('TkDefaultFont', 8), foreground='gray').pack(side='left', padx=10)

        # Row 1: Callsign, Frequency, Mode
        row1 = ttk.Frame(entry_frame)
        row1.pack(fill='x', pady=2)

        ttk.Label(row1, text="Callsign:", width=12, anchor='e').pack(side='left')
        self.callsign_var = tk.StringVar()
        self.callsign_entry = ttk.Entry(row1, textvariable=self.callsign_var, width=15, font=('', 12, 'bold'))
        self.callsign_entry.pack(side='left', padx=5)

        self.lookup_btn = ttk.Button(row1, text="Lookup", command=self.lookup_callsign, width=8)
        self.lookup_btn.pack(side='left', padx=2)

        ttk.Label(row1, text="Frequency:", width=10, anchor='e').pack(side='left', padx=(20, 0))
        self.freq_var = tk.StringVar()
        self.freq_entry = ttk.Entry(row1, textvariable=self.freq_var, width=12)
        self.freq_entry.pack(side='left', padx=5)

        ttk.Label(row1, text="Band:", width=6, anchor='e').pack(side='left', padx=(10, 0))
        self.band_var = tk.StringVar()
        band_combo = ttk.Combobox(row1, textvariable=self.band_var, width=8, state='readonly')
        band_combo['values'] = ('160m', '80m', '60m', '40m', '30m', '20m', '17m', '15m',
                                '12m', '10m', '6m', '2m', '70cm')
        band_combo.pack(side='left', padx=5)

        ttk.Label(row1, text="Mode:", width=6, anchor='e').pack(side='left', padx=(10, 0))
        self.mode_var = tk.StringVar()
        mode_combo = ttk.Combobox(row1, textvariable=self.mode_var, width=10)
        mode_combo['values'] = ('SSB', 'CW', 'FT8', 'FT4', 'RTTY', 'PSK31', 'PSK63',
                               'MFSK', 'JT65', 'JT9', 'AM', 'FM', 'DATA')
        mode_combo.pack(side='left', padx=5)

        # Row 2: Date, Time ON, Time OFF, Power, RST
        row2 = ttk.Frame(entry_frame)
        row2.pack(fill='x', pady=2)

        ttk.Label(row2, text="Date:", width=12, anchor='e').pack(side='left')
        self.date_var = tk.StringVar(value=datetime.utcnow().strftime("%Y-%m-%d"))
        ttk.Entry(row2, textvariable=self.date_var, width=12).pack(side='left', padx=5)

        ttk.Label(row2, text="Time ON:", width=10, anchor='e').pack(side='left', padx=(20, 0))
        self.time_on_var = tk.StringVar()  # No default - captured when callsign entered
        self.time_on_entry = ttk.Entry(row2, textvariable=self.time_on_var, width=8,
                                       state='readonly')
        self.time_on_entry.pack(side='left', padx=5)

        ttk.Label(row2, text="Time OFF:", width=10, anchor='e').pack(side='left', padx=(10, 0))
        self.time_off_var = tk.StringVar()  # Captured when contact logged
        self.time_off_entry = ttk.Entry(row2, textvariable=self.time_off_var, width=8,
                                        state='readonly')
        self.time_off_entry.pack(side='left', padx=5)

        ttk.Label(row2, text="Power:", width=6, anchor='e').pack(side='left', padx=(10, 0))
        self.power_var = tk.StringVar(value=self.config.get('default_power', '100'))
        ttk.Entry(row2, textvariable=self.power_var, width=8).pack(side='left', padx=5)
        ttk.Label(row2, text="W").pack(side='left')

        ttk.Label(row2, text="RST Sent:", width=10, anchor='e').pack(side='left', padx=(10, 0))
        self.rst_sent_var = tk.StringVar(value=self.config.get('default_rst', '59'))
        ttk.Entry(row2, textvariable=self.rst_sent_var, width=6).pack(side='left', padx=5)

        ttk.Label(row2, text="RST Rcvd:", width=10, anchor='e').pack(side='left', padx=(10, 0))
        self.rst_rcvd_var = tk.StringVar(value=self.config.get('default_rst', '59'))
        ttk.Entry(row2, textvariable=self.rst_rcvd_var, width=6).pack(side='left', padx=5)

        # Row 3: Name, QTH, Grid
        row3 = ttk.Frame(entry_frame)
        row3.pack(fill='x', pady=2)

        ttk.Label(row3, text="Name:", width=12, anchor='e').pack(side='left')
        self.name_var = tk.StringVar()
        ttk.Entry(row3, textvariable=self.name_var, width=20).pack(side='left', padx=5)

        ttk.Label(row3, text="QTH:", width=10, anchor='e').pack(side='left', padx=(20, 0))
        self.qth_var = tk.StringVar()
        ttk.Entry(row3, textvariable=self.qth_var, width=25).pack(side='left', padx=5)

        ttk.Label(row3, text="Grid:", width=6, anchor='e').pack(side='left', padx=(10, 0))
        self.grid_var = tk.StringVar()
        ttk.Entry(row3, textvariable=self.grid_var, width=10).pack(side='left', padx=5)

        # Row 4: Country, State, County
        row4 = ttk.Frame(entry_frame)
        row4.pack(fill='x', pady=2)

        ttk.Label(row4, text="Country:", width=12, anchor='e').pack(side='left')
        self.country_var = tk.StringVar()
        self.country_entry = ttk.Entry(row4, textvariable=self.country_var, width=20, state='readonly')
        self.country_entry.pack(side='left', padx=5)

        ttk.Label(row4, text="State:", width=10, anchor='e').pack(side='left', padx=(20, 0))
        self.state_var = tk.StringVar()
        ttk.Entry(row4, textvariable=self.state_var, width=8).pack(side='left', padx=5)

        ttk.Label(row4, text="County:", width=8, anchor='e').pack(side='left', padx=(10, 0))
        self.county_var = tk.StringVar()
        ttk.Entry(row4, textvariable=self.county_var, width=20).pack(side='left', padx=5)

        # Row 5: Continent, CQ Zone, ITU Zone
        row5 = ttk.Frame(entry_frame)
        row5.pack(fill='x', pady=2)

        ttk.Label(row5, text="Continent:", width=12, anchor='e').pack(side='left')
        self.continent_var = tk.StringVar()
        ttk.Entry(row5, textvariable=self.continent_var, width=8, state='readonly').pack(side='left', padx=5)

        ttk.Label(row5, text="CQ Zone:", width=10, anchor='e').pack(side='left', padx=(20, 0))
        self.cq_zone_var = tk.StringVar()
        ttk.Entry(row5, textvariable=self.cq_zone_var, width=6).pack(side='left', padx=5)

        ttk.Label(row5, text="ITU Zone:", width=10, anchor='e').pack(side='left', padx=(10, 0))
        self.itu_zone_var = tk.StringVar()
        ttk.Entry(row5, textvariable=self.itu_zone_var, width=6).pack(side='left', padx=5)

        ttk.Label(row5, text="IOTA:", width=6, anchor='e').pack(side='left', padx=(10, 0))
        self.iota_var = tk.StringVar()
        ttk.Entry(row5, textvariable=self.iota_var, width=12).pack(side='left', padx=5)

        ttk.Label(row5, text="SOTA:", width=6, anchor='e').pack(side='left', padx=(10, 0))
        self.sota_var = tk.StringVar()
        ttk.Entry(row5, textvariable=self.sota_var, width=12).pack(side='left', padx=5)

        ttk.Label(row5, text="POTA:", width=6, anchor='e').pack(side='left', padx=(10, 0))
        self.pota_var = tk.StringVar()
        ttk.Entry(row5, textvariable=self.pota_var, width=12).pack(side='left', padx=5)

        # Row 6: Notes/Comments
        row6 = ttk.Frame(entry_frame)
        row6.pack(fill='x', pady=2)

        ttk.Label(row6, text="Notes:", width=12, anchor='e').pack(side='left')
        self.notes_var = tk.StringVar()
        ttk.Entry(row6, textvariable=self.notes_var, width=80).pack(side='left', padx=5, fill='x', expand=True)

        # Button row
        btn_row = ttk.Frame(entry_frame)
        btn_row.pack(fill='x', pady=10)

        self.log_btn = ttk.Button(btn_row, text="Log Contact (Enter)", command=self.log_contact,
                                  style='Accent.TButton')
        self.log_btn.pack(side='left', padx=5)

        ttk.Button(btn_row, text="Clear (Esc)", command=self.clear_form).pack(side='left', padx=5)

        if self.config.get('qrz.api_key'):
            self.qrz_upload_btn = ttk.Button(btn_row, text="Upload to QRZ",
                                            command=self.upload_to_qrz, state='disabled')
            self.qrz_upload_btn.pack(side='left', padx=5)

        self.dupe_label = ttk.Label(btn_row, text="", foreground="red", font=('', 10, 'bold'))
        self.dupe_label.pack(side='left', padx=20)

        # Keyboard shortcuts
        self.frame.bind_all('<Control-Return>', lambda e: self.log_contact())
        self.frame.bind_all('<Escape>', lambda e: self.clear_form())

        # Spots Display - DX and POTA side by side
        self.create_spots_display()

    def create_spots_display(self):
        """Create combined DX and POTA spots display"""
        # Create a PanedWindow for resizable split
        paned = ttk.PanedWindow(self.frame, orient='horizontal')
        paned.pack(fill='both', expand=True, padx=10, pady=5)

        # LEFT PANEL - DX CLUSTER SPOTS
        dx_panel = ttk.Frame(paned)
        paned.add(dx_panel, weight=1)

        # DX Spots header
        dx_header = ttk.LabelFrame(dx_panel, text="DX Cluster Spots", padding=5)
        dx_header.pack(fill='x', padx=5, pady=5)

        dx_info = ttk.Label(dx_header,
                           text="Connect to a DX Cluster in the 'DX Clusters' tab to see spots here",
                           foreground="blue")
        dx_info.pack()

        # DX Spots display
        dx_spots_frame = ttk.Frame(dx_panel)
        dx_spots_frame.pack(fill='both', expand=True, padx=5, pady=5)

        # Create treeview for DX spots
        dx_columns = ('Callsign', 'Country', 'Mode', 'Band', 'Frequency', 'Comment')
        self.dx_spots_tree = ttk.Treeview(dx_spots_frame, columns=dx_columns,
                                         show='headings', height=15)

        for col in dx_columns:
            self.dx_spots_tree.heading(col, text=col)

        self.dx_spots_tree.column('Callsign', width=90)
        self.dx_spots_tree.column('Country', width=130)
        self.dx_spots_tree.column('Mode', width=50)
        self.dx_spots_tree.column('Band', width=50)
        self.dx_spots_tree.column('Frequency', width=80)
        self.dx_spots_tree.column('Comment', width=200)

        # DX Scrollbars
        dx_vsb = ttk.Scrollbar(dx_spots_frame, orient='vertical',
                              command=self.dx_spots_tree.yview)
        dx_hsb = ttk.Scrollbar(dx_spots_frame, orient='horizontal',
                              command=self.dx_spots_tree.xview)
        self.dx_spots_tree.configure(yscrollcommand=dx_vsb.set, xscrollcommand=dx_hsb.set)

        self.dx_spots_tree.grid(row=0, column=0, sticky='nsew')
        dx_vsb.grid(row=0, column=1, sticky='ns')
        dx_hsb.grid(row=1, column=0, sticky='ew')

        dx_spots_frame.grid_rowconfigure(0, weight=1)
        dx_spots_frame.grid_columnconfigure(0, weight=1)

        # Double-click to populate entry form
        self.dx_spots_tree.bind('<Double-1>', self.on_dx_spot_double_click)

        # RIGHT PANEL - POTA SPOTS
        pota_panel = ttk.Frame(paned)
        paned.add(pota_panel, weight=1)

        # POTA Control frame
        pota_control = ttk.LabelFrame(pota_panel, text="POTA Spots Control", padding=5)
        pota_control.pack(fill='x', padx=5, pady=5)

        # Refresh controls
        refresh_row = ttk.Frame(pota_control)
        refresh_row.pack(fill='x', pady=2)

        ttk.Button(refresh_row, text="Refresh",
                  command=self.refresh_pota_spots_async).pack(side='left', padx=5)

        # Load saved auto-refresh state
        saved_auto = self.config.get('pota_filter.auto_refresh', False)
        self.auto_refresh_var = tk.BooleanVar(value=saved_auto)
        self.auto_refresh = saved_auto
        ttk.Checkbutton(refresh_row, text="Auto",
                       variable=self.auto_refresh_var,
                       command=self.toggle_auto_refresh).pack(side='left', padx=5)

        # Load saved refresh interval
        saved_interval = self.config.get('pota_filter.refresh_interval', 60)
        self.refresh_interval_var = tk.IntVar(value=saved_interval)
        self.refresh_interval = saved_interval
        ttk.Spinbox(refresh_row, from_=30, to=300, increment=30,
                   textvariable=self.refresh_interval_var, width=6).pack(side='left')
        ttk.Label(refresh_row, text="sec").pack(side='left', padx=2)

        self.pota_status_label = ttk.Label(refresh_row, text="Ready", foreground="blue")
        self.pota_status_label.pack(side='left', padx=10)

        # POTA Filters
        pota_filter = ttk.LabelFrame(pota_panel, text="POTA Filters", padding=5)
        pota_filter.pack(fill='x', padx=5, pady=5)

        # Band filters (compact)
        band_row = ttk.Frame(pota_filter)
        band_row.pack(fill='x', pady=2)

        ttk.Label(band_row, text="Bands:").pack(side='left', padx=2)

        self.pota_band_filters = {}
        bands = ['160m', '80m', '40m', '30m', '20m', '17m', '15m', '12m', '10m', '6m']
        for band in bands:
            # Load saved filter state or default to True
            saved_state = self.config.get(f'pota_filter.band.{band}', True)
            var = tk.BooleanVar(value=saved_state)
            self.pota_band_filters[band] = var
            ttk.Checkbutton(band_row, text=band, variable=var,
                           command=self.save_and_apply_pota_filters).pack(side='left', padx=1)

        # Mode filters (compact)
        mode_row = ttk.Frame(pota_filter)
        mode_row.pack(fill='x', pady=2)

        ttk.Label(mode_row, text="Modes:").pack(side='left', padx=2)

        self.pota_mode_filters = {}
        modes = ['CW', 'SSB', 'FM', 'FT8', 'FT4', 'DIGI']
        for mode in modes:
            # Load saved filter state or default to True
            saved_state = self.config.get(f'pota_filter.mode.{mode}', True)
            var = tk.BooleanVar(value=saved_state)
            self.pota_mode_filters[mode] = var
            ttk.Checkbutton(mode_row, text=mode, variable=var,
                           command=self.save_and_apply_pota_filters).pack(side='left', padx=1)

        # Location filter
        loc_row = ttk.Frame(pota_filter)
        loc_row.pack(fill='x', pady=2)

        ttk.Label(loc_row, text="Location:").pack(side='left', padx=2)
        # Load saved location filter
        saved_location = self.config.get('pota_filter.location', '')
        self.location_filter_var = tk.StringVar(value=saved_location)
        self.location_filter_var.trace('w', lambda *args: self.save_and_apply_pota_filters())
        ttk.Entry(loc_row, textvariable=self.location_filter_var, width=15).pack(side='left', padx=2)

        # POTA Spots display
        pota_spots_frame = ttk.Frame(pota_panel)
        pota_spots_frame.pack(fill='both', expand=True, padx=5, pady=5)

        # Create treeview for POTA spots (compact columns)
        pota_columns = ('Activator', 'Park', 'Location', 'Freq', 'Mode', 'Band', 'Time', 'QSOs')
        self.pota_spots_tree = ttk.Treeview(pota_spots_frame, columns=pota_columns,
                                           show='headings', height=15)

        self.pota_spots_tree.heading('Activator', text='Activator')
        self.pota_spots_tree.heading('Park', text='Park Ref')
        self.pota_spots_tree.heading('Location', text='Loc')
        self.pota_spots_tree.heading('Freq', text='Frequency')
        self.pota_spots_tree.heading('Mode', text='Mode')
        self.pota_spots_tree.heading('Band', text='Band')
        self.pota_spots_tree.heading('Time', text='Time')
        self.pota_spots_tree.heading('QSOs', text='QSOs')

        self.pota_spots_tree.column('Activator', width=90)
        self.pota_spots_tree.column('Park', width=90)
        self.pota_spots_tree.column('Location', width=60)
        self.pota_spots_tree.column('Freq', width=80)
        self.pota_spots_tree.column('Mode', width=50)
        self.pota_spots_tree.column('Band', width=50)
        self.pota_spots_tree.column('Time', width=70)
        self.pota_spots_tree.column('QSOs', width=40)

        # POTA Scrollbars
        pota_vsb = ttk.Scrollbar(pota_spots_frame, orient='vertical',
                                command=self.pota_spots_tree.yview)
        pota_hsb = ttk.Scrollbar(pota_spots_frame, orient='horizontal',
                                command=self.pota_spots_tree.xview)
        self.pota_spots_tree.configure(yscrollcommand=pota_vsb.set, xscrollcommand=pota_hsb.set)

        self.pota_spots_tree.grid(row=0, column=0, sticky='nsew')
        pota_vsb.grid(row=0, column=1, sticky='ns')
        pota_hsb.grid(row=1, column=0, sticky='ew')

        pota_spots_frame.grid_rowconfigure(0, weight=1)
        pota_spots_frame.grid_columnconfigure(0, weight=1)

        # Double-click to populate form
        self.pota_spots_tree.bind('<Double-1>', self.on_pota_spot_double_click)

    def update_clock(self):
        """Update the UTC clock display every second"""
        now = datetime.utcnow()
        self.clock_label.config(text=now.strftime("%H:%M:%S"))
        # Schedule next update in 1 second
        self.frame.after(1000, self.update_clock)

    def on_callsign_keypress(self, event=None):
        """Capture time_on when first character is entered in callsign field"""
        callsign = self.callsign_var.get().strip()

        # If callsign has content and time_on hasn't been captured yet
        if callsign and not self.time_on_captured:
            current_time = datetime.utcnow().strftime("%H:%M")
            self.time_on_var.set(current_time)
            self.time_on_captured = True
            print(f"Time ON captured: {current_time}")

    def on_callsign_changed(self, event=None):
        """Handle callsign field change - auto lookup if enabled"""
        callsign = self.callsign_var.get().strip().upper()

        if not callsign:
            return

        self.callsign_var.set(callsign)

        # Check for duplicates if enabled
        if self.config.get('logging.warn_duplicates', True):
            self.check_duplicate()

        # Auto-lookup if enabled
        if self.config.get('logging.auto_lookup', True):
            self.lookup_callsign(auto=True)

    def check_duplicate(self):
        """Check if this is a duplicate contact"""
        callsign = self.callsign_var.get().strip().upper()
        band = self.band_var.get()
        mode = self.mode_var.get()
        date = self.date_var.get()

        if not all([callsign, band, mode, date]):
            self.dupe_label.config(text="")
            return

        dupe = self.database.check_duplicate(callsign, band, mode, date)

        if dupe:
            self.dupe_label.config(text=f"⚠️ DUPLICATE - Worked on {dupe['time_on']}")
        else:
            self.dupe_label.config(text="")

    def on_frequency_changed(self, event=None):
        """Auto-select band when frequency is entered"""
        try:
            freq_str = self.freq_var.get().strip()
            if not freq_str:
                return

            freq = float(freq_str)

            # Map frequency to band
            if 1.8 <= freq < 2.0:
                self.band_var.set('160m')
            elif 3.5 <= freq < 4.0:
                self.band_var.set('80m')
            elif 5.0 <= freq < 5.5:
                self.band_var.set('60m')
            elif 7.0 <= freq < 7.3:
                self.band_var.set('40m')
            elif 10.1 <= freq < 10.15:
                self.band_var.set('30m')
            elif 14.0 <= freq < 14.35:
                self.band_var.set('20m')
            elif 18.068 <= freq < 18.168:
                self.band_var.set('17m')
            elif 21.0 <= freq < 21.45:
                self.band_var.set('15m')
            elif 24.89 <= freq < 24.99:
                self.band_var.set('12m')
            elif 28.0 <= freq < 29.7:
                self.band_var.set('10m')
            elif 50.0 <= freq < 54.0:
                self.band_var.set('6m')
            elif 144.0 <= freq < 148.0:
                self.band_var.set('2m')
            elif 420.0 <= freq < 450.0:
                self.band_var.set('70cm')

            # Check for duplicates after band is set
            if self.config.get('logging.warn_duplicates', True):
                self.check_duplicate()

        except ValueError:
            pass

    def lookup_callsign(self, auto=False):
        """Lookup callsign using QRZ and DXCC"""
        callsign = self.callsign_var.get().strip().upper()

        if not callsign:
            if not auto:
                messagebox.showwarning("Missing Callsign", "Please enter a callsign")
            return

        # First try DXCC lookup (always available)
        dxcc_info = lookup_dxcc(callsign)
        if dxcc_info:
            self.country_var.set(dxcc_info['country'])
            self.continent_var.set(dxcc_info['continent'])
            self.cq_zone_var.set(str(dxcc_info['cq_zone']))
            self.itu_zone_var.set(str(dxcc_info['itu_zone']))

        # Then try QRZ lookup if enabled and configured
        if not self.config.get('qrz.enable_lookup', False):
            return

        qrz_user = self.config.get('qrz.username')
        qrz_pass = self.config.get('qrz.password')

        if not qrz_user or not qrz_pass:
            if not auto:
                # Provide specific feedback about what's missing
                missing_items = []
                if not qrz_user:
                    missing_items.append("Username")
                if not qrz_pass:
                    missing_items.append("Password")

                missing_text = " and ".join(missing_items)
                messagebox.showinfo("QRZ Not Configured",
                                   f"QRZ {missing_text} not configured.\n\n"
                                   "Please go to Settings tab and enter your QRZ credentials,\n"
                                   "then click 'Save Settings' to enable lookups.\n\n"
                                   "Note: QRZ XML lookups require a separate XML Data subscription.")
            return

        # Create session if needed
        if not self.qrz_session:
            self.qrz_session = QRZSession(qrz_user, qrz_pass)

        # Lookup callsign
        try:
            data = self.qrz_session.lookup_callsign(callsign)

            if data:
                # Populate fields from QRZ data
                if 'name' in data and data['name']:
                    # Combine first and last name
                    name = data.get('first_name', '') + ' ' + data.get('name', '')
                    self.name_var.set(name.strip())

                if 'gridsquare' in data:
                    self.grid_var.set(data['gridsquare'])

                if 'state' in data:
                    self.state_var.set(data['state'])

                if 'county' in data:
                    self.county_var.set(data['county'])

                # QRZ data overrides DXCC for zones if available
                if 'cq_zone' in data:
                    self.cq_zone_var.set(data['cq_zone'])

                if 'itu_zone' in data:
                    self.itu_zone_var.set(data['itu_zone'])

                if not auto:
                    messagebox.showinfo("Lookup Successful", f"Found {callsign} on QRZ")
            else:
                if not auto:
                    messagebox.showinfo("Not Found", f"{callsign} not found on QRZ")

        except Exception as e:
            if not auto:
                messagebox.showerror("Lookup Error", f"Error looking up callsign: {str(e)}")

    def log_contact(self):
        """Save contact to database"""
        callsign = self.callsign_var.get().strip().upper()
        if not callsign:
            messagebox.showwarning("Missing Data", "Callsign is required")
            self.callsign_entry.focus()
            return

        # Capture time_off when logging contact
        current_time = datetime.utcnow().strftime("%H:%M")
        self.time_off_var.set(current_time)
        print(f"Time OFF captured: {current_time}")

        contact_data = {
            'callsign': callsign,
            'date': self.date_var.get(),
            'time_on': self.time_on_var.get(),
            'time_off': self.time_off_var.get(),
            'frequency': self.freq_var.get(),
            'band': self.band_var.get(),
            'mode': self.mode_var.get(),
            'rst_sent': self.rst_sent_var.get(),
            'rst_rcvd': self.rst_rcvd_var.get(),
            'power': self.power_var.get(),
            'name': self.name_var.get(),
            'qth': self.qth_var.get(),
            'gridsquare': self.grid_var.get(),
            'county': self.county_var.get(),
            'state': self.state_var.get(),
            'country': self.country_var.get(),
            'continent': self.continent_var.get(),
            'cq_zone': self.cq_zone_var.get(),
            'itu_zone': self.itu_zone_var.get(),
            'iota': self.iota_var.get(),
            'sota': self.sota_var.get(),
            'pota': self.pota_var.get(),
            'my_gridsquare': self.config.get('gridsquare', ''),
            'notes': self.notes_var.get()
        }

        try:
            contact_id = self.database.add_contact(contact_data)

            # Auto-upload to QRZ if enabled
            if self.config.get('qrz.auto_upload', False):
                self.upload_to_qrz(contact_data)
            else:
                messagebox.showinfo("Success", f"Contact with {callsign} logged!")

            self.clear_form()

            # Enable manual QRZ upload button if configured
            if hasattr(self, 'qrz_upload_btn'):
                self.qrz_upload_btn.config(state='normal')
                self.last_contact_data = contact_data

        except Exception as e:
            messagebox.showerror("Error", f"Failed to log contact: {str(e)}")

    def upload_to_qrz(self, contact_data=None):
        """Upload contact to QRZ Logbook"""
        api_key = self.config.get('qrz.api_key')

        if not api_key:
            messagebox.showwarning("QRZ Not Configured",
                                 "QRZ API Key not configured.\n\n"
                                 "Please go to Settings tab and enter your QRZ API key,\n"
                                 "then click 'Save Settings' to enable QRZ Logbook uploads.\n\n"
                                 "Get your API key from: https://www.qrz.com/page/current_spec.html")
            return

        if contact_data is None:
            contact_data = getattr(self, 'last_contact_data', None)

        if not contact_data:
            messagebox.showwarning("No Contact", "No contact to upload")
            return

        try:
            success, message = upload_to_qrz_logbook(api_key, contact_data)

            if success:
                messagebox.showinfo("QRZ Upload Successful", message)
                if hasattr(self, 'qrz_upload_btn'):
                    self.qrz_upload_btn.config(state='disabled')
            else:
                messagebox.showerror("QRZ Upload Failed", message)

        except Exception as e:
            messagebox.showerror("Upload Error", f"Error uploading to QRZ: {str(e)}")

    def clear_form(self):
        """Clear all input fields"""
        self.callsign_var.set('')
        self.date_var.set(datetime.utcnow().strftime("%Y-%m-%d"))
        self.time_on_var.set('')  # Clear time_on (will be captured on next callsign entry)
        self.time_off_var.set('')  # Clear time_off
        self.time_on_captured = False  # Reset flag for next contact
        self.freq_var.set('')
        self.band_var.set('')
        self.mode_var.set('')
        self.rst_sent_var.set(self.config.get('default_rst', '59'))
        self.rst_rcvd_var.set(self.config.get('default_rst', '59'))
        self.power_var.set(self.config.get('default_power', '100'))
        self.name_var.set('')
        self.qth_var.set('')
        self.grid_var.set('')
        self.county_var.set('')
        self.state_var.set('')
        self.country_var.set('')
        self.continent_var.set('')
        self.cq_zone_var.set('')
        self.itu_zone_var.set('')
        self.iota_var.set('')
        self.sota_var.set('')
        self.pota_var.set('')
        self.notes_var.set('')
        self.dupe_label.config(text='')
        self.callsign_entry.focus()

        if hasattr(self, 'qrz_upload_btn'):
            self.qrz_upload_btn.config(state='disabled')

    # DX SPOTS METHODS
    def add_dx_spot(self, spot_data):
        """Add a DX spot to the display (called from DX cluster tab)"""
        self.dx_spots_tree.insert('', 0, values=(
            spot_data.get('callsign', ''),
            spot_data.get('country', ''),
            spot_data.get('mode', ''),
            spot_data.get('band', ''),
            spot_data.get('frequency', ''),
            spot_data.get('comment', '')
        ))

        # Keep only the most recent 100 spots
        children = self.dx_spots_tree.get_children()
        if len(children) > 100:
            self.dx_spots_tree.delete(children[-1])

    def on_dx_spot_double_click(self, event):
        """Handle double-click on DX spot - populate entry form"""
        selection = self.dx_spots_tree.selection()
        if not selection:
            return

        item = self.dx_spots_tree.item(selection[0])
        values = item['values']

        if len(values) >= 6:
            callsign = values[0]
            mode = values[2]
            band = values[3]
            frequency = values[4]
            comment = values[5]

            # Populate the logging form
            self.callsign_var.set(callsign)
            self.freq_var.set(frequency)
            self.mode_var.set(mode)
            self.band_var.set(band)

            # Add comment to notes if present
            if comment:
                current_notes = self.notes_var.get()
                if current_notes:
                    self.notes_var.set(f"{current_notes} | DX: {comment}")
                else:
                    self.notes_var.set(f"DX: {comment}")

            # Trigger callsign lookup (QRZ)
            self.on_callsign_changed()

            # Focus on callsign field
            self.callsign_entry.focus()

    # POTA SPOTS METHODS
    def refresh_pota_spots_async(self):
        """Refresh POTA spots in background thread"""
        self.pota_status_label.config(text="Fetching...", foreground="orange")
        thread = threading.Thread(target=self.refresh_pota_spots, daemon=True)
        thread.start()

    def refresh_pota_spots(self):
        """Fetch spots from POTA API"""
        try:
            spots = self.pota_client.get_spots()
            self.current_pota_spots = spots

            # Update UI in main thread
            self.parent.after(0, self._update_pota_spots_display)
            self.parent.after(0, lambda: self.pota_status_label.config(
                text=f"{len(spots)} spots - {datetime.now().strftime('%H:%M:%S')}",
                foreground="green"))
        except Exception as e:
            self.parent.after(0, lambda: self.pota_status_label.config(
                text=f"Error", foreground="red"))

    def _update_pota_spots_display(self):
        """Update POTA spots display with filtered spots"""
        # Clear existing items
        for item in self.pota_spots_tree.get_children():
            self.pota_spots_tree.delete(item)

        # Apply filters and add spots
        for spot in self.current_pota_spots:
            if self.pota_spot_passes_filters(spot):
                # Format time
                spot_time = spot.get('spot_time', '')
                if 'T' in spot_time:
                    try:
                        dt = datetime.fromisoformat(spot_time.replace('Z', '+00:00'))
                        spot_time = dt.strftime('%H:%M')
                    except:
                        pass

                self.pota_spots_tree.insert('', 'end', values=(
                    spot.get('activator', ''),
                    spot.get('park_ref', ''),
                    spot.get('location', ''),
                    spot.get('frequency', ''),
                    spot.get('mode', ''),
                    spot.get('band', ''),
                    spot_time,
                    spot.get('qso_count', 0)
                ))

    def pota_spot_passes_filters(self, spot):
        """Check if POTA spot passes current filters"""
        # Band filter
        band = spot.get('band', '')
        if band and band in self.pota_band_filters:
            if not self.pota_band_filters[band].get():
                return False

        # Mode filter
        mode = spot.get('mode', '').upper()
        mode_map = {
            'SSB': 'SSB', 'USB': 'SSB', 'LSB': 'SSB',
            'CW': 'CW',
            'FM': 'FM',
            'FT8': 'FT8',
            'FT4': 'FT4',
            'DIGITAL': 'DIGI', 'DATA': 'DIGI'
        }
        mode_category = mode_map.get(mode, mode)

        if mode_category and mode_category in self.pota_mode_filters:
            if not self.pota_mode_filters[mode_category].get():
                return False

        # Location filter
        location_filter = self.location_filter_var.get().upper().strip()
        if location_filter:
            location = spot.get('location', '').upper()
            park_ref = spot.get('park_ref', '').upper()
            if location_filter not in location and location_filter not in park_ref:
                return False

        return True

    def save_and_apply_pota_filters(self):
        """Save POTA filter states and apply filters"""
        # Save band filters
        for band, var in self.pota_band_filters.items():
            self.config.set(f'pota_filter.band.{band}', var.get())

        # Save mode filters
        for mode, var in self.pota_mode_filters.items():
            self.config.set(f'pota_filter.mode.{mode}', var.get())

        # Save location filter
        self.config.set('pota_filter.location', self.location_filter_var.get())

        self.apply_pota_filters()

    def apply_pota_filters(self):
        """Apply current POTA filters"""
        self._update_pota_spots_display()

    def toggle_auto_refresh(self):
        """Toggle POTA auto-refresh"""
        self.auto_refresh = self.auto_refresh_var.get()
        # Save auto-refresh state
        self.config.set('pota_filter.auto_refresh', self.auto_refresh)
        # Save refresh interval
        self.refresh_interval = self.refresh_interval_var.get()
        self.config.set('pota_filter.refresh_interval', self.refresh_interval)
        if self.auto_refresh:
            self.auto_refresh_timer()

    def auto_refresh_timer(self):
        """Timer for POTA auto-refresh"""
        if self.auto_refresh:
            self.refresh_pota_spots_async()
            interval = self.refresh_interval_var.get() * 1000
            self.parent.after(interval, self.auto_refresh_timer)

    def on_pota_spot_double_click(self, event):
        """Handle double-click on POTA spot - populate entry form"""
        selection = self.pota_spots_tree.selection()
        if not selection:
            return

        item = self.pota_spots_tree.item(selection[0])
        values = item['values']

        if len(values) >= 8:
            activator = values[0]
            park_ref = values[1]
            location = values[2]
            frequency = values[3]
            mode = values[4]
            band = values[5]
            time = values[6]
            qsos = values[7]

            # Find full spot details for park name
            park_name = ""
            for spot in self.current_pota_spots:
                if (spot.get('activator') == activator and
                    spot.get('park_ref') == park_ref):
                    park_name = spot.get('park_name', '')
                    break

            # Populate the logging form
            self.callsign_var.set(activator)
            self.freq_var.set(frequency)
            self.mode_var.set(mode)
            self.band_var.set(band)

            # Add POTA reference and park name to POTA field and notes
            self.pota_var.set(park_ref)

            # Build descriptive note
            pota_note = f"POTA: {park_ref}"
            if park_name:
                pota_note += f" ({park_name})"
            self.notes_var.set(pota_note)

            # Trigger callsign lookup (QRZ)
            self.on_callsign_changed()

            # Focus on callsign field
            self.callsign_entry.focus()

    def get_frame(self):
        """Return the frame widget"""
        return self.frame
