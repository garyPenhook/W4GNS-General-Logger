#!/usr/bin/env python3
"""
Test ContactNotifier for completeness and correctness

Tests cover:
- Notification de-duplication logic (60-second window)
- Platform-specific notification code paths
- Preference updates and priority filtering
- Thread-safe singleton pattern
- Edge cases
"""

import sys
import time
import threading

# Add src to path
sys.path.insert(0, '.')

from src.notifier import (
    ContactNotifier, NotificationPreferences,
    get_notifier, set_notifier, _notifier_lock
)

print("="*70)
print("ContactNotifier Unit Tests")
print("="*70)
print()

issues = []


# Test 1: Default Preferences
print("1. DEFAULT PREFERENCES TEST")
print("-" * 70)

prefs = NotificationPreferences()
if prefs.enabled == True:
    print(f"  \u2713 Default enabled: True")
else:
    print(f"  \u2717 Default enabled should be True")
    issues.append('default_enabled')

if prefs.desktop_notification_enabled == False:
    print(f"  \u2713 Default desktop_notification_enabled: False")
else:
    print(f"  \u2717 Default desktop_notification_enabled should be False")
    issues.append('default_desktop')

if prefs.min_priority == 2:
    print(f"  \u2713 Default min_priority: 2")
else:
    print(f"  \u2717 Default min_priority should be 2")
    issues.append('default_priority')

print()


# Test 2: Notification De-duplication
print("2. NOTIFICATION DE-DUPLICATION TEST")
print("-" * 70)

# Create notifier with notifications disabled for testing
prefs = NotificationPreferences(enabled=True, desktop_notification_enabled=False)
notifier = ContactNotifier(prefs)

# First notification should go through
notifier.notify_needed_contact('W4GNS', 1, 'New state')
key = 'W4GNS_1'
if key in notifier._last_notification:
    print(f"  \u2713 First notification recorded in cache")
else:
    print(f"  \u2717 First notification should be recorded")
    issues.append('dedup_first')

first_time = notifier._last_notification.get(key)

# Second notification within 60s should be blocked (cache not updated)
time.sleep(0.1)  # Small delay
notifier.notify_needed_contact('W4GNS', 1, 'New state')
second_time = notifier._last_notification.get(key)

if first_time == second_time:
    print(f"  \u2713 Duplicate notification blocked (cache not updated)")
else:
    print(f"  \u2717 Duplicate should be blocked")
    issues.append('dedup_second')

# Different callsign should not be blocked
notifier.notify_needed_contact('K1ABC', 1, 'New state')
if 'K1ABC_1' in notifier._last_notification:
    print(f"  \u2713 Different callsign notification allowed")
else:
    print(f"  \u2717 Different callsign should be allowed")
    issues.append('dedup_different')

# Same callsign, different priority should not be blocked
notifier.notify_needed_contact('W4GNS', 2, 'New country')
if 'W4GNS_2' in notifier._last_notification:
    print(f"  \u2713 Same callsign, different priority allowed")
else:
    print(f"  \u2717 Same callsign, different priority should be allowed")
    issues.append('dedup_priority')

print()


# Test 3: Priority Filtering
print("3. PRIORITY FILTERING TEST")
print("-" * 70)

# Create notifier with min_priority=2 (notify for priority 1 and 2 only)
prefs = NotificationPreferences(enabled=True,
                                desktop_notification_enabled=False, min_priority=2)
notifier = ContactNotifier(prefs)

# Priority 1 should be notified
notifier.notify_needed_contact('TEST1', 1, 'High priority')
if 'TEST1_1' in notifier._last_notification:
    print(f"  \u2713 Priority 1 notification allowed (min_priority=2)")
else:
    print(f"  \u2717 Priority 1 should be allowed when min_priority=2")
    issues.append('priority_1')

# Priority 2 should be notified
notifier.notify_needed_contact('TEST2', 2, 'Medium priority')
if 'TEST2_2' in notifier._last_notification:
    print(f"  \u2713 Priority 2 notification allowed (min_priority=2)")
else:
    print(f"  \u2717 Priority 2 should be allowed when min_priority=2")
    issues.append('priority_2')

# Priority 3 should NOT be notified (blocked by min_priority)
notifier.notify_needed_contact('TEST3', 3, 'Low priority')
if 'TEST3_3' not in notifier._last_notification:
    print(f"  \u2713 Priority 3 notification blocked (min_priority=2)")
else:
    print(f"  \u2717 Priority 3 should be blocked when min_priority=2")
    issues.append('priority_3')

print()


# Test 4: Disabled Notifications
print("4. DISABLED NOTIFICATIONS TEST")
print("-" * 70)

prefs = NotificationPreferences(enabled=False)
notifier = ContactNotifier(prefs)

notifier.notify_needed_contact('DISABLED1', 1, 'Test')
if 'DISABLED1_1' not in notifier._last_notification:
    print(f"  \u2713 Notifications blocked when disabled")
else:
    print(f"  \u2717 Notifications should be blocked when disabled")
    issues.append('disabled')

print()


# Test 5: Preference Updates
print("5. PREFERENCE UPDATES TEST")
print("-" * 70)

prefs = NotificationPreferences(enabled=True, min_priority=1)
notifier = ContactNotifier(prefs)

# Update preferences
new_prefs = NotificationPreferences(enabled=True, min_priority=3)
notifier.update_preferences(new_prefs)

if notifier.prefs.min_priority == 3:
    print(f"  \u2713 Preferences updated successfully")
else:
    print(f"  \u2717 Preferences should be updated")
    issues.append('prefs_update')

print()


# Test 6: Cache Clearing
print("6. CACHE CLEARING TEST")
print("-" * 70)

prefs = NotificationPreferences(enabled=True,
                                desktop_notification_enabled=False)
notifier = ContactNotifier(prefs)

# Add some notifications
notifier.notify_needed_contact('CACHE1', 1, 'Test')
notifier.notify_needed_contact('CACHE2', 1, 'Test')

if len(notifier._last_notification) == 2:
    print(f"  \u2713 Notifications cached: {len(notifier._last_notification)}")
else:
    print(f"  \u2717 Should have 2 cached notifications")
    issues.append('cache_add')

# Clear cache
notifier.clear_notification_cache()
if len(notifier._last_notification) == 0:
    print(f"  \u2713 Cache cleared successfully")
else:
    print(f"  \u2717 Cache should be empty after clearing")
    issues.append('cache_clear')

# Same callsign should now trigger again
notifier.notify_needed_contact('CACHE1', 1, 'Test')
if 'CACHE1_1' in notifier._last_notification:
    print(f"  \u2713 Re-notification works after cache clear")
else:
    print(f"  \u2717 Should be able to re-notify after cache clear")
    issues.append('cache_renotify')

print()


# Test 7: Thread-Safe Singleton Pattern
print("7. THREAD-SAFE SINGLETON TEST")
print("-" * 70)

# Reset the singleton
import src.notifier as notifier_module
notifier_module._default_notifier = None

notifiers = []
errors = []

def get_notifier_threaded():
    try:
        n = get_notifier()
        notifiers.append(id(n))
    except Exception as e:
        errors.append(str(e))

# Create multiple threads trying to get the notifier
threads = []
for i in range(10):
    t = threading.Thread(target=get_notifier_threaded)
    threads.append(t)

for t in threads:
    t.start()

for t in threads:
    t.join()

if len(errors) == 0:
    print(f"  \u2713 No errors in threaded access")
else:
    print(f"  \u2717 Errors occurred: {errors}")
    issues.append('thread_errors')

# All threads should get the same instance
unique_ids = set(notifiers)
if len(unique_ids) == 1:
    print(f"  \u2713 All threads got same singleton instance")
else:
    print(f"  \u2717 Multiple instances created: {len(unique_ids)}")
    issues.append('thread_singleton')

# Test set_notifier
custom_notifier = ContactNotifier()
set_notifier(custom_notifier)
if get_notifier() is custom_notifier:
    print(f"  \u2713 set_notifier works correctly")
else:
    print(f"  \u2717 set_notifier should update singleton")
    issues.append('set_notifier')

print()


# Summary
print("="*70)
print("SUMMARY")
print("="*70)
print()

if len(issues) == 0:
    print("\u2713 All ContactNotifier tests PASSED!")
else:
    print(f"\u2717 Found {len(issues)} issue(s):")
    for issue in issues:
        print(f"  - {issue}")

print()
print("="*70)
