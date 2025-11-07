"""
Weather Tab - Local weather conditions display
Uses Open-Meteo API (free, open source, no API key required)
"""

import tkinter as tk
from tkinter import ttk, messagebox
import requests
from datetime import datetime
from src.theme_colors import get_info_color, get_muted_color, get_error_color


class WeatherTab:
    def __init__(self, parent, config):
        self.parent = parent
        self.config = config
        self.frame = ttk.Frame(parent)
        self.weather_data = None
        self.auto_refresh_id = None
        self.create_widgets()

        # Auto-refresh weather on tab load if zip code is configured
        if self.config.get('zip_code'):
            self.refresh_weather()

        # Start hourly auto-refresh timer
        self.start_auto_refresh()

    def create_widgets(self):
        """Create the weather interface"""
        # Main container with padding
        main_frame = ttk.Frame(self.frame, padding=10)
        main_frame.pack(fill='both', expand=True)

        # Header with refresh button
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill='x', pady=(0, 10))

        ttk.Label(header_frame, text="Local Weather Conditions",
                 font=('', 14, 'bold')).pack(side='left')

        refresh_btn = ttk.Button(header_frame, text="🔄 Refresh",
                                command=self.refresh_weather)
        refresh_btn.pack(side='right')

        # Location display
        self.location_label = ttk.Label(main_frame, text="",
                                       font=('', 10),
                                       foreground=get_info_color(self.config))
        self.location_label.pack(anchor='w', pady=(0, 10))

        # Current conditions frame
        current_frame = ttk.LabelFrame(main_frame, text="Current Conditions", padding=10)
        current_frame.pack(fill='x', pady=5)

        # Temperature display (large)
        self.temp_label = ttk.Label(current_frame, text="--°F",
                                    font=('', 32, 'bold'))
        self.temp_label.pack()

        # Conditions text
        self.conditions_label = ttk.Label(current_frame, text="",
                                         font=('', 12))
        self.conditions_label.pack()

        # Details grid
        details_frame = ttk.Frame(current_frame)
        details_frame.pack(fill='x', pady=10)

        # Left column
        left_col = ttk.Frame(details_frame)
        left_col.pack(side='left', fill='both', expand=True, padx=5)

        self.feels_like_label = ttk.Label(left_col, text="Feels Like: --°F")
        self.feels_like_label.pack(anchor='w', pady=2)

        self.humidity_label = ttk.Label(left_col, text="Humidity: --%")
        self.humidity_label.pack(anchor='w', pady=2)

        self.pressure_label = ttk.Label(left_col, text="Pressure: -- inHg")
        self.pressure_label.pack(anchor='w', pady=2)

        # Right column
        right_col = ttk.Frame(details_frame)
        right_col.pack(side='right', fill='both', expand=True, padx=5)

        self.wind_label = ttk.Label(right_col, text="Wind: -- mph")
        self.wind_label.pack(anchor='w', pady=2)

        self.visibility_label = ttk.Label(right_col, text="Visibility: -- mi")
        self.visibility_label.pack(anchor='w', pady=2)

        self.dewpoint_label = ttk.Label(right_col, text="Dew Point: --°F")
        self.dewpoint_label.pack(anchor='w', pady=2)

        # Propagation conditions (for ham radio operators)
        prop_frame = ttk.LabelFrame(main_frame, text="Radio Propagation", padding=10)
        prop_frame.pack(fill='x', pady=5)

        self.prop_label = ttk.Label(prop_frame, text="", font=('', 10))
        self.prop_label.pack(anchor='w')

        # Last updated
        self.updated_label = ttk.Label(main_frame, text="",
                                      font=('', 8),
                                      foreground=get_muted_color(self.config))
        self.updated_label.pack(anchor='w', pady=(10, 0))

        # Instructions
        help_frame = ttk.Frame(main_frame)
        help_frame.pack(side='bottom', fill='x', pady=(10, 0))

        help_text = "💡 Set your zip code in Settings → Station Information to see local weather"
        ttk.Label(help_frame, text=help_text,
                 font=('', 9),
                 foreground=get_muted_color(self.config),
                 wraplength=600).pack(anchor='w')

    def refresh_weather(self):
        """Fetch and display current weather"""
        zip_code = self.config.get('zip_code', '').strip()

        if not zip_code:
            messagebox.showwarning(
                "Zip Code Required",
                "Please set your zip code in Settings → Station Information first."
            )
            return

        try:
            # First, get coordinates from zip code using zippopotam.us (free, no key)
            coords = self.get_coordinates_from_zip(zip_code)
            if not coords:
                messagebox.showerror(
                    "Invalid Zip Code",
                    f"Could not find location for zip code: {zip_code}"
                )
                return

            lat, lon, location_name = coords

            # Fetch weather from Open-Meteo API (free, no key required)
            weather = self.fetch_weather(lat, lon)

            if weather:
                self.display_weather(weather, location_name)
                self.weather_data = weather
            else:
                messagebox.showerror(
                    "Weather Fetch Failed",
                    "Could not retrieve weather data. Please try again."
                )

        except Exception as e:
            messagebox.showerror("Error", f"Weather fetch error:\n{str(e)}")

    def get_coordinates_from_zip(self, zip_code):
        """Convert US zip code to lat/lon coordinates"""
        try:
            # Using zippopotam.us - free geocoding API, no key required
            url = f"http://api.zippopotam.us/us/{zip_code}"
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                data = response.json()
                place = data['places'][0]
                lat = float(place['latitude'])
                lon = float(place['longitude'])
                location_name = f"{place['place name']}, {place['state abbreviation']}"
                return (lat, lon, location_name)
            else:
                return None

        except Exception as e:
            print(f"Geocoding error: {e}")
            return None

    def fetch_weather(self, lat, lon):
        """Fetch weather from Open-Meteo API"""
        try:
            # Open-Meteo API - free, open source, no API key required
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                'latitude': lat,
                'longitude': lon,
                'current': 'temperature_2m,relative_humidity_2m,apparent_temperature,'
                          'precipitation,weather_code,pressure_msl,wind_speed_10m,'
                          'wind_direction_10m',
                'temperature_unit': 'fahrenheit',
                'wind_speed_unit': 'mph',
                'precipitation_unit': 'inch',
                'timezone': 'auto'
            }

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                return response.json()
            else:
                return None

        except Exception as e:
            print(f"Weather fetch error: {e}")
            return None

    def display_weather(self, weather, location_name):
        """Display weather data in the interface"""
        try:
            current = weather['current']

            # Location
            self.location_label.config(text=f"📍 {location_name}")

            # Temperature
            temp = current.get('temperature_2m', 0)
            self.temp_label.config(text=f"{temp:.0f}°F")

            # Weather condition from WMO code
            weather_code = current.get('weather_code', 0)
            condition = self.get_weather_description(weather_code)
            self.conditions_label.config(text=condition)

            # Feels like
            feels_like = current.get('apparent_temperature', temp)
            self.feels_like_label.config(text=f"Feels Like: {feels_like:.0f}°F")

            # Humidity
            humidity = current.get('relative_humidity_2m', 0)
            self.humidity_label.config(text=f"Humidity: {humidity}%")

            # Pressure (convert hPa to inHg)
            pressure_hpa = current.get('pressure_msl', 1013)
            pressure_inhg = pressure_hpa * 0.02953
            self.pressure_label.config(text=f"Pressure: {pressure_inhg:.2f} inHg")

            # Wind
            wind_speed = current.get('wind_speed_10m', 0)
            wind_dir = current.get('wind_direction_10m', 0)
            wind_dir_text = self.get_wind_direction(wind_dir)
            self.wind_label.config(text=f"Wind: {wind_speed:.0f} mph {wind_dir_text}")

            # Visibility (not provided by Open-Meteo, estimate from conditions)
            visibility = self.estimate_visibility(weather_code)
            self.visibility_label.config(text=f"Visibility: {visibility} mi")

            # Dew point (approximate calculation)
            dew_point = self.calculate_dew_point(temp, humidity)
            self.dewpoint_label.config(text=f"Dew Point: {dew_point:.0f}°F")

            # Radio propagation assessment
            prop_text = self.assess_propagation(temp, humidity, pressure_inhg, weather_code)
            self.prop_label.config(text=prop_text)

            # Last updated
            updated_time = datetime.now().strftime('%I:%M %p')
            self.updated_label.config(text=f"Last updated: {updated_time}")

        except Exception as e:
            print(f"Display error: {e}")

    def get_weather_description(self, code):
        """Convert WMO weather code to description"""
        weather_codes = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Foggy",
            48: "Depositing rime fog",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            71: "Slight snow",
            73: "Moderate snow",
            75: "Heavy snow",
            77: "Snow grains",
            80: "Slight rain showers",
            81: "Moderate rain showers",
            82: "Violent rain showers",
            85: "Slight snow showers",
            86: "Heavy snow showers",
            95: "Thunderstorm",
            96: "Thunderstorm with slight hail",
            99: "Thunderstorm with heavy hail"
        }
        return weather_codes.get(code, "Unknown")

    def get_wind_direction(self, degrees):
        """Convert wind direction degrees to compass direction"""
        directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                     "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
        index = int((degrees + 11.25) / 22.5) % 16
        return directions[index]

    def estimate_visibility(self, weather_code):
        """Estimate visibility based on weather conditions"""
        if weather_code in [0, 1]:
            return "10+"
        elif weather_code in [2, 3]:
            return "10"
        elif weather_code in [45, 48]:
            return "0.5"
        elif weather_code in [51, 53, 55, 61]:
            return "5"
        elif weather_code in [63, 65, 71, 73]:
            return "2"
        elif weather_code in [75, 95, 96, 99]:
            return "1"
        else:
            return "10"

    def calculate_dew_point(self, temp_f, humidity):
        """Calculate dew point using Magnus formula"""
        # Convert F to C
        temp_c = (temp_f - 32) * 5/9

        # Magnus formula
        a = 17.27
        b = 237.7
        alpha = ((a * temp_c) / (b + temp_c)) + (humidity / 100.0)
        dew_point_c = (b * alpha) / (a - alpha)

        # Convert back to F
        dew_point_f = (dew_point_c * 9/5) + 32
        return dew_point_f

    def assess_propagation(self, temp, humidity, pressure, weather_code):
        """Assess HF propagation conditions based on weather"""
        conditions = []

        # Temperature effects on local noise
        if temp < 32:
            conditions.append("⛄ Cold weather may increase static noise")
        elif temp > 85:
            conditions.append("☀️ Hot weather - watch for thunderstorms")

        # Humidity effects
        if humidity > 80:
            conditions.append("💧 High humidity may affect antenna efficiency")
        elif humidity < 30:
            conditions.append("🏜️ Low humidity - good antenna conditions")

        # Pressure effects on tropospheric ducting
        if pressure > 30.20:
            conditions.append("📡 High pressure - possible VHF/UHF ducting")
        elif pressure < 29.80:
            conditions.append("🌀 Low pressure - stormy conditions likely")

        # Weather effects
        if weather_code in [95, 96, 99]:
            conditions.append("⚡ Thunderstorms - high noise levels, QRN")
        elif weather_code in [51, 53, 55, 61, 63, 65]:
            conditions.append("🌧️ Rain - possible increased QRN")
        elif weather_code == 0:
            conditions.append("✅ Clear conditions - good propagation")

        if not conditions:
            conditions.append("📻 Conditions normal for local operations")

        return "\n".join(f"  • {c}" for c in conditions)

    def start_auto_refresh(self):
        """Start automatic hourly weather refresh"""
        # Refresh every hour (3600000 milliseconds)
        self.auto_refresh_id = self.frame.after(3600000, self.auto_refresh_weather)

    def auto_refresh_weather(self):
        """Auto-refresh callback - silently refresh weather"""
        zip_code = self.config.get('zip_code', '').strip()
        if zip_code:
            try:
                # Silently refresh without showing errors
                coords = self.get_coordinates_from_zip(zip_code)
                if coords:
                    lat, lon, location_name = coords
                    weather = self.fetch_weather(lat, lon)
                    if weather:
                        self.display_weather(weather, location_name)
                        self.weather_data = weather
            except:
                # Silently fail - don't interrupt user
                pass

        # Schedule next refresh
        self.start_auto_refresh()

    def stop_auto_refresh(self):
        """Stop automatic refresh (called on window close)"""
        if self.auto_refresh_id:
            self.frame.after_cancel(self.auto_refresh_id)
            self.auto_refresh_id = None

    def get_frame(self):
        """Return the frame for this tab"""
        return self.frame
