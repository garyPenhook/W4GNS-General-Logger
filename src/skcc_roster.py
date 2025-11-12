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
        self.load_local_roster()

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
            self.roster_data = {m['call']: m for m in members}

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
            r'<td class="right[^"]*">([^<]+)</td>',  # Member Date (e.g., "2-Jan-2006")
            re.DOTALL
        )

        matches = tr_pattern.findall(html_content)

        for match in matches:
            skcc_num, call, name, city, spc, dxcc, member_date = match

            # Clean up the data
            call = call.strip()
            name = name.strip()
            city = city.strip()
            spc = spc.strip()
            member_date = member_date.strip()

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
                'join_date': join_date_yyyymmdd  # YYYYMMDD format
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
        except:
            try:
                # Try alternate format
                dt = datetime.strptime(date_str, "%d-%B-%Y")
                return dt.strftime("%Y%m%d")
            except:
                # Return empty if can't parse
                return ""

    def _save_roster_to_csv(self, members: List[Dict]):
        """Save roster to CSV file"""
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.ROSTER_FILE), exist_ok=True)

        # Write CSV file
        with open(self.ROSTER_FILE, 'w', newline='', encoding='utf-8') as f:
            if members:
                fieldnames = ['skcc_number', 'call', 'name', 'city', 'spc', 'dxcc', 'join_date']
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
            with open(self.ROSTER_FILE, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.roster_data[row['call']] = row
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
        callsign_upper = callsign.upper()

        # First try exact match
        if callsign_upper in self.roster_data:
            return self.roster_data[callsign_upper]

        # Extract base callsign if it has a slash
        if '/' in callsign_upper:
            base_call = callsign_upper.split('/')[0]
        else:
            base_call = callsign_upper

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

    def get_member_count(self) -> int:
        """Get total number of members in roster"""
        return len(self.roster_data)

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
        except:
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
