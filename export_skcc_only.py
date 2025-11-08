#!/usr/bin/env python3
"""
Export SKCC contacts only to ADIF format for import into SKCC Logger

This exports contacts with SKCC numbers in a format compatible with SKCC Logger.
"""

import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database import Database

def export_skcc_contacts(output_file=None, db_path=None):
    """
    Export SKCC contacts to ADIF file

    Args:
        output_file: Output filename (default: skcc_export_YYYYMMDD_HHMMSS.adi)
        db_path: Optional path to database (defaults to logger.db)
    """
    # Initialize database
    if db_path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(script_dir, "logger.db")

    db = Database(db_path)
    cursor = db.conn.cursor()

    # Get all contacts with SKCC numbers
    cursor.execute('''
        SELECT
            callsign, date, time_on, time_off, frequency, band, mode,
            rst_sent, rst_rcvd, power, name, qth, gridsquare, county,
            state, country, continent, cq_zone, itu_zone, dxcc,
            my_gridsquare, comment, skcc_number, my_skcc_number,
            dxcc_entity, key_type, duration_minutes, power_watts, distance_nm
        FROM contacts
        WHERE skcc_number IS NOT NULL AND skcc_number != ''
        ORDER BY date, time_on
    ''')

    contacts = cursor.fetchall()

    if not contacts:
        print("No SKCC contacts found in database!")
        print("\nMake sure you've run:")
        print("  1. python3 extract_skcc_from_comments.py")
        print("  2. python3 set_default_key_type.py BUG")
        return

    # Generate default filename if not provided
    if output_file is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f'skcc_export_{timestamp}.adi'

    print(f"{'='*70}")
    print(f"Exporting {len(contacts)} SKCC contacts to ADIF")
    print(f"Output file: {output_file}")
    print(f"{'='*70}\n")

    # Get user's callsign and SKCC number from config (if available)
    cursor.execute('SELECT value FROM config WHERE key = "callsign"')
    result = cursor.fetchone()
    user_callsign = result[0] if result else ""

    cursor.execute('SELECT value FROM config WHERE key = "skcc_number"')
    result = cursor.fetchone()
    user_skcc = result[0] if result else ""

    # Write ADIF file
    with open(output_file, 'w', encoding='utf-8') as f:
        # Write header
        f.write("ADIF Log Created by W4GNS General Logger\n")
        f.write(f"SKCC Contacts Export\n")
        f.write(f"Version: 1.0.0\n")
        f.write("\n")
        if user_callsign:
            f.write(f"Callsign: {user_callsign}\n")
        if user_skcc:
            f.write(f"SKCC Nr.: {user_skcc}\n")
        f.write(f"Log Created: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}Z\n")
        f.write(f"Record Count: {len(contacts)}\n")
        f.write(f"Log Filename: {os.path.abspath(output_file)}\n")
        f.write("\n")
        f.write("<EOH>\n\n")

        # Column indices
        COL_CALLSIGN = 0
        COL_DATE = 1
        COL_TIME_ON = 2
        COL_TIME_OFF = 3
        COL_FREQUENCY = 4
        COL_BAND = 5
        COL_MODE = 6
        COL_RST_SENT = 7
        COL_RST_RCVD = 8
        COL_POWER = 9
        COL_NAME = 10
        COL_QTH = 11
        COL_GRIDSQUARE = 12
        COL_COUNTY = 13
        COL_STATE = 14
        COL_COUNTRY = 15
        COL_CONTINENT = 16
        COL_CQ_ZONE = 17
        COL_ITU_ZONE = 18
        COL_DXCC = 19
        COL_MY_GRIDSQUARE = 20
        COL_COMMENT = 21
        COL_SKCC_NUMBER = 22
        COL_MY_SKCC_NUMBER = 23
        COL_DXCC_ENTITY = 24
        COL_KEY_TYPE = 25
        COL_DURATION_MINUTES = 26
        COL_POWER_WATTS = 27
        COL_DISTANCE_NM = 28

        # Write each contact
        for contact in contacts:
            fields = []

            # Band
            if contact[COL_BAND]:
                band = contact[COL_BAND].upper()
                fields.append(f"<BAND:{len(band)}>{band}")

            # Callsign (required)
            callsign = contact[COL_CALLSIGN].upper()
            fields.append(f"<CALL:{len(callsign)}>{callsign}")

            # Build SKCC-enhanced comment field for SKCCLogger
            # SKCCLogger expects: "SKCC {number} {key_code} {state/country}"
            comment_parts = []

            # Get existing comment and clean it
            existing_comment = contact[COL_COMMENT]
            if existing_comment:
                # Strip out any old SKCC data (format: "SKCC: 12345 - Name - State")
                import re
                cleaned = str(existing_comment)
                patterns = [
                    r'SKCC:\s*\d+[CTS]?\s*(?:-\s*[^-]*(?:-\s*[^-]*)?)?',
                    r'SKCC\s+\d+[CTS]?\s+(?:BG|ST|SS)(?:\s+[A-Z]{2,})?',
                    r'SKCC\s+\d+[CTS]?',
                ]
                for pattern in patterns:
                    cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
                cleaned = ' '.join(cleaned.split()).strip()
                if cleaned:
                    comment_parts.append(cleaned)

            # Add SKCC data in SKCCLogger format
            skcc_num = contact[COL_SKCC_NUMBER]
            key_type = contact[COL_KEY_TYPE]
            state = contact[COL_STATE]
            country = contact[COL_COUNTRY]

            if skcc_num:
                # Get key type abbreviation
                key_code = ''
                if key_type:
                    key_map = {'STRAIGHT': 'ST', 'BUG': 'BG', 'SIDESWIPER': 'SS'}
                    key_code = key_map.get(str(key_type).upper().strip(), '')

                # Format: "SKCC 12345 BG MD" or "SKCC 12345 BG Canada"
                skcc_comment = f"SKCC {skcc_num}"
                if key_code:
                    skcc_comment += f" {key_code}"
                if state:
                    skcc_comment += f" {state}"
                elif country:
                    skcc_comment += f" {country}"

                comment_parts.append(skcc_comment)

            # Write combined comment
            if comment_parts:
                full_comment = " ".join(comment_parts)
                fields.append(f"<COMMENT:{len(full_comment)}>{full_comment}")

            # Country
            if contact[COL_COUNTRY]:
                country = contact[COL_COUNTRY]
                fields.append(f"<COUNTRY:{len(country)}>{country}")

            # DXCC
            if contact[COL_DXCC]:
                dxcc = str(contact[COL_DXCC])
                fields.append(f"<DXCC:{len(dxcc)}>{dxcc}")

            # Frequency
            if contact[COL_FREQUENCY]:
                freq = contact[COL_FREQUENCY]
                fields.append(f"<FREQ:{len(freq)}>{freq}")

            # Gridsquare
            if contact[COL_GRIDSQUARE]:
                grid = contact[COL_GRIDSQUARE].upper()
                fields.append(f"<GRIDSQUARE:{len(grid)}>{grid}")

            # Mode (required)
            mode = contact[COL_MODE].upper()
            fields.append(f"<MODE:{len(mode)}>{mode}")

            # My Gridsquare
            if contact[COL_MY_GRIDSQUARE]:
                my_grid = contact[COL_MY_GRIDSQUARE].upper()
                fields.append(f"<MY_GRIDSQUARE:{len(my_grid)}>{my_grid}")

            # Name
            if contact[COL_NAME]:
                name = contact[COL_NAME]
                fields.append(f"<NAME:{len(name)}>{name}")

            # Operator (use user's callsign if available)
            if user_callsign:
                fields.append(f"<OPERATOR:{len(user_callsign)}>{user_callsign}")

            # QSO Date (required) - format as YYYYMMDD
            date = contact[COL_DATE].replace('-', '')
            fields.append(f"<QSO_DATE:{len(date)}>{date}")

            # QTH
            if contact[COL_QTH]:
                qth = contact[COL_QTH]
                fields.append(f"<QTH:{len(qth)}>{qth}")

            # RST Received
            if contact[COL_RST_RCVD]:
                rst_rcvd = contact[COL_RST_RCVD]
                fields.append(f"<RST_RCVD:{len(rst_rcvd)}>{rst_rcvd}")

            # RST Sent
            if contact[COL_RST_SENT]:
                rst_sent = contact[COL_RST_SENT]
                fields.append(f"<RST_SENT:{len(rst_sent)}>{rst_sent}")

            # SKCC Number (CRITICAL - export in multiple formats for compatibility)
            skcc = contact[COL_SKCC_NUMBER]
            fields.append(f"<SKCC:{len(skcc)}>{skcc}")
            fields.append(f"<APP_SKCC_NUMBER:{len(skcc)}>{skcc}")
            fields.append(f"<APP_SKCCLOGGER_NUMBER:{len(skcc)}>{skcc}")

            # SKCC Key Type (for award validation)
            if contact[COL_KEY_TYPE]:
                key_type = str(contact[COL_KEY_TYPE]).strip()
                # Export abbreviated code for SKCCLogger
                key_map = {'STRAIGHT': 'ST', 'BUG': 'BG', 'SIDESWIPER': 'SS'}
                key_code = key_map.get(key_type.upper(), key_type)
                fields.append(f"<APP_SKCCLOGGER_KEYTYPE:{len(key_code)}>{key_code}")
                # Also export full name for other programs
                fields.append(f"<APP_SKCC_KEY_TYPE:{len(key_type)}>{key_type}")

            # SKCC-specific award fields
            if contact[COL_MY_SKCC_NUMBER]:
                my_skcc = str(contact[COL_MY_SKCC_NUMBER])
                fields.append(f"<APP_SKCC_MY_NUMBER:{len(my_skcc)}>{my_skcc}")

            if contact[COL_DURATION_MINUTES]:
                duration = str(contact[COL_DURATION_MINUTES])
                fields.append(f"<APP_SKCC_DURATION:{len(duration)}>{duration}")

            if contact[COL_POWER_WATTS]:
                pwr_watts = str(contact[COL_POWER_WATTS])
                fields.append(f"<APP_SKCC_POWER:{len(pwr_watts)}>{pwr_watts}")

            if contact[COL_DISTANCE_NM]:
                distance = str(contact[COL_DISTANCE_NM])
                fields.append(f"<APP_SKCC_DISTANCE:{len(distance)}>{distance}")

            # State
            if contact[COL_STATE]:
                state = contact[COL_STATE].upper()
                fields.append(f"<STATE:{len(state)}>{state}")

            # Station Callsign (use user's callsign if available)
            if user_callsign:
                fields.append(f"<STATION_CALLSIGN:{len(user_callsign)}>{user_callsign}")

            # Time Off - format as HHMMSS
            if contact[COL_TIME_OFF]:
                time_off = contact[COL_TIME_OFF].replace(':', '') + '00'
                fields.append(f"<TIME_OFF:{len(time_off)}>{time_off}")

            # Time On (required) - format as HHMMSS
            time_on = contact[COL_TIME_ON].replace(':', '') + '00'
            fields.append(f"<TIME_ON:{len(time_on)}>{time_on}")

            # TX Power
            if contact[COL_POWER]:
                power = str(contact[COL_POWER])
                fields.append(f"<TX_PWR:{len(power)}>{power}")

            # End of record
            fields.append("<EOR>")

            # Write record (one field per line for readability)
            f.write('\n'.join(fields))
            f.write('\n\n')

    print(f"✓ Successfully exported {len(contacts)} SKCC contacts")
    print(f"\nFile saved to: {os.path.abspath(output_file)}")
    print(f"\nYou can now import this file into SKCC Logger:")
    print(f"  File → Import → ADIF → Select '{output_file}'")

    db.close()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Export SKCC contacts to ADIF format for SKCC Logger',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Export with default filename (skcc_export_YYYYMMDD_HHMMSS.adi)
  python3 export_skcc_only.py

  # Specify output filename
  python3 export_skcc_only.py -o my_skcc_contacts.adi

  # Specify database location
  python3 export_skcc_only.py -d ./logger.db -o skcc.adi
        '''
    )
    parser.add_argument('-o', '--output', help='Output filename')
    parser.add_argument('-d', '--database', help='Path to database file')

    args = parser.parse_args()

    try:
        export_skcc_contacts(args.output, args.database)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
