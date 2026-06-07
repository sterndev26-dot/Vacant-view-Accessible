import serial
import time

import vacantview.config.config as cfg
from vacantview.core.state import state
from vacantview.ui.gui_elements import CE

update_elements = CE()

# Last time each address was heard from (address → monotonic timestamp)
_last_seen = {}
_watchdog_last_check = 0.0
_initial_poll_done   = False


# ---------------------------------------------------------------------------
# Outgoing requests
# ---------------------------------------------------------------------------

def get_data():
    """Broadcast poll to all nodes (used on startup and by external callers)."""
    cmd = '*AT+NODE_MSG,FFFF,@ST;##'
    for ser in (state.ser1, state.ser2):
        if ser and ser.is_open:
            try:
                ser.write(cmd.encode())
            except Exception as e:
                print(f"[UART] broadcast error: {e}")

_poll_broadcast = get_data


def _poll_device(address, ser):
    """Targeted poll for a single silent device."""
    if not ser or not ser.is_open:
        return
    try:
        cmd = f'*AT+NODE_MSG,{address},@ST;##'
        ser.write(cmd.encode())
        print(f"[UART] watchdog poll → {address}")
    except Exception as e:
        print(f"[UART] poll error {address}: {e}")


def _watchdog_check():
    """Poll devices that haven't been heard from for WATCHDOG_TIMEOUT seconds."""
    now     = time.monotonic()
    timeout = getattr(cfg, 'WATCHDOG_TIMEOUT', 2700)
    for address in state.addresses_string:
        if now - _last_seen.get(address, 0) >= timeout:
            _poll_device(address, state.ser1)
    for address in state.addresses_string_WOMEN:
        if now - _last_seen.get(address, 0) >= timeout:
            _poll_device(address, state.ser2)


# ---------------------------------------------------------------------------
# Serial readers — called from main thread, non-blocking
# ---------------------------------------------------------------------------

def _read_port(ser, process_fn, label):
    if not ser or not ser.is_open:
        return
    try:
        waiting = ser.in_waiting
        if not waiting:
            return
        received = ser.read(waiting).decode('utf-8', errors='ignore')
        for msg in received.split('##'):
            if 'AT+NODE' in msg:
                try:
                    process_fn(msg)
                except Exception as e:
                    print(f"[UART] {label} parse error: {e}")
    except serial.SerialException as e:
        print(f"[UART] {label} serial error: {e}")
    except Exception as e:
        print(f"[UART] {label} error: {e}")


# ---------------------------------------------------------------------------
# Message parsers
# ---------------------------------------------------------------------------

def _parse_node_msg(msg):
    """
    Parse AT+NODE_MSG message into (address, type, status).
    Handles any prefix (*, + or none) and any address length.
    Format: [*]AT+NODE_MSG,<address>,<*ST-|*AS-><0|1>
    Returns (address, type_str, status_char) or None if invalid.
    """
    try:
        parts = msg.split(',')
        if len(parts) < 3 or 'AT+NODE' not in parts[0]:
            return None
        address = parts[1].strip()
        if not address or address.upper() in ('FFFF', 'FFF'):
            return None
        type_val = parts[2].strip()
        if len(type_val) < 5:
            return None
        type_str = type_val[:4]    # '*ST-' or '*AS-'
        status    = type_val[4]    # '0' or '1'
        return address, type_str, status
    except Exception:
        return None


def process_node_data_men(msg):
    result = _parse_node_msg(msg)
    if result is None:
        return
    address, type_str, status = result
    _last_seen[address] = time.monotonic()
    if address not in state.addresses_string:
        state.addresses_string.append(address)
    if type_str == '*ST-':
        state.OccupiedCounter_string[address] = '0' if status == '1' else '1'
    elif type_str == '*AS-':
        state.OccupiedCounter_string_MEN_acc[address] = '0' if status == '1' else '1'


def process_node_data_women(msg):
    result = _parse_node_msg(msg)
    if result is None:
        return
    address, type_str, status = result
    _last_seen[address] = time.monotonic()
    if address not in state.addresses_string_WOMEN:
        state.addresses_string_WOMEN.append(address)
    if type_str == '*ST-':
        state.OccupiedCounter_string_WOMEN[address] = '0' if status == '1' else '1'
    elif type_str == '*AS-':
        state.OccupiedCounter_string_WOMEN_acc[address] = '0' if status == '1' else '1'


# ---------------------------------------------------------------------------
# UI update helpers — all run in tkinter main thread
# ---------------------------------------------------------------------------

def _update_men_ui():
    total = len(state.addresses_string)
    state.bg_canvas.itemconfigure('Cubiculs_MEN', text=str(total))

    free_acc  = sum(1 for v in state.OccupiedCounter_string_MEN_acc.values() if v == '0')
    occup_acc = sum(1 for v in state.OccupiedCounter_string_MEN_acc.values() if v == '1')
    free      = sum(1 for v in state.OccupiedCounter_string.values() if v == '0') + free_acc
    occupied  = total - free

    if state.clean_mode_button_1:
        occup_acc += free_acc
        occupied = total
        free = 0
        free_acc = 0

    if not state.no_uart and hasattr(state, 'graph_M_GREEN') and hasattr(state, 'graph_M_RED'):
        _draw_indicators('graph_M_GREEN', 'graph_M_RED', free, occupied, total)
        state.bg_canvas.itemconfigure('accessible_vacant_indicator_men', text=str(free_acc))
        state.bg_canvas.itemconfigure('accessible_occup_indicator_men', text=str(occup_acc))


def _update_women_ui():
    total = len(state.addresses_string_WOMEN)
    state.bg_canvas.itemconfigure('Cubiculs_WOMEN', text=str(total))

    free_acc  = sum(1 for v in state.OccupiedCounter_string_WOMEN_acc.values() if v == '0')
    occup_acc = sum(1 for v in state.OccupiedCounter_string_WOMEN_acc.values() if v == '1')
    free      = sum(1 for v in state.OccupiedCounter_string_WOMEN.values() if v == '0') + free_acc
    occupied  = total - free

    if state.clean_mode_button_2:
        occup_acc += free_acc
        occupied = total
        free = 0
        free_acc = 0

    if not state.no_uart and hasattr(state, 'graph_w_GREEN') and hasattr(state, 'graph_w_RED'):
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


# ---------------------------------------------------------------------------
# Main loop — runs in tkinter main thread every 200ms
# ---------------------------------------------------------------------------

def read_all_data():
    """
    Listen for incoming UART messages and update UI every 200ms.
    No constant polling — nodes send updates proactively.
    Watchdog polls silent devices after WATCHDOG_TIMEOUT seconds.
    """
    global _initial_poll_done, _watchdog_last_check
    if state.flag_monitor_thread:
        return
    try:
        # Single broadcast on startup to wake all nodes
        if not _initial_poll_done:
            _poll_broadcast()
            _initial_poll_done = True

        # Read incoming messages from both ports
        _read_port(state.ser1, process_node_data_men,   'MEN')
        _read_port(state.ser2, process_node_data_women, 'WOMEN')

        # Watchdog: check every 60s, poll silent devices
        now = time.monotonic()
        if now - _watchdog_last_check >= 60:
            _watchdog_last_check = now
            _watchdog_check()

        # Update UI for the selected mode
        mode = state.string_genderSelect.get()
        if mode in ('MEN', 'BOTH'):
            _update_men_ui()
        if mode in ('WOMEN', 'BOTH'):
            _update_women_ui()
    except Exception as e:
        print(f"[UI] update error: {e}")

    state.win.after(200, read_all_data)


# ---------------------------------------------------------------------------
# Start / stop (stubs — reading happens in main thread via read_all_data)
# ---------------------------------------------------------------------------

def start_reader_threads():
    pass


def stop_reader_threads():
    pass


# ---------------------------------------------------------------------------
# Cleaning mode button handlers
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
