from tkinter import ttk
from vacantview.core.state import state, g_auth
from vacantview.data.auth import auth_service
from vacantview.data.models import organization
from vacantview.config.config import IMG_DIR, LOGO_DIR, DEBUG
from vacantview.utils.test_usb import check_usb
from vacantview.ui.image_loader import resource_path
from vacantview.ui.context_menu.rtl_func import prepare_text_for_widget
from vacantview.ui.context_menu.functions.communication_blocking import block_communications, unblock_communications
from vacantview.ui.context_menu.functions.design_import_export import import_canvas_from_json, export_canvas_to_json, config_screen_load

import tkinter as tk
import os
import shutil

from PIL import Image, ImageTk

def open_admin_settings(parent):
    if 'admin_window' in state.open_window:
        return

    state.open_window.append('admin_window')

    admin_window = tk.Toplevel(parent)
    admin_window.title(prepare_text_for_widget(_("Admin Settings")))
    admin_window.overrideredirect(True)

    container = tk.Frame(admin_window)
    container.pack(fill="both", expand=True)

    sidebar = tk.Frame(container, width=150, bg="#e0e0e0")
    sidebar.pack(side="left", fill="y")

    tk.Label(sidebar, text = prepare_text_for_widget(_("Menu")), bg="#e0e0e0", font=("Arial", 12, "bold")).pack(pady=10)

    content = tk.Frame(container)
    content.pack(side="left", fill="both", expand=True, padx=10, pady=10)

    pages = {}

    def show_page(page_name):
        for name, frame in pages.items():
            frame.pack_forget()
        pages[page_name].pack(fill="both", expand=True)
        admin_window.update_idletasks()
        width = max(admin_window.winfo_reqwidth(), 400)
        height = max(admin_window.winfo_reqheight(), 400)
        canvas = state.bg_canvas
        canvas_x = canvas.winfo_rootx()
        canvas_y = canvas.winfo_rooty()
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()

        x = canvas_x + (canvas_width - width) // 2
        y = canvas_y + (canvas_height - height) // 2

        admin_window.geometry(f"{width}x{height}+{x}+{y}")
     

    def on_close():
        if 'admin_window' in state.open_window:
            state.open_window.remove('admin_window')
        admin_window.destroy()

    # --- Security Page ---
    security_page = tk.Frame(content)
    tk.Label(security_page, text = prepare_text_for_widget(_("Security Settings")), font=("Arial", 14, "bold")).pack(pady=5)

    selected_user = tk.StringVar()
    if g_auth.current_user == 'Master':
        tk.Label(security_page, text = prepare_text_for_widget(_("Select user:")), font=("Arial", 12)).pack(pady=(10, 2))
        user_combobox = ttk.Combobox(
            security_page,
            textvariable=selected_user,
            values=('Master', 'User'),
            state="readonly",
            width=28
        )
        user_combobox.pack(pady=(0, 10))
    else:
        selected_user.set(g_auth.current_user)

    try:
        if g_auth.current_user == 'Master' and g_auth.current_user in user_combobox['values']:
            user_combobox.set(g_auth.current_user)
        else:
            user_combobox.set(user_combobox['values'][0])
    except:
        pass

    password_var = tk.StringVar()
    access_code_var = tk.StringVar()
    status_var = tk.StringVar()
    action_label_var = tk.StringVar()

    action_label = tk.Label(security_page, textvariable=action_label_var, font=("Arial", 12))
    status_label = tk.Label(security_page, textvariable=status_var)

    show_password = False
    show_code = False

    def on_password_change(*args):
        value = password_var.get()
        if " " in value:
            status_var.set(prepare_text_for_widget(_("Password cannot contain spaces.")))
            status_label.config(fg="red")
        elif len(value) > 16:
            status_var.set(prepare_text_for_widget(_("Password too long (max 16 characters).")))
            status_label.config(fg="red")
        else:
            status_var.set("")

        if " " in value or len(value) > 16:
            password_var.set(value.replace(" ", "")[:16])

    password_var.trace_add('write', on_password_change)

    def validate_password_input(new_value):
        return " " not in new_value and len(new_value) <= 16

    vcmd_pass = (admin_window.register(validate_password_input), '%P')

    password_entry = tk.Entry(
        security_page,
        textvariable=password_var,
        show="*",
        width=30,
        validate="key",
        validatecommand=vcmd_pass
    )

    def toggle_password_visibility():
        nonlocal show_password
        show_password = not show_password
        password_entry.config(show="" if show_password else "*")
        toggle_pass_btn.config(text="Hide" if show_password else "Show")

    toggle_pass_btn = tk.Button(security_page, text="Show", width=8, command=toggle_password_visibility)

    def on_access_code_change(*args):
        value = access_code_var.get()
        if not value.isdigit():
            access_code_var.set(''.join(filter(str.isdigit, value)))
        elif len(value) > 4:
            access_code_var.set(value[:4])

    access_code_var.trace_add('write', on_access_code_change)

    def validate_access_code_input(new_value):
        return (new_value == "" or new_value.isdigit()) and len(new_value) <= 4

    vcmd_access = (admin_window.register(validate_access_code_input), '%P')

    access_code_entry = tk.Entry(
        security_page,
        textvariable=access_code_var,
        show="*",
        width=30,
        validate="key",
        validatecommand=vcmd_access
    )

    def toggle_code_visibility():
        nonlocal show_code
        show_code = not show_code
        access_code_entry.config(show="" if show_code else "*")
        toggle_code_btn.config(text=prepare_text_for_widget(_("Hide")) if show_code else prepare_text_for_widget(_("Show")))

    toggle_code_btn = tk.Button(security_page, text=prepare_text_for_widget(_("Show")), width=8, command=toggle_code_visibility)

    confirm_pass_btn = tk.Button(security_page, text=prepare_text_for_widget(_("Confirm Password")))
    confirm_code_btn = tk.Button(security_page, text=prepare_text_for_widget(_("Confirm Access Code")))


    def reset_security_ui():
        for widget in [action_label, password_entry, toggle_pass_btn, confirm_pass_btn,
                       access_code_entry, toggle_code_btn, confirm_code_btn, status_label]:
            widget.pack_forget()
        password_var.set("")
        access_code_var.set("")
        status_var.set("")
        action_label_var.set("")

    def validate_password():
        new_pass = password_var.get().strip()
        valid_password = auth_service.update_password(selected_user.get(), new_pass)
        if len(new_pass) >= 4 and valid_password:
            status_var.set(prepare_text_for_widget(_("Password changed successfully.")))
            status_label.config(fg="green")
            security_page.after(1500, lambda: (reset_security_ui(), show_page("security")))
        else:
            status_var.set(prepare_text_for_widget(_("Password too short or invalid.")))
            status_label.config(fg="red")
            password_entry.focus_force()

    def validate_access_code():
        new_code = access_code_var.get().strip()
        valid_pin = auth_service.update_pin(selected_user.get(), new_code)
        if new_code.isdigit() and valid_pin and len(new_code) <= 4:
            status_var.set(prepare_text_for_widget(_("Access Code updated.")))
            status_label.config(fg="green")
            security_page.after(1500, lambda: (reset_security_ui(), show_page("security")))
        else:
            status_var.set(prepare_text_for_widget(_("Code must be up to 4 digits.")))
            status_label.config(fg="red")
            access_code_entry.focus_force()

    confirm_pass_btn.config(command=validate_password)
    confirm_code_btn.config(command=validate_access_code)

    tk.Button(
        security_page, text = prepare_text_for_widget(_("Change Password")), width=30,
        command=lambda: (
            reset_security_ui(),
            action_label_var.set(prepare_text_for_widget(_("Enter new password:"))),
            action_label.pack(pady=(10, 0)),
            password_entry.pack(pady=5),
            toggle_pass_btn.pack(),
            confirm_pass_btn.pack(pady=5),
            status_label.pack(pady=(5, 0)),
            admin_window.lift(),
            admin_window.focus_force(),
            admin_window.grab_set(),
            admin_window.after(100, lambda: password_entry.focus_force())
        )
    ).pack(pady=5)

    tk.Button(
        security_page,text = prepare_text_for_widget(_("Change Access Code")), width=30,
        command=lambda: (
            reset_security_ui(),
            action_label_var.set(prepare_text_for_widget(_("Enter new access code:"))),
            action_label.pack(pady=(10, 0)),
            access_code_entry.pack(pady=5),
            toggle_code_btn.pack(),
            confirm_code_btn.pack(pady=5),
            status_label.pack(pady=(5, 0)),
            admin_window.lift(),
            admin_window.focus_force(),
            admin_window.grab_set(),
            admin_window.after(100, lambda: access_code_entry.focus_force())
        )
    ).pack(pady=5)

    pages["security"] = security_page

    # --- System Page ---
    system_page = tk.Frame(content)
    tk.Label(system_page, text = prepare_text_for_widget(_("System Information")), font=("Arial", 14, "bold")).pack(pady=5)
    tk.Label(system_page, text="Version: 0.3.6").pack(anchor="w")
    tk.Label(system_page, text="Last Update: 02.09.2025").pack(anchor="w")
    tk.Label(system_page, text="Device ID: -").pack(anchor="w")
    pages["system"] = system_page

    # --- Organization Page ---
    org_page = tk.Frame(content)
    org_detail = organization.check_organization()
    tk.Label(org_page, text = prepare_text_for_widget(_("Organization Details")), font=("Arial", 14, "bold")).pack(pady=5)
    tk.Label(org_page, text = prepare_text_for_widget(_("Organization Name:"))).pack(anchor="w")
    org_name_entry = tk.Entry(org_page, width=40)
    org_name_entry.insert(0, org_detail[0])
    org_name_entry.pack(pady=5)
    tk.Label(org_page, text = prepare_text_for_widget(_("Organization ID:"))).pack(anchor="w")
    org_id_entry = tk.Entry(org_page, width=40)
    org_id_entry.insert(0, org_detail[1])
    org_id_entry.pack(pady=5)
    pages["organization"] = org_page
    

   # File Management Page

    if g_auth.current_user == 'Master':
        file_page = tk.Frame(content)
        tk.Label(file_page, text = prepare_text_for_widget(_("File Management")), font=("Arial", 14, "bold")).pack(pady=5)

        selected_source = tk.StringVar(value="system")
        selected_category = tk.StringVar(value="Background")
        selected_file = tk.StringVar(value="")

        def get_current_folder():
            if selected_source.get() == "storage":
                base = check_usb()
                print(base)
                if base:
                    return os.path.join(base, selected_category.get())
                return ""
            if selected_category.get() == "Logo" and selected_source.get() == 'system':
                print(f'vacantview/{LOGO_DIR}')#resource_path()
                return f'vacantview/{LOGO_DIR}' #os.path.abspath(f'vacantview/{LOGO_DIR}') resource_path()
            elif selected_category.get() == "Background" and selected_source.get() == 'system':
                print(resource_path(f'vacantview/{IMG_DIR}'))
                return resource_path(f'vacantview/{IMG_DIR}')


        # Source selection
        source_frame = tk.Frame(file_page)
        source_frame.pack(pady=5)

        tk.Label(source_frame, text = prepare_text_for_widget(_("Source:")), font=("Arial", 10)).pack(side="left", padx=5)
        tk.Radiobutton(source_frame, text="System", variable=selected_source, value="system", command=lambda: select_category("Background")).pack(side="left")
        tk.Radiobutton(source_frame, text="Storage", variable=selected_source, value="storage", command=lambda: select_category("Background")).pack(side="left")
    
        

        # Category buttons
        category_frame = tk.Frame(file_page)
        category_frame.pack(pady=5)
    
        def select_category(cat):
            selected_category.set(cat)
            if selected_source.get() == "storage":
                populate_file_list(mode = 'storage',img_type=cat)
            else:
                populate_file_list(mode = 'system',img_type=cat)

        tk.Button(category_frame, text="Background", width=15, command=lambda: select_category("Background")).pack(side="left", padx=5)
        tk.Button(category_frame, text="Logo", width=15, command=lambda: select_category("Logo")).pack(side="left", padx=5)

        # File browser layout
        file_browser_frame = tk.Frame(file_page)
        file_browser_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Top: Listbox (compact)
        top_frame = tk.Frame(file_browser_frame)
        top_frame.pack(side="top", fill="x")

        file_listbox = tk.Listbox(top_frame, font=("Arial", 9), height=5)
        file_listbox.pack(fill="x", padx=5, pady=5)

        # Bottom: Large preview panel (landscape style)
        preview_panel = tk.Frame(file_browser_frame, bg="#dddddd", height=600)
        preview_panel.pack(side="top", fill="both", expand=True, padx=10, pady=(0,10))

        preview_label = tk.Label(preview_panel, text="Preview:", font=("Arial", 11, "bold"), bg="#dddddd")
        preview_label.pack()

        image_preview_label = tk.Label(preview_panel, bg="#dddddd")
        image_preview_label.pack(pady=10, expand=True)

        def populate_file_list(mode='system', img_type="Background", folder=None, storage=None):
    
            img_logo_dir = f'vacantview/{LOGO_DIR}'#resource_path()
            img_back_dir =f'vacantview/{IMG_DIR}'# resource_path()

            if mode == 'system':
                if img_type == "Logo":
                    folder = os.path.abspath(img_logo_dir)
                else:
                    folder = os.path.abspath(img_back_dir)
            else:  # storage mode
                usb_path = check_usb()
                folder = usb_path
                if not usb_path or not os.path.isdir(usb_path):
                    file_listbox.delete(0, tk.END)
                    image_preview_label.config(image="", text = prepare_text_for_widget(_("No storage device found")))
                    return

                # Use subfolder for category if needed
                folder = os.path.join(usb_path, img_type)

            if not os.path.isdir(folder):
                file_listbox.delete(0, tk.END)
                if DEBUG:
                    print(" [WARNING] Directory not found:", folder)
                return

            file_listbox.delete(0, tk.END)
            print(folder)
            files = os.listdir(folder)
            image_exts = ('.jpg', '.jpeg', '.png', '.gif')
            valid_files = [f for f in files if os.path.isfile(os.path.join(folder, f)) and f.lower().endswith(image_exts)]

            for f in sorted(valid_files):
                file_listbox.insert(tk.END, f)
            image_preview_label.config(image="", text="")
            
        def copy_to_system():
            sel = file_listbox.curselection()
            if not sel:
                return
            file_name = file_listbox.get(sel[0])
            source_path = os.path.join(get_current_folder(), file_name)
            
            if selected_category.get() == "Logo":
                
                dest_dir = os.path.abspath(f'vacantview/{LOGO_DIR}')
                
            else:
                
                dest_dir = os.path.abspath(f'vacantview/{IMG_DIR}')

            os.makedirs(dest_dir, exist_ok=True)
            
            dest_path = os.path.join(dest_dir, file_name)

            try:
                shutil.copy2(source_path, dest_path)
            
            except Exception as e:
                
                if DEBUG:
                    print(" [ERROR] Copy Error. ", f"Failed to copy file:\n{e}")
                pass    

        def on_file_select(event=None):
            sel = file_listbox.curselection()
            if not sel:
                return
            file_name = file_listbox.get(sel[0])
            selected_file.set(file_name)
            full_path = os.path.join(get_current_folder(), file_name)
            print(full_path)

            try:
                img = Image.open(full_path)

                preview_panel.update_idletasks()
                panel_width = preview_panel.winfo_width()
                panel_height = preview_panel.winfo_height() - 60  

                if DEBUG:
                    print(f"[DEBUG] Panel size: {panel_width}x{panel_height}")

                img_ratio = img.width / img.height
                panel_ratio = panel_width / panel_height

                if img_ratio > panel_ratio:
                    new_width = panel_width
                    new_height = int(panel_width / img_ratio)
                else:
                    new_height = panel_height
                    new_width = int(panel_height * img_ratio)

                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)

                image_preview_label.config(image=photo, text="")
                image_preview_label.image = photo
            except Exception as e:
                if DEBUG:
                    print("Error", f"Could not load image:\n{e}")
                else:
                    pass
        context_menu = tk.Menu(file_listbox, tearoff=0)
        context_menu.add_command(label = prepare_text_for_widget(_("Copy to system folder")), command=lambda: copy_to_system())

        def show_context_menu(event):
            if selected_source.get() == "storage":
               
                widget = event.widget
                index = widget.nearest(event.y)
                if index >= 0:
                    widget.selection_clear(0, tk.END)
                    widget.selection_set(index)
                    file_listbox.event_generate("<<ListboxSelect>>")
                    context_menu.tk_popup(event.x_root, event.y_root)    

              # ПКМ        
        file_listbox.bind("<Button-3>", show_context_menu)
        file_listbox.bind("<<ListboxSelect>>", on_file_select)
        preview_panel.bind("<Configure>", lambda e: on_file_select())

        pages["file"] = file_page
        populate_file_list()

        file_page.pack(fill="both", expand=True)

       
        populate_file_list(mode=selected_source.get(), img_type=selected_category.get())


    def exit_to_os():
        parent.withdraw()
        admin_window.destroy()
        state.win.quit()
        state.win.destroy()
        

    # Sidebar buttons
    tk.Button(sidebar, text = prepare_text_for_widget(_("Edit Mode")), width=18, command=on_close).pack(pady=5)
    tk.Button(sidebar, text = prepare_text_for_widget(_("Security")), width=18, command=lambda: show_page("security")).pack(pady=5)
    if g_auth.current_user == 'Master':
        tk.Button(sidebar, text = prepare_text_for_widget(_("System Info")), width=18, command=lambda: show_page("system")).pack(pady=5)
        tk.Button(sidebar, text = prepare_text_for_widget(_("Organization")), width=18, command=lambda: show_page("organization")).pack(pady=5)
        tk.Button(sidebar, text = prepare_text_for_widget(_("File Management")), width=18, command=lambda: show_page("file")).pack(pady=5)
        tk.Button(
        sidebar,
        text=prepare_text_for_widget(_("Block Communications")),
        width=18,
        command=lambda: (
            block_communications(),
            setattr(state, 'c_block', True)
                    )
                ).pack(pady=5)

        tk.Button(
            sidebar,
            text=prepare_text_for_widget(_("Unblock Communications")),
            width=18,
            command=lambda: (
                unblock_communications(),
                setattr(state, 'c_block', False)
            )
        ).pack(pady=5)

        tk.Button(
                sidebar,
                text=prepare_text_for_widget(_("Fullscreen Mode")),
                width=18,
                command=lambda: (
                    state.win.attributes('-fullscreen', True),
                    setattr(state,'fullscreen_mode', True),
                    setattr(state,'fullscreen_signal', True),
                    state.bg_canvas.update_idletasks(),
                    state.win.after(500, lambda: import_canvas_from_json(
                        state.bg_canvas,
                        state.current_mode,
                        True
                    ))
                )
            ).pack(pady=5)


        exit_fullscreen_btn = tk.Button(
            sidebar,
            text=prepare_text_for_widget(_("Exit Fullscreen")),
            width=18,
            command=lambda: (
                state.win.attributes('-fullscreen', False),
                setattr(state,'fullscreen_mode', False),
                setattr(state,'fullscreen_signal', False),
                state.bg_canvas.update_idletasks(),
                    state.win.after(500, lambda: import_canvas_from_json(
                        state.bg_canvas,
                        state.current_mode,
                        True)
            ))
                
        ).pack(pady=5)

        tk.Button(sidebar, text = prepare_text_for_widget(_("Exit to OS")), width=18, command=lambda: exit_to_os()).pack(side="bottom", pady=10)

    show_page("security")
    admin_window.protocol("WM_DELETE_WINDOW", on_close)
    password_entry.bind('<Return>', lambda event: validate_password())
    access_code_entry.bind('<Return>', lambda event: validate_access_code())
    if g_auth.current_user == 'User':
        '''tk.Button(
            sidebar,
            text=prepare_text_for_widget(_("Save and adapt resolution")),
            width=18,
            command=lambda: (export_canvas_to_json(state.bg_canvas, True,None, True), config_screen_load(), import_canvas_from_json(state.bg_canvas, state.current_mode))
        ).pack(pady=5)'''
