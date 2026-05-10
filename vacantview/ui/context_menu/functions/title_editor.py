import tkinter as tk
import re
from tkinter import Toplevel, ttk
from vacantview.core.state import g_auth, state
from vacantview.config.config import DEBUG
import tkinter.font as tkFont
import tkinter.messagebox as mb
from vacantview.ui.context_menu.rtl_func import prepare_text_for_widget

def get_line_delta(tag):
    coords = state.bg_canvas.coords(tag)
    if len(coords) < 4:
        return None

    x_coords = coords[0::2]
    y_coords = coords[1::2]

    if all(x == x_coords[0] for x in x_coords):
        length = abs(y_coords[1] - y_coords[0]) / 2
    elif all(y == y_coords[0] for y in y_coords):
        length = abs(x_coords[1] - x_coords[0]) / 2
    else:
        return None

    return int(length)

def adjust_line_delta(tag, delta):
    try:
        delta = max(delta, 10)

        coords = state.bg_canvas.coords(tag)
        if len(coords) < 4 or len(coords) % 2 != 0:
            print(f"[WARNING] Invalid line coords: {coords}")
            return

        x_coords = coords[0::2]
        y_coords = coords[1::2]
        
        if all(x == x_coords[0] for x in x_coords):
            y_center = sum(y_coords) / len(y_coords)
            new_y_coords = [y_center - delta, y_center + delta]
            new_coords = []
            for y in new_y_coords:
                new_coords.extend([x_coords[0], y])
            state.bg_canvas.coords(tag, *new_coords)

        elif all(y == y_coords[0] for y in y_coords):
            x_center = sum(x_coords) / len(x_coords)
            new_x_coords = [x_center - delta, x_center + delta]
            new_coords = []
            for x in new_x_coords:
                new_coords.extend([x, y_coords[0]])
            state.bg_canvas.coords(tag, *new_coords)

        else:
            print(f"[WARNING] Line is neither vertical nor horizontal: {coords}")

    except Exception as e:
        print(f"[WARNING] Failed to adjust line delta: {e}")


def make_line_horizontal(tag):
    try:
        coords =  state.bg_canvas.coords(tag)
        if len(coords) < 4 or len(coords) % 2 != 0:
            if DEBUG:
                print(f"[WARNING] Invalid line coords: {coords}")
            return

        y_fixed = coords[1]
        x_coords = coords[::2]

        
        if all(x == x_coords[0] for x in x_coords):
            delta = get_line_delta(tag)
            x_coords = [x_coords[0] - delta, x_coords[0] + delta]

        new_coords = []
        for x in x_coords:
            new_coords.extend([x, y_fixed])

        state.bg_canvas.coords(tag, *new_coords)
        state.line_vertical_pos = False

    except Exception as e:
        if DEBUG:
            print(f"[WARNING] Failed to make line horizontal: {e}")
        return
    
def make_line_vertical(tag):
    try:
        coords = state.bg_canvas.coords(tag)
        if len(coords) < 4 or len(coords) % 2 != 0:
            if DEBUG:
                print(f"[WARNING] Invalid line coords: {coords}")
            return

        x_fixed = coords[0]
        y_coords = coords[1::2]

        if all(y == y_coords[0] for y in y_coords):
            delta = get_line_delta(tag)
            y_coords = [y_coords[0] - delta, y_coords[0] + delta]

        new_coords = []
        for y in y_coords:
            new_coords.extend([x_fixed, y])

        state.bg_canvas.coords(tag, *new_coords)
        state.line_vertical_pos = True

    except Exception as e:
        if DEBUG:
            print(f"[WARNING] Failed to make line vertical: {e}")
        return
        
def edit_line_width(tag,new_width):
    
    try:
        setattr(state,f'font_{tag}',new_width)
        state.bg_canvas.itemconfig(tag, width=new_width)
    except Exception as e:
        print(f'[WARNING] Failed to update width line: {e}')    
        
def edit_main_title_text(tag, new_text):
      
    try:
        cleaned_text = re.sub(r'\s+', ' ', new_text.strip())

        if not cleaned_text:
            print('[WARNING] Empty text.')
            return
        
        state.bg_canvas.itemconfig(tag, text=cleaned_text)

    except Exception as e:
        print(f'[WARNING] Failed to update main title text: {e}')



def change_main_title_font(tag, new_font):
    try:
        current = state.bg_canvas.itemcget(tag, 'font').strip()

        if current.startswith('{'):
            match = re.match(r'^\{(.+?)\}\s+(\d+)(.*)$', current)
        else:
            match = re.match(r'^(.+?)\s+(\d+)(.*)$', current)

        if not match:
            if DEBUG:
                print(f"[WARNING] Failed to parse font string: '{current}'")
            return

        font_name, size_str, styles_str = match.groups()
        size = int(size_str)
        styles = styles_str.strip().split() if styles_str else []

        test_font = tkFont.Font(family=new_font, size=size)
        available_styles = {
            "bold": test_font.actual("weight") == "bold",
            "italic": test_font.actual("slant") == "italic",
            "underline": test_font.actual("underline") == 1,
            "overstrike": test_font.actual("overstrike") == 1
        }

        valid_styles = []
        unsupported_styles = []
        for style in styles:
            style_lower = style.lower()
            if style_lower in available_styles and available_styles[style_lower]:
                valid_styles.append(style_lower)
            elif style_lower in available_styles:
                unsupported_styles.append(style_lower)

        if valid_styles:
            final_font = (new_font, size, " ".join(valid_styles))
        else:
            final_font = (new_font, size)

        setattr(state, f'font_{tag}', final_font)
        state.bg_canvas.itemconfig(tag, font=final_font)

        if unsupported_styles and DEBUG:
            print(f"[WARNING] Styles {unsupported_styles} cannot be applied to font '{new_font}'")

    except Exception as e:
        print(f'[WARNING] Failed to change main title font: {e}')

        
def change_main_title_font_size(tag,size):
    try:
        current = state.bg_canvas.itemcget(tag, 'font').strip()

        if current.startswith('{'):
            match = re.match(r'^\{(.+?)\}\s+(\d+)(.*)$', current)
        else:
            match = re.match(r'^(.+?)\s+(\d+)(.*)$', current)

        if not match:
            if DEBUG:
                print(f"[WARNING] Failed to parse font string: '{current}'")
            else:
                pass

        font_name, _, styles_str = match.groups()
        
        styles = styles_str.strip().split() if styles_str else []
        print(styles)
        final_font = (font_name, int(size), *styles)
        setattr(state,f'font_{tag}',final_font)
        state.bg_canvas.itemconfig(tag, font=final_font)

    except Exception as e:
        print(f'[WARNING] Failed to change main title font size: {e}')
        
def change_main_title_font_style(tag, style):
    try:
        current = state.bg_canvas.itemcget(tag, 'font').strip()

        try:
            font_obj = tkFont.nametofont(current)
            font_name = font_obj.actual()['family']
            size = font_obj.actual()['size']
        except tk.TclError:
            if current.startswith('{'):
                match = re.match(r'^\{(.+?)\}\s+(\d+)\s*(.*)$', current)
            else:
                match = re.match(r'^(.+?)\s+(\d+)\s*(.*)$', current)

            if not match:
                if DEBUG:
                    print(f"[WARNING] Failed to parse font string: '{current}'")
                return

            font_name, size_str, _ = match.groups()
            size = int(size_str)

        weight = 'bold' if 'bold' in style.lower() else 'normal'
        slant = 'italic' if 'italic' in style.lower() else 'roman'

        test_font = tkFont.Font(family=font_name, size=size, weight=weight, slant=slant)
        actual = test_font.actual()

        if (weight == 'bold' and actual['weight'] != 'bold') or (slant == 'italic' and actual['slant'] != 'italic'):
            mb.showerror("Font Error",
             f"The font '{font_name}' does not support the style '{style}'.")
            return  

        
        style_parts = []
        if weight == 'bold':
            style_parts.append('bold')
        if slant == 'italic':
            style_parts.append('italic')
        style_str = ' '.join(style_parts) or 'normal'

        final_font = (font_name, size, style_str)

        setattr(state, f'font_{tag}', final_font)
        state.bg_canvas.itemconfig(tag, font=final_font)

    except Exception as e:
        print(f'[WARNING] Failed to change main title font style: {e}')

def scale_tagged_items(tag, direction):
    canvas = state.bg_canvas
    scale_factor = 1.1 if direction == '+' else 0.9

    items = canvas.find_withtag(tag)

    all_coords = []
    for item in items:
        all_coords += canvas.coords(item)

    if not all_coords:
        return

    x_coords = all_coords[::2]
    y_coords = all_coords[1::2]
    center_x = sum(x_coords) / len(x_coords)
    center_y = sum(y_coords) / len(y_coords)

    for item in items:
        coords = canvas.coords(item)
        item_type = canvas.type(item)

        new_coords = []
        for i, coord in enumerate(coords):
            if i % 2 == 0:  # X
                offset = coord - center_x
                new_coord = center_x + offset * scale_factor
            else:  # Y
                offset = coord - center_y
                new_coord = center_y + offset * scale_factor
            new_coords.append(new_coord)

        canvas.coords(item, *new_coords)

        if item_type == 'text':
            current_font = canvas.itemcget(item, "font")
            parts = current_font.split()
            size_index = next((i for i, p in enumerate(parts) if p.isdigit()), None)
            if size_index is not None:
                try:
                    size = float(parts[size_index])
                    new_size = size * scale_factor
                    if new_size < 1:
                        new_size = 1
                    parts[size_index] = str(int(round(new_size)))
                    canvas.itemconfig(item, font=" ".join(parts))
                except ValueError:
                    pass 

def scale_graph_elements_by_tag(tag, direction):
    canvas = state.bg_canvas
    if direction:
        
        if direction not in ("+", "-"):
            if DEBUG:
                print(f"[scale_graph_elements_by_tag] Неверный direction: {direction}")
            return

        if tag not in state.graph_elements:
            if DEBUG:
                print(f"[scale_graph_elements_by_tag] Тег {tag} не отслеживается в словаре.")
            return

        step_scale = 1.1 if direction == "+" else 0.9

        items = canvas.find_withtag(tag)
        if not items:
            if DEBUG:
                print(f"[scale_graph_elements_by_tag] Не найдено элементов с тегом: {tag}")
            return

        x_coords = []
        y_coords = []
        for item in items:
            coords = canvas.coords(item)
            if coords:
                x_coords.extend(coords[::2])
                y_coords.extend(coords[1::2])

        if not x_coords or not y_coords:
            return

        center_x = sum(x_coords) / len(x_coords)
        center_y = sum(y_coords) / len(y_coords)

        current_scale = state.graph_elements[tag].get("accumulated_scale", 1.0)
        new_scale = current_scale * step_scale
        
        for item in items:
            canvas.scale(item, center_x, center_y, step_scale, step_scale)

       
        for item in items:
            if item not in state.graph_elements[tag]["items"]:
                state.graph_elements[tag]["items"].append(item)

      
        state.graph_elements[tag]["accumulated_scale"] = new_scale

        
        state.graph_elements[tag]["scale_params"] = {
            "center_x": center_x,
            "center_y": center_y,
            "scale_x": step_scale,
            "scale_y": step_scale,
        }

        if DEBUG:
            print(f"[scale_graph_elements_by_tag] Тег {tag} масштабирован. Накопленный масштаб: {new_scale}")
    else:
        
        for tag, data in state.graph_elements.items():
            items = data["items"]
            scale_params = data["scale_params"]
            accumulated_scale = data["accumulated_scale"]

            if not items or not scale_params:
                continue

            center_x = scale_params["center_x"]
            center_y = scale_params["center_y"]
            scale_factor = accumulated_scale

            for item in items:
                canvas.scale(item, center_x, center_y, scale_factor, scale_factor)

            if DEBUG:
                print(f"[apply_scaling_to_all_elements] Масштабирование для тега '{scale_factor}' применено.")


def change_accessiable_panel_width(tag, width_size):
    try:
        
        
        item_ids = state.bg_canvas.find_withtag(tag)
        for item_id in item_ids:
            element_type = state.bg_canvas.type(item_id)
            if element_type == "line":
                state.bg_canvas.itemconfig(item_id, width=width_size)
            elif element_type == "arc":
                state.bg_canvas.itemconfig(item_id, width=width_size)        #setattr(state,f'fill_{tag}',None)
        print(f'[INFO] Applying color to the text of element {tag}')
    except Exception as e:
        if DEBUG:
            print(f'[WARING] Applying color to the text of element {tag} resulted in an error: {e}')
        else:
            pass        

def scale_accessible_panel(tag, direction):
    canvas = state.bg_canvas
    if direction not in ["+", "-"]:
        return
    
    item_ids = canvas.find_withtag(tag)
    if not item_ids:
        return

    bbox = canvas.bbox(tag)
    if bbox is None:
        return

    x1, y1, x2, y2 = bbox
    center_x = (x1 + x2) / 2
    center_y = (y1 + y2) / 2

    step = 0.1
    scale = 1 + step if direction == "+" else 1 - step

    canvas.scale(tag, center_x, center_y, scale, scale)

    for item_id in item_ids:
        if canvas.type(item_id) == "text":
            current_font = canvas.itemcget(item_id, "font")
            font_parts = current_font.split()
            if len(font_parts) >= 2 and font_parts[1].isdigit():
                font_size = int(font_parts[1])
                new_size = max(1, int(font_size * scale)) 
                font_parts[1] = str(new_size)
                canvas.itemconfig(item_id, font=" ".join(font_parts))
