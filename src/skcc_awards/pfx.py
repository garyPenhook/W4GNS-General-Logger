"""
SKCC PFX Award - Accumulate 500,000+ points from callsign prefixes

The PFX award is earned by accumulating points based on SKCC member numbers
contacted, where each unique callsign prefix contributes points equal to the
highest SKCC number contacted with that prefix.

Rules:
- Accumulate 500,000+ points
- Points = sum of highest SKCC numbers per unique prefix
- CW mode exclusively
- Mechanical key policy: STRAIGHT, BUG, or SIDESWIPER required
- Both operators must have SKCC membership
- Contacts valid from January 1, 2013 onwards
- Club calls (K9SKC) and special-event calls don't qualify
- Prefix = letters and numbers up to and including last number on left side
- Prefixes/suffixes separated by "/" are ignored (use base callsign)
- Duplicate SKCC number/callsign pairs don't count
- When multiple stations share a prefix, only highest SKCC number counts
- Any band allowed

Examples:
- W4GNS → prefix W4
- K1ABC → prefix K1
- VE3XYZ → prefix VE3
- G0ABC → prefix G0

Endorsements:
- PFX: 500,000 points
- PFX x2-x10: 1M-5M (500K increments)
- PFX x15+: 7.5M, 10M (increment by 5 levels)
"""

import logging
import re
from typing import Dict, List, Any, Set, Tuple
from collections import defaultdict

from src.skcc_awards.base import SKCCAwardBase
from src.utils.skcc_number import extract_base_skcc_number
from src.skcc_awards.constants import (
    PFX_EFFECTIVE_DATE,
    SPECIAL_EVENT_CALLS
)

logger = logging.getLogger(__name__)

# PFX endorsement levels (points)
PFX_ENDORSEMENTS = [
    (500000, "PFX"),
    (1000000, "PFX x2"),
    (1500000, "PFX x3"),
    (2000000, "PFX x4"),
    (2500000, "PFX x5"),
    (3000000, "PFX x6"),
    (3500000, "PFX x7"),
    (4000000, "PFX x8"),
    (4500000, "PFX x9"),
    (5000000, "PFX x10"),
    (7500000, "PFX x15"),
    (10000000, "PFX x20"),
]


class PFXAward(SKCCAwardBase):
    """SKCC PFX Award - 500,000+ points from prefixes"""

    def __init__(self, database):
        """
        Initialize PFX award

        Args:
            database: Database instance for contact queries
        """
        super().__init__(name="PFX", program_id="SKCC_PFX", database=database)

    def _extract_prefix(self, callsign: str) -> str:
        """
        Extract prefix from callsign.

        Prefix = letters and numbers up to and including the last number on the left side.

        Examples:
            W4GNS → W4
            K1ABC → K1
            VE3XYZ → VE3
            G0ABC → G0
            AA1A → AA1
            2E0ABC → 2E0

        Args:
            callsign: Callsign string

        Returns:
            Prefix string
        """
        if not callsign:
            return ""

        # Remove slashes and take base callsign
        callsign = callsign.upper().strip()
        if '/' in callsign:
            # Take the longest part (usually the base call)
            parts = callsign.split('/')
            callsign = max(parts, key=len)

        # Find the position of the last digit on the left side
        # (before any letters that follow the digit)
        match = re.search(r'^([A-Z0-9]*\d)', callsign)
        if match:
            return match.group(1)

        return ""

    def validate(self, contact: Dict[str, Any]) -> bool:
        """
        Check if a contact qualifies for PFX award

        Requirements:
        - CW mode only
        - SKCC number present
        - Contact date on or after January 1, 2013
        - Mechanical key required (STRAIGHT, BUG, or SIDESWIPER)
        - Club calls and special-event calls excluded
        - Valid callsign prefix extractable
        - Both operators must have SKCC membership

        Args:
            contact: Contact record dictionary

        Returns:
            True if contact qualifies for PFX award
        """
        # Check common SKCC rules (CW mode, mechanical key, SKCC number)
        if not self.validate_common_rules(contact):
            return False

        # Get contact date
        qso_date = contact.get('date', '')
        if qso_date:
            qso_date = qso_date.replace('-', '')  # Normalize YYYY-MM-DD to YYYYMMDD

        # Check contact date (must be on/after January 1, 2013)
        if qso_date and qso_date < PFX_EFFECTIVE_DATE:
            return False

        # CRITICAL RULE: Club calls and special-event calls don't qualify
        callsign = contact.get('callsign', '').upper().strip()
        base_call = callsign.split('/')[0] if '/' in callsign else callsign

        if base_call in SPECIAL_EVENT_CALLS:
            logger.debug(f"Club/special-event call filtered for PFX: {callsign}")
            return False

        # Must have extractable prefix
        prefix = self._extract_prefix(callsign)
        if not prefix:
            logger.debug(f"Cannot extract prefix from callsign: {callsign}")
            return False

        # Verify valid SKCC number
        skcc_num = contact.get('skcc_number', '').strip()
        if skcc_num:
            base_number = extract_base_skcc_number(skcc_num)
            if not base_number or not base_number.isdigit():
                return False

        return True

    def calculate_progress(self, contacts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate PFX award progress

        Points = sum of highest SKCC numbers per unique prefix.

        Args:
            contacts: List of contact records

        Returns:
            {
                'current_points': int,         # Total points accumulated
                'required_points': int,        # Always 500,000 for base award
                'achieved': bool,              # True if 500K+ points
                'progress_pct': float,         # Percentage toward 500K
                'endorsement': str,            # Current endorsement level
                'unique_prefixes': int,        # Number of unique prefixes worked
                'prefix_details': dict,        # {prefix: {highest_skcc, callsign, contacts}}
                'next_level_points': int,      # Points for next endorsement
                'total_contacts': int          # Total qualifying contacts
            }
        """
        # Track highest SKCC number per prefix
        prefix_data: Dict[str, Dict] = defaultdict(lambda: {
            'highest_skcc': 0,
            'highest_callsign': '',
            'contacts': []
        })

        # Track seen callsign/SKCC pairs to prevent duplicates
        seen_pairs: Set[Tuple[str, str]] = set()

        total_contacts = 0

        for contact in contacts:
            if self.validate(contact):
                callsign = contact.get('callsign', '').upper().strip()
                skcc_number = contact.get('skcc_number', '').strip()
                base_number = extract_base_skcc_number(skcc_number)

                if not base_number or not base_number.isdigit():
                    continue

                # Check for duplicate callsign/SKCC pair
                pair = (callsign, base_number)
                if pair in seen_pairs:
                    logger.debug(f"Skipping duplicate callsign/SKCC pair: {pair}")
                    continue

                seen_pairs.add(pair)

                prefix = self._extract_prefix(callsign)
                if not prefix:
                    continue

                skcc_value = int(base_number)

                # Track all contacts for this prefix
                prefix_data[prefix]['contacts'].append({
                    'callsign': callsign,
                    'skcc_number': skcc_number,
                    'date': contact.get('date'),
                    'band': contact.get('band')
                })

                # Update highest SKCC number for this prefix
                if skcc_value > prefix_data[prefix]['highest_skcc']:
                    prefix_data[prefix]['highest_skcc'] = skcc_value
                    prefix_data[prefix]['highest_callsign'] = callsign

                total_contacts += 1

        # Calculate total points (sum of highest SKCC per prefix)
        total_points = sum(data['highest_skcc'] for data in prefix_data.values())
        required_points = 500000
        unique_prefixes = len(prefix_data)

        # Determine endorsement level
        current_level = "Not Yet"
        next_level = "PFX"
        next_points = 500000

        for threshold, level_name in PFX_ENDORSEMENTS:
            if total_points >= threshold:
                current_level = level_name
            elif total_points < threshold:
                next_level = level_name
                next_points = threshold
                break

        # Progress percentage
        if current_level == PFX_ENDORSEMENTS[-1][1]:
            progress_pct = 100.0
        else:
            progress_pct = min(100.0, (total_points / required_points) * 100)

        return {
            'current_points': total_points,
            'required_points': required_points,
            'achieved': total_points >= required_points,
            'progress_pct': progress_pct,
            'endorsement': current_level,
            'unique_prefixes': unique_prefixes,
            'prefix_details': dict(prefix_data),
            'next_level_points': next_points if current_level != PFX_ENDORSEMENTS[-1][1] else total_points,
            'total_contacts': total_contacts
        }

    def get_requirements(self) -> Dict[str, Any]:
        """
        Return PFX award requirements

        Returns:
            Award requirements dictionary
        """
        return {
            'name': 'SKCC PFX',
            'description': 'Accumulate 500,000+ points from callsign prefixes',
            'base_requirement': 500000,
            'base_units': 'points',
            'point_calculation': 'Sum of highest SKCC numbers per unique prefix',
            'modes': ['CW'],
            'bands': ['All'],
            'mechanical_key': True,
            'key_types': ['STRAIGHT', 'BUG', 'SIDESWIPER'],
            'effective_date': 'January 1, 2013 or later',
            'validity_rule': 'Both operators must have SKCC membership',
            'special_rules': [
                'Prefix = letters and numbers up to last digit on left side',
                'Only highest SKCC number per prefix contributes points',
                'Duplicate callsign/SKCC pairs do not count',
                'Club calls and special-event calls excluded',
                'Slashes in callsigns ignored (use base call)',
                'Each unique prefix can contribute only once'
            ],
            'endorsements_available': True,
            'endorsement_increments': [500000, 1000000, 1500000, 2000000, 2500000,
                                     3000000, 3500000, 4000000, 4500000, 5000000,
                                     7500000, 10000000]
        }

    def get_endorsements(self) -> List[Dict[str, Any]]:
        """
        Return list of PFX endorsement levels

        Returns:
            List of endorsement level dictionaries
        """
        return [
            {'level': 500000, 'description': 'PFX', 'points_needed': 500000},
            {'level': 1000000, 'description': 'PFX x2', 'points_needed': 1000000},
            {'level': 1500000, 'description': 'PFX x3', 'points_needed': 1500000},
            {'level': 2000000, 'description': 'PFX x4', 'points_needed': 2000000},
            {'level': 2500000, 'description': 'PFX x5', 'points_needed': 2500000},
            {'level': 3000000, 'description': 'PFX x6', 'points_needed': 3000000},
            {'level': 3500000, 'description': 'PFX x7', 'points_needed': 3500000},
            {'level': 4000000, 'description': 'PFX x8', 'points_needed': 4000000},
            {'level': 4500000, 'description': 'PFX x9', 'points_needed': 4500000},
            {'level': 5000000, 'description': 'PFX x10', 'points_needed': 5000000},
            {'level': 7500000, 'description': 'PFX x15', 'points_needed': 7500000},
            {'level': 10000000, 'description': 'PFX x20', 'points_needed': 10000000},
        ]
