"""
Needed Contacts Analyzer for Smart Log Processing

This module analyzes DX spots against the user's log and award progress to determine
which contacts are needed for award advancement. Similar to SKCC Skimmer functionality.
"""

from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class NeededReason:
    """Represents why a contact is needed"""
    award_name: str
    reason: str
    priority: int  # 1=high, 2=medium, 3=low
    current: int
    required: int

    def __str__(self):
        return f"{self.award_name}: {self.reason}"


@dataclass
class SpotAnalysis:
    """Analysis result for a DX spot"""
    callsign: str
    is_needed: bool
    reasons: List[NeededReason]
    highest_priority: int  # Lowest number = highest priority

    @property
    def priority_label(self) -> str:
        """Human-readable priority"""
        if not self.is_needed:
            return "Not Needed"
        if self.highest_priority == 1:
            return "HIGH"
        elif self.highest_priority == 2:
            return "MEDIUM"
        else:
            return "LOW"

    def get_reason_summary(self) -> str:
        """Get a summary of all reasons"""
        if not self.reasons:
            return "Already worked or not applicable"
        return "; ".join(str(r) for r in self.reasons[:3])  # Show top 3


class NeededContactsAnalyzer:
    """
    Analyzes spots to determine if they're needed for award progress.

    This class integrates with existing award calculators and provides
    real-time analysis of DX spots.
    """

    def __init__(self, db_connection):
        """
        Initialize the analyzer.

        Args:
            db_connection: Database connection for querying log
        """
        self.db = db_connection
        self.cache_timeout = 300  # 5 minutes
        self._cache: Dict[str, Tuple[SpotAnalysis, datetime]] = {}

    def analyze_spot(self,
                     callsign: str,
                     band: str,
                     mode: str,
                     frequency: Optional[str] = None,
                     skcc_number: Optional[str] = None,
                     state: Optional[str] = None,
                     country: Optional[str] = None,
                     continent: Optional[str] = None,
                     gridsquare: Optional[str] = None) -> SpotAnalysis:
        """
        Analyze if a spot is needed for any awards.

        Args:
            callsign: Station's callsign
            band: Band (e.g., "20M", "40M")
            mode: Mode (e.g., "CW", "SSB")
            frequency: Frequency in kHz
            skcc_number: SKCC member number if known
            state: US state if known
            country: Country if known
            continent: Continent if known
            gridsquare: Grid square if known

        Returns:
            SpotAnalysis with needed status and reasons
        """
        # Check cache first
        cache_key = f"{callsign}_{band}_{mode}"
        if cache_key in self._cache:
            cached_analysis, timestamp = self._cache[cache_key]
            if (datetime.now() - timestamp).total_seconds() < self.cache_timeout:
                return cached_analysis

        reasons: List[NeededReason] = []

        # Check if already worked on this band/mode
        if self._already_worked(callsign, band, mode):
            analysis = SpotAnalysis(
                callsign=callsign,
                is_needed=False,
                reasons=[],
                highest_priority=99
            )
            self._cache[cache_key] = (analysis, datetime.now())
            return analysis

        # Analyze for each award type
        reasons.extend(self._check_skcc_awards(callsign, band, mode, skcc_number))
        reasons.extend(self._check_was_awards(callsign, band, mode, state))
        reasons.extend(self._check_dxcc_awards(callsign, band, mode, country))
        reasons.extend(self._check_wac_awards(callsign, band, mode, continent))
        reasons.extend(self._check_vucc_awards(callsign, band, mode, gridsquare))
        reasons.extend(self._check_wpx_awards(callsign, band, mode))

        # Determine highest priority
        highest_priority = min((r.priority for r in reasons), default=99)
        is_needed = len(reasons) > 0

        analysis = SpotAnalysis(
            callsign=callsign,
            is_needed=is_needed,
            reasons=sorted(reasons, key=lambda r: r.priority),
            highest_priority=highest_priority
        )

        self._cache[cache_key] = (analysis, datetime.now())
        return analysis

    def _already_worked(self, callsign: str, band: str, mode: str) -> bool:
        """Check if callsign already worked on this band/mode"""
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM contacts
                WHERE LOWER(callsign) = LOWER(?)
                AND LOWER(band) = LOWER(?)
                AND LOWER(mode) = LOWER(?)
            """, (callsign, band, mode))
            count = cursor.fetchone()[0]
            return count > 0
        except Exception as e:
            logger.error(f"Error checking if worked: {e}")
            return False

    def _check_skcc_awards(self, callsign: str, band: str, mode: str,
                           skcc_number: Optional[str]) -> List[NeededReason]:
        """Check if needed for SKCC awards"""
        reasons = []

        # SKCC awards require CW mode
        if mode.upper() not in ['CW', 'A1A']:
            return reasons

        if not skcc_number:
            return reasons

        try:
            # Check Centurion - need unique SKCC members
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT COUNT(DISTINCT skcc_number) FROM contacts
                WHERE skcc_number IS NOT NULL AND skcc_number != ''
                AND mode IN ('CW', 'A1A')
            """)
            current_members = cursor.fetchone()[0]

            # Check if this SKCC number already worked
            cursor.execute("""
                SELECT COUNT(*) FROM contacts
                WHERE skcc_number = ?
                AND mode IN ('CW', 'A1A')
            """, (skcc_number,))
            already_worked = cursor.fetchone()[0] > 0

            if not already_worked:
                # Determine which endorsement level they're working toward
                next_level = self._get_next_centurion_level(current_members)
                if next_level:
                    reasons.append(NeededReason(
                        award_name="SKCC Centurion",
                        reason=f"New member for {next_level} ({current_members}/{self._get_level_count(next_level)})",
                        priority=1,  # High priority
                        current=current_members,
                        required=self._get_level_count(next_level)
                    ))

            # Check if Tribune or Senator (higher priority)
            cursor.execute("""
                SELECT 1 FROM skcc_tribune_members WHERE skcc_number = ?
                LIMIT 1
            """, (skcc_number,))
            is_tribune = cursor.fetchone() is not None

            cursor.execute("""
                SELECT 1 FROM skcc_senator_members WHERE skcc_number = ?
                LIMIT 1
            """, (skcc_number,))
            is_senator = cursor.fetchone() is not None

            if is_senator and not already_worked:
                reasons.append(NeededReason(
                    award_name="SKCC Senator",
                    reason="Senator member (highest level)",
                    priority=1,  # Highest priority
                    current=0,
                    required=1
                ))
            elif is_tribune and not already_worked:
                reasons.append(NeededReason(
                    award_name="SKCC Tribune",
                    reason="Tribune member",
                    priority=1,  # High priority
                    current=0,
                    required=1
                ))

        except Exception as e:
            logger.error(f"Error checking SKCC awards: {e}")

        return reasons

    def _check_was_awards(self, callsign: str, band: str, mode: str,
                          state: Optional[str]) -> List[NeededReason]:
        """Check if needed for WAS (Worked All States) awards"""
        reasons = []

        if not state or len(state) != 2:
            return reasons

        try:
            cursor = self.db.cursor()

            # Check overall WAS
            cursor.execute("""
                SELECT COUNT(DISTINCT state) FROM contacts
                WHERE state IS NOT NULL AND LENGTH(state) = 2
            """)
            worked_states = cursor.fetchone()[0]

            # Check if this state already worked
            cursor.execute("""
                SELECT COUNT(*) FROM contacts
                WHERE UPPER(state) = UPPER(?)
            """, (state,))
            state_worked = cursor.fetchone()[0] > 0

            if not state_worked:
                reasons.append(NeededReason(
                    award_name="WAS",
                    reason=f"New state: {state.upper()} ({worked_states}/50)",
                    priority=1 if worked_states >= 40 else 2,  # High priority when close
                    current=worked_states,
                    required=50
                ))

            # Check SKCC WAS (CW only)
            if mode.upper() in ['CW', 'A1A']:
                cursor.execute("""
                    SELECT COUNT(DISTINCT state) FROM contacts
                    WHERE state IS NOT NULL AND LENGTH(state) = 2
                    AND mode IN ('CW', 'A1A')
                    AND skcc_number IS NOT NULL AND skcc_number != ''
                """)
                skcc_states = cursor.fetchone()[0]

                cursor.execute("""
                    SELECT COUNT(*) FROM contacts
                    WHERE UPPER(state) = UPPER(?)
                    AND mode IN ('CW', 'A1A')
                    AND skcc_number IS NOT NULL AND skcc_number != ''
                """, (state,))
                skcc_state_worked = cursor.fetchone()[0] > 0

                if not skcc_state_worked:
                    reasons.append(NeededReason(
                        award_name="SKCC WAS",
                        reason=f"New SKCC state: {state.upper()} ({skcc_states}/50)",
                        priority=1 if skcc_states >= 40 else 2,
                        current=skcc_states,
                        required=50
                    ))

        except Exception as e:
            logger.error(f"Error checking WAS awards: {e}")

        return reasons

    def _check_dxcc_awards(self, callsign: str, band: str, mode: str,
                           country: Optional[str]) -> List[NeededReason]:
        """Check if needed for DXCC awards"""
        reasons = []

        if not country:
            return reasons

        try:
            cursor = self.db.cursor()

            # Check overall DXCC
            cursor.execute("""
                SELECT COUNT(DISTINCT country) FROM contacts
                WHERE country IS NOT NULL AND country != ''
            """)
            worked_countries = cursor.fetchone()[0]

            # Check if this country already worked
            cursor.execute("""
                SELECT COUNT(*) FROM contacts
                WHERE LOWER(country) = LOWER(?)
            """, (country,))
            country_worked = cursor.fetchone()[0] > 0

            if not country_worked:
                reasons.append(NeededReason(
                    award_name="DXCC",
                    reason=f"New country: {country} ({worked_countries}/100)",
                    priority=1 if worked_countries >= 80 else 2,
                    current=worked_countries,
                    required=100
                ))

        except Exception as e:
            logger.error(f"Error checking DXCC awards: {e}")

        return reasons

    def _check_wac_awards(self, callsign: str, band: str, mode: str,
                          continent: Optional[str]) -> List[NeededReason]:
        """Check if needed for WAC (Worked All Continents) awards"""
        reasons = []

        if not continent:
            return reasons

        try:
            cursor = self.db.cursor()

            # Check overall WAC
            cursor.execute("""
                SELECT COUNT(DISTINCT continent) FROM contacts
                WHERE continent IS NOT NULL AND continent != ''
            """)
            worked_continents = cursor.fetchone()[0]

            # Check if this continent already worked
            cursor.execute("""
                SELECT COUNT(*) FROM contacts
                WHERE LOWER(continent) = LOWER(?)
            """, (continent,))
            continent_worked = cursor.fetchone()[0] > 0

            if not continent_worked:
                reasons.append(NeededReason(
                    award_name="WAC",
                    reason=f"New continent: {continent} ({worked_continents}/6)",
                    priority=1,  # Always high priority - only 6 to work
                    current=worked_continents,
                    required=6
                ))

        except Exception as e:
            logger.error(f"Error checking WAC awards: {e}")

        return reasons

    def _check_vucc_awards(self, callsign: str, band: str, mode: str,
                           gridsquare: Optional[str]) -> List[NeededReason]:
        """Check if needed for VUCC (VHF/UHF Century Club) awards"""
        reasons = []

        if not gridsquare or len(gridsquare) < 4:
            return reasons

        # VUCC is for VHF/UHF bands
        vhf_uhf_bands = ['6M', '2M', '70CM', '23CM', '1.25M']
        if band.upper() not in vhf_uhf_bands:
            return reasons

        try:
            cursor = self.db.cursor()
            grid_4char = gridsquare[:4].upper()

            # Check grids worked on VHF/UHF
            cursor.execute("""
                SELECT COUNT(DISTINCT SUBSTR(UPPER(gridsquare), 1, 4)) FROM contacts
                WHERE gridsquare IS NOT NULL
                AND LENGTH(gridsquare) >= 4
                AND UPPER(band) IN ('6M', '2M', '70CM', '23CM', '1.25M')
            """)
            worked_grids = cursor.fetchone()[0]

            # Check if this grid already worked
            cursor.execute("""
                SELECT COUNT(*) FROM contacts
                WHERE SUBSTR(UPPER(gridsquare), 1, 4) = ?
                AND UPPER(band) IN ('6M', '2M', '70CM', '23CM', '1.25M')
            """, (grid_4char,))
            grid_worked = cursor.fetchone()[0] > 0

            if not grid_worked:
                reasons.append(NeededReason(
                    award_name="VUCC",
                    reason=f"New grid: {grid_4char} ({worked_grids}/100)",
                    priority=2,  # Medium priority
                    current=worked_grids,
                    required=100
                ))

        except Exception as e:
            logger.error(f"Error checking VUCC awards: {e}")

        return reasons

    def _check_wpx_awards(self, callsign: str, band: str, mode: str) -> List[NeededReason]:
        """Check if needed for WPX (Worked All Prefixes) awards"""
        reasons = []

        try:
            # Extract prefix from callsign
            prefix = self._extract_prefix(callsign)
            if not prefix:
                return reasons

            cursor = self.db.cursor()

            # Get all worked callsigns and extract their prefixes
            cursor.execute("SELECT DISTINCT callsign FROM contacts")
            worked_prefixes = set()
            for row in cursor.fetchall():
                db_callsign = row[0]
                if db_callsign:
                    db_prefix = self._extract_prefix(db_callsign)
                    if db_prefix:
                        worked_prefixes.add(db_prefix.upper())

            prefix_worked = prefix.upper() in worked_prefixes

            if not prefix_worked:
                # Count total unique prefixes worked
                total_worked = len(worked_prefixes)

                reasons.append(NeededReason(
                    award_name="WPX",
                    reason=f"New prefix: {prefix}",
                    priority=3,  # Low priority - many prefixes possible
                    current=total_worked,
                    required=300  # Typical WPX goal
                ))

        except Exception as e:
            logger.error(f"Error checking WPX awards: {e}")

        return reasons

    def _extract_prefix(self, callsign: str) -> Optional[str]:
        """
        Extract WPX prefix from callsign according to WPX rules.

        WPX prefix rules for compound callsigns:
        - W1AW/2: Operating from call area 2, prefix is "W2"
        - KH6/W4GNS: Operating from Hawaii, prefix is "KH6"
        - W4GNS/KH6: Operating from Hawaii, prefix is "KH6"
        - VP9/K1ABC: Operating from Bermuda, prefix is "VP9"
        - W4GNS/P: Portable, prefix is "W4" (ignore /P, /M, /MM, /QRP)

        The key is to identify which part indicates the operating location.
        """
        if not callsign:
            return None

        # Split on '/' to handle portable callsigns
        parts = callsign.split('/')

        if len(parts) == 1:
            # No slash, simple callsign
            base = parts[0]
        elif len(parts) == 2:
            prefix_part = parts[0]
            suffix_part = parts[1]

            # Check for common non-location suffixes
            non_location_suffixes = {'P', 'M', 'MM', 'QRP', 'A', 'B', 'AM'}
            if suffix_part.upper() in non_location_suffixes:
                base = prefix_part
            # If suffix is a single digit, it indicates call area change
            elif len(suffix_part) == 1 and suffix_part.isdigit():
                # For W1AW/2, the prefix becomes based on the digit
                # Extract letters from prefix_part and combine with new digit
                letters = ''.join(c for c in prefix_part if c.isalpha())
                if letters:
                    # Use the country prefix letters + new digit
                    for i, c in enumerate(prefix_part):
                        if c.isdigit():
                            return prefix_part[:i] + suffix_part
                return suffix_part
            # If suffix is short (2-4 chars) and has a digit, it's likely a DXCC prefix
            elif len(suffix_part) <= 4 and any(c.isdigit() for c in suffix_part):
                base = suffix_part
            # If prefix is short (2-4 chars) and has a digit, it's likely a DXCC prefix
            elif len(prefix_part) <= 4 and any(c.isdigit() for c in prefix_part):
                base = prefix_part
            # If suffix looks like a full callsign (has letter+digit+letters pattern)
            elif len(suffix_part) > 4:
                base = prefix_part
            else:
                # Default to suffix if it contains a digit
                base = suffix_part if any(c.isdigit() for c in suffix_part) else prefix_part
        else:
            # Multiple slashes - use first part
            base = parts[0]

        # Find where the first digit occurs
        for i, char in enumerate(base):
            if char.isdigit():
                return base[:i+1]

        # If no digit found, return the whole base (special event callsigns)
        if base:
            return base

        return None

    def _get_next_centurion_level(self, current: int) -> Optional[str]:
        """Get next Centurion endorsement level"""
        levels = [
            (100, "Centurion"),
            (200, "Centurion x2"),
            (300, "Centurion x3"),
            (400, "Centurion x4"),
            (500, "Centurion x5"),
            (600, "Centurion x6"),
            (700, "Centurion x7"),
            (800, "Centurion x8"),
            (900, "Centurion x9"),
            (1000, "Centurion x10"),
        ]

        for required, level_name in levels:
            if current < required:
                return level_name

        return None

    def _get_level_count(self, level_name: str) -> int:
        """Get required count for a level"""
        levels = {
            "Centurion": 100,
            "Centurion x2": 200,
            "Centurion x3": 300,
            "Centurion x4": 400,
            "Centurion x5": 500,
            "Centurion x6": 600,
            "Centurion x7": 700,
            "Centurion x8": 800,
            "Centurion x9": 900,
            "Centurion x10": 1000,
        }
        return levels.get(level_name, 100)

    def clear_cache(self):
        """Clear the analysis cache"""
        self._cache.clear()

    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        return {
            'entries': len(self._cache),
            'timeout_seconds': self.cache_timeout
        }
