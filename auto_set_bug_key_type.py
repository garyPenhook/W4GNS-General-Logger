#!/usr/bin/env python3
"""
Automatically set all SKCC contacts to use BUG key type
This script will update all contacts that have an SKCC number but no key_type
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database import Database

def auto_set_bug_key_type(db_path=None):
    """Set all SKCC contacts to BUG key type"""

    # Find database
    if db_path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        possible_paths = [
            os.path.join(script_dir, "logger.db"),
            os.path.join(os.path.expanduser("~"), "logger.db"),
            os.path.join(os.path.expanduser("~"), "apps", "W4GNS-General-Logger-main", "logger.db"),
        ]

        # Find first existing database
        for path in possible_paths:
            if os.path.exists(path):
                db_path = path
                break

        if db_path is None:
            print("Error: Database not found in common locations")
            print("\nSearched:")
            for path in possible_paths:
                print(f"  - {path}")
            print("\nPlease specify database path:")
            print("  python3 auto_set_bug_key_type.py /path/to/logger.db")
            sys.exit(1)

    print("="*70)
    print("Auto-Setting BUG Key Type for All SKCC Contacts")
    print("="*70)

    # Open database
    db = Database(db_path)
    cursor = db.conn.cursor()

    # Count contacts that need updating
    cursor.execute('''
        SELECT COUNT(*)
        FROM contacts
        WHERE skcc_number IS NOT NULL
        AND skcc_number != ''
        AND (key_type IS NULL OR key_type = '')
    ''')

    count = cursor.fetchone()[0]

    if count == 0:
        print("\n✓ All SKCC contacts already have key_type set!")
        print("\nNo updates needed.")
        db.close()
        return

    print(f"\nFound {count} SKCC contacts without key_type")
    print(f"Setting all to: BUG (exports as 'BG' in ADIF)")

    # Update all contacts
    cursor.execute('''
        UPDATE contacts
        SET key_type = 'BUG'
        WHERE skcc_number IS NOT NULL
        AND skcc_number != ''
        AND (key_type IS NULL OR key_type = '')
    ''')

    updated = cursor.rowcount
    db.conn.commit()

    print(f"\n✓ Successfully updated {updated} contacts")

    # Show summary
    cursor.execute('''
        SELECT
            key_type,
            COUNT(*) as count
        FROM contacts
        WHERE skcc_number IS NOT NULL AND skcc_number != ''
        GROUP BY key_type
        ORDER BY count DESC
    ''')

    print("\nKey Type Summary for SKCC Contacts:")
    print("-" * 40)
    for row in cursor.fetchall():
        key = row[0] if row[0] else "None"
        count = row[1]
        print(f"  {key:12} {count:5} contacts")

    db.close()

    print("\n" + "="*70)
    print("✓ COMPLETE!")
    print("="*70)
    print("\nNext steps:")
    print("  1. Re-export your ADIF file from the app")
    print("  2. Import into SKCCLogger")
    print("  3. All contacts should now process correctly!")

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Automatically set all SKCC contacts to BUG key type'
    )
    parser.add_argument('database', nargs='?', help='Path to database file (optional)')

    args = parser.parse_args()

    try:
        auto_set_bug_key_type(args.database)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
