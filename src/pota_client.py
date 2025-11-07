"""
POTA (Parks on the Air) API Client
Fetches activator spots from the POTA API
"""

import requests
import logging
import time
from datetime import datetime


logger = logging.getLogger(__name__)


class POTAClient:
    """Client for fetching POTA spots from the official API"""

    BASE_URL = "https://api.pota.app"
    SPOTS_ENDPOINT = "/spot/activator"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'W4GNS-General-Logger/1.0'
        })

    def get_spots(self):
        """
        Fetch current POTA activator spots

        Returns:
            list: List of spot dictionaries with fields:
                - spotId: Unique spot ID
                - activator: Callsign of the activator
                - frequency: Frequency in kHz
                - mode: Operating mode (SSB, CW, FT8, etc.)
                - reference: Park reference (e.g., US-2298)
                - name: Park name
                - locationDesc: Location (state/country)
                - spotTime: ISO 8601 timestamp
                - spotter: Callsign of spotter
                - comments: Additional comments
                - grid4: 4-character grid square
                - grid6: 6-character grid square
                - latitude: Park latitude
                - longitude: Park longitude
                - count: Number of QSOs
                - expire: Time until expiration in seconds
        """
        # Retry configuration
        max_retries = 3
        retry_delays = [2, 4, 8]  # Exponential backoff in seconds

        for attempt in range(max_retries):
            try:
                url = f"{self.BASE_URL}{self.SPOTS_ENDPOINT}"
                # Increased timeout to 30 seconds
                response = self.session.get(url, timeout=30)
                response.raise_for_status()

                spots = response.json()
                break  # Success, exit retry loop

            except requests.exceptions.Timeout as e:
                if attempt < max_retries - 1:
                    delay = retry_delays[attempt]
                    logger.warning(f"POTA API timeout (attempt {attempt + 1}/{max_retries}), retrying in {delay}s...")
                    time.sleep(delay)
                    continue
                else:
                    logger.error(f"Error fetching POTA spots after {max_retries} attempts: {e}")
                    return []
            except requests.exceptions.RequestException as e:
                logger.error(f"Error fetching POTA spots: {e}")
                return []

        # Parse and enrich spot data
        try:
            processed_spots = []
            for spot in spots:
                # Convert frequency to MHz for consistency
                freq_khz = float(spot.get('frequency', '0'))
                freq_mhz = freq_khz / 1000.0

                # Determine band from frequency
                band = self._frequency_to_band(freq_mhz)

                # Format the spot data
                processed_spot = {
                    'spot_id': spot.get('spotId'),
                    'activator': spot.get('activator', '').upper(),
                    'frequency': f"{freq_mhz:.3f}",
                    'frequency_khz': freq_khz,
                    'mode': spot.get('mode', ''),
                    'park_ref': spot.get('reference', ''),
                    'park_name': spot.get('name', ''),
                    'location': spot.get('locationDesc', ''),
                    'spot_time': spot.get('spotTime', ''),
                    'spotter': spot.get('spotter', ''),
                    'comments': spot.get('comments', ''),
                    'grid': spot.get('grid6') or spot.get('grid4', ''),
                    'latitude': spot.get('latitude'),
                    'longitude': spot.get('longitude'),
                    'qso_count': spot.get('count', 0),
                    'expire_seconds': spot.get('expire', 0),
                    'band': band,
                    'source': spot.get('source', 'POTA')
                }

                processed_spots.append(processed_spot)

            logger.info(f"Retrieved {len(processed_spots)} POTA spots")
            return processed_spots

        except Exception as e:
            logger.error(f"Error processing POTA spots: {e}")
            return []

    def _frequency_to_band(self, freq_mhz):
        """Convert frequency in MHz to band name"""
        if 1.8 <= freq_mhz < 2.0:
            return '160m'
        elif 3.5 <= freq_mhz < 4.0:
            return '80m'
        elif 5.0 <= freq_mhz < 5.5:
            return '60m'
        elif 7.0 <= freq_mhz < 7.3:
            return '40m'
        elif 10.1 <= freq_mhz < 10.15:
            return '30m'
        elif 14.0 <= freq_mhz < 14.35:
            return '20m'
        elif 18.068 <= freq_mhz < 18.168:
            return '17m'
        elif 21.0 <= freq_mhz < 21.45:
            return '15m'
        elif 24.89 <= freq_mhz < 24.99:
            return '12m'
        elif 28.0 <= freq_mhz < 29.7:
            return '10m'
        elif 50.0 <= freq_mhz < 54.0:
            return '6m'
        elif 144.0 <= freq_mhz < 148.0:
            return '2m'
        elif 420.0 <= freq_mhz < 450.0:
            return '70cm'
        else:
            return ''

    def format_spot_time(self, iso_time):
        """Format ISO 8601 time to human-readable format"""
        try:
            dt = datetime.fromisoformat(iso_time.replace('Z', '+00:00'))
            return dt.strftime('%H:%M:%S')
        except (ValueError, AttributeError) as e:
            # ValueError for invalid ISO format, AttributeError for None/non-string
            print(f"Invalid time format '{iso_time}': {e}")
            return iso_time if iso_time else "N/A"
