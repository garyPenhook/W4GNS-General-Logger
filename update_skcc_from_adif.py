#!/usr/bin/env python3
"""
Update existing contacts with SKCC data from ADIF file

This script reads an ADIF file and updates matching contacts in the database
with SKCC numbers and key types, without creating duplicates.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database import Database
from src.adif import import_contacts_from_adif

def update_contacts_from_adif(adif_file, db_path=None):
    """
    Update existing contacts with SKCC data from ADIF file

    Args:
        adif_file: Path to ADIF file
        db_path: Optional path to database (defaults to logger.db)
    """
    # Initialize database
    if db_path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(script_dir, "logger.db")

    db = Database(db_path)

    # Import contacts from ADIF
    print(f"Reading ADIF file: {adif_file}")
    contacts = import_contacts_from_adif(adif_file)
    print(f"Found {len(contacts)} contacts in ADIF file\n")

    updated_count = 0
    not_found_count = 0
    no_skcc_count = 0

    cursor = db.conn.cursor()

    for i, contact in enumerate(contacts, 1):
        callsign = contact.get('callsign')
        date = contact.get('date')
        time_on = contact.get('time_on')
        skcc_number = contact.get('skcc_number')
        key_type = contact.get('key_type')

        # Skip if no SKCC data to update
        if not skcc_number and not key_type:
            no_skcc_count += 1
            continue

        # Find matching contact in database
        cursor.execute('''
            SELECT id, skcc_number, key_type
            FROM contacts
            WHERE callsign = ? AND date = ? AND time_on = ?
        ''', (callsign, date, time_on))

        result = cursor.fetchone()

        if result:
            contact_id = result[0]
            old_skcc = result[1] or '(none)'
            old_key = result[2] or '(none)'

            # Update the contact with SKCC data
            update_fields = []
            update_values = []

            if skcc_number:
                update_fields.append('skcc_number = ?')
                update_values.append(skcc_number)

            if key_type:
                update_fields.append('key_type = ?')
                update_values.append(key_type)

            if update_fields:
                update_values.append(contact_id)
                cursor.execute(f'''
                    UPDATE contacts
                    SET {', '.join(update_fields)}
                    WHERE id = ?
                ''', update_values)

                updated_count += 1
                new_skcc = skcc_number or old_skcc
                new_key = key_type or old_key
                print(f"✓ Updated {callsign} on {date}")
                if skcc_number:
                    print(f"  SKCC: {old_skcc} → {new_skcc}")
                if key_type:
                    print(f"  Key:  {old_key} → {new_key}")
        else:
            not_found_count += 1
            if i <= 5:  # Only print first few
                print(f"  Not found: {callsign} on {date} at {time_on}")

    # Commit changes
    db.conn.commit()

    # Summary
    print(f"\n{'='*60}")
    print(f"Update Summary:")
    print(f"  Contacts updated:          {updated_count}")
    print(f"  Contacts not found in DB:  {not_found_count}")
    print(f"  Contacts with no SKCC:     {no_skcc_count}")
    print(f"{'='*60}")

    if updated_count > 0:
        print(f"\n✓ Successfully updated {updated_count} contacts!")
        print(f"  Your SKCC awards should now show correct counts.")

    db.close()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 update_skcc_from_adif.py <adif_file> [database_path]")
        print("\nExample:")
        print("  python3 update_skcc_from_adif.py ~/skcc_log.adi")
        print("  python3 update_skcc_from_adif.py ~/skcc_log.adi ./logger.db")
        sys.exit(1)

    adif_file = sys.argv[1]
    db_path = sys.argv[2] if len(sys.argv) > 2 else None

    if not os.path.exists(adif_file):
        print(f"Error: ADIF file not found: {adif_file}")
        sys.exit(1)

    try:
        update_contacts_from_adif(adif_file, db_path)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
