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

        spot_pattern = r'DX de ([A-Z0-9\-/]+):\s+(\d+\.?\d*)\s+([A-Z0-9\-/]+)\s+(.+?)\s+(\d{4}Z)'
        match = re.search(spot_pattern, line)

        if match and self.spot_callback:
            spot = {
                'spotter': match.group(1),
                'frequency': match.group(2),
                'callsign': match.group(3),
                'comment': match.group(4).strip(),
                'time': match.group(5)
            }
            self.spot_callback(spot)

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
