"""
SKCC Award Application Report Generator

Generates award application reports compatible with SKCCLogger format
for submission to SKCC awards managers.

Supported awards:
- Core: Centurion, Tribune, Senator
- Specialty: Triple Key, Rag Chew, Marathon, QRP/MPW, Canadian Maple, PFX
- Specialty: 1xQRP, 2xQRP
- Geography: DXQ, DXC, WAS, WAS-T, WAS-S, WAC
"""

import platform
from datetime import datetime
from typing import List, Dict, Any, Optional

from src.skcc_roster import SKCCRosterManager
from src.skcc_awards.qrp_awards import QRP_BAND_POINTS

# Application version
APP_VERSION = "1.0.0"


class AwardApplicationGenerator:
    """Generates SKCC award application reports in SKCCLogger-compatible format"""

    def __init__(self, database, config):
        """
        Initialize award application generator

        Args:
            database: Database instance
            config: Configuration instance
        """
        self.database = database
        self.config = config

    def generate_centurion_report(self, contacts: List[Dict[str, Any]]) -> str:
        """Generate Centurion award application report"""
        return self._generate_standard_report(
            award_name="Centurion",
            contacts=contacts,
            include_cent_date=True
        )

    def generate_tribune_report(self, contacts: List[Dict[str, Any]]) -> str:
        """Generate Tribune award application report"""
        # Calculate endorsement level
        endorsement = self._get_tribune_endorsement(len(contacts))
        return self._generate_standard_report(
            award_name=f"ALL-Band {endorsement}",
            contacts=contacts,
            include_cent_date=True,
            normalize_callsign=True
        )

    def generate_senator_report(self, contacts: List[Dict[str, Any]]) -> str:
        """Generate Senator award application report"""
        return self._generate_standard_report(
            award_name="Senator ALL-Band",
            contacts=contacts,
            include_trib_date=True,
            normalize_callsign=True
        )

    def generate_dxq_report(self, contacts: List[Dict[str, Any]]) -> str:
        """Generate DXQ award application report"""
        return self._generate_dx_report(
            award_name="DXQ ALL-Band",
            contacts=contacts
        )

    def generate_dxc_report(self, contacts: List[Dict[str, Any]]) -> str:
        """Generate DXC award application report"""
        return self._generate_dx_report(
            award_name="DXC ALL-Band",
            contacts=contacts
        )

    def generate_was_report(self, contacts: List[Dict[str, Any]]) -> str:
        """Generate WAS award application report"""
        return self._generate_standard_report(
            award_name="WAS",
            contacts=contacts,
            include_cent_date=False
        )

    def generate_was_t_report(self, contacts: List[Dict[str, Any]]) -> str:
        """Generate WAS-T award application report"""
        return self._generate_standard_report(
            award_name="WAS-T",
            contacts=contacts,
            include_cent_date=True
        )

    def generate_was_s_report(self, contacts: List[Dict[str, Any]]) -> str:
        """Generate WAS-S award application report"""
        return self._generate_standard_report(
            award_name="WAS-S",
            contacts=contacts,
            include_trib_date=True
        )

    def generate_wac_report(self, contacts: List[Dict[str, Any]]) -> str:
        """Generate WAC award application report"""
        return self._generate_standard_report(
            award_name="WAC",
            contacts=contacts,
            include_cent_date=False
        )

    def generate_triple_key_report(self, contacts: List[Dict[str, Any]]) -> str:
        """Generate Triple Key award application report"""
        return self._generate_standard_report(
            award_name="Triple Key",
            contacts=contacts,
            include_key_type=True
        )

    def generate_rag_chew_report(self, contacts: List[Dict[str, Any]]) -> str:
        """Generate Rag Chew award application report"""
        return self._generate_standard_report(
            award_name="Rag Chew",
            contacts=contacts,
            include_duration=True
        )

    def generate_marathon_report(self, contacts: List[Dict[str, Any]]) -> str:
        """Generate Marathon award application report"""
        return self._generate_standard_report(
            award_name="Marathon",
            contacts=contacts,
            include_duration=True
        )

    def generate_pfx_report(self, contacts: List[Dict[str, Any]]) -> str:
        """Generate PFX award application report"""
        return self._generate_standard_report(
            award_name="PFX",
            contacts=contacts,
            include_cent_date=False
        )

    def generate_canadian_maple_report(self, contacts: List[Dict[str, Any]]) -> str:
        """Generate Canadian Maple award application report"""
        return self._generate_standard_report(
            award_name="Canadian Maple",
            contacts=contacts,
            include_cent_date=False
        )

    def generate_qrp_mpw_report(self, contacts: List[Dict[str, Any]]) -> str:
        """Generate QRP/MPW award application report"""
        return self._generate_qrp_mpw_report(contacts)

    def generate_qrp_1x_report(self, contacts: List[Dict[str, Any]]) -> str:
        """Generate 1xQRP award application report"""
        return self._generate_qrp_points_report(
            award_name="1xQRP",
            contacts=contacts,
            include_their_power=False
        )

    def generate_qrp_2x_report(self, contacts: List[Dict[str, Any]]) -> str:
        """Generate 2xQRP award application report"""
        return self._generate_qrp_points_report(
            award_name="2xQRP",
            contacts=contacts,
            include_their_power=True
        )

    def _get_tribune_endorsement(self, contact_count: int) -> str:
        """Get Tribune endorsement level based on contact count"""
        endorsement_map = {
            50: "Tribune",
            100: "Tribune x2",
            150: "Tribune x3",
            200: "Tribune x4",
            250: "Tribune x5",
            300: "Tribune x6",
            350: "Tribune x7",
            400: "Tribune x8",
            450: "Tribune x9",
            500: "Tribune x10",
            750: "Tribune x15",
            1000: "Tribune x20",
            1250: "Tribune x25",
            1500: "Tribune x30",
        }
        current_level = "Tribune"
        for threshold in sorted(endorsement_map.keys(), reverse=True):
            if contact_count >= threshold:
                current_level = endorsement_map[threshold]
                break
        return current_level

    def _generate_standard_report(
        self,
        award_name: str,
        contacts: List[Dict[str, Any]],
        include_cent_date: bool = False,
        include_trib_date: bool = False,
        include_key_type: bool = False,
        include_duration: bool = False,
        include_power: bool = False,
        normalize_callsign: bool = False
    ) -> str:
        """
        Generate standard award application report

        Args:
            award_name: Name of the award
            contacts: List of qualifying contacts
            include_cent_date: Include Centurion date in header
            include_trib_date: Include Tribune date in header
            include_key_type: Include key type column
            include_duration: Include duration column
            include_power: Include power column

        Returns:
            Formatted report string
        """
        lines = []

        # Header
        lines.append(f"              SKCC {award_name} Award/Endorsement Application")
        lines.append(self._get_created_by_line())
        lines.append("")

        # Operator information
        callsign = self.config.get('callsign', 'UNKNOWN')
        name = self.config.get('operator_name', '')
        skcc_number = self.config.get('skcc.my_number', '')
        address = self.config.get('address', '')

        submission_date = datetime.now().strftime("%Y-%m-%d")

        # Build operator info line
        info_parts = [f"Call: {callsign}"]
        info_parts.append(f"Name: {name}" if name else "Name: ")
        info_parts.append(f"SKCC#: {skcc_number}")

        if include_cent_date:
            cent_date = self.config.get('skcc.centurion_date', '')
            if cent_date and len(cent_date) == 8:
                cent_date = f"{cent_date[:4]}-{cent_date[4:6]}-{cent_date[6:]}"
            info_parts.append(f"Cent-Date: {cent_date}" if cent_date else "Cent-Date: ")

        if include_trib_date:
            trib_date = self.config.get('skcc.tribune_x8_date', '')
            if trib_date and len(trib_date) == 8:
                trib_date = f"{trib_date[:4]}-{trib_date[4:6]}-{trib_date[6:]}"
            info_parts.append(f"Trib-Date: {trib_date}" if trib_date else "Trib-Date: ")

        lines.append(" " + "   ".join(info_parts))

        # Address line
        address_line = f" Address: {address}" if address else " Address:"
        address_padded = address_line.ljust(44)
        lines.append(f"{address_padded}Submission Date: {submission_date}")
        lines.append("")

        # Table header - varies by award type
        if include_key_type:
            lines.append("QSO   QSO Date    Callsign    SKCC#   Name            Key Type    Band")
        elif include_duration:
            lines.append("QSO   QSO Date    Callsign    SKCC#   Name            Duration    Band")
        elif include_power:
            lines.append("QSO   QSO Date    Callsign    SKCC#   Name            Power  MPW  Band")
        else:
            lines.append("QSO   QSO Date    Callsign    SKCC#   Name            State       Band")
        lines.append("-" * 74)

        # Contact rows
        for i, contact in enumerate(contacts, 1):
            row = self._format_standard_row(
                i, contact,
                include_key_type=include_key_type,
                include_duration=include_duration,
                include_power=include_power,
                normalize_callsign=normalize_callsign
            )
            lines.append(row)

        lines.append("")

        # Certification statement
        cert_name = name if name else callsign
        lines.append(f"I, {cert_name}, certify that the above contacts were made as stated.")
        lines.append(datetime.now().strftime("%A, %B %d, %Y"))
        lines.append("")
        lines.append("")

        return "\n".join(lines)

    def _generate_qrp_points_report(
        self,
        award_name: str,
        contacts: List[Dict[str, Any]],
        include_their_power: bool = False
    ) -> str:
        """Generate QRP points award report (1xQRP/2xQRP)."""
        lines = []

        lines.append(f"              SKCC {award_name} Award/Endorsement Application")
        lines.append(self._get_created_by_line())
        lines.append("")

        callsign = self.config.get('callsign', 'UNKNOWN')
        name = self.config.get('operator_name', '')
        skcc_number = self.config.get('skcc.my_number', '')
        address = self.config.get('address', '')
        submission_date = datetime.now().strftime("%Y-%m-%d")

        info_parts = [f"Call: {callsign}"]
        info_parts.append(f"Name: {name}" if name else "Name: ")
        info_parts.append(f"SKCC#: {skcc_number}")
        lines.append(" " + "   ".join(info_parts))

        address_line = f" Address: {address}" if address else " Address:"
        address_padded = address_line.ljust(44)
        lines.append(f"{address_padded}Submission Date: {submission_date}")
        lines.append("")

        if include_their_power:
            lines.append("QSO   QSO Date    Callsign    SKCC#   Name            Pwr   Their  Band  Pts")
            lines.append("-" * 78)
        else:
            lines.append("QSO   QSO Date    Callsign    SKCC#   Name            Pwr   Band  Pts")
            lines.append("-" * 72)

        total_points = 0.0
        for i, contact in enumerate(contacts, 1):
            row, points = self._format_qrp_row(i, contact, include_their_power=include_their_power)
            if points is not None:
                total_points += points
            lines.append(row)

        lines.append("")
        lines.append(f"Total Points: {total_points:.1f}")
        lines.append("")

        cert_name = name if name else callsign
        lines.append(f"I, {cert_name}, certify that the above contacts were made as stated.")
        lines.append(datetime.now().strftime("%A, %B %d, %Y"))
        lines.append("")
        lines.append("")

        return "\n".join(lines)

    def _generate_qrp_mpw_report(self, contacts: List[Dict[str, Any]]) -> str:
        """Generate QRP MPW award application report with required fields."""
        lines = []

        lines.append("              SKCC QRP Miles-Per-Watt Award/Endorsement Application")
        lines.append(self._get_created_by_line())
        lines.append("")

        callsign = self.config.get('callsign', 'UNKNOWN')
        name = self.config.get('operator_name', '')
        skcc_number = self.config.get('skcc.my_number', '')
        address = self.config.get('address', '')
        submission_date = datetime.now().strftime("%Y-%m-%d")

        info_parts = [f"Call: {callsign}"]
        info_parts.append(f"Name: {name}" if name else "Name: ")
        info_parts.append(f"SKCC#: {skcc_number}")
        lines.append(" " + "   ".join(info_parts))

        address_line = f" Address: {address}" if address else " Address:"
        address_padded = address_line.ljust(44)
        lines.append(f"{address_padded}Submission Date: {submission_date}")

        distance_source = ''
        if contacts:
            distance_source = (contacts[0].get('distance_source') or '').strip()
        if distance_source:
            lines.append(f" Distance Source: {distance_source}")

        lines.append("")
        lines.append("QSO   Date       Time  Callsign    SKCC#   My#     RSTs RSTr Loc  Dist  MPW   Pwr  Band  Site         Antenna")
        lines.append("-" * 110)

        best_mpw = 0.0
        for i, contact in enumerate(contacts, 1):
            row, mpw = self._format_qrp_mpw_row(i, contact)
            if mpw is not None:
                best_mpw = max(best_mpw, mpw)
            lines.append(row)

        lines.append("")
        lines.append(f"Best MPW: {best_mpw:.1f}")
        lines.append("")

        cert_name = name if name else callsign
        lines.append(f"I, {cert_name}, certify that the above contacts were made as stated.")
        lines.append(datetime.now().strftime("%A, %B %d, %Y"))
        lines.append("")
        lines.append("")

        return "\n".join(lines)

    def _format_qrp_mpw_row(self, qso_num: int, contact: Dict[str, Any]) -> tuple:
        """Format a QRP MPW QSO row."""
        qso_date = contact.get('date', '')
        if qso_date and '-' not in qso_date and len(qso_date) == 8:
            qso_date = f"{qso_date[:4]}-{qso_date[4:6]}-{qso_date[6:]}"

        time_on = (contact.get('time_on', '') or '').strip()
        callsign = (contact.get('callsign', '') or '').upper().strip()
        skcc_num = (contact.get('skcc_number', '') or '').strip()
        my_skcc = (contact.get('my_skcc_number', '') or '').strip()
        rst_sent = (contact.get('rst_sent', '') or '').strip()
        rst_rcvd = (contact.get('rst_rcvd', '') or '').strip()
        location = (
            contact.get('location')
            or contact.get('state')
            or contact.get('country')
            or contact.get('qth')
            or ''
        ).strip().upper()

        distance = contact.get('distance_miles', '')
        power = contact.get('power_watts', '') or contact.get('power', '')
        band = (contact.get('band', '') or '').strip().upper()
        site = (contact.get('site', '') or '').strip()
        antenna = (contact.get('antenna', '') or '').strip()

        distance_str = self._format_numeric_value(distance)
        power_str = self._format_numeric_value(power)

        mpw = None
        if distance_str and power_str:
            try:
                mpw = float(distance) / float(power)
            except (TypeError, ValueError, ZeroDivisionError):
                mpw = None

        mpw_str = self._format_numeric_value(mpw) if mpw is not None else ''

        if len(site) > 12:
            site = site[:12]
        if len(antenna) > 12:
            antenna = antenna[:12]

        row = (
            f"{qso_num:<6}{qso_date:<11}{time_on:<6}{callsign:<12}{skcc_num:<8}"
            f"{my_skcc:<8}{rst_sent:<5}{rst_rcvd:<5}{location:<5}"
            f"{distance_str:<6}{mpw_str:<6}{power_str:<5}{band:<6}"
            f"{site:<13}{antenna:<12}"
        )

        return row, mpw

    def _format_qrp_row(
        self,
        qso_num: int,
        contact: Dict[str, Any],
        include_their_power: bool = False
    ) -> tuple:
        """Format a QRP points QSO row."""
        qso_date = contact.get('date', '')
        if qso_date and '-' not in qso_date and len(qso_date) == 8:
            qso_date = f"{qso_date[:4]}-{qso_date[4:6]}-{qso_date[6:]}"

        callsign = (contact.get('callsign', '') or '').upper().strip()
        skcc_num = (contact.get('skcc_number', '') or '').strip()

        name = (contact.get('name', '') or '').strip()
        if len(name) > 15:
            name = name[:15]

        band = (contact.get('band', '') or '').strip().upper().replace(' ', '')
        if band and not band.endswith('M') and band.isdigit():
            band = band + 'M'

        points = contact.get('band_points')
        if points is None:
            points = QRP_BAND_POINTS.get(band)

        points_str = ""
        if points is not None:
            points_str = f"{points:.1f}" if points % 1 else f"{int(points)}"

        power = contact.get('power_watts', '') or contact.get('power', '')
        power_str = self._format_numeric_value(power)

        if include_their_power:
            their_power = contact.get('their_power_watts', '') or ''
            their_power_str = self._format_numeric_value(their_power)
            row = (
                f"{qso_num:<6}{qso_date:<12}{callsign:<12}{skcc_num:<8}"
                f"{name:<16}{power_str:<6}{their_power_str:<7}{band:<6}{points_str:<4}"
            )
        else:
            row = (
                f"{qso_num:<6}{qso_date:<12}{callsign:<12}{skcc_num:<8}"
                f"{name:<16}{power_str:<6}{band:<6}{points_str:<4}"
            )

        return row, points

    def _format_numeric_value(self, value: Any) -> str:
        """Format numeric values without forcing trailing .0."""
        if value is None or value == '':
            return ''
        try:
            num = float(value)
        except (TypeError, ValueError):
            return str(value).strip()
        if num % 1:
            return f"{num:.1f}"
        return f"{int(num)}"

    def _generate_dx_report(
        self,
        award_name: str,
        contacts: List[Dict[str, Any]]
    ) -> str:
        """
        Generate DX award application report (DXQ/DXC)

        Args:
            award_name: Name of the award (DXQ/DXC)
            contacts: List of qualifying contacts

        Returns:
            Formatted report string
        """
        lines = []

        # Header
        lines.append(f"              SKCC {award_name} Award/Endorsement Application")
        lines.append(self._get_created_by_line())
        lines.append("")

        # Operator information
        callsign = self.config.get('callsign', 'UNKNOWN')
        name = self.config.get('operator_name', '')
        skcc_number = self.config.get('skcc.my_number', '')
        address = self.config.get('address', '')
        my_dxcc = self.config.get('dxcc_entity', '')

        submission_date = datetime.now().strftime("%Y-%m-%d")

        # Build operator info line with My DXCC
        info_parts = [
            f"Call: {callsign}",
            f"Name: {name}" if name else "Name: ",
            f"SKCC#: {skcc_number}",
            f"My DXCC: {my_dxcc}"
        ]
        lines.append(" " + "   ".join(info_parts))

        # Address line
        address_line = f" Address: {address}" if address else " Address:"
        address_padded = address_line.ljust(44)
        lines.append(f"{address_padded}Submission Date: {submission_date}")
        lines.append("")

        # Table header for DX awards
        lines.append("QSO   QSO Date    Callsign    Country         SKCC#   Name            Band")
        lines.append("-" * 74)

        # Contact rows
        for i, contact in enumerate(contacts, 1):
            row = self._format_dx_row(i, contact)
            lines.append(row)

        lines.append("")

        # Certification statement
        cert_name = name if name else callsign
        lines.append(f"I, {cert_name}, certify that the above contacts were made as stated.")
        lines.append(datetime.now().strftime("%A, %B %d, %Y"))
        lines.append("")
        lines.append("")

        return "\n".join(lines)

    def _format_standard_row(
        self,
        qso_num: int,
        contact: Dict[str, Any],
        include_key_type: bool = False,
        include_duration: bool = False,
        include_power: bool = False,
        normalize_callsign: bool = False
    ) -> str:
        """Format a standard QSO row"""
        qso_date = contact.get('date', '')
        if qso_date and '-' not in qso_date and len(qso_date) == 8:
            qso_date = f"{qso_date[:4]}-{qso_date[4:6]}-{qso_date[6:]}"

        callsign = (contact.get('callsign', '') or '').upper().strip()
        if normalize_callsign:
            callsign = SKCCRosterManager.normalize_callsign(callsign)
        skcc_num = (contact.get('skcc_number', '') or '').strip()

        name = (contact.get('name', '') or '').strip()
        if len(name) > 15:
            name = name[:15]

        band = (contact.get('band', '') or '').strip().upper()
        if band and not band.endswith('M'):
            band = band + 'M'

        if include_key_type:
            key_type = (contact.get('key_type', '') or '').strip()
            return f"{qso_num:<6}{qso_date:<12}{callsign:<12}{skcc_num:<8}{name:<16}{key_type:<12}{band}"
        elif include_duration:
            duration = contact.get('duration_minutes', 0) or 0
            return f"{qso_num:<6}{qso_date:<12}{callsign:<12}{skcc_num:<8}{name:<16}{duration:<12}{band}"
        elif include_power:
            power = contact.get('power_watts', '') or ''
            mpw = contact.get('miles_per_watt', '') or ''
            return f"{qso_num:<6}{qso_date:<12}{callsign:<12}{skcc_num:<8}{name:<16}{power:<7}{mpw:<5}{band}"
        else:
            state = (contact.get('state', '') or '').strip()
            return f"{qso_num:<6}{qso_date:<12}{callsign:<12}{skcc_num:<8}{name:<16}{state:<12}{band}"

    def _format_dx_row(self, qso_num: int, contact: Dict[str, Any]) -> str:
        """Format a DX QSO row with Country column"""
        qso_date = contact.get('date', '')
        if qso_date and '-' not in qso_date and len(qso_date) == 8:
            qso_date = f"{qso_date[:4]}-{qso_date[4:6]}-{qso_date[6:]}"

        callsign = (contact.get('callsign', '') or '').upper().strip()

        country = (contact.get('country', '') or '').strip()
        if not country:
            country = "Unavailable"
        if len(country) > 15:
            country = country[:15]

        skcc_num = (contact.get('skcc_number', '') or '').strip()

        name = (contact.get('name', '') or '').strip()
        if len(name) > 15:
            name = name[:15]

        band = (contact.get('band', '') or '').strip().upper()
        if band and not band.endswith('M'):
            band = band + 'M'

        return f"{qso_num:<6}{qso_date:<12}{callsign:<12}{country:<16}{skcc_num:<8}{name:<16}{band}"

    def _get_created_by_line(self) -> str:
        """
        Generate the "Created by" line matching SKCCLogger format

        Returns:
            Created by line with app info
        """
        # Get platform info
        system = platform.system()
        arch = platform.machine()

        if system == "Linux":
            platform_str = "64-bit Linux" if "64" in arch else "32-bit Linux"
        elif system == "Darwin":
            platform_str = "64-bit macOS" if "64" in arch else "macOS"
        elif system == "Windows":
            platform_str = "64-bit Windows" if "64" in arch else "32-bit Windows"
        else:
            platform_str = system

        # Get current timestamp
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d at %H:%M:%S")

        # Determine timezone abbreviation
        # Use tm_isdst > 0 to select DST abbreviation, else standard
        try:
            import time
            tz_index = 1 if time.localtime().tm_isdst > 0 else 0
            tz_abbr = time.tzname[tz_index]
        except Exception:
            tz_abbr = "ET"

        return f"Created by W4GNS-General-Logger v{APP_VERSION} {platform_str} Build {timestamp} {tz_abbr}"

    def save_report_to_file(self, report: str, filename: str) -> bool:
        """
        Save report to a text file

        Args:
            report: Report text
            filename: Output filename

        Returns:
            True if successful
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report)
            return True
        except Exception as e:
            print(f"Error saving report: {e}")
            return False
