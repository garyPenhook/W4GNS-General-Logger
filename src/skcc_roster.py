"""
SKCC Membership Roster Downloader and Parser

Downloads and parses the SKCC membership roster from:
https://www.skccgroup.com/membership_data/membership_roster.php

Provides lookup functions for SKCC member information needed for awards tracking.
"""

import re
import requests
import csv
import os
from datetime import datetime
from typing import Optional, Dict, List
import threading


class SKCCRosterManager:
    """Manager for SKCC membership roster data"""

    ROSTER_URL = "https://www.skccgroup.com/membership_data/membership_roster.php"
    ROSTER_FILE = "data/skcc_roster.csv"

    def __init__(self):
        self.roster_data = {}  # Maps callsign -> member info
        self.roster_by_number = {}  # Maps base SKCC number -> member info
        self.member_count = 0
        self.load_local_roster()

    @staticmethod
    def normalize_callsign(callsign: str) -> str:
        """
        Normalize callsign by removing portable prefixes/suffixes.

        Uses the longest segment around '/' as the base callsign.
        """
        if not callsign:
            return ""
        callsign = callsign.strip().upper()
        if '/' in callsign:
            parts = [part for part in callsign.split('/') if part]
            if parts:
                return max(parts, key=len)
        return callsign

    @staticmethod
    def normalize_skcc_number(skcc_number: str) -> str:
        """Normalize SKCC number to digits-only base."""
        if not skcc_number:
            return ""
        return re.sub(r'[^0-9]', '', str(skcc_number).strip().upper())

    def _split_other_calls(self, other_calls: str) -> List[str]:
        """Split other calls field into individual callsigns."""
        if not other_calls:
            return []
        parts = re.split(r'[,\s]+', other_calls.strip())
        return [part for part in (p.strip().upper() for p in parts) if part]

    def _add_roster_entry(self, callsign: str, member: Dict) -> None:
        """Add callsign and its normalized form to the roster index."""
        if not callsign:
            return
        callsign = callsign.strip().upper()
        if callsign:
            self.roster_data.setdefault(callsign, member)
        normalized = self.normalize_callsign(callsign)
        if normalized:
            self.roster_data.setdefault(normalized, member)

    def _add_number_entry(self, skcc_number: str, member: Dict) -> None:
        """Add SKCC number and its base form to the roster index."""
        base_number = self.normalize_skcc_number(skcc_number)
        if base_number:
            self.roster_by_number.setdefault(base_number, member)

    def download_roster(self, progress_callback=None) -> bool:
        """
        Download SKCC membership roster from website.

        Args:
            progress_callback: Optional callback function(status_msg: str) for progress updates

        Returns:
            True if successful, False otherwise
        """
        try:
            if progress_callback:
                progress_callback("Downloading SKCC roster...")

            # Download the HTML page
            response = requests.get(self.ROSTER_URL, timeout=60)
            response.raise_for_status()
            html_content = response.text

            if progress_callback:
                progress_callback("Parsing roster data...")

            # Parse the HTML table
            members = self._parse_html_roster(html_content)

            if not members:
                if progress_callback:
                    progress_callback("Error: No members found in roster")
                return False

            if progress_callback:
                progress_callback(f"Saving {len(members)} members to local file...")

            # Save to CSV file
            self._save_roster_to_csv(members)

            # Load into memory
            self.roster_data = {}
            self.roster_by_number = {}
            self.member_count = len(members)
            for member in members:
                self._add_roster_entry(member.get('call', ''), member)
                self._add_number_entry(member.get('skcc_number', ''), member)
                for other_call in self._split_other_calls(member.get('other_calls', '')):
                    self._add_roster_entry(other_call, member)

            if progress_callback:
                progress_callback(f"✅ Successfully downloaded {len(members)} SKCC members")

            return True

        except requests.RequestException as e:
            if progress_callback:
                progress_callback(f"❌ Download error: {str(e)}")
            return False
        except Exception as e:
            if progress_callback:
                progress_callback(f"❌ Error: {str(e)}")
            return False

    def download_roster_async(self, progress_callback=None, completion_callback=None):
        """
        Download roster in a background thread.

        Args:
            progress_callback: Optional callback(status_msg) for progress updates
            completion_callback: Optional callback(success: bool) when complete
        """
        def _download_thread():
            success = self.download_roster(progress_callback)
            if completion_callback:
                completion_callback(success)

        thread = threading.Thread(target=_download_thread, daemon=True)
        thread.start()

    def _parse_html_roster(self, html_content: str) -> List[Dict]:
        """Parse HTML roster table into list of member dictionaries"""
        members = []

        # Extract table rows using regex (works without BeautifulSoup)
        # Pattern matches: <tr>...</tr> containing member data including join date
        # Format: SKCC#, Call, Name, City, SPC, DXCC, Member Date, Other Calls
        tr_pattern = re.compile(
            r'<tr>\s*'
            r'<td class="right">(\d+[CTS]?)</td>\s*'  # SKCC number
            r'<td class="left">([^<]+)</td>\s*'  # Call
            r'<td class="left">([^<]*)</td>\s*'  # Name
            r'<td class="left">([^<]*)</td>\s*'  # City
            r'<td class="left">([^<]*)</td>\s*'  # SPC
            r'<td class="right">(\d+)</td>\s*'  # DXCC
            r'<td class="right[^"]*">([^<]+)</td>\s*'  # Member Date (e.g., "2-Jan-2006")
            r'<td class="left">([^<]*)</td>',  # Other Calls
            re.DOTALL
        )

        matches = tr_pattern.findall(html_content)

        for match in matches:
            skcc_num, call, name, city, spc, dxcc, member_date, other_calls = match

            # Clean up the data
            call = call.strip().upper()
            name = name.strip()
            city = city.strip()
            spc = spc.strip()
            member_date = member_date.strip()
            other_calls = other_calls.strip().upper()

            # Skip silent keys (SK in callsign)
            if '/SK' in call.upper():
                continue

            # Parse member date to YYYYMMDD format for easy comparison
            # Input format: "2-Jan-2006" or "15-Dec-2023"
            join_date_yyyymmdd = self._parse_member_date(member_date)

            members.append({
                'skcc_number': skcc_num.strip(),
                'call': call,
                'name': name,
                'city': city,
                'spc': spc,
                'dxcc': dxcc.strip(),
                'join_date': join_date_yyyymmdd,  # YYYYMMDD format
                'other_calls': other_calls
            })

        return members

    def _parse_member_date(self, date_str: str) -> str:
        """
        Parse SKCC member date to YYYYMMDD format.

        Args:
            date_str: Date string like "2-Jan-2006" or "15-Dec-2023"

        Returns:
            Date in YYYYMMDD format, or empty string if parse fails
        """
        try:
            from datetime import datetime
            # Parse formats like "2-Jan-2006"
            dt = datetime.strptime(date_str, "%d-%b-%Y")
            return dt.strftime("%Y%m%d")
        except ValueError:
            try:
                # Try alternate format
                dt = datetime.strptime(date_str, "%d-%B-%Y")
                return dt.strftime("%Y%m%d")
            except ValueError:
                # Return empty if can't parse
                return ""

    def _save_roster_to_csv(self, members: List[Dict]):
        """Save roster to CSV file"""
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.ROSTER_FILE), exist_ok=True)

        # Write CSV file
        with open(self.ROSTER_FILE, 'w', newline='', encoding='utf-8') as f:
            if members:
                fieldnames = [
                    'skcc_number',
                    'call',
                    'name',
                    'city',
                    'spc',
                    'dxcc',
                    'join_date',
                    'other_calls'
                ]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(members)

        # Write metadata file with download timestamp
        meta_file = self.ROSTER_FILE + '.meta'
        with open(meta_file, 'w') as f:
            f.write(f"downloaded: {datetime.now().isoformat()}\n")
            f.write(f"count: {len(members)}\n")

    def load_local_roster(self) -> bool:
        """Load roster from local CSV file"""
        if not os.path.exists(self.ROSTER_FILE):
            return False

        try:
            self.roster_data = {}
            self.roster_by_number = {}
            unique_numbers = set()
            with open(self.ROSTER_FILE, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    skcc_number = row.get('skcc_number', '').strip()
                    if skcc_number:
                        unique_numbers.add(skcc_number)
                    self._add_roster_entry(row.get('call', ''), row)
                    self._add_number_entry(skcc_number, row)
                    for other_call in self._split_other_calls(row.get('other_calls', '')):
                        self._add_roster_entry(other_call, row)
            self.member_count = len(unique_numbers)
            return True
        except Exception as e:
            print(f"Error loading roster: {e}")
            return False

    def lookup_callsign(self, callsign: str) -> Optional[Dict]:
        """
        Look up a callsign in the roster.

        Handles callsigns with portable indicators (/EX, /P, etc.)
        by checking both exact match and base callsign.

        Args:
            callsign: Callsign to look up

        Returns:
            Member info dict or None if not found
        """
        callsign_upper = callsign.upper().strip()

        # First try exact match
        if callsign_upper in self.roster_data:
            return self.roster_data[callsign_upper]

        # Extract base callsign if it has a slash
        base_call = self.normalize_callsign(callsign_upper)

        if base_call in self.roster_data:
            return self.roster_data[base_call]

        # Try base callsign with common portable suffixes
        # e.g., "W8CBC" matches "W8CBC/EX" in roster
        for suffix in ['/EX', '/P', '/QRP', '/MM']:
            roster_entry = self.roster_data.get(base_call + suffix)
            if roster_entry:
                return roster_entry

        # No match found
        return None

    def is_skcc_member(self, callsign: str) -> bool:
        """
        Check if a callsign is an SKCC member.

        Args:
            callsign: Callsign to check

        Returns:
            True if callsign is in SKCC roster
        """
        return self.lookup_callsign(callsign) is not None

    def get_skcc_number(self, callsign: str) -> Optional[str]:
        """
        Get SKCC number for a callsign.

        Args:
            callsign: Callsign to look up

        Returns:
            SKCC number (with suffixes like "12345C") or None
        """
        member = self.lookup_callsign(callsign)
        return member['skcc_number'] if member else None

    def get_join_date(self, callsign: str) -> Optional[str]:
        """
        Get SKCC join date for a callsign.

        Args:
            callsign: Callsign to look up

        Returns:
            Join date in YYYYMMDD format or None if not found
        """
        member = self.lookup_callsign(callsign)
        return member.get('join_date') if member else None

    def get_member_by_number(self, skcc_number: str) -> Optional[Dict]:
        """Look up a member by SKCC number (base digits)."""
        base_number = self.normalize_skcc_number(skcc_number)
        if not base_number:
            return None
        return self.roster_by_number.get(base_number)

    def get_join_date_by_number(self, skcc_number: str) -> Optional[str]:
        """Get SKCC join date by SKCC number."""
        member = self.get_member_by_number(skcc_number)
        return member.get('join_date') if member else None

    def was_member_on_date(self, callsign: str, qso_date: str) -> bool:
        """
        Check if a callsign was an SKCC member on a specific date.

        Args:
            callsign: Callsign to check
            qso_date: QSO date in YYYYMMDD format

        Returns:
            True if callsign was a member on that date (join_date <= qso_date)
        """
        join_date = self.get_join_date(callsign)
        if not join_date or not qso_date:
            return False

        # Normalize dates to YYYYMMDD format (remove hyphens)
        qso_date_norm = qso_date.replace('-', '')
        join_date_norm = join_date.replace('-', '')

        return join_date_norm <= qso_date_norm

    def was_member_number_on_date(self, skcc_number: str, qso_date: str) -> bool:
        """
        Check if an SKCC number was an active member on a specific date.

        Args:
            skcc_number: SKCC number (may include suffix)
            qso_date: QSO date in YYYYMMDD format

        Returns:
            True if join_date <= qso_date
        """
        join_date = self.get_join_date_by_number(skcc_number)
        if not join_date or not qso_date:
            return False

        qso_date_norm = qso_date.replace('-', '')
        join_date_norm = join_date.replace('-', '')

        return join_date_norm <= qso_date_norm

    def get_member_count(self) -> int:
        """Get total number of members in roster"""
        if self.member_count:
            return self.member_count
        unique_numbers = {member.get('skcc_number') for member in self.roster_data.values()}
        return len({num for num in unique_numbers if num})

    def get_roster_age(self) -> Optional[str]:
        """Get age of local roster file"""
        meta_file = self.ROSTER_FILE + '.meta'
        if not os.path.exists(meta_file):
            return None

        try:
            with open(meta_file, 'r') as f:
                for line in f:
                    if line.startswith('downloaded:'):
                        timestamp_str = line.split(':', 1)[1].strip()
                        timestamp = datetime.fromisoformat(timestamp_str)
                        age = datetime.now() - timestamp

                        if age.days > 0:
                            return f"{age.days} days ago"
                        elif age.seconds >= 3600:
                            hours = age.seconds // 3600
                            return f"{hours} hours ago"
                        else:
                            minutes = age.seconds // 60
                            return f"{minutes} minutes ago"
        except (ValueError, TypeError, KeyError, OSError):
            pass

        return "Unknown"

    def has_local_roster(self) -> bool:
        """Check if local roster file exists"""
        return os.path.exists(self.ROSTER_FILE) and len(self.roster_data) > 0


# Global instance
_roster_manager = None

def get_roster_manager() -> SKCCRosterManager:
    """Get global SKCCRosterManager instance"""
    global _roster_manager
    if _roster_manager is None:
        _roster_manager = SKCCRosterManager()
    return _roster_manager
