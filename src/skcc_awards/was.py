"""
SKCC WAS Award - Worked All States

The WAS Award recognizes contacts with SKCC members in all 50 US states.
An operator must show contacts in which they have exchanged names and SKCC
numbers with another SKCC member in each of the 50 states.

Rules:
- Contact SKCC members in all 50 US states
- CW mode exclusively
- Mechanical key policy: straight key, bug, or side swiper only (CRITICAL!)
- Both operators must hold SKCC membership at time of contact
- Contacts may be made at any time and on any band (including WARC)
- No effective date restriction
- Single-band endorsements available
- WAS-QRP endorsement available (≤5W power)
"""

import logging
from typing import Dict, List, Any, Set
from collections import defaultdict

from src.skcc_awards.base import SKCCAwardBase
from src.utils.skcc_number import extract_base_skcc_number
from src.skcc_awards.constants import US_STATES

logger = logging.getLogger(__name__)

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


class SKCCWASAward(SKCCAwardBase):
    """SKCC WAS Award - Worked All 50 US States"""

    def __init__(self, database):
        """
        Initialize SKCC WAS award

        Args:
            database: Database instance for contact queries
        """
        super().__init__(name="SKCC WAS", program_id="SKCC_WAS", database=database)

        # Total states required
        self.total_states = 50

    def validate(self, contact: Dict[str, Any]) -> bool:
        """
        Check if a contact qualifies for SKCC WAS award

        Requirements:
        - CW mode only
        - SKCC number present on both sides
        - Mechanical key required (STRAIGHT, BUG, or SIDESWIPER) - CRITICAL!
        - Remote station must be in one of the 50 US states
        - Both operators must be SKCC members

        Args:
            contact: Contact record dictionary

        Returns:
            True if contact qualifies for SKCC WAS award
        """
        # Check common SKCC rules (CW mode, mechanical key, SKCC number)
        if not self.validate_common_rules(contact):
            return False

        # Must have extractable state from contact
        state = self._get_state_from_contact(contact)
        if not state or state not in US_STATES:
            logger.debug(f"Cannot determine valid US state from contact: {contact.get('callsign')}")
            return False

        # Verify valid SKCC number
        skcc_num = contact.get('skcc_number', '').strip()
        if skcc_num:
            base_number = extract_base_skcc_number(skcc_num)
            if not base_number or not base_number.isdigit():
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
        Calculate SKCC WAS award progress

        Tracks which US states have been worked via contacts with SKCC members
        from each state.

        Args:
            contacts: List of contact records

        Returns:
            {
                'current': int,              # Number of states worked
                'required': int,             # 50 (all states)
                'achieved': bool,            # True if all 50 states worked
                'progress_pct': float,       # Percentage (0-100)
                'level': str,                # "WAS" or "Not Yet"
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
            level_name = "WAS"
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
        Return SKCC WAS award requirements

        Returns:
            Award requirements dictionary
        """
        return {
            'name': 'SKCC WAS Award',
            'description': 'Contact SKCC members in all 50 US states',
            'base_requirement': 'Contacts with members in all 50 states',
            'modes': ['CW'],
            'bands': ['All'],
            'effectiveness': 'Any date (no restriction)',
            'validity_rule': 'Both operators must hold SKCC membership at time of contact',
            'mechanical_key': True,
            'key_types': ['STRAIGHT', 'BUG', 'SIDESWIPER'],
            'states_required': 50,
            'special_rules': [
                'Contacts may be made at any time and on any band (including WARC)',
                'Single-band endorsements available (any individual band)',
                'WAS-QRP endorsement available (≤5W power for all contacts)',
                'Remote stations do not need to be participating in the award',
                'All 50 US states required (AL through WY)',
            ]
        }

    def get_endorsements(self) -> List[Dict[str, Any]]:
        """Return SKCC WAS endorsement levels"""
        return [
            {'level': 'WAS', 'states': 50, 'description': 'All 50 US states'},
            {'level': 'WAS-160M', 'states': 50, 'description': 'All 50 states on 160M'},
            {'level': 'WAS-80M', 'states': 50, 'description': 'All 50 states on 80M'},
            {'level': 'WAS-40M', 'states': 50, 'description': 'All 50 states on 40M'},
            {'level': 'WAS-20M', 'states': 50, 'description': 'All 50 states on 20M'},
            {'level': 'WAS-QRP', 'states': 50, 'description': 'All 50 states at QRP (≤5W)'},
        ]
