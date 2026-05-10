import sqlite3
import hashlib #sha256
import sys
import os
from datetime import datetime


from vacantview.config.config import DB_PATH, DEBUG

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def log_user_login(username, method, status):
  
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        login_time = datetime.now().isoformat(timespec='seconds')

        cursor.execute('''
            INSERT INTO login_log (username, login_time, method, status)
            VALUES (?, ?, ?, ?)
        ''', (username, login_time, method, status))

        conn.commit()
        conn.close()

    except Exception as e:
        if DEBUG:
            print("[Log error]", e)
            

def check_credentials(username, password):
    base_path = DB_PATH
    try:
        hashed = hashlib.sha256(password.encode()).hexdigest()

        conn = sqlite3.connect(base_path)
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM app_users WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()

        if result and result[0] == hashed:
            log_user_login(username, method='password', status='success')
            return True
        else:
            log_user_login(username, method='password', status='failure')
            return False
    except Exception as e:
        if DEBUG:
            print("DB error:", e)
        log_user_login(username, method='password', status='failure')
        return False
        
def check_pin(username, pin):
    base_path = resource_path(DB_PATH)
    try:
        hashed = hashlib.sha256(pin.encode()).hexdigest()

        conn = sqlite3.connect(base_path)
        cursor = conn.cursor()
        cursor.execute("SELECT pin FROM app_users WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()

        if result and result[0] == hashed:
            log_user_login(username, method='pin', status='success')
            return True
        else:
            log_user_login(username, method='pin', status='failure')
            return False
    except Exception as e:
        if DEBUG:
            print("DB error:", e)
        log_user_login(username, method='pin', status='failure')
        return False        
        
def update_pin(username, pin):
    base_path = resource_path(DB_PATH)
    try:
        hashed = hashlib.sha256(pin.encode()).hexdigest()

        conn = sqlite3.connect(base_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE app_users SET pin=? WHERE username = ?", (hashed, username,))
        conn.commit()
        conn.close()

        log_user_login(username, method='update_pin', status='success')
        return True

    except Exception as e:
        if DEBUG:
            print("DB error:", e)
        log_user_login(username, method='update_pin', status='failure')
        return False
    
def update_password(username, password):
    base_path = resource_path(DB_PATH)
    try:
        hashed = hashlib.sha256(password.encode()).hexdigest()

        conn = sqlite3.connect(base_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE app_users SET password=? WHERE username = ?", (hashed, username,))
        conn.commit()
        conn.close()

        log_user_login(username, method='update_password', status='success')
        return True

    except Exception as e:
        if DEBUG:
            print("DB error:", e)
        log_user_login(username, method='update_password', status='failure')
        return False    
