import sqlite3

from vacantview.config.config import DB_PATH, DEBUG


def check_organization():
    
    try:
    
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(f"SELECT organization_name, organization_id FROM organization")
        result = cursor.fetchone()
        conn.close()
        return result
    except Exception as e:
        if DEBUG:
            print("DB error:", e)
        
def update_organization():
    pass