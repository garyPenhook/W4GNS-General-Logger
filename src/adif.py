"""
ADIF (Amateur Data Interchange Format) Parser and Generator
Supports ADIF 3.x format for import/export of contact logs
"""

import re
from datetime import datetime


class ADIFParser:
    """Parse ADIF files and extract contact records with lazy parsing for performance"""

    def __init__(self, filename=None, lazy=True):
        """
        Initialize ADIF parser

        Args:
            filename: Optional ADIF file to parse
            lazy: If True, parse records on-demand; if False, parse all upfront
        """
        self.filename = filename
        self.lazy = lazy
        self._records = None  # Cached parsed records
        self._raw_content = None  # Raw file content for lazy parsing
        self._record_strings = None  # Split records for lazy parsing

        if filename:
            if lazy:
                self._load_raw_content()
            else:
                self._records = self.parse_file(filename)

    def _load_raw_content(self):
        """Load raw file content for lazy parsing"""
        if not self.filename:
            return

        with open(self.filename, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()

        # Find the end of header marker
        eoh_match = re.search(r'<eoh>|<EOH>', content, re.IGNORECASE)
        if eoh_match:
            content = content[eoh_match.end():]

        # Split into record strings (but don't parse yet)
        self._record_strings = [
            rec.strip() for rec in re.split(r'<eor>|<EOR>', content, flags=re.IGNORECASE)
            if rec.strip()
        ]

    @property
    def records(self):
        """Lazy property that parses records on first access"""
        if self._records is None:
            if self._record_strings is not None:
                # Lazy parse from cached record strings
                self._records = [
                    self._parse_record(rec) for rec in self._record_strings
                    if self._parse_record(rec)
                ]
            else:
                self._records = []
        return self._records

    def parse_file(self, filename):
        """Parse an ADIF file and return list of contact records (non-lazy)"""
        with open(filename, 'r', encoding='utf-8', errors='replace') as f:
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

        # Store records for iteration (update internal cache)
        if filename == self.filename:
            self._records = contacts

        return contacts

    def iter_records(self):
        """
        Memory-efficient generator for iterating over records without loading all into memory

        Yields:
            dict: Parsed contact record

        Example:
            >>> parser = ADIFParser('huge_logbook.adi')
            >>> for contact in parser.iter_records():
            ...     print(contact['callsign'])
        """
        if self._record_strings:
            # Lazy parsing from cached strings
            for rec_str in self._record_strings:
                contact = self._parse_record(rec_str)
                if contact:
                    yield contact
        elif self._records:
            # Already parsed, just iterate
            yield from self._records
        elif self.filename:
            # Parse on-the-fly without caching
            with open(self.filename, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()

            eoh_match = re.search(r'<eoh>|<EOH>', content, re.IGNORECASE)
            if eoh_match:
                content = content[eoh_match.end():]

            records = re.split(r'<eor>|<EOR>', content, flags=re.IGNORECASE)

            for record in records:
                if record.strip():
                    contact = self._parse_record(record)
                    if contact:
                        yield contact

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
                'APP_SKCC_DISTANCE': 'distance_miles',
                'APP_SKCC_DISTANCE_NM': 'distance_nm',
                'APP_SKCC_POWER': 'power_watts',
                'APP_SKCC_THEIR_POWER': 'their_power_watts',
                'APP_SKCC_MPW_DISTANCE': 'distance_miles',
                'APP_SKCC_DISTANCE_MILES': 'distance_miles',
                'APP_SKCC_DISTANCE_SOURCE': 'distance_source',
                'APP_SKCC_SITE': 'site',
                'APP_SKCC_ANTENNA': 'antenna',
                'APP_SKCC_SATELLITE': 'is_satellite',
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

    # Python data model methods for iterator protocol
    def __iter__(self):
        """Enable iteration: for contact in parser: (uses lazy parsing if available)"""
        if self.lazy and (self._record_strings is not None or self.filename):
            return self.iter_records()
        return iter(self.records)

    def __len__(self):
        """Enable len(): len(parser) (forces parsing if lazy)"""
        if self._record_strings and self._records is None:
            # Return count without full parsing
            return len(self._record_strings)
        return len(self.records)

    def __repr__(self):
        """Developer-friendly representation"""
        mode = "lazy" if self.lazy else "eager"
        if self._records is not None:
            count = len(self._records)
            status = f"parsed={count}"
        elif self._record_strings is not None:
            count = len(self._record_strings)
            status = f"unparsed={count}"
        else:
            status = "empty"

        if self.filename:
            return f"<ADIFParser(file={self.filename!r}, {status}, mode={mode})>"
        return f"<ADIFParser({status}, mode={mode})>"


class ADIFGenerator:
    """Generate ADIF files from contact records"""

    def __init__(self):
        self.version = "3.1.4"
        # Country to 3-letter code mapping for SKCC logger
        self.country_codes = {
            'UNITED STATES': 'USA',
            'CANADA': 'CAN',
            'MEXICO': 'MEX',
            'ENGLAND': 'ENG',
            'SCOTLAND': 'SCO',
            'WALES': 'WAL',
            'NORTHERN IRELAND': 'NIR',
            'IRELAND': 'IRL',
            'GERMANY': 'DEU',
            'FRANCE': 'FRA',
            'ITALY': 'ITA',
            'SPAIN': 'ESP',
            'PORTUGAL': 'PRT',
            'NETHERLANDS': 'NLD',
            'BELGIUM': 'BEL',
            'AUSTRIA': 'AUT',
            'SWITZERLAND': 'CHE',
            'DENMARK': 'DNK',
            'SWEDEN': 'SWE',
            'NORWAY': 'NOR',
            'FINLAND': 'FIN',
            'POLAND': 'POL',
            'CZECH REPUBLIC': 'CZE',
            'HUNGARY': 'HUN',
            'GREECE': 'GRC',
            'TURKEY': 'TUR',
            'RUSSIA': 'RUS',
            'UKRAINE': 'UKR',
            'AUSTRALIA': 'AUS',
            'NEW ZEALAND': 'NZL',
            'JAPAN': 'JPN',
            'CHINA': 'CHN',
            'SOUTH KOREA': 'KOR',
            'BRAZIL': 'BRA',
            'ARGENTINA': 'ARG',
            'CHILE': 'CHL',
        }

    def _get_country_code(self, country):
        """Convert country name to 3-letter code for SKCC logger format"""
        if not country:
            return ''
        country_upper = country.upper()
        return self.country_codes.get(country_upper, country[:3].upper())

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

        # Build SKCC-enhanced comment field for SKCCLogger compatibility
        # SKCCLogger expects SKCC data in the COMMENT field
        comment_parts = []

        # Get existing comment/notes and strip any old SKCC data from it
        existing_comment = contact.get('comment', '') or contact.get('comments', '') or contact.get('notes', '')
        if existing_comment:
            # Remove any old SKCC-formatted data from existing comments
            cleaned_comment = self._strip_skcc_from_comment(str(existing_comment))
            if cleaned_comment:
                comment_parts.append(cleaned_comment)

        # Add SKCC data to comment for SKCCLogger in correct format
        # SKCCLogger expects: "SKCC:contacts_skcc_number-first_name-state_or_3letter_country_name"
        skcc_number = contact.get('skcc_number', '')
        key_type = contact.get('key_type', '')

        if skcc_number:
            skcc_number = str(skcc_number).strip()
            first_name = (contact.get('first_name') or '').strip()
            state = (contact.get('state') or '').strip()
            country = (contact.get('country') or '').strip()

            # Format: "SKCC:12345-Ron-MD" (with state) or "SKCC:12345-Ron-CAN" (with 3-letter country code)
            skcc_comment = f"SKCC:{skcc_number}"

            if first_name:
                skcc_comment += f"-{first_name}"

            # Add state (for US/Canada/etc) or 3-letter country code (for DX)
            if state:
                skcc_comment += f"-{state}"
            elif country:
                country_code = self._get_country_code(country)
                skcc_comment += f"-{country_code}"

            comment_parts.append(skcc_comment)

        # Combine comment parts
        full_comment = " ".join(comment_parts)

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
            # SKCC-specific fields (user-defined ADIF fields)
            'my_skcc_number': 'APP_SKCC_MY_NUMBER',
            'duration_minutes': 'APP_SKCC_DURATION',
            'distance_nm': 'APP_SKCC_DISTANCE_NM',
            'distance_miles': 'APP_SKCC_DISTANCE',
            'distance_source': 'APP_SKCC_DISTANCE_SOURCE',
            'site': 'APP_SKCC_SITE',
            'antenna': 'APP_SKCC_ANTENNA',
            'is_satellite': 'APP_SKCC_SATELLITE',
            'their_power_watts': 'APP_SKCC_THEIR_POWER',
            'dxcc_entity': 'DXCC_ENTITY'
        }

        for db_field, adif_field in field_map.items():
            value = contact.get(db_field, '')

            if isinstance(value, str):
                value = value.strip()
            else:
                value = str(value) if value else ''

            if db_field == 'is_satellite':
                value = '1' if str(value).strip().lower() in ('1', 'true', 'yes', 'y') else ''

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

        # Add SKCC-enhanced comment field (SKCCLogger reads this)
        if full_comment:
            fields.append(f"<COMMENT:{len(full_comment)}>{full_comment}")

        # Export SKCC number using BOTH standard SKCC field and SKCCLogger format
        # This ensures compatibility with both SKCCLogger and other programs
        if skcc_number:
            # Standard ADIF SKCC field (used by SKCCLogger)
            fields.append(f"<SKCC:{len(skcc_number)}>{skcc_number}")
            # Also include APP fields for other programs
            fields.append(f"<APP_SKCC_NUMBER:{len(skcc_number)}>{skcc_number}")
            fields.append(f"<APP_SKCCLOGGER_NUMBER:{len(skcc_number)}>{skcc_number}")

        # Export key type using SKCCLogger format
        if key_type:
            key_type_str = str(key_type).strip()
            if key_type_str:
                # SKCCLogger expects abbreviated codes
                key_code = self._get_key_type_code(key_type_str)
                # Export using SKCCLogger field name
                fields.append(f"<APP_SKCCLOGGER_KEYTYPE:{len(key_code)}>{key_code}")
                # Also include full name for other programs
                fields.append(f"<APP_SKCC_KEY_TYPE:{len(key_type_str)}>{key_type_str}")

        # Export power_watts as APP_SKCC_POWER for QRP award validation
        # This is separate from TX_PWR and used specifically for QRP MPW calculations
        power_watts = contact.get('power_watts', '')
        if power_watts:
            power_str = str(power_watts).strip()
            if power_str:
                fields.append(f"<APP_SKCC_POWER:{len(power_str)}>{power_str}")

        # Add end-of-record marker
        fields.append("<EOR>")

        return " ".join(fields)

    def _get_key_type_code(self, key_type):
        """
        Convert full key type names to SKCCLogger abbreviated codes

        Args:
            key_type: Full key type name (STRAIGHT, BUG, SIDESWIPER)

        Returns:
            Abbreviated code (ST, BG, SS)
        """
        code_map = {
            'STRAIGHT': 'ST',
            'BUG': 'BG',
            'SIDESWIPER': 'SS'
        }
        return code_map.get(key_type.upper().strip(), key_type)

    def _strip_skcc_from_comment(self, comment):
        """
        Strip SKCC-formatted data from existing comments

        Removes SKCC comment patterns like:
        - New format: "SKCC:12345-Ron-MD" or "SKCC:12345T-Ron-CAN"
        - Old format: "SKCC: 12345S - Ron - MD"
        - Old format: "SKCC 12345 BG MD" (with state)
        - Old format: "SKCC 12345 BG Canada" (with country)

        Args:
            comment: Original comment string

        Returns:
            Cleaned comment with SKCC data removed
        """
        if not comment:
            return ''

        # Pattern to match SKCC data in various formats:
        # - New format: "SKCC:12345-Name-State" or "SKCC:12345T-Name-CAN"
        # - Old format: "SKCC: 12345S - Name - State"
        # - Old format: "SKCC 12345 BG MD" (with key type codes)
        patterns = [
            r'SKCC:\d+[CTS]?-[^-\s]+-[A-Z]{2,3}',  # New format: SKCC:12345-Ron-MD or SKCC:12345T-Ron-CAN
            r'SKCC:\d+[CTS]?-[^-\s]+',  # New format partial: SKCC:12345-Ron
            r'SKCC:\d+[CTS]?',  # New format minimal: SKCC:12345
            r'SKCC:\s*\d+[CTS]?\s*(?:-\s*[^-]*(?:-\s*[^-]*)?)?',  # Old format: SKCC: 12345S - Name - State
            r'SKCC\s+\d+[CTS]?\s+(?:BG|ST|SS)(?:\s+[A-Z]{2,})?',  # Old format: SKCC 12345S BG MD or SKCC 12345 BG Canada
            r'SKCC\s+\d+[CTS]?',  # Old format minimal: SKCC 12345S
        ]

        cleaned = comment
        for pattern in patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)

        # Clean up extra whitespace
        cleaned = ' '.join(cleaned.split())

        return cleaned.strip()


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
        with open(filename, 'r', encoding='utf-8', errors='replace') as f:
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
