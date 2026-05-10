import tkinter as tk
from tkinter import messagebox
import subprocess
import time

def run_command(command, timeout=30):
    try:
        result = subprocess.run(command, shell=True, check=True, 
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                timeout=timeout, text=True)
      
    except subprocess.TimeoutExpired:
        print(f' {timeout} breaked.')
    except subprocess.CalledProcessError as e:
        print(f"Error {command} :\n{e.stderr}")

def block_communications():
    
    run_command("sudo rfkill block wifi")
    run_command("sudo rfkill block bluetooth")
    run_command("sudo ifconfig wlan0 down")
    run_command("sudo ifconfig eth0 down")

    

def unblock_communications():
    
    run_command("sudo rfkill unblock wifi")
    run_command("sudo rfkill unblock bluetooth")
    run_command("sudo ifconfig wlan0 up")
    run_command("sudo ifconfig eth0 up")