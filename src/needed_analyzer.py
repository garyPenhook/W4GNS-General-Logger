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
    already_worked: bool = False  # Track if station already worked on band/mode

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
                highest_priority=99,
                already_worked=True
            )
            self._cache[cache_key] = (analysis, datetime.now())
            return analysis

        # Analyze for SKCC awards only
        reasons.extend(self._check_skcc_awards(callsign, band, mode, skcc_number))

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
            cursor = self.db.conn.cursor()
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
            cursor = self.db.conn.cursor()
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
