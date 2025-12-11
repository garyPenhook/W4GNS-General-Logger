"""
Notification System for Needed Contacts

Provides visual notifications when high-priority contacts appear.
"""

import logging
import time
import html
from typing import Optional
from dataclasses import dataclass
import subprocess
import platform
import threading

logger = logging.getLogger(__name__)


@dataclass
class NotificationPreferences:
    """User preferences for notifications"""
    enabled: bool = True
    desktop_notification_enabled: bool = False
    min_priority: int = 2  # Notify for priority 1 (high) and 2 (medium)


class ContactNotifier:
    """
    Handles notifications for needed contacts.

    Supports:
    - Desktop notifications (Linux/macOS/Windows)
    - Priority-based filtering
    """

    def __init__(self, preferences: Optional[NotificationPreferences] = None):
        """
        Initialize the notifier.

        Args:
            preferences: Notification preferences
        """
        self.prefs = preferences or NotificationPreferences()
        self._last_notification = {}  # Prevents duplicate notifications

    def notify_needed_contact(self, callsign: str, priority: int, reason: str):
        """
        Send notification for a needed contact.

        Args:
            callsign: Station callsign
            priority: Priority level (1=high, 2=medium, 3=low)
            reason: Why this contact is needed
        """
        if not self.prefs.enabled:
            return

        # Check priority threshold
        if priority > self.prefs.min_priority:
            return

        # Prevent duplicate notifications (within 60 seconds)
        current_time = time.time()
        key = f"{callsign}_{priority}"
        if key in self._last_notification:
            if current_time - self._last_notification[key] < 60:
                return

        self._last_notification[key] = current_time

        # Send desktop notifications
        if self.prefs.desktop_notification_enabled:
            self._show_desktop_notification(callsign, priority, reason)

    def _show_desktop_notification(self, callsign: str, priority: int, reason: str):
        """Show desktop notification"""
        try:
            os_name = platform.system()
            priority_text = "HIGH PRIORITY" if priority == 1 else "MEDIUM PRIORITY" if priority == 2 else "LOW PRIORITY"
            title = f"Needed Contact: {callsign}"
            message = f"{priority_text}\n{reason}"

            if os_name == 'Linux':
                # Use notify-send on Linux
                subprocess.run(['notify-send', '-u', 'normal', '-t', '5000',
                              title, message],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif os_name == 'Darwin':  # macOS
                # Use osascript for macOS notifications
                # Escape backslashes and double quotes in title and message
                escaped_title = title.replace('\\', '\\\\').replace('"', '\\"')
                escaped_message = message.replace('\\', '\\\\').replace('"', '\\"')
                apple_script = f'display notification "{escaped_message}" with title "{escaped_title}"'
                subprocess.run(['osascript', '-e', apple_script],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif os_name == 'Windows':
                # Use PowerShell for Windows toast notification
                # Escape XML special characters in title and message
                escaped_title = html.escape(title)
                escaped_message = html.escape(message)
                ps_script = f'''
                [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
                [Windows.UI.Notifications.ToastNotification, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
                [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null

                $template = @"
                <toast>
                    <visual>
                        <binding template="ToastText02">
                            <text id="1">{escaped_title}</text>
                            <text id="2">{escaped_message}</text>
                        </binding>
                    </visual>
                </toast>
"@

                $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
                $xml.LoadXml($template)
                $toast = New-Object Windows.UI.Notifications.ToastNotification $xml
                [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("W4GNS Logger").Show($toast)
                '''
                subprocess.run(['powershell', '-Command', ps_script],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        except Exception as e:
            logger.debug(f"Desktop notification failed: {e}")

    def update_preferences(self, preferences: NotificationPreferences):
        """Update notification preferences"""
        self.prefs = preferences

    def clear_notification_cache(self):
        """Clear the notification cache (allows re-notification of same contacts)"""
        self._last_notification.clear()


# Singleton instance for easy access with thread safety
_default_notifier: Optional[ContactNotifier] = None
_notifier_lock = threading.Lock()


def get_notifier() -> ContactNotifier:
    """Get the default notifier instance (thread-safe)"""
    global _default_notifier
    if _default_notifier is None:
        with _notifier_lock:
            # Double-check locking pattern
            if _default_notifier is None:
                _default_notifier = ContactNotifier()
    return _default_notifier


def set_notifier(notifier: ContactNotifier):
    """Set the default notifier instance (thread-safe)"""
    global _default_notifier
    with _notifier_lock:
        _default_notifier = notifier
