# db/database.py

import sqlite3
import os

# Database file path
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ora_jewelry.db')

def get_connection():
    """
    Create and return a database connection.
    Enables foreign key support for SQLite.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
    return conn

def init_database():
    """
    Initialize the database by creating all tables.
    This will be called when the application starts.
    """
    from db.schema import create_tables
    create_tables()
    print("✅ Database initialized successfully!")

def close_connection(conn):
    """
    Close the database connection.
    """
    if conn:
        conn.close()