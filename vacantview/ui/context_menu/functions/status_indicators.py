import tkinter as tk
from tkinter import Toplevel, ttk
from vacantview.core.state import g_auth, state
from vacantview.config.config import DEBUG

from .status_color_scheme import open_custom_color_picker
from vacantview.core.state import state
from vacantview.ui.context_menu.rtl_func import prepare_text_for_widget

win = state.win

import tkinter.font as tkFont

def change_status_indicator_font(tag, new_font_name):
    ring = getattr(state, tag, None)
    if ring is None:
        return

    try:
        current_font = tkFont.Font(font=ring.canvas.itemcget(ring.text, 'font'))

        font_size = current_font['size']
        font_weight = current_font['weight']  # 'normal' or 'bold'
        font_slant = current_font['slant']    # 'roman' or 'italic'

       
        test_font = tkFont.Font(family=new_font_name, size=font_size)

        supported_styles = {
            'bold': test_font.actual('weight') == 'bold',
            'italic': test_font.actual('slant') == 'italic'
        }

        applied_styles = []
        unsupported_styles = []

        if font_weight == 'bold':
            if supported_styles['bold']:
                applied_styles.append('bold')
            else:
                unsupported_styles.append('bold')

        if font_slant == 'italic':
            if supported_styles['italic']:
                applied_styles.append('italic')
            else:
                unsupported_styles.append('italic')

        if applied_styles:
            final_font = (new_font_name, font_size, " ".join(applied_styles))
        else:
            final_font = (new_font_name, font_size)

        ring.canvas.itemconfig(ring.text, font=final_font)
        state.new_font = list(final_font)

      
        if unsupported_styles and DEBUG:
            print(f"[WARNING] Styles {unsupported_styles} cannot be applied to font '{new_font_name}'")

    except Exception as e:
        if DEBUG:
            print(f'[WARNING] Failed to change indicator font: {e}')

        
def change_status_indicator_font_size(tag, new_size):
    
    ring = getattr(state, tag, None)
    
    if ring is None:
        return

    try:
        current_font = tkFont.Font(font=ring.canvas.itemcget(ring.text, 'font'))

        font_family = current_font.actual()['family']
        font_weight = current_font.actual()['weight']
        font_slant = current_font.actual()['slant']

        new_font = (font_family, new_size, f'{font_weight} {font_slant}'.strip())

        ring.canvas.itemconfig(ring.text, font=new_font)

    except Exception as e:
        print(f'[WARNING] Failed to change font size: {e}')
        
        
def change_status_indicator_font_style(tag, new_style):
    ring = getattr(state, tag, None)
    if ring is None:
        return

    try:
      
        current_font = tkFont.Font(font=ring.canvas.itemcget(ring.text, 'font'))
        font_family = current_font.actual('family')
        font_size = current_font.actual('size')

        weight = 'normal'
        slant = 'roman'

        style = new_style.lower().strip()
        if 'bold' in style:
            weight = 'bold'
        if 'italic' in style:
            slant = 'italic'

        new_font = tkFont.Font(family=font_family, size=font_size, weight=weight, slant=slant)

        ring.canvas.itemconfig(ring.text, font=new_font)

    except Exception as e:
        print(f'[WARNING] Failed to change font style: {e}')
        