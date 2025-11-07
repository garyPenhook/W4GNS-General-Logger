"""
ADIF (Amateur Data Interchange Format) Parser and Generator
Supports ADIF 3.x format for import/export of contact logs
"""

import re
from datetime import datetime


class ADIFParser:
    """Parse ADIF files and extract contact records"""

    def __init__(self):
        self.records = []

    def parse_file(self, filename):
        """Parse an ADIF file and return list of contact records"""
        with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Find the end of header marker
        eoh_match = re.search(r'<eoh>|<EOH>', content, re.IGNORECASE)
        if eoh_match:
            content = content[eoh_match.end():]

        # Split into records (each record ends with <eor>)
        records = re.split(r'<eor>|<EOR>', content, flags=re.IGNORECASE)

        contacts = []
        for record in records:
            if record.strip():
                contact = self._parse_record(record)
                if contact:
                    contacts.append(contact)

        return contacts

    def _parse_record(self, record):
        """Parse a single ADIF record"""
        # ADIF field format: <FIELD_NAME:LENGTH:TYPE>DATA
        # Type is optional, most common is just <FIELD_NAME:LENGTH>DATA
        pattern = r'<([A-Za-z0-9_]+):(\d+)(?::([A-Z]))?>(.*?(?=<|$))'
        matches = re.finditer(pattern, record, re.IGNORECASE | re.DOTALL)

        contact = {}
        for match in matches:
            field_name = match.group(1).upper()
            field_length = int(match.group(2))
            field_data = match.group(4)[:field_length]

            # Map ADIF fields to our database fields
            field_map = {
                'CALL': 'callsign',
                'QSO_DATE': 'date',
                'TIME_ON': 'time_on',
                'TIME_OFF': 'time_off',
                'FREQ': 'frequency',
                'BAND': 'band',
                'MODE': 'mode',
                'RST_SENT': 'rst_sent',
                'RST_RCVD': 'rst_rcvd',
                'TX_PWR': 'power',
                'NAME': 'name',
                'QTH': 'qth',
                'GRIDSQUARE': 'gridsquare',
                'CNTY': 'county',
                'STATE': 'state',
                'COUNTRY': 'country',
                'CONT': 'continent',
                'CQZ': 'cq_zone',
                'ITUZ': 'itu_zone',
                'DXCC': 'dxcc',
                'IOTA': 'iota',
                'SOTA_REF': 'sota',
                'POTA_REF': 'pota',
                'MY_GRIDSQUARE': 'my_gridsquare',
                'COMMENT': 'comment',
                'NOTES': 'notes',
                # SKCC-specific fields (user-defined ADIF fields with APP_ prefix)
                'APP_SKCC_NUMBER': 'skcc_number',
                'APP_SKCC_MY_NUMBER': 'my_skcc_number',
                'APP_SKCC_KEY_TYPE': 'key_type',
                'APP_SKCC_DURATION': 'duration_minutes',
                'APP_SKCC_DISTANCE': 'distance_nm',
                'APP_SKCC_POWER': 'power_watts',
                # SKCC Logger-specific fields (uses different naming)
                'SKCC': 'skcc_number',  # SKCC Logger uses this field name
                'APP_SKCCLOGGER_KEYTYPE': 'key_type',
                'APP_SKCCLOGGER_NUMBER': 'skcc_number',
                'DXCC_ENTITY': 'dxcc_entity'
            }

            if field_name in field_map:
                db_field = field_map[field_name]

                # Format date from YYYYMMDD to YYYY-MM-DD
                if field_name == 'QSO_DATE' and len(field_data) == 8:
                    field_data = f"{field_data[:4]}-{field_data[4:6]}-{field_data[6:8]}"

                # Format time from HHMM or HHMMSS to HH:MM
                elif field_name in ('TIME_ON', 'TIME_OFF') and field_data:
                    if len(field_data) >= 4:
                        field_data = f"{field_data[:2]}:{field_data[2:4]}"

                # Convert frequency from MHz to display format
                elif field_name == 'FREQ':
                    field_data = field_data  # Keep as-is

                # Translate SKCC Logger abbreviated key codes to full names
                elif field_name in ('APP_SKCCLOGGER_KEYTYPE', 'APP_SKCC_KEY_TYPE') and db_field == 'key_type':
                    field_data = self._translate_key_type(field_data)

                contact[db_field] = field_data.strip()

        return contact if contact else None

    def _translate_key_type(self, code):
        """
        Translate SKCC Logger abbreviated key codes to full names

        SKCC Logger uses abbreviated codes:
        - BG = Bug
        - SK or ST = Straight key
        - SS = Sideswiper

        Args:
            code: Abbreviated key code (case-insensitive)

        Returns:
            Full key type name (STRAIGHT, BUG, SIDESWIPER) or original if unrecognized
        """
        code_map = {
            'BG': 'BUG',
            'SK': 'STRAIGHT',
            'ST': 'STRAIGHT',  # Support both SK and ST for straight key
            'SS': 'SIDESWIPER',
            # Also support full names if already present
            'BUG': 'BUG',
            'STRAIGHT': 'STRAIGHT',
            'SIDESWIPER': 'SIDESWIPER'
        }

        return code_map.get(code.upper().strip(), code)


class ADIFGenerator:
    """Generate ADIF files from contact records"""

    def __init__(self):
        self.version = "3.1.4"

    def generate_file(self, filename, contacts, program_name="W4GNS General Logger", program_version="1.0.0"):
        """Generate an ADIF file from list of contact records"""
        with open(filename, 'w', encoding='utf-8') as f:
            # Write header
            f.write(f"ADIF Export from {program_name}\n")
            f.write(f"<ADIF_VER:{len(self.version)}>{self.version}\n")
            f.write(f"<PROGRAMID:{len(program_name)}>{program_name}\n")
            f.write(f"<PROGRAMVERSION:{len(program_version)}>{program_version}\n")
            f.write(f"<CREATED_TIMESTAMP:15>{datetime.utcnow().strftime('%Y%m%d %H%M%S')}\n")
            f.write("<EOH>\n\n")

            # Write records
            for contact in contacts:
                record = self._generate_record(contact)
                f.write(record)
                f.write("\n")

    def _generate_record(self, contact):
        """Generate a single ADIF record from contact data"""
        fields = []

        # Map database fields to ADIF fields
        field_map = {
            'callsign': 'CALL',
            'date': 'QSO_DATE',
            'qso_date': 'QSO_DATE',  # Support both field names
            'time_on': 'TIME_ON',
            'time_off': 'TIME_OFF',
            'frequency': 'FREQ',
            'band': 'BAND',
            'mode': 'MODE',
            'rst_sent': 'RST_SENT',
            'rst_rcvd': 'RST_RCVD',
            'power': 'TX_PWR',
            'power_watts': 'TX_PWR',  # Support alternate field name
            'name': 'NAME',
            'qth': 'QTH',
            'gridsquare': 'GRIDSQUARE',
            'county': 'CNTY',
            'state': 'STATE',
            'country': 'COUNTRY',
            'continent': 'CONT',
            'cq_zone': 'CQZ',
            'itu_zone': 'ITUZ',
            'dxcc': 'DXCC',
            'dxcc_entity': 'DXCC',  # Support alternate field name
            'iota': 'IOTA',
            'sota': 'SOTA_REF',
            'pota': 'POTA_REF',
            'my_gridsquare': 'MY_GRIDSQUARE',
            'comment': 'COMMENT',
            'comments': 'COMMENT',  # Support alternate field name
            'notes': 'NOTES',
            # SKCC-specific fields (user-defined ADIF fields)
            'skcc_number': 'APP_SKCC_NUMBER',
            'my_skcc_number': 'APP_SKCC_MY_NUMBER',
            'key_type': 'APP_SKCC_KEY_TYPE',
            'duration_minutes': 'APP_SKCC_DURATION',
            'distance_nm': 'APP_SKCC_DISTANCE',
            'distance_miles': 'APP_SKCC_DISTANCE',  # Support alternate field name
            'power_watts': 'APP_SKCC_POWER',
            'dxcc_entity': 'DXCC_ENTITY'
        }

        for db_field, adif_field in field_map.items():
            value = contact.get(db_field, '')

            if isinstance(value, str):
                value = value.strip()
            else:
                value = str(value) if value else ''

            if not value:
                continue

            # Format date from YYYY-MM-DD to YYYYMMDD
            if adif_field == 'QSO_DATE':
                value = value.replace('-', '')

            # Format time from HH:MM to HHMMSS (append 00 for seconds)
            elif adif_field in ('TIME_ON', 'TIME_OFF'):
                value = value.replace(':', '') + '00'

            # Ensure gridsquare is uppercase
            elif adif_field == 'GRIDSQUARE':
                value = value.upper()

            # Ensure callsign is uppercase
            elif adif_field == 'CALL':
                value = value.upper()

            fields.append(f"<{adif_field}:{len(value)}>{value}")

        # Add end-of-record marker
        fields.append("<EOR>")

        return " ".join(fields)


def export_contacts_to_adif(contacts, filename, program_name="W4GNS General Logger"):
    """
    Export contacts to ADIF file

    Args:
        contacts: List of contact dictionaries (from database)
        filename: Output filename
        program_name: Name of the program generating the file

    Raises:
        ValueError: If contacts is empty or filename is invalid
        IOError: If file cannot be written
    """
    import os

    # Validate inputs
    if not contacts:
        raise ValueError("No contacts to export")

    if not filename:
        raise ValueError("No filename provided")

    # Check if directory exists and is writable
    directory = os.path.dirname(filename)
    if directory and not os.path.exists(directory):
        try:
            os.makedirs(directory, exist_ok=True)
        except OSError as e:
            raise IOError(f"Cannot create directory {directory}: {e}")

    if directory and not os.access(directory, os.W_OK):
        raise PermissionError(f"Directory not writable: {directory}")

    generator = ADIFGenerator()

    # Convert database Row objects to dictionaries if needed
    contact_list = []
    for contact in contacts:
        try:
            if hasattr(contact, 'keys'):
                # It's a sqlite3.Row object or dict-like
                contact_dict = {key: contact[key] for key in contact.keys()}
            else:
                contact_dict = contact
            contact_list.append(contact_dict)
        except Exception as e:
            print(f"Warning: Skipping invalid contact: {e}")
            continue

    if not contact_list:
        raise ValueError("No valid contacts to export after filtering")

    try:
        generator.generate_file(filename, contact_list, program_name)
    except IOError as e:
        raise IOError(f"Failed to write ADIF file {filename}: {e}")
    except Exception as e:
        raise Exception(f"Error generating ADIF file: {type(e).__name__}: {e}")


def import_contacts_from_adif(filename):
    """
    Import contacts from ADIF file

    Args:
        filename: Input ADIF filename

    Returns:
        List of contact dictionaries ready for database insertion
    """
    parser = ADIFParser()
    contacts = parser.parse_file(filename)
    return contacts


def validate_adif_file(filename):
    """
    Validate an ADIF file

    Returns:
        (bool, str): (is_valid, error_message)
    """
    import os

    # Check file exists
    if not filename:
        return False, "No filename provided"

    if not os.path.exists(filename):
        return False, f"File not found: {filename}"

    if not os.path.isfile(filename):
        return False, f"Path is not a file: {filename}"

    # Check file is readable
    if not os.access(filename, os.R_OK):
        return False, f"File is not readable: {filename}"

    try:
        with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        if not content.strip():
            return False, "File is empty"

        # Check for basic ADIF structure
        if not re.search(r'<eoh>|<EOH>', content, re.IGNORECASE):
            return False, "No <EOH> marker found - may not be a valid ADIF file"

        # Check for at least one record
        if not re.search(r'<eor>|<EOR>', content, re.IGNORECASE):
            return False, "No records found in ADIF file"

        # Try to parse
        parser = ADIFParser()
        contacts = parser.parse_file(filename)

        if not contacts:
            return False, "No valid contacts found in file"

        return True, f"Valid ADIF file with {len(contacts)} contacts"

    except PermissionError:
        return False, f"Permission denied reading file: {filename}"
    except UnicodeDecodeError as e:
        return False, f"File encoding error: {str(e)}"
    except IOError as e:
        return False, f"I/O error reading file: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error: {type(e).__name__}: {str(e)}"
