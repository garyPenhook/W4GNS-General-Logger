"""
QRZ.com API Integration
Provides XML lookup and logbook upload functionality
"""

import xml.etree.ElementTree as ET
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime


class QRZSession:
    """Manage QRZ.com XML API session"""

    def __init__(self, username, password, use_post=False):
        self.username = username
        self.password = password
        self.session_key = None
        self.base_url = "https://xmldata.qrz.com/xml/current/"
        self.use_post = use_post  # Option to use POST instead of GET

    def login(self):
        """
        Login to QRZ and get session key

        Returns:
            (bool, str): (success, message)
        """
        try:
            # Per QRZ XML spec, include agent parameter (strongly recommended)
            # urlencode will properly handle special characters in password
            params = {
                'username': self.username,
                'password': self.password,
                'agent': 'W4GNS-General-Logger-1.0'
            }

            # QRZ supports both GET and POST
            if self.use_post:
                # POST method - better for passwords with special characters
                url = self.base_url
                data = urllib.parse.urlencode(params).encode('utf-8')
                request = urllib.request.Request(url, data=data, method='POST')
            else:
                # GET method (default)
                url = f"{self.base_url}?{urllib.parse.urlencode(params)}"
                request = urllib.request.Request(url)

            # Add proper User-Agent header
            request.add_header('User-Agent', 'W4GNS-General-Logger/1.0')

            with urllib.request.urlopen(request, timeout=10) as response:
                xml_data = response.read().decode('utf-8')

            # Debug: Print raw XML for troubleshooting
            print("QRZ Response XML:")
            print(xml_data)

            root = ET.fromstring(xml_data)

            # Check for session element
            session = root.find('.//Session')
            if session is None:
                # Show the actual response to help debug
                preview = xml_data[:200] if len(xml_data) > 200 else xml_data
                return False, f"QRZ login failed: No session element in response.\n\nReceived:\n{preview}..."

            # Check for error first (QRZ returns errors in Session/Error)
            error_elem = session.find('Error')
            if error_elem is not None and error_elem.text:
                return False, f"QRZ Error: {error_elem.text}"

            # Check for session key
            key_elem = session.find('Key')
            if key_elem is not None and key_elem.text:
                self.session_key = key_elem.text

                # Get subscription info if available
                sub_exp = session.find('SubExp')
                if sub_exp is not None and sub_exp.text:
                    if sub_exp.text == 'non-subscriber':
                        return True, "QRZ login successful (non-subscriber - limited access)"
                    return True, f"QRZ login successful (subscription expires: {sub_exp.text})"

                return True, "QRZ login successful"

            # No key and no error - unexpected response
            return False, "QRZ login failed: No session key in response. You may need an active QRZ XML subscription."

        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8', errors='ignore')
            return False, f"HTTP Error {e.code}: {e.reason}\n\nResponse:\n{error_body[:300]}"
        except urllib.error.URLError as e:
            return False, f"Network error: {str(e)}"
        except ET.ParseError as e:
            # XML parsing failed - show what we received
            return False, f"Invalid XML response from QRZ: {str(e)}\n\nThis might not be an XML response. Check if the URL is correct."
        except Exception as e:
            return False, f"Unexpected error: {type(e).__name__}: {str(e)}"

    def lookup_callsign(self, callsign):
        """
        Look up callsign information

        Args:
            callsign: Callsign to lookup

        Returns:
            dict with callsign data or None if not found
        """
        if not self.session_key:
            success, msg = self.login()
            if not success:
                return None

        try:
            params = urllib.parse.urlencode({
                's': self.session_key,
                'callsign': callsign.upper()
            })

            url = f"{self.base_url}?{params}"

            with urllib.request.urlopen(url, timeout=10) as response:
                xml_data = response.read().decode('utf-8')

            root = ET.fromstring(xml_data)

            # Check for errors
            session = root.find('.//Session')
            if session is not None:
                error_elem = session.find('Error')
                if error_elem is not None:
                    # Session may have expired, try logging in again
                    if 'session' in error_elem.text.lower():
                        success, _ = self.login()
                        if success:
                            return self.lookup_callsign(callsign)
                    return None

            # Parse callsign data
            call_elem = root.find('.//Callsign')
            if call_elem is None:
                return None

            data = {}

            # Map QRZ fields to our fields
            field_map = {
                'call': 'callsign',
                'fname': 'first_name',
                'name': 'name',
                'addr1': 'addr1',
                'addr2': 'addr2',
                'state': 'state',
                'zip': 'zip',
                'country': 'country',
                'lat': 'lat',
                'lon': 'lon',
                'grid': 'gridsquare',
                'county': 'county',
                'cqzone': 'cq_zone',
                'ituzone': 'itu_zone',
                'land': 'country',
                'efdate': 'license_date',
                'expdate': 'license_expiry',
                'class': 'license_class',
                'email': 'email'
            }

            for qrz_field, our_field in field_map.items():
                elem = call_elem.find(qrz_field)
                if elem is not None and elem.text:
                    data[our_field] = elem.text

            return data if data else None

        except Exception as e:
            print(f"QRZ lookup error: {e}")
            return None


class QRZLogbook:
    """Upload contacts to QRZ Logbook"""

    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://logbook.qrz.com/api"

    def upload_contact(self, contact_data):
        """
        Upload a contact to QRZ Logbook

        Args:
            contact_data: dict with contact information

        Returns:
            (bool, str): (success, message)
        """
        try:
            # Build ADIF record for upload
            adif_record = self._build_adif_record(contact_data)

            # Prepare POST data
            post_data = urllib.parse.urlencode({
                'KEY': self.api_key,
                'ACTION': 'INSERT',
                'ADIF': adif_record
            }).encode('utf-8')

            # Make request with proper User-Agent (required by QRZ API)
            request = urllib.request.Request(self.base_url, data=post_data)
            request.add_header('User-Agent', 'W4GNS-General-Logger/1.0')

            with urllib.request.urlopen(request, timeout=15) as response:
                result = response.read().decode('utf-8')

            # Parse response
            if 'RESULT=OK' in result:
                return True, "Contact uploaded to QRZ Logbook"
            elif 'RESULT=FAIL' in result:
                # Extract reason
                if 'REASON=' in result:
                    reason = result.split('REASON=')[1].split('&')[0]
                    reason = urllib.parse.unquote(reason)
                    return False, f"QRZ upload failed: {reason}"
                return False, "QRZ upload failed"
            elif 'RESULT=AUTH' in result:
                return False, "QRZ authentication failed: Invalid API key or insufficient privileges"
            else:
                return False, f"Unexpected response: {result}"

        except urllib.error.URLError as e:
            return False, f"Network error: {str(e)}"
        except Exception as e:
            return False, f"Error: {str(e)}"

    def _build_adif_record(self, contact_data):
        """Build ADIF record string for QRZ upload"""
        fields = []

        # Map our fields to ADIF fields
        field_map = {
            'callsign': 'CALL',
            'date': 'QSO_DATE',
            'time_on': 'TIME_ON',
            'time_off': 'TIME_OFF',
            'frequency': 'FREQ',
            'band': 'BAND',
            'mode': 'MODE',
            'rst_sent': 'RST_SENT',
            'rst_rcvd': 'RST_RCVD',
            'power': 'TX_PWR',
            'name': 'NAME',
            'qth': 'QTH',
            'gridsquare': 'GRIDSQUARE',
            'county': 'CNTY',
            'state': 'STATE',
            'country': 'COUNTRY',
            'cq_zone': 'CQZ',
            'itu_zone': 'ITUZ',
            'iota': 'IOTA',
            'sota': 'SOTA_REF',
            'pota': 'POTA_REF',
            'comment': 'COMMENT',
            'notes': 'NOTES'
        }

        for our_field, adif_field in field_map.items():
            value = contact_data.get(our_field, '')
            if not value:
                continue

            value = str(value).strip()
            if not value:
                continue

            # Format date from YYYY-MM-DD to YYYYMMDD
            if adif_field == 'QSO_DATE':
                value = value.replace('-', '')

            # Format time from HH:MM to HHMMSS
            elif adif_field in ('TIME_ON', 'TIME_OFF'):
                value = value.replace(':', '') + '00'

            # Ensure callsign is uppercase
            elif adif_field == 'CALL':
                value = value.upper()

            fields.append(f"<{adif_field}:{len(value)}>{value}")

        return ' '.join(fields) + ' <EOR>'


def test_qrz_login(username, password, use_post=False):
    """
    Test QRZ login credentials

    Args:
        username: QRZ username
        password: QRZ password
        use_post: If True, use POST instead of GET

    Returns:
        (bool, str): (success, message)
    """
    session = QRZSession(username, password, use_post=use_post)
    return session.login()


def lookup_qrz_callsign(username, password, callsign):
    """
    Look up callsign on QRZ

    Returns:
        dict with callsign data or None
    """
    session = QRZSession(username, password)
    success, msg = session.login()
    if not success:
        return None
    return session.lookup_callsign(callsign)


def upload_to_qrz_logbook(api_key, contact_data):
    """
    Upload contact to QRZ Logbook

    Returns:
        (bool, str): (success, message)
    """
    logbook = QRZLogbook(api_key)
    return logbook.upload_contact(contact_data)
