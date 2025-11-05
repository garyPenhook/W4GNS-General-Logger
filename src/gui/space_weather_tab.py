"""
Space Weather Tab
Displays solar and geomagnetic conditions affecting HF propagation
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime
import threading
from src.space_weather import SpaceWeatherClient


class SpaceWeatherTab:
    def __init__(self, parent, database, config):
        self.database = database
        self.config = config
        self.frame = ttk.Frame(parent)
        self.client = SpaceWeatherClient()
        self.data = None
        self.auto_refresh = True

        self.create_widgets()
        self.refresh_data()

    def get_frame(self):
        """Return the tab's frame"""
        return self.frame

    def create_widgets(self):
        """Create the space weather display widgets"""

        # Main container with scrollbar
        main_container = ttk.Frame(self.frame)
        main_container.pack(fill='both', expand=True, padx=10, pady=10)

        # Title and refresh controls
        header_frame = ttk.Frame(main_container)
        header_frame.pack(fill='x', pady=(0, 10))

        title_label = ttk.Label(header_frame, text="Space Weather & Propagation",
                               font=('TkDefaultFont', 14, 'bold'))
        title_label.pack(side='left')

        self.updated_label = ttk.Label(header_frame, text="Loading...",
                                      font=('TkDefaultFont', 9))
        self.updated_label.pack(side='left', padx=20)

        refresh_btn = ttk.Button(header_frame, text="↻ Refresh", command=self.refresh_data)
        refresh_btn.pack(side='right', padx=5)

        # Overall Propagation Summary
        summary_frame = ttk.LabelFrame(main_container, text="Overall Propagation Conditions",
                                      padding=10)
        summary_frame.pack(fill='x', pady=(0, 10))

        self.summary_label = ttk.Label(summary_frame, text="--",
                                      font=('TkDefaultFont', 16, 'bold'))
        self.summary_label.pack()

        self.summary_desc = ttk.Label(summary_frame, text="Loading data...",
                                     font=('TkDefaultFont', 10))
        self.summary_desc.pack(pady=5)

        # Create two columns for metrics
        metrics_container = ttk.Frame(main_container)
        metrics_container.pack(fill='both', expand=True)

        left_column = ttk.Frame(metrics_container)
        left_column.pack(side='left', fill='both', expand=True, padx=(0, 5))

        right_column = ttk.Frame(metrics_container)
        right_column.pack(side='left', fill='both', expand=True, padx=(5, 0))

        # LEFT COLUMN - Primary Metrics
        # Solar Flux Index
        self.sfi_frame = self.create_metric_display(
            left_column, "Solar Flux Index (SFI)",
            "10.7cm solar radio emissions", 0, 250
        )

        # Sunspot Number
        self.ssn_frame = self.create_metric_display(
            left_column, "Sunspot Number",
            "Current sunspot count", 0, 200
        )

        # K-Index
        self.k_frame = self.create_metric_display(
            left_column, "K-Index",
            "Geomagnetic activity (3-hour)", 0, 9
        )

        # RIGHT COLUMN - Secondary Metrics
        # A-Index
        self.a_frame = self.create_metric_display(
            right_column, "A-Index",
            "Geomagnetic activity (daily)", 0, 100
        )

        # Solar Wind
        self.wind_frame = self.create_metric_display(
            right_column, "Solar Wind",
            "Solar wind speed (km/s)", 0, 800
        )

        # X-Ray Flux
        self.xray_frame = self.create_metric_display(
            right_column, "X-Ray Flux",
            "Solar X-ray background", None, None, is_text=True
        )

        # Band Conditions Summary
        band_frame = ttk.LabelFrame(main_container, text="HF Band Conditions", padding=10)
        band_frame.pack(fill='x', pady=(10, 0))

        # Day and Night columns
        band_container = ttk.Frame(band_frame)
        band_container.pack(fill='x')

        day_frame = ttk.Frame(band_container)
        day_frame.pack(side='left', fill='both', expand=True, padx=5)
        ttk.Label(day_frame, text="Daytime", font=('TkDefaultFont', 10, 'bold')).pack()
        self.day_bands_label = ttk.Label(day_frame, text="Loading...", justify='left')
        self.day_bands_label.pack(anchor='w', pady=5)

        night_frame = ttk.Frame(band_container)
        night_frame.pack(side='left', fill='both', expand=True, padx=5)
        ttk.Label(night_frame, text="Nighttime", font=('TkDefaultFont', 10, 'bold')).pack()
        self.night_bands_label = ttk.Label(night_frame, text="Loading...", justify='left')
        self.night_bands_label.pack(anchor='w', pady=5)

        # Data source attribution
        source_label = ttk.Label(main_container,
                                text="Data from HamQSL.com (N0NBH) and NOAA Space Weather Prediction Center",
                                font=('TkDefaultFont', 8), foreground='gray')
        source_label.pack(pady=(10, 0))

    def create_metric_display(self, parent, title, description, min_val, max_val, is_text=False):
        """Create a metric display with bar graph and interpretation"""

        frame = ttk.LabelFrame(parent, text=title, padding=10)
        frame.pack(fill='x', pady=(0, 10))

        # Description
        desc_label = ttk.Label(frame, text=description, font=('TkDefaultFont', 8),
                              foreground='gray')
        desc_label.pack(anchor='w')

        # Value and interpretation container
        value_frame = ttk.Frame(frame)
        value_frame.pack(fill='x', pady=5)

        # Large value display
        value_label = ttk.Label(value_frame, text="--", font=('TkDefaultFont', 24, 'bold'))
        value_label.pack(side='left', padx=(0, 10))

        # Interpretation
        interp_label = ttk.Label(value_frame, text="", font=('TkDefaultFont', 11))
        interp_label.pack(side='left')

        if not is_text:
            # Bar graph canvas
            canvas = tk.Canvas(frame, height=30, bg='#e0e0e0', highlightthickness=0)
            canvas.pack(fill='x', pady=(5, 0))

            # Scale labels
            scale_frame = ttk.Frame(frame)
            scale_frame.pack(fill='x')
            min_label = ttk.Label(scale_frame, text=str(min_val), font=('TkDefaultFont', 8))
            min_label.pack(side='left')
            max_label = ttk.Label(scale_frame, text=str(max_val), font=('TkDefaultFont', 8))
            max_label.pack(side='right')

            return {
                'frame': frame,
                'value_label': value_label,
                'interp_label': interp_label,
                'canvas': canvas,
                'min_val': min_val,
                'max_val': max_val
            }
        else:
            return {
                'frame': frame,
                'value_label': value_label,
                'interp_label': interp_label
            }

    def update_metric_display(self, metric_dict, value, interpretation=None, color="#388e3c"):
        """Update a metric display with current value"""

        if value is None or value == 'N/A':
            metric_dict['value_label'].config(text="N/A")
            if 'canvas' in metric_dict:
                metric_dict['canvas'].delete('all')
            return

        # Update value
        if isinstance(value, (int, float)):
            metric_dict['value_label'].config(text=str(int(value)))
        else:
            metric_dict['value_label'].config(text=str(value))

        # Update interpretation
        if interpretation:
            metric_dict['interp_label'].config(text=interpretation, foreground=color)

        # Update bar graph
        if 'canvas' in metric_dict:
            canvas = metric_dict['canvas']
            canvas.delete('all')

            width = canvas.winfo_width()
            if width <= 1:
                width = 400  # Default width

            # Calculate bar width
            min_val = metric_dict['min_val']
            max_val = metric_dict['max_val']

            if max_val > min_val:
                percentage = min(100, max(0, ((value - min_val) / (max_val - min_val)) * 100))
                bar_width = (width * percentage) / 100

                # Draw bar
                canvas.create_rectangle(0, 0, bar_width, 30, fill=color, outline='')

    def refresh_data(self):
        """Refresh space weather data"""
        def fetch_data():
            self.data = self.client.get_hamqsl_data()
            self.frame.after(0, self.update_display)

        # Fetch in background thread
        thread = threading.Thread(target=fetch_data, daemon=True)
        thread.start()

    def update_display(self):
        """Update all displays with fetched data"""

        if not self.data:
            self.summary_label.config(text="Error Loading Data")
            self.summary_desc.config(text="Unable to fetch space weather data")
            return

        # Update timestamp
        updated = self.data.get('updated', 'Unknown')
        self.updated_label.config(text=f"Updated: {updated}")

        # Update overall summary
        rating, color, description = self.client.get_propagation_summary(self.data)
        self.summary_label.config(text=rating, foreground=color)
        self.summary_desc.config(text=description)

        # Update Solar Flux Index
        sfi = self.data.get('solar_flux', 0)
        sfi_interp, sfi_color = self.client.interpret_solar_flux(sfi)
        self.update_metric_display(self.sfi_frame, sfi, sfi_interp, sfi_color)

        # Update Sunspot Number
        ssn = self.data.get('sunspot_number', 0)
        ssn_interp, ssn_color = self.client.interpret_sunspots(ssn)
        self.update_metric_display(self.ssn_frame, ssn, ssn_interp, ssn_color)

        # Update K-Index
        k = self.data.get('k_index', 0)
        k_interp, k_color = self.client.interpret_k_index(k)
        self.update_metric_display(self.k_frame, k, k_interp, k_color)

        # Update A-Index
        a = self.data.get('a_index', 0)
        a_interp, a_color = self.client.interpret_a_index(a)
        self.update_metric_display(self.a_frame, a, a_interp, a_color)

        # Update Solar Wind
        wind = self.data.get('solar_wind', 0)
        wind_interp = "Normal" if wind < 450 else "Elevated" if wind < 600 else "High"
        wind_color = "#388e3c" if wind < 450 else "#fbc02d" if wind < 600 else "#e64a19"
        self.update_metric_display(self.wind_frame, wind, wind_interp, wind_color)

        # Update X-Ray
        xray = self.data.get('x_ray', 'N/A')
        xray_interp = f"Class {xray}"
        xray_color = "#388e3c" if xray.startswith('A') or xray.startswith('B') else \
                     "#fbc02d" if xray.startswith('C') else \
                     "#f57c00" if xray.startswith('M') else "#d32f2f"
        self.update_metric_display(self.xray_frame, xray, xray_interp, xray_color)

        # Update band conditions
        self.update_band_conditions()

        # Schedule next auto-refresh (5 minutes)
        if self.auto_refresh:
            self.frame.after(300000, self.refresh_data)

    def update_band_conditions(self):
        """Update HF band condition displays"""
        if not self.data:
            return

        band_conditions = self.data.get('band_conditions', {})

        # Parse day conditions
        day_text = "80m-40m: "
        day_text += self._get_band_rating(['80m-40m_day'], band_conditions.get('day', {}))
        day_text += "\n30m-10m: "
        day_text += self._get_band_rating(['30m-20m_day', '17m-15m_day', '12m-10m_day'],
                                         band_conditions.get('day', {}))
        self.day_bands_label.config(text=day_text)

        # Parse night conditions
        night_text = "80m-40m: "
        night_text += self._get_band_rating(['80m-40m_night'], band_conditions.get('night', {}))
        night_text += "\n30m-10m: "
        night_text += self._get_band_rating(['30m-20m_night', '17m-15m_night', '12m-10m_night'],
                                           band_conditions.get('night', {}))
        self.night_bands_label.config(text=night_text)

    def _get_band_rating(self, band_keys, conditions_dict):
        """Get band condition rating from keys"""
        for key in band_keys:
            if key in conditions_dict:
                return conditions_dict[key]
        return "N/A"
