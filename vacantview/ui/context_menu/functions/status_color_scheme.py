import tkinter as tk
from tkinter import Toplevel, ttk
from vacantview.core.state import g_auth, state
from vacantview.config.config import DEBUG
from vacantview.ui.context_menu.rtl_func import prepare_text_for_widget



# Все стандартные цвета из Tk
TK_COLOR_NAMES = list(tk.Color.__dict__.keys()) if hasattr(tk, 'Color') else [
    'snow', 'ghost white', 'white smoke', 'gainsboro', 'floral white', 'old lace',
    'linen', 'antique white', 'papaya whip', 'blanched almond', 'bisque',
    'peach puff', 'navajo white', 'lemon chiffon', 'mint cream', 'azure',
    'alice blue', 'lavender', 'lavender blush', 'misty rose', 'white', 'black',
    'dark slate gray', 'dim gray', 'slate gray', 'light slate gray', 'gray',
    'light grey', 'midnight blue', 'navy', 'cornflower blue', 'dark slate blue',
    'slate blue', 'medium slate blue', 'light slate blue', 'medium blue',
    'royal blue', 'blue', 'dodger blue', 'deep sky blue', 'sky blue',
    'light sky blue', 'steel blue', 'light steel blue', 'light blue', 'powder blue',
    'pale turquoise', 'dark turquoise', 'medium turquoise', 'turquoise',
    'cyan', 'light cyan', 'cadet blue', 'medium aquamarine', 'aquamarine',
    'dark green', 'dark olive green', 'dark sea green', 'sea green',
    'medium sea green', 'light sea green', 'pale green', 'spring green',
    'lawn green', 'medium spring green', 'green yellow', 'lime green',
    'yellow green', 'forest green', 'olive drab', 'dark khaki', 'khaki',
    'pale goldenrod', 'light goldenrod yellow', 'light yellow', 'yellow',
    'gold', 'light goldenrod', 'goldenrod', 'dark goldenrod', 'rosy brown',
    'indian red', 'saddle brown', 'sienna', 'peru', 'burlywood', 'beige',
    'wheat', 'sandy brown', 'tan', 'chocolate', 'firebrick', 'brown', 'dark salmon',
    'salmon', 'light salmon', 'orange', 'dark orange', 'coral', 'light coral',
    'tomato', 'orange red', 'red', 'hot pink', 'deep pink', 'pink', 'light pink',
    'pale violet red', 'maroon', 'medium violet red', 'violet red',
    'medium orchid', 'dark orchid', 'dark violet', 'blue violet', 'purple',
    'medium purple', 'thistle', 'snow2', 'snow3', 'snow4', 'seashell2',
    'seashell3', 'seashell4', 'AntiqueWhite1', 'AntiqueWhite2', 'AntiqueWhite3',
    'AntiqueWhite4', 'bisque2', 'bisque3', 'bisque4', 'PeachPuff2', 'PeachPuff3',
    'PeachPuff4'
]

from collections import defaultdict
COLOR_CATEGORIES_RINGS = defaultdict(list)
for color in TK_COLOR_NAMES:
    if isinstance(color, str):
        first_letter = color[0].upper()
        COLOR_CATEGORIES_RINGS[first_letter].append(color)

_last_selected_color = "#ffffff"

def open_custom_color_picker(parent, identifier=None, apply_color_callback=None):
    global _last_selected_color

    picker = tk.Toplevel(parent)
    picker.title(prepare_text_for_widget(_("Select Color")))
    picker.configure(bg="white")
    picker.grab_set()
    picker.attributes('-topmost', True)

    picker.update_idletasks()
    w, h = 480, 420
    x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (w // 2)
    y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (h // 2)
    picker.geometry(f"{w}x{h}+{x}+{y}")

    tk.Label(picker, text=prepare_text_for_widget(_("Choose a color:")), font=("Arial", 12), bg="white").pack(pady=5)

    search_var = tk.StringVar()
    search_entry = tk.Entry(picker, textvariable=search_var)
    search_entry.pack(pady=4, padx=10, fill="x")

    notebook = ttk.Notebook(picker)
    notebook.pack(fill='both', expand=True)

    preview = tk.Label(picker, text=prepare_text_for_widget(_("Last: {0}").format(_last_selected_color)), bg=_last_selected_color, fg="white")
    preview.pack(pady=5, fill="x", padx=5)

    color_buttons = []

    def on_color_select(color):
        global _last_selected_color
        _last_selected_color = color
        if apply_color_callback:
            apply_color_callback(identifier, color)
        picker.destroy()

    for category, colors in sorted(COLOR_CATEGORIES_RINGS.items()):
        tab = tk.Frame(notebook, bg="white")
        notebook.add(tab, text=category)

        canvas = tk.Canvas(tab, bg="white", highlightthickness=0)
        scrollbar = tk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="white")

        scrollable_frame.bind(
            "<Configure>",
            lambda e, c=canvas: c.configure(scrollregion=c.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for i, color in enumerate(colors):
            try:
                btn = tk.Button(
                    scrollable_frame, bg=color, width=3, height=1,
                    command=lambda c=color: on_color_select(c),
                    relief="flat"
                )
                btn.grid(row=i // 12, column=i % 12, padx=2, pady=2)
                btn._color_name = color
                color_buttons.append(btn)
            except tk.TclError:
                pass  # skip unknown color names

    def update_search(*args):
        query = search_var.get().lower()
        for btn in color_buttons:
            color_name = btn._color_name.lower()
            visible = query in color_name if query else True
            btn.grid() if visible else btn.grid_remove()

    search_var.trace_add("write", update_search)

    def open_askcolor():
        color = tk_colorchooser.askcolor(color=_last_selected_color, parent=picker)[1]
        if color:
            on_color_select(color)

    bottom = tk.Frame(picker, bg="white")
    bottom.pack(pady=5, fill="x")

   
    tk.Button(bottom, text=prepare_text_for_widget(_("Cancel")), command=picker.destroy).pack(side="right", padx=10)


def apply_progress_color(ring_id, new_color):
    ring = getattr(state, ring_id, None)
    if DEBUG:
        print(f"[apply_ring_color] ring_id: {ring_id}, ring: {ring}, color: {new_color}")
    if not ring:
        return
    if ring_id not in state.ring_color_table:
        state.ring_color_table[ring_id] = {}

    state.ring_color_add_table[ring_id]["fill"] = new_color
    state.ring_color_add_table[ring_id]["outline"] = new_color

    try:
        ring.canvas.itemconfig(ring.outer2, fill=new_color, outline=new_color)
    except Exception as e:
        if DEBUG:
            print("[apply_ring_color] Failed to apply color:", e)
    

def apply_ring_color(ring_id, new_color):
    ring = getattr(state, ring_id, None)
    if DEBUG:
        print(f"[apply_ring_color] ring_id: {ring_id}, ring: {ring}, color: {new_color}")
    if not ring:
        return
    if ring_id not in state.ring_color_table:
        
        state.ring_color_table[ring_id] = {}

    state.ring_color_table[ring_id]["fill"] = new_color
    state.ring_color_table[ring_id]["outline"] = new_color
    print(f"ring.outer1: {ring.outer1}, type: {type(ring.outer1)}")
    try:
        
        if state.indicator_type == 'rounded':
            for element_id in ring.outer1:
                ring.canvas.itemconfig(element_id, fill=new_color, outline=new_color)
        else:
            
            ring.canvas.itemconfig(ring.outer1, fill=new_color, outline=new_color)    
        #ring.canvas.itemconfig(ring.outer2, fill=new_color, outline=new_color)
    except Exception as e:
        if DEBUG:
            print("[apply_ring_color] Failed to apply color:", e)

def apply_outring_color(ring_id, new_color):
    ring = getattr(state, ring_id, None)
    if DEBUG:
        print(f"[apply_outring_color] ring_id: {ring_id}, ring: {ring}, color: {new_color}")
    try:
        
        state.outring_fill[ring_id] = new_color

        if isinstance(ring.outring, (list, tuple)):
            for item in ring.outring:
                ring.canvas.itemconfig(item, fill=new_color, outline=new_color)
        else:
            ring.canvas.itemconfig(ring.outring, outline=new_color)

    except Exception as e:
        if DEBUG:
            print("[apply_outring_color] Failed to apply color:", e)
    
def apply_indicator_background_color(ring_id, new_color):
    ring = getattr(state, ring_id, None)
    if DEBUG:
        print(f"[apply_indicator_background_color] ring_id: {ring_id}, ring: {ring}, color: {new_color}")
    try:
        state.outer3_fill[ring_id] = new_color

        if isinstance(ring.outer3, (list, tuple)):
            for item in ring.outer3:
                ring.canvas.itemconfig(item, fill=new_color, outline=new_color)
        else:
            ring.canvas.itemconfig(ring.outer3, fill=new_color)

    except Exception as e:
        if DEBUG:
            print("[apply_indicator_background_color] Failed to apply color:", e)


def apply_indicator_number_color(ring_id, color):
    
    state.text_color[ring_id] = color
            
def apply_text_color(tag, new_color):
    try:
        
        state.bg_canvas.itemconfig(tag, fill=new_color)
        setattr(state,f'fill_{tag}',None)
        print(f'[INFO] Applying color to the text of element {tag}')
    except Exception as e:
        if DEBUG:
            print(f'[WARING] Applying color to the text of element {tag} resulted in an error: {e}')
        else:
            pass
        
def apply_a_panel_color(tag, new_color):
    try:
        
        item_ids = state.bg_canvas.find_withtag(tag)
        for item_id in item_ids:
            element_type = state.bg_canvas.type(item_id)
            if element_type == "line":
                state.bg_canvas.itemconfig(item_id, fill=new_color)
            elif element_type == "arc":
                state.bg_canvas.itemconfig(item_id, outline=new_color)       
        print(f'[INFO] Applying color to the text of element {tag}')
    except Exception as e:
        if DEBUG:
            print(f'[WARING] Applying color to the text of element {tag} resulted in an error: {e}')
        else:
            pass        

def recolor_figure(tag,new_color):
    
        for item_id in state.bg_canvas.find_withtag(tag):
            cfg = state.bg_canvas.itemconfig(item_id)
            obj_type = state.bg_canvas.type(item_id)

            if 'fill' in cfg and obj_type == 'line':
                state.bg_canvas.itemconfig(item_id, fill=new_color)
            elif 'outline' in cfg:
                state.bg_canvas.itemconfig(item_id, outline=new_color)

            '''if 'fill' in cfg and obj_type != 'line':
                state.bg_canvas.itemconfig(item_id, fill="")'''
def recolor_figure(tag,new_color):
    
        for item_id in state.bg_canvas.find_withtag(tag):
            cfg = state.bg_canvas.itemconfig(item_id)
            obj_type = state.bg_canvas.type(item_id)

            if 'fill' in cfg and obj_type == 'line':
                state.bg_canvas.itemconfig(item_id, fill=new_color)
            elif 'outline' in cfg:
                state.bg_canvas.itemconfig(item_id, outline=new_color)

            '''if 'fill' in cfg and obj_type != 'line':
                state.bg_canvas.itemconfig(item_id, fill="")'''
            
def recolor_accessable_rect(tag,new_color):
    
        for item_id in state.bg_canvas.find_withtag(tag):
            cfg = state.bg_canvas.itemconfig(item_id)
            obj_type = state.bg_canvas.type(item_id)
            state.bg_canvas.itemconfig(item_id, fill=new_color)
                     