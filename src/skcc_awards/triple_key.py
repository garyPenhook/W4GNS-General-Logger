"""
SKCC Triple Key Award - Contact 100+ members with each of three key types

The Triple Key award is earned by making contact with 100+ different SKCC members
using EACH of the three mechanical key types: Straight Key, Bug, and Sideswiper.

Rules:
- Contact 300 different SKCC members distributed as:
  * 100 contacts using your Straight Key
  * 100 contacts using your Bug
  * 100 contacts using your Sideswiper
- CRITICAL: All 300 contacts must be with DIFFERENT members
- Each member can only count ONCE across all key types
- CW mode exclusively
- Mechanical key policy: STRAIGHT, BUG, or SIDESWIPER required
- Both operators must have SKCC membership
- Key type must be logged in contact (CRITICAL!)
- Remote stations don't need to be participating in the award
- Any band allowed
- Contacts valid on or after November 10, 2018
"""

import logging
from typing import Dict, List, Any, Set
from collections import defaultdict

from src.skcc_awards.base import SKCCAwardBase
from src.utils.skcc_number import extract_base_skcc_number
from src.skcc_awards.constants import (
    TRIPLE_KEY_ENDORSEMENTS,
    TRIPLE_KEY_EFFECTIVE_DATE,
    VALID_KEY_TYPES,
    get_endorsement_level,
    get_next_endorsement_threshold
)
from src.skcc_roster import get_roster_manager

logger = logging.getLogger(__name__)


class TripleKeyAward(SKCCAwardBase):
    """SKCC Triple Key Award - 100+ unique members with each of 3 key types"""

    def __init__(self, database):
        """
        Initialize Triple Key award

        Args:
            database: Database instance for contact queries
        """
        super().__init__(name="Triple Key", program_id="SKCC_TRIPLE_KEY", database=database)
        self.roster_manager = get_roster_manager()
        self.user_join_date = self._get_user_join_date()

    def _get_user_join_date(self) -> str:
        """
        Get user's SKCC join date from config.

        Returns:
            User's join date in YYYYMMDD format, or empty string if not set
        """
        if hasattr(self.database, 'config'):
            return self.database.config.get('skcc.join_date', '')
        return ''

    def validate(self, contact: Dict[str, Any]) -> bool:
        """
        Check if a contact qualifies for Triple Key award

        Requirements:
        - CW mode only
        - SKCC number present
        - Contact date on or after November 10, 2018
        - Mechanical key required (STRAIGHT, BUG, or SIDESWIPER)
        - Key type MUST be logged (CRITICAL!)
        - Both operators must have SKCC membership

        Args:
            contact: Contact record dictionary

        Returns:
            True if contact qualifies for Triple Key award
        """
        # Check common SKCC rules (CW mode, mechanical key, SKCC number)
        if not self.validate_common_rules(contact):
            return False

        # Get contact date
        qso_date = contact.get('qso_date', contact.get('date', ''))
        if qso_date:
            qso_date = qso_date.replace('-', '')  # Normalize YYYY-MM-DD to YYYYMMDD

        # Check contact date (must be on/after November 10, 2018)
        if qso_date and qso_date < TRIPLE_KEY_EFFECTIVE_DATE:
            return False

        # CRITICAL RULE: Key type must be logged
        key_type = contact.get('key_type', '').upper()
        if not key_type or key_type not in VALID_KEY_TYPES:
            logger.debug(f"Missing or invalid key type for Triple Key: {key_type}")
            return False

        # Get callsign (remove portable/suffix indicators)
        callsign = contact.get('callsign', '').upper().strip()
        base_call = callsign.split('/')[0] if '/' in callsign else callsign

        # Verify valid SKCC number
        skcc_num = contact.get('skcc_number', '').strip()
        if skcc_num:
            base_number = extract_base_skcc_number(skcc_num)
            if not base_number or not base_number.isdigit():
                return False

        # CRITICAL RULE: "Both operators must have SKCC membership at time of contact"
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

        return True

    def calculate_progress(self, contacts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate Triple Key award progress

        CRITICAL RULE: Tracks 300 DIFFERENT SKCC members, with 100 contacted using each
        key type. Each member can only count ONCE across all key types (first contact wins).

        Args:
            contacts: List of contact records

        Returns:
            {
                'current': int,                    # Minimum count across all 3 key types
                'required': int,                   # Always 100 per key type (300 total)
                'achieved': bool,                  # True if 100+ members with ALL 3 keys
                'progress_pct': float,             # Percentage toward 100 (based on minimum)
                'endorsement': str,                # Current endorsement level
                'total_contacts': int,             # Count of unique members (max 300)
                'straight_count': int,             # Unique members with Straight Key
                'bug_count': int,                  # Unique members with Bug
                'sideswiper_count': int,           # Unique members with Sideswiper
                'straight_members': set,           # SKCC numbers for Straight Key
                'bug_members': set,                # SKCC numbers for Bug
                'sideswiper_members': set,         # SKCC numbers for Sideswiper
                'by_key_type': dict,               # Summary per key type
                'next_level_count': int            # Total contacts for next endorsement
                'duplicate_contacts': int,         # Contacts rejected (member already counted)
            }
        """
        # Track unique members by key type
        members_by_key: Dict[str, Set[str]] = {
            'STRAIGHT': set(),
            'BUG': set(),
            'SIDESWIPER': set()
        }

        # Track which members have already been counted (to enforce uniqueness)
        all_members_counted: Set[str] = set()
        duplicate_contacts = 0

        # Sort contacts by date to ensure earliest contact wins
        sorted_contacts = sorted(
            [c for c in contacts if self.validate(c)],
            key=lambda x: (x.get('qso_date', x.get('date', '')), x.get('time_on', ''))
        )

        # Process all qualifying contacts
        for contact in sorted_contacts:
            skcc_number = contact.get('skcc_number', '').strip()
            key_type = contact.get('key_type', '').upper()

            if skcc_number and key_type in VALID_KEY_TYPES:
                base_number = extract_base_skcc_number(skcc_number)
                if base_number and base_number.isdigit():
                    # CRITICAL: Each member can only count ONCE across all key types
                    if base_number not in all_members_counted:
                        members_by_key[key_type].add(base_number)
                        all_members_counted.add(base_number)
                    else:
                        duplicate_contacts += 1
                        logger.debug(
                            f"Triple Key: Member {base_number} already counted, "
                            f"ignoring duplicate contact with {key_type}"
                        )

        # Count unique members per key type
        straight_count = len(members_by_key['STRAIGHT'])
        bug_count = len(members_by_key['BUG'])
        sideswiper_count = len(members_by_key['SIDESWIPER'])

        # For Triple Key, the "current" count is the MINIMUM across all 3 key types
        # because ALL three must have 100+ for the base award
        min_count = min(straight_count, bug_count, sideswiper_count)

        # CRITICAL: Total contacts is count of UNIQUE members (not sum of key types)
        # Each member can only count once, so this is the total number of different members
        total_unique_members = len(all_members_counted)

        # Award is achieved when ALL three key types have 100+ unique members
        required_per_key = 100
        achieved = (straight_count >= required_per_key and
                   bug_count >= required_per_key and
                   sideswiper_count >= required_per_key)

        # For endorsement calculation, use total unique members
        # Endorsements are based on 300, 600, 900, etc. unique members total
        endorsement_level = get_endorsement_level(total_unique_members, TRIPLE_KEY_ENDORSEMENTS)
        next_level = get_next_endorsement_threshold(total_unique_members, TRIPLE_KEY_ENDORSEMENTS)

        # Progress percentage based on minimum count (most restrictive)
        progress_pct = min(100.0, (min_count / required_per_key) * 100)

        return {
            'current': min_count,
            'required': required_per_key,
            'achieved': achieved,
            'progress_pct': progress_pct,
            'endorsement': endorsement_level,
            'total_contacts': total_unique_members,
            'straight_count': straight_count,
            'bug_count': bug_count,
            'sideswiper_count': sideswiper_count,
            'straight_members': members_by_key['STRAIGHT'],
            'bug_members': members_by_key['BUG'],
            'sideswiper_members': members_by_key['SIDESWIPER'],
            'duplicate_contacts': duplicate_contacts,
            'by_key_type': {
                'STRAIGHT': {
                    'count': straight_count,
                    'required': required_per_key,
                    'achieved': straight_count >= required_per_key,
                    'progress_pct': min(100.0, (straight_count / required_per_key) * 100)
                },
                'BUG': {
                    'count': bug_count,
                    'required': required_per_key,
                    'achieved': bug_count >= required_per_key,
                    'progress_pct': min(100.0, (bug_count / required_per_key) * 100)
                },
                'SIDESWIPER': {
                    'count': sideswiper_count,
                    'required': required_per_key,
                    'achieved': sideswiper_count >= required_per_key,
                    'progress_pct': min(100.0, (sideswiper_count / required_per_key) * 100)
                }
            },
            'next_level_count': next_level
        }

    def get_requirements(self) -> Dict[str, Any]:
        """
        Return Triple Key award requirements

        Returns:
            Award requirements dictionary
        """
        return {
            'name': 'SKCC Triple Key',
            'description': 'Contact 300 different members using each of 3 mechanical key types',
            'base_requirement': '300 different members: 100 with straight key, 100 with bug, 100 with sideswiper',
            'key_types_required': ['STRAIGHT', 'BUG', 'SIDESWIPER'],
            'modes': ['CW'],
            'bands': ['All'],
            'mechanical_key': True,
            'effective_date': 'November 10, 2018 or later',
            'validity_rule': 'Both operators must have SKCC membership at time of contact',
            'special_rules': [
                'CRITICAL: All 300 contacts must be with DIFFERENT members',
                'Each member can only count ONCE across all key types',
                'Key type MUST be logged in contact (CRITICAL requirement)',
                'First contact with a member determines which key type they count for',
                'Remote stations do not need to be participating in the award',
                'All three key types must have 100+ unique members for base award',
                'Endorsements based on total unique members contacted'
            ],
            'endorsements_available': True,
            'endorsement_increments': [300, 600, 900, 1500, 3000]
        }

    def get_endorsements(self) -> List[Dict[str, Any]]:
        """
        Return list of Triple Key endorsement levels

        Returns:
            List of endorsement level dictionaries
        """
        return [
            {'level': 300, 'description': 'Triple Key', 'contacts_needed': '300 different members'},
            {'level': 600, 'description': 'Triple Key x2', 'contacts_needed': '600 different members'},
            {'level': 900, 'description': 'Triple Key x3', 'contacts_needed': '900 different members'},
            {'level': 1500, 'description': 'Triple Key x5', 'contacts_needed': '1500 different members'},
            {'level': 3000, 'description': 'Triple Key x10', 'contacts_needed': '3000 different members'},
        ]
