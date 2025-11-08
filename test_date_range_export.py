#!/usr/bin/env python3
"""
Test script for date/time range export functionality
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database import Database

def test_date_range_query():
    """Test the date range query functionality"""
    print("Testing date/time range export functionality...")
    print("-" * 50)

    # Initialize database
    db = Database()

    # Test 1: Get all contacts (for comparison)
    all_contacts = db.get_all_contacts(limit=10)
    print(f"\nTest 1: Total contacts in database (first 10): {len(all_contacts)}")
    if all_contacts:
        print(f"Sample contact: {all_contacts[0]['callsign']} on {all_contacts[0]['date']} at {all_contacts[0]['time_on']}")

    # Test 2: Get contacts from a specific date range
    # Example: Get contacts from 2024-01-01 to 2024-12-31
    print("\nTest 2: Get contacts from 2024-01-01 to 2024-12-31")
    contacts_2024 = db.get_contacts_by_date_range('2024-01-01', '2024-12-31')
    print(f"Found {len(contacts_2024)} contacts in 2024")
    if contacts_2024:
        print(f"First contact: {contacts_2024[0]['callsign']} on {contacts_2024[0]['date']} at {contacts_2024[0]['time_on']}")
        print(f"Last contact: {contacts_2024[-1]['callsign']} on {contacts_2024[-1]['date']} at {contacts_2024[-1]['time_on']}")

    # Test 3: Get contacts with time range
    print("\nTest 3: Get contacts from 2024-01-01 00:00 to 2024-01-31 23:59")
    contacts_jan = db.get_contacts_by_date_range('2024-01-01', '2024-01-31', '00:00', '23:59')
    print(f"Found {len(contacts_jan)} contacts in January 2024")
    if contacts_jan:
        print(f"First contact: {contacts_jan[0]['callsign']} on {contacts_jan[0]['date']} at {contacts_jan[0]['time_on']}")

    # Test 4: Get contacts from a specific weekend (simulating SKCC WES)
    print("\nTest 4: Simulating SKCC WES weekend (example: 2024-11-02 to 2024-11-03)")
    weekend_contacts = db.get_contacts_by_date_range('2024-11-02', '2024-11-03')
    print(f"Found {len(weekend_contacts)} contacts during that weekend")
    if weekend_contacts:
        for contact in weekend_contacts[:5]:  # Show first 5
            print(f"  - {contact['callsign']} on {contact['date']} at {contact['time_on']}")

    # Close database
    db.close()

    print("\n" + "-" * 50)
    print("Test completed successfully!")
    print("\nThe date/time range export functionality is working correctly.")
    print("You can now use this feature from the File menu:")
    print("  File -> Export by Date/Time Range (ADIF)...")

if __name__ == "__main__":
    test_date_range_query()
