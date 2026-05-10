import os
import sys
from dotenv import load_dotenv, set_key
from tkinter import messagebox


def get_base_path():
    if getattr(sys, "frozen", False):
        return sys._MEIPASS
    else:
        
        return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

env_path = os.path.join(get_base_path(), ".env")
load_dotenv(dotenv_path=env_path,override=True)

def restart_program():
    python = sys.executable
    os.execv(python, [python] + sys.argv)

def set_language(lang_code):
    lang_code = lang_code.strip("'\"")
    set_key(env_path, "APP_LANG", lang_code)

    answer = messagebox.askokcancel(
        "Restart required",
        "The language has been changed.\nTo apply changes, the app must restart.\n\nPress OK to restart now.\nPress Cancel to restart later."
    )

    if answer:
        restart_program()
    else:
        messagebox.showinfo("Restart postponed", "The new language will be applied after next restart.")
        


    
DEBUG = os.getenv("DEBUG")

FULLSCREEN_ON_LOAD= str(os.getenv("FULLSCREEN_ON_LOAD"))
WIDTH=str(os.getenv("WIDTH"))
HEIGH=str(os.getenv("HEIGH"))

NAME_MODE = os.getenv("NAME_MODE")

APP_LANG= os.getenv("APP_LANG")
DB_PATH = os.getenv("DB_PATH")
IMG_DIR = os.getenv("IMG_DIR")
LOGO_DIR = os.getenv("LOGO_DIR")
LOGO_ACCESSIBLE = os.getenv("LOGO_ACCESSIBLE")
LOGO_COMPANY = os.getenv("LOGO_COMPANY")

BOTH_CNF = os.getenv("BOTH_CNF")
BOTH_A_CNF = os.getenv("BOTH_A_CNF")
MAN_CNF= os.getenv("MAN_CNF")
WOMAN_CNF=os.getenv("WOMAN_CNF")
CUSTOM_CNF=os.getenv("CUSTOM_CNF")
MAN_A_CNF=os.getenv("MAN_A_CNF")
WOMAN_A_CNF=os.getenv("WOMAN_A_CNF")

INPUT_PIN_MEN = int(os.getenv("PIN_INPUT_MEN"))
INPUT_PIN_WOMEN = int(os.getenv("PIN_INPUT_WOMEN"))
BUTTON_PIN = int(os.getenv("PIN_BUTTON"))
BUTTON_PIN_2 = int(os.getenv("PIN_BUTTON_2"))

_pir_raw = os.getenv("PIN_PIR", "").strip()
PIR_PIN = int(_pir_raw) if _pir_raw and _pir_raw != "0" else None
AUDIO_VACANT = os.getenv("AUDIO_VACANT", "")
AUDIO_OCCUPIED = os.getenv("AUDIO_OCCUPIED", "")
AUDIO_COOLDOWN = float(os.getenv("AUDIO_COOLDOWN", "10"))