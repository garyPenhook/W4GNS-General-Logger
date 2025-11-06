"""
SKCC Senator Award - Contact 200+ Tribune/Senator members after achieving Tribune x8

The Senator award is earned by making contact with 200+ different SKCC members
who are Tribunes or Senators, AFTER achieving Tribune x8 status.

Rules:
- Must achieve Tribune x8 first (400+ Tribune/Senator contacts)
- Only contacts AFTER Tribune x8 achievement count toward Senator
- Contact 200+ additional Tribunes/Senators (ONLY T or S suffix, NOT C)
- Both parties must be SKCC members at time of contact (QSO date >= join dates)
- Both parties must hold Centurion status at time of contact
- Exchanges must include SKCC numbers
- QSOs must be CW mode only
- Mechanical key policy: Contact must use mechanical key (STRAIGHT, BUG, or SIDESWIPER)
- Club calls don't qualify for Senator
- Any band(s) allowed
- Contacts valid on or after August 1, 2013
"""

import logging
from typing import Dict, List, Any, Set, Optional
from datetime import datetime

from src.skcc_awards.base import SKCCAwardBase
from src.utils.skcc_number import extract_base_skcc_number, get_member_type
from src.skcc_awards.constants import (
    SENATOR_ENDORSEMENTS,
    SENATOR_EFFECTIVE_DATE,
    SPECIAL_EVENT_CALLS,
    get_endorsement_level,
    get_next_endorsement_threshold
)
from src.skcc_roster import get_roster_manager
from src.skcc_award_rosters import get_award_roster_manager

logger = logging.getLogger(__name__)


class SenatorAward(SKCCAwardBase):
    """SKCC Senator Award - 200+ unique Tribune/Senator contacts after Tribune x8"""

    def __init__(self, database):
        """
        Initialize Senator award

        Args:
            database: Database instance for contact queries
        """
        super().__init__(name="Senator", program_id="SKCC_SENATOR", database=database)
        self.roster_manager = get_roster_manager()

        # Get award roster manager for Tribune/Senator validation
        self.award_rosters = get_award_roster_manager(database=database)

        # Get user's critical dates from config
        self.user_join_date = self._get_user_join_date()
        self.user_centurion_date = self._get_user_centurion_date()
        self.user_tribune_x8_date = self._get_user_tribune_x8_date()

    def _get_user_join_date(self) -> str:
        """Get user's SKCC join date from config (YYYYMMDD format)"""
        if hasattr(self.database, 'config'):
            return self.database.config.get('skcc.join_date', '')
        return ''

    def _get_user_centurion_date(self) -> str:
        """Get user's Centurion achievement date from config (YYYYMMDD format)"""
        if hasattr(self.database, 'config'):
            return self.database.config.get('skcc.centurion_date', '')
        return ''

    def _get_user_tribune_x8_date(self) -> str:
        """Get user's Tribune x8 achievement date from config (YYYYMMDD format)"""
        if hasattr(self.database, 'config'):
            return self.database.config.get('skcc.tribune_x8_date', '')
        return ''

    def validate(self, contact: Dict[str, Any]) -> bool:
        """
        Check if a contact qualifies for Senator award

        Requirements:
        - CW mode only
        - SKCC number present
        - Contact date on or after August 1, 2013
        - Mechanical key required (STRAIGHT, BUG, or SIDESWIPER)
        - Club calls excluded
        - Remote station must have Tribune/Senator status (T or S suffix ONLY, NOT C)
        - Both parties must be SKCC members at time of contact
        - Both parties must hold Centurion status at time of contact
        - QSO date must be on/after user's Tribune x8 achievement date

        Args:
            contact: Contact record dictionary

        Returns:
            True if contact qualifies for Senator award
        """
        # Check common SKCC rules (CW mode, mechanical key, SKCC number)
        if not self.validate_common_rules(contact):
            return False

        # Get contact date
        qso_date = contact.get('date', '')
        if qso_date:
            qso_date = qso_date.replace('-', '')  # Normalize YYYY-MM-DD to YYYYMMDD

        # Check contact date (must be on/after August 1, 2013)
        if not qso_date or qso_date < SENATOR_EFFECTIVE_DATE:
            logger.debug(f"Contact before Senator effective date (Aug 1, 2013): {qso_date}")
            return False

        # Get callsign (remove portable/suffix indicators)
        callsign = contact.get('callsign', '').upper().strip()
        base_call = callsign.split('/')[0] if '/' in callsign else callsign

        # CRITICAL RULE: Club calls don't qualify for Senator
        if base_call in SPECIAL_EVENT_CALLS:
            logger.debug(
                f"Club/special-event call filtered for Senator: {callsign} "
                f"(date: {qso_date})"
            )
            return False

        # CRITICAL RULE: "Both parties in the QSO must be SKCC members at the time of the QSO"
        # Check if contacted station was SKCC member at time of QSO
        if not self.roster_manager.was_member_on_date(base_call, qso_date):
            logger.debug(
                f"Contact {base_call} not valid: not an SKCC member on {qso_date}"
            )
            return False

        # CRITICAL RULE: User must have been SKCC member at time of QSO
        if self.user_join_date and qso_date < self.user_join_date:
            logger.debug(
                f"Contact {base_call} not valid: QSO date {qso_date} before "
                f"user join date {self.user_join_date}"
            )
            return False

        # CRITICAL RULE: User must hold Centurion status at time of QSO
        if self.user_centurion_date and qso_date < self.user_centurion_date:
            logger.debug(
                f"Contact {base_call} not valid: QSO date {qso_date} before "
                f"user Centurion date {self.user_centurion_date}"
            )
            return False

        # CRITICAL RULE: Remote station must have been Tribune or Senator at time of QSO
        # This is validated against the official SKCC award rosters
        # "Senator applications require contacts exclusively with Tribunes or Senators only"
        skcc_num = contact.get('skcc_number', '').strip()
        if not skcc_num:
            logger.debug(f"Contact {base_call} missing SKCC number")
            return False

        # Check if the contacted station was Tribune or Senator at time of QSO
        if not self.award_rosters.was_tribune_or_senator_on_date(skcc_num, qso_date):
            logger.debug(
                f"Contact {callsign} with SKCC#{skcc_num} not valid: "
                f"was not Tribune/Senator on {qso_date}"
            )
            return False

        return True

    def _find_tribune_x8_date(self, contacts: List[Dict[str, Any]]) -> Optional[str]:
        """
        Find the date when Tribune x8 was achieved (400+ Tribune/Senator contacts)

        Args:
            contacts: List of all contact records

        Returns:
            Date string (YYYYMMDD) when Tribune x8 was achieved, or None if not achieved
        """
        # Sort contacts by date
        sorted_contacts = sorted(
            [c for c in contacts if c.get('date')],
            key=lambda x: x.get('date', '').replace('-', '')
        )

        # Track unique Tribune/Senator members chronologically
        unique_members = set()
        tribune_x8_threshold = 400

        for contact in sorted_contacts:
            if self.validate(contact):
                skcc_number = contact.get('skcc_number', '').strip()
                if skcc_number:
                    base_number = extract_base_skcc_number(skcc_number)
                    if base_number and base_number.isdigit():
                        unique_members.add(base_number)

                        # Check if Tribune x8 achieved
                        if len(unique_members) >= tribune_x8_threshold:
                            qso_date = contact.get('date', '').replace('-', '')
                            logger.info(f"Tribune x8 achieved on {qso_date} with {len(unique_members)} contacts")
                            return qso_date

        return None

    def calculate_progress(self, contacts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate Senator award progress

        Counts unique Tribune/Senator SKCC numbers contacted AFTER achieving Tribune x8.

        Args:
            contacts: List of contact records

        Returns:
            {
                'current': int,             # Unique Senator-qualifying contacts after Tribune x8
                'required': int,            # Always 200 for base award
                'achieved': bool,           # True if Tribune x8 AND 200+ post-x8 contacts
                'progress_pct': float,      # Percentage toward 200
                'endorsement': str,         # Current endorsement level (Senator, Sx2, etc.)
                'unique_members': set,      # Set of unique SKCC numbers (post-Tribune x8)
                'is_tribune_x8': bool,      # Whether user has achieved Tribune x8
                'tribune_x8_date': str,     # Date Tribune x8 was achieved (YYYYMMDD)
                'tribune_x8_count': int,    # Total Tribune contacts (for x8 check)
                'total_tribune_contacts': int  # All Tribune contacts (including pre-x8)
            }
        """
        # First, check if user has manually set Tribune x8 date, otherwise auto-calculate
        tribune_x8_date = self.user_tribune_x8_date
        if not tribune_x8_date:
            tribune_x8_date = self._find_tribune_x8_date(contacts)
        is_tribune_x8 = tribune_x8_date is not None and tribune_x8_date != ''

        # Count total Tribune contacts for context
        total_tribune_members = set()
        for contact in contacts:
            if self.validate(contact):
                skcc_number = contact.get('skcc_number', '').strip()
                if skcc_number:
                    base_number = extract_base_skcc_number(skcc_number)
                    if base_number and base_number.isdigit():
                        total_tribune_members.add(base_number)

        tribune_x8_count = len(total_tribune_members)

        # Collect unique Senator-qualifying members (AFTER Tribune x8 date)
        unique_senator_members = set()

        if is_tribune_x8:
            for contact in contacts:
                if self.validate(contact):
                    qso_date = contact.get('date', '').replace('-', '')

                    # Only count contacts AFTER Tribune x8 achievement
                    if qso_date and qso_date >= tribune_x8_date:
                        skcc_number = contact.get('skcc_number', '').strip()
                        if skcc_number:
                            base_number = extract_base_skcc_number(skcc_number)
                            if base_number and base_number.isdigit():
                                unique_senator_members.add(base_number)

        current_count = len(unique_senator_members)
        required_count = 200

        # Determine endorsement level using constants
        endorsement_level = get_endorsement_level(current_count, SENATOR_ENDORSEMENTS)
        next_level = get_next_endorsement_threshold(current_count, SENATOR_ENDORSEMENTS)

        return {
            'current': current_count,
            'required': required_count,
            'achieved': is_tribune_x8 and current_count >= required_count,
            'progress_pct': min(100.0, (current_count / required_count) * 100),
            'endorsement': endorsement_level,
            'unique_members': unique_senator_members,
            'next_level_count': next_level,
            'is_tribune_x8': is_tribune_x8,
            'tribune_x8_date': tribune_x8_date if tribune_x8_date else 'Not achieved',
            'tribune_x8_count': tribune_x8_count,
            'total_tribune_contacts': len(total_tribune_members),
            'prerequisite_met': is_tribune_x8
        }

    def get_requirements(self) -> Dict[str, Any]:
        """
        Return Senator award requirements

        Returns:
            Award requirements dictionary
        """
        return {
            'name': 'SKCC Senator',
            'description': 'Contact 200+ Tribunes/Senators after achieving Tribune x8 (must be Tribune x8 first)',
            'base_requirement': 200,
            'base_units': 'unique Tribune/Senator members (after Tribune x8)',
            'prerequisite': 'Must achieve Tribune x8 first (400+ Tribune/Senator contacts)',
            'prerequisite_requirement': 400,
            'modes': ['CW'],
            'bands': ['All'],
            'mechanical_key': True,
            'key_types': ['STRAIGHT', 'BUG', 'SIDESWIPER'],
            'effective_date': 'August 1, 2013 or later',
            'validity_rule': 'Only contacts AFTER Tribune x8 achievement count toward Senator',
            'special_rules': [
                'Must achieve Tribune x8 before Senator contacts count',
                'Club calls do not qualify for Senator',
                'Remote station must be Tribune or Senator (from official list)',
                'Each SKCC number counts only once',
                'Contacts must occur on or after achieving Tribune x8 status'
            ],
            'endorsements_available': True,
            'endorsement_increments': [200, 400, 600, 800, 1000, 1200, 1400, 1600, 1800, 2000]
        }

    def get_endorsements(self) -> List[Dict[str, Any]]:
        """
        Return list of Senator endorsement levels

        Returns:
            List of endorsement level dictionaries
        """
        return [
            {'level': 200, 'description': 'Senator', 'contacts_needed': 200},
            {'level': 400, 'description': 'Senator x2', 'contacts_needed': 400},
            {'level': 600, 'description': 'Senator x3', 'contacts_needed': 600},
            {'level': 800, 'description': 'Senator x4', 'contacts_needed': 800},
            {'level': 1000, 'description': 'Senator x5', 'contacts_needed': 1000},
            {'level': 1200, 'description': 'Senator x6', 'contacts_needed': 1200},
            {'level': 1400, 'description': 'Senator x7', 'contacts_needed': 1400},
            {'level': 1600, 'description': 'Senator x8', 'contacts_needed': 1600},
            {'level': 1800, 'description': 'Senator x9', 'contacts_needed': 1800},
            {'level': 2000, 'description': 'Senator x10', 'contacts_needed': 2000},
        ]
