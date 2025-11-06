"""
SKCC Tribune Award - Contact 50+ Centurions/Tribunes/Senators

The Tribune award is earned by making contact with 50+ different SKCC members
who are Centurions, Tribunes, or Senators.

Rules:
- Must be a Centurion first (100+ unique SKCC members)
- Contact 50+ Tribunes/Senators (from official list)
- Both operators must hold Centurion status at time of contact
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
from src.utils.skcc_number import extract_base_skcc_number
from src.skcc_awards.constants import (
    TRIBUNE_ENDORSEMENTS,
    TRIBUNE_EFFECTIVE_DATE,
    TRIBUNE_SPECIAL_EVENT_CUTOFF,
    SPECIAL_EVENT_CALLS,
    get_endorsement_level,
    get_next_endorsement_threshold
)

logger = logging.getLogger(__name__)


class TribuneAward(SKCCAwardBase):
    """SKCC Tribune Award - 50+ unique Tribune/Senator contacts"""

    def __init__(self, database):
        """
        Initialize Tribune award

        Args:
            database: Database instance for contact queries and member list lookups
        """
        super().__init__(name="Tribune", program_id="SKCC_TRIBUNE", database=database)

        # Cache Tribune and Senator member lists for validation
        self._load_member_lists()

    def _load_member_lists(self):
        """Load Tribune and Senator member lists from database"""
        try:
            # Get Tribune members
            cursor = self.database.conn.cursor()
            cursor.execute("SELECT skcc_number FROM skcc_tribune_members")
            self._tribune_numbers = {row[0] for row in cursor.fetchall()}

            # Get Senator members
            cursor.execute("SELECT skcc_number FROM skcc_senator_members")
            self._senator_numbers = {row[0] for row in cursor.fetchall()}

            # Combined list of valid members
            self._all_valid_members = self._tribune_numbers | self._senator_numbers

            logger.info(f"Loaded {len(self._tribune_numbers)} Tribune and {len(self._senator_numbers)} Senator members")
        except Exception as e:
            logger.warning(f"Could not load member lists: {e}. Tribune/Senator validation disabled.")
            self._tribune_numbers = set()
            self._senator_numbers = set()
            self._all_valid_members = set()

    def validate(self, contact: Dict[str, Any]) -> bool:
        """
        Check if a contact qualifies for Tribune award

        Requirements:
        - CW mode only
        - SKCC number present
        - Contact date on or after March 1, 2007
        - Mechanical key required (STRAIGHT, BUG, or SIDESWIPER)
        - Club calls and special event calls excluded after October 1, 2008
        - Remote station must be Tribune/Senator (checked via list if available)
        - Both operators must hold appropriate SKCC membership at time of contact

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
        if qso_date and qso_date < TRIBUNE_EFFECTIVE_DATE:
            return False

        # CRITICAL RULE: Club calls and special event calls don't count after Oct 1, 2008
        if qso_date and qso_date >= TRIBUNE_SPECIAL_EVENT_CUTOFF:
            callsign = contact.get('callsign', '').upper().strip()
            base_call = callsign.split('/')[0] if '/' in callsign else callsign

            if base_call in SPECIAL_EVENT_CALLS:
                logger.debug(
                    f"Special-event call filtered after Oct 1, 2008: {callsign} "
                    f"(date: {qso_date})"
                )
                return False

        # Remote station must be Tribune/Senator (from member lists if available)
        # If member lists are not loaded, we accept any SKCC member
        if self._all_valid_members:
            skcc_num = contact.get('skcc_number', '')
            base_number = extract_base_skcc_number(skcc_num)

            if not base_number or base_number not in self._all_valid_members:
                return False

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
