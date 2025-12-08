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

        # Filter qualifying contacts
        qualifying = [c for c in contacts if award_instance.validate(c)]

        if not qualifying:
            raise ValueError(f"No qualifying contacts found for {award_instance.name} award")

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
            dxcc_part = f"   My DXCC: {user_dxcc_entity}" if user_dxcc_entity else "   My DXCC: 291"
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
        # Try to get local timezone, default to ET
        try:
            import time
            if time.daylight:
                tz_abbr = time.tzname[time.localtime().tm_isdst]
            else:
                tz_abbr = time.tzname[0]
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
        # Extract and format fields
        date = contact.get('date', '')
        if date and len(date) == 10 and date[4] == '-':  # YYYY-MM-DD format
            date = date  # Keep as-is
        elif date and len(date) == 8:  # YYYYMMDD format
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
        # Extract and format fields
        date = contact.get('date', '')
        if date and len(date) == 10 and date[4] == '-':  # YYYY-MM-DD format
            date = date  # Keep as-is
        elif date and len(date) == 8:  # YYYYMMDD format
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
