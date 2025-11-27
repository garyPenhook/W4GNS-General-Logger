"""
DX Cluster Telnet Client with async support for better performance
Handles connections to DX cluster servers
"""

import telnetlib
import threading
import queue
import time
import re

# Optional async support
try:
    import asyncio
    ASYNC_AVAILABLE = True
except ImportError:
    ASYNC_AVAILABLE = False


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
            except (OSError, AttributeError) as e:
                # OSError for socket errors, AttributeError if connection object invalid
                print(f"Error closing connection: {e}")
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

    # Python data model methods for context manager protocol
    def __enter__(self):
        """Enable context manager: with DXClusterClient(...) as client:"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Automatic cleanup when exiting context"""
        self.disconnect()
        return False  # Don't suppress exceptions

    def __bool__(self):
        """Enable truthiness testing: if client:"""
        return self.connected

    def __repr__(self):
        """Developer-friendly representation"""
        status = "connected" if self.connected else "disconnected"
        async_status = " [async available]" if ASYNC_AVAILABLE else ""
        return f"<DXClusterClient({self.hostname}:{self.port}, {status}{async_status})>"

    # Async I/O methods for improved performance
    async def connect_async(self):
        """
        Async version of connect() for non-blocking connection

        Returns:
            bool: True if connected successfully

        Note: This creates an async connection that can be used with read_async()
        """
        if not ASYNC_AVAILABLE:
            return self.connect()

        try:
            # Open async connection
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self.hostname, self.port),
                timeout=10
            )

            self._async_reader = reader
            self._async_writer = writer
            self.connected = True
            self.running = True

            # Send callsign
            await asyncio.sleep(1)
            await self.send_command_async(self.callsign)

            return True

        except asyncio.TimeoutError:
            self.message_queue.put(f"Connection timeout to {self.hostname}:{self.port}")
            self.connected = False
            return False
        except Exception as e:
            self.message_queue.put(f"Connection error: {str(e)}")
            self.connected = False
            return False

    async def send_command_async(self, command):
        """Async version of send_command()"""
        if not ASYNC_AVAILABLE or not hasattr(self, '_async_writer'):
            self.send_command(command)
            return

        if self.connected and self._async_writer:
            try:
                self._async_writer.write(f"{command}\r\n".encode('ascii'))
                await self._async_writer.drain()
            except Exception as e:
                self.message_queue.put(f"Send error: {str(e)}")
                self.connected = False

    async def read_async(self, timeout=1.0):
        """
        Read data from cluster asynchronously

        Args:
            timeout: Read timeout in seconds

        Returns:
            list: Lines received from the cluster
        """
        if not ASYNC_AVAILABLE or not hasattr(self, '_async_reader'):
            return []

        lines = []
        try:
            while True:
                try:
                    data = await asyncio.wait_for(
                        self._async_reader.readline(),
                        timeout=timeout
                    )
                    if not data:
                        break

                    line = data.decode('ascii', errors='ignore').strip()
                    if line:
                        lines.append(line)
                        self._parse_spot(line)

                except asyncio.TimeoutError:
                    break  # No more data available

        except Exception as e:
            self.message_queue.put(f"Read error: {str(e)}")

        return lines

    async def disconnect_async(self):
        """Async version of disconnect()"""
        self.running = False
        self.connected = False

        if hasattr(self, '_async_writer') and self._async_writer:
            try:
                self._async_writer.close()
                await self._async_writer.wait_closed()
            except Exception as e:
                print(f"Error closing async connection: {e}")

        self._async_reader = None
        self._async_writer = None
