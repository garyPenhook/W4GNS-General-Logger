"""
DX Cluster Tab - Cluster connection and spot monitoring
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import time
from src.dx_clusters import DX_CLUSTERS, get_cluster_by_callsign
from src.dx_client import DXClusterClient
from src.dxcc import get_continent_from_callsign, get_country_from_callsign


class DXClusterTab:
    def __init__(self, parent, database, config):
        self.parent = parent
        self.database = database
        self.config = config
        self.frame = ttk.Frame(parent)
        self.client = None

        # Rate limiting for spots
        self.spot_queue = []
        self.last_spot_time = 0
        self.min_spot_interval = 0.5  # Minimum 0.5 seconds between spot displays

        # Duplicate filtering - track recent spots
        self.recent_spots = {}  # {callsign: timestamp}
        self.duplicate_window = 180  # 3 minutes in seconds

        self.create_widgets()
        self.update_timer()

    def create_widgets(self):
        """Create the DX cluster interface"""

        # Top control frame
        control_frame = ttk.LabelFrame(self.frame, text="Cluster Connection", padding=10)
        control_frame.pack(fill='x', padx=10, pady=5)

        # Cluster selection
        select_row = ttk.Frame(control_frame)
        select_row.pack(fill='x', pady=5)

        ttk.Label(select_row, text="Select Cluster:").pack(side='left')

        self.cluster_var = tk.StringVar()
        cluster_names = [f"{c['callsign']} - {c['location']}" for c in DX_CLUSTERS]
        self.cluster_combo = ttk.Combobox(select_row, textvariable=self.cluster_var,
                                          values=cluster_names, width=40, state='readonly')
        self.cluster_combo.pack(side='left', padx=5)

        # Set default from config
        default_cluster = self.config.get('dx_cluster.selected', 'W3LPL')
        for i, cluster in enumerate(DX_CLUSTERS):
            if cluster['callsign'] == default_cluster:
                self.cluster_combo.current(i)
                break

        # Connection info
        info_row = ttk.Frame(control_frame)
        info_row.pack(fill='x', pady=5)

        ttk.Label(info_row, text="Your Callsign:").pack(side='left')
        self.user_callsign_var = tk.StringVar(value=self.config.get('callsign', ''))
        ttk.Entry(info_row, textvariable=self.user_callsign_var, width=12).pack(side='left', padx=5)

        self.connect_btn = ttk.Button(info_row, text="Connect", command=self.toggle_connection)
        self.connect_btn.pack(side='left', padx=20)

        self.status_label = ttk.Label(info_row, text="Disconnected", foreground="red")
        self.status_label.pack(side='left', padx=10)

        # Cluster info display
        info_display = ttk.Frame(control_frame)
        info_display.pack(fill='x', pady=5)

        self.cluster_info_label = ttk.Label(info_display, text="", foreground="blue")
        self.cluster_info_label.pack(side='left')
        self.update_cluster_info()

        # Bind cluster selection change
        self.cluster_combo.bind('<<ComboboxSelected>>', self.on_cluster_changed)

        # Filters frame
        filter_frame = ttk.LabelFrame(self.frame, text="Spot Filters", padding=10)
        filter_frame.pack(fill='x', padx=10, pady=5)

        # Band filters
        band_row = ttk.Frame(filter_frame)
        band_row.pack(fill='x', pady=2)

        ttk.Label(band_row, text="Bands:").pack(side='left', padx=(0, 5))

        self.band_filters = {}
        bands = ['160m', '80m', '60m', '40m', '30m', '20m', '17m', '15m', '12m', '10m', '6m', '2m']
        for band in bands:
            var = tk.BooleanVar(value=True)  # All bands enabled by default
            self.band_filters[band] = var
            ttk.Checkbutton(band_row, text=band, variable=var,
                           command=self.apply_filters).pack(side='left', padx=2)

        ttk.Button(band_row, text="All Bands",
                  command=lambda: self.toggle_all_filters(self.band_filters, True)).pack(side='left', padx=5)
        ttk.Button(band_row, text="Clear Bands",
                  command=lambda: self.toggle_all_filters(self.band_filters, False)).pack(side='left')

        # Mode filters
        mode_row = ttk.Frame(filter_frame)
        mode_row.pack(fill='x', pady=2)

        ttk.Label(mode_row, text="Modes:").pack(side='left', padx=(0, 5))

        self.mode_filters = {}
        modes = ['CW', 'SSB', 'RTTY', 'FT8', 'FT4', 'PSK', 'DIGI']
        for mode in modes:
            var = tk.BooleanVar(value=True)  # All modes enabled by default
            self.mode_filters[mode] = var
            ttk.Checkbutton(mode_row, text=mode, variable=var,
                           command=self.apply_filters).pack(side='left', padx=2)

        ttk.Button(mode_row, text="All Modes",
                  command=lambda: self.toggle_all_filters(self.mode_filters, True)).pack(side='left', padx=5)
        ttk.Button(mode_row, text="Clear Modes",
                  command=lambda: self.toggle_all_filters(self.mode_filters, False)).pack(side='left')

        # Continent filters
        continent_row = ttk.Frame(filter_frame)
        continent_row.pack(fill='x', pady=2)

        ttk.Label(continent_row, text="Continents:").pack(side='left', padx=(0, 5))

        self.continent_filters = {}
        continents = [
            ('NA', 'North America'),
            ('SA', 'South America'),
            ('EU', 'Europe'),
            ('AF', 'Africa'),
            ('AS', 'Asia'),
            ('OC', 'Oceania')
        ]
        for code, name in continents:
            var = tk.BooleanVar(value=True)  # All continents enabled by default
            self.continent_filters[code] = var
            ttk.Checkbutton(continent_row, text=code, variable=var,
                           command=self.apply_filters).pack(side='left', padx=2)

        ttk.Button(continent_row, text="All Continents",
                  command=lambda: self.toggle_all_filters(self.continent_filters, True)).pack(side='left', padx=5)
        ttk.Button(continent_row, text="Clear Continents",
                  command=lambda: self.toggle_all_filters(self.continent_filters, False)).pack(side='left')

        # Rate limiting control
        rate_row = ttk.Frame(filter_frame)
        rate_row.pack(fill='x', pady=2)

        ttk.Label(rate_row, text="Spot Display Rate:").pack(side='left', padx=(0, 5))
        ttk.Label(rate_row, text="Slow").pack(side='left')

        self.rate_limit_var = tk.DoubleVar(value=0.5)
        rate_scale = ttk.Scale(rate_row, from_=0.1, to=2.0, orient='horizontal',
                              variable=self.rate_limit_var, command=self.update_rate_limit, length=200)
        rate_scale.pack(side='left', padx=5)

        ttk.Label(rate_row, text="Fast").pack(side='left')
        self.rate_label = ttk.Label(rate_row, text="(0.5s between spots)")
        self.rate_label.pack(side='left', padx=10)

        # Duplicate filtering control
        dup_row = ttk.Frame(filter_frame)
        dup_row.pack(fill='x', pady=2)

        ttk.Label(dup_row, text="Duplicate Filter:").pack(side='left', padx=(0, 5))

        self.duplicate_filter_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(dup_row, text="Hide duplicate spots within 3 minutes",
                       variable=self.duplicate_filter_var).pack(side='left', padx=2)

        ttk.Button(dup_row, text="Clear Duplicate History",
                  command=self.clear_duplicate_history).pack(side='left', padx=20)

        # Spots display frame
        spots_frame = ttk.LabelFrame(self.frame, text="DX Spots", padding=10)
        spots_frame.pack(fill='both', expand=True, padx=10, pady=5)

        # Create treeview for spots - order: DX Call, Country, Mode, Band, Frequency, Comment
        columns = ('Callsign', 'Country', 'Mode', 'Band', 'Frequency', 'Comment')
        self.spots_tree = ttk.Treeview(spots_frame, columns=columns, show='headings', height=12)

        # Set column headings
        self.spots_tree.heading('Callsign', text='DX Call')
        self.spots_tree.heading('Country', text='Country')
        self.spots_tree.heading('Mode', text='Mode')
        self.spots_tree.heading('Band', text='Band')
        self.spots_tree.heading('Frequency', text='Frequency')
        self.spots_tree.heading('Comment', text='Comment')

        # Set column widths
        self.spots_tree.column('Callsign', width=100)
        self.spots_tree.column('Country', width=150)
        self.spots_tree.column('Mode', width=70)
        self.spots_tree.column('Band', width=60)
        self.spots_tree.column('Frequency', width=90)
        self.spots_tree.column('Comment', width=300)

        # Scrollbar for spots
        spots_scrollbar = ttk.Scrollbar(spots_frame, orient='vertical', command=self.spots_tree.yview)
        self.spots_tree.configure(yscrollcommand=spots_scrollbar.set)

        self.spots_tree.pack(side='left', fill='both', expand=True)
        spots_scrollbar.pack(side='right', fill='y')

        # Console output frame - reduced expand to ensure command input is visible
        console_frame = ttk.LabelFrame(self.frame, text="Cluster Console", padding=10)
        console_frame.pack(fill='both', expand=False, padx=10, pady=5)

        self.console_text = scrolledtext.ScrolledText(console_frame, height=8,
                                                      state='disabled', wrap='word')
        self.console_text.pack(fill='both', expand=True)

        # Command input frame - made more prominent with LabelFrame
        cmd_frame = ttk.LabelFrame(self.frame, text="Send Commands to Cluster", padding=10)
        cmd_frame.pack(fill='x', padx=10, pady=5)

        # Command entry row with dropdown (similar to Log4OM approach)
        entry_row = ttk.Frame(cmd_frame)
        entry_row.pack(fill='x', pady=(0, 5))

        ttk.Label(entry_row, text="Command:").pack(side='left')
        self.command_var = tk.StringVar()

        # Common DX cluster commands dropdown
        common_commands = [
            "SH/DX",
            "SH/DX 14000-14350",
            "SH/DX 7000-7300",
            "SH/DX 3500-4000",
            "SH/DX 21000-21450",
            "SH/DX 28000-29700",
            "SH/WWV",
            "SH/WCY",
            "SH/SUN",
            "SH/MOON",
            "SH/MUF",
            "SH/QTH <call>",
            "SH/QRZ <call>",
            "SET/DX",
            "UNSET/DX",
            "SET/WWV",
            "UNSET/WWV",
            "SET/WCY",
            "UNSET/WCY",
            "ACCEPT/SPOT <filter>",
            "REJECT/SPOT <filter>",
            "CLEAR/SPOTS",
            "SH/FILTER",
            "CLEAR/FILTER"
        ]

        # Use combobox to allow both selection and custom typing
        self.command_entry = ttk.Combobox(entry_row, textvariable=self.command_var,
                                          values=common_commands, width=40)
        self.command_entry.pack(side='left', padx=5, fill='x', expand=True)
        self.command_entry.bind('<Return>', self.send_command)

        ttk.Button(entry_row, text="Send", command=self.send_command).pack(side='left', padx=2)

        # Quick commands row - most frequently used
        quick_row = ttk.Frame(cmd_frame)
        quick_row.pack(fill='x')

        ttk.Label(quick_row, text="Quick Commands:").pack(side='left')
        ttk.Button(quick_row, text="SH/DX", command=lambda: self.quick_command("SH/DX")).pack(side='left', padx=2)
        ttk.Button(quick_row, text="SH/DX 20M", command=lambda: self.quick_command("SH/DX 14000-14350")).pack(side='left', padx=2)
        ttk.Button(quick_row, text="SH/DX 40M", command=lambda: self.quick_command("SH/DX 7000-7300")).pack(side='left', padx=2)
        ttk.Button(quick_row, text="SH/WWV", command=lambda: self.quick_command("SH/WWV")).pack(side='left', padx=2)
        ttk.Button(quick_row, text="Clear Filter", command=lambda: self.quick_command("CLEAR/FILTER")).pack(side='left', padx=2)

    def on_cluster_changed(self, event=None):
        """Handle cluster selection change"""
        self.update_cluster_info()

    def update_cluster_info(self):
        """Update the cluster information display"""
        selection = self.cluster_var.get()
        if selection:
            callsign = selection.split(' - ')[0]
            cluster = get_cluster_by_callsign(callsign)
            if cluster:
                info = f"Type: {cluster['type']} | Host: {cluster['hostname']} | Port: {cluster['port']} | Region: {cluster['region']}"
                self.cluster_info_label.config(text=info)

    def toggle_connection(self):
        """Connect or disconnect from cluster"""
        if self.client and self.client.is_connected():
            self.disconnect()
        else:
            self.connect()

    def connect(self):
        """Connect to selected cluster"""
        callsign = self.user_callsign_var.get().strip().upper()
        if not callsign:
            messagebox.showwarning("Missing Callsign", "Please enter your callsign")
            return

        selection = self.cluster_var.get()
        if not selection:
            messagebox.showwarning("No Cluster Selected", "Please select a cluster")
            return

        cluster_callsign = selection.split(' - ')[0]
        cluster = get_cluster_by_callsign(cluster_callsign)

        if not cluster:
            messagebox.showerror("Error", "Invalid cluster selection")
            return

        self.append_console(f"Connecting to {cluster['name']}...")

        try:
            self.client = DXClusterClient(cluster['hostname'], cluster['port'], callsign)
            self.client.set_spot_callback(self.on_spot_received)

            if self.client.connect():
                self.status_label.config(text="Connected", foreground="green")
                self.connect_btn.config(text="Disconnect")
                self.append_console(f"Connected to {cluster['callsign']}")

                # Save selection to config
                self.config.set('callsign', callsign)
                self.config.set('dx_cluster.selected', cluster['callsign'])
            else:
                self.append_console("Connection failed")
                messagebox.showerror("Connection Failed", "Could not connect to cluster")
        except Exception as e:
            self.append_console(f"Error: {str(e)}")
            messagebox.showerror("Error", f"Connection error: {str(e)}")

    def disconnect(self):
        """Disconnect from cluster"""
        if self.client:
            self.client.disconnect()
            self.client = None

        self.status_label.config(text="Disconnected", foreground="red")
        self.connect_btn.config(text="Connect")
        self.append_console("Disconnected")

    def send_command(self, event=None):
        """Send command to cluster"""
        if not self.client or not self.client.is_connected():
            messagebox.showwarning("Not Connected", "Please connect to a cluster first")
            return

        command = self.command_var.get().strip()
        if command:
            self.client.send_command(command)
            self.append_console(f"> {command}")
            self.command_var.set('')

    def quick_command(self, command):
        """Send a quick command"""
        if not self.client or not self.client.is_connected():
            messagebox.showwarning("Not Connected", "Please connect to a cluster first")
            return

        self.client.send_command(command)
        self.append_console(f"> {command}")

    def on_spot_received(self, spot):
        """Callback when a spot is received - called from client thread"""
        # Schedule UI and database updates on the main thread
        self.parent.after(0, self._process_spot, spot)

    def _process_spot(self, spot):
        """Process spot on main thread (safe for database and UI operations)"""
        # Check if spot passes filters
        if not self.spot_passes_filters(spot):
            return

        # Add to queue for rate-limited display
        self.spot_queue.append(spot)

    def _display_next_spot(self):
        """Display next spot from queue with rate limiting"""
        current_time = time.time()

        # Check if enough time has passed since last spot
        if current_time - self.last_spot_time >= self.min_spot_interval:
            if self.spot_queue:
                spot = self.spot_queue.pop(0)

                # Extract info for display
                callsign = spot.get('callsign', '')
                frequency = spot.get('frequency', '')
                comment = spot.get('comment', '')

                # Get country from callsign
                country_info = get_country_from_callsign(callsign)
                country = country_info if country_info else ''

                # Get mode from comment
                mode = self.extract_mode_from_comment(comment.upper())
                mode_display = mode if mode else ''

                # Get band from frequency
                band = self.frequency_to_band(frequency)
                band_display = band if band else ''

                # Add to treeview at the top - order: Callsign, Country, Mode, Band, Frequency, Comment
                self.spots_tree.insert('', 0, values=(
                    callsign,
                    country,
                    mode_display,
                    band_display,
                    frequency,
                    comment
                ))

                # Keep only last 100 spots
                items = self.spots_tree.get_children()
                if len(items) > 100:
                    self.spots_tree.delete(items[-1])

                # Save to database
                spot['cluster_source'] = self.cluster_var.get().split(' - ')[0]
                self.database.add_dx_spot(spot)

                self.last_spot_time = current_time

    def append_console(self, text):
        """Append text to console"""
        self.console_text.config(state='normal')
        self.console_text.insert('end', text + '\n')
        self.console_text.see('end')
        self.console_text.config(state='disabled')

    def update_timer(self):
        """Periodic update to check for new messages and display queued spots"""
        if self.client and self.client.is_connected():
            messages = self.client.get_messages()
            for msg in messages:
                self.append_console(msg)

        # Display next queued spot if ready
        self._display_next_spot()

        # Schedule next update
        self.parent.after(100, self.update_timer)  # Check more frequently for smoother display

    def toggle_all_filters(self, filter_dict, state):
        """Enable or disable all filters in a group"""
        for var in filter_dict.values():
            var.set(state)
        self.apply_filters()

    def apply_filters(self):
        """Apply current filters to displayed spots"""
        # Note: This currently only affects new incoming spots
        # Could be extended to re-filter existing spots in the tree
        pass

    def update_rate_limit(self, value):
        """Update the rate limiting interval"""
        self.min_spot_interval = float(value)
        self.rate_label.config(text=f"({self.min_spot_interval:.1f}s between spots)")

    def clear_duplicate_history(self):
        """Clear the duplicate spot history"""
        self.recent_spots.clear()
        messagebox.showinfo("History Cleared",
                          "Duplicate spot history has been cleared.\n"
                          "All spots will now appear again.")

    def spot_passes_filters(self, spot):
        """Check if a spot passes the current band, mode, continent, and duplicate filters"""
        callsign = spot.get('callsign', '').upper().strip()

        # Check duplicate filter
        if self.duplicate_filter_var.get():
            current_time = time.time()

            # Clean up old entries (older than duplicate window)
            expired_calls = [call for call, timestamp in self.recent_spots.items()
                           if current_time - timestamp > self.duplicate_window]
            for call in expired_calls:
                del self.recent_spots[call]

            # Check if this callsign was spotted recently
            if callsign in self.recent_spots:
                time_since = current_time - self.recent_spots[callsign]
                if time_since < self.duplicate_window:
                    # Duplicate - filter it out
                    return False

            # Not a duplicate - record it
            self.recent_spots[callsign] = current_time

        # Check band filter
        frequency = spot.get('frequency', '')
        band = self.frequency_to_band(frequency)
        if band and band in self.band_filters:
            if not self.band_filters[band].get():
                return False

        # Check mode filter
        comment = spot.get('comment', '').upper()
        mode = self.extract_mode_from_comment(comment)
        if mode and mode in self.mode_filters:
            if not self.mode_filters[mode].get():
                return False

        # Check continent filter - filter by SPOTTED station's continent
        continent_info = get_continent_from_callsign(callsign)
        if continent_info:
            continent = continent_info.get('continent')
            if continent and continent in self.continent_filters:
                if not self.continent_filters[continent].get():
                    return False

        return True

    def frequency_to_band(self, frequency):
        """Convert frequency (in kHz) to band name"""
        try:
            freq = float(frequency)

            # Band ranges in kHz
            if 1800 <= freq < 2000:
                return '160m'
            elif 3500 <= freq < 4000:
                return '80m'
            elif 5330 <= freq < 5405:
                return '60m'
            elif 7000 <= freq < 7300:
                return '40m'
            elif 10100 <= freq < 10150:
                return '30m'
            elif 14000 <= freq < 14350:
                return '20m'
            elif 18068 <= freq < 18168:
                return '17m'
            elif 21000 <= freq < 21450:
                return '15m'
            elif 24890 <= freq < 24990:
                return '12m'
            elif 28000 <= freq < 29700:
                return '10m'
            elif 50000 <= freq < 54000:
                return '6m'
            elif 144000 <= freq < 148000:
                return '2m'
        except (ValueError, TypeError):
            pass

        return None

    def extract_mode_from_comment(self, comment):
        """Extract mode from spot comment"""
        comment = comment.upper()

        # Check for specific mode keywords
        if 'FT8' in comment:
            return 'FT8'
        elif 'FT4' in comment:
            return 'FT4'
        elif 'RTTY' in comment or 'BAUDOT' in comment:
            return 'RTTY'
        elif 'PSK' in comment:
            return 'PSK'
        elif 'CW' in comment:
            return 'CW'
        elif 'SSB' in comment or 'PHONE' in comment:
            return 'SSB'
        elif any(mode in comment for mode in ['DIGI', 'FT', 'JS8', 'JT', 'WSPR']):
            return 'DIGI'

        # Default guess based on frequency band
        # CW is typically below 7040 on 40m, 14070 on 20m, etc.
        # For now, return None to allow all if mode not specified
        return None

    def get_frame(self):
        """Return the frame widget"""
        return self.frame
