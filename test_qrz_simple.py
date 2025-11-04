#!/usr/bin/env python3
"""
Simple direct QRZ test - bypasses all our code
"""

import urllib.request
import urllib.parse

print("=" * 60)
print("SIMPLE QRZ DIRECT TEST")
print("=" * 60)
print()

username = input("Enter QRZ username: ").strip()
password = input("Enter QRZ password: ")
print()

print("Testing QRZ XML API...")
print("-" * 60)

try:
    # Method 1: Try with POST (recommended for passwords)
    print("\n[TEST 1] Using POST method...")
    url = "https://xmldata.qrz.com/xml/current/"

    data = urllib.parse.urlencode({
        'username': username,
        'password': password,
        'agent': 'W4GNS-Logger-Test'
    }).encode('utf-8')

    request = urllib.request.Request(url, data=data, method='POST')
    request.add_header('User-Agent', 'W4GNS-Logger-Test/1.0')

    response = urllib.request.urlopen(request, timeout=10)
    xml = response.read().decode('utf-8')

    print("✅ Request successful!")
    print("\nResponse:")
    print(xml)
    print()

    # Check what we got
    if '<Key>' in xml:
        print("✅ SESSION KEY FOUND - Login successful!")
        key = xml.split('<Key>')[1].split('</Key>')[0]
        print(f"Session key: {key[:20]}...")
    elif '<Error>' in xml:
        error = xml.split('<Error>')[1].split('</Error>')[0]
        print(f"❌ QRZ Error: {error}")
    else:
        print("⚠️  Unexpected response format")

except urllib.error.HTTPError as e:
    print(f"❌ HTTP Error: {e.code} {e.reason}")
    print(f"Response: {e.read().decode('utf-8')}")

except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {e}")

print()
print("=" * 60)

# Also test what subscription they have
print("\nIMPORTANT: For XML API access, you need:")
print("• QRZ XML Logbook Data subscription")
print("• Not just regular QRZ membership")
print("• Check at: https://www.qrz.com/i/subscriptions.html")
print()
print("Do you have 'XML Logbook Data' subscription? (y/n): ", end='')
has_xml = input().strip().lower()

if has_xml == 'n':
    print()
    print("⚠️  That's the issue! You need XML Logbook Data subscription.")
    print("   Regular QRZ subscription is NOT the same as XML API access.")
    print("   Visit: https://www.qrz.com/i/subscriptions.html")
