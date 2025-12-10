"""
Notification System for Needed Contacts

Provides audio and visual notifications when high-priority contacts appear.
"""

import logging
from typing import Optional
from dataclasses import dataclass
import subprocess
import sys
import platform
import threading
import shlex

logger = logging.getLogger(__name__)


@dataclass
class NotificationPreferences:
    """User preferences for notifications"""
    enabled: bool = True
    sound_enabled: bool = True
    desktop_notification_enabled: bool = False
    min_priority: int = 2  # Notify for priority 1 (high) and 2 (medium)
    sound_command: Optional[str] = None


class ContactNotifier:
    """
    Handles notifications for needed contacts.

    Supports:
    - Audio alerts (system beep or custom command)
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
        import time
        current_time = time.time()
        key = f"{callsign}_{priority}"
        if key in self._last_notification:
            if current_time - self._last_notification[key] < 60:
                return

        self._last_notification[key] = current_time

        # Send notifications
        if self.prefs.sound_enabled:
            self._play_sound(priority)

        if self.prefs.desktop_notification_enabled:
            self._show_desktop_notification(callsign, priority, reason)

    def _play_sound(self, priority: int):
        """Play audio alert based on priority"""
        try:
            if self.prefs.sound_command:
                # Custom sound command - use shlex.split for safety instead of shell=True
                try:
                    cmd_parts = shlex.split(self.prefs.sound_command)
                    subprocess.run(cmd_parts, shell=False,
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                except ValueError as e:
                    logger.warning(f"Invalid sound command format: {e}")
            else:
                # System beep (platform-specific)
                self._system_beep(priority)
        except Exception as e:
            logger.debug(f"Could not play sound: {e}")

    def _system_beep(self, priority: int):
        """Generate system beep"""
        try:
            os_name = platform.system()

            if os_name == 'Linux':
                # Use paplay with beep if available, otherwise try beep command
                beep_count = 3 if priority == 1 else 2
                for _ in range(beep_count):
                    subprocess.run(['paplay', '/usr/share/sounds/freedesktop/stereo/bell.oga'],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif os_name == 'Darwin':  # macOS
                beep_count = 3 if priority == 1 else 2
                for _ in range(beep_count):
                    subprocess.run(['afplay', '/System/Library/Sounds/Glass.aiff'],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif os_name == 'Windows':
                import winsound
                frequency = 1000 if priority == 1 else 800
                duration = 200  # milliseconds
                beep_count = 3 if priority == 1 else 2
                for _ in range(beep_count):
                    winsound.Beep(frequency, duration)
            else:
                # Fallback: print bell character
                print('\a', end='', flush=True)

        except Exception as e:
            logger.debug(f"System beep failed: {e}")
            # Ultimate fallback
            try:
                print('\a', end='', flush=True)
            except Exception:
                pass

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
                apple_script = f'display notification "{message}" with title "{title}"'
                subprocess.run(['osascript', '-e', apple_script],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif os_name == 'Windows':
                # Use PowerShell for Windows toast notification
                ps_script = f'''
                [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
                [Windows.UI.Notifications.ToastNotification, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
                [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null

                $template = @"
                <toast>
                    <visual>
                        <binding template="ToastText02">
                            <text id="1">{title}</text>
                            <text id="2">{message}</text>
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
