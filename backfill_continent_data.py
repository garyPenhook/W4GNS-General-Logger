#!/usr/bin/env python3
"""
Backfill continent data for existing contacts in the database.

This script updates all contacts in the database that are missing continent
information by looking up the DXCC data from their callsign prefix.
"""

import sqlite3
import os
from src.dxcc import lookup_dxcc


def backfill_continent_data(db_path=None):
    """
    Backfill continent data for all contacts in the database

    Args:
        db_path: Path to the database file (default: logger.db in project root)
    """
    # Get database path
    if db_path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(script_dir, "logger.db")

    if not os.path.exists(db_path):
        print(f"Database not found at: {db_path}")
        return

    print(f"Connecting to database: {db_path}")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get all contacts
    cursor.execute("SELECT id, callsign, continent, country FROM contacts")
    contacts = cursor.fetchall()

    total_contacts = len(contacts)
    print(f"Found {total_contacts} contacts in database")

    # Track statistics
    updated = 0
    already_had_continent = 0
    no_dxcc_match = 0
    errors = 0

    # Process each contact
    for contact in contacts:
        contact_id = contact['id']
        callsign = contact['callsign']
        current_continent = contact['continent']
        current_country = contact['country']

        # Skip if already has continent data
        if current_continent and current_continent.strip():
            already_had_continent += 1
            continue

        # Lookup DXCC info
        try:
            dxcc_info = lookup_dxcc(callsign)

            if dxcc_info:
                continent = dxcc_info.get('continent', '')
                country = dxcc_info.get('country', '')
                cq_zone = dxcc_info.get('cq_zone', '')
                itu_zone = dxcc_info.get('itu_zone', '')

                # Update the contact
                cursor.execute('''
                    UPDATE contacts
                    SET continent = ?,
                        country = CASE WHEN country IS NULL OR country = '' THEN ? ELSE country END,
                        cq_zone = CASE WHEN cq_zone IS NULL OR cq_zone = '' THEN ? ELSE cq_zone END,
                        itu_zone = CASE WHEN itu_zone IS NULL OR itu_zone = '' THEN ? ELSE itu_zone END
                    WHERE id = ?
                ''', (continent, country, str(cq_zone), str(itu_zone), contact_id))

                updated += 1
                print(f"✓ Updated {callsign:12} -> {continent} ({country})")
            else:
                no_dxcc_match += 1
                print(f"✗ No DXCC match for {callsign}")

        except Exception as e:
            errors += 1
            print(f"✗ Error processing {callsign}: {e}")

    # Commit changes
    conn.commit()
    conn.close()

    # Print summary
    print("\n" + "="*60)
    print("Backfill Summary:")
    print("="*60)
    print(f"Total contacts:              {total_contacts}")
    print(f"Already had continent data:  {already_had_continent}")
    print(f"Updated with continent data: {updated}")
    print(f"No DXCC match found:         {no_dxcc_match}")
    print(f"Errors:                      {errors}")
    print("="*60)

    if updated > 0:
        print(f"\n✓ Successfully updated {updated} contacts!")
        print("  Your WAC (Worked All Continents) tracking should now be complete.")
    elif already_had_continent == total_contacts:
        print("\n✓ All contacts already have continent data!")
    else:
        print("\n⚠ No updates were made.")


if __name__ == "__main__":
    import sys

    print("="*60)
    print("W4GNS General Logger - Continent Data Backfill")
    print("="*60)
    print()

    # Allow custom database path from command line
    db_path = sys.argv[1] if len(sys.argv) > 1 else None

    backfill_continent_data(db_path)
