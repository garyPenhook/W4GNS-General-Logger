"""
DX Cluster Telnet Client
Handles connections to DX cluster servers
"""

import telnetlib
import threading
import queue
import time
import re


class DXClusterClient:
    def __init__(self, hostname, port, callsign):
        self.hostname = hostname
        self.port = port
        self.callsign = callsign
        self.connection = None
        self.connected = False
        self.running = False
        self.read_thread = None
        self.message_queue = queue.Queue()
        self.spot_callback = None

    def connect(self):
        """Connect to DX cluster"""
        try:
            self.connection = telnetlib.Telnet(self.hostname, self.port, timeout=10)
            self.connected = True
            self.running = True

            # Wait for login prompt and send callsign
            time.sleep(1)
            self.send_command(self.callsign)

            # Start reading thread
            self.read_thread = threading.Thread(target=self._read_loop, daemon=True)
            self.read_thread.start()

            return True
        except Exception as e:
            self.message_queue.put(f"Connection error: {str(e)}")
            self.connected = False
            return False

    def disconnect(self):
        """Disconnect from DX cluster"""
        self.running = False
        self.connected = False
        if self.connection:
            try:
                self.connection.close()
            except:
                pass
        self.connection = None

    def send_command(self, command):
        """Send a command to the cluster"""
        if self.connected and self.connection:
            try:
                self.connection.write(f"{command}\r\n".encode('ascii'))
            except Exception as e:
                self.message_queue.put(f"Send error: {str(e)}")
                self.connected = False

    def _read_loop(self):
        """Background thread to read from cluster"""
        while self.running and self.connected:
            try:
                data = self.connection.read_until(b"\n", timeout=1)
                if data:
                    line = data.decode('ascii', errors='ignore').strip()
                    if line:
                        self.message_queue.put(line)
                        self._parse_spot(line)
            except EOFError:
                self.message_queue.put("Connection closed by server")
                self.connected = False
                break
            except Exception as e:
                if self.running:
                    self.message_queue.put(f"Read error: {str(e)}")
                break

    def _parse_spot(self, line):
        """Parse DX spot from cluster output"""
        # Common DX spot format: DX de CALLSIGN:     FREQ  DX_CALL  info
        # Example: DX de K1TTT:      14025.0  W1AW       CQ NA       2130Z
        # Supports multiple formats from different cluster types

        # Skip lines that are clearly not spots
        if not line.startswith('DX de '):
            return

        # Most flexible pattern - handles all common variations:
        # - Variable whitespace (spaces, tabs, multiple spaces)
        # - Optional decimal in frequency
        # - Callsigns with various special characters (-, /, #)
        # - Comment field that may be empty or contain any characters
        # - Time formats: 4 digits (HHMM) or 6 digits (HHMMSS) followed by Z

        # Primary pattern: DX de SPOTTER: FREQ DX_CALL [COMMENT] TIMEZ
        # Use \s+ for flexible whitespace, make comment optional with greedy match before time
        spot_pattern = r'DX de\s+([A-Z0-9\-/#]+)\s*:\s+(\d+\.?\d*)\s+([A-Z0-9\-/]+)(?:\s+(.+?))?\s+(\d{4,6}Z)\s*$'
        match = re.search(spot_pattern, line, re.IGNORECASE)

        if match and self.spot_callback:
            # Extract time and normalize it to 4 digits if needed
            time_str = match.group(5)
            if len(time_str) == 7:  # 6 digits + Z (HHMMSSZ)
                time_str = time_str[0:4] + 'Z'  # Convert to HHMMZ

            spot = {
                'spotter': match.group(1).upper(),
                'frequency': match.group(2),
                'callsign': match.group(3).upper(),
                'comment': match.group(4).strip() if match.group(4) else '',
                'time': time_str
            }
            self.spot_callback(spot)
        else:
            # Debug: Log unparsed spot lines to console for troubleshooting
            if line.startswith('DX de '):
                self.message_queue.put(f"[Parser] Could not parse spot format: {line}")

    def set_spot_callback(self, callback):
        """Set callback function for when spots are received"""
        self.spot_callback = callback

    def get_messages(self):
        """Get all pending messages from queue"""
        messages = []
        while not self.message_queue.empty():
            try:
                messages.append(self.message_queue.get_nowait())
            except queue.Empty:
                break
        return messages

    def is_connected(self):
        """Check if connected"""
        return self.connected
