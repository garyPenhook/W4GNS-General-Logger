"""
POTA (Parks on the Air) API Client
Fetches activator spots from the POTA API with async support for better performance
"""

import requests
import logging
import time
from datetime import datetime

# Optional async support
try:
    import asyncio
    import aiohttp
    ASYNC_AVAILABLE = True
except ImportError:
    ASYNC_AVAILABLE = False


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
        # Retry configuration with 4 retries (matching git best practices)
        max_retries = 4
        retry_delays = [2, 4, 8, 16]  # Exponential backoff in seconds

        spots = []

        for attempt in range(max_retries):
            try:
                url = f"{self.BASE_URL}{self.SPOTS_ENDPOINT}"
                # Timeout set to 30 seconds for potentially large response
                response = self.session.get(url, timeout=30)
                response.raise_for_status()

                spots = response.json()
                break  # Success, exit retry loop

            except requests.exceptions.Timeout as e:
                if attempt < max_retries - 1:
                    delay = retry_delays[attempt]
                    logger.warning(f"POTA API timeout (attempt {attempt + 1}/{max_retries}), retrying in {delay}s...")
                    print(f"POTA API timeout (attempt {attempt + 1}/{max_retries}), retrying in {delay}s...")
                    time.sleep(delay)
                    continue
                else:
                    logger.error(f"Error: POTA API timeout after {max_retries} attempts. Check your internet connection.")
                    print(f"Error: POTA API timeout after {max_retries} attempts. Check your internet connection.")
                    return []

            except requests.exceptions.ConnectionError as e:
                if attempt < max_retries - 1:
                    delay = retry_delays[attempt]
                    error_msg = str(e)
                    # Check for DNS resolution errors
                    if 'Name or service not known' in error_msg or 'Failed to resolve' in error_msg:
                        logger.warning(f"DNS resolution error for api.pota.app (attempt {attempt + 1}/{max_retries}), retrying in {delay}s...")
                        print(f"DNS resolution error for api.pota.app (attempt {attempt + 1}/{max_retries}), retrying in {delay}s...")
                    else:
                        logger.warning(f"Connection error to POTA API (attempt {attempt + 1}/{max_retries}), retrying in {delay}s...")
                        print(f"Connection error to POTA API (attempt {attempt + 1}/{max_retries}), retrying in {delay}s...")
                    time.sleep(delay)
                    continue
                else:
                    if 'Name or service not known' in str(e) or 'Failed to resolve' in str(e):
                        logger.error(f"Error: Cannot resolve api.pota.app after {max_retries} attempts. Check DNS settings or internet connection.")
                        print(f"Error: Cannot resolve api.pota.app after {max_retries} attempts. Check DNS settings or internet connection.")
                    else:
                        logger.error(f"Error: Cannot connect to POTA API after {max_retries} attempts: {e}")
                        print(f"Error: Cannot connect to POTA API after {max_retries} attempts: {e}")
                    return []

            except requests.exceptions.HTTPError as e:
                # Don't retry on HTTP errors (4xx, 5xx)
                logger.error(f"HTTP Error fetching POTA spots: {e}")
                print(f"HTTP Error fetching POTA spots: {e}")
                return []

            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    delay = retry_delays[attempt]
                    logger.warning(f"Network error connecting to POTA API (attempt {attempt + 1}/{max_retries}), retrying in {delay}s...")
                    print(f"Network error connecting to POTA API (attempt {attempt + 1}/{max_retries}), retrying in {delay}s...")
                    time.sleep(delay)
                    continue
                else:
                    logger.error(f"Error: Network error fetching POTA spots after {max_retries} attempts: {e}")
                    print(f"Error: Network error fetching POTA spots after {max_retries} attempts: {e}")
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

    # Python data model methods for context manager protocol
    def __enter__(self):
        """Enable context manager: with POTAClient() as client:"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Automatic cleanup when exiting context"""
        if self.session:
            self.session.close()
        return False  # Don't suppress exceptions

    def __repr__(self):
        """Developer-friendly representation"""
        async_status = " [async available]" if ASYNC_AVAILABLE else ""
        return f"<POTAClient(base_url={self.BASE_URL!r}{async_status})>"

    # Async I/O methods for improved performance
    async def get_spots_async(self):
        """
        Async version of get_spots() for non-blocking I/O

        Returns:
            list: List of spot dictionaries (same format as get_spots())

        Example:
            >>> async def main():
            ...     async with POTAClient() as client:
            ...         spots = await client.get_spots_async()
            ...         print(f"Got {len(spots)} spots")
            >>> asyncio.run(main())
        """
        if not ASYNC_AVAILABLE:
            logger.warning("Async support not available (aiohttp not installed), falling back to sync")
            return self.get_spots()

        max_retries = 4
        retry_delays = [2, 4, 8, 16]
        spots = []

        async with aiohttp.ClientSession() as session:
            for attempt in range(max_retries):
                try:
                    url = f"{self.BASE_URL}{self.SPOTS_ENDPOINT}"
                    headers = {'User-Agent': 'W4GNS-General-Logger/1.0'}

                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=30), headers=headers) as response:
                        response.raise_for_status()
                        spots = await response.json()
                        break  # Success

                except asyncio.TimeoutError:
                    if attempt < max_retries - 1:
                        delay = retry_delays[attempt]
                        logger.warning(f"POTA API timeout (attempt {attempt + 1}/{max_retries}), retrying in {delay}s...")
                        await asyncio.sleep(delay)
                        continue
                    else:
                        logger.error(f"POTA API timeout after {max_retries} attempts")
                        return []

                except aiohttp.ClientError as e:
                    if attempt < max_retries - 1:
                        delay = retry_delays[attempt]
                        logger.warning(f"Connection error to POTA API (attempt {attempt + 1}/{max_retries}), retrying in {delay}s...")
                        await asyncio.sleep(delay)
                        continue
                    else:
                        logger.error(f"Cannot connect to POTA API after {max_retries} attempts: {e}")
                        return []

                except Exception as e:
                    logger.error(f"Unexpected error fetching POTA spots: {e}")
                    return []

        # Process spots (same as sync version)
        try:
            processed_spots = []
            for spot in spots:
                freq_khz = float(spot.get('frequency', '0'))
                freq_mhz = freq_khz / 1000.0
                band = self._frequency_to_band(freq_mhz)

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

            logger.info(f"Retrieved {len(processed_spots)} POTA spots (async)")
            return processed_spots

        except Exception as e:
            logger.error(f"Error processing POTA spots: {e}")
            return []

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            self.session.close()
        return False
