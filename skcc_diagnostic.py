#!/usr/bin/env python3
"""
SKCC Awards Diagnostic Tool
Run this script to diagnose why your SKCC awards aren't showing credit.

Usage:
    python3 skcc_diagnostic.py
"""

from src.database import Database
from src.config import Config
import sys

def main():
    print("=" * 70)
    print("SKCC AWARDS DIAGNOSTIC TOOL")
    print("=" * 70)

    # Load configuration
    config = Config()
    db = Database()

    # Check critical configuration settings
    print("\n📋 CONFIGURATION CHECK:")
    print("-" * 70)

    join_date = config.get('skcc.join_date', '')
    centurion_date = config.get('skcc.centurion_date', '')
    tribune_x8_date = config.get('skcc.tribune_x8_date', '')

    config_ok = True

    if join_date:
        print(f"✓ SKCC Join Date: {join_date}")
    else:
        print("❌ SKCC Join Date: NOT SET")
        print("   ⚠️  CRITICAL: All awards require your SKCC join date!")
        config_ok = False

    if centurion_date:
        print(f"✓ Centurion Date: {centurion_date}")
    else:
        print("⚪ Centurion Date: NOT SET")
        print("   ℹ️  Required for Tribune and Senator awards")

    if tribune_x8_date:
        print(f"✓ Tribune x8 Date: {tribune_x8_date}")
    else:
        print("⚪ Tribune x8 Date: NOT SET (only needed for Senator)")

    # Check contacts in database
    print("\n📊 CONTACT DATA ANALYSIS:")
    print("-" * 70)

    contacts = db.get_all_contacts(limit=999999)
    contacts_list = list(contacts)
    total_contacts = len(contacts_list)

    print(f"Total contacts in log: {total_contacts:,}")

    if total_contacts == 0:
        print("\n⚠️  No contacts found in database!")
        print("   Make sure your ADIF file was imported successfully.")
    else:
        # Analyze contacts
        cw_contacts = 0
        skcc_contacts = 0
        key_type_contacts = 0
        valid_skcc_contacts = 0

        for contact in contacts_list:
            mode = contact['mode']
            skcc_number = contact['skcc_number']
            key_type = contact['key_type']

            if mode and mode.upper() == 'CW':
                cw_contacts += 1

            if skcc_number and skcc_number.strip():
                skcc_contacts += 1

                # Check if it's a valid SKCC contact
                if mode and mode.upper() == 'CW' and key_type:
                    valid_skcc_contacts += 1

            if key_type and key_type.strip():
                key_type_contacts += 1

        print(f"\nCW Mode contacts: {cw_contacts:,} ({cw_contacts/total_contacts*100:.1f}%)")
        print(f"Contacts with SKCC numbers: {skcc_contacts:,} ({skcc_contacts/total_contacts*100:.1f}%)")
        print(f"Contacts with Key Types: {key_type_contacts:,} ({key_type_contacts/total_contacts*100:.1f}%)")
        print(f"Valid SKCC QSOs (CW + SKCC# + Key): {valid_skcc_contacts:,} ({valid_skcc_contacts/total_contacts*100:.1f}%)")

        # Sample contacts
        print(f"\n🔍 SAMPLE CONTACTS (first 3):")
        print("-" * 70)
        for i, contact in enumerate(contacts_list[:3]):
            print(f"\nContact {i+1}:")
            print(f"  Callsign: {contact['callsign']}")
            print(f"  Date: {contact['date']}")
            print(f"  Mode: {contact['mode'] or '(not set)'}")
            print(f"  SKCC Number: {contact['skcc_number'] or '(not set)'}")
            print(f"  Key Type: {contact['key_type'] or '(not set)'}")

    # Diagnosis and recommendations
    print("\n\n🔧 DIAGNOSIS & RECOMMENDATIONS:")
    print("=" * 70)

    issues_found = []
    recommendations = []

    if not join_date:
        issues_found.append("SKCC Join Date is not set")
        recommendations.append(
            "❶ Set SKCC Join Date:\n"
            "   • Open SKCC Awards tab in W4GNS Logger\n"
            "   • Find 'Your SKCC Information' section\n"
            "   • Enter your SKCC Join Date in YYYYMMDD format\n"
            "   • Example: 20200315 (for March 15, 2020)\n"
            "   • Click 'Save'\n"
            "   • Click 'Refresh Awards' button"
        )

    if not centurion_date and tribune_x8_date:
        issues_found.append("Centurion Date missing (you have Tribune x8 set)")
        recommendations.append(
            "❷ Set Centurion Date:\n"
            "   • You achieved Centurion BEFORE Tribune\n"
            "   • Enter the date when you reached 100 members\n"
            "   • Must be earlier than your Tribune x8 date\n"
            "   • Click 'Save' and 'Refresh Awards'"
        )

    if total_contacts > 0 and skcc_contacts == 0:
        issues_found.append("No contacts have SKCC numbers")
        recommendations.append(
            "❸ Add SKCC Numbers:\n"
            "   • Your contacts are missing SKCC number data\n"
            "   • Check your logging program's ADIF export settings\n"
            "   • Look for SKCC number field or APP_SKCC_NUMBER\n"
            "   • You may need to re-export and re-import your log"
        )

    if total_contacts > 0 and cw_contacts < total_contacts * 0.5:
        issues_found.append(f"Only {cw_contacts} of {total_contacts} contacts are CW mode")
        recommendations.append(
            "❹ Mode Field:\n"
            "   • SKCC awards require CW mode\n"
            "   • Make sure MODE field is set to 'CW' in your contacts\n"
            "   • Check ADIF export includes MODE field"
        )

    if total_contacts > 0 and key_type_contacts == 0:
        issues_found.append("No contacts have Key Types")
        recommendations.append(
            "❺ Add Key Type Information:\n"
            "   • SKCC requires key type (STRAIGHT, BUG, SIDESWIPER)\n"
            "   • This field may need to be added manually\n"
            "   • Check if your logging program supports key type field"
        )

    if issues_found:
        print("\n❌ ISSUES FOUND:")
        for i, issue in enumerate(issues_found, 1):
            print(f"   {i}. {issue}")

        print("\n✅ HOW TO FIX:")
        for rec in recommendations:
            print(f"\n{rec}")

        return 1  # Exit with error code
    else:
        print("\n✅ Configuration appears correct!")
        if total_contacts > 0:
            print(f"   You have {skcc_contacts:,} SKCC contacts ready for award validation.")
        print("   Try clicking 'Refresh Awards' button in the SKCC Awards tab.")
        return 0  # Success

if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n❌ Error running diagnostic: {e}")
        sys.exit(1)
