"""
Text-Based Award Application Export

Generates formatted text award applications matching the SKCC award manager format.
This is the format expected by the awards manager (text-based application, not ADIF).

Format based on example: "W4GNS ALL-Band x2 Tribune App - 2025-11-09.txt"
"""

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


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
        user_skcc_number: Optional[str] = None
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
                user_skcc_number=user_skcc_number
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
        user_skcc_number: Optional[str] = None
    ) -> str:
        """
        Build the formatted award application text.

        Args:
            award_instance: SKCC award instance
            contacts: List of qualifying contacts
            callsign: Applicant's callsign
            applicant_name: Applicant's name
            applicant_address: Applicant's address
            user_skcc_number: Applicant's SKCC number

        Returns:
            str: Formatted application text
        """
        lines = []

        # Get award title from the award instance
        award_title = self._get_award_title(award_instance, len(contacts))

        # Header - must start with exactly 10 spaces
        lines.append(f"          {award_title}")

        # Created by line
        app_version = "W4GNS General Logger"
        build_date = datetime.now().strftime("%Y-%m-%d at %H:%M:%S")
        lines.append(f"Created by {app_version} {build_date}")
        lines.append("")

        # Applicant info line - starts with 1 space
        name_part = f"   Name: {applicant_name}" if applicant_name else ""
        skcc_part = f"   SKCC#: {user_skcc_number}" if user_skcc_number else ""

        # Try to get Centurion date from config
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

        # Address and submission date line - starts with 1 space
        # Format: " Address: <address>" padded to position 43 with spaces, then "Submission Date: <date>"
        submission_date = datetime.now().strftime("%Y-%m-%d")
        if applicant_address:
            address_line = f" Address: {applicant_address}"
        else:
            address_line = " Address:"

        # Pad address line to 43 characters, then add submission date
        address_padded = address_line.ljust(43)
        lines.append(f"{address_padded}Submission Date: {submission_date}")
        lines.append("")

        # Column headers - exact format from example
        lines.append("QSO#   QSO Date     Callsign      SKCC#    Name         State        Band")
        lines.append("-" * 78)

        # Contact records
        for idx, contact in enumerate(contacts, 1):
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

            title = f"SKCC {current_level} Award/Endorsement Application"
        elif award_name == "Centurion":
            title = "SKCC Centurion Award/Endorsement Application"
        elif award_name == "Senator":
            title = "SKCC Senator Award/Endorsement Application"
        else:
            title = f"SKCC {award_name} Award/Endorsement Application"

        return title

    def _format_qso_line(self, qso_number: int, contact: Dict[str, Any]) -> str:
        """
        Format a single QSO line for the application table.

        Column positions (must be exact):
        - QSO#: 0-6 (7 chars, right-aligned)
        - QSO Date: 7-19 (13 chars)
        - Callsign: 20-33 (14 chars)
        - SKCC#: 34-42 (9 chars)
        - Name: 43-55 (13 chars)
        - State: 56-68 (13 chars)
        - Band: 69+ (variable)

        Args:
            qso_number: QSO sequence number (1-based)
            contact: Contact record dictionary

        Returns:
            str: Formatted QSO line with exact column positions
        """
        # Extract and format fields
        date = contact.get('date', '')
        if date and len(date) == 10 and date[4] == '-':  # YYYY-MM-DD format
            date = date  # Keep as-is
        elif date and len(date) == 8:  # YYYYMMDD format
            date = f"{date[:4]}-{date[4:6]}-{date[6:]}"

        callsign = (contact.get('callsign', '') or '').upper().strip()
        skcc_number = (contact.get('skcc_number', '') or '').strip()
        name = (contact.get('name', '') or '').strip()
        state = (contact.get('state', '') or '').strip()
        band = (contact.get('band', '') or '').strip()

        # Build line with exact column positions
        # Start with QSO# right-aligned in first 7 chars
        line = f"{qso_number:<7}"  # positions 0-6

        # QSO Date in positions 7-19 (13 chars)
        line += f"{date:<13}"

        # Callsign in positions 20-33 (14 chars)
        line += f"{callsign:<14}"

        # SKCC# in positions 34-42 (9 chars)
        line += f"{skcc_number:<9}"

        # Name in positions 43-55 (13 chars)
        line += f"{name:<13}"

        # State in positions 56-68 (13 chars)
        line += f"{state:<13}"

        # Band starting at position 69
        line += band

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
        user_skcc_number: Optional[str] = None
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
            user_skcc_number
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
    user_skcc_number: Optional[str] = None
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
        user_skcc_number=user_skcc_number
    )
