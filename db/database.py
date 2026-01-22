import sqlite3
import os

from db.schema import create_tables

# Database file path
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ora_jewelry.db')

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")  #turn on foreign key 
    return conn

def init_database():
    create_tables()
    print("Database started successfully!!!!")

def close_connection(conn):
    if conn:
        conn.close()