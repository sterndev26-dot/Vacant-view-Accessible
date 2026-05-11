import sqlite3
import os
import hashlib

from vacantview.core.state import state
from vacantview.config.config import DB_PATH, DEBUG

def _hash(value):
    return hashlib.sha256(value.encode()).hexdigest()



def init_db():
    try:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

       
        # Users
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS app_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                pin TEXT NOT NULL,
                type INTEGER NOT NULL
            )
        ''')
        
        # Organization
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS organization (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                organization_name TEXT DEFAULT 'STERN',
                organization_id TEXT DEFAULT '-'
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS login_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                login_time TEXT NOT NULL,
                method TEXT NOT NULL,
                status TEXT NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                action TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        
        cursor.execute("INSERT INTO organization DEFAULT VALUES")

        # Seed default users only if table is empty
        cursor.execute("SELECT COUNT(*) FROM app_users")
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                "INSERT INTO app_users (username, password, pin, type) VALUES (?, ?, ?, ?)",
                ("Master", _hash("1234"), _hash("1234"), 1)
            )
            cursor.execute(
                "INSERT INTO app_users (username, password, pin, type) VALUES (?, ?, ?, ?)",
                ("User", _hash("1234"), _hash("1234"), 2)
            )

        conn.commit()
        conn.close()
        
    except Exception as e:
        if DEBUG:
            print("DB error:", e)
            return False