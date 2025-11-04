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
                name TEXT,
                qth TEXT,
                gridsquare TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

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

    def add_contact(self, contact_data):
        """Add a new contact to the log"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO contacts
            (callsign, date, time_on, time_off, frequency, band, mode,
             rst_sent, rst_rcvd, name, qth, gridsquare, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            contact_data.get('name', ''),
            contact_data.get('qth', ''),
            contact_data.get('gridsquare', ''),
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
