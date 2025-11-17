#!/usr/bin/env python3
"""
Quick script to restore database from ADIF backup
"""
import sys
from src.database import Database
from src.adif import ADIFParser

def restore_from_adif(adif_file):
    """Restore database from ADIF file"""
    print(f"Restoring database from {adif_file}...")

    # Parse ADIF file
    parser = ADIFParser()
    contacts = parser.parse_file(adif_file)
    print(f"Found {len(contacts)} contacts in ADIF file")

    # Initialize database (this will create new database with DELETE journal mode)
    db = Database()
    print("Database initialized with DELETE journal mode")

    # Import contacts in batches
    batch_size = 100
    total_imported = 0

    for i in range(0, len(contacts), batch_size):
        batch = contacts[i:i+batch_size]
        try:
            db.add_contacts_batch(batch)
            total_imported += len(batch)
            if (i + batch_size) % 1000 == 0:
                print(f"Imported {total_imported} contacts...")
        except Exception as e:
            print(f"Error importing batch at position {i}: {e}")
            continue

    print(f"\nSuccessfully imported {total_imported} contacts")

    # Verify database
    cursor = db.conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM contacts")
    count = cursor.fetchone()[0]
    print(f"Database now has {count} contacts")

    # Verify journal mode
    cursor.execute("PRAGMA journal_mode")
    journal_mode = cursor.fetchone()[0]
    print(f"Journal mode: {journal_mode}")

    cursor.execute("PRAGMA synchronous")
    sync_mode = cursor.fetchone()[0]
    print(f"Synchronous mode: {sync_mode}")

    cursor.execute("PRAGMA integrity_check")
    integrity = cursor.fetchone()[0]
    print(f"Integrity check: {integrity}")

    db.close()
    print("\nRestore complete!")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 restore_from_adif.py <adif_file>")
        sys.exit(1)

    restore_from_adif(sys.argv[1])
