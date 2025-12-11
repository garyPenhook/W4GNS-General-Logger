"""
Needed Contacts Analyzer for Smart Log Processing

This module analyzes DX spots against the user's log and award progress to determine
which contacts are needed for award advancement. Similar to SKCC Skimmer functionality.

Uses the actual award calculator classes (Centurion, Tribune, Senator) to determine
the user's current goals and validate spotted stations.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging

from src.skcc_awards.centurion import CenturionAward
from src.skcc_awards.tribune import TribuneAward
from src.skcc_awards.senator import SenatorAward
from src.utils.skcc_number import extract_base_skcc_number, get_member_type, is_centurion
from src.skcc_roster import get_roster_manager
from src.skcc_award_rosters import get_award_roster_manager

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
    real-time analysis of DX spots. It uses the award calculator classes
    (Centurion, Tribune, Senator) to determine user's current goals.
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

        # Initialize award calculators
        self.centurion = CenturionAward(db_connection)
        self.tribune = TribuneAward(db_connection)
        self.senator = SenatorAward(db_connection)

        # Get roster managers for validation
        self.roster_manager = get_roster_manager()
        self.award_rosters = get_award_roster_manager(database=db_connection)

        # Cache for user's award progress (cleared periodically)
        self._progress_cache: Dict[str, Dict] = {}
        self._progress_cache_time: Optional[datetime] = None

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

    def _get_user_progress(self) -> Dict[str, Dict]:
        """
        Get cached user progress on all awards, updating every 5 minutes.
        Uses the award calculators to get accurate progress.
        """
        now = datetime.now()

        # Return cached progress if still valid
        if (self._progress_cache_time and
            (now - self._progress_cache_time).total_seconds() < self.cache_timeout):
            return self._progress_cache

        # Recalculate progress
        try:
            all_contacts = self.db.get_all_contacts(limit=999999)
            contacts_list = [dict(c) for c in all_contacts] if all_contacts else []

            self._progress_cache = {
                'centurion': self.centurion.calculate_progress(contacts_list),
                'tribune': self.tribune.calculate_progress(contacts_list),
                'senator': self.senator.calculate_progress(contacts_list),
            }
            self._progress_cache_time = now
        except Exception as e:
            logger.error(f"Error calculating progress: {e}")
            # Return empty progress on error
            self._progress_cache = {
                'centurion': {'current': 0, 'required': 100, 'achieved': False},
                'tribune': {'current': 0, 'required': 50, 'achieved': False},
                'senator': {'current': 0, 'required': 200, 'achieved': False},
            }

        return self._progress_cache

    def _check_skcc_awards(self, callsign: str, band: str, mode: str,
                           skcc_number: Optional[str]) -> List[NeededReason]:
        """
        Check if a spotted station is needed for SKCC awards.

        Analyzes the spotted station against the user's current award goals.
        Returns NeededReason(s) if the station helps with any award progress.

        Rules:
        - CW mode only (CW or A1A)
        - Station must have SKCC number
        - Validates against real award requirements and rosters
        """
        reasons = []

        # SKCC awards require CW mode
        if mode.upper() not in ['CW', 'A1A']:
            return reasons

        # Must have SKCC number to be useful
        if not skcc_number:
            return reasons

        try:
            # Get user's current progress
            progress = self._get_user_progress()
            centurion_progress = progress['centurion']
            tribune_progress = progress['tribune']
            senator_progress = progress['senator']

            # Extract base SKCC number for uniqueness check
            base_skcc = extract_base_skcc_number(skcc_number)
            if not base_skcc or not base_skcc.isdigit():
                return reasons

            # Determine which award the user is currently working toward
            # Priority: Senator > Tribune > Centurion

            # --- SENATOR AWARD (highest priority) ---
            if tribune_progress.get('achieved') and not senator_progress.get('achieved'):
                # User is working toward Senator
                # Check if this station is Tribune or Senator (T/S suffix)
                if is_centurion(skcc_number):  # Has C, T, or S suffix
                    member_type = get_member_type(skcc_number)
                    # For Senator, need T/S specifically (not just C)
                    if member_type in ['T', 'S']:
                        # Check via rosters first
                        is_tribune_or_senator = self.award_rosters.was_tribune_or_senator_on_date(
                            skcc_number,
                            self._get_today_date()
                        )
                        # Fallback to suffix check
                        if not is_tribune_or_senator and member_type in ['T', 'S']:
                            is_tribune_or_senator = True

                        if is_tribune_or_senator:
                            current = senator_progress.get('current', 0)
                            required = senator_progress.get('required', 200)
                            reasons.append(NeededReason(
                                award_name="SKCC Senator",
                                reason=f"Tribune/Senator member ({current}/{required})",
                                priority=1,  # Highest priority
                                current=current,
                                required=required
                            ))

            # --- TRIBUNE AWARD (medium priority) ---
            if (centurion_progress.get('achieved') and
                not tribune_progress.get('achieved')):
                # User is working toward Tribune
                # Check if this station is Centurion or higher (C/T/S suffix)
                if is_centurion(skcc_number):
                    # Check via rosters
                    is_centurion_or_higher = self.award_rosters.was_centurion_or_higher_on_date(
                        skcc_number,
                        self._get_today_date()
                    )
                    # Fallback to suffix check
                    if not is_centurion_or_higher:
                        is_centurion_or_higher = True

                    if is_centurion_or_higher:
                        current = tribune_progress.get('current', 0)
                        required = tribune_progress.get('required', 50)
                        reasons.append(NeededReason(
                            award_name="SKCC Tribune",
                            reason=f"Centurion+ member ({current}/{required})",
                            priority=2,  # High priority
                            current=current,
                            required=required
                        ))

            # --- CENTURION AWARD (lowest priority) ---
            if not centurion_progress.get('achieved'):
                # User is working toward Centurion (any SKCC member)
                # Any SKCC member with valid number counts
                current = centurion_progress.get('current', 0)
                next_level = self._get_next_centurion_level(current)
                if next_level:
                    required = self._get_level_count(next_level)
                    reasons.append(NeededReason(
                        award_name="SKCC Centurion",
                        reason=f"SKCC member for {next_level} ({current}/{required})",
                        priority=3,  # Lower priority than Tribune/Senator
                        current=current,
                        required=required
                    ))

        except Exception as e:
            logger.error(f"Error checking SKCC awards for {callsign}: {e}")

        return reasons

    def _get_today_date(self) -> str:
        """Get today's date in YYYYMMDD format"""
        return datetime.now().strftime('%Y%m%d')


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
        """Clear both analysis and progress caches"""
        self._cache.clear()
        self._progress_cache.clear()
        self._progress_cache_time = None

    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        return {
            'entries': len(self._cache),
            'timeout_seconds': self.cache_timeout
        }
