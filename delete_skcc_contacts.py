#!/usr/bin/env python3
"""
Delete all contacts with SKCC numbers so they can be re-imported

CAUTION: This will permanently delete contacts from your database!
Make a backup first!
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database import Database

def delete_skcc_contacts(db_path=None, confirm=True):
    """
    Delete all contacts that have SKCC numbers

    Args:
        db_path: Optional path to database (defaults to logger.db)
        confirm: If True, ask for user confirmation before deleting
    """
    # Initialize database
    if db_path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(script_dir, "logger.db")

    db = Database(db_path)
    cursor = db.conn.cursor()

    # Count SKCC contacts
    cursor.execute('''
        SELECT COUNT(*) FROM contacts
        WHERE skcc_number IS NOT NULL AND skcc_number != ''
    ''')
    skcc_count = cursor.fetchone()[0]

    # Show some examples
    cursor.execute('''
        SELECT callsign, date, skcc_number, key_type
        FROM contacts
        WHERE skcc_number IS NOT NULL AND skcc_number != ''
        LIMIT 10
    ''')
    examples = cursor.fetchall()

    print(f"{'='*60}")
    print(f"Found {skcc_count} contacts with SKCC numbers")
    print(f"{'='*60}\n")

    if examples:
        print("Examples (first 10):")
        for row in examples:
            call, date, skcc, key = row
            key_str = key or '(no key_type)'
            print(f"  {call:10} {date:12} SKCC:{skcc:10} Key:{key_str}")
        print()

    if skcc_count == 0:
        print("No SKCC contacts found. Nothing to delete.")
        db.close()
        return

    # Confirm deletion
    if confirm:
        response = input(f"\n⚠️  DELETE {skcc_count} contacts? This cannot be undone! (yes/no): ")
        if response.lower() != 'yes':
            print("Deletion cancelled.")
            db.close()
            return

    # Delete SKCC contacts
    print(f"\nDeleting {skcc_count} SKCC contacts...")
    cursor.execute('''
        DELETE FROM contacts
        WHERE skcc_number IS NOT NULL AND skcc_number != ''
    ''')

    deleted = cursor.rowcount
    db.conn.commit()

    print(f"✓ Deleted {deleted} contacts")
    print(f"\nYou can now re-import your SKCC Logger ADIF file.")
    print(f"The new import will correctly populate SKCC numbers and key types.")

    db.close()


if __name__ == '__main__':
    print("=" * 60)
    print("Delete SKCC Contacts")
    print("=" * 60)
    print("\n⚠️  WARNING: This will permanently delete contacts!")
    print("Make sure you have a backup of your database or ADIF file.")
    print()

    db_path = sys.argv[1] if len(sys.argv) > 1 else None

    try:
        delete_skcc_contacts(db_path, confirm=True)
    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
