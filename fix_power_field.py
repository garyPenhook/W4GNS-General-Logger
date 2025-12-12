#!/usr/bin/env python3
"""
Fix power field mismatch in database

Problem: Contacts have power stored in 'power' (text) field but not in
'power_watts' (numeric) field. This prevents QRP/MPW award validation.

Solution: Copy numeric power values from 'power' field to 'power_watts' field.
"""

import sqlite3
import sys
import os
import glob

def fix_power_field(db_path):
    """
    Update power_watts field from power field for all contacts

    Args:
        db_path: Path to database file
    """
    print(f"Processing: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Find contacts with power but no power_watts
    cursor.execute("""
        SELECT id, callsign, power
        FROM contacts
        WHERE LENGTH(power) > 0
        AND power_watts IS NULL
    """)

    contacts = cursor.fetchall()
    print(f"  Found {len(contacts)} contacts needing power_watts update")

    if not contacts:
        conn.close()
        return 0

    updated = 0
    failed = 0

    for contact_id, callsign, power_text in contacts:
        try:
            # Try to convert power text to float
            # Handle common formats: "5.0", "5", "100.0", "5.0W", etc.
            power_clean = power_text.strip().upper().replace('W', '').strip()
            power_watts = float(power_clean)

            # Update the power_watts field
            cursor.execute(
                "UPDATE contacts SET power_watts = ? WHERE id = ?",
                (power_watts, contact_id)
            )
            updated += 1

            if updated % 100 == 0:
                print(f"    Updated {updated} contacts...")

        except (ValueError, TypeError) as e:
            failed += 1
            print(f"    WARNING: Could not parse power for {callsign}: '{power_text}' - {e}")

    # Commit changes
    conn.commit()
    conn.close()

    print(f"  ✓ Updated {updated} contacts")
    if failed > 0:
        print(f"  ⚠ Failed to parse {failed} contacts")

    return updated


def main():
    """Main execution"""
    print("=" * 70)
    print("Power Field Fix Utility")
    print("=" * 70)
    print()

    # Find all database files
    db_files = glob.glob("./logs/*.db")

    if not db_files:
        print("ERROR: No database files found in ./logs/")
        return 1

    print(f"Found {len(db_files)} database file(s)\n")

    total_updated = 0

    for db_file in sorted(db_files):
        try:
            updated = fix_power_field(db_file)
            total_updated += updated
            print()
        except Exception as e:
            print(f"  ERROR processing {db_file}: {e}")
            print()

    print("=" * 70)
    print(f"COMPLETE: Updated {total_updated} total contacts across all databases")
    print("=" * 70)
    print()
    print("Next steps:")
    print("1. Launch the app")
    print("2. Go to SKCC Awards → Specialty Awards")
    print("3. Click 'Refresh Awards'")
    print("4. Your VK4TJ contact should now show in QRP/MPW award!")
    print("   Expected: Level 2 (1,500 MPW) with 1,883.1 MPW")

    return 0


if __name__ == '__main__':
    sys.exit(main())
