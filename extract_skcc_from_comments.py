#!/usr/bin/env python3
"""
Extract SKCC numbers from comment fields and populate skcc_number field

Many contacts have SKCC data in comments like "SKCC: 27628T - FL" but the
skcc_number field is empty. This script extracts those numbers and populates
the proper field so SKCC awards will recognize them.
"""

import sys
import os
import re

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database import Database

def extract_skcc_from_comments(db_path=None, dry_run=False):
    """
    Extract SKCC numbers from comment fields and populate skcc_number field

    Args:
        db_path: Optional path to database (defaults to logger.db)
        dry_run: If True, show what would be updated without actually updating
    """
    # Initialize database
    if db_path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(script_dir, "logger.db")

    db = Database(db_path)
    cursor = db.conn.cursor()

    # Find contacts with SKCC in comments but no skcc_number field
    cursor.execute('''
        SELECT id, callsign, date, comment
        FROM contacts
        WHERE (comment LIKE '%SKCC:%' OR comment LIKE '%skcc:%')
        AND (skcc_number IS NULL OR skcc_number = '')
    ''')

    contacts = cursor.fetchall()

    if not contacts:
        print("No contacts found with SKCC in comments.")
        return

    print(f"{'='*70}")
    print(f"Found {len(contacts)} contacts with SKCC data in comments")
    print(f"{'='*70}\n")

    # Pattern to match SKCC numbers in comments
    # Matches: "SKCC: 27628T" or "SKCC:27628T" or "skcc: 12345C"
    skcc_pattern = re.compile(r'SKCC:\s*(\d+[CTSX]?\d*)', re.IGNORECASE)

    updated_count = 0
    not_found_count = 0

    for contact_id, callsign, date, comment in contacts:
        # Try to extract SKCC number from comment
        match = skcc_pattern.search(comment)

        if match:
            skcc_number = match.group(1).upper().strip()

            if dry_run:
                print(f"Would update: {callsign:10} {date:12} SKCC: {skcc_number}")
            else:
                # Update the contact
                cursor.execute('''
                    UPDATE contacts
                    SET skcc_number = ?
                    WHERE id = ?
                ''', (skcc_number, contact_id))
                updated_count += 1
                print(f"✓ Updated: {callsign:10} {date:12} SKCC: {skcc_number}")
        else:
            not_found_count += 1
            if not_found_count <= 5:  # Only show first few
                print(f"  Could not parse: {callsign:10} {date:12} Comment: {comment[:50]}")

    # Commit changes
    if not dry_run:
        db.conn.commit()

    # Summary
    print(f"\n{'='*70}")
    print(f"Summary:")
    print(f"  SKCC numbers extracted:    {updated_count}")
    print(f"  Could not parse:           {not_found_count}")
    print(f"{'='*70}")

    if dry_run:
        print("\nThis was a DRY RUN. No changes were made.")
        print("Run without --dry-run to apply changes.")
    elif updated_count > 0:
        print(f"\n✓ Successfully updated {updated_count} contacts!")
        print("\nNOTE: You still need to set the key_type field for these contacts.")
        print("SKCC awards require both skcc_number AND key_type (STRAIGHT, BUG, or SIDESWIPER).")
        print("\nYou can set a default key type for all SKCC contacts with:")
        print("  python3 set_default_key_type.py BUG")

    db.close()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Extract SKCC numbers from comment fields',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Dry run - see what would be updated
  python3 extract_skcc_from_comments.py --dry-run

  # Actually update the database
  python3 extract_skcc_from_comments.py

  # Specify database location
  python3 extract_skcc_from_comments.py ./logger.db
        '''
    )
    parser.add_argument('database', nargs='?', help='Path to database file')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be updated without making changes')

    args = parser.parse_args()

    try:
        extract_skcc_from_comments(args.database, dry_run=args.dry_run)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
