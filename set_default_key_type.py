#!/usr/bin/env python3
"""
Set a default key_type for all SKCC contacts that don't have one

Since SKCC awards require key_type (STRAIGHT, BUG, or SIDESWIPER),
this script sets a default key type for all contacts with SKCC numbers
but no key_type.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database import Database

VALID_KEY_TYPES = ['STRAIGHT', 'BUG', 'SIDESWIPER']

def set_default_key_type(key_type, db_path=None, dry_run=False):
    """
    Set default key_type for SKCC contacts

    Args:
        key_type: The key type to set (STRAIGHT, BUG, or SIDESWIPER)
        db_path: Optional path to database (defaults to logger.db)
        dry_run: If True, show what would be updated without actually updating
    """
    # Validate key type
    key_type = key_type.upper().strip()
    if key_type not in VALID_KEY_TYPES:
        print(f"Error: Invalid key type '{key_type}'")
        print(f"Valid options: {', '.join(VALID_KEY_TYPES)}")
        sys.exit(1)

    # Initialize database
    if db_path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(script_dir, "logger.db")

    db = Database(db_path)
    cursor = db.conn.cursor()

    # Find SKCC contacts without key_type
    cursor.execute('''
        SELECT id, callsign, date, skcc_number
        FROM contacts
        WHERE skcc_number IS NOT NULL
        AND skcc_number != ''
        AND (key_type IS NULL OR key_type = '')
    ''')

    contacts = cursor.fetchall()

    if not contacts:
        print("No SKCC contacts found without key_type.")
        print("\nAll SKCC contacts already have key types set!")
        db.close()
        return

    print(f"{'='*70}")
    print(f"Found {len(contacts)} SKCC contacts without key_type")
    print(f"Will set key_type to: {key_type}")
    print(f"{'='*70}\n")

    if dry_run:
        # Show examples
        for i, (contact_id, callsign, date, skcc_number) in enumerate(contacts[:10]):
            print(f"Would update: {callsign:10} {date:12} SKCC:{skcc_number:10} → Key:{key_type}")
        if len(contacts) > 10:
            print(f"... and {len(contacts) - 10} more contacts")
    else:
        # Update all contacts
        cursor.execute('''
            UPDATE contacts
            SET key_type = ?
            WHERE skcc_number IS NOT NULL
            AND skcc_number != ''
            AND (key_type IS NULL OR key_type = '')
        ''', (key_type,))

        updated_count = cursor.rowcount
        db.conn.commit()

        print(f"✓ Updated {updated_count} contacts with key_type = {key_type}")

    print(f"\n{'='*70}")
    if dry_run:
        print("This was a DRY RUN. No changes were made.")
        print("Run without --dry-run to apply changes.")
    else:
        print("✓ All SKCC contacts now have key_type set!")
        print("\nYour SKCC awards should now show correctly.")
        print("Refresh the SKCC Awards tab in the application.")

    db.close()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Set default key_type for SKCC contacts',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f'''
Valid key types: {', '.join(VALID_KEY_TYPES)}

Examples:
  # Dry run - see what would be updated
  python3 set_default_key_type.py BUG --dry-run

  # Set all SKCC contacts to use BUG key
  python3 set_default_key_type.py BUG

  # Use STRAIGHT key
  python3 set_default_key_type.py STRAIGHT

  # Specify database location
  python3 set_default_key_type.py BUG ./logger.db
        '''
    )
    parser.add_argument('key_type', help='Key type to set (STRAIGHT, BUG, or SIDESWIPER)')
    parser.add_argument('database', nargs='?', help='Path to database file')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be updated without making changes')

    args = parser.parse_args()

    try:
        set_default_key_type(args.key_type, args.database, dry_run=args.dry_run)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
