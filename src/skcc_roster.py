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
        # Pattern matches: <tr>...</tr> containing member data
        tr_pattern = re.compile(r'<tr>\s*<td class="right">(\d+[CTS]?)</td>\s*<td class="left">([^<]+)</td>\s*<td class="left">([^<]*)</td>\s*<td class="left">([^<]*)</td>\s*<td class="left">([^<]*)</td>\s*<td class="right">(\d+)</td>', re.DOTALL)

        matches = tr_pattern.findall(html_content)

        for match in matches:
            skcc_num, call, name, city, spc, dxcc = match

            # Clean up the data
            call = call.strip()
            name = name.strip()
            city = city.strip()
            spc = spc.strip()

            # Skip silent keys (SK in callsign)
            if '/SK' in call.upper():
                continue

            members.append({
                'skcc_number': skcc_num.strip(),
                'call': call,
                'name': name,
                'city': city,
                'spc': spc,
                'dxcc': dxcc.strip()
            })

        return members

    def _save_roster_to_csv(self, members: List[Dict]):
        """Save roster to CSV file"""
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.ROSTER_FILE), exist_ok=True)

        # Write CSV file
        with open(self.ROSTER_FILE, 'w', newline='', encoding='utf-8') as f:
            if members:
                fieldnames = ['skcc_number', 'call', 'name', 'city', 'spc', 'dxcc']
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

        Args:
            callsign: Callsign to look up

        Returns:
            Member info dict or None if not found
        """
        return self.roster_data.get(callsign.upper())

    def is_skcc_member(self, callsign: str) -> bool:
        """
        Check if a callsign is an SKCC member.

        Args:
            callsign: Callsign to check

        Returns:
            True if callsign is in SKCC roster
        """
        return callsign.upper() in self.roster_data

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
