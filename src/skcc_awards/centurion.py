"""
SKCC Centurion Award - Contact 100+ Different SKCC Members

The Centurion award is earned by making contact with 100 different SKCC members.
Endorsements are available in 100-contact increments up to Centurion x10,
then in 500-contact increments (Cx15, Cx20, etc.).

Rules:
- Both operators must hold SKCC membership at time of contact
- QSO dates must match or exceed both participants' SKCC join dates
- Exchanges must include SKCC numbers
- QSOs must be CW mode only
- Mechanical key policy: Contacts must use straight key, sideswiper (cootie), or bug
- Club calls and special event calls don't count after December 1, 2009
- Any band(s) allowed
- Each call sign counts only once (per category)
"""

import logging
from typing import Dict, List, Any, Set

from src.skcc_awards.base import SKCCAwardBase
from src.utils.skcc_number import extract_base_skcc_number
from src.skcc_awards.constants import (
    CENTURION_ENDORSEMENTS,
    CENTURION_SPECIAL_EVENT_CUTOFF,
    SPECIAL_EVENT_CALLS,
    get_endorsement_level,
    get_next_endorsement_threshold
)
from src.skcc_roster import get_roster_manager

logger = logging.getLogger(__name__)


class CenturionAward(SKCCAwardBase):
    """SKCC Centurion Award - 100+ unique SKCC member contacts"""

    def __init__(self, database):
        """
        Initialize Centurion award

        Args:
            database: Database instance for contact queries
        """
        super().__init__(name="Centurion", program_id="SKCC_CENTURION", database=database)
        self.roster_manager = get_roster_manager()

        # Get user's SKCC join date from database config (if set)
        # This should be in YYYYMMDD format
        self.user_join_date = self._get_user_join_date()

    def _get_user_join_date(self) -> str:
        """
        Get user's SKCC join date from config.

        Returns:
            User's join date in YYYYMMDD format, or empty string if not set
        """
        # Access config through database if available
        if hasattr(self.database, 'config'):
            return self.database.config.get('skcc.join_date', '')
        return ''

    def validate(self, contact: Dict[str, Any]) -> bool:
        """
        Check if a contact qualifies for Centurion award

        Requirements:
        - CW mode only
        - SKCC number present on both sides
        - Mechanical key required (STRAIGHT, BUG, or SIDESWIPER)
        - Club calls and special event calls excluded after December 1, 2009
        - Both operators must hold SKCC membership at time of contact
        - QSO dates must match or exceed both participants' SKCC join dates

        Args:
            contact: Contact record dictionary

        Returns:
            True if contact qualifies for Centurion award
        """
        # Check common SKCC rules (CW mode, mechanical key, SKCC number)
        if not self.validate_common_rules(contact):
            return False

        # Get contact date for date-based validations
        qso_date = contact.get('date', '')  # Expecting YYYYMMDD or YYYY-MM-DD format

        # Normalize date format (handle YYYY-MM-DD or YYYYMMDD)
        if qso_date:
            qso_date = qso_date.replace('-', '')

        # Get callsign (remove portable/suffix indicators)
        callsign = contact.get('callsign', '').upper().strip()
        base_call = callsign.split('/')[0] if '/' in callsign else callsign

        # CRITICAL RULE: Club calls and special event calls don't count after Dec 1, 2009
        if qso_date and qso_date >= CENTURION_SPECIAL_EVENT_CUTOFF:
            if base_call in SPECIAL_EVENT_CALLS:
                logger.debug(
                    f"Special-event call filtered after Dec 1, 2009: {callsign} "
                    f"(date: {qso_date})"
                )
                return False

        # Verify remote operator has valid SKCC number
        skcc_num = contact.get('skcc_number', '').strip()
        if skcc_num:
            base_number = extract_base_skcc_number(skcc_num)
            if not base_number or not base_number.isdigit():
                logger.debug(f"Invalid SKCC number format: {skcc_num}")
                return False

        # CRITICAL RULE: "Both parties in the QSO must be SKCC members at the time of the QSO"
        # Check if contacted station was SKCC member at time of QSO
        if not self.roster_manager.was_member_on_date(base_call, qso_date):
            logger.debug(
                f"Contact {base_call} not valid: not an SKCC member on {qso_date} "
                f"(join date: {self.roster_manager.get_join_date(base_call)})"
            )
            return False

        # CRITICAL RULE: "QSO dates must match or exceed both participants' SKCC join dates"
        # Check if QSO happened on or after user's join date
        if self.user_join_date and qso_date:
            if qso_date < self.user_join_date:
                logger.debug(
                    f"Contact {base_call} not valid: QSO date {qso_date} before "
                    f"user join date {self.user_join_date}"
                )
                return False

        return True

    def calculate_progress(self, contacts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate Centurion award progress

        Counts unique SKCC numbers contacted (base number without suffixes).

        Args:
            contacts: List of contact records

        Returns:
            {
                'current': int,        # Unique SKCC members contacted
                'required': int,       # Always 100 for base award
                'achieved': bool,      # True if 100+ members
                'progress_pct': float, # Percentage toward 100
                'endorsement': str,    # Current endorsement level (Centurion, Cx2, etc.)
                'unique_members': set  # Set of unique SKCC numbers
            }
        """
        # Collect unique SKCC numbers (base number without suffixes like C, T, S, x)
        unique_members = set()

        for contact in contacts:
            if self.validate(contact):
                skcc_number = contact.get('skcc_number', '').strip()
                if skcc_number:
                    base_number = extract_base_skcc_number(skcc_number)
                    if base_number and base_number.isdigit():
                        unique_members.add(base_number)

        current_count = len(unique_members)
        required_count = 100

        # Determine endorsement level using constants
        endorsement_level = get_endorsement_level(current_count, CENTURION_ENDORSEMENTS)
        next_level = get_next_endorsement_threshold(current_count, CENTURION_ENDORSEMENTS)

        return {
            'current': current_count,
            'required': required_count,
            'achieved': current_count >= required_count,
            'progress_pct': min(100.0, (current_count / required_count) * 100),
            'endorsement': endorsement_level,
            'unique_members': unique_members,
            'next_level_count': next_level
        }

    def get_requirements(self) -> Dict[str, Any]:
        """
        Return Centurion award requirements

        Returns:
            Award requirements dictionary
        """
        return {
            'name': 'SKCC Centurion',
            'description': 'Contact 100 different SKCC members',
            'base_requirement': 100,
            'base_units': 'unique SKCC members',
            'modes': ['CW'],
            'bands': ['All'],
            'mechanical_key': True,
            'key_types': ['STRAIGHT', 'BUG', 'SIDESWIPER'],
            'validity_rule': 'Both operators must hold SKCC membership at time of contact',
            'special_rules': [
                'Club calls (K9SKC) and special event calls excluded after December 1, 2009',
                'Each SKCC number counts only once (base number without suffixes)',
                'Any band allowed',
                'QSO must use mechanical key (no electronic keyers)'
            ],
            'endorsements_available': True,
            'endorsement_increments': [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1500, 2000, 2500, 3000, 3500, 4000]
        }

    def get_endorsements(self) -> List[Dict[str, Any]]:
        """
        Return list of Centurion endorsement levels

        Returns:
            List of endorsement level dictionaries
        """
        return [
            {'level': 100, 'description': 'Centurion', 'contacts_needed': 100},
            {'level': 200, 'description': 'Centurion x2', 'contacts_needed': 200},
            {'level': 300, 'description': 'Centurion x3', 'contacts_needed': 300},
            {'level': 400, 'description': 'Centurion x4', 'contacts_needed': 400},
            {'level': 500, 'description': 'Centurion x5', 'contacts_needed': 500},
            {'level': 600, 'description': 'Centurion x6', 'contacts_needed': 600},
            {'level': 700, 'description': 'Centurion x7', 'contacts_needed': 700},
            {'level': 800, 'description': 'Centurion x8', 'contacts_needed': 800},
            {'level': 900, 'description': 'Centurion x9', 'contacts_needed': 900},
            {'level': 1000, 'description': 'Centurion x10', 'contacts_needed': 1000},
            {'level': 1500, 'description': 'Centurion x15', 'contacts_needed': 1500},
            {'level': 2000, 'description': 'Centurion x20', 'contacts_needed': 2000},
            {'level': 2500, 'description': 'Centurion x25', 'contacts_needed': 2500},
            {'level': 3000, 'description': 'Centurion x30', 'contacts_needed': 3000},
            {'level': 3500, 'description': 'Centurion x35', 'contacts_needed': 3500},
            {'level': 4000, 'description': 'Centurion x40', 'contacts_needed': 4000},
        ]
