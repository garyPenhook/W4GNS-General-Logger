"""
SKCC Canadian Maple Award - Contact SKCC members across Canadian provinces/territories

The Canadian Maple award has 4 distinct levels of achievement:
1. Yellow Maple: 10 contacts from any 10 provinces/territories (mixed bands)
2. Orange Maple: 10 contacts from same 10 provinces/territories on single band
3. Red Maple: 90 contacts - 10 from each province/territory across 9 HF bands
4. Gold Maple: 90 QRP contacts (≤5W) across all 9 HF bands

Rules:
- CW mode exclusively
- Mechanical key policy: STRAIGHT, BUG, or SIDESWIPER required
- Remote station must be in Canada
- Both operators must have SKCC membership at time of contact
- QSO dates must match or exceed both participants' SKCC join dates
- Valid HF bands: 160M, 80M, 60M, 40M, 30M, 20M, 17M, 15M, 12M, 10M
- 9 main HF bands for Red/Gold: 160M, 80M, 40M, 30M, 20M, 17M, 15M, 12M, 10M
- Provinces valid from September 1, 2009
- Territories (YT, NT, NU) valid from January 1, 2014
- Power must be logged for Gold Maple (≤5W)
"""

import logging
from typing import Dict, List, Any, Set
from collections import defaultdict

from src.skcc_awards.base import SKCCAwardBase
from src.utils.skcc_number import extract_base_skcc_number
from src.skcc_awards.constants import (
    CANADIAN_PROVINCES,
    CANADIAN_TERRITORIES,
    CANADIAN_PROVINCES_EFFECTIVE_DATE,
    CANADIAN_TERRITORIES_EFFECTIVE_DATE
)
from src.skcc_roster import get_roster_manager

logger = logging.getLogger(__name__)

# 9 main HF bands for Red/Gold Maple (excludes 60M)
RED_GOLD_BANDS = {'160M', '80M', '40M', '30M', '20M', '17M', '15M', '12M', '10M'}

# All 10 valid HF bands for Yellow/Orange
ALL_HF_BANDS = {'160M', '80M', '60M', '40M', '30M', '20M', '17M', '15M', '12M', '10M'}

# QRP power threshold (watts)
QRP_THRESHOLD = 5.0


class CanadianMapleAward(SKCCAwardBase):
    """SKCC Canadian Maple Award - 4 levels (Yellow, Orange, Red, Gold)"""

    def __init__(self, database):
        """
        Initialize Canadian Maple award

        Args:
            database: Database instance for contact queries
        """
        super().__init__(name="Canadian Maple", program_id="SKCC_CANADIAN_MAPLE", database=database)
        self.roster_manager = get_roster_manager()

        # Get user's SKCC join date from config
        self.user_join_date = self._get_user_join_date()

        # All valid provinces and territories
        self._all_locations = CANADIAN_PROVINCES | CANADIAN_TERRITORIES

    def _get_user_join_date(self) -> str:
        """Get user's SKCC join date from config (YYYYMMDD format)"""
        if hasattr(self.database, 'config'):
            return self.database.config.get('skcc.join_date', '')
        return ''

    def validate(self, contact: Dict[str, Any]) -> bool:
        """
        Check if a contact qualifies for Canadian Maple award

        Requirements:
        - CW mode only
        - SKCC number present
        - Mechanical key required (STRAIGHT, BUG, or SIDESWIPER)
        - Remote station in Canada
        - Province contacts valid from September 1, 2009
        - Territory contacts valid from January 1, 2014
        - Both operators must be SKCC members at time of contact
        - QSO dates must match or exceed both participants' SKCC join dates

        Args:
            contact: Contact record dictionary

        Returns:
            True if contact qualifies for Canadian Maple award
        """
        # Check common SKCC rules (CW mode, mechanical key, SKCC number)
        if not self.validate_common_rules(contact):
            return False

        # Get contact date
        qso_date = contact.get('date', '')
        if qso_date:
            qso_date = qso_date.replace('-', '')  # Normalize YYYY-MM-DD to YYYYMMDD

        # Get callsign (remove portable/suffix indicators)
        callsign = contact.get('callsign', '').upper().strip()
        base_call = callsign.split('/')[0] if '/' in callsign else callsign

        # Get province/territory
        location = self._extract_location(contact)
        if not location:
            logger.debug(f"Contact {base_call}: no Canadian province/territory identified")
            return False

        # Check date validity based on location type
        if location in CANADIAN_PROVINCES:
            if not qso_date or qso_date < CANADIAN_PROVINCES_EFFECTIVE_DATE:
                logger.debug(
                    f"Contact {base_call}: province contact before Sept 1, 2009 "
                    f"(date: {qso_date})"
                )
                return False
        elif location in CANADIAN_TERRITORIES:
            if not qso_date or qso_date < CANADIAN_TERRITORIES_EFFECTIVE_DATE:
                logger.debug(
                    f"Contact {base_call}: territory contact before Jan 1, 2014 "
                    f"(date: {qso_date})"
                )
                return False

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

        # Verify valid SKCC number
        skcc_num = contact.get('skcc_number', '').strip()
        if skcc_num:
            base_number = extract_base_skcc_number(skcc_num)
            if not base_number or not base_number.isdigit():
                logger.debug(f"Contact {base_call}: invalid SKCC number format: {skcc_num}")
                return False

        return True

    def _extract_location(self, contact: Dict[str, Any]) -> str:
        """
        Extract Canadian province or territory from contact

        Tries multiple methods:
        1. Direct 'state' field
        2. Callsign prefix (VE1-VE9, VO1, VY0, etc.)
        3. Comments field

        Args:
            contact: Contact record dictionary

        Returns:
            Province/territory code (e.g., 'ON', 'BC') or empty string
        """
        # Method 1: Direct state/province field
        if 'state' in contact and contact['state']:
            loc = contact['state'].upper().strip()
            if loc in self._all_locations:
                return loc

        # Method 2: Callsign prefix
        callsign = contact.get('callsign', '').upper().strip()
        if callsign:
            # Canadian callsigns: VE1-VE9, VO1, VO2, VY0, VY1, VY2
            # Map to provinces/territories
            if callsign.startswith('VE1') or callsign.startswith('VA1'):
                return 'NS'  # Nova Scotia
            elif callsign.startswith('VE2') or callsign.startswith('VA2'):
                return 'QC'  # Quebec
            elif callsign.startswith('VE3') or callsign.startswith('VA3'):
                return 'ON'  # Ontario
            elif callsign.startswith('VE4') or callsign.startswith('VA4'):
                return 'MB'  # Manitoba
            elif callsign.startswith('VE5') or callsign.startswith('VA5'):
                return 'SK'  # Saskatchewan
            elif callsign.startswith('VE6') or callsign.startswith('VA6'):
                return 'AB'  # Alberta
            elif callsign.startswith('VE7') or callsign.startswith('VA7'):
                return 'BC'  # British Columbia
            elif callsign.startswith('VE8') or callsign.startswith('VA8'):
                return 'NT'  # Northwest Territories
            elif callsign.startswith('VE9') or callsign.startswith('VA9'):
                return 'NB'  # New Brunswick
            elif callsign.startswith('VO1'):
                return 'NL'  # Newfoundland
            elif callsign.startswith('VO2'):
                return 'NL'  # Labrador (part of NL)
            elif callsign.startswith('VY0'):
                return 'NU'  # Nunavut
            elif callsign.startswith('VY1'):
                return 'YT'  # Yukon
            elif callsign.startswith('VY2'):
                return 'PE'  # Prince Edward Island

        # Method 3: Comments field
        comments = contact.get('comments', '').upper()
        for loc in self._all_locations:
            if loc in comments:
                return loc

        return ""

    def _normalize_band(self, band: str) -> str:
        """
        Normalize band notation (e.g., '20m' -> '20M')

        Args:
            band: Band string from contact

        Returns:
            Normalized band string
        """
        if not band:
            return ""
        return band.upper().strip()

    def calculate_progress(self, contacts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate Canadian Maple award progress

        Tracks 4 distinct achievement levels:
        - Yellow Maple: 10 provinces/territories (any bands)
        - Orange Maple: 10 provinces/territories on single band
        - Red Maple: All 10 locations across 9 HF bands (90 contacts)
        - Gold Maple: All 10 locations across 9 HF bands at QRP (90 contacts)

        Args:
            contacts: List of contact records

        Returns:
            {
                'yellow_maple': dict,    # Yellow Maple progress
                'orange_maple': dict,    # Orange Maple progress
                'red_maple': dict,       # Red Maple progress
                'gold_maple': dict,      # Gold Maple progress
                'highest_achieved': str, # Highest level achieved
                'locations_worked': set, # All locations worked
                'bands_worked': set,     # All bands worked
            }
        """
        # Track contacts by location
        locations_worked = set()

        # Track for Yellow Maple (any 10 provinces/territories, mixed bands)
        yellow_locations = set()

        # Track for Orange Maple (10 provinces/territories on single band)
        locations_by_band: Dict[str, Set[str]] = defaultdict(set)

        # Track for Red Maple (10 locations x 9 bands)
        red_matrix: Dict[str, Set[str]] = defaultdict(set)  # {location: {bands}}

        # Track for Gold Maple (10 locations x 9 bands at QRP)
        gold_matrix: Dict[str, Set[str]] = defaultdict(set)  # {location: {bands}}

        all_bands_worked = set()

        # Process all qualifying contacts
        for contact in contacts:
            if self.validate(contact):
                location = self._extract_location(contact)
                band = self._normalize_band(contact.get('band', ''))
                power = contact.get('power_watts')

                if not location or not band:
                    continue

                locations_worked.add(location)
                all_bands_worked.add(band)

                # Yellow Maple: any 10 locations, any bands
                yellow_locations.add(location)

                # Orange Maple: 10 locations on single band
                if band in ALL_HF_BANDS:
                    locations_by_band[band].add(location)

                # Red Maple: 10 locations x 9 HF bands
                if band in RED_GOLD_BANDS:
                    red_matrix[location].add(band)

                # Gold Maple: 10 locations x 9 HF bands at QRP
                if band in RED_GOLD_BANDS and power is not None:
                    try:
                        power_val = float(power)
                        if power_val <= QRP_THRESHOLD:
                            gold_matrix[location].add(band)
                    except (ValueError, TypeError):
                        pass

        # Calculate Yellow Maple
        yellow_achieved = len(yellow_locations) >= 10
        yellow_progress = {
            'achieved': yellow_achieved,
            'locations_count': len(yellow_locations),
            'required': 10,
            'progress_pct': min(100.0, (len(yellow_locations) / 10) * 100),
            'locations_worked': sorted(list(yellow_locations))
        }

        # Calculate Orange Maple (need 10 locations on ANY single band)
        orange_achieved = False
        orange_band = None
        orange_count = 0
        for band, locs in locations_by_band.items():
            if len(locs) >= 10:
                orange_achieved = True
                orange_band = band
                orange_count = len(locs)
                break

        if not orange_achieved:
            # Find best band
            for band, locs in locations_by_band.items():
                if len(locs) > orange_count:
                    orange_count = len(locs)
                    orange_band = band

        orange_progress = {
            'achieved': orange_achieved,
            'locations_count': orange_count,
            'required': 10,
            'progress_pct': min(100.0, (orange_count / 10) * 100),
            'band': orange_band,
            'locations_worked': sorted(list(locations_by_band.get(orange_band, []))) if orange_band else []
        }

        # Calculate Red Maple (10 locations x 9 bands = 90 contacts)
        red_contacts = sum(len(bands) for bands in red_matrix.values())
        red_complete_locations = sum(1 for bands in red_matrix.values() if len(bands) >= 9)
        red_achieved = red_complete_locations >= 10

        red_progress = {
            'achieved': red_achieved,
            'total_contacts': red_contacts,
            'required': 90,  # 10 locations x 9 bands
            'progress_pct': min(100.0, (red_contacts / 90) * 100),
            'complete_locations': red_complete_locations,
            'matrix': {loc: sorted(list(bands)) for loc, bands in red_matrix.items()}
        }

        # Calculate Gold Maple (10 locations x 9 bands at QRP = 90 QRP contacts)
        gold_contacts = sum(len(bands) for bands in gold_matrix.values())
        gold_complete_locations = sum(1 for bands in gold_matrix.values() if len(bands) >= 9)
        gold_achieved = gold_complete_locations >= 10

        gold_progress = {
            'achieved': gold_achieved,
            'total_contacts': gold_contacts,
            'required': 90,  # 10 locations x 9 bands at QRP
            'progress_pct': min(100.0, (gold_contacts / 90) * 100),
            'complete_locations': gold_complete_locations,
            'matrix': {loc: sorted(list(bands)) for loc, bands in gold_matrix.items()}
        }

        # Determine highest level achieved
        if gold_achieved:
            highest = "Gold Maple"
        elif red_achieved:
            highest = "Red Maple"
        elif orange_achieved:
            highest = "Orange Maple"
        elif yellow_achieved:
            highest = "Yellow Maple"
        else:
            highest = "Not Yet"

        return {
            'yellow_maple': yellow_progress,
            'orange_maple': orange_progress,
            'red_maple': red_progress,
            'gold_maple': gold_progress,
            'highest_achieved': highest,
            'locations_worked': sorted(list(locations_worked)),
            'bands_worked': sorted(list(all_bands_worked)),
        }

    def get_requirements(self) -> Dict[str, Any]:
        """
        Return Canadian Maple award requirements

        Returns:
            Award requirements dictionary
        """
        return {
            'name': 'SKCC Canadian Maple',
            'description': '4 levels of achievement contacting SKCC members across Canada',
            'levels': {
                'Yellow Maple': '10 provinces/territories (any bands)',
                'Orange Maple': '10 provinces/territories on single band',
                'Red Maple': '90 contacts - 10 from each province/territory across 9 HF bands',
                'Gold Maple': '90 QRP contacts (≤5W) across all 9 HF bands'
            },
            'modes': ['CW'],
            'bands': ['All HF: 160M, 80M, 60M, 40M, 30M, 20M, 17M, 15M, 12M, 10M'],
            'red_gold_bands': ['160M', '80M', '40M', '30M', '20M', '17M', '15M', '12M', '10M'],
            'mechanical_key': True,
            'key_types': ['STRAIGHT', 'BUG', 'SIDESWIPER'],
            'effective_date': 'Sept 1, 2009 (provinces), Jan 1, 2014 (territories)',
            'validity_rule': 'Remote station must be in Canada',
            'special_rules': [
                'Provinces valid from September 1, 2009',
                'Territories (YT, NT, NU) valid from January 1, 2014',
                'Power must be logged for Gold Maple (≤5W QRP)',
                'Red/Gold use 9 HF bands (excludes 60M)',
                'All 10 provinces/territories required for each level'
            ],
            'provinces': sorted(list(CANADIAN_PROVINCES)),
            'territories': sorted(list(CANADIAN_TERRITORIES))
        }

    def get_endorsements(self) -> List[Dict[str, Any]]:
        """
        Return Canadian Maple achievement levels

        Returns:
            List of level dictionaries
        """
        return [
            {'level': 'Yellow', 'description': 'Yellow Maple', 'requirement': '10 provinces/territories (any bands)'},
            {'level': 'Orange', 'description': 'Orange Maple', 'requirement': '10 provinces/territories on single band'},
            {'level': 'Red', 'description': 'Red Maple', 'requirement': '90 contacts across 9 HF bands'},
            {'level': 'Gold', 'description': 'Gold Maple', 'requirement': '90 QRP contacts (≤5W) across 9 HF bands'},
        ]
