"""
Database management for contact logging
Uses SQLite for local storage
"""

import sqlite3
import os
from datetime import datetime


class Database:
    def __init__(self, db_path="logger.db"):
        self.db_path = db_path
        self.conn = None
        self.init_database()

    def init_database(self):
        """Initialize database and create tables if they don't exist"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()

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
            'comment': 'TEXT'
        }

        for column, data_type in new_columns.items():
            if column not in existing_columns:
                try:
                    cursor.execute(f'ALTER TABLE contacts ADD COLUMN {column} {data_type}')
                    print(f"Added column: {column}")
                except sqlite3.OperationalError:
                    pass  # Column already exists

        self.conn.commit()

    def add_contact(self, contact_data):
        """Add a new contact to the log"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO contacts
            (callsign, date, time_on, time_off, frequency, band, mode,
             rst_sent, rst_rcvd, power, name, qth, gridsquare, county, state,
             country, continent, cq_zone, itu_zone, dxcc, iota, sota, pota,
             my_gridsquare, comment, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            contact_data.get('notes', '')
        ))
        self.conn.commit()
        return cursor.lastrowid

    def get_all_contacts(self, limit=100):
        """Retrieve all contacts (most recent first)"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM contacts
            ORDER BY date DESC, time_on DESC
            LIMIT ?
        ''', (limit,))
        return cursor.fetchall()

    def search_contacts(self, callsign):
        """Search for contacts by callsign"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM contacts
            WHERE callsign LIKE ?
            ORDER BY date DESC, time_on DESC
        ''', (f'%{callsign}%',))
        return cursor.fetchall()

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
        return cursor.fetchall()

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
