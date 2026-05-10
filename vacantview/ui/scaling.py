import tkinter as tk
from PIL import Image, ImageTk

class UIScaler:
    def __init__(self, root: tk.Tk, base_width=1000, base_height=800):
        self.root = root
        self.screen_width = root.winfo_screenwidth()
        self.screen_height = root.winfo_screenheight()
        self.base_width = base_width
        self.base_height = base_height

        
        self._original_font_sizes = {}

        
        self._original_images = {}

       
        self._photoimage_refs = {}

    def scale_window(self, width_ratio=0.4, height_ratio=0.25):
        win_width = int(self.screen_width * width_ratio)
        win_height = int(self.screen_height * height_ratio)
        x_pos = (self.screen_width - win_width) // 2
        y_pos = (self.screen_height - win_height) // 2
        self.root.geometry(f"{win_width}x{win_height}+{x_pos}+{y_pos}")
        return win_width, win_height

    def scale_font_size(self, base_height, factor=0.15, min_size=12):
        size = max(min_size, int(base_height * factor))
        return size

    def place_frame_center(self, frame, relwidth=0.9, relheight=0.8):
        frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=relwidth, relheight=relheight)

    def register_image(self, canvas: tk.Canvas, item_id, pil_image: Image.Image):
        """Register original PIL image for scaling later."""
        self._original_images[item_id] = pil_image

    def scale_canvas_items(self, canvas: tk.Canvas, current_width: int, current_height: int):
        scale_x = current_width / self.base_width
        scale_y = current_height / self.base_height

        all_items = canvas.find_all()

        for item in all_items:
            tags = canvas.gettags(item)
            item_type = canvas.type(item)

            
            if 'bg_image' in tags:
                
                continue

            if item_type in ('rectangle', 'oval', 'line', 'polygon'):
              
                canvas.scale(item, 0, 0, scale_x, scale_y)

            if item_type == 'text':
             
                
             
                font_str = canvas.itemcget(item, 'font')
                font_parts = font_str.split()
                if len(font_parts) >= 2:
                    font_family = font_parts[0]
                    try:
                        orig_size = int(font_parts[1])
                    except ValueError:
                        orig_size = 12
                    font_style = " ".join(font_parts[2:]) if len(font_parts) > 2 else ""

                    if item not in self._original_font_sizes:
                        self._original_font_sizes[item] = orig_size

                    base_size = self._original_font_sizes[item]
                    new_size = max(8, int(base_size * min(scale_x, scale_y)))
                    new_font = f"{font_family} {new_size} {font_style}".strip()
                    canvas.itemconfig(item, font=new_font)


            elif item_type == 'image':
               
                if item in self._original_images:
                    pil_img = self._original_images[item]
                    new_w = max(1, int(pil_img.width * scale_x))
                    new_h = max(1, int(pil_img.height * scale_y))
                    resized = pil_img.resize((new_w, new_h), Image.ANTIALIAS)
                    photo_img = ImageTk.PhotoImage(resized)
                    canvas.itemconfig(item, image=photo_img)
                    self._photoimage_refs[item] = photo_img  

                    
                    canvas.scale(item, 0, 0, scale_x, scale_y)

       
        canvas.tag_lower('background')

  
        canvas.config(width=current_width, height=current_height)
        canvas.update()
