from vacantview.ui.image_loader import load_background_image, resource_path
from vacantview.core.state import state
from tkinter import filedialog, Toplevel, ttk
from PIL import Image, ImageTk
from vacantview.config.config import IMG_DIR, LOGO_DIR, LOGO_COMPANY, LOGO_ACCESSIBLE

from vacantview.ui.context_menu.rtl_func import prepare_text_for_widget

import tkinter as tk
import os

win = state.win

def change_accessible_icon(canvas, tag, icon_rect, self_obj):
   

    filepath = filedialog.askopenfilename(
        title=prepare_text_for_widget(_("Icon")),
        filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")]
    )

    if not filepath:
        return  

    try:
        
        logo_path = os.path.join('vacantview', LOGO_DIR, LOGO_ACCESSIBLE)
        shutil.copyfile(filepath, logo_path)

     
        coords = canvas.coords(icon_rect)
        icon_left, icon_top, icon_right, icon_bottom = coords
        icon_width = icon_right - icon_left
        icon_height = icon_bottom - icon_top

       
        icon_image = Image.open(logo_path)
        scale = 1.1
        new_w = int(icon_width * scale)
        new_h = int(icon_height * scale)
        icon_image = icon_image.resize((new_w, new_h), Image.Resampling.LANCZOS)

        if not hasattr(self_obj, 'tk_icons'):
            self_obj.tk_icons = {}

        self_obj.tk_icons[tag] = ImageTk.PhotoImage(icon_image)


        icon_tags_to_remove = ('accessible_icon_image_men', 'accessible_icon_image_women')
        for t in icon_tags_to_remove:
            for item in canvas.find_withtag(t):
                if tag in canvas.gettags(item):
                    canvas.delete(item)

       
        canvas.create_image(
            (icon_left + icon_right) // 2,
            (icon_top + icon_bottom) // 2,
            image=self_obj.tk_icons[tag],
            tags=(logo_path, tag, 'accessible_icon_image_men')
        )

        #print(f"{logo_path}")

    except Exception as e:
        
        print(f"ERROR: {e}")

class CustomFileDialog(tk.Toplevel):
    def __init__(self, parent, directory, filetypes=[("Image files", "*.jpg *.jpeg *.png")]):
        super().__init__(parent)
        self.title(prepare_text_for_widget(_("Select a File")))
        self.geometry("600x400")
        self.resizable(False, False)

        self.attributes('-topmost', True)
        
        self.transient(parent)
        self.grab_set()

        self.parent = parent
        self.directory = resource_path(directory)
        self.filetypes = filetypes
        self.selected_file = None


        self.label = tk.Label(self, text=f"Directory: {self.directory}", font=("Arial", 12))
        self.label.pack(pady=5)

        self.listbox = tk.Listbox(self, font=("Arial", 11), selectmode=tk.SINGLE)
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=10)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)

        self.btn_open = ttk.Button(btn_frame, text="Open", command=self.open_file)
        self.btn_open.pack(side=tk.LEFT, padx=10)

        self.btn_cancel = ttk.Button(btn_frame, text="Cancel", command=self.cancel)
        self.btn_cancel.pack(side=tk.LEFT, padx=10)

        self.populate_list()

        self.listbox.bind("<Double-Button-1>", lambda e: self.open_file())

    def populate_list(self):
        self.listbox.delete(0, tk.END)
        files = os.listdir(self.directory)
        filtered_files = []
        exts = []
        for desc, pattern in self.filetypes:
            for ext in pattern.split():
                exts.append(ext.lstrip("*").lower())
        for f in files:
            if os.path.isfile(os.path.join(self.directory, f)):
                if any(f.lower().endswith(ext) for ext in exts):
                    filtered_files.append(f)
        filtered_files.sort()
        for f in filtered_files:
            self.listbox.insert(tk.END, f)

    def open_file(self):
        sel = self.listbox.curselection()
        if not sel:
            return
        filename = self.listbox.get(sel[0])
        self.selected_file = os.path.join(self.directory, filename)
        self.grab_release()  # release the grab before destroying
        self.destroy()

    def cancel(self):
        self.selected_file = None
        self.grab_release()  # release the grab before destroying
        self.destroy()


def show_custom_file_dialog(parent, directory):
    dialog = CustomFileDialog(parent, directory)
    parent.wait_window(dialog)
    return dialog.selected_file


def show_custom_file_dialog(parent, directory):
    dialog = CustomFileDialog(parent, directory)
    parent.wait_window(dialog)
    return dialog.selected_file


def upload_background_image(mode = None):
    from vacantview.ui.gui_elements import CE

    if mode:
        
        file_path = mode#os.path.join('vacantview', IMG_DIR, mode)
       
    else:
        file_path = show_custom_file_dialog(win, os.path.join('vacantview', IMG_DIR))
    if not file_path or not os.path.exists(file_path):
        return
    

    bg_items = state.bg_canvas.find_withtag("background")
    for item in bg_items:
        state.bg_canvas.delete(item)
   
    if mode:
        state.image = Image.open(load_background_image(file_path,True))
    else:
        state.background_filepath = os.path.join('vacantview',IMG_DIR,file_path)#resource_path()
        state.image = Image.open(load_background_image(state.background_filepath))
    state.copy_of_image = state.image.copy()
    new_photo = ImageTk.PhotoImage(state.image)
    
    state.bg_image_id = state.bg_canvas.create_image(
        0, 0, anchor="nw", image=new_photo, tags=("background",)
    )
    state.bg_photo = new_photo
    state.bg_canvas.tag_lower(state.bg_image_id)
    
    state.bg_set_img = True
  
    create_elements = CE()
    event = type('Event', (object,), {
        'width': state.bg_canvas.winfo_width(),
        'height': state.bg_canvas.winfo_height()
    })()
        
    create_elements.resize_image(event)
  

    
def upload_logo_image(mode=None):
    from vacantview.ui.gui_elements import CE
    if not mode:
        file_path = show_custom_file_dialog(win, os.path.join('vacantview', LOGO_DIR))
       
        state.logo_file_path = file_path #resource_path()
    elif mode:
        file_path = mode
        
        state.logo_file_path = mode
    
    if not state.logo_file_path or not os.path.exists(state.logo_file_path):
        return

    create_elements = CE()

    logo_img = Image.open(state.logo_file_path).convert("RGBA")

   
    state.logo_original_img = logo_img
    state.logo_scale = 1.0
    
    canvas_height = state.bg_canvas.winfo_height()
    canvas_width = state.bg_canvas.winfo_width()
    state.logo_positions['x'] = 25
    state.logo_positions['y'] = 25
    
    resized_img = logo_img.copy()
    state.logo_photo = ImageTk.PhotoImage(resized_img)
    state.logo_image_id = state.bg_canvas.create_image(
        state.logo_positions['x'],state.logo_positions['y'],image=state.logo_photo,
        anchor="nw",
        tags=("logo",)
    )
    background_items = state.bg_canvas.find_withtag("background")
    if background_items:
        background_id = background_items[0]
        
        state.bg_canvas.tag_raise(state.logo_image_id, background_id)
    else:
       
        state.bg_canvas.tag_raise(state.logo_image_id)
    
def resize_logo(sign):
    if not hasattr(state, 'logo_original_img') or not hasattr(state, 'logo_scale'):
        return

    step = 1.3 if sign == '+' else 0.7 if sign == '-' else None
    if step is None:
        return 
    
    new_scale = state.logo_scale * step

    if 0.01 <= new_scale <= 3.0:
        state.logo_scale = new_scale

        w, h = state.logo_original_img.size
        new_size = (max(1, int(w * state.logo_scale)), max(1, int(h * state.logo_scale)))
        resized = state.logo_original_img.resize(new_size, Image.Resampling.LANCZOS)

        state.logo_photo = ImageTk.PhotoImage(resized)
        coords = state.bg_canvas.coords(state.logo_image_id)
        if len(coords) >= 2:
            state.logo_positions['x'] = coords[0]
            state.logo_positions['y'] = coords[1]
        state.bg_canvas.delete("logo")
        state.logo_image_id = state.bg_canvas.create_image(
            state.logo_positions['x'], state.logo_positions['y'],
            image=state.logo_photo,
            anchor="nw",
            tags=("logo",)
        )

def upload_logo_image_start(logo_import=None):
    from vacantview.ui.gui_elements import CE
    import os
    from PIL import Image, ImageTk

    if not logo_import:
        state.logo_file_path = os.path.join('vacantview', LOGO_DIR, LOGO_COMPANY)

    logo_full_path = resource_path(os.path.join('vacantview', LOGO_DIR, LOGO_COMPANY))
    if not state.logo_file_path or not os.path.exists(logo_full_path):
        if DEBUG:
            print(f" [ERROR] Logo image not found at: {state.logo_file_path}")
        return

    create_elements = CE()
    logo_img = Image.open(state.logo_file_path).convert("RGBA")
    state.logo_original_img = logo_img

    canvas_height = state.bg_canvas.winfo_height()
    canvas_width = state.bg_canvas.winfo_width()

   
    if canvas_height <= 1 or canvas_width <= 1:
        state.bg_canvas.after(100, lambda: upload_logo_image_start(logo_import))
        return

   
    prev_width, prev_height = getattr(state, "bg_canvas_prev_size", (0, 0))

    
    resolution_changed = (canvas_width != prev_width) or (canvas_height != prev_height)

    
    desired_logo_height = canvas_height // 40
    orig_width, orig_height = logo_img.size

 
    if not hasattr(state, "logo_scale") or state.logo_scale is None or resolution_changed:
        state.logo_scale = desired_logo_height / orig_height

    current_scale = state.logo_scale
    new_width = int(orig_width * current_scale)
    new_height = int(orig_height * current_scale)

    resized_img = logo_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    state.logo_photo = ImageTk.PhotoImage(resized_img)

   
    if not hasattr(state, "logo_rel_pos"):
        if hasattr(state, "logo_positions") and state.logo_positions and prev_width > 0 and prev_height > 0:
           
            rel_x = state.logo_positions['x'] / prev_width
            rel_y = state.logo_positions['y'] / prev_height
            state.logo_rel_pos = {'x': rel_x, 'y': rel_y}
        else:
            
            rel_x = (canvas_width - new_width - 15) / canvas_width
            rel_y = (canvas_height - new_height - 15) / canvas_height
            state.logo_rel_pos = {'x': rel_x, 'y': rel_y}

    
    abs_x = int(state.logo_rel_pos['x'] * canvas_width)
    abs_y = int(state.logo_rel_pos['y'] * canvas_height)
    state.logo_positions = {'x': abs_x, 'y': abs_y}

   
    if hasattr(state, "logo_image_id"):
        state.bg_canvas.delete(state.logo_image_id)

   
    state.logo_image_id = state.bg_canvas.create_image(
        abs_x,
        abs_y,
        image=state.logo_photo,
        anchor="nw",
        tags=("logo",)
    )

   
    state.bg_canvas_prev_size = (canvas_width, canvas_height)







def set_canvas_background_color(ident, color):
    from vacantview.ui.gui_elements import CE
    
    if hasattr(state, "bg_image_id"):
        try:
            state.bg_canvas.delete(state.bg_image_id)
        except:
            pass
        del state.bg_image_id
        del state.bg_photo
        del state.image
        del state.copy_of_image
        
    state.bg_fill_tag = ident
    
    state.bg_color = color
    state.bg_set_img = False
    create_elements = CE()
    event = type('Event', (object,), {
        'width': state.bg_canvas.winfo_width(),
        'height': state.bg_canvas.winfo_height()
    })()
    create_elements.resize_image(event)




