"""
SKCC Award Roster Management

Downloads and manages Centurion, Tribune, and Senator award rosters to validate
that contacted stations had achieved the award level at time of QSO.

CRITICAL: For Tribune and Senator awards, you must verify the OTHER station had
already achieved Tribune or Senator status at the time of contact.
"""

import requests
import re
import os
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class SKCCAwardRosterManager:
    """
    Manages SKCC award rosters (Centurion, Tribune, Senator)

    These rosters contain the date each member achieved each award level,
    which is critical for validating Tribune and Senator contacts.
    """

    ROSTER_URLS = {
        'centurion': 'https://www.skccgroup.com/operating_awards/centurion/centurion_roster.php',
        'tribune': 'https://www.skccgroup.com/operating_awards/tribune/tribune_roster.php',
        'senator': 'https://www.skccgroup.com/operating_awards/senator/senator_roster.php'
    }

    def __init__(self, cache_dir=None, database=None):
        """
        Initialize award roster manager

        Args:
            cache_dir: Directory to cache roster files (default: ~/.skcc_rosters)
            database: Database instance for storing roster data (optional)
        """
        if cache_dir is None:
            cache_dir = os.path.expanduser('~/.skcc_rosters')

        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        self.database = database

        # In-memory roster data: {award_type: {skcc_number: award_date, ...}}
        self.rosters = {
            'centurion': {},
            'tribune': {},
            'senator': {}
        }

        # Track if rosters are loaded
        self.loaded = {
            'centurion': False,
            'tribune': False,
            'senator': False
        }

    def _get_roster_file_path(self, award_type: str) -> str:
        """Get file path for cached roster"""
        return os.path.join(self.cache_dir, f'{award_type}_roster.txt')

    def _get_roster_age(self, award_type: str) -> Optional[int]:
        """
        Get age of cached roster file in days

        Returns:
            Age in days, or None if file doesn't exist
        """
        file_path = self._get_roster_file_path(award_type)
        if not os.path.exists(file_path):
            return None

        file_time = os.path.getmtime(file_path)
        age_seconds = time.time() - file_time
        return int(age_seconds / 86400)  # Convert to days

    def download_roster(self, award_type: str, force: bool = False) -> bool:
        """
        Download award roster from SKCC website

        Args:
            award_type: 'centurion', 'tribune', or 'senator'
            force: Force download even if cached file is recent

        Returns:
            True if successful, False otherwise
        """
        if award_type not in self.ROSTER_URLS:
            logger.error(f"Invalid award type: {award_type}")
            return False

        # Check if we need to download
        if not force:
            age = self._get_roster_age(award_type)
            if age is not None and age < 7:  # Cache for 7 days
                logger.info(f"{award_type} roster is {age} days old, using cache")
                return self.load_roster(award_type)

        url = self.ROSTER_URLS[award_type]
        file_path = self._get_roster_file_path(award_type)

        try:
            logger.info(f"Downloading {award_type} roster from {url}")
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            # Save to cache
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(response.text)

            logger.info(f"Downloaded {award_type} roster to {file_path}")

            # Parse and load
            return self._parse_roster(award_type, response.text)

        except requests.RequestException as e:
            logger.error(f"Failed to download {award_type} roster: {e}")
            # Try to load from cache if available
            return self.load_roster(award_type)
        except Exception as e:
            logger.error(f"Error downloading {award_type} roster: {e}")
            return False

    def load_roster(self, award_type: str) -> bool:
        """
        Load award roster from cached file

        Args:
            award_type: 'centurion', 'tribune', or 'senator'

        Returns:
            True if successful, False otherwise
        """
        file_path = self._get_roster_file_path(award_type)

        if not os.path.exists(file_path):
            logger.warning(f"No cached {award_type} roster found at {file_path}")
            return False

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            return self._parse_roster(award_type, content)

        except Exception as e:
            logger.error(f"Error loading {award_type} roster: {e}")
            return False

    def _parse_roster(self, award_type: str, html_content: str) -> bool:
        """
        Parse HTML roster and extract member numbers and award dates

        Format example:
        <td>1</td><td>W4DF/SK</td><td>436</td><td>Fred</td><td>Lynchburg</td>
        <td>VA</td><td>28 Jan 2006</td><td>80M</td>

        Args:
            award_type: 'centurion', 'tribune', or 'senator'
            html_content: HTML content from roster page

        Returns:
            True if parsing successful
        """
        roster_data = {}
        roster_records = []  # For database storage

        try:
            # Extract table rows
            # Pattern matches table rows with member data
            # Typical row: <tr><td>num</td><td>call</td><td>skcc</td>...<td>date</td>...

            # For Tribune, pattern must match both with and without endorsements
            if award_type == 'tribune':
                # Tribune format: Award# [x#] | Callsign | SKCC | Name | City | SPC | Awarded | ...
                # Examples: "1 x15" (with endorsement) or "5" (without endorsement)
                pattern = r'<td[^>]*>\d+(?:\s+x\d+)?</td>\s*<td[^>]*>([^<]+)</td>\s*<td[^>]*>(\d+)</td>.*?<td[^>]*>(\d{2}\s+\w+\s+\d{4})</td>'
            else:
                # Centurion/Senator format: Award# | Callsign | SKCC | Name | City | SPC | Awarded | ...
                pattern = r'<td[^>]*>(\d+)</td>\s*<td[^>]*>([^<]+)</td>\s*<td[^>]*>(\d+)</td>.*?<td[^>]*>(\d{2}\s+\w+\s+\d{4})</td>'

            matches = re.findall(pattern, html_content, re.DOTALL | re.IGNORECASE)

            for match in matches:
                if award_type == 'tribune':
                    callsign_raw, skcc_number, date_str = match
                else:
                    award_num, callsign_raw, skcc_number, date_str = match

                # Clean up data
                callsign = callsign_raw.strip().upper()
                skcc_number = skcc_number.strip()
                date_str = date_str.strip()

                # Parse date (format: "28 Jan 2006")
                try:
                    award_date = datetime.strptime(date_str, '%d %b %Y')
                    date_formatted = award_date.strftime('%Y%m%d')  # YYYYMMDD format

                    # Store by SKCC number
                    if skcc_number.isdigit():
                        roster_data[skcc_number] = date_formatted
                        roster_records.append({
                            'skcc_number': skcc_number,
                            'callsign': callsign,
                            'award_date': date_formatted
                        })

                except ValueError as e:
                    logger.debug(f"Could not parse date '{date_str}': {e}")
                    continue

            # Store in memory
            self.rosters[award_type] = roster_data
            self.loaded[award_type] = True

            # Store in database if available
            if self.database and roster_records:
                self._save_to_database(award_type, roster_records)

            logger.info(f"Parsed {len(roster_data)} {award_type} awards")
            return True

        except Exception as e:
            logger.error(f"Error parsing {award_type} roster: {e}")
            return False

    def _save_to_database(self, award_type: str, records: list) -> bool:
        """
        Save roster data to database

        Creates a new database connection for thread safety since roster downloads
        happen in background threads.

        Args:
            award_type: 'centurion', 'tribune', or 'senator'
            records: List of dicts with 'skcc_number', 'callsign', 'award_date'

        Returns:
            True if successful
        """
        if not self.database:
            return False

        try:
            import sqlite3

            # Create a new connection for thread safety
            # SQLite connections cannot be shared across threads
            conn = sqlite3.connect(self.database.db_path)
            cursor = conn.cursor()

            # Map award type to table and date column
            table_map = {
                'centurion': ('skcc_centurion_members', 'centurion_date'),
                'tribune': ('skcc_tribune_members', 'tribune_date'),
                'senator': ('skcc_senator_members', 'senator_date')
            }

            table_name, date_column = table_map[award_type]

            # Clear existing data
            cursor.execute(f'DELETE FROM {table_name}')

            # Insert new data
            for record in records:
                cursor.execute(f'''
                    INSERT INTO {table_name} (skcc_number, callsign, {date_column})
                    VALUES (?, ?, ?)
                ''', (record['skcc_number'], record['callsign'], record['award_date']))

            conn.commit()
            conn.close()

            logger.info(f"Saved {len(records)} {award_type} records to database")
            return True

        except Exception as e:
            logger.error(f"Error saving {award_type} roster to database: {e}")
            try:
                conn.rollback()
                conn.close()
            except:
                pass
            return False

    def get_award_date(self, award_type: str, skcc_number: str) -> Optional[str]:
        """
        Get the date a member achieved a specific award

        Args:
            award_type: 'centurion', 'tribune', or 'senator'
            skcc_number: SKCC member number (can include suffix like 'C', 'T', 'S')

        Returns:
            Award date in YYYYMMDD format, or None if not found
        """
        # Ensure roster is loaded
        if not self.loaded.get(award_type):
            self.download_roster(award_type)

        # Strip suffix from SKCC number (e.g., "1234T" -> "1234")
        base_number = re.sub(r'[CTSX]$', '', skcc_number.strip().upper())

        return self.rosters[award_type].get(base_number)

    def was_award_holder_on_date(self, award_type: str, skcc_number: str, qso_date: str) -> bool:
        """
        Check if a member had achieved an award by a specific QSO date

        CRITICAL: For Tribune and Senator validation, the other station must
        have achieved the award BEFORE the QSO date.

        Args:
            award_type: 'centurion', 'tribune', or 'senator'
            skcc_number: SKCC member number
            qso_date: QSO date in YYYYMMDD format

        Returns:
            True if member had achieved award before QSO date
        """
        award_date = self.get_award_date(award_type, skcc_number)

        if not award_date:
            return False

        # Normalize QSO date
        qso_normalized = qso_date.replace('-', '')

        # Member must have achieved award on or before QSO date
        return award_date <= qso_normalized

    def was_tribune_or_senator_on_date(self, skcc_number: str, qso_date: str) -> bool:
        """
        Check if a member was Tribune OR Senator at time of QSO

        This is the critical validation for Tribune and Senator awards.

        Args:
            skcc_number: SKCC member number
            qso_date: QSO date in YYYYMMDD format

        Returns:
            True if member was Tribune or Senator at time of QSO
        """
        # Check if they were Tribune by the QSO date
        if self.was_award_holder_on_date('tribune', skcc_number, qso_date):
            return True

        # Check if they were Senator by the QSO date
        if self.was_award_holder_on_date('senator', skcc_number, qso_date):
            return True

        return False

    def was_centurion_or_higher_on_date(self, skcc_number: str, qso_date: str) -> bool:
        """
        Check if a member was Centurion OR Tribune OR Senator at time of QSO

        This is the critical validation for Tribune award contacts - the contacted
        station must have been at least a Centurion at the time of QSO.

        Args:
            skcc_number: SKCC member number
            qso_date: QSO date in YYYYMMDD format

        Returns:
            True if member was Centurion, Tribune, or Senator at time of QSO
        """
        # Check if they were Centurion by the QSO date
        if self.was_award_holder_on_date('centurion', skcc_number, qso_date):
            return True

        # Check if they were Tribune by the QSO date
        if self.was_award_holder_on_date('tribune', skcc_number, qso_date):
            return True

        # Check if they were Senator by the QSO date
        if self.was_award_holder_on_date('senator', skcc_number, qso_date):
            return True

        return False

    def download_all_rosters(self, force: bool = False) -> Dict[str, bool]:
        """
        Download all three award rosters

        Args:
            force: Force download even if cached files are recent

        Returns:
            Dictionary with success status for each roster
        """
        results = {}

        for award_type in ['centurion', 'tribune', 'senator']:
            results[award_type] = self.download_roster(award_type, force)

        return results

    def get_roster_info(self) -> Dict[str, Dict]:
        """
        Get information about loaded rosters

        Returns:
            Dictionary with roster statistics
        """
        info = {}

        for award_type in ['centurion', 'tribune', 'senator']:
            age = self._get_roster_age(award_type)
            count = len(self.rosters.get(award_type, {}))

            info[award_type] = {
                'loaded': self.loaded.get(award_type, False),
                'count': count,
                'age_days': age,
                'status': 'current' if (age and age < 7) else ('old' if age else 'missing')
            }

        return info


# Singleton instance
_award_roster_manager = None

def get_award_roster_manager(database=None) -> SKCCAwardRosterManager:
    """Get singleton instance of award roster manager"""
    global _award_roster_manager
    if _award_roster_manager is None:
        _award_roster_manager = SKCCAwardRosterManager(database=database)
    return _award_roster_manager
