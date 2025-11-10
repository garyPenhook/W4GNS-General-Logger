"""
Space Weather Data Client
Fetches solar and geomagnetic data relevant to HF radio propagation

Data sources:
- HamQSL.com (N0NBH) - Comprehensive ham radio space weather
- NOAA Space Weather Prediction Center - Official government data
- NASA DONKI - Space weather event alerts and forecasts
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

    # NASA DONKI (Database Of Notifications, Knowledge, Information) APIs
    DONKI_BASE_URL = "https://api.nasa.gov/DONKI"
    DONKI_FLARES = f"{DONKI_BASE_URL}/FLR"
    DONKI_CME = f"{DONKI_BASE_URL}/CME"
    DONKI_GST = f"{DONKI_BASE_URL}/GST"
    DONKI_SEP = f"{DONKI_BASE_URL}/SEP"

    def __init__(self, config=None):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'W4GNS-General-Logger/1.0'
        })
        self.cache = {}
        self.cache_timeout = 300  # 5 minutes for HamQSL/NOAA

        # Get NASA API key from config (fallback to DEMO_KEY)
        self.nasa_api_key = "DEMO_KEY"
        if config:
            self.nasa_api_key = config.get('nasa.api_key', 'DEMO_KEY')
            # DONKI cache timeout in seconds (default 24 hours)
            donki_cache_hours = config.get('nasa.donki_cache_hours', 24)
            self.donki_cache_timeout = donki_cache_hours * 3600
        else:
            self.donki_cache_timeout = 86400  # 24 hours default

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

        # Try up to 3 times with exponential backoff
        max_retries = 3
        retry_delay = 1  # seconds

        for attempt in range(max_retries):
            try:
                response = self.session.get(self.HAMQSL_URL, timeout=10)
                response.raise_for_status()

                # Parse XML - data is nested inside <solar><solardata>
                root = ET.fromstring(response.content)
                solardata = root.find('solardata')
                if solardata is None:
                    print("Error: Could not find <solardata> element in XML")
                    return None

                # Success, break out of retry loop
                break

            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    print(f"Timeout fetching space weather, retrying in {retry_delay}s...")
                    import time
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                    continue
                else:
                    print("Error: Timeout fetching HamQSL data after retries")
                    return None

            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    print(f"Network error ({e}), retrying in {retry_delay}s...")
                    import time
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                else:
                    print(f"Error fetching HamQSL data: {e}")
                    return None

        try:
            data = {
                'solar_flux': self._get_int(solardata, 'solarflux'),
                'sunspot_number': self._get_int(solardata, 'sunspots'),
                'a_index': self._get_int(solardata, 'aindex'),
                'k_index': self._get_int(solardata, 'kindex'),
                'x_ray': self._get_text(solardata, 'xray'),
                'geomag_field': self._get_text(solardata, 'geomagfield'),
                'solar_wind': self._get_float(solardata, 'solarwind'),
                'helium_line': self._get_float(solardata, 'heliumline'),
                'proton_flux': self._get_int(solardata, 'protonflux'),
                'electron_flux': self._get_int(solardata, 'electonflux'),  # Note: typo in source XML
                'aurora': self._get_int(solardata, 'aurora'),
                'signal_noise': self._get_text(solardata, 'signalnoise'),
                'updated': self._get_text(solardata, 'updated'),
                'band_conditions': {
                    'day': self._parse_band_conditions(solardata, 'calculatedconditions/band'),
                    'night': self._parse_band_conditions(solardata, 'calculatedvhfconditions/phenomenon')
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
        return elem.text.strip() if elem is not None and elem.text else 'N/A'

    def _get_int(self, root, path):
        """Get integer from XML element"""
        elem = root.find(path)
        try:
            if elem is not None and elem.text:
                return int(elem.text.strip())
            return 0
        except (ValueError, TypeError):
            return 0

    def _get_float(self, root, path):
        """Get float from XML element"""
        elem = root.find(path)
        try:
            if elem is not None and elem.text:
                return float(elem.text.strip())
            return 0.0
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

    def get_donki_events(self, days=7):
        """
        Fetch space weather events from NASA DONKI

        Args:
            days: Number of days to look back (default 7)

        Returns dict with:
            - solar_flares: List of recent solar flare events
            - cmes: List of coronal mass ejections
            - geomagnetic_storms: List of geomagnetic storms
            - sep_events: List of solar energetic particle events
            - updated: Timestamp of data fetch
        """
        # Check cache (use longer timeout for DONKI)
        cache_key = 'donki_events'
        if cache_key in self.cache:
            cached_time, cached_data = self.cache[cache_key]
            elapsed = (datetime.now() - cached_time).total_seconds()
            if elapsed < self.donki_cache_timeout:
                return cached_data

        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        date_params = {
            'startDate': start_date.strftime('%Y-%m-%d'),
            'endDate': end_date.strftime('%Y-%m-%d'),
            'api_key': self.nasa_api_key
        }

        events = {
            'solar_flares': [],
            'cmes': [],
            'geomagnetic_storms': [],
            'sep_events': [],
            'updated': datetime.now().isoformat()
        }

        # Fetch solar flares
        try:
            response = self.session.get(self.DONKI_FLARES, params=date_params, timeout=10)
            response.raise_for_status()
            flares = response.json()

            # Filter to significant flares (M-class and above)
            for flare in flares:
                class_type = flare.get('classType', '')
                if class_type and (class_type.startswith('M') or class_type.startswith('X')):
                    linked = flare.get('linkedEvents')
                    events['solar_flares'].append({
                        'time': flare.get('beginTime', ''),
                        'peak_time': flare.get('peakTime', ''),
                        'class': class_type,
                        'location': flare.get('sourceLocation', 'Unknown'),
                        'region': flare.get('activeRegionNum', 'N/A'),
                        'linked_events': len(linked) > 0 if linked else False
                    })
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                print("NASA API rate limit exceeded. Using cached data if available. Get your free API key at https://api.nasa.gov/")
            else:
                print(f"HTTP Error fetching DONKI solar flares: {e}")
        except Exception as e:
            print(f"Error fetching DONKI solar flares: {e}")

        # Fetch CMEs
        try:
            response = self.session.get(self.DONKI_CME, params=date_params, timeout=10)
            response.raise_for_status()
            cmes = response.json()

            # Get recent significant CMEs
            for cme in cmes[:10]:  # Limit to 10 most recent
                # Get analysis data
                analyses = cme.get('cmeAnalyses', [])
                speed = 0
                if analyses:
                    analysis = analyses[0]  # Most accurate analysis
                    speed = analysis.get('speed', 0)

                linked = cme.get('linkedEvents')
                events['cmes'].append({
                    'time': cme.get('startTime', ''),
                    'location': cme.get('sourceLocation', 'Unknown'),
                    'speed': speed,
                    'note': cme.get('note', ''),
                    'linked_events': len(linked) > 0 if linked else False
                })
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                print("NASA API rate limit exceeded (CME data). Using cached data if available.")
            else:
                print(f"HTTP Error fetching DONKI CMEs: {e}")
        except Exception as e:
            print(f"Error fetching DONKI CMEs: {e}")

        # Fetch Geomagnetic Storms
        try:
            response = self.session.get(self.DONKI_GST, params=date_params, timeout=10)
            response.raise_for_status()
            storms = response.json()

            for storm in storms:
                # Get max Kp value
                kp_values = storm.get('allKpIndex', [])
                max_kp = 0
                if kp_values:
                    max_kp = max(kp.get('kpIndex', 0) for kp in kp_values)

                linked = storm.get('linkedEvents')
                events['geomagnetic_storms'].append({
                    'time': storm.get('startTime', ''),
                    'max_kp': max_kp,
                    'linked_events': len(linked) > 0 if linked else False
                })
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                print("NASA API rate limit exceeded (Geomagnetic storm data). Using cached data if available.")
            else:
                print(f"HTTP Error fetching DONKI geomagnetic storms: {e}")
        except Exception as e:
            print(f"Error fetching DONKI geomagnetic storms: {e}")

        # Fetch Solar Energetic Particle (SEP) Events
        try:
            response = self.session.get(self.DONKI_SEP, params=date_params, timeout=10)
            response.raise_for_status()
            sep_events = response.json()

            for sep in sep_events[:5]:  # Limit to 5 most recent
                linked = sep.get('linkedEvents')
                events['sep_events'].append({
                    'time': sep.get('eventTime', ''),
                    'instruments': ', '.join([i.get('displayName', '') for i in sep.get('instruments', [])[:2]]),
                    'linked_events': len(linked) > 0 if linked else False
                })
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                print("NASA API rate limit exceeded (SEP data). Using cached data if available.")
            else:
                print(f"HTTP Error fetching DONKI SEP events: {e}")
        except Exception as e:
            print(f"Error fetching DONKI SEP events: {e}")

        # Cache the result
        self.cache[cache_key] = (datetime.now(), events)
        return events

    def interpret_solar_flare(self, flare_class):
        """
        Interpret solar flare class for HF radio impact

        Flare classes: A, B, C, M, X (each 10x stronger)
        Returns: (severity, color, description)
        """
        if not flare_class:
            return "Unknown", "#757575", "Unknown class"

        class_letter = flare_class[0].upper()

        if class_letter == 'X':
            return "Extreme", "#d32f2f", "Major HF radio blackouts possible"
        elif class_letter == 'M':
            return "High", "#f57c00", "Moderate HF radio blackouts possible"
        elif class_letter == 'C':
            return "Moderate", "#fbc02d", "Minor HF impacts possible"
        elif class_letter == 'B':
            return "Low", "#7cb342", "Minimal HF impact"
        else:  # A
            return "Minimal", "#388e3c", "No significant HF impact"

    def interpret_cme_speed(self, speed):
        """
        Interpret CME speed for Earth impact potential

        Args:
            speed: CME speed in km/s

        Returns: (severity, color, description)
        """
        if speed < 300:
            return "Slow", "#388e3c", "Unlikely to cause disturbances"
        elif speed < 500:
            return "Moderate", "#7cb342", "Minor geomagnetic activity possible"
        elif speed < 1000:
            return "Fast", "#fbc02d", "Geomagnetic storm possible if Earth-directed"
        elif speed < 2000:
            return "Very Fast", "#f57c00", "Major geomagnetic storm likely if Earth-directed"
        else:
            return "Extreme", "#d32f2f", "Severe geomagnetic storm likely if Earth-directed"

    def get_event_summary(self, events):
        """
        Generate summary of recent space weather events

        Returns: (alert_level, color, message)
        """
        if not events:
            return "Normal", "#388e3c", "No significant space weather events"

        # Count significant events
        x_flares = sum(1 for f in events.get('solar_flares', []) if f['class'].startswith('X'))
        m_flares = sum(1 for f in events.get('solar_flares', []) if f['class'].startswith('M'))
        fast_cmes = sum(1 for c in events.get('cmes', []) if c['speed'] > 1000)
        storms = len(events.get('geomagnetic_storms', []))

        # Determine alert level
        if x_flares > 0 or fast_cmes > 2 or storms > 1:
            return "High Alert", "#d32f2f", f"{x_flares} X-flares, {fast_cmes} fast CMEs, {storms} geomagnetic storms"
        elif m_flares > 3 or fast_cmes > 0 or storms > 0:
            return "Elevated", "#f57c00", f"{m_flares} M-flares, {fast_cmes} fast CMEs, {storms} geomagnetic storms"
        elif m_flares > 0:
            return "Minor Activity", "#fbc02d", f"{m_flares} M-flares detected"
        else:
            return "Normal", "#388e3c", "No significant space weather events"
