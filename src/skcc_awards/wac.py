"""
SKCC WAC Award - Worked All Continents

The WAC Award recognizes contacts with SKCC members in all 6 continents.
An operator must show contacts in which they have exchanged names and SKCC
numbers with another SKCC member from each of the 6 continents.

Rules:
- Contact SKCC members in all 6 continents
- CW mode exclusively
- Mechanical key policy: straight key, bug, or side swiper only (CRITICAL!)
- Both operators must hold SKCC membership at time of contact
- Contacts valid from October 9, 2011 onwards
- Contacts may be made on any band (including WARC)
- Single-band endorsements available
- WAC-QRP endorsement available (≤5W power)

Continents:
- North America (NA)
- South America (SA)
- Europe (EU)
- Africa (AF)
- Asia (AS)
- Oceania (OC)
"""

import logging
from typing import Dict, List, Any, Set
from collections import defaultdict

from src.skcc_awards.base import SKCCAwardBase
from src.utils.skcc_number import extract_base_skcc_number
from src.skcc_awards.constants import WAC_EFFECTIVE_DATE
from src.skcc_roster import get_roster_manager

logger = logging.getLogger(__name__)

# QRP power threshold (watts)
QRP_THRESHOLD = 5.0

# Valid continents
CONTINENTS = {'NA', 'SA', 'EU', 'AF', 'AS', 'OC'}

CONTINENT_NAMES = {
    'NA': 'North America',
    'SA': 'South America',
    'EU': 'Europe',
    'AF': 'Africa',
    'AS': 'Asia',
    'OC': 'Oceania'
}


class SKCCWACAward(SKCCAwardBase):
    """SKCC WAC Award - Worked All 6 Continents"""

    def __init__(self, database):
        """
        Initialize SKCC WAC award

        Args:
            database: Database instance for contact queries
        """
        super().__init__(name="SKCC WAC", program_id="SKCC_WAC", database=database)
        self.roster_manager = get_roster_manager()
        self.user_join_date = self._get_user_join_date()

        # Total continents required
        self.total_continents = 6

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
        Check if a contact qualifies for SKCC WAC award

        Requirements:
        - CW mode only
        - SKCC number present on both sides
        - Mechanical key required (STRAIGHT, BUG, or SIDESWIPER) - CRITICAL!
        - Contact date on or after October 9, 2011
        - Remote station must be on one of the 6 continents
        - Both operators must be SKCC members

        Args:
            contact: Contact record dictionary

        Returns:
            True if contact qualifies for SKCC WAC award
        """
        # Check common SKCC rules (CW mode, mechanical key, SKCC number)
        if not self.validate_common_rules(contact):
            return False

        # Get contact date
        qso_date = contact.get('qso_date', contact.get('date', ''))
        if qso_date:
            qso_date = qso_date.replace('-', '')  # Normalize YYYY-MM-DD to YYYYMMDD

        # Check contact date (must be on/after October 9, 2011)
        if qso_date and qso_date < WAC_EFFECTIVE_DATE:
            return False

        # Get callsign (remove portable/suffix indicators)
        callsign = contact.get('callsign', '').upper().strip()
        base_call = callsign.split('/')[0] if '/' in callsign else callsign

        # Must have extractable continent from contact
        continent = self._get_continent_from_contact(contact)
        if not continent or continent not in CONTINENTS:
            logger.debug(f"Cannot determine valid continent from contact: {contact.get('callsign')}")
            return False

        # Verify valid SKCC number
        skcc_num = contact.get('skcc_number', '').strip()
        if skcc_num:
            base_number = extract_base_skcc_number(skcc_num)
            if not base_number or not base_number.isdigit():
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

    def _get_continent_from_contact(self, contact: Dict[str, Any]) -> str:
        """
        Get continent from contact

        Tries multiple methods to determine continent:
        1. Direct continent field (if available)
        2. DXCC entity lookup (if dxcc_entity field present)
        3. Country field lookup
        4. Comments field

        Args:
            contact: Contact record dictionary

        Returns:
            Continent code (e.g., 'NA', 'EU') or empty string if unknown
        """
        # Method 1: Direct continent field
        if 'continent' in contact and contact['continent']:
            cont = contact['continent'].upper().strip()
            if cont in CONTINENTS:
                return cont

        # Method 2: Country field (try to map to continent)
        country = contact.get('country', '').upper().strip()
        if country:
            # Simple mapping of common countries to continents
            # This is a basic implementation - full DXCC mapping would be more complete
            country_to_continent = {
                'UNITED STATES': 'NA',
                'USA': 'NA',
                'CANADA': 'NA',
                'MEXICO': 'NA',
                'BRAZIL': 'SA',
                'ARGENTINA': 'SA',
                'CHILE': 'SA',
                'UNITED KINGDOM': 'EU',
                'GERMANY': 'EU',
                'FRANCE': 'EU',
                'ITALY': 'EU',
                'SPAIN': 'EU',
                'RUSSIA': 'EU',
                'JAPAN': 'AS',
                'CHINA': 'AS',
                'INDIA': 'AS',
                'AUSTRALIA': 'OC',
                'NEW ZEALAND': 'OC',
                'SOUTH AFRICA': 'AF',
                'EGYPT': 'AF',
            }

            for country_name, cont in country_to_continent.items():
                if country_name in country:
                    return cont

        # Method 3: Comments field
        comments = contact.get('comments', '').upper()
        for cont in CONTINENTS:
            if cont in comments or CONTINENT_NAMES[cont].upper() in comments:
                return cont

        # Method 4: Callsign prefix heuristics (basic implementation)
        callsign = contact.get('callsign', '').upper().strip()
        if callsign:
            # North America: K, W, N, VE, XE
            if callsign[0] in 'KWN' or callsign.startswith('VE') or callsign.startswith('XE'):
                return 'NA'
            # Europe: G, DL, F, I, EA, SP, etc.
            elif callsign[0] in 'G' or callsign.startswith('DL') or callsign.startswith('F') or callsign.startswith('EA'):
                return 'EU'
            # Asia: JA, HL, BY, etc.
            elif callsign.startswith('JA') or callsign.startswith('HL') or callsign.startswith('BY'):
                return 'AS'
            # Oceania: VK, ZL
            elif callsign.startswith('VK') or callsign.startswith('ZL'):
                return 'OC'
            # South America: PY, LU, CE
            elif callsign.startswith('PY') or callsign.startswith('LU') or callsign.startswith('CE'):
                return 'SA'
            # Africa: ZS, EA8, etc.
            elif callsign.startswith('ZS') or callsign.startswith('EA8'):
                return 'AF'

        return ""

    def calculate_progress(self, contacts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate SKCC WAC award progress

        Tracks which continents have been worked via contacts with SKCC members
        from each continent.

        Args:
            contacts: List of contact records

        Returns:
            {
                'current': int,                 # Number of continents worked
                'required': int,                # 6 (all continents)
                'achieved': bool,               # True if all 6 continents worked
                'progress_pct': float,          # Percentage (0-100)
                'level': str,                   # "WAC" or "Not Yet"
                'continents_worked': list,      # List of worked continent codes
                'continents_needed': list,      # List of needed continent codes
                'continent_details': dict,      # Per-continent contact counts
                'band_details': dict,           # Contacts per band per continent
                'qrp_continents': set,          # Continents worked at QRP
            }
        """
        # Track continents worked and contact details
        continents_worked: Set[str] = set()
        continent_details: Dict[str, int] = {code: 0 for code in CONTINENTS}
        band_details: Dict[str, Dict[str, int]] = {
            code: {} for code in CONTINENTS
        }
        qrp_continents: Set[str] = set()

        for contact in contacts:
            if self.validate(contact):
                continent = self._get_continent_from_contact(contact)

                if continent in CONTINENTS:
                    continents_worked.add(continent)
                    continent_details[continent] += 1

                    # Track by band
                    band = contact.get('band', 'Unknown').upper()
                    if band not in band_details[continent]:
                        band_details[continent][band] = 0
                    band_details[continent][band] += 1

                    # Track QRP continents
                    power = contact.get('power_watts')
                    if power is not None:
                        try:
                            power_val = float(power)
                            if power_val <= QRP_THRESHOLD:
                                qrp_continents.add(continent)
                        except (ValueError, TypeError):
                            pass

        # Determine if award is achieved (all 6 continents worked)
        achieved = len(continents_worked) >= 6
        current_count = len(continents_worked)

        # Calculate continents needed
        continents_needed = sorted(list(CONTINENTS - continents_worked))

        # Calculate level
        if achieved:
            level_name = "WAC"
        else:
            level_name = "Not Yet"

        return {
            'current': current_count,
            'required': 6,
            'achieved': achieved,
            'progress_pct': min(100.0, (current_count / 6) * 100),
            'level': level_name,
            'continents_worked': sorted(list(continents_worked)),
            'continents_needed': continents_needed,
            'continent_details': continent_details,
            'band_details': band_details,
            'qrp_continents': sorted(list(qrp_continents)),
        }

    def get_requirements(self) -> Dict[str, Any]:
        """
        Return SKCC WAC award requirements

        Returns:
            Award requirements dictionary
        """
        return {
            'name': 'SKCC WAC Award',
            'description': 'Contact SKCC members in all 6 continents',
            'base_requirement': 'Contacts with members from all 6 continents',
            'modes': ['CW'],
            'bands': ['All'],
            'effective_date': 'October 9, 2011 or later',
            'validity_rule': 'Both operators must hold SKCC membership at time of contact',
            'mechanical_key': True,
            'key_types': ['STRAIGHT', 'BUG', 'SIDESWIPER'],
            'continents_required': 6,
            'continents': sorted([f"{code} ({CONTINENT_NAMES[code]})" for code in CONTINENTS]),
            'special_rules': [
                'Contacts may be made on any band (including WARC)',
                'Single-band endorsements available (any individual band)',
                'WAC-QRP endorsement available (≤5W power for all contacts)',
                'Remote stations do not need to be participating in the award',
                'All 6 continents required (NA, SA, EU, AF, AS, OC)',
            ]
        }

    def get_endorsements(self) -> List[Dict[str, Any]]:
        """Return SKCC WAC endorsement levels"""
        return [
            {'level': 'WAC', 'continents': 6, 'description': 'All 6 continents'},
            {'level': 'WAC-160M', 'continents': 6, 'description': 'All 6 continents on 160M'},
            {'level': 'WAC-80M', 'continents': 6, 'description': 'All 6 continents on 80M'},
            {'level': 'WAC-40M', 'continents': 6, 'description': 'All 6 continents on 40M'},
            {'level': 'WAC-20M', 'continents': 6, 'description': 'All 6 continents on 20M'},
            {'level': 'WAC-QRP', 'continents': 6, 'description': 'All 6 continents at QRP (≤5W)'},
        ]
