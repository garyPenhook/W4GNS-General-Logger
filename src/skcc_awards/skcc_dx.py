"""
SKCC DX Awards - DXQ (QSO-based) and DXC (Country-based)

Two variants of SKCC DX awards:

1. DXQ - QSO-based Award:
   Contact SKCC members in different DXCC entities (each member counts separately)

2. DXC - Country-based Award:
   Contact SKCC members in different DXCC entities (each country counts only once)

Common Rules:
- CW mode exclusively
- Mechanical key policy: STRAIGHT, BUG, or SIDESWIPER required
- Both operators must have SKCC membership
- Must be DX (outside own DXCC entity)
- Maritime-mobile within 12-nautical-mile limit counts; beyond doesn't count
- Distance must be logged for /MM stations
- Any band allowed

DXQ effective date: June 14, 2009
DXC effective date: December 19, 2009

Levels (both awards):
- Level 10: 10 DXCC entities
- Level 25: 25 DXCC entities
- Level 50+: 50+ DXCC entities
"""

import logging
from typing import Dict, List, Any, Set
from collections import defaultdict

from src.skcc_awards.base import SKCCAwardBase
from src.utils.skcc_number import extract_base_skcc_number
from src.skcc_awards.constants import (
    DXQ_EFFECTIVE_DATE,
    DXC_EFFECTIVE_DATE
)

logger = logging.getLogger(__name__)

# Maritime mobile distance threshold (nautical miles)
MARITIME_MOBILE_LIMIT = 12.0

# Achievement levels
DX_LEVELS = [
    (10, "DX-10"),
    (25, "DX-25"),
    (50, "DX-50"),
    (75, "DX-75"),
    (100, "DX-100"),
]


class SKCCDXQAward(SKCCAwardBase):
    """SKCC DXQ Award - QSO-based DX contacts (each member per country counts)"""

    def __init__(self, database, operator_dxcc_entity: int = 291):
        """
        Initialize DXQ award

        Args:
            database: Database instance for contact queries
            operator_dxcc_entity: Operator's DXCC entity (default 291 = USA)
        """
        super().__init__(name="SKCC DXQ", program_id="SKCC_DXQ", database=database)
        self.operator_dxcc_entity = operator_dxcc_entity

    def validate(self, contact: Dict[str, Any]) -> bool:
        """
        Check if a contact qualifies for DXQ award

        Requirements:
        - CW mode only
        - SKCC number present
        - Contact date on or after June 14, 2009
        - Mechanical key required (STRAIGHT, BUG, or SIDESWIPER)
        - Must be DX (different DXCC entity)
        - Maritime-mobile within 12nm counts; beyond doesn't
        - Both operators must have SKCC membership

        Args:
            contact: Contact record dictionary

        Returns:
            True if contact qualifies for DXQ award
        """
        # Check common SKCC rules (CW mode, mechanical key, SKCC number)
        if not self.validate_common_rules(contact):
            return False

        # Get contact date
        qso_date = contact.get('date', '')
        if qso_date:
            qso_date = qso_date.replace('-', '')  # Normalize YYYY-MM-DD to YYYYMMDD

        # Check contact date (must be on/after June 14, 2009)
        if qso_date and qso_date < DXQ_EFFECTIVE_DATE:
            return False

        # Check for DXCC entity
        dxcc_entity = contact.get('dxcc_entity')
        if not dxcc_entity:
            logger.debug("Missing DXCC entity for DXQ")
            return False

        # Must be DX (different from operator's entity)
        if dxcc_entity == self.operator_dxcc_entity:
            return False

        # Check maritime-mobile distance if applicable
        callsign = contact.get('callsign', '').upper()
        if '/MM' in callsign or callsign.endswith('MM'):
            distance_nm = contact.get('distance_nm')
            if distance_nm is None:
                logger.debug("Missing distance for maritime-mobile station")
                return False

            try:
                distance = float(distance_nm)
                if distance > MARITIME_MOBILE_LIMIT:
                    logger.debug(f"Maritime-mobile beyond 12nm limit: {distance}nm")
                    return False
            except (ValueError, TypeError):
                logger.debug(f"Invalid distance format: {distance_nm}")
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
        Calculate DXQ award progress

        For DXQ, each member contact in each DXCC entity counts separately.

        Args:
            contacts: List of contact records

        Returns:
            {
                'current': int,              # Number of DX QSOs
                'entities_worked': int,      # Number of unique DXCC entities
                'achieved_level': str,       # Current level (DX-10, DX-25, etc.)
                'next_level': str,           # Next level to achieve
                'progress_pct': float,       # Progress toward next level
                'entity_details': dict,      # Contacts per entity
                'total_qsos': int            # Total qualifying QSOs
            }
        """
        # Track QSOs by DXCC entity and member
        entities_worked = set()
        entity_details: Dict[int, List[Dict]] = defaultdict(list)
        total_qsos = 0

        for contact in contacts:
            if self.validate(contact):
                dxcc_entity = contact.get('dxcc_entity')
                skcc_number = contact.get('skcc_number', '').strip()

                if dxcc_entity:
                    entities_worked.add(dxcc_entity)
                    entity_details[dxcc_entity].append({
                        'callsign': contact.get('callsign'),
                        'skcc_number': skcc_number,
                        'date': contact.get('date'),
                        'band': contact.get('band')
                    })
                    total_qsos += 1

        entities_count = len(entities_worked)

        # Determine current level
        current_level = "Not Yet"
        next_level = "DX-10"
        next_threshold = 10

        for threshold, level_name in DX_LEVELS:
            if entities_count >= threshold:
                current_level = level_name
            elif entities_count < threshold:
                next_level = level_name
                next_threshold = threshold
                break

        # Calculate progress toward next level
        if current_level == DX_LEVELS[-1][1]:
            progress_pct = 100.0
        else:
            progress_pct = min(100.0, (entities_count / next_threshold) * 100)

        return {
            'current': total_qsos,
            'entities_worked': entities_count,
            'achieved_level': current_level,
            'next_level': next_level if current_level != DX_LEVELS[-1][1] else current_level,
            'progress_pct': progress_pct,
            'entity_details': {entity: len(contacts) for entity, contacts in entity_details.items()},
            'total_qsos': total_qsos
        }

    def get_requirements(self) -> Dict[str, Any]:
        """
        Return DXQ award requirements

        Returns:
            Award requirements dictionary
        """
        return {
            'name': 'SKCC DXQ',
            'description': 'QSO-based DX award - each member per country counts separately',
            'base_requirement': '10+ DXCC entities',
            'modes': ['CW'],
            'bands': ['All'],
            'mechanical_key': True,
            'key_types': ['STRAIGHT', 'BUG', 'SIDESWIPER'],
            'effective_date': 'June 14, 2009 or later',
            'validity_rule': 'Must contact SKCC members outside own DXCC entity',
            'special_rules': [
                'Each member contact in each DXCC entity counts separately',
                'Maritime-mobile within 12nm counts; beyond does not',
                'Distance must be logged for /MM stations',
                'Multiple contacts with same member in different entities count'
            ],
            'levels_available': True,
            'level_thresholds': [10, 25, 50, 75, 100]
        }

    def get_endorsements(self) -> List[Dict[str, Any]]:
        """Return DXQ achievement levels"""
        return [
            {'level': 10, 'description': 'DXQ-10', 'entities_needed': 10},
            {'level': 25, 'description': 'DXQ-25', 'entities_needed': 25},
            {'level': 50, 'description': 'DXQ-50', 'entities_needed': 50},
            {'level': 75, 'description': 'DXQ-75', 'entities_needed': 75},
            {'level': 100, 'description': 'DXQ-100', 'entities_needed': 100},
        ]


class SKCCDXCAward(SKCCAwardBase):
    """SKCC DXC Award - Country-based DX contacts (each country counts once)"""

    def __init__(self, database, operator_dxcc_entity: int = 291):
        """
        Initialize DXC award

        Args:
            database: Database instance for contact queries
            operator_dxcc_entity: Operator's DXCC entity (default 291 = USA)
        """
        super().__init__(name="SKCC DXC", program_id="SKCC_DXC", database=database)
        self.operator_dxcc_entity = operator_dxcc_entity

    def validate(self, contact: Dict[str, Any]) -> bool:
        """
        Check if a contact qualifies for DXC award

        Requirements:
        - CW mode only
        - SKCC number present
        - Contact date on or after December 19, 2009
        - Mechanical key required (STRAIGHT, BUG, or SIDESWIPER)
        - Must be DX (different DXCC entity)
        - Maritime-mobile within 12nm counts; beyond doesn't
        - Both operators must have SKCC membership

        Args:
            contact: Contact record dictionary

        Returns:
            True if contact qualifies for DXC award
        """
        # Check common SKCC rules (CW mode, mechanical key, SKCC number)
        if not self.validate_common_rules(contact):
            return False

        # Get contact date
        qso_date = contact.get('date', '')
        if qso_date:
            qso_date = qso_date.replace('-', '')  # Normalize YYYY-MM-DD to YYYYMMDD

        # Check contact date (must be on/after December 19, 2009)
        if qso_date and qso_date < DXC_EFFECTIVE_DATE:
            return False

        # Check for DXCC entity
        dxcc_entity = contact.get('dxcc_entity')
        if not dxcc_entity:
            logger.debug("Missing DXCC entity for DXC")
            return False

        # Must be DX (different from operator's entity)
        if dxcc_entity == self.operator_dxcc_entity:
            return False

        # Check maritime-mobile distance if applicable
        callsign = contact.get('callsign', '').upper()
        if '/MM' in callsign or callsign.endswith('MM'):
            distance_nm = contact.get('distance_nm')
            if distance_nm is None:
                logger.debug("Missing distance for maritime-mobile station")
                return False

            try:
                distance = float(distance_nm)
                if distance > MARITIME_MOBILE_LIMIT:
                    logger.debug(f"Maritime-mobile beyond 12nm limit: {distance}nm")
                    return False
            except (ValueError, TypeError):
                logger.debug(f"Invalid distance format: {distance_nm}")
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
        Calculate DXC award progress

        For DXC, each DXCC entity counts only once (first contact with any member).

        Args:
            contacts: List of contact records

        Returns:
            {
                'current': int,              # Number of unique DXCC entities
                'achieved_level': str,       # Current level (DXC-10, DXC-25, etc.)
                'next_level': str,           # Next level to achieve
                'progress_pct': float,       # Progress toward next level
                'entity_details': dict,      # First contact per entity
                'entities_worked': set       # Set of DXCC entities
            }
        """
        # Track unique DXCC entities (first contact only)
        entities_worked = set()
        entity_details: Dict[int, Dict] = {}

        for contact in contacts:
            if self.validate(contact):
                dxcc_entity = contact.get('dxcc_entity')

                if dxcc_entity and dxcc_entity not in entities_worked:
                    entities_worked.add(dxcc_entity)
                    entity_details[dxcc_entity] = {
                        'callsign': contact.get('callsign'),
                        'skcc_number': contact.get('skcc_number'),
                        'date': contact.get('date'),
                        'band': contact.get('band')
                    }

        entities_count = len(entities_worked)

        # Determine current level
        current_level = "Not Yet"
        next_level = "DXC-10"
        next_threshold = 10

        for threshold, level_name in DX_LEVELS:
            level_name_dxc = level_name.replace("DX-", "DXC-")
            if entities_count >= threshold:
                current_level = level_name_dxc
            elif entities_count < threshold:
                next_level = level_name_dxc
                next_threshold = threshold
                break

        # Calculate progress toward next level
        if current_level == "DXC-100":
            progress_pct = 100.0
        else:
            progress_pct = min(100.0, (entities_count / next_threshold) * 100)

        return {
            'current': entities_count,
            'achieved_level': current_level,
            'next_level': next_level if current_level != "DXC-100" else current_level,
            'progress_pct': progress_pct,
            'entity_details': entity_details,
            'entities_worked': entities_worked
        }

    def get_requirements(self) -> Dict[str, Any]:
        """
        Return DXC award requirements

        Returns:
            Award requirements dictionary
        """
        return {
            'name': 'SKCC DXC',
            'description': 'Country-based DX award - each country counts once',
            'base_requirement': '10+ unique DXCC entities',
            'modes': ['CW'],
            'bands': ['All'],
            'mechanical_key': True,
            'key_types': ['STRAIGHT', 'BUG', 'SIDESWIPER'],
            'effective_date': 'December 19, 2009 or later',
            'validity_rule': 'Must contact SKCC members outside own DXCC entity',
            'special_rules': [
                'Each DXCC entity counts only once (first contact)',
                'Maritime-mobile within 12nm counts; beyond does not',
                'Distance must be logged for /MM stations',
                'Multiple members in same entity do not add to count'
            ],
            'levels_available': True,
            'level_thresholds': [10, 25, 50, 75, 100]
        }

    def get_endorsements(self) -> List[Dict[str, Any]]:
        """Return DXC achievement levels"""
        return [
            {'level': 10, 'description': 'DXC-10', 'entities_needed': 10},
            {'level': 25, 'description': 'DXC-25', 'entities_needed': 25},
            {'level': 50, 'description': 'DXC-50', 'entities_needed': 50},
            {'level': 75, 'description': 'DXC-75', 'entities_needed': 75},
            {'level': 100, 'description': 'DXC-100', 'entities_needed': 100},
        ]
