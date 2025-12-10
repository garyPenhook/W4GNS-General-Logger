"""
Combined Spots Tab - DX Cluster spots (left) and POTA spots (right)
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import threading
from src.pota_client import POTAClient
from src.theme_colors import get_success_color, get_error_color, get_warning_color, get_info_color
from src.needed_analyzer import NeededContactsAnalyzer
from src.notifier import get_notifier, NotificationPreferences


class CombinedSpotsTab:
    def __init__(self, parent, database, config):
        self.parent = parent
        self.database = database
        self.config = config
        self.frame = ttk.Frame(parent)
        self.logging_tab = None  # Reference to logging tab for QSO population
        self.notebook = None  # Reference to notebook for tab switching

        # Smart log processing - needed contacts analyzer
        self.analyzer = NeededContactsAnalyzer(database)

        # Notification system
        self.notifier = get_notifier()
        self._load_notification_preferences()

        # DX spots filter state
        self.show_needed_only = tk.BooleanVar(value=self.config.get('dx_filter.needed_only', False))
        self.show_priority_colors = tk.BooleanVar(value=self.config.get('dx_filter.priority_colors', True))

        # POTA client and state
        self.pota_client = POTAClient()
        self.auto_refresh = False
        self.refresh_interval = 60
        self.current_pota_spots = []

        self.create_widgets()
        # Do initial POTA fetch
        self.refresh_pota_spots()

        # Start auto-refresh if it was enabled
        if self.auto_refresh:
            self.auto_refresh_timer()

    def create_widgets(self):
        """Create the combined spots interface with DX on left and POTA on right"""

        # Create a PanedWindow for resizable split
        paned = ttk.PanedWindow(self.frame, orient='horizontal')
        paned.pack(fill='both', expand=True, padx=5, pady=5)

        # LEFT PANEL - DX CLUSTER SPOTS
        dx_panel = ttk.Frame(paned)
        paned.add(dx_panel, weight=1)

        # DX Spots header with smart filtering controls
        dx_header = ttk.LabelFrame(dx_panel, text="DX Cluster Spots", padding=5)
        dx_header.pack(fill='x', padx=5, pady=5)

        dx_info = ttk.Label(dx_header,
                           text="Connect to a DX Cluster in the 'DX Clusters' tab to see spots here",
                           foreground=get_info_color(self.config))
        dx_info.pack()

        # Smart filtering controls
        dx_filter_frame = ttk.Frame(dx_header)
        dx_filter_frame.pack(fill='x', pady=5)

        ttk.Label(dx_filter_frame, text="Smart Filter:", font=('TkDefaultFont', 9, 'bold')).pack(side='left', padx=2)

        ttk.Checkbutton(dx_filter_frame, text="Show Needed Only",
                       variable=self.show_needed_only,
                       command=self.save_dx_filters).pack(side='left', padx=5)

        ttk.Checkbutton(dx_filter_frame, text="Priority Colors",
                       variable=self.show_priority_colors,
                       command=self.save_dx_filters).pack(side='left', padx=5)

        # Notification controls
        dx_notify_frame = ttk.Frame(dx_header)
        dx_notify_frame.pack(fill='x', pady=2)

        ttk.Label(dx_notify_frame, text="Alerts:", font=('TkDefaultFont', 9, 'bold')).pack(side='left', padx=2)

        self.notify_sound_var = tk.BooleanVar(value=self.config.get('notifications.sound', True))
        ttk.Checkbutton(dx_notify_frame, text="Sound Alert",
                       variable=self.notify_sound_var,
                       command=self.save_notification_prefs).pack(side='left', padx=5)

        self.notify_desktop_var = tk.BooleanVar(value=self.config.get('notifications.desktop', False))
        ttk.Checkbutton(dx_notify_frame, text="Desktop Notification",
                       variable=self.notify_desktop_var,
                       command=self.save_notification_prefs).pack(side='left', padx=5)

        # Legend
        legend_frame = ttk.Frame(dx_header)
        legend_frame.pack(fill='x', pady=2)
        ttk.Label(legend_frame, text="Priority:", font=('TkDefaultFont', 8)).pack(side='left', padx=2)
        ttk.Label(legend_frame, text="HIGH", foreground='#00C853', font=('TkDefaultFont', 8, 'bold')).pack(side='left', padx=5)
        ttk.Label(legend_frame, text="MEDIUM", foreground='#FFB300', font=('TkDefaultFont', 8, 'bold')).pack(side='left', padx=5)
        ttk.Label(legend_frame, text="LOW", foreground='#808080', font=('TkDefaultFont', 8)).pack(side='left', padx=5)

        # DX Spots display
        dx_spots_frame = ttk.Frame(dx_panel)
        dx_spots_frame.pack(fill='both', expand=True, padx=5, pady=5)

        # Create treeview for DX spots with Needed column
        dx_columns = ('Priority', 'Callsign', 'Country', 'Mode', 'Band', 'Frequency', 'Needed For', 'Comment')
        self.dx_spots_tree = ttk.Treeview(dx_spots_frame, columns=dx_columns,
                                         show='headings', height=25)

        for col in dx_columns:
            self.dx_spots_tree.heading(col, text=col)

        self.dx_spots_tree.column('Priority', width=50)
        self.dx_spots_tree.column('Callsign', width=90)
        self.dx_spots_tree.column('Country', width=130)
        self.dx_spots_tree.column('Mode', width=50)
        self.dx_spots_tree.column('Band', width=50)
        self.dx_spots_tree.column('Frequency', width=80)
        self.dx_spots_tree.column('Needed For', width=200)
        self.dx_spots_tree.column('Comment', width=200)

        # Configure color tags for priority levels
        self.dx_spots_tree.tag_configure('high_priority', foreground='#00C853')  # Bright green
        self.dx_spots_tree.tag_configure('medium_priority', foreground='#FFB300')  # Amber
        self.dx_spots_tree.tag_configure('low_priority', foreground='#808080')  # Gray
        self.dx_spots_tree.tag_configure('not_needed', foreground='#404040')  # Dark gray

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

        self.pota_status_label = ttk.Label(refresh_row, text="Ready", foreground=get_info_color(self.config))
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

        # Mode filters - CW only
        self.pota_mode_filters = {}
        modes = ['CW']
        for mode in modes:
            var = tk.BooleanVar(value=True)
            self.pota_mode_filters[mode] = var

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
        pota_columns = ('Activator', 'Park', 'Location', 'Freq', 'Mode', 'Band')
        self.pota_spots_tree = ttk.Treeview(pota_spots_frame, columns=pota_columns,
                                           show='headings', height=25)

        self.pota_spots_tree.heading('Activator', text='Activator')
        self.pota_spots_tree.heading('Park', text='Park')
        self.pota_spots_tree.heading('Location', text='Loc')
        self.pota_spots_tree.heading('Freq', text='Frequency')
        self.pota_spots_tree.heading('Mode', text='Mode')
        self.pota_spots_tree.heading('Band', text='Band')

        self.pota_spots_tree.column('Activator', width=90)
        self.pota_spots_tree.column('Park', width=200)
        self.pota_spots_tree.column('Location', width=60)
        self.pota_spots_tree.column('Freq', width=80)
        self.pota_spots_tree.column('Mode', width=50)
        self.pota_spots_tree.column('Band', width=50)

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

        # Double-click to show details
        self.pota_spots_tree.bind('<Double-1>', self.on_pota_spot_double_click)

    def _load_notification_preferences(self):
        """Load notification preferences from config"""
        prefs = NotificationPreferences(
            enabled=self.config.get('notifications.enabled', True),
            sound_enabled=self.config.get('notifications.sound', True),
            desktop_notification_enabled=self.config.get('notifications.desktop', False),
            min_priority=self.config.get('notifications.min_priority', 2),
            sound_command=self.config.get('notifications.sound_command', None)
        )
        self.notifier.update_preferences(prefs)

    # DX SPOTS METHODS
    def add_dx_spot(self, spot_data):
        """Add a DX spot to the display (called from DX cluster tab)"""
        callsign = spot_data.get('callsign', '')
        country = spot_data.get('country', '')
        mode = spot_data.get('mode', '')
        band = spot_data.get('band', '')
        frequency = spot_data.get('frequency', '')
        comment = spot_data.get('comment', '')

        # Analyze if this spot is needed for any awards
        analysis = self.analyzer.analyze_spot(
            callsign=callsign,
            band=band,
            mode=mode,
            frequency=frequency,
            skcc_number=spot_data.get('skcc_number'),
            state=spot_data.get('state'),
            country=country,
            continent=spot_data.get('continent'),
            gridsquare=spot_data.get('gridsquare')
        )

        # Send notification if needed and high priority
        if analysis.is_needed and analysis.highest_priority <= 2:
            reason = analysis.get_reason_summary()
            self.notifier.notify_needed_contact(callsign, analysis.highest_priority, reason)

        # Filter out if "needed only" is enabled and spot is not needed
        if self.show_needed_only.get() and not analysis.is_needed:
            return

        # Determine priority display and tag
        priority_text = analysis.priority_label
        if analysis.is_needed:
            needed_for = analysis.get_reason_summary()
        else:
            needed_for = ""

        # Determine color tag
        if not self.show_priority_colors.get():
            tag = ''
        elif analysis.highest_priority == 1:
            tag = 'high_priority'
        elif analysis.highest_priority == 2:
            tag = 'medium_priority'
        elif analysis.highest_priority == 3:
            tag = 'low_priority'
        else:
            tag = 'not_needed'

        # Insert spot with priority and needed info
        self.dx_spots_tree.insert('', 0, values=(
            priority_text,
            callsign,
            country,
            mode,
            band,
            frequency,
            needed_for,
            comment
        ), tags=(tag,))

        # Keep only the most recent 100 spots
        children = self.dx_spots_tree.get_children()
        if len(children) > 100:
            self.dx_spots_tree.delete(children[-1])

    def save_dx_filters(self):
        """Save DX filter preferences"""
        self.config.set('dx_filter.needed_only', self.show_needed_only.get())
        self.config.set('dx_filter.priority_colors', self.show_priority_colors.get())

    def save_notification_prefs(self):
        """Save notification preferences"""
        self.config.set('notifications.sound', self.notify_sound_var.get())
        self.config.set('notifications.desktop', self.notify_desktop_var.get())
        # Reload preferences into notifier
        self._load_notification_preferences()

    def on_dx_spot_double_click(self, event):
        """Handle double-click on DX spot - populate entry form in logging tab"""
        selection = self.dx_spots_tree.selection()
        if not selection:
            return

        if not self.logging_tab:
            messagebox.showwarning("Not Connected", "Logging tab not available")
            return

        item = self.dx_spots_tree.item(selection[0])
        values = item['values']

        if len(values) >= 8:
            # Updated for new column layout: Priority, Callsign, Country, Mode, Band, Frequency, Needed For, Comment
            callsign = values[1]
            mode = values[3]
            band = values[4]
            frequency = values[5]
            needed_for = values[6]
            comment = values[7]

            # Switch to Log Contacts tab
            if self.notebook:
                self.notebook.select(0)  # First tab is Log Contacts

            # Reset time_on flag so time can be captured when Tab is pressed
            self.logging_tab.time_on_captured = False
            self.logging_tab.time_on_var.set('')  # Clear time_on for new contact

            # Populate the logging form
            self.logging_tab.callsign_var.set(callsign)
            self.logging_tab.freq_var.set(frequency)
            self.logging_tab.mode_var.set(mode)
            self.logging_tab.band_var.set(band)

            # Add comment and needed info to notes if present
            notes_parts = []
            if needed_for:
                notes_parts.append(f"NEEDED: {needed_for}")
            if comment:
                notes_parts.append(f"DX: {comment}")

            if notes_parts:
                current_notes = self.logging_tab.notes_var.get()
                new_note = " | ".join(notes_parts)
                if current_notes:
                    self.logging_tab.notes_var.set(f"{current_notes} | {new_note}")
                else:
                    self.logging_tab.notes_var.set(new_note)

            # Trigger callsign lookup (QRZ)
            self.logging_tab.on_callsign_changed()

            # Focus on callsign field
            self.logging_tab.callsign_entry.focus()

    # POTA SPOTS METHODS
    def refresh_pota_spots_async(self):
        """Refresh POTA spots in background thread"""
        self.pota_status_label.config(text="Fetching...", foreground=get_warning_color(self.config))
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
                foreground=get_success_color(self.config)))
        except Exception as e:
            self.parent.after(0, lambda: self.pota_status_label.config(
                text=f"Error", foreground=get_error_color(self.config)))

    def _update_pota_spots_display(self):
        """Update POTA spots display with filtered spots"""
        # Clear existing items
        for item in self.pota_spots_tree.get_children():
            self.pota_spots_tree.delete(item)

        # Apply filters and add spots
        for spot in self.current_pota_spots:
            if self.pota_spot_passes_filters(spot):
                # Combine park reference and name
                park_ref = spot.get('park_ref', '')
                park_name = spot.get('park_name', '')
                park_display = f"{park_ref} {park_name}" if park_name else park_ref

                self.pota_spots_tree.insert('', 'end', values=(
                    spot.get('activator', ''),
                    park_display,
                    spot.get('location', ''),
                    spot.get('frequency', ''),
                    spot.get('mode', ''),
                    spot.get('band', '')
                ))

    def pota_spot_passes_filters(self, spot):
        """Check if POTA spot passes current filters"""
        # Band filter
        band = spot.get('band', '')
        if band and band in self.pota_band_filters:
            if not self.pota_band_filters[band].get():
                return False

        # Mode filter - CW only
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

        # Filter out any non-CW spots
        if mode_category and mode_category != 'CW':
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
        """Handle double-click on POTA spot - populate entry form in logging tab"""
        selection = self.pota_spots_tree.selection()
        if not selection:
            return

        if not self.logging_tab:
            messagebox.showwarning("Not Connected", "Logging tab not available")
            return

        item = self.pota_spots_tree.item(selection[0])
        values = item['values']

        if len(values) >= 6:
            activator = values[0]
            park_display = values[1]
            location = values[2]
            frequency = values[3]
            mode = values[4]
            band = values[5]

            # Extract park_ref from park_display (first part before space)
            park_ref = park_display.split()[0] if park_display else ''

            # Switch to Log Contacts tab
            if self.notebook:
                self.notebook.select(0)  # First tab is Log Contacts

            # Reset time_on flag so time can be captured when Tab is pressed
            self.logging_tab.time_on_captured = False
            self.logging_tab.time_on_var.set('')  # Clear time_on for new contact

            # Populate the logging form
            self.logging_tab.callsign_var.set(activator)
            self.logging_tab.freq_var.set(frequency)
            self.logging_tab.mode_var.set(mode)
            self.logging_tab.band_var.set(band)

            # Add POTA reference to POTA field and full park info to notes
            self.logging_tab.pota_var.set(park_ref)
            self.logging_tab.notes_var.set(f"POTA: {park_display}")

            # Trigger callsign lookup (QRZ)
            self.logging_tab.on_callsign_changed()

            # Focus on callsign field
            self.logging_tab.callsign_entry.focus()

    def set_logging_tab(self, logging_tab):
        """Set reference to logging tab for QSO population"""
        self.logging_tab = logging_tab

    def set_notebook(self, notebook):
        """Set reference to notebook for tab switching"""
        self.notebook = notebook

    def get_frame(self):
        """Return the frame widget"""
        return self.frame
