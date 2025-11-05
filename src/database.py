"""
Database management for contact logging
Uses SQLite for local storage
"""

import sqlite3
import os
from datetime import datetime


class Database:
    def __init__(self, db_path=None):
        # Default to logger.db in the project root directory
        if db_path is None:
            # Get the directory where this script is located (src/)
            script_dir = os.path.dirname(os.path.abspath(__file__))
            # Go up one level to the project root
            project_root = os.path.dirname(script_dir)
            db_path = os.path.join(project_root, "logger.db")

        self.db_path = db_path
        self.conn = None
        self.init_database()

    def init_database(self):
        """
        Initialize database and create tables if they don't exist

        Raises:
            sqlite3.DatabaseError: If database connection or initialization fails
        """
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            cursor = self.conn.cursor()
        except sqlite3.Error as e:
            raise sqlite3.DatabaseError(f"Failed to connect to database {self.db_path}: {e}")

        # Create contacts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                callsign TEXT NOT NULL,
                date TEXT NOT NULL,
                time_on TEXT NOT NULL,
                time_off TEXT,
                frequency TEXT,
                band TEXT,
                mode TEXT,
                rst_sent TEXT,
                rst_rcvd TEXT,
                power TEXT,
                name TEXT,
                qth TEXT,
                gridsquare TEXT,
                county TEXT,
                state TEXT,
                country TEXT,
                continent TEXT,
                cq_zone TEXT,
                itu_zone TEXT,
                dxcc TEXT,
                iota TEXT,
                sota TEXT,
                pota TEXT,
                my_gridsquare TEXT,
                comment TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Upgrade existing database schema if needed
        self._upgrade_schema(cursor)

        # Create DX spots table for caching
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dx_spots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                callsign TEXT NOT NULL,
                frequency TEXT NOT NULL,
                spotter TEXT,
                time TEXT NOT NULL,
                comment TEXT,
                cluster_source TEXT,
                received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        self.conn.commit()

    def _upgrade_schema(self, cursor):
        """Upgrade existing database schema to add new columns"""
        # Get existing columns
        cursor.execute("PRAGMA table_info(contacts)")
        existing_columns = [row[1] for row in cursor.fetchall()]

        # Add missing columns
        new_columns = {
            'power': 'TEXT',
            'county': 'TEXT',
            'state': 'TEXT',
            'country': 'TEXT',
            'continent': 'TEXT',
            'cq_zone': 'TEXT',
            'itu_zone': 'TEXT',
            'dxcc': 'TEXT',
            'iota': 'TEXT',
            'sota': 'TEXT',
            'pota': 'TEXT',
            'my_gridsquare': 'TEXT',
            'comment': 'TEXT',
            # SKCC-specific fields
            'skcc_number': 'TEXT',           # Remote station's SKCC number (e.g., "12345T")
            'my_skcc_number': 'TEXT',        # Operator's SKCC number
            'key_type': 'TEXT',              # STRAIGHT, BUG, or SIDESWIPER (mechanical keys only)
            'duration_minutes': 'INTEGER',   # For Rag Chew award (minimum 30 minutes)
            'power_watts': 'REAL',           # For QRP endorsements (≤5W)
            'distance_nm': 'REAL',           # Distance in nautical miles (for Maritime-mobile validation)
            'dxcc_entity': 'INTEGER'         # DXCC entity code
        }

        for column, data_type in new_columns.items():
            if column not in existing_columns:
                try:
                    cursor.execute(f'ALTER TABLE contacts ADD COLUMN {column} {data_type}')
                    print(f"Added column: {column}")
                except sqlite3.OperationalError:
                    pass  # Column already exists

        self.conn.commit()

        # Create SKCC member list tables
        self._create_skcc_tables(cursor)

    def _create_skcc_tables(self, cursor):
        """Create SKCC member list tables for Tribune/Senator validation"""

        # Centurion members table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS skcc_centurion_members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                skcc_number TEXT NOT NULL UNIQUE,
                callsign TEXT NOT NULL,
                centurion_date TEXT,
                other_callsigns TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Tribune members table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS skcc_tribune_members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                skcc_number TEXT NOT NULL UNIQUE,
                callsign TEXT NOT NULL,
                tribune_date TEXT,
                other_callsigns TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Senator members table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS skcc_senator_members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                skcc_number TEXT NOT NULL UNIQUE,
                callsign TEXT NOT NULL,
                senator_date TEXT,
                other_callsigns TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        self.conn.commit()

    def add_contact(self, contact_data):
        """
        Add a new contact to the log

        Args:
            contact_data: Dictionary containing contact fields

        Returns:
            int: ID of the inserted contact

        Raises:
            ValueError: If required fields are missing
            sqlite3.DatabaseError: If database operation fails
        """
        # Validate required fields
        if not contact_data:
            raise ValueError("No contact data provided")

        if not contact_data.get('callsign'):
            raise ValueError("Callsign is required")

        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO contacts
                (callsign, date, time_on, time_off, frequency, band, mode,
                 rst_sent, rst_rcvd, power, name, qth, gridsquare, county, state,
                 country, continent, cq_zone, itu_zone, dxcc, iota, sota, pota,
                 my_gridsquare, comment, notes,
                 skcc_number, my_skcc_number, key_type, duration_minutes, power_watts, distance_nm, dxcc_entity)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                contact_data.get('callsign', ''),
                contact_data.get('date', ''),
                contact_data.get('time_on', ''),
                contact_data.get('time_off', ''),
                contact_data.get('frequency', ''),
                contact_data.get('band', ''),
                contact_data.get('mode', ''),
                contact_data.get('rst_sent', ''),
                contact_data.get('rst_rcvd', ''),
                contact_data.get('power', ''),
                contact_data.get('name', ''),
                contact_data.get('qth', ''),
                contact_data.get('gridsquare', ''),
                contact_data.get('county', ''),
                contact_data.get('state', ''),
                contact_data.get('country', ''),
                contact_data.get('continent', ''),
                contact_data.get('cq_zone', ''),
                contact_data.get('itu_zone', ''),
                contact_data.get('dxcc', ''),
                contact_data.get('iota', ''),
                contact_data.get('sota', ''),
                contact_data.get('pota', ''),
                contact_data.get('my_gridsquare', ''),
                contact_data.get('comment', ''),
                contact_data.get('notes', ''),
                # SKCC fields
                contact_data.get('skcc_number', ''),
                contact_data.get('my_skcc_number', ''),
                contact_data.get('key_type', ''),
                contact_data.get('duration_minutes', None),
                contact_data.get('power_watts', None),
                contact_data.get('distance_nm', None),
                contact_data.get('dxcc_entity', None)
            ))
            self.conn.commit()
            return cursor.lastrowid

        except sqlite3.IntegrityError as e:
            self.conn.rollback()
            raise sqlite3.DatabaseError(f"Database integrity error: {e}")
        except sqlite3.OperationalError as e:
            self.conn.rollback()
            raise sqlite3.DatabaseError(f"Database operational error: {e}")
        except Exception as e:
            self.conn.rollback()
            raise Exception(f"Unexpected error adding contact: {type(e).__name__}: {e}")

    def get_all_contacts(self, limit=100):
        """Retrieve all contacts (most recent first)"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM contacts
            ORDER BY date DESC, time_on DESC
            LIMIT ?
        ''', (limit,))
        # Convert Row objects to dicts for compatibility
        return [dict(row) for row in cursor.fetchall()]

    def search_contacts(self, callsign):
        """Search for contacts by callsign"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM contacts
            WHERE callsign LIKE ?
            ORDER BY date DESC, time_on DESC
        ''', (f'%{callsign}%',))
        # Convert Row objects to dicts for compatibility
        return [dict(row) for row in cursor.fetchall()]

    def check_duplicate(self, callsign, band, mode, date):
        """
        Check if a contact is a duplicate (same call, band, mode, date)

        Returns:
            dict with duplicate info or None if not a duplicate
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM contacts
            WHERE callsign = ? AND band = ? AND mode = ? AND date = ?
            ORDER BY time_on DESC
            LIMIT 1
        ''', (callsign.upper(), band, mode, date))
        result = cursor.fetchone()
        return dict(result) if result else None

    def check_duplicate_within_time_window(self, callsign, date, time_on, window_minutes=10):
        """
        Check if a contact is a duplicate within a time window

        Args:
            callsign: Callsign to check
            date: Date in YYYYMMDD format
            time_on: Time in HHMM or HHMMSS format
            window_minutes: Time window in minutes (default 10)

        Returns:
            dict with duplicate info or None if not a duplicate
        """
        from datetime import datetime, timedelta

        cursor = self.conn.cursor()

        # Get all contacts with same callsign on the same date
        cursor.execute('''
            SELECT * FROM contacts
            WHERE callsign = ? AND date = ?
            ORDER BY time_on
        ''', (callsign.upper(), date))

        results = cursor.fetchall()
        if not results:
            return None

        # Parse the new contact's time
        try:
            # Handle both HHMM and HHMMSS formats
            if len(time_on) == 4:
                new_time = datetime.strptime(f"{date}{time_on}", "%Y%m%d%H%M")
            elif len(time_on) == 6:
                new_time = datetime.strptime(f"{date}{time_on}", "%Y%m%d%H%M%S")
            else:
                return None  # Invalid time format
        except ValueError:
            return None

        # Check each existing contact
        for row in results:
            existing_time_str = row['time_on']
            try:
                # Parse existing time
                if len(existing_time_str) == 4:
                    existing_time = datetime.strptime(f"{date}{existing_time_str}", "%Y%m%d%H%M")
                elif len(existing_time_str) == 6:
                    existing_time = datetime.strptime(f"{date}{existing_time_str}", "%Y%m%d%H%M%S")
                else:
                    continue

                # Calculate time difference
                time_diff = abs((new_time - existing_time).total_seconds() / 60)

                # If within window, it's a duplicate
                if time_diff <= window_minutes:
                    return dict(row)
            except ValueError:
                continue

        return None

    def add_dx_spot(self, spot_data):
        """Add a DX spot to cache"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO dx_spots
            (callsign, frequency, spotter, time, comment, cluster_source)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            spot_data.get('callsign', ''),
            spot_data.get('frequency', ''),
            spot_data.get('spotter', ''),
            spot_data.get('time', ''),
            spot_data.get('comment', ''),
            spot_data.get('cluster_source', '')
        ))
        self.conn.commit()

    def get_recent_spots(self, limit=50):
        """Get recent DX spots"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM dx_spots
            ORDER BY received_at DESC
            LIMIT ?
        ''', (limit,))
        # Convert Row objects to dicts for compatibility
        return [dict(row) for row in cursor.fetchall()]

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
