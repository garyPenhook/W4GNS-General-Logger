import os
import sqlite3
import tempfile
import unittest

from src.database import Database


def create_backup_database(path, callsign="W4GNS"):
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            callsign TEXT NOT NULL,
            date TEXT NOT NULL,
            time_on TEXT NOT NULL,
            band TEXT,
            mode TEXT
        )
        """
    )
    cursor.execute(
        """
        INSERT INTO contacts (callsign, date, time_on, band, mode)
        VALUES (?, ?, ?, ?, ?)
        """,
        (callsign, "2025-11-07", "1939", "20m", "CW"),
    )
    conn.commit()
    conn.close()


class DatabaseBootstrapTests(unittest.TestCase):
    def test_adopts_valid_backup_database_when_logger_db_is_missing(self):
        with tempfile.TemporaryDirectory() as tempdir:
            db_path = os.path.join(tempdir, "logger.db")
            backup_path = os.path.join(tempdir, "w4gns_log_20251107_193902.db")
            create_backup_database(backup_path, callsign="N0CALL")

            database = Database(db_path=db_path)
            try:
                count = database.conn.execute("SELECT COUNT(*) FROM contacts").fetchone()[0]
                contact = database.get_all_contacts(limit=1)[0]
                columns = {
                    row[1]
                    for row in database.conn.execute("PRAGMA table_info(contacts)").fetchall()
                }
            finally:
                database.close()

            self.assertEqual(count, 1)
            self.assertEqual(contact["my_gridsquare"], "")
            self.assertEqual(contact["skcc_number"], "")
            self.assertIn("skcc_number", columns)
            self.assertIn("their_power_watts", columns)

    def test_skips_invalid_backup_and_creates_fresh_database(self):
        with tempfile.TemporaryDirectory() as tempdir:
            db_path = os.path.join(tempdir, "logger.db")
            backup_path = os.path.join(tempdir, "w4gns_log_20251107_193902.db")

            with open(backup_path, "w", encoding="utf-8") as handle:
                handle.write("not a sqlite database")

            database = Database(db_path=db_path)
            try:
                count = database.conn.execute("SELECT COUNT(*) FROM contacts").fetchone()[0]
            finally:
                database.close()

            self.assertTrue(os.path.exists(db_path))
            self.assertEqual(count, 0)


if __name__ == "__main__":
    unittest.main()
