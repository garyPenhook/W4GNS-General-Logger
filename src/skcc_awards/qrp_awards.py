"""
SKCC QRP Awards (1xQRP and 2xQRP)

Implements the SKCC QRP points-based awards:
- 1xQRP: Applicant operates QRP (<= 5W) and accumulates 300 points
- 2xQRP: Both stations operate QRP (<= 5W) and accumulate 150 points

Points are awarded by band, with one contact per station per band.
"""

import re
from typing import Dict, List, Any, Tuple

from src.skcc_awards.base import SKCCAwardBase
from src.utils.skcc_number import extract_base_skcc_number
from src.skcc_roster import get_roster_manager

QRP_MAX_POWER = 5.0
QRP_60M_EFFECTIVE_DATE = "20130901"  # 60m counts only on/after Sept 1, 2013

QRP_BAND_POINTS = {
    '160M': 4.0,
    '80M': 3.0,
    '10M': 3.0,
    '60M': 2.0,
    '40M': 2.0,
    '30M': 2.0,
    '20M': 1.0,
    '17M': 1.0,
    '15M': 1.0,
    '12M': 1.0,
    '6M': 0.5,
    '2M': 0.5,
}


class QRPBaseAward(SKCCAwardBase):
    """Shared logic for SKCC QRP awards."""

    REQUIRED_POINTS = 0
    REQUIRE_THEIR_POWER = False

    def __init__(self, database, name: str, program_id: str):
        super().__init__(name=name, program_id=program_id, database=database)
        self.roster_manager = get_roster_manager()
        self.user_join_date = self._get_user_join_date()

    def _get_user_join_date(self) -> str:
        if hasattr(self.database, 'config'):
            return self.database.config.get('skcc.join_date', '')
        return ''

    def should_deduplicate_for_export(self) -> bool:
        """QRP awards allow multiple QSOs with the same member across bands."""
        return False

    def normalize_callsign_for_export(self, callsign: str) -> str:
        return self.roster_manager.normalize_callsign(callsign)

    def _get_qso_date(self, contact: Dict[str, Any]) -> str:
        qso_date = contact.get('qso_date', contact.get('date', '')) or ''
        return qso_date.replace('-', '') if qso_date else ''

    def _normalize_band(self, band: str) -> str:
        if not band:
            return ''
        band = band.strip().upper().replace(' ', '')
        if band.endswith('M'):
            return band
        if band.isdigit():
            return f"{band}M"
        return band

    def _get_power_value(self, value: Any, fallback: Any = None) -> float:
        if value is None or value == '':
            value = fallback
        if value is None or value == '':
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            match = re.search(r'([0-9]+(?:\.[0-9]+)?)', str(value))
            if match:
                try:
                    return float(match.group(1))
                except (TypeError, ValueError):
                    return None
        return None

    def _is_valid_power(self, power: float) -> bool:
        return power is not None and power > 0 and power <= QRP_MAX_POWER

    def _is_band_allowed(self, band: str, qso_date: str) -> bool:
        if band not in QRP_BAND_POINTS:
            return False
        if band == '60M':
            if not qso_date:
                return False
            return qso_date >= QRP_60M_EFFECTIVE_DATE
        return True

    def validate(self, contact: Dict[str, Any]) -> bool:
        """Check if a contact qualifies for this QRP award."""
        if not self.validate_common_rules(contact):
            return False

        qso_date = self._get_qso_date(contact)
        band = self._normalize_band(contact.get('band', ''))

        if not self._is_band_allowed(band, qso_date):
            return False

        callsign = contact.get('callsign', '')
        base_call = self.roster_manager.normalize_callsign(callsign)
        if not base_call:
            return False

        if not self.roster_manager.was_member_on_date(base_call, qso_date):
            return False

        if self.user_join_date and qso_date and qso_date < self.user_join_date:
            return False

        skcc_num = (contact.get('skcc_number', '') or '').strip()
        base_number = extract_base_skcc_number(skcc_num)
        if not base_number or not base_number.isdigit():
            return False

        power = self._get_power_value(contact.get('power_watts'), contact.get('power'))
        if not self._is_valid_power(power):
            return False

        if self.REQUIRE_THEIR_POWER:
            their_power = self._get_power_value(contact.get('their_power_watts'))
            if not self._is_valid_power(their_power):
                return False

        return True

    def _select_unique_contacts(self, contacts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Select unique contacts by callsign + band and calculate points."""
        qualifying = [c for c in contacts if self.validate(c)]
        qualifying.sort(key=lambda x: (self._get_qso_date(x), x.get('time_on', '')))

        seen: set[Tuple[str, str]] = set()
        selected: List[Dict[str, Any]] = []
        duplicate_count = 0
        total_points = 0.0
        points_by_band: Dict[str, float] = {}
        qsos_by_band: Dict[str, int] = {}

        for contact in qualifying:
            band = self._normalize_band(contact.get('band', ''))
            base_call = self.roster_manager.normalize_callsign(contact.get('callsign', ''))
            if not band or not base_call:
                continue

            key = (base_call, band)
            if key in seen:
                duplicate_count += 1
                continue

            seen.add(key)
            points = QRP_BAND_POINTS.get(band)
            if points is None:
                continue

            total_points += points
            points_by_band[band] = points_by_band.get(band, 0.0) + points
            qsos_by_band[band] = qsos_by_band.get(band, 0) + 1

            contact_copy = dict(contact)
            contact_copy['band'] = band
            contact_copy['band_points'] = points
            selected.append(contact_copy)

        return {
            'contacts': selected,
            'total_points': total_points,
            'points_by_band': points_by_band,
            'qsos_by_band': qsos_by_band,
            'duplicates': duplicate_count,
        }

    def get_application_contacts(self, contacts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Return the contacts to include in QRP award applications."""
        return self._select_unique_contacts(contacts)['contacts']

    def calculate_progress(self, contacts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate current progress toward this QRP award."""
        result = self._select_unique_contacts(contacts)
        total_points = result['total_points']
        required_points = self.REQUIRED_POINTS

        progress_pct = 0.0
        if required_points:
            progress_pct = min(100.0, (total_points / required_points) * 100)

        return {
            'current_points': total_points,
            'required_points': required_points,
            'achieved': total_points >= required_points,
            'progress_pct': progress_pct,
            'points_by_band': result['points_by_band'],
            'qsos_by_band': result['qsos_by_band'],
            'unique_contacts': len(result['contacts']),
            'duplicate_contacts': result['duplicates'],
            'contact_details': result['contacts'],
        }

    def get_requirements(self) -> Dict[str, Any]:
        """Return QRP award requirements."""
        return {
            'name': f"SKCC {self.name}",
            'description': 'Accumulate QRP points by band (one contact per station per band)',
            'base_requirement': self.REQUIRED_POINTS,
            'base_units': 'points',
            'max_power_watts': QRP_MAX_POWER,
            'modes': ['CW'],
            'bands': sorted(QRP_BAND_POINTS.keys()),
            'mechanical_key': True,
            'key_types': ['STRAIGHT', 'BUG', 'SIDESWIPER'],
            'special_rules': [
                'Only one contact per station per band counts',
                '60m contacts count only on/after Sept 1, 2013',
                'Both operators must be SKCC members at time of contact',
            ],
            'endorsements_available': False,
        }

    def get_endorsements(self) -> List[Dict[str, Any]]:
        return [
            {'level': self.REQUIRED_POINTS, 'description': self.name, 'points_needed': self.REQUIRED_POINTS}
        ]

    def export_qualifying_contacts_to_adif(
        self,
        contacts: List[Dict[str, Any]],
        filename: str,
        include_award_info: bool = True
    ) -> int:
        """Export QRP award contacts with per-band deduplication."""
        qualifying = self.get_application_contacts(contacts)

        if not qualifying:
            raise ValueError(f"No qualifying contacts found for {self.name} award")

        if include_award_info:
            for contact in qualifying:
                existing_comment = contact.get('comment', contact.get('comments', ''))
                award_note = f"[{self.name} Award]"
                if existing_comment:
                    if award_note not in existing_comment:
                        contact['comment'] = f"{existing_comment} {award_note}"
                else:
                    contact['comment'] = award_note

        normalized_contacts = []
        for contact in qualifying:
            contact_copy = dict(contact)
            callsign = contact_copy.get('callsign', '')
            normalized = self.normalize_callsign_for_export(callsign)
            if normalized:
                contact_copy['callsign'] = normalized
            normalized_contacts.append(contact_copy)

        from src.adif import export_contacts_to_adif

        try:
            export_contacts_to_adif(
                normalized_contacts,
                filename,
                program_name=f"W4GNS General Logger - {self.name} Award"
            )
            return len(normalized_contacts)
        except Exception as e:
            raise IOError(f"Failed to export {self.name} award contacts: {e}")


class QRP1xAward(QRPBaseAward):
    """SKCC 1xQRP Award - applicant operates QRP and earns 300 points."""

    REQUIRED_POINTS = 300
    REQUIRE_THEIR_POWER = False

    def __init__(self, database):
        super().__init__(database, name="1xQRP", program_id="SKCC_QRP_1X")


class QRP2xAward(QRPBaseAward):
    """SKCC 2xQRP Award - both stations operate QRP and earn 150 points."""

    REQUIRED_POINTS = 150
    REQUIRE_THEIR_POWER = True

    def __init__(self, database):
        super().__init__(database, name="2xQRP", program_id="SKCC_QRP_2X")
