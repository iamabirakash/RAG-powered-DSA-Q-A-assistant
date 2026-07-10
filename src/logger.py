import sqlite3
import datetime
import os
import logging

logger = logging.getLogger(__name__)

class QueryLogger:
    def __init__(self, db_path="data/analytics.db"):
        self.db_path = db_path
        self._initialize_db()

    def _initialize_db(self):
        """Creates the sqlite table if it doesn't exist."""
        os.makedirs(os.path.dirname(self.db_path) or ".", exist_ok=True)
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS queries (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        query TEXT NOT NULL,
                        response TEXT NOT NULL,
                        context_snippet TEXT
                    )
                ''')
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Database initialization error: {e}")

    def log_query(self, query, response, context_snippet=""):
        """Logs a single query and its response."""
        timestamp = datetime.datetime.now().isoformat()
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO queries (timestamp, query, response, context_snippet)
                    VALUES (?, ?, ?, ?)
                ''', (timestamp, query, response, context_snippet))
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Error logging query: {e}")
            return None

    def get_all_logs(self):
        """Retrieves all logged queries for analytics."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, timestamp, query, response, context_snippet
                    FROM queries
                    ORDER BY timestamp DESC
                ''')
                return cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Error fetching logs: {e}")
            return []


