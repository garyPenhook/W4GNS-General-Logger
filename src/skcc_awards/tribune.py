"""
SKCC Tribune Award - Contact 50+ Centurions/Tribunes/Senators

The Tribune award is earned by making contact with 50+ different SKCC members
who are Centurions, Tribunes, or Senators.

Rules:
- Must be a Centurion first (100+ unique SKCC members)
- Contact 50+ Centurions/Tribunes/Senators
- Both operators must hold Centurion status at time of contact
- The QSO date must be on or after both participants' Centurion Award date
- Both parties must be SKCC members at time of contact (QSO date >= join dates)
- Exchanges must include SKCC numbers
- QSOs must be CW mode only
- Mechanical key policy: Contact must use mechanical key (STRAIGHT, BUG, or SIDESWIPER)
- Club calls and special event calls don't count after October 1, 2008
- Any band(s) allowed
- Contacts valid on or after March 1, 2007
- Each call sign counts only once (per category)
"""

import logging
from typing import Dict, List, Any, Set

from src.skcc_awards.base import SKCCAwardBase
from src.utils.skcc_number import extract_base_skcc_number, get_member_type
from src.skcc_awards.constants import (
    TRIBUNE_ENDORSEMENTS,
    TRIBUNE_EFFECTIVE_DATE,
    TRIBUNE_SPECIAL_EVENT_CUTOFF,
    SPECIAL_EVENT_CALLS,
    get_endorsement_level,
    get_next_endorsement_threshold
)
from src.skcc_roster import get_roster_manager
from src.skcc_award_rosters import get_award_roster_manager

logger = logging.getLogger(__name__)


class TribuneAward(SKCCAwardBase):
    """SKCC Tribune Award - 50+ unique Tribune/Senator contacts"""

    def __init__(self, database):
        """
        Initialize Tribune award

        Args:
            database: Database instance for contact queries
        """
        super().__init__(name="Tribune", program_id="SKCC_TRIBUNE", database=database)
        self.roster_manager = get_roster_manager()

        # Get award roster manager for Tribune/Senator validation
        self.award_rosters = get_award_roster_manager()

        # Get user's critical dates from config
        self.user_join_date = self._get_user_join_date()
        self.user_centurion_date = self._get_user_centurion_date()

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

    def validate(self, contact: Dict[str, Any]) -> bool:
        """
        Check if a contact qualifies for Tribune award

        Requirements:
        - CW mode only
        - SKCC number present
        - Contact date on or after March 1, 2007
        - Mechanical key required (STRAIGHT, BUG, or SIDESWIPER)
        - Club calls and special event calls excluded after October 1, 2008
        - Remote station must have Centurion/Tribune/Senator status (C, T, or S suffix)
        - Both parties must be SKCC members at time of contact
        - QSO date must be on/after both participants' Centurion Award dates
        - QSO date must be on/after user's Centurion achievement date

        Args:
            contact: Contact record dictionary

        Returns:
            True if contact qualifies for Tribune award
        """
        # Check common SKCC rules (CW mode, mechanical key, SKCC number)
        if not self.validate_common_rules(contact):
            return False

        # Get contact date
        qso_date = contact.get('date', '')
        if qso_date:
            qso_date = qso_date.replace('-', '')  # Normalize YYYY-MM-DD to YYYYMMDD

        # Check contact date (must be on/after March 1, 2007)
        if not qso_date or qso_date < TRIBUNE_EFFECTIVE_DATE:
            logger.debug(f"Contact before Tribune effective date (Mar 1, 2007): {qso_date}")
            return False

        # Get callsign (remove portable/suffix indicators)
        callsign = contact.get('callsign', '').upper().strip()
        base_call = callsign.split('/')[0] if '/' in callsign else callsign

        # CRITICAL RULE: Club calls and special event calls don't count after Oct 1, 2008
        if qso_date >= TRIBUNE_SPECIAL_EVENT_CUTOFF:
            if base_call in SPECIAL_EVENT_CALLS:
                logger.debug(
                    f"Special-event call filtered after Oct 1, 2008: {callsign} "
                    f"(date: {qso_date})"
                )
                return False

<<<<<<< HEAD
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

        # CRITICAL RULE: Remote station must have been Tribune or Senator at time of QSO
        # This is validated against the official SKCC award rosters
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

        # CRITICAL RULE: "The QSO date must be on or after both participants' Centurion Award date"
        # Check user's Centurion achievement date
        if self.user_centurion_date and qso_date < self.user_centurion_date:
            logger.debug(
                f"Contact {base_call} not valid: QSO date {qso_date} before "
                f"user Centurion date {self.user_centurion_date}"
            )
            return False

        # Note: We cannot verify the contacted station's exact Centurion achievement date
        # without historical records. We rely on the C/T/S suffix in their SKCC number
        # or current roster status as evidence they hold/held Centurion status.

        return True

    def calculate_progress(self, contacts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate Tribune award progress

        Counts unique Tribune/Senator SKCC numbers contacted.

        Args:
            contacts: List of contact records

        Returns:
            {
                'current': int,        # Unique Tribune members contacted
                'required': int,       # Always 50 for base award
                'achieved': bool,      # True if Centurion AND 50+ members
                'progress_pct': float, # Percentage toward 50
                'endorsement': str,    # Current endorsement level (Tribune, Tx2, etc.)
                'unique_members': set, # Set of unique SKCC numbers
                'is_centurion': bool,  # Whether user has achieved Centurion
                'centurion_count': int # User's Centurion contact count
            }
        """
        # First, check if user is a Centurion (prerequisite)
        # Count unique SKCC members for Centurion check
        all_contacts = self.database.get_all_contacts(limit=999999)
        unique_centurions = set()

        for contact in all_contacts:
            contact_dict = dict(contact)
            if contact_dict.get('mode', '').upper() == 'CW' and contact_dict.get('skcc_number'):
                skcc_num = contact_dict.get('skcc_number', '').strip()
                if skcc_num:
                    base_number = extract_base_skcc_number(skcc_num)
                    if base_number and base_number.isdigit():
                        unique_centurions.add(base_number)

        is_centurion = len(unique_centurions) >= 100

        # Collect unique Tribune members
        unique_members = set()

        for contact in contacts:
            if self.validate(contact):
                skcc_number = contact.get('skcc_number', '').strip()
                if skcc_number:
                    base_number = extract_base_skcc_number(skcc_number)
                    if base_number and base_number.isdigit():
                        unique_members.add(base_number)

        current_count = len(unique_members)
        required_count = 50

        # Determine endorsement level using constants
        endorsement_level = get_endorsement_level(current_count, TRIBUNE_ENDORSEMENTS)
        next_level = get_next_endorsement_threshold(current_count, TRIBUNE_ENDORSEMENTS)

        return {
            'current': current_count,
            'required': required_count,
            'achieved': is_centurion and current_count >= required_count,
            'progress_pct': min(100.0, (current_count / required_count) * 100),
            'endorsement': endorsement_level,
            'unique_members': unique_members,
            'next_level_count': next_level,
            'is_centurion': is_centurion,
            'centurion_count': len(unique_centurions),
            'prerequisite_met': is_centurion
        }

    def get_requirements(self) -> Dict[str, Any]:
        """
        Return Tribune award requirements

        Returns:
            Award requirements dictionary
        """
        return {
            'name': 'SKCC Tribune',
            'description': 'Contact 50+ Centurions/Tribunes/Senators (must be Centurion first)',
            'base_requirement': 50,
            'base_units': 'unique Tribune/Senator members',
            'prerequisite': 'Must achieve Centurion first (100+ SKCC members)',
            'prerequisite_requirement': 100,
            'modes': ['CW'],
            'bands': ['All'],
            'mechanical_key': True,
            'key_types': ['STRAIGHT', 'BUG', 'SIDESWIPER'],
            'effective_date': 'March 1, 2007 or later',
            'validity_rule': 'Both operators must hold Centurion status at time of contact',
            'special_rules': [
                'Must be Centurion before Tribune contacts count',
                'Special event calls excluded after October 1, 2008',
                'Remote station must be Tribune or Senator (from official list)',
                'Each SKCC number counts only once'
            ],
            'endorsements_available': True,
            'endorsement_increments': [50, 100, 150, 200, 250, 300, 350, 400, 450, 500, 750, 1000, 1250, 1500]
        }

    def get_endorsements(self) -> List[Dict[str, Any]]:
        """
        Return list of Tribune endorsement levels

        Returns:
            List of endorsement level dictionaries
        """
        return [
            {'level': 50, 'description': 'Tribune', 'contacts_needed': 50},
            {'level': 100, 'description': 'Tribune x2', 'contacts_needed': 100},
            {'level': 150, 'description': 'Tribune x3', 'contacts_needed': 150},
            {'level': 200, 'description': 'Tribune x4', 'contacts_needed': 200},
            {'level': 250, 'description': 'Tribune x5', 'contacts_needed': 250},
            {'level': 300, 'description': 'Tribune x6', 'contacts_needed': 300},
            {'level': 350, 'description': 'Tribune x7', 'contacts_needed': 350},
            {'level': 400, 'description': 'Tribune x8', 'contacts_needed': 400},
            {'level': 450, 'description': 'Tribune x9', 'contacts_needed': 450},
            {'level': 500, 'description': 'Tribune x10', 'contacts_needed': 500},
            {'level': 750, 'description': 'Tribune x15', 'contacts_needed': 750},
            {'level': 1000, 'description': 'Tribune x20', 'contacts_needed': 1000},
            {'level': 1250, 'description': 'Tribune x25', 'contacts_needed': 1250},
            {'level': 1500, 'description': 'Tribune x30', 'contacts_needed': 1500},
        ]
