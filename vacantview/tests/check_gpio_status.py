import os
import subprocess
from dotenv import load_dotenv
load_dotenv()

DEBUG = os.getenv("DEBUG", "false").lower() in ("true", "1")

GPIOCHIP_CANDIDATES = [
    "/dev/gpiochip0",
    "/dev/gpiochip4",  # Raspberry Pi 5
]

def check_gpio_group():
    try:
        groups = subprocess.check_output(["groups"], text=True).strip().split()
    except Exception:
        return True  # can't determine — don't block startup
    if "gpio" in groups:
        if DEBUG:
            print("User is a member of the 'gpio' group.")
        return True
    if DEBUG:
        print("User is NOT a member of the 'gpio' group.")
        print("Add with: sudo usermod -aG gpio $USER  then reboot.")
    return False

def check_gpiochip_permissions():
    for chip in GPIOCHIP_CANDIDATES:
        if os.path.exists(chip):
            if DEBUG:
                print(f"{chip} found.")
            return True
    if DEBUG:
        print("No gpiochip device found. GPIO may not be enabled.")
    return False

def full_rpi_check():
    if DEBUG:
        print("Raspberry Pi GPIO Environment Checker\n")
    try:
        with open('/proc/device-tree/model', 'r') as f:
            print("This system a Raspberry Pi.")
    except FileNotFoundError:
        print("This system does not appear to be a Raspberry Pi.")
        return False

    if not check_gpio_group():
        return False
    if not check_gpiochip_permissions():
        return False
    if DEBUG:
        print("\nCheck completed.")
    return True
