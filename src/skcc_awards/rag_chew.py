"""
SKCC Rag Chew Award - Accumulate 300+ minutes of extended CW conversations

The Rag Chew award is earned by accumulating a total of 300 minutes (5 hours)
of extended CW conversations with SKCC members.

Rules:
- Accumulate 300+ total minutes of conversations
- Minimum 30 minutes per QSO (40 minutes for multi-station operations)
- CW mode exclusively
- Mechanical key policy: STRAIGHT, BUG, or SIDESWIPER required
- Both operators must have SKCC membership
- Duration must be logged in minutes (CRITICAL!)
- Back-to-back contacts with same member prohibited
- Multiple contacts with same member allowed over time
- Any band (including WARC)
- Contacts valid on or after July 1, 2013
"""

import logging
from typing import Dict, List, Any, Set, Tuple
from datetime import datetime, timedelta

from src.skcc_awards.base import SKCCAwardBase
from src.utils.skcc_number import extract_base_skcc_number
from src.skcc_awards.constants import (
    RAG_CHEW_ENDORSEMENTS,
    RAG_CHEW_EFFECTIVE_DATE,
    get_endorsement_level,
    get_next_endorsement_threshold
)
from src.skcc_roster import get_roster_manager

logger = logging.getLogger(__name__)


class RagChewAward(SKCCAwardBase):
    """SKCC Rag Chew Award - Accumulate 300+ minutes of conversations"""

    # Minimum duration thresholds
    MIN_DURATION_SINGLE = 30  # 30 minutes minimum for single-station QSOs
    MIN_DURATION_MULTI = 40   # 40 minutes minimum for multi-station QSOs

    def __init__(self, database):
        """
        Initialize Rag Chew award

        Args:
            database: Database instance for contact queries
        """
        super().__init__(name="Rag Chew", program_id="SKCC_RAG_CHEW", database=database)
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

    def should_deduplicate_for_export(self) -> bool:
        """Rag Chew allows multiple QSOs with the same member over time."""
        return False

    def validate(self, contact: Dict[str, Any]) -> bool:
        """
        Check if a contact qualifies for Rag Chew award

        Requirements:
        - CW mode only
        - SKCC number present
        - Contact date on or after July 1, 2013
        - Mechanical key required (STRAIGHT, BUG, or SIDESWIPER)
        - Duration must be logged (CRITICAL!)
        - Minimum 30 minutes duration (40 for multi-station)
        - Both operators must have SKCC membership

        Args:
            contact: Contact record dictionary

        Returns:
            True if contact qualifies for Rag Chew award
        """
        # Check common SKCC rules (CW mode, mechanical key, SKCC number)
        if not self.validate_common_rules(contact):
            return False

        # Get contact date
        qso_date = contact.get('qso_date', contact.get('date', ''))
        if qso_date:
            qso_date = qso_date.replace('-', '')  # Normalize YYYY-MM-DD to YYYYMMDD

        # Check contact date (must be on/after July 1, 2013)
        if qso_date and qso_date < RAG_CHEW_EFFECTIVE_DATE:
            return False

        # CRITICAL RULE: Duration must be logged
        duration = contact.get('duration_minutes')
        if duration is None:
            logger.debug("Missing duration for Rag Chew award")
            return False

        # Convert to int if string
        try:
            duration = int(duration)
        except (ValueError, TypeError):
            logger.debug(f"Invalid duration format: {duration}")
            return False

        # Check minimum duration (30 minutes for single-station, 40 for multi)
        # For now, we'll use 30 as the standard minimum
        # TODO: Add multi-station detection logic if needed
        if duration < self.MIN_DURATION_SINGLE:
            logger.debug(f"Duration {duration} below minimum {self.MIN_DURATION_SINGLE}")
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

    def _check_back_to_back(self, contacts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter out back-to-back contacts with the same member.

        Back-to-back is defined as contacts with the same SKCC number on the same day.

        Args:
            contacts: List of validated contact records

        Returns:
            Filtered list with back-to-back contacts removed
        """
        # Sort contacts by date and time
        sorted_contacts = sorted(
            contacts,
            key=lambda x: (x.get('date', ''), x.get('time_on', ''))
        )

        filtered = []
        last_contact_by_member: Dict[str, str] = {}  # {skcc_number: last_date}

        for contact in sorted_contacts:
            skcc_number = contact.get('skcc_number', '').strip()
            base_number = extract_base_skcc_number(skcc_number)
            qso_date = contact.get('date', '').replace('-', '')

            if not base_number or not qso_date:
                continue

            # Check if this is a back-to-back contact (same member, same day)
            last_date = last_contact_by_member.get(base_number)
            if last_date == qso_date:
                logger.debug(
                    f"Skipping back-to-back Rag Chew contact: {base_number} on {qso_date}"
                )
                continue

            # This contact is valid
            filtered.append(contact)
            last_contact_by_member[base_number] = qso_date

        return filtered

    def calculate_progress(self, contacts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate Rag Chew award progress

        Accumulates total minutes of qualifying conversations.

        Args:
            contacts: List of contact records

        Returns:
            {
                'current': int,              # Total minutes accumulated
                'required': int,             # Always 300 for base award
                'achieved': bool,            # True if 300+ minutes
                'progress_pct': float,       # Percentage toward 300 minutes
                'endorsement': str,          # Current endorsement level
                'total_minutes': int,        # Same as 'current'
                'qualifying_contacts': int,  # Number of qualifying QSOs
                'average_duration': float,   # Average minutes per QSO
                'contact_details': list,     # List of qualifying contacts
                'next_level_minutes': int    # Minutes for next endorsement
            }
        """
        # Filter for qualifying contacts
        qualifying_contacts = [c for c in contacts if self.validate(c)]

        # Remove back-to-back contacts with same member
        qualifying_contacts = self._check_back_to_back(qualifying_contacts)

        # Accumulate total minutes
        total_minutes = 0
        contact_details = []

        for contact in qualifying_contacts:
            duration = int(contact.get('duration_minutes', 0))
            total_minutes += duration

            contact_details.append({
                'callsign': contact.get('callsign'),
                'skcc_number': contact.get('skcc_number'),
                'date': contact.get('date'),
                'duration_minutes': duration,
                'band': contact.get('band')
            })

        required_minutes = 300
        num_contacts = len(qualifying_contacts)

        # Calculate average duration
        average_duration = total_minutes / num_contacts if num_contacts > 0 else 0

        # Determine endorsement level
        endorsement_level = get_endorsement_level(total_minutes, RAG_CHEW_ENDORSEMENTS)
        next_level = get_next_endorsement_threshold(total_minutes, RAG_CHEW_ENDORSEMENTS)

        return {
            'current': total_minutes,
            'required': required_minutes,
            'achieved': total_minutes >= required_minutes,
            'progress_pct': min(100.0, (total_minutes / required_minutes) * 100),
            'endorsement': endorsement_level,
            'total_minutes': total_minutes,
            'qualifying_contacts': num_contacts,
            'average_duration': round(average_duration, 1),
            'contact_details': contact_details,
            'next_level_minutes': next_level
        }

    def get_requirements(self) -> Dict[str, Any]:
        """
        Return Rag Chew award requirements

        Returns:
            Award requirements dictionary
        """
        return {
            'name': 'SKCC Rag Chew',
            'description': 'Accumulate 300 minutes of extended CW conversations',
            'base_requirement': 300,
            'base_units': 'minutes of conversation',
            'minimum_per_qso': '30 minutes (40 for multi-station)',
            'modes': ['CW'],
            'bands': ['All (including WARC)'],
            'mechanical_key': True,
            'key_types': ['STRAIGHT', 'BUG', 'SIDESWIPER'],
            'effective_date': 'July 1, 2013 or later',
            'validity_rule': 'Both operators must have SKCC membership at time of contact',
            'special_rules': [
                'Duration MUST be logged in minutes (CRITICAL requirement)',
                'Minimum 30 minutes per QSO (40 for multi-station operations)',
                'Back-to-back contacts with same member prohibited (same day)',
                'Multiple contacts with same member allowed over different days',
                'Total minutes accumulated across all qualifying contacts'
            ],
            'endorsements_available': True,
            'endorsement_increments': [300, 600, 900, 1200, 1500, 1800, 2100, 2400, 2700, 3000, 4500, 6000, 7500, 9000]
        }

    def get_endorsements(self) -> List[Dict[str, Any]]:
        """
        Return list of Rag Chew endorsement levels

        Returns:
            List of endorsement level dictionaries
        """
        return [
            {'level': 300, 'description': 'Rag Chew', 'minutes_needed': 300},
            {'level': 600, 'description': 'Rag Chew x2', 'minutes_needed': 600},
            {'level': 900, 'description': 'Rag Chew x3', 'minutes_needed': 900},
            {'level': 1200, 'description': 'Rag Chew x4', 'minutes_needed': 1200},
            {'level': 1500, 'description': 'Rag Chew x5', 'minutes_needed': 1500},
            {'level': 1800, 'description': 'Rag Chew x6', 'minutes_needed': 1800},
            {'level': 2100, 'description': 'Rag Chew x7', 'minutes_needed': 2100},
            {'level': 2400, 'description': 'Rag Chew x8', 'minutes_needed': 2400},
            {'level': 2700, 'description': 'Rag Chew x9', 'minutes_needed': 2700},
            {'level': 3000, 'description': 'Rag Chew x10', 'minutes_needed': 3000},
            {'level': 4500, 'description': 'Rag Chew x15', 'minutes_needed': 4500},
            {'level': 6000, 'description': 'Rag Chew x20', 'minutes_needed': 6000},
            {'level': 7500, 'description': 'Rag Chew x25', 'minutes_needed': 7500},
            {'level': 9000, 'description': 'Rag Chew x30', 'minutes_needed': 9000},
        ]
