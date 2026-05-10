from vacantview.core.state import g_auth, state
from tkinter import Menu
from .functions.status_color_scheme import open_custom_color_picker, apply_ring_color, apply_progress_color, apply_outring_color, apply_indicator_background_color, \
     apply_text_color, recolor_figure, recolor_accessable_rect, apply_a_panel_color, apply_indicator_number_color
from .functions.status_indicators import change_status_indicator_font, change_status_indicator_font_size,change_status_indicator_font_style
from .functions.branding_images import upload_background_image, upload_logo_image, set_canvas_background_color,resize_logo
from .functions.title_editor import change_main_title_font, change_main_title_font_size, edit_main_title_text, edit_line_width, \
     make_line_horizontal, make_line_vertical, adjust_line_delta, get_line_delta, change_main_title_font_style, scale_tagged_items, scale_graph_elements_by_tag, \
     change_accessiable_panel_width,scale_accessible_panel
from tkinter import Menu, filedialog

from tkinter import messagebox

from .functions.design_import_export import export_canvas_to_json, import_canvas_from_json, r_to_default, config_screen_load, set_force_load

from .functions.modes import men_mode,women_mode,both_mode,custom_mode

from vacantview.utils.test_usb import check_usb, detect_usb

from .functions.communication_blocking import block_communications, unblock_communications
from .functions.audio_manager import select_audio_vacant, select_audio_occupied
from vacantview.ui.context_menu.rtl_func import prepare_text_for_widget, update_canvas_texts
from vacantview.config.config import set_language

import tkinter as tk
import tkinter.font as tkfont
import arabic_reshaper

from bidi.algorithm import get_display

import subprocess
import sys

DEBUG = state.DEBUG
win = state.win



def exit_mode():
    g_auth.current_user = 'Guest'
    if not state.clean_mode_button_1:
        state.bg_canvas.itemconfigure('cleaning_message_1', state='hidden')
        state.bg_canvas.itemconfigure('cleaning_message_1_add', state='hidden')

    if not state.clean_mode_button_2:
        state.bg_canvas.itemconfigure('cleaning_message_2', state='hidden')
        state.bg_canvas.itemconfigure('cleaning_message_2_add', state='hidden')
    if not state.custom_title:
        state.bg_canvas.itemconfigure('custom_title_text', state='hidden')
    win.quit()

def show_delta_input_popup(event=None, tag=None):
    x = event.x_root if event else win.winfo_pointerx()
    y = event.y_root if event else win.winfo_pointery()

    current_delta = get_line_delta(tag)
    if current_delta is None:
        print(f"[WARNING] Can't determine line length for tag '{tag}'")
        return

    popup = tk.Toplevel(win)
    popup.wm_overrideredirect(True)
    popup.geometry(f"250x100+{x}+{y}")
    popup.configure(bg="white", padx=10, pady=10)

    label = tk.Label(popup, text=prepare_text_for_widget(_("Line length (≥10 px):")), bg="white")
    label.pack(anchor="w")

    entry = tk.Entry(popup, width=30)
    entry.insert(0, str(current_delta))
    entry.pack(pady=5)
    entry.focus_set()

    def apply():
        try:
            new_delta = int(entry.get())
            new_delta = max(new_delta, 10)
            adjust_line_delta(tag, new_delta)
        except ValueError:
            print("[WARNING] Invalid input, must be an integer")
        popup.destroy()

    apply_btn = tk.Button(popup, text=prepare_text_for_widget(_("OK")), command=apply)
    apply_btn.pack()

    def close(event):
        popup.destroy()

    popup.bind("<FocusOut>", close)
    entry.bind("<Return>", lambda e: apply())

def reshape_rtl_text(text):
    # Use arabic_reshaper to reshape Arabic (or similar) text for correct display
    reshaped_text = arabic_reshaper.reshape(text)
    # Use get_display to reorder characters properly for right-to-left rendering
    return get_display(reshaped_text)

def is_rtl_char(char):
    # Check if a single character is in the Unicode range commonly used for RTL scripts
    # '\u0590' to '\u08FF' covers Hebrew, Arabic, and related blocks
    return '\u0590' <= char <= '\u08FF'

def is_rtl_text(text):
    # Check if any character in the text belongs to the RTL character range
    # If yes, treat the entire string as RTL
    return any(is_rtl_char(c) for c in text)

def prepare_text_for_widget(text: str) -> str:
  
    if not text:
        return text
    if is_rtl_text(text):
        reshaped = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped)
        return bidi_text
    else:
        return text

def show_text_input_popup(event=None, tag=None):
    try:
        # Run a PyQt widget as a separate process using the current Python interpreter
        result = subprocess.run(
            [sys.executable, "vacantview/ui/context_menu/pyqt_rtl_input.py"],
            capture_output=True,  # Capture stdout and stderr
            text=True,            # Return output as text (not bytes)
            timeout=60            # Timeout after 60 seconds
        )

        # Check if the subprocess ended with an error
        if result.returncode != 0:
            print("Error in pyqt_rtl_input.py:")
            print(result.stderr)  # Print the error message from the subprocess
            return

        raw_text = result.stdout.strip()  # Get the output text and remove leading/trailing whitespace
        if not raw_text:  # If output is empty, do nothing
            return

        # If the text is in a right-to-left language, reshape it for correct display
        if is_rtl_text(raw_text):
            display_text = reshape_rtl_text(raw_text)
        else:
            display_text = raw_text  # Otherwise, use the text as is

        # If a tag is provided, update the main title text using this tag and the processed text
        if tag:
            edit_main_title_text(tag, display_text)

    except subprocess.TimeoutExpired:
        # Handle the case when the subprocess takes too long (over 60 seconds)
        pass
    except Exception as e:
        # Handle any other exceptions silently (you may want to log them in real code)
        pass


def show_scroll_menu_font(event=None,tag=None):

    x = event.x_root if event else win.winfo_pointerx()
    y = event.y_root if event else win.winfo_pointery()

    menu_win = tk.Toplevel(win)
    menu_win.wm_overrideredirect(True)
    menu_win.geometry(f"200x150+{x}+{y}")

    scrollbar = tk.Scrollbar(menu_win)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    listbox = tk.Listbox(menu_win, yscrollcommand=scrollbar.set)
    font_list = sorted(tkfont.families())
    for font in font_list:
        listbox.insert(tk.END, font)
    listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar.config(command=listbox.yview)

    def on_select(evt):
        selected = listbox.get(listbox.curselection())
        if tag not in ('graph_w_GREEN','graph_w_RED','graph_M_GREEN','graph_M_RED'):
            change_main_title_font(tag,selected)
        else:
            change_status_indicator_font(tag,selected)
        if DEBUG:
            print(f"Selected font: {selected}")
        menu_win.destroy()

    listbox.bind("<ButtonRelease-1>", on_select)
    listbox.focus_set()

    def close(event):
        menu_win.destroy()

    menu_win.bind("<FocusOut>", close)

def show_scroll_menu_width_line(event=None,tag=None):

    x = event.x_root if event else win.winfo_pointerx()
    y = event.y_root if event else win.winfo_pointery()

    menu_win = tk.Toplevel(win)
    menu_win.wm_overrideredirect(True)
    menu_win.geometry(f"50x150+{x}+{y}")

    scrollbar = tk.Scrollbar(menu_win)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    listbox = tk.Listbox(menu_win, yscrollcommand=scrollbar.set)
    line_widths = [1, 2, 3, 4, 5, 6, 8, 10, 12, 14, 16, 18, 20]
    for width in line_widths:
        listbox.insert(tk.END, width)
    listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar.config(command=listbox.yview)

    def on_select(evt):
        selected = listbox.get(listbox.curselection())
        if tag=='v_line':
            edit_line_width(tag,selected)
        elif tag in ('accessible_panel_men','accessible_panel_women'):
            change_accessiable_panel_width(tag,selected)


        if DEBUG:
            print(f"Selected width line: {selected}")
        menu_win.destroy()

    listbox.bind("<ButtonRelease-1>", on_select)
    listbox.focus_set()

    def close(event):
        menu_win.destroy()

    menu_win.bind("<FocusOut>", close)

def show_scroll_menu_size(event=None,tag=None):

    x = event.x_root if event else win.winfo_pointerx()
    y = event.y_root if event else win.winfo_pointery()

    menu_win = tk.Toplevel(win)
    menu_win.wm_overrideredirect(True)
    menu_win.geometry(f"50x150+{x}+{y}")

    scrollbar = tk.Scrollbar(menu_win)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    listbox = tk.Listbox(menu_win, yscrollcommand=scrollbar.set)
    font_sizes = [
        8, 9, 10, 11, 12, 14, 16, 18, 20, 22,
        24, 26, 28, 32, 36, 40, 44, 48, 52, 56,
        60, 64, 68, 72, 80, 88, 96, 104, 112, 120,
        128, 136, 144, 152, 160, 168, 176, 184 ]
    for font in font_sizes:
        listbox.insert(tk.END, font)
    listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar.config(command=listbox.yview)

    def on_select(evt):
        selected = listbox.get(listbox.curselection())

        if tag not in ('graph_w_GREEN','graph_w_RED','graph_M_GREEN','graph_M_RED'):
            change_main_title_font_size(tag,selected)
        else:
            change_status_indicator_font_size(tag,selected)

        if DEBUG:
            print(f"Selected size: {selected}")
        menu_win.destroy()

    listbox.bind("<ButtonRelease-1>", on_select)
    listbox.focus_set()

    def close(event):
        menu_win.destroy()

    menu_win.bind("<FocusOut>", close)

def select_file_for_usb(mount_point,mode):
    if mode == 'background':
        fltypes = [("Images", "*.png *.jpg *.jpeg *.bmp"),]
    elif mode == 'logo':
        fltypes =[("Images PNG", "*.png"),]

    filepath = filedialog.askopenfilename(
        title=f"Logo {mount_point}",
        initialdir=mount_point,
        filetypes=fltypes
    )

    if filepath and mode == 'background':
        upload_background_image(filepath)
    elif filepath and mode == 'logo':
        upload_logo_image(filepath)

def show_scroll_menu_style(event=None,tag=None):

    x = event.x_root if event else win.winfo_pointerx()
    y = event.y_root if event else win.winfo_pointery()

    menu_win = tk.Toplevel(win)
    menu_win.wm_overrideredirect(True)
    menu_win.geometry(f"100x150+{x}+{y}")

    scrollbar = tk.Scrollbar(menu_win)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    listbox = tk.Listbox(menu_win, yscrollcommand=scrollbar.set)

    font_styles = ['italic','bold','bold italic','normal']
    for style in font_styles:
        listbox.insert(tk.END, style)
    listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar.config(command=listbox.yview)

    def on_select(evt):
        selected = listbox.get(listbox.curselection())

        if tag not in ('graph_w_GREEN','graph_w_RED','graph_M_GREEN','graph_M_RED'):
            change_main_title_font_style(tag,selected)
        else:
            change_status_indicator_font_style(tag,selected)

        if DEBUG:
            print(f"Selected size: {selected}")
        menu_win.destroy()

    listbox.bind("<ButtonRelease-1>", on_select)
    listbox.focus_set()

    def close(event):
        menu_win.destroy()

    menu_win.bind("<FocusOut>", close)

def get_unique_tags_of_hidden_items(canvas):
    hidden_tags = set()
    for item in canvas.find_all():
        if canvas.itemcget(item, 'state') == 'hidden':
            for tag in canvas.gettags(item):
                hidden_tags.add(tag)
    return list(hidden_tags)

def show_context_menu(event, target=None, identifier=None):
    if DEBUG:
        print(f"Right-clicked on: {target} | ID: {identifier}")
    if g_auth.current_user in ('Master', 'User',):
        menu = Menu(event.widget, tearoff=0)
    else:
        return
    if g_auth.current_user == "Master":
        

        state.hidden_tags = get_unique_tags_of_hidden_items(state.bg_canvas)


        hidden_items_menu = tk.Menu(menu, tearoff=0)
        state.filtered_tags = [tag for tag in state.hidden_tags if tag not in ('cleaning_message_1','cleaning_message_2', 'custom_title_text')]

        if not state.filtered_tags:
            hidden_items_menu.add_command(label=prepare_text_for_widget(_("Empty")), state="disabled")
        elif state.current_mode == 'custom':
            for tag in state.filtered_tags:
                if tag=="graph_M_GREEN":
                    hidden_items_menu.add_command(
                    label=f"Status Indicator Men Vacant",
                    command=lambda t=tag: state.bg_canvas.itemconfigure(t, state='normal'))
                elif tag=="graph_M_RED":
                    hidden_items_menu.add_command(
                    label=f"Status Indicator Men Occupied",
                    command=lambda t=tag: state.bg_canvas.itemconfigure(t, state='normal'))
                elif tag=="graph_w_GREEN":
                    hidden_items_menu.add_command(
                    label=f"Status Indicator Women Vacant",
                    command=lambda t=tag: state.bg_canvas.itemconfigure(t, state='normal'))
                elif tag=="graph_w_RED":
                    hidden_items_menu.add_command(
                    label=f"Status Indicator Women Occupied",
                    command=lambda t=tag: state.bg_canvas.itemconfigure(t, state='normal'))
                elif tag == 'h1':
                    hidden_items_menu.add_command(
                    label=f"Main Headline",
                    command=lambda t=tag: state.bg_canvas.itemconfigure(t, state='normal'))
                elif tag == 'h2_v':
                    hidden_items_menu.add_command(
                    label=f"Description of Vacant Status 1",
                    command=lambda t=tag: state.bg_canvas.itemconfigure(t, state='normal'))
                elif tag == 'h2_o':
                    hidden_items_menu.add_command(
                    label=f"Description of Occupied Status 1",
                    command=lambda t=tag: state.bg_canvas.itemconfigure(t, state='normal'))
                elif tag == 'h2_v2':
                    hidden_items_menu.add_command(
                    label=f"Description of Vacant Status 2",
                    command=lambda t=tag: state.bg_canvas.itemconfigure(t, state='normal'))
                elif tag == 'h2_o2':
                    hidden_items_menu.add_command(
                    label=f"Description of Occupied Status 2",
                    command=lambda t=tag: state.bg_canvas.itemconfigure(t, state='normal'))
                elif tag == 'v_line':
                    hidden_items_menu.add_command(
                    label=f"Divider Line",
                    command=lambda t=tag: state.bg_canvas.itemconfigure(t, state='normal'))
                elif tag == 'Cubiculs_MEN':
                    hidden_items_menu.add_command(
                    label=f"Total Number of Men's Restrooms",
                    command=lambda t=tag: [state.bg_canvas.itemconfigure(t, state='normal'),state.s_element_dict[state.current_mode].append('Cubiculs_MEN')])
                elif tag == 'Cubiculs_WOMEN':

                    hidden_items_menu.add_command(
                    label=f"Total Number of Women's Restrooms",
                    command=lambda t=tag: [state.bg_canvas.itemconfigure(t, state='normal'),state.s_element_dict[state.current_mode].append('Cubiculs_WOMEN')])
                elif tag  == 'figure_men':
                    hidden_items_menu.add_command(
                    label=f"Male Figure",
                    command=lambda t=tag: state.bg_canvas.itemconfigure(t, state='normal'))
                elif tag == 'figure_women':
                    hidden_items_menu.add_command(
                    label=f"Female Figure",
                    command=lambda t=tag: state.bg_canvas.itemconfigure(t, state='normal'))
                elif tag == 'logo':
                    hidden_items_menu.add_command(
                    label=f"Logo",
                    command=lambda t=tag: state.bg_canvas.itemconfigure(t, state='normal'))
                elif tag == 'accessible_panel_men':
                    hidden_items_menu.add_command(
                    label=f"Status Panel for Men's Accessible Restrooms",
                    command=lambda t=tag: state.bg_canvas.itemconfigure(t, state='normal'))
                elif tag == 'accessible_panel_women':
                    hidden_items_menu.add_command(
                    label=f"Status Panel for Women's Accessible Restrooms",
                    command=lambda t=tag: state.bg_canvas.itemconfigure(t, state='normal'))
                elif tag == 'accessible_vacant_indicator_men':

                    hidden_items_menu.add_command(
                    label=f"Vacant Indicator for Men's Accessible Restrooms",
                    command=lambda t=tag: [state.bg_canvas.itemconfigure(t, state='normal'),state.s_element_dict[state.current_mode].append('accessible_vacant_indicator_men')])
                elif tag == 'accessible_vacant_indicator_women':

                    hidden_items_menu.add_command(
                    label=f"Vacant Indicator for Women's Accessible Restrooms",
                    command=lambda t=tag: [state.bg_canvas.itemconfigure(t, state='normal'),state.s_element_dict[state.current_mode].append('accessible_vacant_indicator_women')])
                elif tag == 'accessible_occup_indicator_men':

                    hidden_items_menu.add_command(
                    label=f"Occupied Indicator for Men's Accessible Restrooms",
                    command=lambda t=tag: [state.bg_canvas.itemconfigure(t, state='normal'),state.s_element_dict[state.current_mode].append('accessible_occup_indicator_men')])
                elif tag == 'accessible_occup_indicator_women':

                    hidden_items_menu.add_command(
                    label=f"Occupied Indicator for Women's Accessible Restrooms",
                    command=lambda t=tag: [state.bg_canvas.itemconfigure(t, state='normal'),state.s_element_dict[state.current_mode].append('accessible_occup_indicator_women')])
                elif tag == 'TOTAL_1':
                    hidden_items_menu.add_command(
                    label=f"Text for Men's figure",
                    command=lambda t=tag: state.bg_canvas.itemconfigure(t, state='normal'))
                elif tag == 'TOTAL_2':
                    hidden_items_menu.add_command(
                    label=f"Text for Women's figure",
                    command=lambda t=tag: state.bg_canvas.itemconfigure(t, state='normal'))

        elif state.current_mode != 'custom':
            for tag in state.filtered_tags:
                if tag == 'logo':
                    hidden_items_menu.add_command(
                        label=f"Logo",
                        command=lambda t=tag: state.bg_canvas.itemconfigure(t, state='normal'))
                elif tag == 'TOTAL_1':
                    if state.current_mode in ('men','men_accessible'):
                        hidden_items_menu.add_command(
                        label=f"Text for Men's figure",
                        command=lambda t=tag: state.bg_canvas.itemconfigure(t, state='normal'))
                elif tag == 'TOTAL_2':
                    if state.current_mode in ('women','women_accessible'):
                        hidden_items_menu.add_command(
                        label=f"Text for Women's figure",
                        command=lambda t=tag: state.bg_canvas.itemconfigure(t, state='normal'))
                elif tag == 'h1':
                    hidden_items_menu.add_command(
                    label=f"Main Headline",
                    command=lambda t=tag: state.bg_canvas.itemconfigure(t, state='normal'))
                elif tag == 'h2_v':
                    if state.current_mode in ('men','men_accessible'):
                        hidden_items_menu.add_command(
                        label=f"Description of Vacant Status 1",
                        command=lambda t=tag: state.bg_canvas.itemconfigure(t, state='normal'))
                elif tag == 'h2_o':
                    if state.current_mode in ('men','men_accessible'):
                        hidden_items_menu.add_command(
                        label=f"Description of Occupied Status 1",
                        command=lambda t=tag: state.bg_canvas.itemconfigure(t, state='normal'))
                elif tag == 'h2_v2':
                    if state.current_mode in ('women','women_accessible'):
                        hidden_items_menu.add_command(
                        label=f"Description of Vacant Status 2",
                        command=lambda t=tag: state.bg_canvas.itemconfigure(t, state='normal'))
                elif tag == 'h2_o2':
                    if state.current_mode in ('women','women_accessible'):
                        hidden_items_menu.add_command(
                        label=f"Description of Occupied Status 2",
                        command=lambda t=tag: state.bg_canvas.itemconfigure(t, state='normal'))
            if not 'logo' in state.filtered_tags:
                hidden_items_menu.add_command(label="Empty", state="disabled")

        menu.add_cascade(label=prepare_text_for_widget(_("Hidden Elements")), menu=hidden_items_menu)
        def save_and_adapt():
            answer = messagebox.askokcancel(
                "Warning",
                "The current element sizes match the resolution, so it is not recommended to use this function, "
                "as the sizes of indicators may change. Continue anyway?"
            )
            if answer:
                export_canvas_to_json(state.bg_canvas, True, None, True)
                config_screen_load()
                import_canvas_from_json(state.bg_canvas, state.current_mode)
            else:
                print("Cancel pressed — performing cancel action")
        if state.current_res_size == (state.bg_canvas.winfo_width(),state.bg_canvas.winfo_height()):
            menu.add_command(
                    label=prepare_text_for_widget(_("Save and adapt resolution")),
                    command=save_and_adapt
                )
                    
        else:            
            menu.add_command(label=prepare_text_for_widget(_("Save and adapt resolution")),command=lambda: (export_canvas_to_json(state.bg_canvas, True,None, True), config_screen_load(), import_canvas_from_json(state.bg_canvas, state.current_mode)))
        
        
        if target == 'accessible_panel_men':

            menu.add_command(label=prepare_text_for_widget(_("Scale ( + )")), command=lambda: scale_accessible_panel(tag=identifier,direction='+'))
            menu.add_command(label=prepare_text_for_widget(_("Scale ( - )")), command=lambda: scale_accessible_panel(tag=identifier,direction='-'))

            width_line_menu = Menu(menu, tearoff=0)
            width_line_menu.add_command(label=prepare_text_for_widget(_("Set Width")), command=lambda: show_scroll_menu_width_line(tag=identifier))
            menu.add_cascade(label=prepare_text_for_widget(_("Line Width")), menu=width_line_menu )

            color_line_menu = Menu(menu, tearoff=0)
            color_line_menu.add_command(label=prepare_text_for_widget(_("Set Line Color")), command=lambda: open_custom_color_picker(win, identifier, apply_a_panel_color))

            menu.add_cascade(label=prepare_text_for_widget(_("Line Color Schema")), menu=color_line_menu )

            if not state.current_mode in ('men','women','both','men_accessible','women_accessible','both_accessible'):
                menu.add_command(label=prepare_text_for_widget(_("Hide Panel")), command=lambda: (
                    state.bg_canvas.itemconfigure(identifier, state='hidden'),
                    state.bg_canvas.itemconfigure('accessible_occup_indicator_men', state='normal'),
                    state.bg_canvas.itemconfigure('accessible_vacant_indicator_men', state='normal')
                ))

        if target == 'accessible_panel_women':

            menu.add_command(label=prepare_text_for_widget(_("Scale ( + )")), command=lambda: scale_accessible_panel(tag=identifier,direction='+'))
            menu.add_command(label=prepare_text_for_widget(_("Scale ( - )")), command=lambda: scale_accessible_panel(tag=identifier,direction='-'))

            width_line_menu = Menu(menu, tearoff=0)
            width_line_menu.add_command(label=prepare_text_for_widget(_("Set Width")), command=lambda: show_scroll_menu_width_line(tag=identifier))
            menu.add_cascade(label=prepare_text_for_widget(_("Line Width")), menu=width_line_menu )

            color_line_menu = Menu(menu, tearoff=0)
            color_line_menu.add_command(label=prepare_text_for_widget(_("Set Line Color")), command=lambda: open_custom_color_picker(win, identifier, apply_a_panel_color))

            menu.add_cascade(label=prepare_text_for_widget(_("Line Color Schema")), menu=color_line_menu )

            if not state.current_mode in ('men','women','both','men_accessible','women_accessible','both_accessible'):
                menu.add_command(label=prepare_text_for_widget(_("Hide Panel")), command=lambda: (
                    state.bg_canvas.itemconfigure(identifier, state='hidden'),
                    state.bg_canvas.itemconfigure('accessible_occup_indicator_women', state='normal'),
                    state.bg_canvas.itemconfigure('accessible_vacant_indicator_women', state='normal')
                ))


        if target == "ring":

            menu.add_command(label=prepare_text_for_widget(_("Scale ( + )")), command=lambda: scale_graph_elements_by_tag(tag=identifier,direction='+'))
            menu.add_command(label=prepare_text_for_widget(_("Scale ( - )")), command=lambda: scale_graph_elements_by_tag(tag=identifier,direction='-'))

            status_color_menu = Menu(menu, tearoff=0)
            if state.a_progress_on:
                if state.indicator_type == 'circle' or state.indicator_type == 'square' or state.indicator_type == 'rounded':
                    status_color_menu.add_command(label=prepare_text_for_widget(_("Disable Progress Animation")), command=lambda: (setattr(state,'a_progress_on',False),))

                status_color_menu.add_command(label=prepare_text_for_widget(_("Set Status Color")), command=lambda: open_custom_color_picker(win, identifier, apply_ring_color))
                if state.indicator_type == 'circle' or state.indicator_type == 'square' or state.indicator_type == 'rounded':
                    status_color_menu.add_command(label=prepare_text_for_widget(_("Set Progress Status Color")), command=lambda: open_custom_color_picker(win, identifier, apply_progress_color))

            else:
                if state.indicator_type == 'circle' or state.indicator_type == 'square' or state.indicator_type == 'rounded':
                    status_color_menu.add_command(label=prepare_text_for_widget(_("Enable Progress Animation")), command=lambda: (setattr(state,'a_progress_on',True),))
                status_color_menu.add_command(label=prepare_text_for_widget(_("Set Status Color")), command=lambda: open_custom_color_picker(win, identifier, apply_ring_color))

            if not state.indicator_type == 'rounded':
                status_color_menu.add_command(label=prepare_text_for_widget(_("Set Outer Ring Status Color")), command=lambda: open_custom_color_picker(win, identifier, apply_outring_color))
            status_color_menu.add_command(label=prepare_text_for_widget(_("Set Indicator Background Color")), command=lambda: open_custom_color_picker(win, identifier, apply_indicator_background_color))
            status_color_menu.add_command(label=prepare_text_for_widget(_("Set Number Color")), command=lambda: open_custom_color_picker(win, identifier, apply_indicator_number_color))

            menu.add_cascade(label=prepare_text_for_widget(_("Status Color Scheme")), menu=status_color_menu)

            if not state.current_mode in ('men','women','both','men_accessible','women_accessible','both_accessible'):
                menu.add_command(label=prepare_text_for_widget(_("Hide Ring")), command=lambda: (state.bg_canvas.itemconfigure(identifier, state='hidden')))

            indicators_menu = Menu(menu, tearoff=0)
            indicators_menu.add_command(label=prepare_text_for_widget(_("Set Indicator Font")), command=lambda: show_scroll_menu_font(tag=identifier))
            indicators_menu.add_command(label=prepare_text_for_widget(_("Set Indicator Font Size")), command=lambda: show_scroll_menu_size(tag=identifier))
            indicators_menu.add_command(label=prepare_text_for_widget(_("Set Indicator Font Style")), command=lambda: show_scroll_menu_style(tag=identifier))

            if state.indicator_type == 'circle':
                indicators_menu.add_command(label=prepare_text_for_widget(_("Set Indicator Shape ( Square )")), command=lambda: (setattr(state, 'a_progress_on', True),setattr(state, 'indicator_type', 'square'), setattr(state, 'refresh_ui_flag', True)))
                indicators_menu.add_command(label=prepare_text_for_widget(_("Set Indicator Shape ( Rounded )")), command=lambda: (setattr(state, 'a_progress_on', True),setattr(state, 'refresh_ui_flag', True), setattr(state, 'indicator_type', 'rounded')))
            elif state.indicator_type == 'square':
                indicators_menu.add_command(label=prepare_text_for_widget(_("Set Indicator Shape ( Circle )")), command=lambda: (setattr(state, 'a_progress_on', True),setattr(state, 'refresh_ui_flag', True), setattr(state, 'indicator_type', 'circle')))
                indicators_menu.add_command(label=prepare_text_for_widget(_("Set Indicator Shape ( Rounded )")), command=lambda: (setattr(state, 'a_progress_on', True),setattr(state, 'refresh_ui_flag', True), setattr(state, 'indicator_type', 'rounded')))
            elif state.indicator_type == 'rounded':
                indicators_menu.add_command(label=prepare_text_for_widget(_("Set Indicator Shape ( Circle )")), command=lambda: (setattr(state, 'a_progress_on', True),setattr(state, 'refresh_ui_flag', True), setattr(state, 'indicator_type', 'circle')))
                indicators_menu.add_command(label=prepare_text_for_widget(_("Set Indicator Shape ( Square )")), command=lambda: (setattr(state, 'a_progress_on', True),setattr(state, 'refresh_ui_flag', True), setattr(state, 'indicator_type', 'square')))

            menu.add_cascade(label=prepare_text_for_widget(_("Numerical Status Indicators")), menu=indicators_menu)


        elif target=='background':

            view_mode_menu = tk.Menu(menu, tearoff=0)
            if state.current_mode == 'custom':
                export_custom_menu = tk.Menu(view_mode_menu, tearoff=0)
                export_custom_menu.add_command(label=prepare_text_for_widget(_("Man Restroom")), command=lambda: (export_canvas_to_json(state.bg_canvas,False,'men')))
                export_custom_menu.add_command(label=prepare_text_for_widget(_("Man with Accessible Restroom")), command=lambda: (export_canvas_to_json(state.bg_canvas,False, 'men_accessible')))
                export_custom_menu.add_command(label=prepare_text_for_widget(_("Woman Restroom")), command=lambda: (export_canvas_to_json(state.bg_canvas,False,  'women')))
                export_custom_menu.add_command(label=prepare_text_for_widget(_("Woman with Accessible Restroom")), command=lambda: (export_canvas_to_json(state.bg_canvas,False,'women_accessible')))
                export_custom_menu.add_command(label=prepare_text_for_widget(_("Family Restroom")), command=lambda: (export_canvas_to_json(state.bg_canvas,False, 'both')))
                export_custom_menu.add_command(label=prepare_text_for_widget(_("Family with Accessible Restroom")), command=lambda: (export_canvas_to_json(state.bg_canvas,False,  'both_accessible')))
                view_mode_menu.add_cascade(label=prepare_text_for_widget(_("Export")), menu=export_custom_menu)
            else:
                view_mode_menu.add_command(label=prepare_text_for_widget(_("Export")), command=lambda: export_canvas_to_json(state.bg_canvas))
            view_mode_menu.add_command(label=prepare_text_for_widget(_("Import")), command=lambda: (import_canvas_from_json(state.bg_canvas), scale_graph_elements_by_tag(None, None)))
            view_mode_menu.add_command(label=prepare_text_for_widget(_("Save")), command=lambda: (export_canvas_to_json(state.bg_canvas, True),config_screen_load()))
            view_mode_menu.add_command(label=prepare_text_for_widget(_("Force use current mode")), command= lambda: set_force_load(str(state.current_mode)))
            view_mode_menu.add_command(label=prepare_text_for_widget(_("Adapt viewing mode")), command= lambda: set_force_load())
            
            view_mode_menu.add_command(label=prepare_text_for_widget(_("Restore to Default")), command=lambda: (r_to_default(), import_canvas_from_json(state.bg_canvas, state.current_mode), scale_graph_elements_by_tag(None, None)))
            menu.add_cascade(label=prepare_text_for_widget(_("View Mode Settings")), menu=view_mode_menu)

            mode_menu = tk.Menu(menu, tearoff=0)
            mode_menu.add_command(label=prepare_text_for_widget(_("Man Restroom")), command=lambda: (setattr(state, 'current_mode', 'men'), state.string_genderSelect.set(state.BackGrounds[0]), import_canvas_from_json(state.bg_canvas, state.current_mode)))
            mode_menu.add_command(label=prepare_text_for_widget(_("Man with Accessible Restroom")), command=lambda: (setattr(state, 'current_mode', 'men_accessible'), state.string_genderSelect.set(state.BackGrounds[0]), import_canvas_from_json(state.bg_canvas, state.current_mode)))
            mode_menu.add_command(label=prepare_text_for_widget(_("Woman Restroom")), command=lambda: (setattr(state, 'current_mode', 'women'), state.string_genderSelect.set(state.BackGrounds[1]), import_canvas_from_json(state.bg_canvas, state.current_mode)))
            mode_menu.add_command(label=prepare_text_for_widget(_("Woman with Accessible Restroom")), command=lambda: (setattr(state, 'current_mode', 'women_accessible'), state.string_genderSelect.set(state.BackGrounds[1]), import_canvas_from_json(state.bg_canvas, state.current_mode)))
            mode_menu.add_command(label=prepare_text_for_widget(_("Family Restroom")), command=lambda: (setattr(state, 'current_mode', 'both'), state.string_genderSelect.set(state.BackGrounds[2]), import_canvas_from_json(state.bg_canvas, state.current_mode)))
            mode_menu.add_command(label=prepare_text_for_widget(_("Family with Accessible Restroom")), command=lambda: (setattr(state, 'current_mode', 'both_accessible'), state.string_genderSelect.set(state.BackGrounds[2]), import_canvas_from_json(state.bg_canvas, state.current_mode)))
            mode_menu.add_command(label=prepare_text_for_widget(_("Custom")), command=lambda: (setattr(state, 'current_mode', 'custom'), state.string_genderSelect.set(state.BackGrounds[2]), import_canvas_from_json(state.bg_canvas, state.current_mode)))
            menu.add_cascade(label=prepare_text_for_widget(_("Change View Mode")), menu=mode_menu)


            if not state.drag_and_drop:
                menu_dragging = tk.Menu(menu, tearoff=0)
                for i in range(5, 35, 5):
                    menu_dragging.add_command(label=prepare_text_for_widget(_('Grid Step: {0} px').format(i)), command=lambda i=i: [setattr(state, 'GRID_SIZE', i), setattr(state, 'drag_and_drop', True)])
                menu.add_cascade(label=prepare_text_for_widget(_("Enable Dragging")), menu=menu_dragging)
            else:
                menu.add_command(label=prepare_text_for_widget(_("Disable Dragging")), command=lambda: setattr(state, 'drag_and_drop', False))

            language_menu = Menu(menu, tearoff=0)
            menu.add_cascade(label=prepare_text_for_widget(_("Languages")), menu=language_menu)

            language_menu.add_command(label=prepare_text_for_widget(_("English")), command=lambda: (setattr(state,'current_lang',"en"),set_language("en"),))
            language_menu.add_command(label=prepare_text_for_widget(_("Español")), command=lambda: (setattr(state,'current_lang',"es"),set_language("es"),))
            language_menu.add_command(label=prepare_text_for_widget(_("Français")), command=lambda: (setattr(state,'current_lang',"fr"),set_language("fr"),))
            language_menu.add_command(label=prepare_text_for_widget(_("Deutsch")), command=lambda: (setattr(state,'current_lang',"de"),set_language("de"),))
            language_menu.add_command(label=prepare_text_for_widget("עברית"), command=lambda: (setattr(state,'current_lang',"he"),set_language("he"),))

            if not state.custom_title:
                if state.current_mode in ('both','both_accessible','custom'):
                    
                    menu.add_command(label=prepare_text_for_widget(_("Additional header: On")), command=lambda: (
                        setattr(state, 'custom_title', True),
                        state.bg_canvas.itemconfigure('h2_v_add', state='normal'),
                        state.bg_canvas.itemconfigure('custom_title_text', state='normal'),
                        state.bg_canvas.itemconfigure('h2_o_add', state='normal'),
                        state.bg_canvas.itemconfigure('h2_v2_add', state='normal'),
                        state.bg_canvas.itemconfigure('h2_o2_add', state='normal'),
                        state.bg_canvas.itemconfigure('cleaning_message_2_add', state='normal'),
                        state.bg_canvas.itemconfigure('cleaning_message_1_add', state='normal'),
                        state.bg_canvas.itemconfigure('TOTAL_3', state='normal'),
                        state.bg_canvas.itemconfigure('TOTAL_4', state='normal'),
                    ))
                elif state.current_mode in ('men','men_accessible'):
                    
                    menu.add_command(label=prepare_text_for_widget(_("Additional header: On")), command=lambda: (
                        setattr(state, 'custom_title', True),
                        state.bg_canvas.itemconfigure('h2_v_add', state='normal'),
                        state.bg_canvas.itemconfigure('custom_title_text', state='normal'),
                        state.bg_canvas.itemconfigure('h2_o_add', state='normal'),
                        state.bg_canvas.itemconfigure('cleaning_message_1_add', state='normal'),
                        state.bg_canvas.itemconfigure('TOTAL_3', state='normal'),
                    ))
                        
                elif state.current_mode in ('women','women_accessible'):
                    
                    menu.add_command(label=prepare_text_for_widget(_("Additional header: On")), command=lambda: (
                        setattr(state, 'custom_title', True),
                        state.bg_canvas.itemconfigure('custom_title_text', state='normal'),
                        state.bg_canvas.itemconfigure('h2_v2_add', state='normal'),
                        state.bg_canvas.itemconfigure('h2_o2_add', state='normal'),
                        state.bg_canvas.itemconfigure('cleaning_message_1_add', state='normal'),
                        state.bg_canvas.itemconfigure('TOTAL_4', state='normal'),
                    ))
                    
                    
            else:
                if state.current_mode in ('both','both_accessible','custom'):
                    menu.add_command(label=prepare_text_for_widget(_("Additional header: Off")), command=lambda: (
                        setattr(state, 'custom_title', False),
                        state.bg_canvas.itemconfigure('h2_v_add', state='hidden'),
                        state.bg_canvas.itemconfigure('custom_title_text', state='hidden'),
                        state.bg_canvas.itemconfigure('h2_o_add', state='hidden'),
                        state.bg_canvas.itemconfigure('h2_v2_add', state='hidden'),
                        state.bg_canvas.itemconfigure('h2_o2_add', state='hidden'),
                        state.bg_canvas.itemconfigure('cleaning_message_2_add', state='hidden'),
                        state.bg_canvas.itemconfigure('cleaning_message_1_add', state='hidden'),
                        state.bg_canvas.itemconfigure('TOTAL_3', state='hidden'),
                        state.bg_canvas.itemconfigure('TOTAL_4', state='hidden'),
                    ))
                elif state.current_mode in ('men','men_accessible'):
                    menu.add_command(label=prepare_text_for_widget(_("Additional header: Off")), command=lambda: (
                        setattr(state, 'custom_title', False),
                        state.bg_canvas.itemconfigure('h2_v_add', state='hidden'),
                        state.bg_canvas.itemconfigure('custom_title_text', state='hidden'),
                        state.bg_canvas.itemconfigure('h2_o_add', state='hidden'),
                        state.bg_canvas.itemconfigure('cleaning_message_1_add', state='hidden'),
                        state.bg_canvas.itemconfigure('TOTAL_3', state='hidden'),
                    ))
                    
                elif state.current_mode in ('women','women_accessible'):
                    menu.add_command(label=prepare_text_for_widget(_("Additional header: Off")), command=lambda: (
                        setattr(state, 'custom_title', False),
                        state.bg_canvas.itemconfigure('custom_title_text', state='hidden'),
                        state.bg_canvas.itemconfigure('h2_v2_add', state='hidden'),
                        state.bg_canvas.itemconfigure('h2_o2_add', state='hidden'),
                        state.bg_canvas.itemconfigure('cleaning_message_1_add', state='hidden'),
                        state.bg_canvas.itemconfigure('TOTAL_4', state='hidden'),
                    ))

            audio_menu = Menu(menu, tearoff=0)
            audio_menu.add_command(label=prepare_text_for_widget(_("Set Vacant Audio File")), command=select_audio_vacant)
            audio_menu.add_command(label=prepare_text_for_widget(_("Set Occupied Audio File")), command=select_audio_occupied)
            menu.add_cascade(label=prepare_text_for_widget(_("Audio Announcer")), menu=audio_menu)

            image_menu = Menu(menu, tearoff=0)
            image_menu.add_command(label=prepare_text_for_widget(_("Change Background Image")), command=lambda: upload_background_image())
            image_menu.add_command(label=prepare_text_for_widget(_("Change Logo ")), command=lambda: upload_logo_image())

            usb_devices = detect_usb()

            if usb_devices:
                for path in usb_devices:
                    image_menu.add_command(
                        label=prepare_text_for_widget(_("Change Background Image USB - {0}").format(path)),
                        command=lambda p=path: select_file_for_usb(p, 'background')
                    )
                    image_menu.add_command(
                        label=prepare_text_for_widget(_("Change Logo USB - {0}").format(path)),
                        command=lambda p=path: select_file_for_usb(p, 'logo')
                    )

            menu.add_cascade(label=prepare_text_for_widget(_("Image Handling")), menu=image_menu)

            menu.add_command(label=prepare_text_for_widget(_("Change Background Color")), command=lambda: open_custom_color_picker(win, identifier, set_canvas_background_color))

        elif target == 'text':

            status_text_menu = Menu(menu, tearoff=0)
            status_text_menu.add_command(label=prepare_text_for_widget(_("Set Text Color")), command=lambda: open_custom_color_picker(win, identifier, apply_text_color))
            menu.add_cascade(label=prepare_text_for_widget(_("Text Color Schema")), menu=status_text_menu)

            font_text_menu = Menu(menu, tearoff=0)
            font_text_menu.add_command(label=prepare_text_for_widget(_("Change Font")), command=lambda: show_scroll_menu_font(tag=identifier))
            font_text_menu.add_command(label=prepare_text_for_widget(_("Change Size")), command=lambda: show_scroll_menu_size(tag=identifier))
            font_text_menu.add_command(label=prepare_text_for_widget(_("Change Font Style")), command=lambda: show_scroll_menu_style(tag=identifier))
            
            menu.add_command(
                    label=prepare_text_for_widget(_("Change Text")),
                    command=lambda: show_text_input_popup(tag=identifier)
                )

            '''if identifier in ('h1','custom_title_text','h2_v_add','h2_v2_add','h2_o_add','h2_o2_add','TOTAL_3','TOTAL_4'):
                menu.add_command(
                    label=prepare_text_for_widget(_("Change Text")),
                    command=lambda: show_text_input_popup(tag=identifier)
                )'''

            if identifier in ('accessible_vacant_indicator_men','accessible_vacant_indicator_women','accessible_occup_indicator_men','accessible_occup_indicator_women','h2_v','h2_v2','h2_o','h2_o2','TOTAL_2','TOTAL_1'):
                if not state.current_mode in ('men','women','both','men_accessible','women_accessible','both_accessible'):
                    menu.add_command(label=prepare_text_for_widget(_("Hide")), command=lambda: state.bg_canvas.itemconfigure(identifier, state='hidden'))
            elif identifier in ('custom_title_text','h2_v_add','h2_v2_add','h2_o_add','h2_o2_add','TOTAL_3','TOTAL_4') and state.current_mode != 'custom':
                pass
            else:
                menu.add_command(label=prepare_text_for_widget(_("Hide")), command=lambda: state.bg_canvas.itemconfigure(identifier, state='hidden'))

            menu.add_cascade(label=prepare_text_for_widget(_("Font")), menu=font_text_menu)


        elif target == 'indicator_men':

            status_text_menu = Menu(menu, tearoff=0)
            status_text_menu.add_command(label=prepare_text_for_widget(_("Set Text Color")), command=lambda: open_custom_color_picker(win, identifier, apply_text_color))
            menu.add_cascade(label=prepare_text_for_widget(_("Text Color Schema")), menu=status_text_menu)

            if not state.current_mode in ('men', 'women', 'both', 'men_accessible', 'women_accessible', 'both_accessible'):
                menu.add_command(label=prepare_text_for_widget(_("Hide Indicator")), command=lambda: state.bg_canvas.itemconfigure(identifier, state='hidden'))

            font_text_menu = Menu(menu, tearoff=0)
            font_text_menu.add_command(label=prepare_text_for_widget(_("Change Font")), command=lambda: show_scroll_menu_font(tag=identifier))
            font_text_menu.add_command(label=prepare_text_for_widget(_("Change Size")), command=lambda: show_scroll_menu_size(tag=identifier))
            font_text_menu.add_command(label=prepare_text_for_widget(_("Change Font Style")), command=lambda: show_scroll_menu_style(tag=identifier))

            menu.add_cascade(label=prepare_text_for_widget(_("Font")), menu=font_text_menu)




        elif target == 'indicator_women':

            status_text_menu = Menu(menu, tearoff=0)
            status_text_menu.add_command(label=prepare_text_for_widget(_("Set Text Color")), command=lambda: open_custom_color_picker(win, identifier, apply_text_color))
            menu.add_cascade(label=prepare_text_for_widget(_("Text Color Schema")), menu=status_text_menu)

            if not state.current_mode in ('men', 'women', 'both', 'men_accessible', 'women_accessible', 'both_accessible'):
                menu.add_command(
                    label=prepare_text_for_widget(_("Hide Indicator")),
                    command=lambda: (
                        state.bg_canvas.itemconfigure(identifier, state='hidden'),
                        state.s_element_dict[state.current_mode].remove(identifier)
                    )
                )

            font_text_menu = Menu(menu, tearoff=0)
            font_text_menu.add_command(label=prepare_text_for_widget(_("Change Font")), command=lambda: show_scroll_menu_font(tag=identifier))
            font_text_menu.add_command(label=prepare_text_for_widget(_("Change Size")), command=lambda: show_scroll_menu_size(tag=identifier))
            font_text_menu.add_command(label=prepare_text_for_widget(_("Change Font Style")), command=lambda: show_scroll_menu_style(tag=identifier))

            menu.add_cascade(label=prepare_text_for_widget(_("Font")), menu=font_text_menu)




        elif target == 'line':


            menu.add_command(label=prepare_text_for_widget(_("Set Length")), command=lambda: show_delta_input_popup(tag=identifier))

            color_line_menu = Menu(menu, tearoff=0)
            color_line_menu.add_command(label=prepare_text_for_widget(_("Set Line Color")), command=lambda: open_custom_color_picker(win, identifier, apply_text_color))
            menu.add_cascade(label=prepare_text_for_widget(_("Line Color Schema")), menu=color_line_menu)

            width_line_menu = Menu(menu, tearoff=0)
            width_line_menu.add_command(label=prepare_text_for_widget(_("Set Width")), command=lambda: show_scroll_menu_width_line(tag=identifier))
            menu.add_cascade(label=prepare_text_for_widget(_("Line Width")), menu=width_line_menu)

            if not state.current_mode in ('men','women','both','men_accessible','women_accessible','both_accessible'):
                menu.add_command(label=prepare_text_for_widget(_("Hide Line")), command=lambda: state.bg_canvas.itemconfigure(identifier, state='hidden'))

            if state.line_vertical_pos:
                menu.add_command(label=prepare_text_for_widget(_("Make Line Horizontal")), command=lambda: make_line_horizontal(tag=identifier))
            else:
                menu.add_command(label=prepare_text_for_widget(_("Make Line Vertical")), command=lambda: make_line_vertical(tag=identifier))




        elif target == 'cleaning_message':

            
            menu.add_command(
                label=prepare_text_for_widget(_("Change Text")),
                command=lambda: show_text_input_popup(tag=identifier)
            )
            if identifier not in ('cleaning_message_1',):
                menu.add_command(label=prepare_text_for_widget(_("Hide")), command=lambda: state.bg_canvas.itemconfigure(identifier, state='hidden'))
            menu.add_command(label=prepare_text_for_widget(_("Change Font")), command=lambda: show_scroll_menu_font(tag=identifier))
            menu.add_command(label=prepare_text_for_widget(_("Change Size")), command=lambda: show_scroll_menu_size(tag=identifier))
            menu.add_command(label=prepare_text_for_widget(_("Change Font Style")), command=lambda: show_scroll_menu_style(tag=identifier))
            menu.add_command(label=prepare_text_for_widget(_("Set Text Color")), command=lambda: open_custom_color_picker(win, identifier, apply_text_color))




        elif target == 'figure':

            size_f_menu = Menu(menu, tearoff=0)
            size_f_menu.add_command(label=prepare_text_for_widget(_("Scale ( + )")), command=lambda: scale_tagged_items(identifier, '+'))
            size_f_menu.add_command(label=prepare_text_for_widget(_("Scale ( - )")), command=lambda: scale_tagged_items(identifier, '-'))
            menu.add_cascade(label=prepare_text_for_widget(_("Set figure size")), menu=size_f_menu)

            if not state.current_mode in ('men','women','both','men_accessible','women_accessible','both_accessible'):
                if identifier == 'figure_men':
                    menu.add_command(label=prepare_text_for_widget(_("Hide Men Figure")), command=lambda: (state.bg_canvas.itemconfigure(identifier, state='hidden'), state.bg_canvas.itemconfigure('Cubiculs_MEN', state='normal')))
                elif identifier == 'figure_women':
                    menu.add_command(label=prepare_text_for_widget(_("Hide Women Figure")), command=lambda: (state.bg_canvas.itemconfigure(identifier, state='hidden'), state.bg_canvas.itemconfigure('Cubiculs_WOMEN', state='normal')))

            menu.add_command(label=prepare_text_for_widget(_("Set Color")), command=lambda: open_custom_color_picker(win, identifier, recolor_figure))


        elif target == 'logo':
            menu.add_command(label=prepare_text_for_widget(_("Hide Logo")), command=lambda: state.bg_canvas.itemconfigure(identifier, state='hidden'))
            menu.add_command(label=prepare_text_for_widget(_("Scale ( + )")), command=lambda: resize_logo('+'))
            menu.add_command(label=prepare_text_for_widget(_("Scale ( - )")), command=lambda: resize_logo('-'))


        elif target == 'accessible':
            menu.add_command(label=prepare_text_for_widget(_("Set Color")), command=lambda: open_custom_color_picker(win, identifier, recolor_accessable_rect))


        elif target == "accessible_logo":
            menu.add_command(label=prepare_text_for_widget(_("Change Logo Image")), command=lambda: change_accessible_icon(state.bg_canvas, identifier, state.icon_rect, state.tk_icons))


        menu.add_command(label=prepare_text_for_widget(_("Close Menu")), command=menu.unpost)
        menu.add_command(label=prepare_text_for_widget(_("Exit")), command=exit_mode)


    elif g_auth.current_user == "User":

        if target == "ring":

            status_color_menu = Menu(menu, tearoff=0)
            if state.a_progress_on:
                if state.indicator_type == 'circle' or state.indicator_type == 'square' or state.indicator_type == 'rounded':
                    status_color_menu.add_command(label=prepare_text_for_widget(_("Disable Progress Animation")), command=lambda: (setattr(state, 'a_progress_on', False),))

                status_color_menu.add_command(label=prepare_text_for_widget(_("Set Status Color")), command=lambda: open_custom_color_picker(win, identifier, apply_ring_color))
                if state.indicator_type == 'circle' or state.indicator_type == 'square' or state.indicator_type == 'rounded':
                    status_color_menu.add_command(label=prepare_text_for_widget(_("Set Progress Status Color")), command=lambda: open_custom_color_picker(win, identifier, apply_progress_color))

            else:
                if state.indicator_type == 'circle' or state.indicator_type == 'square' or state.indicator_type == 'rounded':
                    status_color_menu.add_command(label=prepare_text_for_widget(_("Enable Progress Animation")), command=lambda: (setattr(state, 'a_progress_on', True),))
                status_color_menu.add_command(label=prepare_text_for_widget(_("Set Status Color")), command=lambda: open_custom_color_picker(win, identifier, apply_ring_color))

            if not state.indicator_type == 'rounded':
                status_color_menu.add_command(label=prepare_text_for_widget(_("Set Outer Ring Status Color")), command=lambda: open_custom_color_picker(win, identifier, apply_outring_color))

            status_color_menu.add_command(label=prepare_text_for_widget(_("Set Indicator Background Color")), command=lambda: open_custom_color_picker(win, identifier, apply_indicator_background_color))
            status_color_menu.add_command(label=prepare_text_for_widget(_("Set Number Color")), command=lambda: open_custom_color_picker(win, identifier, apply_indicator_number_color))

            menu.add_cascade(label=prepare_text_for_widget(_("Status Color Scheme")), menu=status_color_menu)






        elif target=='background':
            view_mode_menu = tk.Menu(menu, tearoff=0)
            view_mode_menu.add_command(label=prepare_text_for_widget(_("Save")), command=lambda: export_canvas_to_json(state.bg_canvas, True))
            view_mode_menu.add_command(label=prepare_text_for_widget(_("Restore to Default")), command=lambda: (
                r_to_default(),
                import_canvas_from_json(state.bg_canvas, state.current_mode),
                scale_graph_elements_by_tag(None, None)
            ))
            menu.add_cascade(label=prepare_text_for_widget(_("View Mode Settings")), menu=view_mode_menu)




        elif target == 'text':

            status_text_menu = Menu(menu, tearoff=0)
            status_text_menu.add_command(label=prepare_text_for_widget(_("Set Text Color")), command=lambda: open_custom_color_picker(win, identifier, apply_text_color))
            menu.add_cascade(label=prepare_text_for_widget(_("Text Color Schema")), menu=status_text_menu)

        elif target == 'line':

            color_line_menu = Menu(menu, tearoff=0)
            color_line_menu.add_command(label=prepare_text_for_widget(_("Set Line Color")), command=lambda: open_custom_color_picker(win, identifier, apply_text_color))
            menu.add_cascade(label=prepare_text_for_widget(_("Line Color Schema")), menu=color_line_menu)

        elif target == 'cleaning_message':

            menu.add_command(label=prepare_text_for_widget(_("Change Text")), command=lambda: show_text_input_popup(tag=identifier))
            menu.add_command(label=prepare_text_for_widget(_("Change Font")), command=lambda: show_scroll_menu_font(tag=identifier))
            menu.add_command(label=prepare_text_for_widget(_("Change Size")), command=lambda: show_scroll_menu_size(tag=identifier))
            menu.add_command(label=prepare_text_for_widget(_("Change Font Style")), command=lambda: show_scroll_menu_style(tag=identifier))
            menu.add_command(label=prepare_text_for_widget(_("Set Text Color")), command=lambda: open_custom_color_picker(win, identifier, apply_text_color))

        elif target == 'figure':

            menu.add_command(label=prepare_text_for_widget(_("Set Color")), command=lambda: open_custom_color_picker(win, identifier, recolor_figure))

        elif target == 'logo':
            pass

        menu.add_command(label=prepare_text_for_widget(_("Close Menu")), command=menu.unpost)
        menu.add_command(label=prepare_text_for_widget(_("Exit")), command=exit_mode)


    try:
        menu.tk_popup(event.x_root, event.y_root)
        menu.wait_window(menu)
    finally:
        pass

    def close_menu(e):
        menu.unpost()
        event.widget.unbind("<Button-1>", close_handler)

    close_handler = event.widget.bind("<Button-1>", close_menu)

    return "break"
