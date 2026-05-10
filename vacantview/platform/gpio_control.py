import lgpio
from gpiozero import Button as GPIOButton
from signal import pause
import time
import tkinter as tk
import os

from tkinter import *

from vacantview.core.state import state
from vacantview.platform import sensor_read

from vacantview.config.config import BUTTON_PIN, BUTTON_PIN_2, INPUT_PIN_MEN, INPUT_PIN_WOMEN

from threading import Timer

# Open GPIO chip 0
state.h = lgpio.gpiochip_open(0)

# Claim input pins with pull-up resistors
lgpio.gpio_claim_input(state.h, INPUT_PIN_MEN, lgpio.SET_PULL_UP)
lgpio.gpio_claim_input(state.h, INPUT_PIN_WOMEN, lgpio.SET_PULL_UP)

# Initialize buttons with pull-up and debounce
button_1 = GPIOButton(BUTTON_PIN, pull_up=True, bounce_time=0.05)
button_2 = GPIOButton(BUTTON_PIN_2, pull_up=True, bounce_time=0.05)

def init():
    # Read initial states of men and women input pins
    men = lgpio.gpio_read(state.h, INPUT_PIN_MEN)
    women = lgpio.gpio_read(state.h, INPUT_PIN_WOMEN)

    # Set int_COUNT based on input pin states
    if men == 0 and women == 1:
        state.int_COUNT = 0
    elif men == 1 and women == 0:
        state.int_COUNT = 1
    elif men == 0 and women == 0:
        state.int_COUNT = 2
    elif men == 1 and women == 1:
        state.int_COUNT = 3

    # Update UI state string accordingly
    
    state.string_genderSelect.set(state.BackGrounds[state.int_COUNT])

def make_callback(gpio_name, handler_func, button_name):
    last_tick = [0]

    def callback():
        tick = time.time()
        # Prevent multiple triggers within 0.1 seconds
        if tick - last_tick[0] > 0.1:
            handler_func(button_name)
            last_tick[0] = tick

    return callback

def start_cleaning_mode(button_name):
    print(f"Starting 30-minute cleaning mode for {button_name}.")
    state.button_states[button_name]['active'] = True
    state.button_states[button_name]['permanent'] = False
    
    if button_name == 'button_1':
        sensor_read.handle_interrupt(BUTTON_PIN)
    else:
        sensor_read.handle_interrupt_add(BUTTON_PIN_2)
    
    timer = Timer(30 * 60, stop_cleaning_mode, args=[button_name])
    state.button_states[button_name]['timer'] = timer
    timer.start()
   
def stop_cleaning_mode(button_name):
    print(f"Stopping cleaning mode for {button_name}.")
    btn_state = state.button_states[button_name]
    
    if btn_state['timer']:
        btn_state['timer'].cancel()
        btn_state['timer'] = None
    
    btn_state['active'] = False
    btn_state['permanent'] = False
    
    if button_name == 'button_1':
        sensor_read.handle_interrupt(BUTTON_PIN)
    else:
        sensor_read.handle_interrupt_add(BUTTON_PIN_2)


def start_permanent_mode(button_name):
    print(f"Permanent cleaning mode activated for {button_name}.")
    
    if button_name == 'button_1':
        sensor_read.handle_interrupt(BUTTON_PIN)
    else:
        sensor_read.handle_interrupt_add(BUTTON_PIN_2)
        
    btn_state = state.button_states[button_name]
    btn_state['active'] = True
    btn_state['permanent'] = True
    if btn_state['timer']:
        btn_state['timer'].cancel()
        btn_state['timer'] = None

def setup_gpio_interrupt():
    def on_press(button_name):
        # Record the time when button is pressed
        state.button_press_time = time.time()

    def on_release(button_name):
        duration = time.time() - state.button_press_time
        print(f"{button_name} held for {duration:.2f} seconds.")

        btn_state = state.button_states[button_name]

        if duration >= 10:
        
            start_permanent_mode(button_name)
        else:

            if btn_state['permanent']:
                stop_cleaning_mode(button_name)
            elif btn_state['active']:
                stop_cleaning_mode(button_name)
            else:
                start_cleaning_mode(button_name)

    # Assign callbacks to button press and release events
    button_1.when_pressed = make_callback('button_1 press', on_press, 'button_1')
    button_1.when_released = make_callback('button_1 release', on_release, 'button_1')
    
    button_2.when_pressed = make_callback('button_2 press', on_press, 'button_2')
    button_2.when_released = make_callback('button_2 release', on_release, 'button_2')
