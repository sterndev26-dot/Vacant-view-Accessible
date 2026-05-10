import tkinter as tk

from vacantview.data.auth.auth_service import check_pin
from vacantview.core.state import state, g_auth
from vacantview.admin.utils.user_editor import open_admin_settings
from vacantview.config.config import DEBUG
from vacantview.ui.context_menu.rtl_func import prepare_text_for_widget

def open_pin_window(parent):
    if 'admin_window' in state.open_window:
        if DEBUG:
            print("Admin window is open. Cannot open PIN window.")
        return

    pin_window = tk.Toplevel(parent)
    pin_window.title(prepare_text_for_widget(_("Enter PIN")))
    pin_window.resizable(False, False)
    pin_window.overrideredirect(True)

    win_width, win_height = 250, 180
    canvas = state.bg_canvas
    canvas.update_idletasks()  

    canvas_x = canvas.winfo_rootx()
    canvas_y = canvas.winfo_rooty()
    canvas_width = canvas.winfo_width()
    canvas_height = canvas.winfo_height()

    x = canvas_x + (canvas_width - win_width) // 2
    y = canvas_y + (canvas_height - win_height) // 2

    pin_window.geometry(f"{win_width}x{win_height}+{x}+{y}")
    pin_window.attributes("-topmost", True)

    pin_window.grab_set()
    pin_window.focus_force()

    label = tk.Label(pin_window, text = prepare_text_for_widget(_("Enter PIN code:")))
    label.pack(pady=10)

    pin_var = tk.StringVar()

    msg_label = tk.Label(pin_window, text="", fg="red")
    msg_label.pack(pady=5)

    def clear_message():
        msg_label.config(text="", fg="red")

    def on_close():
        pin_window.destroy()

    def check_user_pin():
        pin = pin_var.get()

        if pin.isdigit() and len(pin) == 4:
            valid = check_pin(g_auth.current_user, pin)
            if valid:
                msg_label.config(text = prepare_text_for_widget(_("PIN accepted")), fg="green")
                open_admin_settings(state.win)
                pin_window.after(500, pin_window.destroy)
            else:
                msg_label.config(text = prepare_text_for_widget(_("Invalid PIN.")), fg="red")
                pin_window.after(1500, clear_message)
                pin_var.set("")
                pin_entry.focus()
        else:
            msg_label.config(text = prepare_text_for_widget(_("Invalid PIN. Enter 4 digits.")), fg="red")
            pin_window.after(1000, clear_message)
            pin_var.set("")
            pin_entry.focus()

    def on_pin_change(*args):
        value = pin_var.get()

        if not value.isdigit():
            pin_var.set(''.join(filter(str.isdigit, value)))
        elif len(value) > 4:
            pin_var.set(value[:4])
        elif len(value) == 4:
            check_user_pin()

    pin_var.trace_add('write', on_pin_change)

    def validate_pin(new_value):
        return new_value.isdigit() and len(new_value) <= 4

    vcmd = (pin_window.register(validate_pin), '%P')

    pin_entry = tk.Entry(
        pin_window,
        textvariable=pin_var,
        show="*",
        font=("Arial", 14),
        justify="center",
        validate="key",
        validatecommand=vcmd
    )
    pin_entry.pack(pady=5)
    pin_entry.focus()

    def enforce_focus():
        try:
            pin_window.lift()
            pin_window.focus_force()
            pin_entry.focus_force()
        except:
            pass
        if pin_window.winfo_exists():
            pin_window.after(500, enforce_focus)

    enforce_focus()
    pin_entry.bind("<Escape>", lambda event: on_close())
    pin_window.bind("<Escape>", lambda event: on_close())
    pin_entry.bind("<Button-1>", lambda event: pin_entry.focus_force())
    pin_window.bind("<Button-1>", lambda event: pin_window.focus_force())
