"""
SKCC WAS-T Award - Worked All States (Tribune)

The WAS-T Award recognizes contacts with Tribune or Senator SKCC members in all 50 US states.
An operator must show contacts in which they have exchanged names and SKCC
numbers with Tribune or Senator members in each of the 50 states.

Rules:
- Contact Tribune (T) or Senator (S) members in all 50 US states
- CW mode exclusively
- Mechanical key policy: straight key, bug, or side swiper only (CRITICAL!)
- Both operators must hold SKCC membership at time of contact
- Contacts valid on or after February 1, 2016
- Contacts may be made on any band (including WARC)
- Single-band endorsements available
- WAS-T-QRP endorsement available (≤5W power)
- Mobile/portable Tribune/Senator operations count regardless of home state
"""

import logging
from typing import Dict, List, Any, Set
from collections import defaultdict

from src.skcc_awards.base import SKCCAwardBase
from src.utils.skcc_number import extract_base_skcc_number, get_member_type
from src.skcc_awards.constants import US_STATES
from src.skcc_roster import get_roster_manager

logger = logging.getLogger(__name__)

# WAS-T effective date
WAST_EFFECTIVE_DATE = "20160201"  # February 1, 2016

# QRP power threshold (watts)
QRP_THRESHOLD = 5.0

# US Call area to state mappings (primary states for each call area)
CALL_AREA_TO_STATES: Dict[str, List[str]] = {
    '0': ['CO', 'KS', 'NE', 'OK', 'WY'],
    '1': ['CT', 'ME', 'MA', 'NH', 'RI', 'VT'],
    '2': ['NJ', 'NY'],
    '3': ['DE', 'MD', 'PA', 'VA', 'WV'],
    '4': ['AL', 'GA', 'KY', 'NC', 'SC', 'TN'],
    '5': ['AR', 'LA', 'MS', 'OK', 'TX'],
    '6': ['CA', 'HI'],
    '7': ['AZ', 'ID', 'MT', 'NM', 'OR', 'UT', 'WA'],
    '8': ['IN', 'MI', 'OH', 'WV'],
    '9': ['IL', 'IA', 'MN', 'MO', 'WI'],
}


class SKCCWASTAward(SKCCAwardBase):
    """SKCC WAS-T Award - Worked All 50 US States (Tribune/Senator)"""

    def __init__(self, database):
        """
        Initialize SKCC WAS-T award

        Args:
            database: Database instance for contact queries
        """
        super().__init__(name="SKCC WAS-T", program_id="SKCC_WAS_T", database=database)
        self.roster_manager = get_roster_manager()
        self.user_join_date = self._get_user_join_date()

        # Total states required
        self.total_states = 50

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
        Check if a contact qualifies for SKCC WAS-T award

        Requirements:
        - CW mode only
        - SKCC number present on both sides
        - Mechanical key required (STRAIGHT, BUG, or SIDESWIPER) - CRITICAL!
        - Remote station must be in one of the 50 US states
        - Remote station must be Tribune (T) or Senator (S) member
        - Contact date on or after February 1, 2016
        - Both operators must be SKCC members

        Args:
            contact: Contact record dictionary

        Returns:
            True if contact qualifies for SKCC WAS-T award
        """
        # Check common SKCC rules (CW mode, mechanical key, SKCC number)
        if not self.validate_common_rules(contact):
            return False

        # Get contact date
        qso_date = contact.get('qso_date', contact.get('date', ''))
        if qso_date:
            qso_date = qso_date.replace('-', '')  # Normalize YYYY-MM-DD to YYYYMMDD

        # CRITICAL RULE: Contacts valid on or after February 1, 2016
        if qso_date and qso_date < WAST_EFFECTIVE_DATE:
            logger.debug(
                f"Contact not valid: QSO date {qso_date} before "
                f"WAS-T effective date {WAST_EFFECTIVE_DATE}"
            )
            return False

        # Get callsign (remove portable/suffix indicators)
        callsign = contact.get('callsign', '').upper().strip()
        base_call = callsign.split('/')[0] if '/' in callsign else callsign

        # Verify valid SKCC number
        skcc_num = contact.get('skcc_number', '').strip()
        if not skcc_num:
            return False

        base_number = extract_base_skcc_number(skcc_num)
        if not base_number or not base_number.isdigit():
            return False

        # CRITICAL RULE: Remote station must be Tribune (T) or Senator (S)
        member_type = get_member_type(skcc_num)
        if member_type not in ['T', 'S']:
            logger.debug(
                f"Contact {callsign} not valid: SKCC number {skcc_num} is not "
                f"Tribune or Senator (member type: {member_type})"
            )
            return False

        # Must have extractable state from contact
        state = self._get_state_from_contact(contact)
        if not state or state not in US_STATES:
            logger.debug(f"Cannot determine valid US state from contact: {callsign}")
            return False

        # CRITICAL RULE: "Both operators must hold SKCC membership at time of contact"
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

    def _get_state_from_contact(self, contact: Dict[str, Any]) -> str:
        """
        Get US state from contact

        Tries multiple methods to determine state:
        1. Direct state field (if available)
        2. Call area from callsign prefix
        3. State abbreviation in comments

        Args:
            contact: Contact record dictionary

        Returns:
            State abbreviation (e.g., 'CA', 'NY') or empty string if unknown
        """
        # Method 1: Direct state field
        if 'state' in contact and contact['state']:
            state = contact['state'].upper().strip()
            if len(state) == 2 and state in US_STATES:
                return state

        # Method 2: Call area from callsign prefix
        callsign = contact.get('callsign', '').upper().strip()
        if callsign:
            # Extract call area digit (K0-K9, W0-W9, etc.)
            # Format is usually K[digit] or W[digit] or similar
            if len(callsign) >= 2:
                if callsign[0] in 'KWN':
                    if callsign[1].isdigit():
                        call_area = callsign[1]
                        # Get primary state for this call area
                        if call_area in CALL_AREA_TO_STATES:
                            # Return first state in call area
                            return CALL_AREA_TO_STATES[call_area][0]

        # Method 3: State abbreviation in comments (fallback)
        comments = contact.get('comments', '').upper()
        for state_code in US_STATES:
            if state_code in comments:
                return state_code

        return ""

    def calculate_progress(self, contacts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate SKCC WAS-T award progress

        Tracks which US states have been worked via contacts with Tribune/Senator
        members from each state.

        Args:
            contacts: List of contact records

        Returns:
            {
                'current': int,              # Number of states worked
                'required': int,             # 50 (all states)
                'achieved': bool,            # True if all 50 states worked
                'progress_pct': float,       # Percentage (0-100)
                'level': str,                # "WAS-T" or "Not Yet"
                'states_worked': list,       # List of worked state codes
                'states_needed': list,       # List of needed state codes
                'state_details': dict,       # Per-state contact counts
                'band_details': dict,        # Contacts per band per state
                'qrp_states': set,           # States worked at QRP
            }
        """
        # Track states worked and contact details
        states_worked: Set[str] = set()
        state_details: Dict[str, int] = {code: 0 for code in US_STATES}
        band_details: Dict[str, Dict[str, int]] = {
            code: {} for code in US_STATES
        }
        qrp_states: Set[str] = set()

        for contact in contacts:
            if self.validate(contact):
                state = self._get_state_from_contact(contact)

                if state in US_STATES:
                    states_worked.add(state)
                    state_details[state] += 1

                    # Track by band
                    band = contact.get('band', 'Unknown').upper()
                    if band not in band_details[state]:
                        band_details[state][band] = 0
                    band_details[state][band] += 1

                    # Track QRP states
                    power = contact.get('power_watts')
                    if power is not None:
                        try:
                            power_val = float(power)
                            if power_val <= QRP_THRESHOLD:
                                qrp_states.add(state)
                        except (ValueError, TypeError):
                            pass

        # Determine if award is achieved (all 50 states worked)
        achieved = len(states_worked) >= 50
        current_count = len(states_worked)

        # Calculate states needed
        states_needed = sorted(list(US_STATES - states_worked))

        # Calculate level and required
        if achieved:
            level_name = "WAS-T"
        else:
            level_name = "Not Yet"

        return {
            'current': current_count,
            'required': 50,
            'achieved': achieved,
            'progress_pct': min(100.0, (current_count / 50) * 100),
            'level': level_name,
            'states_worked': sorted(list(states_worked)),
            'states_needed': states_needed,
            'state_details': state_details,
            'band_details': band_details,
            'qrp_states': sorted(list(qrp_states)),
        }

    def get_requirements(self) -> Dict[str, Any]:
        """
        Return SKCC WAS-T award requirements

        Returns:
            Award requirements dictionary
        """
        return {
            'name': 'SKCC WAS-T Award',
            'description': 'Contact Tribune or Senator members in all 50 US states',
            'base_requirement': 'Contacts with Tribune/Senator members in all 50 states',
            'modes': ['CW'],
            'bands': ['All'],
            'effective_date': 'February 1, 2016 or later',
            'validity_rule': 'Both operators must hold SKCC membership at time of contact',
            'mechanical_key': True,
            'key_types': ['STRAIGHT', 'BUG', 'SIDESWIPER'],
            'states_required': 50,
            'member_types_required': ['Tribune (T)', 'Senator (S)'],
            'special_rules': [
                'CRITICAL: Remote station must be Tribune or Senator member',
                'Contacts may be made on any band (including WARC)',
                'Single-band endorsements available (any individual band)',
                'WAS-T-QRP endorsement available (≤5W power for all contacts)',
                'Mobile/portable Tribune/Senator operations count regardless of home state',
                'Non-Tribune members may apply for this award',
                'All 50 US states required (AL through WY)',
            ]
        }

    def get_endorsements(self) -> List[Dict[str, Any]]:
        """Return SKCC WAS-T endorsement levels"""
        return [
            {'level': 'WAS-T', 'states': 50, 'description': 'All 50 US states (Tribune/Senator)'},
            {'level': 'WAS-T-160M', 'states': 50, 'description': 'All 50 states on 160M (Tribune/Senator)'},
            {'level': 'WAS-T-80M', 'states': 50, 'description': 'All 50 states on 80M (Tribune/Senator)'},
            {'level': 'WAS-T-40M', 'states': 50, 'description': 'All 50 states on 40M (Tribune/Senator)'},
            {'level': 'WAS-T-20M', 'states': 50, 'description': 'All 50 states on 20M (Tribune/Senator)'},
            {'level': 'WAS-T-QRP', 'states': 50, 'description': 'All 50 states at QRP (≤5W, Tribune/Senator)'},
        ]
