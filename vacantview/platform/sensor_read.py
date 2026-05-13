import serial
import threading
import time
import os

from vacantview.core.state import state
from vacantview.ui.gui_elements import CE

update_elements = CE()

# How often to send a broadcast poll request to all nodes (seconds)
POLL_INTERVAL = 5

_stop_event = threading.Event()


# ---------------------------------------------------------------------------
# Outgoing request
# ---------------------------------------------------------------------------

def get_data():
    cmd = '*AT+NODE_MSG,FFFF,@ST;##'
    for ser in (state.ser1, state.ser2):
        if ser and ser.is_open:
            try:
                ser.write(cmd.encode())
            except Exception as e:
                print(f"[UART] send error: {e}")


# ---------------------------------------------------------------------------
# Background reader threads — one per serial port
# ---------------------------------------------------------------------------

def _reader_thread(get_ser, process_fn, port_label):
    """
    Continuously read from a serial port in a background thread.
    Maintains a buffer so messages are never split across reads.
    Parses every complete message ending with '##'.
    """
    buf = ""
    while not _stop_event.is_set():
        ser = get_ser()
        if not ser or not ser.is_open:
            time.sleep(0.5)
            continue
        try:
            waiting = ser.in_waiting
            if waiting:
                chunk = ser.read(waiting).decode('utf-8', errors='ignore')
                buf += chunk
                # Extract all complete messages (delimited by ##)
                while '##' in buf:
                    msg, buf = buf.split('##', 1)
                    msg = msg.strip()
                    if 'AT+NODE' in msg:
                        try:
                            process_fn(msg)
                        except Exception as e:
                            print(f"[UART] parse error on {port_label}: {e}")
            else:
                time.sleep(0.02)
        except serial.SerialException as e:
            print(f"[UART] {port_label} serial error: {e}")
            buf = ""
            time.sleep(1)
        except Exception as e:
            print(f"[UART] {port_label} unexpected error: {e}")
            buf = ""
            time.sleep(0.5)


def _poll_thread():
    """Periodically broadcast a data request so nodes keep responding."""
    while not _stop_event.is_set():
        get_data()
        time.sleep(POLL_INTERVAL)


# ---------------------------------------------------------------------------
# Message parsers
# ---------------------------------------------------------------------------

def process_node_data_men(words):
    index = words.index('AT+NODE')
    address = words[index+13: index+16]
    if address not in state.addresses_string:
        state.addresses_string.append(address)
    if words[index+8: index+11] == 'MSG':
        if words[index+17: index+21] == '*ST-':
            state.OccupiedCounter_string[address] = '0' if words[index+21] == '1' else '1'
        elif words[index+17: index+21] == '*AS-':
            state.OccupiedCounter_string_MEN_acc[address] = '0' if words[index+21] == '1' else '1'


def process_node_data_women(words):
    index = words.index('AT+NODE')
    address = words[index+13: index+16]
    if address not in state.addresses_string_WOMEN:
        state.addresses_string_WOMEN.append(address)
    if words[index+8: index+11] == 'MSG':
        if words[index+17: index+21] == '*ST-':
            state.OccupiedCounter_string_WOMEN[address] = '0' if words[index+21] == '1' else '1'
        elif words[index+17: index+21] == '*AS-':
            state.OccupiedCounter_string_WOMEN_acc[address] = '0' if words[index+21] == '1' else '1'


# ---------------------------------------------------------------------------
# UI update — runs in tkinter main thread via after()
# ---------------------------------------------------------------------------

def _wait_for_attrs(attrs, timeout=1.0):
    start = time.time()
    while not all(hasattr(state, a) for a in attrs):
        if time.time() - start > timeout:
            return False
        time.sleep(0.05)
    return True


def _update_men_ui():
    total = len(state.addresses_string)
    state.bg_canvas.itemconfigure('Cubiculs_MEN', text=str(total))

    free_acc = sum(1 for v in state.OccupiedCounter_string_MEN_acc.values() if v == '0')
    occup_acc = sum(1 for v in state.OccupiedCounter_string_MEN_acc.values() if v == '1')
    free = sum(1 for v in state.OccupiedCounter_string.values() if v == '0') + free_acc
    occupied = total - free

    if state.clean_mode_button_1:
        occup_acc += free_acc
        occupied = total
        free = 0
        free_acc = 0

    if not state.no_uart and _wait_for_attrs(['graph_M_GREEN', 'graph_M_RED']):
        _draw_indicators('graph_M_GREEN', 'graph_M_RED', free, occupied, total)
        state.bg_canvas.itemconfigure('accessible_vacant_indicator_men', text=str(free_acc))
        state.bg_canvas.itemconfigure('accessible_occup_indicator_men', text=str(occup_acc))


def _update_women_ui():
    total = len(state.addresses_string_WOMEN)
    state.bg_canvas.itemconfigure('Cubiculs_WOMEN', text=str(total))

    free_acc = sum(1 for v in state.OccupiedCounter_string_WOMEN_acc.values() if v == '0')
    occup_acc = sum(1 for v in state.OccupiedCounter_string_WOMEN_acc.values() if v == '1')
    free = sum(1 for v in state.OccupiedCounter_string_WOMEN.values() if v == '0') + free_acc
    occupied = total - free

    if state.clean_mode_button_2:
        occup_acc += free_acc
        occupied = total
        free = 0
        free_acc = 0

    if not state.no_uart and _wait_for_attrs(['graph_w_GREEN', 'graph_w_RED']):
        _draw_indicators('graph_w_GREEN', 'graph_w_RED', free, occupied, total)
        state.bg_canvas.itemconfigure('accessible_vacant_indicator_women', text=str(free_acc))
        state.bg_canvas.itemconfigure('accessible_occup_indicator_women', text=str(occup_acc))


def _draw_indicators(tag_green, tag_red, free, occupied, total):
    g = getattr(state, tag_green)
    r = getattr(state, tag_red)
    t = state.indicator_type
    if t == 'circle':
        update_elements.update_ring_data(g, free, total, tag_green)
        update_elements.update_ring_data(r, occupied, total, tag_red)
    elif t == 'square':
        update_elements.update_rect_data(g, free, total, tag_green)
        update_elements.update_rect_data(r, occupied, total, tag_red)
    else:
        update_elements.update_rounded_data(g, free, total, tag_green)
        update_elements.update_rounded_data(r, occupied, total, tag_red)


def read_all_data():
    """Called in the tkinter main thread every 200ms to refresh the UI."""
    if state.flag_monitor_thread:
        return
    try:
        mode = state.string_genderSelect.get()
        if mode in ('MEN', 'BOTH'):
            _update_men_ui()
        if mode in ('WOMEN', 'BOTH'):
            _update_women_ui()
    except Exception as e:
        print(f"[UI] update error: {e}")
    state.win.after(200, read_all_data)


# ---------------------------------------------------------------------------
# Start / stop
# ---------------------------------------------------------------------------

def start_reader_threads():
    """Launch background threads for serial reading and periodic polling."""
    _stop_event.clear()

    threading.Thread(
        target=_reader_thread,
        args=(lambda: state.ser1, process_node_data_men, 'ser1'),
        daemon=True, name='uart-men'
    ).start()

    threading.Thread(
        target=_reader_thread,
        args=(lambda: state.ser2, process_node_data_women, 'ser2'),
        daemon=True, name='uart-women'
    ).start()

    threading.Thread(
        target=_poll_thread,
        daemon=True, name='uart-poll'
    ).start()

    print("[UART] Reader threads started.")


def stop_reader_threads():
    _stop_event.set()


# ---------------------------------------------------------------------------
# Cleaning mode button handlers (unchanged logic)
# ---------------------------------------------------------------------------

def _toggle_cleaning(btn_num, clean_attr, msg1_tag, msg2_tag, msg1_add_tag, msg2_add_tag, mode_check):
    is_both = state.string_genderSelect.get() not in ('MEN', 'WOMEN')
    current = getattr(state, clean_attr)
    new_val = not current
    setattr(state, clean_attr, new_val)

    def _set(tag, visible):
        try:
            state.bg_canvas.itemconfigure(tag, state='normal' if visible else 'hidden')
        except Exception:
            pass

    _set(msg1_tag, new_val)
    if state.custom_title:
        _set(msg1_add_tag, new_val)
    if is_both:
        _set(msg2_tag, new_val)
        if state.custom_title:
            _set(msg2_add_tag, new_val)


def handle_interrupt(channel):
    _toggle_cleaning(
        1, 'clean_mode_button_1',
        'cleaning_message_1', 'cleaning_message_2',
        'cleaning_message_1_add', 'cleaning_message_2_add',
        'button_1'
    )


def handle_interrupt_add(channel):
    _toggle_cleaning(
        2, 'clean_mode_button_2',
        'cleaning_message_2', 'cleaning_message_1',
        'cleaning_message_2_add', 'cleaning_message_1_add',
        'button_2'
    )
