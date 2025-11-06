#!/usr/bin/env python3
"""
Database Fix Script - Removes corrupted database files
Run this from your W4GNS-General-Logger-main directory
"""
import os
import shutil
from pathlib import Path

print("=" * 60)
print("W4GNS Logger - Database Fix Script")
print("=" * 60)

# Get current directory
current_dir = Path.cwd()
print(f"\nCurrent directory: {current_dir}")

# Database files to check
db_files = ['logger.db', 'logbook.db', 'w4gns_logger.db']

# Create backup directory
backup_dir = current_dir / 'old_databases'
backup_dir.mkdir(exist_ok=True)
print(f"Backup directory: {backup_dir}")

# Check and move database files
found_files = []
for db_file in db_files:
    db_path = current_dir / db_file
    if db_path.exists():
        found_files.append(db_file)
        backup_path = backup_dir / f"{db_file}.corrupted"
        print(f"\n✓ Found: {db_file}")
        print(f"  Moving to: {backup_path}")
        shutil.move(str(db_path), str(backup_path))
        print(f"  ✓ Moved successfully")

if not found_files:
    print("\n✓ No database files found - ready to create fresh database")
else:
    print(f"\n✓ Moved {len(found_files)} database file(s) to backup")

# Verify no .db files remain
remaining_dbs = list(current_dir.glob('*.db'))
if remaining_dbs:
    print("\n⚠ WARNING: Some .db files still exist:")
    for db in remaining_dbs:
        print(f"  - {db.name}")
else:
    print("\n✓ No .db files remaining in directory")

print("\n" + "=" * 60)
print("Done! You can now run: python main.py")
print("=" * 60)
