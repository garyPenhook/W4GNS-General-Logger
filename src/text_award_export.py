"""
Text-Based Award Application Export

Generates formatted text award applications matching the SKCC award manager format.
This is the format expected by the awards manager (text-based application, not ADIF).

Format based on SKCCLogger examples for proper awards manager acceptance.
"""

import os
import platform
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# QRP points mapping for 1x/2x QRP awards
from src.skcc_awards.qrp_awards import QRP_BAND_POINTS

# Application version for "Created by" line
APP_VERSION = "1.0.0"


class TextAwardExporter:
    """Export award applications as formatted text files"""

    def __init__(self, database):
        """
        Initialize text award exporter

        Args:
            database: Database instance
        """
        self.database = database

    def export_award_application_as_text(
        self,
        award_instance,
        output_directory: str = "exports",
        callsign: Optional[str] = None,
        applicant_name: Optional[str] = None,
        applicant_address: Optional[str] = None,
        user_skcc_number: Optional[str] = None,
        user_dxcc_entity: Optional[int] = None
    ) -> str:
        """
        Export an award application as formatted text.

        Args:
            award_instance: Instance of an SKCC award (e.g., TribuneAward)
            output_directory: Directory to save export files
            callsign: Applicant's callsign (required)
            applicant_name: Applicant's full name
            applicant_address: Applicant's address (city, state format)
            user_skcc_number: Applicant's SKCC number
            user_dxcc_entity: User's DXCC entity code (for DX awards)

        Returns:
            str: Path to exported text file

        Raises:
            ValueError: If no qualifying contacts found or required info missing
            IOError: If file cannot be written
        """
        if not callsign:
            raise ValueError("Callsign is required for award application")

        # Get all contacts from database
        contacts = self._get_all_contacts()

        if not contacts:
            raise ValueError("No contacts found in database")

        # Filter qualifying contacts (allow award-specific selection)
        if hasattr(award_instance, 'get_application_contacts'):
            qualifying = award_instance.get_application_contacts(contacts)
        else:
            qualifying = [c for c in contacts if award_instance.validate(c)]

        if not qualifying:
            raise ValueError(f"No qualifying contacts found for {award_instance.name} award")

        dedupe = True
        if hasattr(award_instance, 'should_deduplicate_for_export'):
            dedupe = award_instance.should_deduplicate_for_export()

        if dedupe:
            # Deduplicate by SKCC number (keep only first QSO with each unique member)
            from src.utils.skcc_number import extract_base_skcc_number

            # Sort by date/time to ensure we keep the first contact with each member
            qualifying.sort(key=lambda x: (x.get('date', ''), x.get('time_on', '')))

            seen_skcc_numbers = set()
            deduplicated = []

            for contact in qualifying:
                skcc_number = contact.get('skcc_number', '').strip()
                if skcc_number:
                    base_number = extract_base_skcc_number(skcc_number)
                    if base_number and base_number not in seen_skcc_numbers:
                        seen_skcc_numbers.add(base_number)
                        deduplicated.append(contact)

            qualifying = deduplicated

        # Normalize callsigns for award submission rules
        if hasattr(award_instance, 'normalize_callsign_for_export'):
            normalized_contacts = []
            for contact in qualifying:
                contact_copy = dict(contact)
                callsign = contact_copy.get('callsign', '')
                normalized = award_instance.normalize_callsign_for_export(callsign)
                if normalized:
                    contact_copy['callsign'] = normalized
                normalized_contacts.append(contact_copy)
            qualifying = normalized_contacts

        # Generate filename based on award and dates
        award_name = award_instance.name.replace(' ', '-')
        submission_date = datetime.now().strftime('%Y-%m-%d')
        filename = f"{callsign} {award_name} Application - {submission_date}.txt"

        os.makedirs(output_directory, exist_ok=True)
        filepath = os.path.join(output_directory, filename)

        # Build and write the application
        try:
            application_text = self._build_application_text(
                award_instance=award_instance,
                contacts=qualifying,
                callsign=callsign,
                applicant_name=applicant_name,
                applicant_address=applicant_address,
                user_skcc_number=user_skcc_number,
                user_dxcc_entity=user_dxcc_entity
            )

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(application_text)

            logger.info(
                f"Exported {len(qualifying)} qualifying contacts for {award_instance.name} "
                f"award application to {filepath}"
            )

            return filepath

        except Exception as e:
            logger.error(f"Failed to export {award_instance.name} award application: {e}")
            raise IOError(f"Failed to write award application to {filepath}: {e}")

    def _build_application_text(
        self,
        award_instance,
        contacts: List[Dict[str, Any]],
        callsign: str,
        applicant_name: Optional[str] = None,
        applicant_address: Optional[str] = None,
        user_skcc_number: Optional[str] = None,
        user_dxcc_entity: Optional[int] = None
    ) -> str:
        """
        Build the formatted award application text matching SKCCLogger format.

        Args:
            award_instance: SKCC award instance
            contacts: List of qualifying contacts
            callsign: Applicant's callsign
            applicant_name: Applicant's name
            applicant_address: Applicant's address
            user_skcc_number: Applicant's SKCC number
            user_dxcc_entity: User's DXCC entity code (for DX awards)

        Returns:
            str: Formatted application text
        """
        lines = []

        # Check if this is a QRP points award
        if award_instance.name in ("1xQRP", "2xQRP"):
            return self._build_qrp_application_text(
                award_instance=award_instance,
                contacts=contacts,
                callsign=callsign,
                applicant_name=applicant_name,
                applicant_address=applicant_address,
                user_skcc_number=user_skcc_number,
                include_their_power=(award_instance.name == "2xQRP")
            )

        if award_instance.name == "QRP MPW":
            return self._build_qrp_mpw_application_text(
                award_instance=award_instance,
                contacts=contacts,
                callsign=callsign,
                applicant_name=applicant_name,
                applicant_address=applicant_address,
                user_skcc_number=user_skcc_number
            )

        # Check if this is a DX award (DXQ or DXC)
        award_name = award_instance.name
        is_dx_award = award_name in ("SKCC DXQ", "SKCC DXC")

        # Get award title from the award instance
        award_title = self._get_award_title(award_instance, len(contacts))

        # Header - must start with exactly 14 spaces to center properly
        lines.append(f"              {award_title}")

        # Created by line - match SKCCLogger format exactly
        lines.append(self._get_created_by_line())
        lines.append("")

        # Applicant info line - format depends on award type
        name_part = f"   Name: {applicant_name}" if applicant_name else "   Name: "
        skcc_part = f"   SKCC#: {user_skcc_number}" if user_skcc_number else "   SKCC#: "

        if is_dx_award:
            # For DX awards, use My DXCC instead of Cent-Date
            dxcc_part = f"   My DXCC: {user_dxcc_entity}" if user_dxcc_entity else "   My DXCC: "
            lines.append(f" Call: {callsign}{name_part}{skcc_part}{dxcc_part}")
        else:
            # For regular awards, use Cent-Date
            centurion_date = ""
            if hasattr(self.database, 'config'):
                cent_date = self.database.config.get('skcc.centurion_date', '')
                if cent_date:
                    # Format YYYYMMDD to YYYY-MM-DD if needed
                    if len(cent_date) == 8:
                        centurion_date = f"{cent_date[:4]}-{cent_date[4:6]}-{cent_date[6:]}"
                    else:
                        centurion_date = cent_date

            cent_part = f"   Cent-Date: {centurion_date}" if centurion_date else ""
            lines.append(f" Call: {callsign}{name_part}{skcc_part}{cent_part}")

        # Address and submission date line
        submission_date = datetime.now().strftime("%Y-%m-%d")
        if applicant_address:
            address_line = f" Address: {applicant_address}"
        else:
            address_line = " Address:"

        # Pad address line to position 44, then add submission date
        address_padded = address_line.ljust(44)
        lines.append(f"{address_padded}Submission Date: {submission_date}")
        lines.append("")

        # Column headers - different for DX awards vs regular awards
        if is_dx_award:
            # DX awards use Country column instead of State
            lines.append("QSO   QSO Date    Callsign    Country         SKCC#   Name            Band")
            lines.append("-" * 74)
        else:
            # Regular awards use State column
            lines.append("QSO   QSO Date    Callsign    SKCC#   Name            State       Band")
            lines.append("-" * 74)

        # Contact records
        for idx, contact in enumerate(contacts, 1):
            if is_dx_award:
                qso_line = self._format_dx_qso_line(idx, contact)
            else:
                qso_line = self._format_qso_line(idx, contact)
            lines.append(qso_line)

        # Certification statement
        lines.append("")
        cert_name = applicant_name if applicant_name else callsign
        lines.append(f"I, {cert_name}, certify that the above contacts were made as stated.")
        lines.append(datetime.now().strftime("%A, %B %d, %Y"))
        lines.append("")
        lines.append("")

        return "\n".join(lines)

    def _build_qrp_mpw_application_text(
        self,
        award_instance,
        contacts: List[Dict[str, Any]],
        callsign: str,
        applicant_name: Optional[str] = None,
        applicant_address: Optional[str] = None,
        user_skcc_number: Optional[str] = None
    ) -> str:
        """Build the formatted QRP MPW application text."""
        lines = []

        award_title = "SKCC QRP Miles-Per-Watt Award/Endorsement Application"
        lines.append(f"              {award_title}")
        lines.append(self._get_created_by_line())
        lines.append("")

        name_part = f"   Name: {applicant_name}" if applicant_name else "   Name: "
        skcc_part = f"   SKCC#: {user_skcc_number}" if user_skcc_number else "   SKCC#: "
        lines.append(f" Call: {callsign}{name_part}{skcc_part}")

        submission_date = datetime.now().strftime("%Y-%m-%d")
        address_line = f" Address: {applicant_address}" if applicant_address else " Address:"
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
        for idx, contact in enumerate(contacts, 1):
            line, mpw = self._format_qrp_mpw_line(idx, contact)
            if mpw is not None:
                best_mpw = max(best_mpw, mpw)
            lines.append(line)

        lines.append("")
        lines.append(f"Best MPW: {best_mpw:.1f}")
        lines.append("")

        cert_name = applicant_name if applicant_name else callsign
        lines.append(f"I, {cert_name}, certify that the above contacts were made as stated.")
        lines.append(datetime.now().strftime("%A, %B %d, %Y"))
        lines.append("")
        lines.append("")

        return "\n".join(lines)

    def _format_qrp_mpw_line(self, qso_number: int, contact: Dict[str, Any]) -> tuple:
        """Format a QRP MPW QSO line."""
        date = contact.get('date', '')
        if date and len(date) == 8 and '-' not in date:
            date = f"{date[:4]}-{date[4:6]}-{date[6:]}"

        time_on = (contact.get('time_on', '') or '').strip()
        callsign = (contact.get('callsign', '') or '').upper().strip()
        skcc_number = (contact.get('skcc_number', '') or '').strip()
        my_skcc = (contact.get('my_skcc_number', '') or '').strip()
        rst_sent = (contact.get('rst_sent', '') or '').strip()
        rst_rcvd = (contact.get('rst_rcvd', '') or '').strip()
        location = (
            contact.get('state')
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

        line = (
            f"{qso_number:<6}{date:<11}{time_on:<6}{callsign:<12}{skcc_number:<8}"
            f"{my_skcc:<8}{rst_sent:<5}{rst_rcvd:<5}{location:<5}"
            f"{distance_str:<6}{mpw_str:<6}{power_str:<5}{band:<6}"
            f"{site:<13}{antenna:<12}"
        )

        return line, mpw

    def _build_qrp_application_text(
        self,
        award_instance,
        contacts: List[Dict[str, Any]],
        callsign: str,
        applicant_name: Optional[str] = None,
        applicant_address: Optional[str] = None,
        user_skcc_number: Optional[str] = None,
        include_their_power: bool = False
    ) -> str:
        """Build the formatted QRP points application text."""
        lines = []

        award_title = f"SKCC {award_instance.name} Award/Endorsement Application"
        lines.append(f"              {award_title}")
        lines.append(self._get_created_by_line())
        lines.append("")

        name_part = f"   Name: {applicant_name}" if applicant_name else "   Name: "
        skcc_part = f"   SKCC#: {user_skcc_number}" if user_skcc_number else "   SKCC#: "
        lines.append(f" Call: {callsign}{name_part}{skcc_part}")

        submission_date = datetime.now().strftime("%Y-%m-%d")
        address_line = f" Address: {applicant_address}" if applicant_address else " Address:"
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
        for idx, contact in enumerate(contacts, 1):
            line, points = self._format_qrp_line(idx, contact, include_their_power=include_their_power)
            if points is not None:
                total_points += points
            lines.append(line)

        lines.append("")
        lines.append(f"Total Points: {total_points:.1f}")
        lines.append("")

        cert_name = applicant_name if applicant_name else callsign
        lines.append(f"I, {cert_name}, certify that the above contacts were made as stated.")
        lines.append(datetime.now().strftime("%A, %B %d, %Y"))
        lines.append("")
        lines.append("")

        return "\n".join(lines)

    def _format_qrp_line(
        self,
        qso_number: int,
        contact: Dict[str, Any],
        include_their_power: bool = False
    ) -> tuple:
        """Format a single QRP points QSO line."""
        date = contact.get('date', '')
        if date and len(date) == 8 and '-' not in date:
            date = f"{date[:4]}-{date[4:6]}-{date[6:]}"

        callsign = (contact.get('callsign', '') or '').upper().strip()
        skcc_number = (contact.get('skcc_number', '') or '').strip()

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
            line = (
                f"{qso_number:<6}{date:<12}{callsign:<12}{skcc_number:<8}"
                f"{name:<16}{power_str:<6}{their_power_str:<7}{band:<6}{points_str:<4}"
            )
        else:
            line = (
                f"{qso_number:<6}{date:<12}{callsign:<12}{skcc_number:<8}"
                f"{name:<16}{power_str:<6}{band:<6}{points_str:<4}"
            )

        return line, points

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

    def _get_created_by_line(self) -> str:
        """
        Generate the "Created by" line matching SKCCLogger format.

        Returns:
            Created by line with app info
        """
        # Get platform info
        system = platform.system()
        arch = platform.machine()

        if system == "Linux":
            platform_str = f"64-bit Linux" if "64" in arch else "32-bit Linux"
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

    def _get_award_title(self, award_instance, contact_count: int) -> str:
        """
        Generate the award title line based on award type and endorsement level.

        Args:
            award_instance: SKCC award instance
            contact_count: Number of qualifying contacts

        Returns:
            str: Award title
        """
        award_name = award_instance.name

        # For Tribune, check for endorsement level
        if award_name == "Tribune" and contact_count >= 50:
            # Calculate endorsement level
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

            # Find the highest endorsement level we've reached
            current_level = "Tribune"
            for threshold in sorted(endorsement_map.keys(), reverse=True):
                if contact_count >= threshold:
                    current_level = endorsement_map[threshold]
                    break

            title = f"SKCC ALL-Band {current_level} Award/Endorsement Application"
        elif award_name == "Centurion":
            title = "SKCC Centurion Award/Endorsement Application"
        elif award_name == "Senator":
            title = "SKCC Senator ALL-Band Award/Endorsement Application"
        elif award_name == "SKCC DXQ":
            title = "SKCC DXQ ALL-Band Award/Endorsement Application"
        elif award_name == "SKCC DXC":
            title = "SKCC DXC ALL-Band Award/Endorsement Application"
        elif award_name == "SKCC WAS":
            title = "SKCC WAS Award/Endorsement Application"
        elif award_name == "SKCC WAS-T":
            title = "SKCC WAS-T Award/Endorsement Application"
        elif award_name == "SKCC WAS-S":
            title = "SKCC WAS-S Award/Endorsement Application"
        elif award_name == "SKCC WAC":
            title = "SKCC WAC Award/Endorsement Application"
        else:
            title = f"SKCC {award_name} Award/Endorsement Application"

        return title

    def _format_qso_line(self, qso_number: int, contact: Dict[str, Any]) -> str:
        """
        Format a single QSO line for regular awards (Centurion, Tribune, Senator, etc.)

        SKCCLogger format:
        QSO   QSO Date    Callsign    SKCC#   Name            State       Band
        1     2025-09-10  VA3ACW/VE1  2813    Stan            ON          40M

        Args:
            qso_number: QSO sequence number (1-based)
            contact: Contact record dictionary

        Returns:
            str: Formatted QSO line matching SKCCLogger format
        """
        # Extract and format fields - convert YYYYMMDD to YYYY-MM-DD if needed
        date = contact.get('date', '')
        if date and len(date) == 8 and '-' not in date:  # YYYYMMDD format
            date = f"{date[:4]}-{date[4:6]}-{date[6:]}"

        callsign = (contact.get('callsign', '') or '').upper().strip()
        skcc_number = (contact.get('skcc_number', '') or '').strip()

        # Get name - truncate to 15 chars for display
        name = (contact.get('name', '') or '').strip()
        if len(name) > 15:
            name = name[:15]

        state = (contact.get('state', '') or '').strip()

        # Format band - ensure it has 'M' suffix (e.g., 40M, 20M)
        band = (contact.get('band', '') or '').strip().upper()
        if band and not band.endswith('M'):
            band = band + 'M'

        # Build line with SKCCLogger column widths
        # Format: QSO   QSO Date    Callsign    SKCC#   Name            State       Band
        line = f"{qso_number:<6}{date:<12}{callsign:<12}{skcc_number:<8}{name:<16}{state:<12}{band}"

        return line

    def _format_dx_qso_line(self, qso_number: int, contact: Dict[str, Any]) -> str:
        """
        Format a single QSO line for DX awards (DXQ, DXC)

        SKCCLogger format:
        QSO   QSO Date    Callsign    Country         SKCC#   Name            Band
        1     2025-09-10  VA3ACW/VE1  Unavailable     2813    Stan            40M

        Args:
            qso_number: QSO sequence number (1-based)
            contact: Contact record dictionary

        Returns:
            str: Formatted QSO line matching SKCCLogger DX format
        """
        # Extract and format fields - convert YYYYMMDD to YYYY-MM-DD if needed
        date = contact.get('date', '')
        if date and len(date) == 8 and '-' not in date:  # YYYYMMDD format
            date = f"{date[:4]}-{date[4:6]}-{date[6:]}"

        callsign = (contact.get('callsign', '') or '').upper().strip()

        # Get country - use "Unavailable" if not set (matching SKCCLogger behavior)
        country = (contact.get('country', '') or '').strip()
        if not country:
            country = "Unavailable"
        # Truncate country to 15 chars for display
        if len(country) > 15:
            country = country[:15]

        skcc_number = (contact.get('skcc_number', '') or '').strip()

        # Get name - truncate to 15 chars for display
        name = (contact.get('name', '') or '').strip()
        if len(name) > 15:
            name = name[:15]

        # Format band - ensure it has 'M' suffix (e.g., 40M, 20M)
        band = (contact.get('band', '') or '').strip().upper()
        if band and not band.endswith('M'):
            band = band + 'M'

        # Build line with SKCCLogger DX column widths
        # Format: QSO   QSO Date    Callsign    Country         SKCC#   Name            Band
        line = f"{qso_number:<6}{date:<12}{callsign:<12}{country:<16}{skcc_number:<8}{name:<16}{band}"

        return line

    def _get_all_contacts(self) -> List[Dict[str, Any]]:
        """
        Get all contacts from the database.

        Returns:
            List of contact dictionaries
        """
        # Check if database has a method to get all contacts
        if hasattr(self.database, 'get_all_contacts'):
            return self.database.get_all_contacts()

        # Otherwise, query directly
        if hasattr(self.database, 'conn'):
            cursor = self.database.conn.cursor()
            cursor.execute("SELECT * FROM contacts")
            rows = cursor.fetchall()

            # Convert Row objects to dictionaries
            contacts = []
            for row in rows:
                contact = {key: row[key] for key in row.keys()}
                contacts.append(contact)

            return contacts

        raise NotImplementedError("Database does not support contact retrieval")

    # Python data model methods for callable protocol
    def __call__(
        self,
        award_instance,
        output_directory: str = "exports",
        callsign: Optional[str] = None,
        applicant_name: Optional[str] = None,
        applicant_address: Optional[str] = None,
        user_skcc_number: Optional[str] = None,
        user_dxcc_entity: Optional[int] = None
    ) -> str:
        """
        Enable callable protocol: exporter(award, ...)

        This is a shorthand for export_award_application_as_text()
        """
        return self.export_award_application_as_text(
            award_instance,
            output_directory,
            callsign,
            applicant_name,
            applicant_address,
            user_skcc_number,
            user_dxcc_entity
        )

    def __repr__(self):
        """Developer-friendly representation"""
        return f"<TextAwardExporter(database={self.database!r})>"


def export_award_application_as_text(
    award_instance,
    database,
    output_directory: str = "exports",
    callsign: Optional[str] = None,
    applicant_name: Optional[str] = None,
    applicant_address: Optional[str] = None,
    user_skcc_number: Optional[str] = None,
    user_dxcc_entity: Optional[int] = None
) -> str:
    """
    Convenience function to export a single award application as text.

    Args:
        award_instance: Instance of an SKCC award
        database: Database instance
        output_directory: Directory to save export file
        callsign: Applicant's callsign (required)
        applicant_name: Applicant's full name
        applicant_address: Applicant's address
        user_skcc_number: Applicant's SKCC number
        user_dxcc_entity: User's DXCC entity code (for DX awards)

    Returns:
        str: Path to exported text file

    Example:
        >>> from src.database import Database
        >>> from src.skcc_awards import TribuneAward
        >>> db = Database('logbook.db')
        >>> award = TribuneAward(db)
        >>> filepath = export_award_application_as_text(
        ...     award, db, callsign='W4GNS',
        ...     applicant_name='Gary Scott',
        ...     applicant_address='Penhook, VA'
        ... )
        >>> print(f"Exported to: {filepath}")
    """
    exporter = TextAwardExporter(database)
    return exporter.export_award_application_as_text(
        award_instance,
        output_directory=output_directory,
        callsign=callsign,
        applicant_name=applicant_name,
        applicant_address=applicant_address,
        user_skcc_number=user_skcc_number,
        user_dxcc_entity=user_dxcc_entity
    )
