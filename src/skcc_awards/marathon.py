"""
SKCC Marathon Award - 100 QSOs of 60+ Minutes Each

The Marathon award is earned by completing 100 QSOs, each 60 minutes or longer,
with different SKCC members.

Rules:
- Complete 100 QSOs, each 60 minutes or longer
- Each QSO must be with a different SKCC member
- CW mode exclusively
- Mechanical key policy: STRAIGHT, BUG, or SIDESWIPER required
- Both operators must have SKCC membership
- Duration must be logged in minutes (CRITICAL!)
- Must use own call signs and personal SKCC numbers (no club calls)
- QSOs must be from home QTH (with exceptions for portable/relocation)
- One band change permitted per QSO (max 10 minute break)
- Any band (including WARC)
- Contacts valid on or after January 1, 2008
"""

import logging
from typing import Dict, List, Any, Set, Tuple

from src.skcc_awards.base import SKCCAwardBase
from src.utils.skcc_number import extract_base_skcc_number
from src.skcc_awards.constants import SPECIAL_EVENT_CALLS
from src.skcc_roster import get_roster_manager

logger = logging.getLogger(__name__)

# Marathon award effective date
MARATHON_EFFECTIVE_DATE = "20080101"  # January 1, 2008

# Minimum duration per QSO (minutes)
MARATHON_MIN_DURATION = 60


class MarathonAward(SKCCAwardBase):
    """SKCC Marathon Award - 100 QSOs of 60+ minutes each with different members"""

    def __init__(self, database):
        """
        Initialize Marathon award

        Args:
            database: Database instance for contact queries
        """
        super().__init__(name="Marathon", program_id="SKCC_MARATHON", database=database)
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
        Check if a contact qualifies for Marathon award

        Requirements:
        - CW mode only
        - SKCC number present
        - Contact date on or after January 1, 2008
        - Mechanical key required (STRAIGHT, BUG, or SIDESWIPER)
        - Duration must be logged (CRITICAL!)
        - Minimum 60 minutes duration
        - Both operators must have SKCC membership
        - No club calls or special event calls

        Args:
            contact: Contact record dictionary

        Returns:
            True if contact qualifies for Marathon award
        """
        # Check common SKCC rules (CW mode, mechanical key, SKCC number)
        if not self.validate_common_rules(contact):
            return False

        # Get contact date
        qso_date = contact.get('qso_date', contact.get('date', ''))
        if qso_date:
            qso_date = qso_date.replace('-', '')  # Normalize YYYY-MM-DD to YYYYMMDD

        # Check contact date (must be on/after January 1, 2008)
        if qso_date and qso_date < MARATHON_EFFECTIVE_DATE:
            return False

        # Get callsign (remove portable/suffix indicators)
        callsign = contact.get('callsign', '').upper().strip()
        base_call = callsign.split('/')[0] if '/' in callsign else callsign

        # CRITICAL RULE: No club calls or special event calls
        if base_call in SPECIAL_EVENT_CALLS:
            logger.debug(f"Club/special-event call filtered for Marathon: {callsign}")
            return False

        # CRITICAL RULE: Duration must be logged
        duration = contact.get('duration_minutes')
        if duration is None:
            logger.debug("Missing duration for Marathon award")
            return False

        # Convert to int if string
        try:
            duration = int(duration)
        except (ValueError, TypeError):
            logger.debug(f"Invalid duration format: {duration}")
            return False

        # CRITICAL RULE: Minimum 60 minutes duration
        if duration < MARATHON_MIN_DURATION:
            logger.debug(
                f"Duration {duration} below Marathon minimum {MARATHON_MIN_DURATION}"
            )
            return False

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
        Calculate Marathon award progress

        Tracks qualifying 60+ minute QSOs with different SKCC members.
        CRITICAL: Each member can only count ONCE for Marathon.

        Args:
            contacts: List of contact records

        Returns:
            {
                'current': int,              # Number of qualifying marathons
                'required': int,             # Always 100 for base award
                'achieved': bool,            # True if 100+ marathons
                'progress_pct': float,       # Percentage toward 100
                'total_minutes': int,        # Total minutes across all marathons
                'qualifying_contacts': int,  # Number of qualifying QSOs
                'unique_members': int,       # Number of unique members
                'average_duration': float,   # Average minutes per marathon
                'contact_details': list,     # List of qualifying contacts
                'duplicate_members': int,    # Contacts rejected (member already counted)
            }
        """
        # Filter for qualifying contacts
        qualifying_contacts = [c for c in contacts if self.validate(c)]

        # Sort by date to ensure earliest contact wins
        qualifying_contacts.sort(
            key=lambda x: (x.get('qso_date', x.get('date', '')), x.get('time_on', ''))
        )

        # Track unique members (each member can only count once)
        members_counted: Set[str] = set()
        valid_marathons = []
        duplicate_members = 0
        total_minutes = 0

        for contact in qualifying_contacts:
            skcc_number = contact.get('skcc_number', '').strip()
            base_number = extract_base_skcc_number(skcc_number)

            if base_number and base_number.isdigit():
                # CRITICAL: Each member can only count ONCE
                if base_number not in members_counted:
                    duration = int(contact.get('duration_minutes', 0))
                    total_minutes += duration
                    members_counted.add(base_number)

                    valid_marathons.append({
                        'callsign': contact.get('callsign'),
                        'skcc_number': skcc_number,
                        'date': contact.get('qso_date', contact.get('date')),
                        'duration_minutes': duration,
                        'band': contact.get('band')
                    })
                else:
                    duplicate_members += 1
                    logger.debug(
                        f"Marathon: Member {base_number} already counted, "
                        f"ignoring duplicate contact"
                    )

        required_marathons = 100
        num_marathons = len(valid_marathons)
        unique_members = len(members_counted)

        # Calculate average duration
        average_duration = total_minutes / num_marathons if num_marathons > 0 else 0

        return {
            'current': num_marathons,
            'required': required_marathons,
            'achieved': num_marathons >= required_marathons,
            'progress_pct': min(100.0, (num_marathons / required_marathons) * 100),
            'total_minutes': total_minutes,
            'qualifying_contacts': num_marathons,
            'unique_members': unique_members,
            'average_duration': round(average_duration, 1),
            'contact_details': valid_marathons,
            'duplicate_members': duplicate_members
        }

    def get_requirements(self) -> Dict[str, Any]:
        """
        Return Marathon award requirements

        Returns:
            Award requirements dictionary
        """
        return {
            'name': 'SKCC Marathon',
            'description': 'Complete 100 QSOs, each 60 minutes or longer, with different SKCC members',
            'base_requirement': 100,
            'base_units': 'QSOs of 60+ minutes each',
            'minimum_per_qso': '60 minutes',
            'modes': ['CW'],
            'bands': ['All (including WARC)'],
            'mechanical_key': True,
            'key_types': ['STRAIGHT', 'BUG', 'SIDESWIPER'],
            'effective_date': 'January 1, 2008 or later',
            'validity_rule': 'Both operators must have SKCC membership at time of contact',
            'special_rules': [
                'CRITICAL: Duration MUST be logged in minutes (60+ minutes required)',
                'CRITICAL: Each QSO must be with a DIFFERENT SKCC member',
                'Must use own call signs and personal SKCC numbers (no club calls)',
                'QSOs must be from home QTH (exceptions for permanent relocation/portable)',
                'One band change permitted per QSO (max 10 minute break)',
                'Minor frequency shifts within bands allowed',
                'Both parties must submit QSO details or confirm via email'
            ],
            'endorsements_available': False
        }

    def get_endorsements(self) -> List[Dict[str, Any]]:
        """
        Return list of Marathon endorsement levels

        Returns:
            List of endorsement level dictionaries (empty - no endorsements)
        """
        return [
            {'level': 100, 'description': 'Marathon', 'marathons_needed': 100}
        ]
