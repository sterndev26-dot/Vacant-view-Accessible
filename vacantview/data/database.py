import sqlite3
import os

from vacantview.core.state import state
from vacantview.config.config import DB_PATH, DEBUG



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
        conn.commit()
        conn.close()
        
    except Exception as e:
        if DEBUG:
            print("DB error:", e)
            return False