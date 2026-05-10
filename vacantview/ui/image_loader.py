from PIL import Image, ImageTk
import os,sys

from vacantview.config.config import IMG_DIR,DEBUG

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def load_background_image(gender, def_mode = False):
    if def_mode:
        #print(f"!!!!{gender}")
        path = resource_path(gender)
    else:
        path = resource_path(os.path.join(IMG_DIR,f"{gender}")) 
    if DEBUG:
        print(f" [INFO] {path}")
    #path = os.path.join(os.path.dirname(os.path.dirname(__file__)), IMG_DIR, f"{gender}")
    return path
