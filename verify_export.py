#!/usr/bin/env python3
"""
Verify that ADIF export includes all required SKCC fields
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database import Database
from src.adif import ADIFGenerator

def verify_export(db_path='logger.db'):
    """Test export functionality"""

    # Find database
    if not os.path.exists(db_path):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        possible_paths = [
            os.path.join(script_dir, "logger.db"),
            os.path.join(os.path.expanduser("~"), "logger.db"),
            os.path.join(os.path.expanduser("~"), "apps", "W4GNS-General-Logger-main", "logger.db"),
        ]

        for path in possible_paths:
            if os.path.exists(path):
                db_path = path
                break
        else:
            print("❌ Database not found")
            print("\nSearched locations:")
            for path in possible_paths:
                print(f"  - {path}")
            return False

    print(f"Using database: {db_path}")

    # Open database
    db = Database(db_path)
    cursor = db.conn.cursor()

    # Get SKCC contacts with key_type
    cursor.execute('''
        SELECT COUNT(*)
        FROM contacts
        WHERE skcc_number IS NOT NULL
        AND skcc_number != ''
        AND key_type IS NOT NULL
        AND key_type != ''
    ''')

    count_with_key = cursor.fetchone()[0]

    cursor.execute('''
        SELECT COUNT(*)
        FROM contacts
        WHERE skcc_number IS NOT NULL
        AND skcc_number != ''
    ''')

    total_skcc = cursor.fetchone()[0]

    print(f"\n{'='*70}")
    print(f"Database Status:")
    print(f"{'='*70}")
    print(f"Total SKCC contacts: {total_skcc}")
    print(f"SKCC contacts with key_type: {count_with_key}")

    if count_with_key == 0:
        print("\n❌ No contacts have key_type set!")
        print("\nRun: python3 set_default_key_type.py BUG")
        db.close()
        return False

    # Test export with one contact
    cursor.execute('''
        SELECT *
        FROM contacts
        WHERE skcc_number IS NOT NULL
        AND skcc_number != ''
        AND key_type IS NOT NULL
        AND key_type != ''
        LIMIT 1
    ''')

    # Get column names
    columns = [description[0] for description in cursor.description]

    # Get row and convert to dict
    row = cursor.fetchone()
    if not row:
        print("\n❌ No contacts found for testing")
        db.close()
        return False

    contact = dict(zip(columns, row))

    print(f"\n{'='*70}")
    print(f"Test Contact:")
    print(f"{'='*70}")
    print(f"Callsign: {contact.get('callsign', 'N/A')}")
    print(f"SKCC Number: {contact.get('skcc_number', 'N/A')}")
    print(f"Key Type: {contact.get('key_type', 'N/A')}")
    print(f"State: {contact.get('state', 'N/A')}")
    print(f"Country: {contact.get('country', 'N/A')}")

    # Generate ADIF record
    generator = ADIFGenerator()
    record = generator._generate_record(contact)

    print(f"\n{'='*70}")
    print(f"Generated ADIF Record:")
    print(f"{'='*70}")
    print(record)

    # Verify required fields
    print(f"\n{'='*70}")
    print(f"Field Verification:")
    print(f"{'='*70}")

    required_fields = {
        'APP_SKCCLOGGER_KEYTYPE': 'Key type for SKCCLogger',
        'APP_SKCC_KEY_TYPE': 'Key type (full name)',
        'APP_SKCC_NUMBER': 'SKCC number',
        'COMMENT': 'Comment with SKCC data',
    }

    all_present = True
    for field, description in required_fields.items():
        if f'<{field}:' in record:
            print(f"✓ {field}: Present")
        else:
            print(f"❌ {field}: MISSING")
            all_present = False

    # Check if COMMENT includes state/country
    if '<COMMENT:' in record:
        # Extract comment value
        import re
        match = re.search(r'<COMMENT:\d+>([^<]+)', record)
        if match:
            comment = match.group(1)
            print(f"\nComment content: {comment}")

            state = contact.get('state', '')
            country = contact.get('country', '')

            if state and state in comment:
                print(f"✓ State '{state}' found in comment")
            elif country and country in comment:
                print(f"✓ Country '{country}' found in comment")
            else:
                print(f"⚠ State/country not found in comment")

    db.close()

    print(f"\n{'='*70}")
    if all_present:
        print("✓ Export code is working correctly!")
        print(f"\n{'='*70}")
        print("NEXT STEPS:")
        print("1. Open the W4GNS General Logger application")
        print("2. Go to File → Export to ADIF")
        print("3. Save the file (e.g., w4gns_complete_export.adi)")
        print("4. Import into SKCCLogger")
        print(f"{'='*70}")
        return True
    else:
        print("❌ Some required fields are missing from export")
        return False

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Verify ADIF export includes SKCC fields')
    parser.add_argument('database', nargs='?', help='Path to database file')

    args = parser.parse_args()

    try:
        success = verify_export(args.database)
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
