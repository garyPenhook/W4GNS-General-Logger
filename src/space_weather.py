"""
Space Weather Data Client
Fetches solar and geomagnetic data relevant to HF radio propagation

Data sources:
- HamQSL.com (N0NBH) - Comprehensive ham radio space weather
- NOAA Space Weather Prediction Center - Official government data
"""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta


class SpaceWeatherClient:
    """Client for fetching space weather data from multiple sources"""

    # HamQSL.com provides excellent ham radio-specific data
    HAMQSL_URL = "https://www.hamqsl.com/solarxml.php"

    # NOAA Space Weather Prediction Center JSON APIs
    NOAA_SOLAR_FLUX = "https://services.swpc.noaa.gov/json/f107_cm_flux.json"
    NOAA_KP_INDEX = "https://services.swpc.noaa.gov/json/planetary_k_index_1m.json"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'W4GNS-General-Logger/1.0'
        })
        self.cache = {}
        self.cache_timeout = 300  # 5 minutes

    def get_hamqsl_data(self):
        """
        Fetch comprehensive space weather from HamQSL.com

        Returns dict with:
        - solar_flux: 10.7cm solar flux (SFI)
        - sunspot_number: Current sunspot count
        - a_index: Planetary A-index (daily geomagnetic activity)
        - k_index: Planetary K-index (3-hour geomagnetic activity)
        - x_ray: Solar X-ray flux class
        - geomag_field: Geomagnetic field status
        - solar_wind: Solar wind speed (km/s)
        - helium_line: Helium line measurement
        - proton_flux: Proton flux
        - electron_flux: Electron flux
        - aurora: Aurora activity level
        - signal_noise: Radio signal noise level
        - band_conditions: HF band conditions (day/night)
        - updated: Data timestamp
        """

        # Check cache
        cache_key = 'hamqsl'
        if cache_key in self.cache:
            cached_time, cached_data = self.cache[cache_key]
            if (datetime.now() - cached_time).seconds < self.cache_timeout:
                return cached_data

        try:
            response = self.session.get(self.HAMQSL_URL, timeout=10)
            response.raise_for_status()

            # Parse XML
            root = ET.fromstring(response.content)

            data = {
                'solar_flux': self._get_int(root, 'solarflux'),
                'sunspot_number': self._get_int(root, 'sunspots'),
                'a_index': self._get_int(root, 'aindex'),
                'k_index': self._get_int(root, 'kindex'),
                'x_ray': self._get_text(root, 'xray'),
                'geomag_field': self._get_text(root, 'geomagfield'),
                'solar_wind': self._get_float(root, 'solarwind'),
                'helium_line': self._get_float(root, 'heliumline'),
                'proton_flux': self._get_int(root, 'protonflux'),
                'electron_flux': self._get_int(root, 'electonflux'),  # Note: typo in source XML
                'aurora': self._get_int(root, 'aurora'),
                'signal_noise': self._get_text(root, 'signalnoise'),
                'updated': self._get_text(root, 'updated'),
                'band_conditions': {
                    'day': self._parse_band_conditions(root, 'calculatedconditions/band'),
                    'night': self._parse_band_conditions(root, 'calculatedvhfconditions/phenomenon')
                }
            }

            # Cache the result
            self.cache[cache_key] = (datetime.now(), data)
            return data

        except Exception as e:
            print(f"Error fetching HamQSL data: {e}")
            return None

    def _get_text(self, root, path):
        """Get text from XML element"""
        elem = root.find(path)
        return elem.text if elem is not None else 'N/A'

    def _get_int(self, root, path):
        """Get integer from XML element"""
        elem = root.find(path)
        try:
            return int(elem.text) if elem is not None else 0
        except (ValueError, TypeError):
            return 0

    def _get_float(self, root, path):
        """Get float from XML element"""
        elem = root.find(path)
        try:
            return float(elem.text) if elem is not None else 0.0
        except (ValueError, TypeError):
            return 0.0

    def _parse_band_conditions(self, root, base_path):
        """Parse HF band conditions"""
        conditions = {}
        bands_elem = root.find(base_path)
        if bands_elem is not None:
            for band_elem in bands_elem:
                band_name = band_elem.get('name', '')
                band_time = band_elem.get('time', '')
                condition = band_elem.text
                if band_name:
                    conditions[f"{band_name}_{band_time}"] = condition
        return conditions

    def interpret_solar_flux(self, sfi):
        """
        Interpret Solar Flux Index for propagation

        SFI < 70: Very Poor
        70-79: Poor
        80-89: Fair
        90-139: Good
        140-179: Very Good
        180+: Excellent
        """
        if sfi < 70:
            return "Very Poor", "#d32f2f"
        elif sfi < 80:
            return "Poor", "#f57c00"
        elif sfi < 90:
            return "Fair", "#fbc02d"
        elif sfi < 140:
            return "Good", "#7cb342"
        elif sfi < 180:
            return "Very Good", "#388e3c"
        else:
            return "Excellent", "#1976d2"

    def interpret_k_index(self, k):
        """
        Interpret K-Index for propagation

        0-1: Very Quiet, Excellent for HF
        2: Quiet, Good for HF
        3: Unsettled, Fair for HF
        4: Active, Poor for HF
        5-6: Minor Storm, Very Poor for HF
        7-9: Major Storm, Extremely Poor for HF
        """
        if k <= 1:
            return "Very Quiet", "#388e3c"
        elif k == 2:
            return "Quiet", "#7cb342"
        elif k == 3:
            return "Unsettled", "#fbc02d"
        elif k == 4:
            return "Active", "#f57c00"
        elif k <= 6:
            return "Minor Storm", "#e64a19"
        else:
            return "Major Storm", "#d32f2f"

    def interpret_a_index(self, a):
        """
        Interpret A-Index for propagation

        0-7: Quiet
        8-15: Unsettled
        16-29: Active
        30-49: Minor Storm
        50-99: Major Storm
        100+: Severe Storm
        """
        if a <= 7:
            return "Quiet", "#388e3c"
        elif a <= 15:
            return "Unsettled", "#7cb342"
        elif a <= 29:
            return "Active", "#fbc02d"
        elif a <= 49:
            return "Minor Storm", "#f57c00"
        elif a <= 99:
            return "Major Storm", "#e64a19"
        else:
            return "Severe Storm", "#d32f2f"

    def interpret_sunspots(self, ssn):
        """
        Interpret Sunspot Number for propagation

        0-5: Very Low Activity
        6-20: Low Activity
        21-50: Moderate Activity
        51-100: High Activity
        101-150: Very High Activity
        150+: Extreme Activity
        """
        if ssn <= 5:
            return "Very Low", "#d32f2f"
        elif ssn <= 20:
            return "Low", "#f57c00"
        elif ssn <= 50:
            return "Moderate", "#fbc02d"
        elif ssn <= 100:
            return "High", "#7cb342"
        elif ssn <= 150:
            return "Very High", "#388e3c"
        else:
            return "Extreme", "#1976d2"

    def get_propagation_summary(self, data):
        """
        Generate overall propagation summary

        Returns: (rating, color, description)
        """
        if not data:
            return "Unknown", "#757575", "No data available"

        sfi = data.get('solar_flux', 0)
        k = data.get('k_index', 0)
        a = data.get('a_index', 0)

        # Calculate weighted score
        # High SFI is good, low K/A is good
        sfi_score = min(sfi / 180 * 100, 100)  # 0-100
        k_score = max(0, 100 - (k * 12.5))      # 0-100 (lower K is better)
        a_score = max(0, 100 - (a * 2))         # 0-100 (lower A is better)

        overall = (sfi_score * 0.5 + k_score * 0.3 + a_score * 0.2)

        if overall >= 80:
            return "Excellent", "#388e3c", "Ideal conditions for HF propagation"
        elif overall >= 60:
            return "Good", "#7cb342", "Good conditions for HF propagation"
        elif overall >= 40:
            return "Fair", "#fbc02d", "Fair conditions, some absorption possible"
        elif overall >= 20:
            return "Poor", "#f57c00", "Poor conditions, high absorption likely"
        else:
            return "Very Poor", "#d32f2f", "Very poor conditions, severe absorption"
