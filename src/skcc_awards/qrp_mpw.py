"""
SKCC QRP Miles per Watt (MPW) Award

The QRP MPW award recognizes QRP contacts achieving a distance of at least
1,000 miles per watt equivalent. Subsequent endorsements are issued at 1,500
and 2,000 miles-per-watt thresholds with no upper limit.

Rules:
- Both operators must hold SKCC membership at time of contact
- QSOs made on or after Sept. 1, 2014 are eligible
- Output power must be 5 watts or less for entire QSO
- Contact may NOT be initiated at high power then reduced
- Must exchange signal report, location, name, SKCC number, and power output
- Log must include site and antenna description
- Distance must come from N9SSA calculator (miles)
- SKCC-approved keying devices only (straight key, side-swiper, semi-automatic)
- Satellite contacts are ineligible
- Award is not affected by C, T, or S status of members
- Endorsement levels: 1,000 MPW (base), 1,500 MPW, 2,000 MPW (and beyond)
"""

import logging
from typing import Dict, List, Any
from datetime import datetime

from src.skcc_awards.base import SKCCAwardBase
from src.utils.skcc_number import extract_base_skcc_number
from src.skcc_awards.constants import SPECIAL_EVENT_CALLS
from src.skcc_roster import get_roster_manager

logger = logging.getLogger(__name__)

# Award effective date
QRP_MPW_EFFECTIVE_DATE = "20140901"  # September 1, 2014
QRP_MPW_DISTANCE_SOURCE = "N9SSA"

# Miles per Watt thresholds
MPW_THRESHOLDS = {
    'base': 1000,      # Base award
    'level_2': 1500,   # Second endorsement
    'level_3': 2000,   # Third endorsement
}

# Maximum QRP power in watts
QRP_MAX_POWER = 5.0

# Country identifiers for location validation
US_COUNTRY_NAMES = {
    'UNITED STATES', 'UNITED STATES OF AMERICA', 'USA', 'US', 'U.S.A.', 'U.S.'
}
CANADA_COUNTRY_NAMES = {'CANADA', 'CAN'}


class QRPMPWAward(SKCCAwardBase):
    """SKCC QRP Miles per Watt Award - 1,000+ MPW contacts"""

    def __init__(self, database):
        """
        Initialize QRP MPW award

        Args:
            database: Database instance for contact queries
        """
        super().__init__(name="QRP MPW", program_id="SKCC_QRP_MPW", database=database)
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

    def _get_qso_date(self, contact: Dict[str, Any]) -> str:
        """Return QSO date normalized to YYYYMMDD, or empty string if missing."""
        qso_date = contact.get('qso_date') or contact.get('date') or ''
        qso_date = str(qso_date).strip()
        if qso_date:
            qso_date = qso_date.replace('-', '')
        return qso_date

    def _parse_float(self, value: Any) -> float:
        """Parse numeric values with minimal tolerance for formatting."""
        if value is None or value == '':
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def _is_truthy(self, value: Any) -> bool:
        if value is None:
            return False
        return str(value).strip().lower() in ('1', 'true', 'yes', 'y')

    def _get_location_code(self, contact: Dict[str, Any]) -> str:
        """Return validated location code (state/province or IAAF country code)."""
        state = (contact.get('state') or '').strip().upper()
        country = (contact.get('country') or '').strip().upper()
        qth = (contact.get('qth') or '').strip().upper()

        if state:
            return state

        if country and len(country) == 3 and country.isalpha():
            return country

        if qth and len(qth) == 3 and qth.isalpha():
            return qth

        return ''

    def _location_is_valid(self, contact: Dict[str, Any]) -> bool:
        """Validate location rules for US/Canada vs. DX stations."""
        state = (contact.get('state') or '').strip().upper()
        country = (contact.get('country') or '').strip().upper()
        qth = (contact.get('qth') or '').strip().upper()

        if state and len(state) == 2 and state.isalpha():
            if not country or country in US_COUNTRY_NAMES or country in CANADA_COUNTRY_NAMES:
                return True
            return False

        if country in US_COUNTRY_NAMES or country in CANADA_COUNTRY_NAMES:
            return False

        if country and len(country) == 3 and country.isalpha():
            return True

        return bool(qth) and len(qth) == 3 and qth.isalpha()

    def validate(self, contact: Dict[str, Any]) -> bool:
        """
        Check if a contact qualifies for QRP MPW award

        Requirements:
        - CW mode only
        - SKCC number present on both sides
        - Mechanical key required (STRAIGHT, BUG, or SIDESWIPER)
        - Both operators must hold SKCC membership at time of contact
        - QSO date >= Sept 1, 2014
        - Power must be <= 5 watts
        - Must have distance information
        - Must achieve at least 1,000 miles per watt

        Args:
            contact: Contact record dictionary

        Returns:
            bool: True if contact qualifies, False otherwise
        """
        # Base validation (CW mode, mechanical key)
        if not self.validate_common_rules(contact):
            return False

        # Extract fields
        callsign = contact.get('callsign', '').strip().upper()
        qso_date = self._get_qso_date(contact)
        skcc_num = contact.get('skcc_number', '').strip()
        my_skcc_num = contact.get('my_skcc_number', '').strip()
        power_watts = contact.get('power_watts')
        distance_miles = contact.get('distance_miles')
        distance_source = (contact.get('distance_source') or '').strip()
        site = (contact.get('site') or '').strip()
        antenna = (contact.get('antenna') or '').strip()
        time_on = (contact.get('time_on') or '').strip()
        band = (contact.get('band') or '').strip()
        rst_sent = (contact.get('rst_sent') or '').strip()
        rst_rcvd = (contact.get('rst_rcvd') or '').strip()
        name = (contact.get('name') or '').strip()
        is_satellite = contact.get('is_satellite')

        # Must have valid SKCC number
        if not skcc_num:
            logger.debug(f"Contact {callsign} missing SKCC number")
            return False

        base_number = extract_base_skcc_number(skcc_num)
        if not base_number or not base_number.isdigit():
            logger.debug(f"Invalid SKCC number format: {skcc_num}")
            return False

        # CRITICAL RULE: QSOs made on or after Sept. 1, 2014 are eligible
        if not qso_date or qso_date < QRP_MPW_EFFECTIVE_DATE:
            logger.debug(
                f"Contact {callsign} not valid: QSO date {qso_date} before "
                f"effective date {QRP_MPW_EFFECTIVE_DATE}"
            )
            return False

        # CRITICAL RULE: Satellite contacts are ineligible
        if self._is_truthy(is_satellite):
            logger.debug(f"Contact {callsign} not valid: satellite contact")
            return False

        # CRITICAL RULE: Logging requires date, time, band, and full exchange
        if not time_on or not band:
            logger.debug(f"Contact {callsign} missing time/band")
            return False

        if not rst_sent or not rst_rcvd:
            logger.debug(f"Contact {callsign} missing RST exchange")
            return False

        if rst_sent in ('599', '559') and rst_rcvd in ('599', '559'):
            logger.debug(f"Contact {callsign} has perfunctory RST exchange")
            return False

        if not name:
            logger.debug(f"Contact {callsign} missing operator name")
            return False

        if not my_skcc_num:
            logger.debug(f"Contact {callsign} missing operator SKCC number")
            return False

        if not self._location_is_valid(contact):
            logger.debug(f"Contact {callsign} missing/invalid location")
            return False

        if not site or not antenna:
            logger.debug(f"Contact {callsign} missing site/antenna description")
            return False

        if distance_source.strip().upper() != QRP_MPW_DISTANCE_SOURCE:
            logger.debug(f"Contact {callsign} invalid distance source: {distance_source}")
            return False

        # Get callsign (remove portable/suffix indicators)
        base_call = callsign.split('/')[0] if '/' in callsign else callsign

        # Filter out club and special event calls
        if base_call in SPECIAL_EVENT_CALLS:
            logger.debug(f"Club/special-event call filtered: {callsign}")
            return False

        # CRITICAL RULE: "Both stations must be members of the SKCC at time of the contact"
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

        # CRITICAL RULE: Power must be <= 5 watts
        if power_watts is None:
            logger.debug(f"Contact {callsign} missing power information")
            return False

        try:
            power = float(power_watts)
            if power <= 0 or power > QRP_MAX_POWER:
                logger.debug(
                    f"Contact {callsign} not valid: power {power}W exceeds "
                    f"QRP limit of {QRP_MAX_POWER}W"
                )
                return False
        except (ValueError, TypeError):
            logger.debug(f"Contact {callsign} has invalid power value: {power_watts}")
            return False

        # Must have distance information from N9SSA calculator
        distance = self._parse_float(distance_miles)
        if distance is None or distance <= 0:
            logger.debug(f"Contact {callsign} has invalid distance: {distance_miles}")
            return False

        # Calculate miles per watt
        mpw = distance / power

        # CRITICAL RULE: Must achieve at least 1,000 miles per watt
        if mpw < MPW_THRESHOLDS['base']:
            logger.debug(
                f"Contact {callsign} not valid: {mpw:.1f} MPW is below "
                f"minimum threshold of {MPW_THRESHOLDS['base']} MPW"
            )
            return False

        logger.debug(
            f"Contact {callsign} valid for QRP MPW: "
            f"{distance:.1f} miles @ {power}W = {mpw:.1f} MPW"
        )
        return True

    def calculate_progress(self, contacts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate QRP MPW award progress

        Tracks the highest MPW achievement and counts contacts at each threshold.

        Args:
            contacts: List of validated contact records

        Returns:
            dict: Progress statistics including:
                - max_mpw: Highest MPW achieved
                - count_1000: Number of contacts >= 1,000 MPW
                - count_1500: Number of contacts >= 1,500 MPW
                - count_2000: Number of contacts >= 2,000 MPW
                - qualified_contacts: List of qualifying contact details
                - current_level: Current achievement level
                - next_threshold: Next MPW goal
        """
        max_mpw = 0.0
        count_1000 = 0
        count_1500 = 0
        count_2000 = 0
        qualified_contacts = []

        for contact in contacts:
            if not self.validate(contact):
                continue

            power_watts = contact.get('power_watts')
            distance_miles = contact.get('distance_miles')

            try:
                power = float(power_watts)
                distance = float(distance_miles)
            except (ValueError, TypeError):
                continue

            if power <= 0:
                continue

            mpw = distance / power

            # Track highest MPW
            if mpw > max_mpw:
                max_mpw = mpw

            # Count contacts at each threshold
            if mpw >= MPW_THRESHOLDS['base']:
                count_1000 += 1
            if mpw >= MPW_THRESHOLDS['level_2']:
                count_1500 += 1
            if mpw >= MPW_THRESHOLDS['level_3']:
                count_2000 += 1

            # Store qualified contact details
            qualified_contacts.append({
                'callsign': contact.get('callsign'),
                'qso_date': contact.get('qso_date', contact.get('date')),
                'time_on': contact.get('time_on'),
                'rst_sent': contact.get('rst_sent'),
                'rst_rcvd': contact.get('rst_rcvd'),
                'location': self._get_location_code(contact),
                'site': contact.get('site'),
                'antenna': contact.get('antenna'),
                'distance_source': contact.get('distance_source'),
                'distance_miles': distance,
                'power_watts': power,
                'mpw': mpw,
                'my_skcc_number': contact.get('my_skcc_number'),
                'band': contact.get('band'),
                'mode': contact.get('mode')
            })

        # Determine current achievement level
        # Per SKCC rules: "Additional endorsements continue in 500-mile increments with no upper limit"
        current_level = "Not Achieved"
        next_threshold = MPW_THRESHOLDS['base']

        if max_mpw >= MPW_THRESHOLDS['base']:
            current_level = "1,000 MPW"
            next_threshold = MPW_THRESHOLDS['level_2']

        if max_mpw >= MPW_THRESHOLDS['level_2']:
            current_level = "1,500 MPW"
            next_threshold = MPW_THRESHOLDS['level_3']

        if max_mpw >= MPW_THRESHOLDS['level_3']:
            # Calculate endorsement level beyond 2,000 MPW
            # Endorsements continue at 500 MPW increments (2,500, 3,000, 3,500, etc.)
            endorsement_level = int(max_mpw // 500) * 500

            if endorsement_level > 2000:
                current_level = f"{endorsement_level:,} MPW"
                next_threshold = endorsement_level + 500
            else:
                current_level = "2,000 MPW"
                next_threshold = 2500

        # Sort contacts by MPW (highest first)
        qualified_contacts.sort(key=lambda x: x['mpw'], reverse=True)

        return {
            'max_mpw': max_mpw,
            'count_1000': count_1000,
            'count_1500': count_1500,
            'count_2000': count_2000,
            'qualified_contacts': qualified_contacts[:50],  # Top 50 contacts
            'current_level': current_level,
            'next_threshold': next_threshold,
            'achieved': max_mpw >= MPW_THRESHOLDS['base']
        }

    def get_requirements(self) -> Dict[str, Any]:
        """
        Return QRP MPW award requirements

        Returns:
            Dictionary with award requirements
        """
        return {
            'name': 'QRP Miles per Watt',
            'program_id': 'SKCC_QRP_MPW',
            'description': (
                'Achieve QRP contacts with a distance of at least 1,000 miles per watt. '
                'Subsequent endorsements at 1,500 and 2,000 MPW thresholds (and beyond).'
            ),
            'minimum_mpw': MPW_THRESHOLDS['base'],
            'max_power_watts': QRP_MAX_POWER,
            'effective_date': '2014-09-01',
            'mode': 'CW',
            'key_types': ['STRAIGHT', 'BUG', 'SIDESWIPER'],
            'membership_required': True,
            'special_rules': [
                'Both stations must be SKCC members at time of contact',
                'QSOs on or after September 1, 2014',
                'Output power must be 5 watts or less for entire QSO',
                'Contact may NOT be initiated at high power then reduced to increase MPW',
                'Must exchange signal report, location, name, SKCC number, and power output',
                'Log must include date, time, band, location, site, antenna, distance, and MPW',
                'Distance must be from N9SSA calculator',
                'Satellite contacts are ineligible',
                'Award is not affected by C, T, or S member status',
                'Distance and power information required for calculation'
            ],
            'endorsements_available': True,
            'endorsement_levels': [1000, 1500, 2000]
        }

    def get_endorsements(self) -> List[Dict[str, Any]]:
        """
        Return list of QRP MPW endorsement levels

        Returns:
            List of endorsement level dictionaries
        """
        return [
            {
                'level': 1000,
                'description': '1,000 MPW',
                'mpw_needed': 1000,
                'display_name': 'Base Award'
            },
            {
                'level': 1500,
                'description': '1,500 MPW',
                'mpw_needed': 1500,
                'display_name': 'Level 2 Endorsement'
            },
            {
                'level': 2000,
                'description': '2,000 MPW',
                'mpw_needed': 2000,
                'display_name': 'Level 3 Endorsement'
            },
        ]

    def get_summary(self) -> str:
        """
        Get award summary text

        Returns:
            str: Human-readable summary of award requirements
        """
        return (
            "SKCC QRP Miles per Watt Award\n"
            "═════════════════════════════\n"
            "Contact SKCC members with QRP power (≤5W) achieving:\n"
            "  • Base Award: 1,000 miles per watt\n"
            "  • Level 2: 1,500 miles per watt\n"
            "  • Level 3: 2,000 miles per watt (and beyond)\n"
            "\n"
            "Requirements:\n"
            "  • QSOs on or after Sept. 1, 2014\n"
            "  • Maximum power: 5 watts for entire QSO\n"
            "  • Both stations must be SKCC members at time of contact\n"
            "  • CW mode with mechanical key only\n"
            "  • Must include distance (N9SSA), site, antenna, and power information"
        )
