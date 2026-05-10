import threading
import time
import glob
import os
import serial
import tkinter as tk


from vacantview.core.state import state
from vacantview.platform.device_manager import check_accessible_cubicles
from vacantview.ui.context_menu.context_menu import prepare_text_for_widget

from vacantview.ui.scaling import UIScaler # import our scaler module


def available_ports(tk_module):
    result = {"success": False}
    DEBUG = os.getenv("DEBUG", "false").lower() in ("true", "1")
    uart0 = os.getenv("UART_PORT0")
    uart1 = os.getenv("UART_PORT1")
    uart2 = os.getenv("UART_PORT2")

    splash = tk_module.Tk()
    splash.title("Startup")
    splash.configure(bg="blue")
    splash.attributes("-fullscreen", True)

    # Create scaler and apply window scaling
    scaler = UIScaler(splash)
    win_width, win_height = scaler.scale_window(0.4, 0.25)

    frame = tk_module.Frame(splash, bg="blue")
    scaler.place_frame_center(frame, relwidth=0.9, relheight=0.8)

    # Scale font size based on window height
    font_size = scaler.scale_font_size(win_height, factor=0.15, min_size=12)

    label = tk_module.Label(
        frame,
        text=prepare_text_for_widget(_("Initializing devices...\nPlease wait")),
        fg="yellow",
        bg="blue",
        font=("Arial", font_size, "bold")
    )
    label.pack(expand=True, fill='both')

    def disable_event():
        pass

    splash.protocol("WM_DELETE_WINDOW", disable_event)

    def force_focus(event=None):
        splash.focus_force()
        splash.attributes("-topmost", True)

    splash.bind("<FocusOut>", force_focus)
    splash.after(500, force_focus)

    def check_ports():
        uart_ports = glob.glob('/dev/ttyAMA*') + glob.glob('/dev/ttyS*')

        if DEBUG:
            print("Available UART ports:", uart_ports)

        try:
            if uart1 and uart2 and uart1 in uart_ports and uart2 in uart_ports:
                state.ser1 = serial.Serial(uart1, 115200)
                state.ser2 = serial.Serial(uart2, 115200)
                time.sleep(5)
                state.is_accessible = check_accessible_cubicles(state.ser1, state.ser2)
                result["success"] = True
            elif uart0 and uart1 and uart0 in uart_ports and uart1 in uart_ports:
                state.ser1 = serial.Serial(uart0, 115200)
                state.ser2 = serial.Serial(uart1, 115200)
                time.sleep(5)
                state.is_accessible = check_accessible_cubicles(state.ser1, state.ser2)
                result["success"] = True
            else:
                if DEBUG:
                    print(f"Required UART ports {uart1}, {uart2} not both available.")
        except Exception as e:
            if DEBUG:
                print(f"[UART ERROR]: {e}")
        finally:
            splash.after(0, splash.quit)

    threading.Thread(target=check_ports, daemon=True).start()

    splash.mainloop()
    splash.destroy()

    return result["success"]
