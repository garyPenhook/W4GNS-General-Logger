"""
POTA (Parks on the Air) Tab - Display POTA activator spots
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import threading
from src.pota_client import POTAClient


class POTATab:
    def __init__(self, parent, database, config):
        self.parent = parent
        self.database = database
        self.config = config
        self.frame = ttk.Frame(parent)
        self.pota_client = POTAClient()
        self.auto_refresh = False
        self.refresh_interval = 60  # seconds
        self.current_spots = []

        self.create_widgets()
        # Do initial fetch
        self.refresh_spots()

    def create_widgets(self):
        """Create the POTA spots interface"""

        # Control frame
        control_frame = ttk.LabelFrame(self.frame, text="POTA Spots Control", padding=10)
        control_frame.pack(fill='x', padx=10, pady=5)

        # Refresh controls
        refresh_row = ttk.Frame(control_frame)
        refresh_row.pack(fill='x', pady=5)

        ttk.Button(refresh_row, text="Refresh Spots",
                  command=self.refresh_spots_async).pack(side='left', padx=5)

        self.auto_refresh_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(refresh_row, text="Auto-refresh every",
                       variable=self.auto_refresh_var,
                       command=self.toggle_auto_refresh).pack(side='left', padx=(20, 5))

        self.refresh_interval_var = tk.IntVar(value=60)
        ttk.Spinbox(refresh_row, from_=30, to=300, increment=30,
                   textvariable=self.refresh_interval_var, width=8).pack(side='left')
        ttk.Label(refresh_row, text="seconds").pack(side='left', padx=5)

        self.status_label = ttk.Label(refresh_row, text="Ready", foreground="blue")
        self.status_label.pack(side='left', padx=20)

        # Filter frame
        filter_frame = ttk.LabelFrame(self.frame, text="Filters", padding=10)
        filter_frame.pack(fill='x', padx=10, pady=5)

        # Band filters
        band_row = ttk.Frame(filter_frame)
        band_row.pack(fill='x', pady=2)

        ttk.Label(band_row, text="Bands:").pack(side='left', padx=(0, 5))

        self.band_filters = {}
        bands = ['160m', '80m', '60m', '40m', '30m', '20m', '17m', '15m', '12m', '10m', '6m', '2m']
        for band in bands:
            var = tk.BooleanVar(value=True)
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
        modes = ['CW', 'SSB', 'FM', 'FT8', 'FT4', 'RTTY', 'PSK', 'DIGI']
        for mode in modes:
            var = tk.BooleanVar(value=True)
            self.mode_filters[mode] = var
            ttk.Checkbutton(mode_row, text=mode, variable=var,
                           command=self.apply_filters).pack(side='left', padx=2)

        ttk.Button(mode_row, text="All Modes",
                  command=lambda: self.toggle_all_filters(self.mode_filters, True)).pack(side='left', padx=5)
        ttk.Button(mode_row, text="Clear Modes",
                  command=lambda: self.toggle_all_filters(self.mode_filters, False)).pack(side='left')

        # Search/filter by location
        search_row = ttk.Frame(filter_frame)
        search_row.pack(fill='x', pady=2)

        ttk.Label(search_row, text="Filter Location:").pack(side='left', padx=(0, 5))
        self.location_filter_var = tk.StringVar()
        self.location_filter_var.trace('w', lambda *args: self.apply_filters())
        ttk.Entry(search_row, textvariable=self.location_filter_var, width=20).pack(side='left', padx=5)
        ttk.Label(search_row, text="(e.g., US-CA, US-TX)").pack(side='left', padx=5)

        # Spots display frame
        spots_frame = ttk.LabelFrame(self.frame, text="POTA Activator Spots", padding=10)
        spots_frame.pack(fill='both', expand=True, padx=10, pady=5)

        # Create treeview for spots
        columns = ('Activator', 'Park', 'Location', 'Frequency', 'Mode', 'Band',
                   'Spotter', 'Comments')
        self.spots_tree = ttk.Treeview(spots_frame, columns=columns, show='headings', height=20)

        # Set column headings and widths
        self.spots_tree.heading('Activator', text='Activator')
        self.spots_tree.heading('Park', text='Park')
        self.spots_tree.heading('Location', text='Location')
        self.spots_tree.heading('Frequency', text='Frequency')
        self.spots_tree.heading('Mode', text='Mode')
        self.spots_tree.heading('Band', text='Band')
        self.spots_tree.heading('Spotter', text='Spotter')
        self.spots_tree.heading('Comments', text='Comments')

        self.spots_tree.column('Activator', width=100)
        self.spots_tree.column('Park', width=250)
        self.spots_tree.column('Location', width=80)
        self.spots_tree.column('Frequency', width=90)
        self.spots_tree.column('Mode', width=60)
        self.spots_tree.column('Band', width=60)
        self.spots_tree.column('Spotter', width=100)
        self.spots_tree.column('Comments', width=200)

        # Scrollbars
        vsb = ttk.Scrollbar(spots_frame, orient='vertical', command=self.spots_tree.yview)
        hsb = ttk.Scrollbar(spots_frame, orient='horizontal', command=self.spots_tree.xview)
        self.spots_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.spots_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')

        spots_frame.grid_rowconfigure(0, weight=1)
        spots_frame.grid_columnconfigure(0, weight=1)

        # Double-click to show park details
        self.spots_tree.bind('<Double-1>', self.on_spot_double_click)

        # Info label
        info_row = ttk.Frame(self.frame)
        info_row.pack(fill='x', padx=10, pady=5)
        self.info_label = ttk.Label(info_row, text="Double-click a spot to view park details",
                                    foreground="gray")
        self.info_label.pack(side='left')

    def refresh_spots_async(self):
        """Refresh spots in a background thread to avoid blocking UI"""
        self.status_label.config(text="Fetching spots...", foreground="orange")
        thread = threading.Thread(target=self.refresh_spots, daemon=True)
        thread.start()

    def refresh_spots(self):
        """Fetch spots from POTA API"""
        try:
            spots = self.pota_client.get_spots()
            self.current_spots = spots

            # Update UI in main thread
            self.parent.after(0, self._update_spots_display)
            self.parent.after(0, lambda: self.status_label.config(
                text=f"Last updated: {datetime.now().strftime('%H:%M:%S')} - {len(spots)} spots",
                foreground="green"))
        except Exception as e:
            self.parent.after(0, lambda: self.status_label.config(
                text=f"Error: {str(e)}", foreground="red"))
            self.parent.after(0, lambda: messagebox.showerror(
                "POTA API Error", f"Failed to fetch POTA spots:\n{str(e)}"))

    def _update_spots_display(self):
        """Update the spots display with filtered spots"""
        # Clear existing items
        for item in self.spots_tree.get_children():
            self.spots_tree.delete(item)

        # Apply filters and add spots
        filtered_count = 0
        for spot in self.current_spots:
            if self.spot_passes_filters(spot):
                # Combine park reference and name
                park_ref = spot.get('park_ref', '')
                park_name = spot.get('park_name', '')
                park_display = f"{park_ref} {park_name}" if park_name else park_ref

                self.spots_tree.insert('', 'end', values=(
                    spot.get('activator', ''),
                    park_display,
                    spot.get('location', ''),
                    spot.get('frequency', ''),
                    spot.get('mode', ''),
                    spot.get('band', ''),
                    spot.get('spotter', ''),
                    spot.get('comments', '')
                ))
                filtered_count += 1

        self.info_label.config(
            text=f"Showing {filtered_count} of {len(self.current_spots)} spots - Double-click to view details")

    def spot_passes_filters(self, spot):
        """Check if spot passes current filters"""
        # Band filter
        band = spot.get('band', '')
        if band and band in self.band_filters:
            if not self.band_filters[band].get():
                return False

        # Mode filter
        mode = spot.get('mode', '').upper()
        # Map mode variations
        mode_map = {
            'SSB': 'SSB', 'USB': 'SSB', 'LSB': 'SSB',
            'CW': 'CW',
            'FM': 'FM',
            'FT8': 'FT8',
            'FT4': 'FT4',
            'RTTY': 'RTTY',
            'PSK31': 'PSK', 'PSK63': 'PSK',
            'DIGITAL': 'DIGI', 'DATA': 'DIGI'
        }
        mode_category = mode_map.get(mode, mode)

        if mode_category and mode_category in self.mode_filters:
            if not self.mode_filters[mode_category].get():
                return False

        # Location filter
        location_filter = self.location_filter_var.get().upper().strip()
        if location_filter:
            location = spot.get('location', '').upper()
            park_ref = spot.get('park_ref', '').upper()
            if location_filter not in location and location_filter not in park_ref:
                return False

        return True

    def apply_filters(self):
        """Apply current filters to displayed spots"""
        self._update_spots_display()

    def toggle_all_filters(self, filter_dict, state):
        """Enable or disable all filters in a group"""
        for var in filter_dict.values():
            var.set(state)
        self.apply_filters()

    def toggle_auto_refresh(self):
        """Toggle auto-refresh on/off"""
        self.auto_refresh = self.auto_refresh_var.get()
        if self.auto_refresh:
            self.auto_refresh_timer()

    def auto_refresh_timer(self):
        """Timer for auto-refresh"""
        if self.auto_refresh:
            self.refresh_spots_async()
            interval = self.refresh_interval_var.get() * 1000  # Convert to milliseconds
            self.parent.after(interval, self.auto_refresh_timer)

    def on_spot_double_click(self, event):
        """Handle double-click on a spot - show park details"""
        selection = self.spots_tree.selection()
        if not selection:
            return

        item = self.spots_tree.item(selection[0])
        values = item['values']

        if len(values) >= 8:
            activator = values[0]
            park_display = values[1]
            location = values[2]
            frequency = values[3]
            mode = values[4]
            band = values[5]
            spotter = values[6]
            comments = values[7]

            # Extract park_ref from park_display (first part before space)
            park_ref = park_display.split()[0] if park_display else ''

            # Find full spot details
            spot_details = None
            for spot in self.current_spots:
                if (spot.get('activator') == activator and
                    spot.get('park_ref') == park_ref and
                    spot.get('frequency') == frequency):
                    spot_details = spot
                    break

            # Build detail message
            details = f"POTA Activator Spot Details\n\n"
            details += f"Activator: {activator}\n"
            details += f"Park: {park_display}\n"

            if spot_details:
                grid = spot_details.get('grid', '')
                if grid:
                    details += f"Grid: {grid}\n"

                # Show spot time
                spot_time = spot_details.get('spot_time', '')
                if 'T' in spot_time:
                    try:
                        dt = datetime.fromisoformat(spot_time.replace('Z', '+00:00'))
                        spot_time = dt.strftime('%H:%M UTC')
                    except:
                        pass
                if spot_time:
                    details += f"Spotted: {spot_time}\n"

                # Show QSO count
                qso_count = spot_details.get('qso_count', 0)
                if qso_count:
                    details += f"QSO Count: {qso_count}\n"

            details += f"Location: {location}\n"
            details += f"Frequency: {frequency} MHz\n"
            details += f"Mode: {mode}\n"
            details += f"Band: {band}\n"
            details += f"Spotter: {spotter}\n"

            if comments:
                details += f"Comments: {comments}\n"

            messagebox.showinfo("POTA Spot Details", details)

    def get_frame(self):
        """Return the frame widget"""
        return self.frame
