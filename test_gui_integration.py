#!/usr/bin/env python3
"""
Simple test to verify GUI integration without running full app
"""

import sys
import os

# Test imports
print("Testing imports...")
try:
    from src.needed_analyzer import NeededContactsAnalyzer
    print("✓ NeededContactsAnalyzer imported")
except Exception as e:
    print(f"✗ Failed to import NeededContactsAnalyzer: {e}")
    sys.exit(1)

try:
    from src.notifier import get_notifier
    print("✓ Notifier imported")
except Exception as e:
    print(f"✗ Failed to import Notifier: {e}")
    sys.exit(1)

# Check if logging_tab_enhanced has the changes
print("\nChecking logging_tab_enhanced.py...")
with open('src/gui/logging_tab_enhanced.py', 'r') as f:
    content = f.read()

    checks = [
        ('NeededContactsAnalyzer import', 'from src.needed_analyzer import NeededContactsAnalyzer'),
        ('Analyzer initialization', 'self.analyzer = NeededContactsAnalyzer'),
        ('High priority tag', "tag_configure('high_priority'"),
        ('Analyzer in add_dx_spot', 'analysis = self.analyzer.analyze_spot'),
        ('Cache clear on save', 'self.analyzer.clear_cache()'),
    ]

    for name, check_str in checks:
        if check_str in content:
            print(f"✓ {name}")
        else:
            print(f"✗ MISSING: {name}")

print("\n" + "="*70)
print("INTEGRATION STATUS:")
print("="*70)

# Final verdict
if all(check_str in content for _, check_str in checks):
    print("✅ All integrations present - Smart filtering IS installed!")
    print()
    print("If you're not seeing changes, make sure:")
    print("  1. You restarted the app after pulling changes")
    print("  2. You're connected to a DX cluster")
    print("  3. Spots are actually appearing in the 'DX Cluster Spots' section")
    print("  4. You have some contacts in your log (to compare against)")
else:
    print("❌ Some integrations missing - reinstallation may be needed")

print()
