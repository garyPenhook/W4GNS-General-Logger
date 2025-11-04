#!/usr/bin/env python3
"""
Diagnostic script to check QRZ configuration
"""

import os
import sys

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config import Config

def main():
    print("QRZ Configuration Diagnostic")
    print("=" * 60)
    print()

    # Create config object
    config = Config()

    print(f"Config file path: {config.config_path}")
    print(f"Config file exists: {os.path.exists(config.config_path)}")
    print()

    # Check QRZ settings
    qrz_username = config.get('qrz.username')
    qrz_password = config.get('qrz.password')
    qrz_api_key = config.get('qrz.api_key')
    qrz_enable_lookup = config.get('qrz.enable_lookup', False)
    qrz_auto_upload = config.get('qrz.auto_upload', False)

    print("QRZ Configuration Values:")
    print("-" * 60)
    print(f"Username: '{qrz_username}'")
    print(f"  - Is None: {qrz_username is None}")
    print(f"  - Is empty string: {qrz_username == ''}")
    print(f"  - Is falsy: {not qrz_username}")
    print(f"  - Length: {len(qrz_username) if qrz_username else 0}")
    print()

    print(f"Password: '{'*' * len(qrz_password) if qrz_password else ''}'")
    print(f"  - Is None: {qrz_password is None}")
    print(f"  - Is empty string: {qrz_password == ''}")
    print(f"  - Is falsy: {not qrz_password}")
    print(f"  - Length: {len(qrz_password) if qrz_password else 0}")
    print()

    print(f"API Key: '{qrz_api_key[:10] + '...' if qrz_api_key and len(qrz_api_key) > 10 else qrz_api_key}'")
    print(f"  - Is None: {qrz_api_key is None}")
    print(f"  - Is empty string: {qrz_api_key == ''}")
    print(f"  - Is falsy: {not qrz_api_key}")
    print()

    print(f"Enable Lookup: {qrz_enable_lookup}")
    print(f"Auto Upload: {qrz_auto_upload}")
    print()

    # Check the validation condition used in logging_tab_enhanced.py
    print("Validation Check Results:")
    print("-" * 60)

    if not qrz_enable_lookup:
        print("❌ QRZ lookup is DISABLED in settings")
    else:
        print("✅ QRZ lookup is ENABLED in settings")

    if not qrz_username or not qrz_password:
        print("❌ VALIDATION FAILS: Username or password is empty/None")
        if not qrz_username:
            print("   - Username is missing or empty")
        if not qrz_password:
            print("   - Password is missing or empty")
    else:
        print("✅ VALIDATION PASSES: Both username and password are set")

    print()
    print("Full configuration data:")
    print("-" * 60)
    import json
    print(json.dumps(config.data, indent=2))

if __name__ == '__main__':
    main()
