import copy
import tkinter as tk
import json
import json
import os
import shutil
import time
from tkinter import filedialog
from PIL import ImageTk, Image
import os
from vacantview.core.state import state
from vacantview.config.config import DEBUG
from vacantview.ui.context_menu.functions.title_editor import scale_graph_elements_by_tag
from vacantview.ui.context_menu.functions.branding_images import upload_logo_image_start,upload_background_image
from vacantview.ui.context_menu.functions.modes import men_mode,women_mode,both_mode,custom_mode
from vacantview.config.config import IMG_DIR, BOTH_CNF, BOTH_A_CNF, MAN_CNF, WOMAN_CNF, CUSTOM_CNF, MAN_A_CNF, WOMAN_A_CNF, set_key, env_path
from vacantview.ui.image_loader import resource_path

from tkinter import filedialog, messagebox
from vacantview.ui.context_menu.rtl_func import prepare_text_for_widget


image_cache = {}


def update_canvas_texts(canvas):
    
    tags_to_update = [
        'h1', 'h2_v', 'h2_o', 'h2_v2', 'h2_o2', 'h2_v_add', 'h2_o_add',
        'h2_v2_add', 'h2_o2_add', 'TOTAL_1', 'TOTAL_2', 'TOTAL_3', 'TOTAL_4',
        'cleaning_message_1', 'cleaning_message_2', 'custom_title_text',
        'cleaning_message_1_add', 'cleaning_message_2_add', 'h2_v2_add'
    ]

   
    for tag in tags_to_update:
        items = canvas.find_withtag(tag)
        for item in items:
            
            if canvas.type(item) == "text":
                
                current_text = canvas.itemcget(item, 'text')
                #print(f"Checking tag: {tag} - Current text: {current_text}")

               
                if current_text == "TOTAL":
                    new_text = prepare_text_for_widget(_("TOTAL"))
                elif current_text == "VACANT":
                    new_text = prepare_text_for_widget(_("VACANT"))
                elif current_text == "OCCUPIED":
                    new_text = prepare_text_for_widget(_("OCCUPIED"))
                elif current_text == "WC IS BEING CLEANED, PLEASE USE WC IN FLOOR #1":
                    new_text = prepare_text_for_widget(_("WC IS BEING CLEANED, PLEASE USE WC IN FLOOR #1"))
                elif current_text == "WC IS BEING CLEANED, PLEASE USE WC IN FLOOR #2":
                    new_text = prepare_text_for_widget(_("WC IS BEING CLEANED, PLEASE USE WC IN FLOOR #2"))
                elif current_text == "WC IS BEING CLEANED, PLEASE USE WC IN FLOOR #1 ADD":
                    new_text = prepare_text_for_widget(_("WC IS BEING CLEANED, PLEASE USE WC IN FLOOR #1 ADD"))
                elif current_text == "WC IS BEING CLEANED, PLEASE USE WC IN FLOOR #2 ADD":
                    new_text = prepare_text_for_widget(_("WC IS BEING CLEANED, PLEASE USE WC IN FLOOR #2 ADD"))    
                elif current_text == "CUSTOM TEXT":
                    new_text = prepare_text_for_widget(_("CUSTOM TEXT"))
                elif current_text == "WASHROOM OCCUPANCY":
                    new_text = prepare_text_for_widget(_("WASHROOM OCCUPANCY"))
                elif current_text == "MEN":
                    new_text = prepare_text_for_widget(_("MEN"))
                elif current_text == "WOMEN":
                    new_text = prepare_text_for_widget(_("WOMEN"))
                else:
                    new_text = current_text

                canvas.itemconfig(item, text=new_text)
                #print(f"Updated text for tag {tag}: {new_text}")

def apply_mode_and_show(mode_function, hidden_tags, canvas, show_tag, delay_ms=500):
    
    canvas.update()
    for tag in hidden_tags:
        canvas.itemconfigure(tag, state='hidden')
        
    for t in show_tag:
        canvas.after(delay_ms, lambda tag=t: canvas.itemconfigure(tag, state='normal'))
   

def update_positions_and_colors_from_json(canvas_items, positions, colors, ring_color_table, canvas_width, canvas_height, gender_key):
    updated_tags = set()
    largest_by_tag = {}

    for item in canvas_items:
        if not isinstance(item, dict):
            continue

        options = item.get("options", {})
        coords = item.get("coords", [])
        tags = options.get("tags", "").split()

        for tag in tags:
            if tag in positions and len(coords) == 4 and options.get("type") != "arc":
                x1, y1, x2, y2 = coords
                area = abs((x2 - x1) * (y2 - y1))
                if tag not in largest_by_tag or area > largest_by_tag[tag][0]:
                    largest_by_tag[tag] = (area, (x1, y1, x2, y2))

    
    for tag, (area, (x1, y1, x2, y2)) in largest_by_tag.items():
        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2
        norm_x = cx / canvas_width
        norm_y = cy / canvas_height

        if gender_key in positions[tag]:
            positions[tag][gender_key] = (norm_x, norm_y)

    
    for item in canvas_items:
        options = item.get("options", {})
        tags = options.get("tags", "").split()
        tag = next((t for t in tags if t in positions), None)
        if not tag or tag in updated_tags:
            continue

        outline = options.get("outline", "").strip()
        fill = options.get("fill", "").strip()

        if outline and fill:
            if "GREEN" in tag:
                colors["GREEN"] = (outline, fill)
            elif "RED" in tag:
                colors["RED"] = (outline, fill)

            ring_color_table[tag] = {
                "outline": outline,
                "fill": fill
            }

            updated_tags.add(tag)
            
def config_screen_load():
    if not state.fullscreen_mode:
        set_key(env_path, "FULLSCREEN_ON_LOAD", "0")
    else:
        set_key(env_path, "FULLSCREEN_ON_LOAD", "1")
        
def set_force_load(force_current_mode = 'Current'):
    set_key(env_path, "NAME_MODE", force_current_mode)
      
            
def export_state_to_json(filename=os.path.join('vacantview','config',"state_data.json")):
    
    canvas_data = {
        "fullscreen_mode": state.fullscreen_mode,
        "outring_fill": state.outring_fill,
        "outer3_fill": state.outer3_fill,
        "text_color": state.text_color,
        "new_font": state.new_font,
        "int_cansize": state.int_cansize,
        "graph_elements": state.graph_elements,
        "logo_positions": state.logo_positions,
        "logo_file_path": state.logo_file_path,
        "logo_scale" : state.logo_scale,
        "bg_set_img": state.bg_set_img,
        "background_filepath": state.background_filepath,
        "current_mode": state.current_mode,
        "hidden_tags": state.hidden_tags,
        "filtered_tags": state.filtered_tags,
        
    }

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(canvas_data, f, indent=2)

    #print(f"State variables exported to {filename}")
    
def r_to_default():
    
    
    if state.current_mode == 'men':
        filename = MAN_CNF
        filename_orig = MAN_CNF.replace("man.json","default/man.json")
    elif state.current_mode == 'women':
        filename = WOMAN_CNF
        filename_orig = WOMAN_CNF.replace("woman.json","default/woman.json")
    elif state.current_mode == 'both':
        filename = BOTH_CNF
        filename_orig = BOTH_CNF.replace("family.json","default/family.json")
    elif state.current_mode == 'men_accessible':
        filename = MAN_A_CNF
        filename_orig = MAN_A_CNF.replace("man_with_accessible.json","default/man_with_accessible.json")
    elif state.current_mode == 'women_accessible':
        filename = WOMAN_A_CNF
        filename_orig = WOMAN_A_CNF.replace("woman_with_accessible.json","default/woman_with_accessible.json")
    elif state.current_mode == 'both_accessible':
        filename = BOTH_A_CNF
        filename_orig = BOTH_A_CNF.replace("family_with_accessible.json","default/family_with_accessible.json")
    elif state.current_mode == 'custom':
        filename = CUSTOM_CNF
        filename_orig = CUSTOM_CNF.replace("custom.json","default/custom.json")
    #print(filename_orig)    
    shutil.copy(filename_orig,filename)

def export_canvas_to_json(canvas, save=False, set_current_mode = None, refresh = False):
    try:
        if not save:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json")],
                title="Save file as"
            )
        else:
            if state.current_mode == 'men':
                filename = MAN_CNF #resource_path()
            elif state.current_mode == 'women':
                filename = WOMAN_CNF
            elif state.current_mode == 'both':
                filename = BOTH_CNF
            elif state.current_mode == 'men_accessible':
                filename = MAN_A_CNF
            elif state.current_mode == 'women_accessible':
                filename = WOMAN_A_CNF
            elif state.current_mode == 'both_accessible':
                filename = BOTH_A_CNF
            elif state.current_mode == 'custom':
                filename = CUSTOM_CNF
        
        if not filename:
            #print("The save is canceled by the user.")
            return

        
        canvas.update_idletasks()  
        width = canvas.winfo_width()
        height = canvas.winfo_height()

        items = canvas.find_all()
        data = []
        logo_positions = {'x': 0, 'y': 0}

        for item in items:
            item_type = canvas.type(item)
            coords = canvas.coords(item)
            options = {}

            config = canvas.itemconfig(item)
            for key, val in config.items():
                options[key] = val[-1]

            tags = canvas.gettags(item)
            
            if "logo" in tags:
                if len(coords) >= 2:
                    state.logo_positions['x'] = coords[0]
                    state.logo_positions['y'] = coords[1]

            if item_type == "image":
                options["file"] = tags[0] if tags else ""
                if len(tags) > 1:
                    options["tag"] = tags[1]
                if len(tags) > 2:
                    options["marker"] = tags[2]

            data.append({
                "type": item_type,
                "coords": coords,
                "options": options
            })
            
        state_mode = state.current_mode
        
        if set_current_mode:
            state_mode = set_current_mode
            
        if refresh:
            current_resolution = state.res_refresh
        else:    
            current_resolution = [width, height]
        canvas_data = {
            "resolution": current_resolution,     
            "canvas_items": data,
            "indicator_type": state.indicator_type,
            "outring_fill": state.outring_fill,
            "outer3_fill": state.outer3_fill,
            "text_color": state.text_color,
            "new_font": state.new_font,
            "int_cansize": state.int_cansize,
            "graph_elements": state.graph_elements,
            "logo_positions": state.logo_positions,
            "logo_file_path": state.logo_file_path,
            "logo_scale" : state.logo_scale,
            "bg_set_img": state.bg_set_img,
            "background_filepath": state.background_filepath,
            "current_mode": state_mode,
            "hidden_tags": state.hidden_tags,
            "filtered_tags": state.filtered_tags,
            "fullscreen_mode": state.fullscreen_mode,
            "s_element_dict": state.s_element_dict,
            "ring_color_table" : copy.deepcopy(state.ring_color_table),
            "ring_color_add_table" : copy.deepcopy(state.ring_color_add_table),
            "custom_title" : state.custom_title,
            "a_progress_on" : state.a_progress_on,
            "c_block" : state.c_block,
            "positions" : state.positions,
            "logo_rel_pos" : state.logo_rel_pos,
            "bg_color" : state.bg_color
            
        }

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(canvas_data, f, indent=2, ensure_ascii=False)

        #print(f"Canvas successfully exported to a file: {filename}")
        if not save:
            messagebox.showinfo("Export completed", f"The data has been successfully saved to a file:\n{filename}")

    except Exception as e:
        if DEBUG:
            print(f"[export_canvas_to_json error]: {e}")
        messagebox.showerror("Error export.", f"Save error:\n{e}")


def import_canvas_from_json(canvas, set_current_mode = None, resize_signal = False):
    
 

    if set_current_mode:
        if set_current_mode == 'men':
            filename = MAN_CNF
        elif set_current_mode == 'women':
            filename = WOMAN_CNF
        elif set_current_mode == 'both':
            filename = BOTH_CNF
        elif set_current_mode == 'men_accessible':
            filename = MAN_A_CNF
        elif set_current_mode == 'women_accessible':
            filename = WOMAN_A_CNF
        elif set_current_mode == 'both_accessible':
            filename = BOTH_A_CNF
        elif set_current_mode == 'custom':
            filename = CUSTOM_CNF
    else:    
       
        filename = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("JSON files.", "*.json")],
            title="Select the file to import"
        )
    
    if not filename:
        #print("Import canceled by user.")
        return
    
    if not os.path.exists(filename):
        if DEBUG:
            print(f"File not found: {filename}")
        return

    with open(filename, "r", encoding="utf-8") as f:
        canvas_data = json.load(f)
    canvas_items = canvas_data.get("canvas_items", [])
    
    fullscreen_mode = canvas_data.get("fullscreen_mode")
    if isinstance(fullscreen_mode, bool):
        state.fullscreen_mode = fullscreen_mode
        
    
    a_progress_on = canvas_data.get("a_progress_on")
    if isinstance(a_progress_on, bool):
        state.a_progress_on = a_progress_on
    #print(state.fullscreen_mode,state.fullscreen_signal)
   
    if resize_signal:
        if state.fullscreen_mode and state.fullscreen_signal:
            state.win.attributes('-fullscreen', True)
            state.fullscreen_mode = True
        elif state.fullscreen_mode and not state.fullscreen_signal:
            state.win.attributes('-fullscreen', False)
            state.fullscreen_mode = False
        elif not state.fullscreen_mode and state.fullscreen_signal:
            state.win.attributes('-fullscreen', True)
            state.fullscreen_mode = True
        else:
            state.win.attributes('-fullscreen', False)
            state.fullscreen_mode = False
    else:
        
        if state.fullscreen_mode:
            state.win.attributes('-fullscreen', True)
            state.fullscreen_mode = True
        else:
            state.win.attributes('-fullscreen', False)
            state.fullscreen_mode = False
    
    logo_scale = canvas_data.get("logo_scale")
    if isinstance(logo_scale, float):
        state.logo_scale = logo_scale
        
    custom_title = canvas_data.get("custom_title")
    if isinstance(custom_title, bool):
        state.custom_title = custom_title  
  
    outring_fill_data = canvas_data.get("outring_fill")
    if isinstance(outring_fill_data, dict):
        state.outring_fill.update(outring_fill_data)
        
    logo_rel_pos = canvas_data.get("logo_rel_pos")
    if isinstance(logo_rel_pos, dict):
        state.logo_rel_pos.update(logo_rel_pos)

    outer3_fill_data = canvas_data.get("outer3_fill")
    if isinstance(outer3_fill_data, dict):
        state.outer3_fill.update(outer3_fill_data)
        
    positions = canvas_data.get("positions")
    if isinstance("positions", dict):
        state.positions.update(positions)    
        
    s_element_dict = canvas_data.get("s_element_dict")
    if isinstance(s_element_dict, dict):
        state.s_element_dict.update(s_element_dict)
        
    text_color = canvas_data.get("text_color")
    if isinstance(text_color, dict):
        state.text_color.update(text_color)
    
    new_font = canvas_data.get("new_font")
    if isinstance(new_font, list):
        state.new_font = new_font
    
    int_cansize = canvas_data.get("int_cansize")
    if isinstance(int_cansize, int):
        state.int_cansize = int_cansize
        
    graph_elements = canvas_data.get("graph_elements")
    if isinstance(graph_elements, dict):
        state.graph_elements = graph_elements
       
        
    logo_positions = canvas_data.get("logo_positions")
    if isinstance(logo_positions, dict):
        state.logo_positions = logo_positions
        
    logo_file_path = canvas_data.get("logo_file_path")     
    if isinstance(logo_file_path, str):
        state.logo_file_path = logo_file_path
    
    bg_color = canvas_data.get("bg_color")     
    if isinstance(bg_color, str):
        state.bg_color = bg_color
        
    bg_set_img = canvas_data.get("bg_set_img")
    if isinstance(bg_set_img, bool):
        state.bg_set_img = bg_set_img
        
    current_mode = canvas_data.get("current_mode")
    if isinstance(current_mode, str):
        state.current_mode = current_mode
        
    background_filepath = canvas_data.get("background_filepath")
    if isinstance(background_filepath, str):
        state.background_filepath = background_filepath    
    
    hidden_tags = canvas_data.get("hidden_tags")
    if isinstance(hidden_tags, list):
        state.hidden_tags = hidden_tags 
    
    filtered_tags = canvas_data.get("filtered_tags")
    if isinstance(filtered_tags, list):
        state.filtered_tags = filtered_tags
        
    ring_color_table = canvas_data.get("ring_color_table")
    if isinstance(ring_color_table, dict):
        state.ring_color_table.update(ring_color_table)
        
    ring_color_add_table = canvas_data.get("ring_color_add_table")
    if isinstance(ring_color_add_table, dict):
        state.ring_color_add_table.update(ring_color_add_table)
        
    c_block = canvas_data.get("c_block")
    if isinstance(c_block, bool):
        state.c_block = c_block    
    
    canvas.update()
    
    update_positions_and_colors_from_json(
        canvas_items=canvas_items,
        positions=state.positions,
        colors=state.colors,
        ring_color_table=state.ring_color_table,
        canvas_width=canvas.winfo_width(),
        canvas_height=canvas.winfo_height(),
        gender_key=state.string_genderSelect.get()
    )
        
    indicator_type = canvas_data.get("indicator_type", None)
    if indicator_type is not None:
        setattr(state,'flag_start_mode', True)
        state.indicator_type = indicator_type
        setattr(state, 'refresh_ui_flag', True)
        #print(f"Imported indicator_type = {indicator_type}, updated UI")
        
    def get_original_resolution(canvas_items):
       
        for item in canvas_items:
            if isinstance(item, dict) and "resolution" in item:
                res = item["resolution"]
                if isinstance(res, (list, tuple)) and len(res) == 2:
                    width, height = res
                    
                    return width, height

    
        for item in canvas_items:
            if item.get("type") == "rectangle":
                coords = item.get("coords", [])
                if coords and coords[0:2] == [0.0, 0.0] and len(coords) == 4:
                    width = coords[2] - coords[0]
                    height = coords[3] - coords[1]
                    
                    return width, height

        return 1920,1080
    
    def get_original_resolution_from_data(data):
        if "resolution" in data:
            return tuple(data["resolution"])
        return get_original_resolution(data.get("canvas_items", []))
    

    ORIGINAL_WIDTH, ORIGINAL_HEIGHT  = get_original_resolution_from_data(canvas_data)
    

    
    state.bg_canvas_prev_size = (ORIGINAL_WIDTH, ORIGINAL_HEIGHT)
    
    def wait_for_canvas_ready():
        canvas.update_idletasks()
        width = canvas.winfo_width()
        height = canvas.winfo_height()

        if width <= 1 or height <= 1:

            canvas.after(100, wait_for_canvas_ready)
            
       
        else:
            pass
        
    
        
    wait_for_canvas_ready()
    canvas.update_idletasks()
    current_width = canvas.winfo_width()
    current_height = canvas.winfo_height()
    state.current_res_size = (current_width,current_height)
    #print(ORIGINAL_WIDTH, ORIGINAL_HEIGHT)
    #print(current_width,current_height)
    
    state.res_refresh = (current_width, current_height)
    def scale_coords(coords, scale, offset_x=0, offset_y=0):
        return [
            coord * scale + offset_x if i % 2 == 0 else coord * scale + offset_y
            for i, coord in enumerate(coords)
        ]

    
    data = canvas_data.get("canvas_items", [])
    canvas.delete("all")
    
    scale_x = current_width / ORIGINAL_WIDTH
    scale_y = current_height / ORIGINAL_HEIGHT

    if current_width < ORIGINAL_WIDTH or current_height < ORIGINAL_HEIGHT:
        scale = min(scale_x, scale_y)
    else:
        scale = max(scale_x, scale_y)
    if ORIGINAL_WIDTH <  ORIGINAL_HEIGHT:    
        scale = max(scale_x, scale_y)    
   
    scaled_canvas_width = ORIGINAL_WIDTH * scale
    scaled_canvas_height = ORIGINAL_HEIGHT * scale

    offset_x = (current_width - scaled_canvas_width) / 2
    offset_y = (current_height - scaled_canvas_height) / 2

    image_cache.clear()

    for item in data:
        item_type = item.get("type")
        coords = item.get("coords", [])
        options = item.get("options", {}).copy()

        if item_type == "image":
            img_path = options.get("file", "")
            tag = options.get("tag", "")
            marker = options.get("marker", "")

            if not os.path.exists(img_path):
                #print(f"Img not found: {img_path}")
                #if img_path == 'background':
                    
                tag = getattr(state, "bg_fill_tag", "background")
                
    
                existing = state.bg_canvas.find_withtag(tag)
                if existing:
                    current_width = canvas.winfo_width()
                    current_height = canvas.winfo_height()
                    rect_id = existing[0]
                    state.bg_canvas.coords(rect_id, 0, 0, current_width, current_height)
                    state.bg_canvas.itemconfig(rect_id, fill=state.bg_color, outline=state.bg_color)
                     
                else:
                    
                    current_width = canvas.winfo_width()
                    current_height = canvas.winfo_height()
                    rect_id = state.bg_canvas.create_rectangle(
                        0, 0, current_width, current_height,
                        fill=state.bg_color, outline=state.bg_color, tags=(tag,)
                    )
                    state.bg_canvas.tag_lower(rect_id)
                
                continue

            try:
                img = Image.open(img_path)

                if marker in ("accessible_icon_image_men", "accessible_icon_image_women"):
                    icon_items = canvas.find_withtag('accessible_icon')
                    icon_box_coords = None

                    for item_id in icon_items:
                        tags = canvas.gettags(item_id)
                        if tag in tags:
                            icon_box_coords = canvas.coords(item_id)
                            break

                    if icon_box_coords and len(icon_box_coords) == 4:
                        icon_left, icon_top, icon_right, icon_bottom = icon_box_coords
                        icon_width = icon_right - icon_left
                        icon_height = icon_bottom - icon_top

                        scale_icon = 1.1
                        new_w = int(icon_width * scale_icon)
                        new_h = int(icon_height * scale_icon)


                        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

                        center_x = (icon_left + icon_right) / 2
                        center_y = (icon_top + icon_bottom) / 2

                        scaled_coords = scale_coords([center_x, center_y], scale, offset_x, offset_y)

                    else:
                        
                        continue
                
                scaled_coords = scale_coords(coords, scale, offset_x, offset_y)

                img_tk = ImageTk.PhotoImage(img)
                image_cache[(img_path, tag)] = img_tk

                canvas.create_image(
                    *scaled_coords,
                    image=img_tk,
                    tags=(img_path, tag, marker) if marker else (img_path, tag)
                )

            except Exception as e:
                
                print(f"Error '{img_path}': {e}")
                   

        elif item_type in ("rectangle", "oval", "line", "polygon", "arc", "text"):
            scaled_coords = scale_coords(coords, scale, offset_x, offset_y)

            if "width" in options:
                try:
                    w = float(options["width"])
                    options["width"] = w * scale
                except:
                    pass

            if "font" in options:
                try:
                    font_parts = options["font"].split()
                    if len(font_parts) >= 2 and font_parts[1].isdigit():
                        size = int(font_parts[1])
                        new_size = int(size * scale)
                        font_parts[1] = str(new_size)
                        options["font"] = " ".join(font_parts)
                except:
                    pass

            try:
                create_func = getattr(canvas, f"create_{item_type}")
                create_func(*scaled_coords, **options)
            except Exception as e:
                print(f"Error drawing {item_type}: {e}")
        else:
            print(f"Not supported: {item_type}")
      
    upload_logo_image_start(True)
    
    if state.current_mode == 'custom':
      
        if bg_set_img:        
            upload_background_image(mode=state.background_filepath)
                 
    elif state.current_mode == 'men':
        state.filtered_tags.append('cleaning_message_2')
        state.filtered_tags.append('cleaning_message_2_add')
        state.bg_canvas.after(1000, lambda: apply_mode_and_show(
            mode_function=men_mode,
            hidden_tags=state.filtered_tags,
            canvas=state.bg_canvas,
            show_tag=('Cubiculs_MEN',),
            delay_ms=500))
        if bg_set_img:        
            upload_background_image(mode=state.background_filepath)
        
    elif state.current_mode == 'women':
        state.filtered_tags.append('cleaning_message_2')
        state.filtered_tags.append('cleaning_message_2_add')
        state.bg_canvas.after(1000, lambda: apply_mode_and_show(
            mode_function=women_mode,
            hidden_tags=state.filtered_tags,
            canvas=state.bg_canvas,
            show_tag=('Cubiculs_WOMEN',),
            delay_ms=500))
        if bg_set_img:        
            upload_background_image(mode=state.background_filepath)
    elif state.current_mode == 'both':
        state.bg_canvas.after(1000, lambda: apply_mode_and_show(
            mode_function=both_mode,
            hidden_tags=state.filtered_tags,
            canvas=state.bg_canvas,
            show_tag=('Cubiculs_WOMEN','Cubiculs_MEN',),
            delay_ms=500))
        if bg_set_img:        
            upload_background_image(mode=state.background_filepath)
    elif state.current_mode == 'men_accessible':
        state.filtered_tags.append('cleaning_message_2')
        state.filtered_tags.append('cleaning_message_2_add')
        state.bg_canvas.after(1000, lambda: apply_mode_and_show(
            mode_function=men_mode,
            hidden_tags=state.filtered_tags,
            canvas=state.bg_canvas,
            show_tag=('Cubiculs_MEN','accessible_panel_men',
                      'accessible_vacant_indicator_men',
                      'accessible_occup_indicator_men',),
            delay_ms=500))
        state.bg_canvas.update()
        if bg_set_img:        
            upload_background_image(mode=state.background_filepath)
    elif state.current_mode == 'women_accessible':
        state.filtered_tags.append('cleaning_message_2')
        state.filtered_tags.append('cleaning_message_2_add')
        state.bg_canvas.after(1000, lambda: apply_mode_and_show(
            mode_function=women_mode,
            hidden_tags=state.filtered_tags,
            canvas=state.bg_canvas,
            show_tag=('Cubiculs_WOMEN','accessible_panel_women',
                      'accessible_vacant_indicator_women',
                      'accessible_occup_indicator_women',),
            delay_ms=500))
        if bg_set_img:        
            upload_background_image(mode=state.background_filepath)
    elif state.current_mode == 'both_accessible':
        state.bg_canvas.after(1000, lambda: apply_mode_and_show(
            mode_function=both_mode,
            hidden_tags=state.filtered_tags,
            canvas=state.bg_canvas,
            show_tag=('Cubiculs_WOMEN','Cubiculs_MEN',
                      'accessible_panel_men','accessible_vacant_indicator_men',
                      'accessible_occup_indicator_men',
                      'accessible_panel_women','accessible_vacant_indicator_women',
                      'accessible_occup_indicator_women',),
            delay_ms=500))
        if bg_set_img:        
            upload_background_image(mode=state.background_filepath)
    
    for tag in state.s_element_dict[state.current_mode]:
        state.bg_canvas.itemconfigure(tag, state='normal')
        
    if state.c_block:
        block_communications()
    update_canvas_texts(state.bg_canvas)
    
    background_items = state.bg_canvas.find_withtag("background")
    if background_items:
        background_id = background_items[0]
        
        state.bg_canvas.tag_raise(state.logo_image_id, background_id)
    else:
       
        state.bg_canvas.tag_raise(state.logo_image_id)


