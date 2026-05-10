import tkinter as tk
from tkinter import ttk
from vacantview.data.auth.auth_service import check_credentials
from vacantview.core.state import g_auth, state
from vacantview.ui.context_menu.rtl_func import prepare_text_for_widget

def show_auth_window(parent):
    
    if hasattr(parent, "auth_window") and parent.auth_window and parent.auth_window.winfo_exists():
        parent.auth_window.lift()
        parent.auth_window.focus_force()
        return
    

    auth_window = tk.Toplevel(parent)
    parent.auth_window = auth_window
    auth_window.title(prepare_text_for_widget(_("Authentication")))
    auth_window.geometry("300x200")
    auth_window.transient(parent)
    auth_window.overrideredirect(True)
    

    parent.update_idletasks()
    x = parent.winfo_rootx() + (parent.winfo_width() // 2) - 150
    y = parent.winfo_rooty() + (parent.winfo_height() // 2) - 100
    auth_window.geometry(f"+{x}+{y}")

    # Обновляем заголовок окна с помощью prepare_text_for_widget
    auth_window.after(10, lambda: auth_window.title(prepare_text_for_widget(_("Authentication"))))
    
    ttk.Label(auth_window, text=prepare_text_for_widget(_("Select Mode:"))).pack(pady=(20, 5))

    mode_var = tk.StringVar()
    mode_combo = ttk.Combobox(auth_window, textvariable=mode_var, state="readonly")
    mode_combo['values'] = ("User", "Master")
    mode_combo.current(0)
    mode_combo.pack(pady=5)

    ttk.Label(auth_window, text=prepare_text_for_widget(_("Password:"))).pack(pady=(5, 0))
    password_var = tk.StringVar()
    password_entry = ttk.Entry(auth_window, textvariable=password_var, show="*")
    password_entry.pack()
    
    status_label = ttk.Label(auth_window, text="", foreground="red")
    status_label.pack(pady=(5, 0))

    def on_login():
        selected_mode = mode_var.get()
        password = password_var.get()
        valid = check_credentials(selected_mode, password)
        if valid:
            g_auth.current_user = selected_mode
            status_label.config(text=prepare_text_for_widget(_(f"Success.")), foreground="green")
            
            auth_window.after(500, lambda: (setattr(parent, "auth_window", None), auth_window.destroy()))
        else:
            status_label.config(text=prepare_text_for_widget(_("Wrong password. Try again.")))
            password_var.set("")
            password_entry.focus_force()

    def on_close():
        if 'admin_window' in state.open_window:
            state.open_window.remove('admin_window')
        auth_window.destroy()
        
    password_entry.bind("<Return>", lambda event: on_login())
    auth_window.bind("<F5>", lambda event: on_close())
    password_entry.bind("<F5>", lambda event: on_close())

    ttk.Button(auth_window, text=prepare_text_for_widget(_("Login")), command=on_login).pack(pady=15)

    # Убедимся, что окно будет подниматься и фокусироваться после того как оно завершит отрисовку
    auth_window.after(10, lambda: parent.wait_window(auth_window))  # wait_window с отложенной инициализацией
    auth_window.after(100, lambda: parent.focus_force())  # поднимаем родительское окно
    auth_window.after(100, lambda: parent.lift())  # гарантируем, что родительское окно будет поверх

    auth_window.after(100, lambda: parent.attributes("-topmost", True))  # установить родитель в верхний слой

