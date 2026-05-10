from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
from queue import Queue

from vacantview.ui.context_menu.functions.title_editor import scale_graph_elements_by_tag
from vacantview.ui.image_loader import load_background_image
from vacantview.ui.context_menu.functions.branding_images import upload_logo_image_start
from vacantview.ui.gui_elements import CE, AdminElements
from vacantview.core.state import state, g_auth
from vacantview.platform import gpio_control
from vacantview.platform import sensor_read
from vacantview.platform.device_manager import check_accessible_cubicles

from vacantview.ui.context_menu.functions.design_import_export import import_canvas_from_json, update_canvas_texts

from vacantview.ui.scaling import UIScaler

from vacantview.admin.admin_auth import show_auth_window
from vacantview.ui.context_menu.context_menu import show_context_menu
from vacantview.admin.utils.user_editor import open_admin_settings
from vacantview.admin.pin_entry import open_pin_window

from vacantview.config.config import FULLSCREEN_ON_LOAD, WIDTH, HEIGH, NAME_MODE

from vacantview.tests.test_ports import available_ports
from vacantview.ui.context_menu.rtl_func import prepare_text_for_widget

import RPi.GPIO as GPIO
import tkinter as tk
import tkinter.font
import threading
import time
import gettext
import os


localedir = 'vacantview/locale'

lang = gettext.translation('messages', localedir=localedir, languages=[state.current_lang], fallback=True)
lang.install()


from vacantview.tests.test_ports import available_ports
update_queue = Queue()

create_elements = CE()
admin_elements = AdminElements()

DEBUG = state.DEBUG
win = state.win

def monitor_user_select():
    while not state.flag_monitor_thread:
        
        previous_value = g_auth.current_user
        while True:
            current_value = g_auth.current_user
            if current_value != previous_value:
                previous_value = current_value
                if g_auth.current_user in ['Master', 'User']:
                    if DEBUG:
                        print(f"Current user: {current_value}")
                    update_queue.put('show_button')
                else:
                    if DEBUG:
                        print(f"Current user: {current_value}")
                    update_queue.put('hide_button')
            time.sleep(1)

def update_button_visibility():
    try:
        while not update_queue.empty(): 
            action = update_queue.get_nowait()  
            if action == 'show_button':
                state.admin_button.place(relx=0.95, rely=0.05, anchor=NE)
                if g_auth.current_user in ('Master', 'User'):
                    state.bg_canvas.itemconfigure('cleaning_message_1', state='normal')
                    if state.current_mode in ('both','both_accessible','custom'):
                        state.bg_canvas.itemconfigure('cleaning_message_2', state='normal')
                    if state.custom_title:
                        
                        state.bg_canvas.itemconfigure('cleaning_message_1_add', state='normal')
                        if state.current_mode in ('both','both_accessible','custom'):
                            state.bg_canvas.itemconfigure('cleaning_message_2_add', state='normal')
                        
                    state.config_cleaning_mode = True
            elif action == 'hide_button':
                state.admin_button.place_forget() 
    except Exception as e:
        print(f"Error processing update: {e}")
    state.after_id = win.after(100, update_button_visibility)
        
def snap_to_grid(x, y):
        snapped_x = state.GRID_SIZE * round(x / state.GRID_SIZE)
        snapped_y = state.GRID_SIZE * round(y / state.GRID_SIZE)
        return snapped_x, snapped_y
    
    
def on_ring_press(event):
     
        if event.num != 1:
            return

        item = state.bg_canvas.find_closest(event.x, event.y)
        if item:
            tags = state.bg_canvas.gettags(item)
            if 'background' in tags:
                return
            elif 'accessible_icon_image_men' in tags or 'accessible_icon_image_women' in tags:
                return
                 
            if tags:
                if 'accessible_vacant' in tags or 'accessible_occup' in tags:
                    state.drag_data_rings["item_tag"] = tags[1]
                else:    
                    state.drag_data_rings["item_tag"] = tags[0]
                    
                state.drag_data_rings["start_x"] = event.x
                state.drag_data_rings["start_y"] = event.y

                label_text = None
                if tags[0] in ('graph_M_GREEN', 'graph_M_RED'):
                    label_text = prepare_text_for_widget(_("MEN INDICATOR"))
                elif tags[0] in ('graph_w_GREEN', 'graph_w_RED'):
                    label_text = prepare_text_for_widget(_("WOMEN INDICATOR"))
                elif tags[0] == 'Cubiculs_MEN':
                    label_text = prepare_text_for_widget(_("MEN TOTAL"))
                elif tags[0] == 'Cubiculs_WOMEN':
                    label_text = prepare_text_for_widget(_("WOMEN TOTAL"))
                elif 'accessible_panel_men' in (tags[0],):
                    label_text = prepare_text_for_widget(_("Accessible_Panel_Men"))
                elif 'accessible_panel_women' in (tags[0],):
                    label_text = prepare_text_for_widget(_("Accessible Panel Women"))
                elif 'accessible_vacant_indicator_men' in (tags[0],):
                    label_text = prepare_text_for_widget(_("Accessible Vacant Indicator Men"))
                elif 'accessible_vacant_indicator_women' in (tags[0],):
                    label_text = prepare_text_for_widget(_("Accessible Vacant Indicator Women"))
                elif 'accessible_occup_indicator_men' in (tags[0],):
                    label_text = prepare_text_for_widget(_("Accessible Occup Indicator Men"))
                elif 'accessible_occup_indicator_women' in (tags[0],):
                    label_text = prepare_text_for_widget(_("Accessible Occup Indicator Women"))
                    

                if label_text:
                    state.drag_data_rings["floating_label_id"] = state.bg_canvas.create_text(
                        event.x, event.y + 50, text=label_text, fill="yellow", font="Arial 12", tags="floating_label")

def on_ring_motion(event):
    canvas = state.bg_canvas
    tag = state.drag_data_rings["item_tag"]
    
    if tag and tag != 'background':
        
        snapped_x, snapped_y = snap_to_grid(event.x, event.y)

        dx = snapped_x - state.drag_data_rings["start_x"]
        dy = snapped_y - state.drag_data_rings["start_y"]

        canvas.move(tag, dx, dy)
        state.drag_data_rings["start_x"] = snapped_x
        state.drag_data_rings["start_y"] = snapped_y

        floating_id = state.drag_data_rings.get("floating_label_id")
        if floating_id:
            canvas.coords(floating_id, snapped_x, snapped_y - 20)    
            
def on_ring_release(event):
    canvas = state.bg_canvas
    tag = state.drag_data_rings["item_tag"]

    if tag:
        snapped_x, snapped_y = snap_to_grid(event.x, event.y)
        
        dx = snapped_x - state.drag_data_rings["start_x"]
        dy = snapped_y - state.drag_data_rings["start_y"]
        
        canvas.move(tag, dx, dy)

        if tag == 'logo':
            canvas_width = canvas.winfo_width()
            canvas_height = canvas.winfo_height()
            coords = canvas.coords(state.logo_image_id)
            if coords:
                abs_x, abs_y = coords[0], coords[1]
                rel_x = abs_x / canvas_width
                rel_y = abs_y / canvas_height
                state.logo_rel_pos = {'x': rel_x, 'y': rel_y}
                state.logo_positions = {'x': abs_x, 'y': abs_y} 

 
    floating_id = state.drag_data_rings.get("floating_label_id")
    if floating_id:
        canvas.delete(floating_id)
        state.drag_data_rings["floating_label_id"] = None

    state.drag_data_rings["item_tag"] = ''
        
        
def monitor_refresh_flag():
    if state.refresh_ui_flag:
        if state.flag_start_mode:
            recreate_graph_elements(True)
            setattr(state,'flag_start_mode', False)
        else:
            recreate_graph_elements()
            
        state.refresh_ui_flag = False 

    win.after(500, monitor_refresh_flag) 
        
def recreate_graph_elements(first: bool = False):
    gender = state.string_genderSelect.get()

    graph_ids = ["graph_w_GREEN", "graph_w_RED", "graph_M_GREEN", "graph_M_RED"]

    def delete_graph_elements(graph_names):
        for graph_id in graph_names:
            graph = getattr(state, graph_id, None)
            if graph and hasattr(graph, 'canvas'):
                for attr in ['outring', 'outer1', 'outer2', 'outer3', 'text']:
                    item = getattr(graph, attr, None)
                    if item:
                        graph.canvas.delete(item)

    def forget(*widgets):
        for w in widgets:
            if w:
                w.place_forget()
                
    '''if not first:
        delete_graph_elements(graph_ids)'''
        
    delete_ids = set()
    create_ids = set()

    if gender == "BOTH":
        #forget(state.disp_Cubiculs_MEN_only, state.disp_Cubiculs_WOMEN_only)
        create_ids.update(graph_ids)
          

    elif gender == "MEN":
        #forget(state.disp_Cubiculs_MEN, state.disp_Cubiculs_WOMEN, state.disp_Cubiculs_WOMEN_only)
        delete_ids.update(["graph_w_RED", "graph_w_GREEN"])
        create_ids.update(["graph_M_RED", "graph_M_GREEN"])

    elif gender == "WOMEN":
        #forget(state.disp_Cubiculs_MEN_only, state.disp_Cubiculs_MEN, state.disp_Cubiculs_WOMEN)
        delete_ids.update(["graph_M_RED", "graph_M_GREEN"])
        create_ids.update(["graph_w_RED", "graph_w_GREEN"])

    elif gender == "NONE": 
        forget(
            state.disp_Cubiculs_MEN_only,
            state.disp_Cubiculs_WOMEN_only,
            state.disp_Cubiculs_MEN,
            state.disp_Cubiculs_WOMEN
        )
        delete_ids.update(graph_ids)
        state.no_uart = True
        
    delete_graph_elements(delete_ids)

    def create_graph(name, color_key, state):
        pos = state.positions[name]
        color = state.colors[color_key]
        method_map = {
            'circle': create_elements.create_ring,
            'square': create_elements.create_rect,
            'rounded': create_elements.create_rounded
        }
        create_method = method_map.get(state.indicator_type)
        if not create_method:
            raise ValueError(f"Unknown indicator_type: {state.indicator_type}")
        return create_method(state.bg_canvas, color, pos, ring_id=name)
    
    if state.indicator_type in ['circle', 'square', 'rounded']:
            for gid in create_ids:
                color = "GREEN" if "GREEN" in gid else "RED"
                graph = create_graph(gid, color, state)
                setattr(state, gid, graph)
                    
def on_right_click_ring(event):
    item = state.bg_canvas.find_closest(event.x, event.y)

    if item:
        tags = state.bg_canvas.gettags(item)
        if tags:
            tag = tags[0]
            #print(f"{tag}")
            if tag == 'background':
                show_context_menu(event, target="background", identifier=tag)
            elif tag=="graph_M_GREEN":
                floating_id = state.drag_data_rings.get("floating_label_id")
                if floating_id:
                    canvas.delete(floating_id)
                    state.drag_data_rings["floating_label_id"] = None
                show_context_menu(event, target="ring", identifier=tag)
            elif tag=="graph_M_RED":
                floating_id = state.drag_data_rings.get("floating_label_id")
                if floating_id:
                    canvas.delete(floating_id)
                    state.drag_data_rings["floating_label_id"] = None
                show_context_menu(event, target="ring", identifier=tag)
            elif tag=="graph_w_GREEN":
                floating_id = state.drag_data_rings.get("floating_label_id")
                if floating_id:
                    canvas.delete(floating_id)
                    state.drag_data_rings["floating_label_id"] = None
                show_context_menu(event, target="ring", identifier=tag)
            elif tag=="graph_w_RED":
                floating_id = state.drag_data_rings.get("floating_label_id")
                if floating_id:
                    canvas.delete(floating_id)
                    state.drag_data_rings["floating_label_id"] = None
                show_context_menu(event, target="ring", identifier=tag)
            elif tag == 'h1':
                show_context_menu(event, target="text", identifier=tag)
            elif tag == 'h2_v' or tag == 'h2_v_add':
                 show_context_menu(event, target="text", identifier=tag)
            elif tag == 'h2_o' or tag == 'h2_o_add':
                 show_context_menu(event, target="text", identifier=tag)
            elif tag == 'h2_v2' or tag == 'h2_v2_add':
                 show_context_menu(event, target="text", identifier=tag)
            elif tag == 'h2_o2' or tag == 'h2_o2_add':
                 show_context_menu(event, target="text", identifier=tag)
            elif tag == 'v_line':
                 show_context_menu(event, target="line", identifier=tag)
            elif tag == 'cleaning_message_1' or tag == 'cleaning_message_2' or tag == 'cleaning_message_1_add' or tag == 'cleaning_message_2_add':
                 show_context_menu(event, target="cleaning_message", identifier=tag)
            elif tag == 'custom_title_text':
                 show_context_menu(event, target="text", identifier=tag)
            elif tag == 'Cubiculs_MEN':
                floating_id = state.drag_data_rings.get("floating_label_id")
                if floating_id:
                    canvas.delete(floating_id)
                    state.drag_data_rings["floating_label_id"] = None
                show_context_menu(event, target="indicator_men", identifier=tag)
            elif tag == 'Cubiculs_WOMEN':
                floating_id = state.drag_data_rings.get("floating_label_id")
                if floating_id:
                    canvas.delete(floating_id)
                    state.drag_data_rings["floating_label_id"] = None
                show_context_menu(event, target="indicator_women", identifier=tag)
            elif tag in ('TOTAL_1','TOTAL_2','TOTAL_3','TOTAL_4'):
                show_context_menu(event, target="text", identifier=tag)
            elif tag in ('total_circle_1','total_circle_2'):    
                show_context_menu(event, target="circle", identifier=tag)
            elif tag in ('figure_men','figure_women'):
                show_context_menu(event, target="figure", identifier=tag)
            elif tag == 'logo':
                show_context_menu(event, target="logo", identifier=tag)
            elif tag == 'accessible_occup_indicator' or tag == 'accessible_vacant_indicator':
                show_context_menu(event, target="text", identifier=tag)
            elif tag == 'accessible_vacant' or tag == 'accessible_occup':
                show_context_menu(event,target="accessible", identifier=tag)
            elif tag == 'accessible_panel_men':
                show_context_menu(event,target="accessible_panel_men", identifier=tag)
            elif tag == 'accessible_panel_women':
                show_context_menu(event,target="accessible_panel_women", identifier=tag)
            elif tag in ('accessible_vacant_indicator_men','accessible_vacant_indicator_women','accessible_occup_indicator_men','accessible_occup_indicator_women',):
                show_context_menu(event, target="text", identifier=tag)
            elif tag in (os.path.join(LOGO_DIR,LOGO_ACCESSIBLE),):
                show_context_menu(event, target="accessible_logo", identifier=tag)                    
                    
def disable_event():
        pass
    
def wait_for_canvas_ready(canvas, timeout=2.0, check_interval=0.05):

    start_time = time.time()
    while True:
        canvas.update()
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        if width > 1 and height > 1:
            return True
        if time.time() - start_time > timeout:
         
            time.sleep(check_interval) 
    
def start_app():
    
    win.title("WC")
    win.geometry(f"{WIDTH}x{HEIGH}")
    #win.attributes('-type', 'splash')#
    #win.overrideredirect(True)
    if int(FULLSCREEN_ON_LOAD) == 1:
        win.attributes('-fullscreen', True)
    else:
        win.attributes('-fullscreen', False)
    win.attributes("-topmost", True)

    if not available_ports(tk):
        state.BackGrounds[3]
        state.no_uart = True
    else:    
        sensor_read.get_data()
        gpio_control.init()
    
    state.myFont = tkinter.font.Font(family='Helvetica', size=32, weight='bold')
    state.myFontNumbers = tkinter.font.Font(family='Arial', size=65, weight='bold')
    
    state.bg_canvas = Canvas(win, bg='#00436e', highlightthickness=0)
    state.bg_canvas.pack(fill=BOTH, expand=YES)
    state.bg_fill_tag = 'background'

    new_width = state.bg_canvas.winfo_width()
    new_height = state.bg_canvas.winfo_height()
    

    if state.bg_set_img:
        state.copy_of_image = state.image.copy()
        photo = ImageTk.PhotoImage(state.image)
        state.bg_image_id = state.bg_canvas.create_image(0, 0, anchor=NW, image=photo, tags=('background',))
        state.bg_photo = photo
        state.bg_canvas.tag_lower(state.bg_image_id)
        
    else:
        if hasattr(state, "bg_image_id"):
            state.bg_canvas.delete(state.bg_image_id)
            del state.bg_image_id
            if hasattr(state, "bg_photo"):
                del state.bg_photo
            if hasattr(state, "copy_of_image"):
                del state.copy_of_image

        tag = state.bg_fill_tag
        state.bg_color = getattr(state, "bg_color", "#00436e")

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
    
    if state.string_genderSelect.get() == 'BOTH' and NAME_MODE == 'Current':
        if state.is_accessible[0] == 0 or state.is_accessible[1] == 0:
            setattr(state,'current_mode','both_accessible')
        else:    
            setattr(state,'current_mode','both')
        if not wait_for_canvas_ready(state.bg_canvas):
            print("Warning: Canvas not ready, proceeding anyway")    
            
        import_canvas_from_json(state.bg_canvas,state.current_mode)
        state.bg_canvas.itemconfigure('cleaning_message_1', state='hidden')
        state.bg_canvas.itemconfigure('cleaning_message_2', state='hidden')
        state.bg_canvas.itemconfigure('cleaning_message_1_add', state='hidden')
        state.bg_canvas.itemconfigure('cleaning_message_2_add', state='hidden')
       
    elif state.string_genderSelect.get() == 'MEN' and NAME_MODE == 'Current':
        if state.is_accessible[0] == 0:
            setattr(state,'current_mode','men_accessible')
        else:    
            setattr(state,'current_mode','men')
        if not wait_for_canvas_ready(state.bg_canvas):
            print("Warning: Canvas not ready, proceeding anyway")    
        import_canvas_from_json(state.bg_canvas,state.current_mode)
        state.bg_canvas.itemconfigure('cleaning_message_1', state='hidden')
        state.bg_canvas.itemconfigure('cleaning_message_2', state='hidden')
        state.bg_canvas.itemconfigure('cleaning_message_1_add', state='hidden')
        state.bg_canvas.itemconfigure('cleaning_message_2_add', state='hidden')
        
    elif state.string_genderSelect.get() == 'WOMEN' and NAME_MODE == 'Current':
        if state.is_accessible[1] == 0:
            setattr(state,'current_mode','women_accessible')
            
        else:    
            setattr(state,'current_mode','women')
        if not wait_for_canvas_ready(state.bg_canvas):
            print("Warning: Canvas not ready, proceeding anyway")        
        import_canvas_from_json(state.bg_canvas,state.current_mode)
        state.bg_canvas.itemconfigure('cleaning_message_1', state='hidden')
        state.bg_canvas.itemconfigure('cleaning_message_2', state='hidden')
        state.bg_canvas.itemconfigure('cleaning_message_1_add', state='hidden')
        state.bg_canvas.itemconfigure('cleaning_message_2_add', state='hidden')
    elif state.string_genderSelect.get() == 'NONE' and NAME_MODE == 'Current':
        for item_id in state.bg_canvas.find_all():
            tags = state.bg_canvas.gettags(item_id)
            state.no_uart = True
            #state.disp_ERROR.lift()
            if 'background' not in tags and 'logo' not in tags:
                state.bg_canvas.delete(item_id)
    elif NAME_MODE != 'Current':
        
        setattr(state,'current_mode',NAME_MODE)
        import_canvas_from_json(state.bg_canvas, getattr(state,'current_mode'))
        state.bg_canvas.itemconfigure('cleaning_message_1', state='hidden')
        state.bg_canvas.itemconfigure('cleaning_message_2', state='hidden')
        state.bg_canvas.itemconfigure('cleaning_message_1_add', state='hidden')
        state.bg_canvas.itemconfigure('cleaning_message_2_add', state='hidden')
    state.drag_data_rings["item_tag"] = None
   
    state.bg_canvas.itemconfigure('cleaning_message_1', state='hidden')
    state.bg_canvas.itemconfigure('cleaning_message_2', state='hidden')
 
    '''if not state.no_uart:
        state.sensor_thread = threading.Thread(target=sensor_read.read_all_data)
        state.monitor_thread = threading.Thread(target=monitor_user_select)
        state.monitor_thread.start()
        state.sensor_thread.start()'''
    state.sensor_thread = threading.Thread(target=sensor_read.read_all_data)
    state.monitor_thread = threading.Thread(target=monitor_user_select)
    state.monitor_thread.start()
    state.sensor_thread.start()

    gpio_control.setup_gpio_interrupt() 
    
    win.lift()
    win.focus_force()
    
    win.bind('<F5>', lambda event: show_auth_window(win))
    win.bind("<Button-1>", lambda event: win.focus_force())
    win.bind("<Escape>", lambda event: open_pin_window(win) if g_auth.current_user in ('Master','User') else None)
    
    canvas = state.bg_canvas
        
    canvas.bind("<Button-1>", lambda event: on_ring_press(event) if g_auth.current_user == 'Master' and state.drag_and_drop else None )
    
    canvas.bind("<B1-Motion>", on_ring_motion )
    canvas.bind("<ButtonRelease-1>",on_ring_release )

   
    
    
    state.bg_canvas.bind("<Button-3>", on_right_click_ring)

    admin_elements.Create_CButton(open_pin_window)
 
    state.admin_button.place_forget()
        
    win.after(500, monitor_refresh_flag)
    
    win.after(100, update_button_visibility)
    #win.after(60000, lambda: win.attributes("-topmost", True))
    
    state.bg_canvas.update()

    win.protocol("WM_DELETE_WINDOW", disable_event)
    
    if state.no_uart:
        state.disp_ERROR = canvas.create_text(400,300,
            text = prepare_text_for_widget(_("NO CONNECTION\nCHECK CONNECTIONS")),
            fill="white",
            font=("Arial", 40), 
            anchor="center"
             )
        
    width = canvas.winfo_width()
    height = canvas.winfo_height()
  
    update_canvas_texts(state.bg_canvas)
    win.mainloop()
