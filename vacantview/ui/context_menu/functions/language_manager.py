import gettext
import os
from vacantview.core.state import state

localedir = 'vacantview/locale'

_translation = None

def set_language(lang_code):
    global _translation
    _translation = gettext.translation('messages', localedir=localedir, languages=[lang_code], fallback=True)

def _(text):
    return _translation.gettext(text) if _translation else text


def update_ui_texts():
    label.config(text=_("Initializing devices...\nPlease wait"))
    button.config(text=_("Click me"))
  
