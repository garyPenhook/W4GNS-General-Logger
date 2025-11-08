"""
DX Cluster Tab - Cluster connection and spot monitoring
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import time
from src.dx_clusters import DX_CLUSTERS, get_cluster_by_callsign
from src.dx_client import DXClusterClient
from src.dxcc import get_continent_from_callsign, get_country_from_callsign
from src.theme_colors import get_success_color, get_error_color, get_info_color


class DXClusterTab:
    def __init__(self, parent, database, config):
        self.parent = parent
        self.database = database
        self.config = config
        self.frame = ttk.Frame(parent)
        self.client = None
        self.logging_tab = None  # Reference to logging tab for spot display

        # Rate limiting for spots
        self.spot_queue = []
        self.last_spot_time = 0
        self.min_spot_interval = self.config.get('dx_filter.rate_limit', 0.5)

        # Duplicate filtering - track recent spots
        self.recent_spots = {}  # {callsign: timestamp}
        self.duplicate_window = 180  # 3 minutes in seconds

        self.create_widgets()
        self.update_timer()

        # Auto-connect if enabled
        if self.config.get('dx_cluster.auto_connect', False):
            # Delay connection until after main loop is running to avoid issues
            self.parent.after(500, self.auto_connect_on_startup)

    def auto_connect_on_startup(self):
        """Automatically connect to cluster on startup if enabled"""
        callsign = self.user_callsign_var.get().strip()
        if callsign and self.cluster_var.get():
            print("Auto-connecting to DX cluster...")
            self.connect()
        else:
            print("Auto-connect skipped: missing callsign or cluster selection")

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

        # Set default from config (prefer USA RBN-enabled cluster)
        default_cluster = self.config.get('dx_cluster.selected', 'AE5E')
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

        self.status_label = ttk.Label(info_row, text="Disconnected", foreground=get_error_color(self.config))
        self.status_label.pack(side='left', padx=10)

        # Cluster info display
        info_display = ttk.Frame(control_frame)
        info_display.pack(fill='x', pady=5)

        self.cluster_info_label = ttk.Label(info_display, text="", foreground=get_info_color(self.config))
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
            # Load saved filter state or default to True
            saved_state = self.config.get(f'dx_filter.band.{band}', True)
            var = tk.BooleanVar(value=saved_state)
            self.band_filters[band] = var
            ttk.Checkbutton(band_row, text=band, variable=var,
                           command=self.save_and_apply_filters).pack(side='left', padx=2)

        ttk.Button(band_row, text="All Bands",
                  command=lambda: self.toggle_all_filters(self.band_filters, True)).pack(side='left', padx=5)
        ttk.Button(band_row, text="Clear Bands",
                  command=lambda: self.toggle_all_filters(self.band_filters, False)).pack(side='left')

        # Mode filters - CW only
        self.mode_filters = {}
        modes = ['CW']
        for mode in modes:
            var = tk.BooleanVar(value=True)
            self.mode_filters[mode] = var

        # Continent filters (by spotter location)
        continent_row = ttk.Frame(filter_frame)
        continent_row.pack(fill='x', pady=2)

        ttk.Label(continent_row, text="Spotter Continents:").pack(side='left', padx=(0, 5))

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
            # Load saved filter state or default to True
            saved_state = self.config.get(f'dx_filter.continent.{code}', True)
            var = tk.BooleanVar(value=saved_state)
            self.continent_filters[code] = var
            ttk.Checkbutton(continent_row, text=code, variable=var,
                           command=self.save_and_apply_filters).pack(side='left', padx=2)

        ttk.Button(continent_row, text="All Continents",
                  command=lambda: self.toggle_all_filters(self.continent_filters, True)).pack(side='left', padx=5)
        ttk.Button(continent_row, text="Clear Continents",
                  command=lambda: self.toggle_all_filters(self.continent_filters, False)).pack(side='left')

        # Rate limiting control
        rate_row = ttk.Frame(filter_frame)
        rate_row.pack(fill='x', pady=2)

        ttk.Label(rate_row, text="Spot Display Rate:").pack(side='left', padx=(0, 5))
        ttk.Label(rate_row, text="Slow").pack(side='left')

        # Load saved rate limit or default to 0.5
        saved_rate = self.config.get('dx_filter.rate_limit', 0.5)
        self.rate_limit_var = tk.DoubleVar(value=saved_rate)
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

        # Load saved duplicate filter state or default to True
        saved_dup = self.config.get('dx_filter.duplicate_filter', True)
        self.duplicate_filter_var = tk.BooleanVar(value=saved_dup)
        ttk.Checkbutton(dup_row, text="Hide duplicate spots within 3 minutes",
                       variable=self.duplicate_filter_var,
                       command=self.save_duplicate_filter).pack(side='left', padx=2)

        ttk.Button(dup_row, text="Clear Duplicate History",
                  command=self.clear_duplicate_history).pack(side='left', padx=20)

        # Console output frame
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
                self.status_label.config(text="Connected", foreground=get_success_color(self.config))
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

        self.status_label.config(text="Disconnected", foreground=get_error_color(self.config))
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

                # Get mode from comment, fall back to frequency-based guess
                mode = self.extract_mode_from_comment(comment.upper())
                if not mode:
                    mode = self.guess_mode_from_frequency(frequency)
                mode_display = mode if mode else ''

                # Get band from frequency
                band = self.frequency_to_band(frequency)
                band_display = band if band else ''

                # Send spot to combined spots tab for display
                if self.logging_tab:
                    spot_data = {
                        'callsign': callsign,
                        'country': country,
                        'mode': mode_display,
                        'band': band_display,
                        'frequency': frequency,
                        'comment': comment
                    }
                    self.logging_tab.add_dx_spot(spot_data)

                # Save to database
                spot['cluster_source'] = self.cluster_var.get().split(' - ')[0]
                self.database.add_dx_spot(spot)

                self.last_spot_time = current_time

    def append_console(self, text):
        """Append text to console"""
        self.console_text.config(state='normal')
        self.console_text.insert('end', text + '\n')

        # Detect RBN unavailability messages and provide helpful guidance
        if 'no rbn' in text.lower() and 'available' in text.lower():
            # Add a helpful suggestion
            suggestion = (
                "\n⚠️ RBN (Reverse Beacon Network) spots are not available on this cluster node.\n"
                "💡 Try these USA clusters with active RBN/Skimmer feeds:\n"
                "   • AE5E (Thief River Falls, MN) - dxspots.com:7300\n"
                "   • K1AX-11 (N. Virginia) - dxdata.io:7300\n"
                "   • AI9T (Marshall, IL) - dxc.ai9t.com:7300\n"
                "   • K7TJ-1 (Spokane, WA) - k7tj.ewarg.org:7300\n"
                "   • KB8PMY-3 (Hamilton, OH) - kb8pmy.net:7300\n"
                "   Or check the Settings tab for the full list of RBN clusters.\n\n"
            )
            self.console_text.insert('end', suggestion)

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
        self.save_and_apply_filters()

    def save_and_apply_filters(self):
        """Save filter states and apply filters"""
        # Save band filters
        for band, var in self.band_filters.items():
            self.config.set(f'dx_filter.band.{band}', var.get())

        # Save mode filters
        for mode, var in self.mode_filters.items():
            self.config.set(f'dx_filter.mode.{mode}', var.get())

        # Save continent filters
        for continent, var in self.continent_filters.items():
            self.config.set(f'dx_filter.continent.{continent}', var.get())

        self.apply_filters()

    def apply_filters(self):
        """Apply current filters to displayed spots"""
        # Note: This currently only affects new incoming spots
        # Could be extended to re-filter existing spots in the tree
        pass

    def save_duplicate_filter(self):
        """Save duplicate filter state"""
        self.config.set('dx_filter.duplicate_filter', self.duplicate_filter_var.get())

    def update_rate_limit(self, value):
        """Update the rate limiting interval"""
        self.min_spot_interval = float(value)
        self.rate_label.config(text=f"({self.min_spot_interval:.1f}s between spots)")
        # Save to config
        self.config.set('dx_filter.rate_limit', self.min_spot_interval)

    def clear_duplicate_history(self):
        """Clear the duplicate spot history"""
        self.recent_spots.clear()
        messagebox.showinfo("History Cleared",
                          "Duplicate spot history has been cleared.\n"
                          "All spots will now appear again.")

    def spot_passes_filters(self, spot):
        """Check if a spot passes the current band, mode, continent, and duplicate filters"""
        callsign = spot.get('callsign', '').upper().strip()
        frequency = spot.get('frequency', '')

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
        band = self.frequency_to_band(frequency)
        if band and band in self.band_filters:
            if not self.band_filters[band].get():
                return False

        # Check mode filter - CW only
        comment = spot.get('comment', '').upper()
        mode = self.extract_mode_from_comment(comment)

        # If mode not in comment, guess from frequency
        if not mode:
            mode = self.guess_mode_from_frequency(frequency)

        # Filter out any non-CW spots
        if mode and mode != 'CW':
            return False

        # Check continent filter - filter by SPOTTER's continent (not DX station)
        # This shows you worldwide DX, but only from spotters in selected continents
        any_continent_disabled = any(not var.get() for var in self.continent_filters.values())

        if any_continent_disabled:
            # Get spotter's callsign and determine their continent
            spotter = spot.get('spotter', '').upper().strip()
            if spotter:
                # get_continent_from_callsign returns a string like "NA", not a dict
                continent = get_continent_from_callsign(spotter)

                if continent:
                    if continent in self.continent_filters:
                        # We know the spotter's continent - check if it's enabled
                        if not self.continent_filters[continent].get():
                            return False
                    else:
                        # Continent not in our filter list - filter it out for safety
                        return False
                else:
                    # Can't determine spotter's continent - filter it out when filtering is active
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

        # If mode not specified in comment, return None to show all spots
        # regardless of mode filter settings
        return None

    def guess_mode_from_frequency(self, frequency):
        """Guess mode from frequency - CW is typically in lower portion of bands"""
        try:
            freq = float(frequency)

            # CW band segments (approximate)
            if 1800 <= freq < 1840:  # 160m CW
                return 'CW'
            elif 3500 <= freq < 3600:  # 80m CW
                return 'CW'
            elif 7000 <= freq < 7040:  # 40m CW
                return 'CW'
            elif 10100 <= freq < 10140:  # 30m CW
                return 'CW'
            elif 14000 <= freq < 14070:  # 20m CW
                return 'CW'
            elif 18068 <= freq < 18110:  # 17m CW
                return 'CW'
            elif 21000 <= freq < 21070:  # 15m CW
                return 'CW'
            elif 24890 <= freq < 24920:  # 12m CW
                return 'CW'
            elif 28000 <= freq < 28070:  # 10m CW
                return 'CW'
            # Phone/SSB segments
            elif 1840 <= freq < 2000:  # 160m SSB
                return 'SSB'
            elif 3600 <= freq < 4000:  # 80m SSB
                return 'SSB'
            elif 7040 <= freq < 7300:  # 40m SSB
                return 'SSB'
            elif 14070 <= freq < 14350:  # 20m SSB
                return 'SSB'
            elif 18110 <= freq < 18168:  # 17m SSB
                return 'SSB'
            elif 21070 <= freq < 21450:  # 15m SSB
                return 'SSB'
            elif 24920 <= freq < 24990:  # 12m SSB
                return 'SSB'
            elif 28070 <= freq < 29700:  # 10m SSB
                return 'SSB'
        except (ValueError, TypeError):
            pass

        return None

    def set_logging_tab(self, logging_tab):
        """Set the reference to the logging tab for spot display"""
        self.logging_tab = logging_tab

    def get_frame(self):
        """Return the frame widget"""
        return self.frame
