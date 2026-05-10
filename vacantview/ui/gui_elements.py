import tkinter as tk
import os
import json

from tkinter import *
from PIL import Image, ImageTk  

from vacantview.core.state import state,g_auth
from vacantview.ui.context_menu.context_menu import show_context_menu
from vacantview.config.config import DEBUG, LOGO_DIR, LOGO_ACCESSIBLE
from vacantview.ui.image_loader import resource_path
from vacantview.ui.context_menu.functions.title_editor import scale_graph_elements_by_tag



from functools import partial

win = state.win

class Graphics:
    pass

class CE:

    def __init__(self):
        pass
    
    def draw_main_labels_2(self, canvas):
        
        if state.string_genderSelect.get() in ('MEN','WOMEN'):
            if state.string_genderSelect.get() in ('MEN',):
                canvas.create_text(150, 190, text=prepare_text_for_widget(_("TOTAL")), fill="white", font=("Arial", 12), tags=('TOTAL_3'))
                canvas.create_text(320, 370, text=prepare_text_for_widget(_("OCCUPIED")), fill="white", font=("Arial", 12), tags=('h2_o_add',), state='hidden')
                canvas.create_text(850, 570, text=prepare_text_for_widget(_("VACANT")), fill="white", font=("Arial", 12), tags=('h2_v_add',), state='hidden')

                
            elif state.string_genderSelect.get() in ('WOMEN',):
                canvas.create_text(520, 370, text=prepare_text_for_widget(_("VACANT")), fill="white", font=("Arial", 12), tags=('h2_v2_add',), state='hidden')
                canvas.create_text(670, 370, text=prepare_text_for_widget(_("OCCUPIED")), fill="white", font=("Arial", 12), tags=('h2_o2_add',), state='hidden')
                canvas.create_text(155, 195, text=prepare_text_for_widget(_("TOTAL")), fill="white", font=("Arial", 12), tags=('TOTAL_4'))

                
            canvas.create_text(750, 650, text=prepare_text_for_widget(_("WC IS BEING CLEANED, PLEASE USE WC IN FLOOR #1 ADD")), font=('Arial', 20, 'bold'), fill="yellow", state='hidden', tags=('cleaning_message_1_add'))
        else:
            canvas.create_text(150, 190, text=prepare_text_for_widget(_("TOTAL")), fill="white", font=("Arial", 12), tags=('TOTAL_3'))
            canvas.create_text(155, 195, text=prepare_text_for_widget(_("TOTAL")), fill="white", font=("Arial", 12), tags=('TOTAL_4'))

            canvas.create_text(850, 570, text=prepare_text_for_widget(_("VACANT")), fill="white", font=("Arial", 12), tags=('h2_v_add',), state='hidden')
            canvas.create_text(520, 370, text=prepare_text_for_widget(_("VACANT")), fill="white", font=("Arial", 12), tags=('h2_v2_add',), state='hidden')

            canvas.create_text(320, 370, text=prepare_text_for_widget(_("OCCUPIED")), fill="white", font=("Arial", 12), tags=('h2_o_add',), state='hidden')
            canvas.create_text(670, 370, text=prepare_text_for_widget(_("OCCUPIED")), fill="white", font=("Arial", 12), tags=('h2_o2_add',), state='hidden')

            canvas.create_text(750, 450, text=prepare_text_for_widget(_("WC IS BEING CLEANED, PLEASE USE WC IN FLOOR #2 ADD")), font=('Arial', 20, 'bold'), fill="yellow", state='hidden', tags=('cleaning_message_2_add'))
            canvas.create_text(750, 650, text=prepare_text_for_widget(_("WC IS BEING CLEANED, PLEASE USE WC IN FLOOR #1 ADD")), font=('Arial', 20, 'bold'), fill="yellow", state='hidden', tags=('cleaning_message_1_add'))
                    
    def draw_main_labels(self, canvas):
        
        canvas.create_text(400, 50, text=prepare_text_for_widget(_("WASHROOM OCCUPANCY")), fill="white", font=("Arial", 16, "bold"), tags=('h1',))
        canvas.create_text(150, 350, text=prepare_text_for_widget(_("VACANT")), fill="white", font=("Arial", 12), tags=('h2_v',))
        canvas.create_text(300, 350, text=prepare_text_for_widget(_("OCCUPIED")), fill="white", font=("Arial", 12), tags=('h2_o',))
        canvas.create_text(500, 350, text=prepare_text_for_widget(_("VACANT")), fill="white", font=("Arial", 12), tags=('h2_v2',))
        canvas.create_text(650, 350, text=prepare_text_for_widget(_("OCCUPIED")), fill="white", font=("Arial", 12), tags=('h2_o2',))
        
        if state.string_genderSelect.get() in ('MEN','WOMEN'):
            canvas.create_text(750, 650, text=prepare_text_for_widget(_("WC IS BEING CLEANED, PLEASE USE WC IN FLOOR #1")), font=('Arial', 20, 'bold'), fill="yellow", state='hidden', tags=('cleaning_message_1',))
        else:
            canvas.create_text(750, 450, text=prepare_text_for_widget(_("WC IS BEING CLEANED, PLEASE USE WC IN FLOOR #2")), font=('Arial', 20, 'bold'), fill="yellow", state='hidden', tags=('cleaning_message_2',))
            canvas.create_text(750, 650, text=prepare_text_for_widget(_("WC IS BEING CLEANED, PLEASE USE WC IN FLOOR #1")), font=('Arial', 20, 'bold'), fill="yellow", state='hidden', tags=('cleaning_message_1',))
        canvas.create_text(850, 550, text=prepare_text_for_widget(_("CUSTOM TEXT")), font=('Arial', 20, 'bold'), fill="white", state='hidden', tags=('custom_title_text',))

        
        canvas.create_line(400, 100, 400, 330, fill="white", width=3,tags=('v_line',))
        
        canvas.create_text(150, 190, text=prepare_text_for_widget(_("TOTAL")), fill="white", font=("Arial", 12),tags=('TOTAL_1','figure_men'))
        canvas.create_text(660, 190, text="TOTAL", fill="white", font=("Arial", 12),tags=('TOTAL_2','figure_women'))    
        
        #--------------------------------------------------MEN--------------------------------------------------------#
           
        radius = 25
        x, y = 150, 150
        canvas.create_oval(x - radius, y - radius, x + radius, y + radius,fill="", outline="white", width=3, tags=('total_circle_1','figure_men'))
        
        canvas.create_text(151, 150, text="", fill="white", font=("Arial", 24),tags=('Cubiculs_MEN','figure_men'))
        
        radius = 30
        x, y = 150, 50
        canvas.create_oval(x - radius, y - radius, x + radius, y + radius,fill="", outline="white", width=6, tags=('figure_men',))


        canvas.create_line(110, 97, 152, 90, fill="white", width=6,tags=('figure_men',))
        canvas.create_line(150, 90, 190, 97, fill="white", width=6,tags=('figure_men',))
        
        canvas.create_line(200, 107, 200, 198, fill="white", width=6,tags=('figure_men',))
        canvas.create_line(100.3, 198, 100.3, 107, fill="white", width=6,tags=('figure_men',))  
        
        #  Straight Lines
        # canvas.create_line(200, 107, 200, 197, fill="white", width=6, tags=('figure_men',))  # Right wall
        canvas.create_line(190, 206, 175.3, 304, fill="white", width=6, tags=('figure_men',))  # Inner right
        canvas.create_line(165, 310, 135, 310, fill="white", width=6, tags=('figure_men',))  # Bottom horizontal
        canvas.create_line(110, 206, 125, 300, fill="white", width=6, tags=('figure_men',))  # Inner left
        # canvas.create_line(101, 197, 101, 107, fill="white", width=6, tags=('figure_men',))  # Left wall


        # Fillets (arcs)

        # Top left corner
        canvas.create_arc(100, 97, 123, 125, start=90, extent=85, style='arc', outline="white", width=6, tags=('figure_men',))

        # Top right corner
        canvas.create_arc(177, 97, 200, 117, start=0, extent=85, style='arc', outline="white", width=6,tags=('figure_men',))

        # Inner right rounded corner
        canvas.create_arc(180, 187, 200, 207, start=270, extent=90, style='arc', outline="white", width=6,tags=('figure_men',))

        # Inner left rounded corner
        canvas.create_arc(100, 187, 120, 207, start=180, extent=90, style='arc', outline="white", width=6,tags=('figure_men',))

        # Bottom right rounded corner
        canvas.create_arc(156, 290, 176, 310, start=260, extent=90, style='arc', outline="white", width=6,tags=('figure_men',))

        # Bottom left rounded corner
        canvas.create_arc(125, 290, 145, 310, start=180, extent=90, style='arc', outline="white", width=6,tags=('figure_men',))

        #--------------------------------------------------WOMEN--------------------------------------------------------#
        
        
        radius = 30
        x, y = 660, 50  
        canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill="", outline="white", width=6, tags=('figure_women',))

        radius = 25
        x, y = 659, 150
        canvas.create_oval(x - radius, y - radius, x + radius, y + radius,fill="", outline="white", width=3, tags=('total_circle_2','figure_women'))
        
        canvas.create_text(660, 150, text="", fill="white", font=("Arial", 24),tags=('Cubiculs_WOMEN','figure_women'))

        canvas.create_line(627, 97.5, 662, 90, fill="white", width=6, tags=('figure_women',))
        canvas.create_line(661, 90, 690, 97, fill="white", width=6, tags=('figure_women',))

        canvas.create_line(698, 102, 708, 197, fill="white", width=6, tags=('figure_women',))
        canvas.create_line(610, 197, 620, 106, fill="white", width=6, tags=('figure_women',))

        # Inner right rounded corner

        canvas.create_arc(682.8, 187, 708, 207, start=270, extent=90, style='arc', outline="white", width=6, tags=('figure_women',))

        # Inner left rounded corner

        canvas.create_arc(610, 187, 636.9, 207, start=180, extent=90, style='arc', outline="white", width=6, tags=('figure_women',))

        # Top left corner
        canvas.create_arc(620, 97, 643, 120, start=110, extent=65, style='arc', outline="white", width=6, tags=('figure_women',))

        # Top right corner
        canvas.create_arc(675, 97, 698, 109, start=0, extent=80, style='arc', outline="white", width=6, tags=('figure_women',))

        canvas.create_line(690, 255, 675, 305, fill="white", width=6, tags=('figure_women',))  # Inner right
        canvas.create_line(665, 310, 655, 310, fill="white", width=6, tags=('figure_women',))  # Bottom horizontal
        canvas.create_line(630, 254, 645, 303, fill="white", width=6, tags=('figure_women',))  # Inner left
        canvas.create_line(623, 207, 618, 245, fill="white", width=6, tags=('figure_women',))  # Left
        canvas.create_line(695, 206.5, 700, 245, fill="white", width=6, tags=('figure_women',))  # Right


        # Bottom right rounded corner
        canvas.create_arc(656, 290, 676, 310, start=260, extent=90, style='arc', outline="white", width=6, tags=('figure_women',))

        # Bottom left rounded corner
        canvas.create_arc(645, 290, 665, 310, start=195, extent=90, style='arc', outline="white", width=6, tags=('figure_women',))

        canvas.create_arc(618, 238, 635, 255, start=165, extent=130, style='arc', outline="white", width=6, tags=('figure_women',))

        canvas.create_arc(682, 238, 700, 255, start=260, extent=115, style='arc', outline="white", width=6, tags=('figure_women',))
        
        
    def create_rect(self, win, color, position, ring_id='1'):
        graph = Graphics()
        canvas = state.bg_canvas
        gender = state.string_genderSelect.get()

        canvas.update_idletasks()
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()

        tag = ring_id
        
        elements = canvas.find_withtag(tag)
        
        tag = ring_id

        if elements:
           
            coords = canvas.bbox(tag)
            if coords:
      
            
                x1, y1, x2, y2 = coords
                x = (x1 + x2) // 2
                y = (y1 + y2) // 2
                size = max(x2 - x1, y2 - y1)
            else:
                relx, rely = position.get(gender, (0.5, 0.5))
                x = int(canvas_width * relx)
                y = int(canvas_height * rely)
                size = 250

        r = size // 2

        pad_outer = int(size * 0.02)
        pad_rect = int(size * 0.06)
        pad_inner = int(size * 0.16)
        
        graph.canvas = canvas
        graph.relx = x / canvas_width
        graph.rely = y / canvas_height
        graph.size = size

        canvas.delete(tag)

        graph.outring = canvas.create_rectangle(
            x - r + pad_outer, y - r + pad_outer, x + r - pad_outer, y + r - pad_outer,
            outline=state.outring_fill[ring_id], width=3, tags=(tag,)
        )

        graph.outer1 = canvas.create_rectangle(
            x - r + pad_rect, y - r + pad_rect, x + r - pad_rect, y + r - pad_rect,
            outline=state.ring_color_table[ring_id]["outline"],
            fill=state.ring_color_table[ring_id]["fill"], width=1, tags=(tag,)
        )

        graph.outer2 = canvas.create_rectangle(
            x - r + pad_rect, y - r + pad_rect, x + r - pad_rect, y + r - pad_rect,
            outline="", fill="", width=0, tags=(tag,)
        )

        graph.outer3 = canvas.create_rectangle(
            x - r + pad_inner, y - r + pad_inner, x + r - pad_inner, y + r - pad_inner,
            outline='white', fill=state.outer3_fill[ring_id], width=0, tags=(tag,)
        )

        font_size = max(12, int(size * 0.2))
        graph.text = canvas.create_text(
            x, y, anchor="center", font=("Arial", font_size), text="0", fill='white', tags=(tag,)
        )
        
        return graph


    def create_rounded(self, win, color_tuple, position, ring_id='1'):
        graph = Graphics()
        canvas = state.bg_canvas
        gender = state.string_genderSelect.get()

        canvas.update_idletasks()
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()

        tag = ring_id
        elements = canvas.find_withtag(tag)

        if elements:
            coords = canvas.bbox(tag)
            if coords:
                x1, y1, x2, y2 = coords
                x = (x1 + x2) // 2
                y = (y1 + y2) // 2
                size = max(x2 - x1, y2 - y1)
            else:
                relx, rely = position.get(gender, (0.5, 0.5))
                x = int(canvas_width * relx)
                y = int(canvas_height * rely)
                size = 250
        else:
            relx, rely = position.get(gender, (0.5, 0.5))
            x = int(canvas_width * relx)
            y = int(canvas_height * rely)
            size = 250

        r = size // 2

        # Padding similar to create_rect
        pad_outer = int(size * 0.02)
        pad_rect = int(size * 0.06)
        pad_inner = int(size * 0.16)

        canvas.delete(tag)
        graph.canvas = canvas
        color = list(color_tuple[:2])
        radius = max(10, size // 12)

        def create_rounded_rect(x1, y1, x2, y2, radius, outline='', fill='', width=1, tags=()):
            items = []
            arc_shift = 0.51

            items.append(canvas.create_rectangle(x1 + radius, y1, x2 - radius, y2,
                                                 outline=outline, fill=fill, width=width, tags=tags))
            items.append(canvas.create_rectangle(x1, y1 + radius, x2, y2 - radius,
                                                 outline=outline, fill=fill, width=width, tags=tags))

            items.append(canvas.create_arc(x1 + arc_shift, y1 + arc_shift, x1 + 2 * radius - arc_shift, y1 + 2 * radius - arc_shift,
                                           start=90, extent=90,
                                           outline=outline, fill=fill, width=width, tags=tags))
            items.append(canvas.create_arc(x2 - 2 * radius + arc_shift, y1 + arc_shift, x2 - arc_shift, y1 + 2 * radius - arc_shift,
                                           start=0, extent=90,
                                           outline=outline, fill=fill, width=width, tags=tags))
            items.append(canvas.create_arc(x2 - 2 * radius + arc_shift, y2 - 2 * radius + arc_shift, x2 - arc_shift, y2 - arc_shift,
                                           start=270, extent=90,
                                           outline=outline, fill=fill, width=width, tags=tags))
            items.append(canvas.create_arc(x1 + arc_shift, y2 - 2 * radius + arc_shift, x1 + 2 * radius - arc_shift, y2 - arc_shift,
                                           start=180, extent=90,
                                           outline=outline, fill=fill, width=width, tags=tags))
            return items

        # Main colored layer (pad_rect)
        graph.outer1_radius = radius
        graph.outer1 = create_rounded_rect(
            x - r + pad_rect, y - r + pad_rect, x + r - pad_rect, y + r - pad_rect,
            radius=radius,
            outline=state.ring_color_table[ring_id]["outline"], fill=state.ring_color_table[ring_id]["fill"], width=1, tags=(tag,)
        )

       # Instead of a regular rectangle, create a rounded one:
        graph.outer2 = create_rounded_rect(
            x - r + pad_rect, y - r + pad_rect, x + r - pad_rect, y + r - pad_rect,
            radius=radius,
            outline=color[1], fill=color[1], width=1, tags=(tag,)
                                                            )

        # Inner layer (pad_inner)
        graph.outer3_radius = radius
        graph.outer3 = create_rounded_rect(
            x - r + pad_inner, y - r + pad_inner, x + r - pad_inner, y + r - pad_inner,
            radius=radius,
            outline=state.outer3_fill[ring_id], fill=state.outer3_fill[ring_id], width=0, tags=(tag,)
        )

        font_size = max(12, int(size * 0.2))
        graph.text = canvas.create_text(
            x, y, anchor='center', font=f'Arial {font_size}',
            text="0", fill='white', tags=(tag, 'text')
        )

        graph.relx = x / canvas_width
        graph.rely = y / canvas_height
        graph.size = size

        return graph

    
    def create_ring(self, win, color, position, ring_id='1'):
        graph = Graphics()
        canvas = state.bg_canvas
        gender = state.string_genderSelect.get()

        canvas.update_idletasks()
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()

        tag = ring_id
        elements = canvas.find_withtag(tag)

        if elements:
            coords = canvas.bbox(tag)  # (x1, y1, x2, y2)
            if coords:
                x1, y1, x2, y2 = coords
                x = (x1 + x2) // 2
                y = (y1 + y2) // 2
                size = max(x2 - x1, y2 - y1)
            else:
                x = y = 0
                size = 250
        else:
            relx, rely = position.get(gender, (0.5, 0.5))
            x = int(canvas_width * relx)
            y = int(canvas_height * rely)
            size = 250

        r = size // 2

      
        pad_outer = int(size * 0.02)   
        pad_arc = int(size * 0.06)     
        pad_inner = int(size * 0.16)   

        # Saving data
        graph.relx = x / canvas_width
        graph.rely = y / canvas_height
        graph.canvas = canvas
        graph.size = size

        # Delete previous elements only after calculating the bbox
        canvas.delete(ring_id)

        # Redrawing the ring
        graph.outring = canvas.create_oval(
            x - r + pad_outer, y - r + pad_outer, x + r - pad_outer, y + r - pad_outer,
            outline=state.outring_fill[ring_id], width=3, tags=(tag,)
        )
        # outline=state.ring_color_table[ring_id]["outline"] , fill=state.ring_color_table[ring_id]["fill"]
        graph.outer1 = canvas.create_arc(
            x - r + pad_arc, y - r + pad_arc, x + r - pad_arc, y + r - pad_arc,
            extent=359.9, outline=state.ring_color_table[ring_id]["outline"], fill=state.ring_color_table[ring_id]["fill"], width=1, tags=(tag,)
        )
        
        graph.outer2 = canvas.create_arc(
            x - r + pad_arc, y - r + pad_arc, x + r - pad_arc, y + r - pad_arc,
            start=0, extent=0 , width=3, tags=(tag,)
        )

        graph.outer3 = canvas.create_oval(
            x - r + pad_inner, y - r + pad_inner, x + r - pad_inner, y + r - pad_inner,
            outline='white', fill=state.outer3_fill[ring_id], width=0, tags=(tag,)
        )

        graph.text = canvas.create_text(
            x, y, anchor="center", font=("Arial", int(size * 0.2)), text="0", fill='white', tags=(tag,)
        )

        return graph


    # Creating accessibility panels
    def create_accessible_panel(self, accessible_panel_type: str):
        canvas = state.bg_canvas
        tag = accessible_panel_type
        if accessible_panel_type == 'accessible_panel_men':
            
            x1, y1 = 10, 10
            original_width = 180
            panel_width = original_width * 0.75 * 0.9  # 
            x2 = x1 + panel_width
            y2 = 50
        elif accessible_panel_type == 'accessible_panel_women':
            
            x1, y1 = 500, 10
            original_width = 180
            panel_width = original_width * 0.75 * 0.9  
            x2 = x1 + panel_width
            y2 = 50
            
        r = 10
        spacing = 5

        def draw_rounded_rect_outline(x1, y1, x2, y2, r, **kwargs):
            items = []

            line_color = kwargs.pop("fill", "white")
            line_width = kwargs.pop("width", 2) * 2  

            # Straight lines
            items.append(canvas.create_line(x1 + r, y1, x2 - r, y1, fill=line_color, width=line_width, **kwargs))
            items.append(canvas.create_line(x1 + r, y2, x2 - r, y2, fill=line_color, width=line_width, **kwargs))
            items.append(canvas.create_line(x1, y1 + r, x1, y2 - r, fill=line_color, width=line_width, **kwargs))
            items.append(canvas.create_line(x2, y1 + r, x2, y2 - r, fill=line_color, width=line_width, **kwargs))

            arc_kwargs = {
                **kwargs,
                "style": "arc",
                "outline": line_color,
                "width": line_width
            }

            # Arches (fillets)
            items.append(canvas.create_arc(x1, y1, x1 + 2 * r, y1 + 2 * r, start=90, extent=90, **arc_kwargs))
            items.append(canvas.create_arc(x2 - 2 * r, y1, x2, y1 + 2 * r, start=0, extent=90, **arc_kwargs))
            items.append(canvas.create_arc(x2 - 2 * r, y2 - 2 * r, x2, y2, start=270, extent=90, **arc_kwargs))
            items.append(canvas.create_arc(x1, y2 - 2 * r, x1 + 2 * r, y2, start=180, extent=90, **arc_kwargs))

            return items	

        frame_items = draw_rounded_rect_outline(
            x1, y1, x2, y2, r, fill="white", width=2, tags=(tag,)
        )
        
        # Icon on the left
        icon_space = 40
        icon_left = x1 + spacing
        icon_top = y1 + spacing
        icon_right = x1 + icon_space
        icon_bottom = y2 - spacing

        icon_box = canvas.create_rectangle(
            icon_left, icon_top, icon_right, icon_bottom,
            outline="", fill="", tags=(tag, 'accessible_icon')
        )
        
        state.icon_rect = icon_box 

        icon_width = icon_right - icon_left
        icon_height = icon_bottom - icon_top
        
        icon_accessiable_path = os.path.join('vacantview', LOGO_DIR, LOGO_ACCESSIBLE)
        
        try:
            icon_image = Image.open(icon_accessiable_path)
            

            scale = 1.1
            new_w = int(icon_width * scale)
            new_h = int(icon_height * scale)
            icon_image = icon_image.resize((new_w, new_h),Image.Resampling.LANCZOS )

            if not hasattr(self, 'tk_icons'):
                state.tk_icons = {}

            state.tk_icons[tag] = ImageTk.PhotoImage(icon_image)
            if accessible_panel_type == 'accessible_panel_men': 
                canvas.create_image(
                    (icon_left + icon_right) // 2,
                    (icon_top + icon_bottom) // 2,
                    image=self.tk_icons[tag],
                    tags=(icon_accessiable_path, tag, 'accessible_icon_image_men')
                )
            elif accessible_panel_type == 'accessible_panel_women':
                canvas.create_image(
                    (icon_left + icon_right) // 2,
                    (icon_top + icon_bottom) // 2,
                    image=self.tk_icons[tag],
                    tags=(icon_accessiable_path, tag, 'accessible_icon_image_men')
                )
            
        except Exception as e:
            print(f"Error: {e}")

        box_area_left = icon_right + spacing
        box_area_right = x2 - spacing
        total_box_area = box_area_right - box_area_left
        box_width = (total_box_area - spacing) / 2  

        green_left = box_area_left
        green_right = green_left + box_width
        green_box = canvas.create_rectangle(
            green_left, y1 + spacing, green_right, y2 - spacing,
            fill="green", outline="", tags=('accessible_vacant', tag)
        )
        if accessible_panel_type == 'accessible_panel_men':
            green_text = canvas.create_text(
                (green_left + green_right) // 2, (y1 + y2) // 2,
                text="0", fill="white", font="Arial 14 bold", tags=('accessible_vacant_indicator_men', tag)
            )
        elif accessible_panel_type == 'accessible_panel_women':
            green_text = canvas.create_text(
                (green_left + green_right) // 2, (y1 + y2) // 2,
                text="0", fill="white", font="Arial 14 bold", tags=('accessible_vacant_indicator_women', tag)
            )
        red_left = green_right + spacing
        red_right = red_left + box_width
        red_box = canvas.create_rectangle(
            red_left, y1 + spacing, red_right, y2 - spacing,
            fill="red", outline="", tags=('accessible_occup', tag)
        )
        if accessible_panel_type == 'accessible_panel_men':
            red_text = canvas.create_text(
                (red_left + red_right) // 2, (y1 + y2) // 2,
                text="0", fill="white", font="Arial 14 bold", tags=('accessible_occup_indicator_men', tag)
            )
            
        elif accessible_panel_type == 'accessible_panel_women':
            red_text = canvas.create_text(
                (red_left + red_right) // 2, (y1 + y2) // 2,
                text="0", fill="white", font="Arial 14 bold", tags=('accessible_occup_indicator_women', tag)
            )

        return {
            "frame": frame_items,
            "icon_box": icon_box,
            "green_box": green_box,
            "green_text": green_text,
            "red_box": red_box,
            "red_text": red_text
        }
    
    def update_rect_data(self, graph, value, total, ring_id=None):
        if ring_id and ring_id in state.text_color:
            text_fill = state.text_color.get(ring_id, 'white')
            graph.canvas.itemconfig(graph.text, text=str(value), fill=text_fill)
        else:
            graph.canvas.itemconfig(graph.text, text=str(value))

        if ring_id in ('graph_M_GREEN', 'graph_w_GREEN'):
            color = state.ring_color_table.get(ring_id, {"fill": "#888888", "outline": "#888888"})
            color_add = state.ring_color_add_table.get(ring_id, {"fill": "#888888", "outline": "#888888"})
        elif ring_id in ('graph_M_RED', 'graph_w_RED'):
            color = state.ring_color_table.get(ring_id, {"fill": "#888888", "outline": "#888888"})
            color_add = state.ring_color_add_table.get(ring_id, {"fill": "#888888", "outline": "#888888"})
        else:
            # Если ring_id не подходит, задаём цвета по умолчанию
            color = {"fill": "#888888", "outline": "#888888"}
            color_add = {"fill": "#888888", "outline": "#888888"}

        outline_color = color["outline"]
        fill_color = color["fill"]

        if state.a_progress_on:
            fill_add = color_add["outline"]
            outline_add = color_add["fill"]
        else:
            fill_add = fill_color
            outline_add = outline_color

        try:
            coords_outer1 = graph.canvas.bbox(graph.outer1)
            if coords_outer1:
                x0, y0, x1, y1 = coords_outer1
                
                line_width_outer1 = 1  
                half_line = line_width_outer1 / 2

                
                x0_adj = x0 + half_line
                y0_adj = y0 + half_line
                x1_adj = x1 - half_line
                y1_adj = y1 - half_line

                full_width = x1_adj - x0_adj
            else:
                return
        except Exception as e:
            if DEBUG:
                print(f"Failed to get bbox for outer1: {e}")
            return

        if value == 0 or total == 0:
            try:
                if graph.outer2:
                    graph.canvas.delete(graph.outer2)
                    graph.outer2 = None
            except Exception as e:
                if DEBUG:
                    print(f"Failed to delete outer2: {e}")
        else:
            if not state.a_progress_on:
                bar_left = x0_adj
                bar_right = x1_adj
            else:
                progress_ratio = value / total
                bar_width = int(full_width * progress_ratio)
                bar_left = x0_adj
                bar_right = x0_adj + bar_width

            bar_top = y0_adj
            bar_bottom = y1_adj

            if graph.outer2 is None:
                graph.outer2 = graph.canvas.create_rectangle(
                    bar_left, bar_top, bar_right, bar_bottom,
                    fill=fill_add,
                    outline=outline_add,
                    width=3,
                    tags=(ring_id,)
                )
            else:
                graph.canvas.coords(graph.outer2, bar_left, bar_top, bar_right, bar_bottom)
                graph.canvas.itemconfig(graph.outer2, fill=fill_add, outline=outline_add)

        state.bg_canvas.tag_raise(graph.outer3)
        graph.canvas.tag_raise(graph.text)

    
    def update_rounded_data(self, graph, value, total, ring_id=None):
        canvas = graph.canvas

        # Text update
        if ring_id and ring_id in state.text_color:
            text_fill = state.text_color.get(ring_id, 'white')
            canvas.itemconfig(graph.text, text=str(value), fill=text_fill)
        else:
            canvas.itemconfig(graph.text, text=str(value))

        # Color assignment based on ring_id
        if ring_id in ('graph_M_GREEN', 'graph_w_GREEN'):
            color = state.ring_color_table.get(ring_id, {"fill": "#888888", "outline": "#888888"})
            color_add = state.ring_color_add_table.get(ring_id, {"fill": "#888888", "outline": "#888888"})
        elif ring_id in ('graph_M_RED', 'graph_w_RED'):
            color = state.ring_color_table.get(ring_id, {"fill": "#888888", "outline": "#888888"})
            color_add = state.ring_color_add_table.get(ring_id, {"fill": "#888888", "outline": "#888888"})
        else:
            color = {"fill": "#888888", "outline": "#888888"}
            color_add = {"fill": "#888888", "outline": "#888888"}

        outline_color = color["outline"]
        fill_color = color["fill"]

        if state.a_progress_on:
            fill_add = color_add["outline"]
            outline_add = color_add["fill"]
        else:
            fill_add = fill_color
            outline_add = outline_color

        # Get the bbox specifically for outer1 so that the dimensions match outer2
        coords = None
        if graph.outer1:
            if isinstance(graph.outer1, list) and graph.outer1:
                coords = canvas.bbox(graph.outer1[0])
            elif graph.outer1:
                coords = canvas.bbox(graph.outer1)

        if coords:
            x1, y1, x2, y2 = coords
            x = (x1 + x2) // 2
            y = (y1 + y2) // 2
            size = max(x2 - x1, y2 - y1)
        else:
            canvas_width = canvas.winfo_width()
            canvas_height = canvas.winfo_height()
            x = int(graph.relx * canvas_width)
            y = int(graph.rely * canvas_height)
            size = graph.size

        r = size // 2

        # Full coordinates of outer1 without padding (so that outer2 is at the same scale)
        coords_outer1_full = (x - r, y - r, x + r, y + r)
        x0, y0, x1, y1 = coords_outer1_full
        full_width = x1 - x0
        height = y1 - y0

        def create_rounded_progress_bar(left, top, right, bottom, radius, outline, fill, width, tags):
            items = []
            bar_width = right - left

            if bar_width <= 0:
                return items
            if bar_width < 2 * radius:
                # If the width is very small, draw an oval with the width of bar\_width
                items.append(canvas.create_oval(
                    left, top, left + bar_width, bottom,
                    outline=outline, fill=fill, width=width, tags=tags))
            else:
                arc_shift = 0.51
                items.append(canvas.create_rectangle(
                    left + radius, top, right - radius, bottom,
                    outline=outline, fill=fill, width=width, tags=tags))
                items.append(canvas.create_rectangle(
                    left, top + radius, right, bottom - radius,
                    outline=outline, fill=fill, width=width, tags=tags))
                items.append(canvas.create_arc(
                    left + arc_shift, top + arc_shift,
                    left + 2 * radius - arc_shift, top + 2 * radius - arc_shift,
                    start=90, extent=90,
                    outline=outline, fill=fill, width=width, tags=tags))
                items.append(canvas.create_arc(
                    right - 2 * radius + arc_shift, top + arc_shift,
                    right - arc_shift, top + 2 * radius - arc_shift,
                    start=0, extent=90,
                    outline=outline, fill=fill, width=width, tags=tags))
                items.append(canvas.create_arc(
                    right - 2 * radius + arc_shift, bottom - 2 * radius + arc_shift,
                    right - arc_shift, bottom - arc_shift,
                    start=270, extent=90,
                    outline=outline, fill=fill, width=width, tags=tags))
                items.append(canvas.create_arc(
                    left + arc_shift, bottom - 2 * radius + arc_shift,
                    left + 2 * radius - arc_shift, bottom - arc_shift,
                    start=180, extent=90,
                    outline=outline, fill=fill, width=width, tags=tags))
            return items

        # Update or delete outer2 depending on the value
        if value == 0 or total == 0:
            if graph.outer2:
                if isinstance(graph.outer2, list):
                    for item in graph.outer2:
                        canvas.delete(item)
                else:
                    canvas.delete(graph.outer2)
                graph.outer2 = None
        else:
            if not state.a_progress_on:
                bar_left = x0
                bar_right = x1
            else:
                progress_ratio = value / total
                bar_width = int(full_width * progress_ratio)
                bar_left = x0
                bar_right = x0 + bar_width

            bar_top = y0
            bar_bottom = y1

            radius = getattr(graph, 'outer1_radius', max(10, height // 12))

            # Delete the old outer2
            if graph.outer2:
                if isinstance(graph.outer2, list):
                    for item in graph.outer2:
                        canvas.delete(item)
                else:
                    canvas.delete(graph.outer2)

            # Create a new outer2 with animated fill and rounded corners
            graph.outer2 = create_rounded_progress_bar(
                bar_left, bar_top, bar_right, bar_bottom,
                radius=radius,
                outline=outline_add,
                fill=fill_add,
                width=1,
                tags=(ring_id,)
            )

        # Layer management: outer3 on top, outer2 below outer3, text above everything
        if graph.outer3:
            if isinstance(graph.outer3, list):
                for item in graph.outer3:
                    canvas.tag_raise(item)
                ref_item = graph.outer3[0] if graph.outer3 else None
            else:
                canvas.tag_raise(graph.outer3)
                ref_item = graph.outer3
        else:
            ref_item = None

        if graph.outer2 and ref_item:
            if isinstance(graph.outer2, list):
                for item in graph.outer2:
                    try:
                        canvas.tag_lower(item, ref_item)
                    except Exception:
                        pass
            else:
                try:
                    canvas.tag_lower(graph.outer2, ref_item)
                except Exception:
                    pass

        canvas.tag_raise(graph.text)
    
    def update_ring_data(self, graph, value, total, ring_id=None):
        if ring_id and ring_id in state.text_color:
            text_fill = state.text_color.get(ring_id, 'white')
            graph.canvas.itemconfig(graph.text, text=str(value), fill=text_fill)
        else:
            graph.canvas.itemconfig(graph.text, text=str(value))
       
        if state.indicator_type in ('circle',):
            if ring_id in ('graph_M_GREEN', 'graph_w_GREEN'):
                color = state.ring_color_table.get(ring_id, {"fill": "#888888", "outline": "#888888"})
                color_add = state.ring_color_add_table.get(ring_id, {"fill": "#888888", "outline": "#888888"})

            elif ring_id in ('graph_M_RED', 'graph_w_RED'):
                color = state.ring_color_table.get(ring_id, {"fill": "#888888", "outline": "#888888"})
                color_add = state.ring_color_add_table.get(ring_id, {"fill": "#888888", "outline": "#888888"})

            outline_color = color["outline"]
            fill_color = color["fill"]

            if state.a_progress_on:
                fill_add = color_add["outline"]
                outline_add = color_add["fill"]
            else:
                fill_add = fill_color
                outline_add = outline_color

            extent = -359.9 * (value / total) if total != 0 else 360

            def config_item(item, **kwargs):
                try:
                    if isinstance(item, (list, tuple)):
                        for subitem in item:
                            graph.canvas.itemconfig(subitem, **kwargs)
                    else:
                        graph.canvas.itemconfig(item, **kwargs)
                except Exception as e:
                    if DEBUG:
                        print(f"itemconfig error on item {item} with kwargs {kwargs}: {e}")

            try:
                coords = graph.canvas.bbox(ring_id)
                if coords:
                    x = (coords[0] + coords[2]) // 2
                    y = (coords[1] + coords[3]) // 2
                else:
                    return  
            except Exception as e:
                if DEBUG:
                    print(f"Failed to get position for ring_id '{ring_id}': {e}")
                return

            if graph.outer2 is not None and graph.canvas.type(graph.outer2) not in ("arc", "rectangle"):
                return

            # Calculate dynamic paddings matching create\_ring
            r = graph.size // 2
            pad_mid = int(graph.size * 0.06) 

            if value == 0 or (total == 0 and not state.a_progress_on):
                try:
                    if graph.outer2:
                        graph.canvas.delete(graph.outer2)
                        graph.outer2 = None
                except Exception as e:
                    if DEBUG:
                        print(f"Failed to delete outer2: {e}")
            else:
                extent = -359.9 * (value / total) if total != 0 else 360
                if graph.outer2 is None:
                    graph.outer2 = graph.canvas.create_arc(
                        x - r + pad_mid, y - r + pad_mid, x + r - pad_mid, y + r - pad_mid,
                        start=0,
                        extent=extent,
                        fill=fill_add,
                        outline=fill_add,
                        width=3,
                        tags=(ring_id,)
                    )
                else:
                    if graph.canvas.type(graph.outer2) == "arc":
                        graph.canvas.itemconfig(
                            graph.outer2,
                            extent=extent,
                            fill=fill_add,
                            outline=fill_add
                        )
                    else:
                        x0, y0, x1, y1 = graph.canvas.coords(graph.outer2)
                        full_width = x1 - x0
                        new_width = full_width * (value / total)
                        graph.canvas.coords(graph.outer2, x0, y0, x0 + new_width, y1)
                        graph.canvas.itemconfig(
                            graph.outer2,
                            fill=outline_color,
                            outline=outline_color
                        )

            state.bg_canvas.tag_raise(graph.outer3)
            graph.canvas.tag_raise(graph.text)

   
    def update_all_rings(self, cansize, font):
        is_both = state.string_genderSelect.get() == "BOTH"
        self.update_ring_coords(state.graph_M_GREEN, cansize, font, is_both, "graph_M_GREEN")
        self.update_ring_coords(state.graph_M_RED, cansize, font, is_both, "graph_M_RED")
        self.update_ring_coords(state.graph_w_GREEN, cansize, font, is_both, "graph_w_GREEN")
        self.update_ring_coords(state.graph_w_RED, cansize, font, is_both, "graph_w_RED")
    

    
    def resize_image(self, event):
        
        new_width = event.width
        new_height = event.height
         
        
        ratio = int(new_width * 0.02 + new_height * 0.03)
        ratio2 = int(new_width * 0.015 + new_height * 0.02)
        ratio3 = int(new_width * 0.0085 + new_height * 0.002)

        if hasattr(state, "copy_of_image"):
           
            orig_w, orig_h = state.copy_of_image.size
            scale = min(new_width / orig_w, new_height / orig_h)

            scaled_w = int(orig_w * scale)
            scaled_h = int(orig_h * scale)

            resized_img = state.copy_of_image.resize((scaled_w, scaled_h), Image.LANCZOS)
            photo = ImageTk.PhotoImage(resized_img)

           
            x = (new_width - scaled_w) // 2
            y = (new_height - scaled_h) // 2

           
            if hasattr(state, "bg_image_id") and state.bg_image_id:
                state.bg_canvas.itemconfig(state.bg_image_id, image=photo)
                state.bg_canvas.coords(state.bg_image_id, x, y)
            else:
                state.bg_image_id = state.bg_canvas.create_image(x, y, anchor="nw", image=photo)

            state.bg_photo = photo

        elif hasattr(state, "bg_color"):
        
            tag = getattr(state, "bg_fill_tag", "background")
            existing = state.bg_canvas.find_withtag(tag)

            if existing:
                rect_id = existing[0]
                state.bg_canvas.coords(rect_id, 0, 0, new_width, new_height)
                state.bg_canvas.itemconfig(rect_id, fill=state.bg_color, outline=state.bg_color)
            else:
                rect_id = state.bg_canvas.create_rectangle(
                    0, 0, new_width, new_height,
                    fill=state.bg_color, outline=state.bg_color, tags=(tag,)
                )
                state.bg_canvas.tag_lower(rect_id)

       
        state.new_font[1] = ratio
        state.new_font_CUBICLES = f"Arial, {ratio2}"
        state.new_font_CUBICLES_BOTH = f"Arial, {ratio3}"
        state.int_cansize = new_height * 0.3 + new_width * 0.01

        ratio4 = int(new_width * 0.012 + new_height * 0.004)
        state.new_font_clean = f"Arial {ratio4} bold"


            
class AdminElements:
    
    def __init__(self):
        pass
    
    def Create_CButton(self, window):
    

       state.admin_button = tk.Button(
                                win,
                                text="⚙",
                                font=("Arial", 14),
                                bg="#eeeeee",
                                relief="flat",
                                command=lambda: window(win))
        
    

