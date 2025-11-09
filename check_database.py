#!/usr/bin/env python3
"""Check database contents for Tribune award debugging"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database import Database

def check_database():
    """Check database contents"""

    db = Database("logger.db")
    cursor = db.conn.cursor()

    # Check total contacts
    cursor.execute("SELECT COUNT(*) FROM contacts")
    total = cursor.fetchone()[0]
    print(f"Total contacts: {total}")

    # Check SKCC contacts
    cursor.execute("SELECT COUNT(*) FROM contacts WHERE skcc_number IS NOT NULL AND skcc_number != ''")
    skcc_count = cursor.fetchone()[0]
    print(f"SKCC contacts: {skcc_count}")

    # Check CW contacts with SKCC numbers
    cursor.execute("SELECT COUNT(*) FROM contacts WHERE mode = 'CW' AND skcc_number IS NOT NULL AND skcc_number != ''")
    cw_skcc = cursor.fetchone()[0]
    print(f"CW SKCC contacts: {cw_skcc}")

    # Show sample SKCC contacts
    cursor.execute("""
        SELECT callsign, date, skcc_number, mode, key_type
        FROM contacts
        WHERE skcc_number IS NOT NULL AND skcc_number != ''
        LIMIT 10
    """)

    print("\nSample SKCC contacts:")
    for row in cursor.fetchall():
        print(f"  {row[0]} - {row[1]} - SKCC#{row[2]} - {row[3]} - Key:{row[4]}")

    # Check config
    cursor.execute("SELECT key, value FROM config WHERE key LIKE 'skcc.%'")
    print("\nSKCC Config:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}")

    db.close()

if __name__ == '__main__':
    try:
        check_database()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
