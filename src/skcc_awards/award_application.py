"""
SKCC Award Application Report Generator

Generates award application reports compatible with SKCCLogger format
for submission to SKCC awards managers.
"""

import platform
from datetime import datetime
from typing import List, Dict, Any, Optional


class AwardApplicationGenerator:
    """Generates SKCC award application reports"""

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
        """
        Generate Centurion award application report

        Args:
            contacts: List of qualifying contacts

        Returns:
            Formatted report string
        """
        return self._generate_report(
            award_name="Centurion",
            contacts=contacts,
            date_field_name="Cent-Date"
        )

    def generate_tribune_report(self, contacts: List[Dict[str, Any]]) -> str:
        """
        Generate Tribune award application report

        Args:
            contacts: List of qualifying contacts

        Returns:
            Formatted report string
        """
        return self._generate_report(
            award_name="Tribune ALL-Band",
            contacts=contacts,
            date_field_name="Cent-Date"
        )

    def generate_senator_report(self, contacts: List[Dict[str, Any]]) -> str:
        """
        Generate Senator award application report

        Args:
            contacts: List of qualifying contacts

        Returns:
            Formatted report string
        """
        return self._generate_report(
            award_name="Senator ALL-Band",
            contacts=contacts,
            date_field_name="Trib-Date"
        )

    def _generate_report(
        self,
        award_name: str,
        contacts: List[Dict[str, Any]],
        date_field_name: str
    ) -> str:
        """
        Generate award application report

        Args:
            award_name: Name of the award (e.g., "Centurion", "Tribune ALL-Band")
            contacts: List of qualifying contacts
            date_field_name: Name of the date field (e.g., "Cent-Date", "Trib-Date")

        Returns:
            Formatted report string
        """
        lines = []

        # Header
        lines.append(f"            SKCC {award_name} Award/Endorsement Application")
        lines.append(self._get_created_by_line())
        lines.append("")

        # Operator information
        callsign = self.config.get('callsign', 'UNKNOWN')
        name = self.config.get('operator_name', '')
        skcc_number = self.config.get('skcc.my_number', '')
        address = self.config.get('address', '')

        # Get achievement date
        if date_field_name == "Cent-Date":
            achievement_date = self.config.get('skcc.centurion_date', '')
        else:
            achievement_date = self.config.get('skcc.tribune_date', '')

        # Format achievement date from YYYYMMDD to YYYY-MM-DD
        if achievement_date and len(achievement_date) == 8:
            achievement_date = f"{achievement_date[:4]}-{achievement_date[4:6]}-{achievement_date[6:]}"

        submission_date = datetime.now().strftime("%Y-%m-%d")

        # Operator info line
        info_parts = [
            f"Call: {callsign}",
            f"Name: {name}" if name else "Name: ",
            f"SKCC#: {skcc_number}",
            f"{date_field_name}: {achievement_date}" if achievement_date else f"{date_field_name}: "
        ]
        lines.append(" " + "   ".join(info_parts))

        # Address line
        address_line = f"Address: {address}" if address else "Address: "
        submission_part = f"Submission Date: {submission_date}"
        # Pad address line to align submission date
        padding = max(0, 80 - len(address_line) - len(submission_part))
        lines.append(f" {address_line}{' ' * padding}{submission_part}")
        lines.append("")

        # Table header
        lines.append("QSO#   QSO Date     Callsign      SKCC#    Name         State        Band")
        lines.append("-" * 74)

        # Contact rows
        for i, contact in enumerate(contacts, 1):
            qso_date = contact.get('date', '')
            contact_callsign = contact.get('callsign', '')
            skcc_num = contact.get('skcc_number', '')
            contact_name = contact.get('name', '')
            state = contact.get('state', '')
            band = contact.get('band', '')

            # Format date from YYYY-MM-DD to YYYY-MM-DD (keep as is)
            # If date is in YYYYMMDD format, convert it
            if qso_date and '-' not in qso_date and len(qso_date) == 8:
                qso_date = f"{qso_date[:4]}-{qso_date[4:6]}-{qso_date[6:]}"

            # Format band (remove 'M' suffix if present, e.g., "40M" -> "40")
            band_num = band.replace('M', '').replace('m', '') if band else ''

            # Format row with proper column widths
            row = (
                f"{i:<6} "
                f"{qso_date:<12} "
                f"{contact_callsign:<13} "
                f"{skcc_num:<8} "
                f"{contact_name:<12} "
                f"{state:<12} "
                f"{band_num}"
            )
            lines.append(row)

        lines.append("")

        # Certification statement
        cert_name = name if name else callsign
        lines.append(f"I, {cert_name}, certify that the above contacts were made as stated.")
        lines.append(datetime.now().strftime("%A, %B %d, %Y"))

        return "\n".join(lines)

    def _get_created_by_line(self) -> str:
        """
        Generate the "Created by" line

        Returns:
            Created by line with app info
        """
        # Get platform info
        system = platform.system()
        if system == "Linux":
            platform_str = "Linux"
        elif system == "Darwin":
            platform_str = "macOS"
        elif system == "Windows":
            platform_str = "Windows"
        else:
            platform_str = system

        # Get current timestamp
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d at %H:%M:%S")

        # Determine timezone (simplified)
        timezone = "UTC"  # Default to UTC for simplicity

        return f"Created by W4GNS-General-Logger v1.0.0 {platform_str} Build {timestamp} {timezone}"

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
