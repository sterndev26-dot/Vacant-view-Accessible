import sqlite3
from datetime import datetime
from vacantview.config.config import DB_PATH, DEBUG

def log_user_action(username: str, action: str) -> bool:

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        timestamp = datetime.now().isoformat(timespec='seconds')

        cursor.execute('''
            INSERT INTO user_actions (username, action, timestamp)
            VALUES (?, ?, ?)
        ''', (username, action, timestamp))

        conn.commit()
        conn.close()
        return True

    except Exception as e:
        if DEBUG:
            print("[log_user_action error]:", e)
        return False
