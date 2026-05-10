import serial
import threading
import tkinter as tk
import time

from vacantview.core.state import state
from vacantview.ui.gui_elements import CE

#from .device_manager import parse_devices_from_received
from tkinter import *

update_elements = CE()

def get_data():
    string_data = '*AT+NODE_MSG,FFFF,@ST;##'
    # Send data request command to both serial ports if available
    if state.ser1:
        state.ser1.write(string_data.encode())
    if state.ser2:
        state.ser2.write(string_data.encode())
    # Schedule repeated calls can be handled outside this function

def wait_for_attributes(state, attributes, timeout=1.0, check_interval=0.1):
    start_time = time.time()
    while True:
        # Check if all attributes exist on state
        if all(hasattr(state, attr) for attr in attributes):
            return True
        if time.time() - start_time > timeout:
            print(f"[ERROR] Timeout waiting for attributes: {attributes}")
            return False
        time.sleep(check_interval)

def read_data_MEN():
    # Initialize total space if empty
    if not state.string_TotalSpace.get():
        state.string_TotalSpace.set('0')

    if state.ser1 and state.ser1.in_waiting:
        try:
            # Read all available bytes from serial port 1
            received_data = state.ser1.read(state.ser1.in_waiting).decode('utf-8')
            # Split data on message delimiter and process each chunk
            for words in received_data.split("##"):
                if 'AT+NODE' in words:
                    process_node_data_men(words)
        except (serial.SerialException, UnicodeDecodeError):
            pass

    total = len(state.addresses_string)
    # Update UI with total cubicles count
    state.bg_canvas.itemconfigure('Cubiculs_MEN', text=total)

    # Count free and occupied accessible cubicles for men
    free_Acc= sum(1 for status in state.OccupiedCounter_string_MEN_acc.values() if status == '0')
    occup_Acc = sum(1 for status in state.OccupiedCounter_string_MEN_acc.values() if status == '1')
    free = sum(1 for status in state.OccupiedCounter_string.values() if status == '0') + free_Acc
    occupied =  total - free

    # Adjust counts if cleaning mode is active
    if state.string_genderSelect.get() in ('MEN','WOMEN'):
        if state.clean_mode_button_1:
            occup_Acc = occup_Acc + free_Acc
            occupied = total
            free = 0
            free_Acc = 0
    else:
        if state.clean_mode_button_1:
            occup_Acc = occup_Acc + free_Acc
            occupied = total
            free = 0
            free_Acc = 0

    if not state.no_uart:
        # Update graphical elements if ready
        if wait_for_attributes(state, ['graph_M_GREEN', 'graph_M_RED']):
            if state.indicator_type == 'circle':
                update_elements.update_ring_data(state.graph_M_GREEN, free, total, 'graph_M_GREEN')
                update_elements.update_ring_data(state.graph_M_RED, occupied, total, 'graph_M_RED')
            elif state.indicator_type == 'square':
                update_elements.update_rect_data(state.graph_M_GREEN, free, total, 'graph_M_GREEN')
                update_elements.update_rect_data(state.graph_M_RED, occupied, total, 'graph_M_RED')
            else:
                update_elements.update_rounded_data(state.graph_M_GREEN, free, total, 'graph_M_GREEN')
                update_elements.update_rounded_data(state.graph_M_RED, occupied, total, 'graph_M_RED')
           
            # Update accessible cubicles counters on UI
            state.bg_canvas.itemconfigure('accessible_vacant_indicator_men', text=str(free_Acc))
            state.bg_canvas.itemconfigure('accessible_occup_indicator_men', text=str(occup_Acc))

def read_data_WOMEN():
    # Initialize total space if empty
    if not state.string_TotalSpace_WOMEN.get():
        state.string_TotalSpace_WOMEN.set('0')

    if state.ser2 and state.ser2.in_waiting:
        try:
            # Read all available bytes from serial port 2
            received_data = state.ser2.read(state.ser2.in_waiting).decode('utf-8')
            # Split data on message delimiter and process each chunk
            for words in received_data.split("##"):
                if 'AT+NODE' in words:
                    process_node_data_women(words)
        except (serial.SerialException, UnicodeDecodeError):
            pass

    total = len(state.addresses_string_WOMEN)
    state.bg_canvas.itemconfigure('Cubiculs_WOMEN', text=str(total))

    # Count free and occupied accessible cubicles for women
    free_Acc= sum(1 for status in state.OccupiedCounter_string_WOMEN_acc.values() if status == '0')
    occup_Acc = sum(1 for status in state.OccupiedCounter_string_WOMEN_acc.values() if status == '1')
    free = sum(1 for status in state.OccupiedCounter_string_WOMEN.values() if status == '0') + free_Acc
    occupied =  total - free

    # Adjust counts if cleaning mode is active
    if state.string_genderSelect.get() in ('MEN','WOMEN'):
        if state.clean_mode_button_1:
            occup_Acc = occup_Acc + free_Acc
            occupied = total
            free = 0
            free_Acc = 0
    else:
        if state.clean_mode_button_2:
            occup_Acc = occup_Acc + free_Acc
            occupied = total
            free = 0
            free_Acc = 0

    if not state.no_uart:
        # Update graphical elements if ready
        if wait_for_attributes(state, ['graph_w_GREEN', 'graph_w_RED']):
            if state.indicator_type == 'circle':
                update_elements.update_ring_data(state.graph_w_GREEN, free, total, 'graph_w_GREEN')
                update_elements.update_ring_data(state.graph_w_RED, occupied, total, 'graph_w_RED')
            elif state.indicator_type == 'square':
                update_elements.update_rect_data(state.graph_w_GREEN, free, total, 'graph_w_GREEN')
                update_elements.update_rect_data(state.graph_w_RED, occupied, total, 'graph_w_RED')
            else:
                update_elements.update_rounded_data(state.graph_w_GREEN, free, total, 'graph_w_GREEN')
                update_elements.update_rounded_data(state.graph_w_RED, occupied, total, 'graph_w_RED')
    
            # Update accessible cubicles counters on UI
            state.bg_canvas.itemconfigure('accessible_vacant_indicator_women', text=str(free_Acc))
            state.bg_canvas.itemconfigure('accessible_occup_indicator_women', text=str(occup_Acc))

def read_all_data():
    # Call reading functions based on selected gender view
    if state.string_genderSelect.get() == 'MEN':
        read_data_MEN()
    elif state.string_genderSelect.get() == 'WOMEN':
        read_data_WOMEN()
    elif state.string_genderSelect.get() == 'BOTH':
        read_data_MEN()
        read_data_WOMEN()

    # Schedule next call after 200 ms
    state.win.after(200, read_all_data)

def process_node_data_men(words):
    # Extract address from the message
    index = words.index('AT+NODE')
    address = words[index+13 : index+16]
    if address not in state.addresses_string:
        state.addresses_string.append(address)

    if words[index+8: index+11] == 'MSG':
        if words[index+17 : index + 21] == '*ST-':
            state.OccupiedCounter_string[address] = '0' if words[index+21] == '1' else '1'
        elif words[index+17 : index + 21] == '*AS-':
            state.OccupiedCounter_string_MEN_acc[address] = '0' if words[index+21] == '1' else '1'

def process_node_data_women(words):
    # Extract address from the message
    index = words.index('AT+NODE')
    address = words[index+13 : index+16]
    if address not in state.addresses_string_WOMEN:
        state.addresses_string_WOMEN.append(address)

    if words[index+8: index+11] == 'MSG':
        if words[index+17 : index + 21] == '*ST-':
            state.OccupiedCounter_string_WOMEN[address] = '0' if words[index+21] == '1' else '1'
        elif words[index+17 : index + 21] == '*AS-':
            state.OccupiedCounter_string_WOMEN_acc[address] = '0' if words[index+21] == '1' else '1'

def handle_interrupt(channel):
    # Toggle cleaning mode button 1 and update UI messages accordingly
    if state.string_genderSelect.get() in ('MEN','WOMEN'):
        if state.clean_mode_button_1 or state.clean_mode_button_1:
            state.bg_canvas.itemconfigure('cleaning_message_1', state='hidden')
            if state.custom_title:
                state.bg_canvas.itemconfigure('cleaning_message_1_add', state='hidden')
            state.clean_mode_button_1 = False
        else:
            if state.custom_title:
                state.bg_canvas.itemconfigure('cleaning_message_1_add', state='normal')
            state.bg_canvas.itemconfigure('cleaning_message_1', state='normal')
            state.clean_mode_button_1 = True
    else:
        if state.clean_mode_button_1:
            if state.custom_title:
                state.bg_canvas.itemconfigure('cleaning_message_1_add', state='hidden')
            state.bg_canvas.itemconfigure('cleaning_message_1', state='hidden')
            state.clean_mode_button_1 = False
        else:
            if state.custom_title:
                state.bg_canvas.itemconfigure('cleaning_message_1_add', state='normal')
            state.bg_canvas.itemconfigure('cleaning_message_1', state='normal')
            state.clean_mode_button_1 = True

def handle_interrupt_add(channel):
    # Toggle cleaning mode button 2 and update UI messages accordingly
    if state.string_genderSelect.get() in ('MEN','WOMEN'):
        if state.clean_mode_button_1:
            if state.custom_title:
                state.bg_canvas.itemconfigure('cleaning_message_1_add', state='hidden')
            state.bg_canvas.itemconfigure('cleaning_message_1', state='hidden')
            state.clean_mode_button_1 = False
        else:
            if state.custom_title:
                state.bg_canvas.itemconfigure('cleaning_message_1_add', state='normal')
            state.bg_canvas.itemconfigure('cleaning_message_1', state='normal')
            state.clean_mode_button_1 = True    
    else:
        if state.clean_mode_button_2:
            if state.custom_title:
                state.bg_canvas.itemconfigure('cleaning_message_2_add', state='hidden')
            state.bg_canvas.itemconfigure('cleaning_message_2', state='hidden')
            state.clean_mode_button_2 = False
        else:
            if state.custom_title:
                state.bg_canvas.itemconfigure('cleaning_message_2_add', state='normal')
            state.bg_canvas.itemconfigure('cleaning_message_2', state='normal')
            state.clean_mode_button_2 = True
