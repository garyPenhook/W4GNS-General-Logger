#!/usr/bin/env python3
"""
Test script to debug QRZ connection issues
"""

import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

def test_qrz_login(username, password):
    """Test QRZ login and show detailed response"""

    print(f"Testing QRZ login for user: {username}")
    print("-" * 60)

    try:
        # Build the request exactly as QRZ spec requires
        params = urllib.parse.urlencode({
            'username': username,
            'password': password,
            'agent': 'W4GNS-General-Logger-1.0'
        })

        url = f"https://xmldata.qrz.com/xml/current/?{params}"
        print(f"Request URL: {url[:50]}...[password hidden]")
        print()

        # Create request with User-Agent
        request = urllib.request.Request(url)
        request.add_header('User-Agent', 'W4GNS-General-Logger/1.0')

        # Make the request
        with urllib.request.urlopen(request, timeout=10) as response:
            xml_data = response.read().decode('utf-8')

        print("Raw XML Response:")
        print("-" * 60)
        print(xml_data)
        print("-" * 60)
        print()

        # Parse the XML
        root = ET.fromstring(xml_data)

        # Check for session element
        session = root.find('.//Session')
        if session is None:
            print("ERROR: No Session element found in response")
            return False

        print("Session element found!")
        print()

        # Check all session child elements
        print("Session Contents:")
        for child in session:
            print(f"  {child.tag}: {child.text}")
        print()

        # Check for error
        error_elem = session.find('Error')
        if error_elem is not None and error_elem.text:
            print(f"❌ QRZ Error: {error_elem.text}")
            return False

        # Check for session key
        key_elem = session.find('Key')
        if key_elem is not None and key_elem.text:
            print(f"✅ Session Key: {key_elem.text[:20]}...")

            # Check subscription info
            sub_exp = session.find('SubExp')
            if sub_exp is not None and sub_exp.text:
                print(f"📅 Subscription: {sub_exp.text}")

            return True
        else:
            print("❌ No session key found in response")
            return False

    except urllib.error.HTTPError as e:
        print(f"❌ HTTP Error: {e.code} {e.reason}")
        print(f"   Response: {e.read().decode('utf-8')}")
        return False
    except urllib.error.URLError as e:
        print(f"❌ Network Error: {e.reason}")
        return False
    except ET.ParseError as e:
        print(f"❌ XML Parse Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("QRZ.com Login Test")
    print("=" * 60)
    print()

    username = input("Enter your QRZ username: ").strip()
    password = input("Enter your QRZ password: ").strip()
    print()

    if not username or not password:
        print("Username and password are required!")
    else:
        success = test_qrz_login(username, password)
        print()
        print("=" * 60)
        if success:
            print("✅ LOGIN SUCCESSFUL!")
        else:
            print("❌ LOGIN FAILED - See details above")
