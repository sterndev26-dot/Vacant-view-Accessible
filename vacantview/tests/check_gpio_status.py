import os
import subprocess
import sys
import shutil
from dotenv import load_dotenv
load_dotenv()

DEBUG = os.getenv("DEBUG").lower() in ("true",1)

def check_raspi_gpio():
    if shutil.which("raspi-gpio") is None:
        if DEBUG:
            print("'raspi-gpio' command not found. You can install it with:")
            print("  sudo apt install raspi-gpio")
        return False
    if DEBUG:
        print("'raspi-gpio' command is available.\n")
    result = subprocess.run(["raspi-gpio", "get"], capture_output=True, text=True)
    if DEBUG:
        print("GPIO status (partial):")
        print("\n".join(result.stdout.strip().splitlines()) + "\n...")
    return True

def check_gpio_group():
    groups = subprocess.check_output(["groups"], text=True).strip().split()
    if "gpio" in groups:
        if DEBUG:
            print("User is a member of the 'gpio' group.")
    else:
        if DEBUG:
            print("User is NOT a member of the 'gpio' group.")
            print("Add the user to the group with:\n   sudo usermod -aG gpio $USER\n   then reboot.")
        return False
    return True

def check_gpiochip_permissions():
    if not os.path.exists("/dev/gpiochip0"):
        if DEBUG:
            print("/dev/gpiochip0 not found. Either you're not on a Raspberry Pi, or GPIO is not enabled.")
        return False

    stat = os.stat("/dev/gpiochip0")
    gid = stat.st_gid
    group_name = subprocess.check_output(["getent", "group", str(gid)], text=True).split(":")[0]
    if group_name == "gpio":
        if DEBUG:
            print("/dev/gpiochip0 has correct group ownership (gpio).")
    else:
        if DEBUG:
            print(f"/dev/gpiochip0 belongs to a different group: {group_name}.")
    return True

def check_rpi_gpio_installed():
    try:
        import RPi.GPIO
        if DEBUG:
            print("RPi.GPIO module is installed.")
        return True
    except ImportError:
        if DEBUG:
            print("RPi.GPIO module is NOT installed.")
            print("Install it with:\n   sudo apt install python3-rpi.gpio")
        return False

def full_rpi_check():
    if DEBUG:
        print("Raspberry Pi GPIO Environment Checker\n")
    try:
        with open('/proc/device-tree/model', 'r') as f:
            model = f.read().lower()
            print("This system a Raspberry Pi.")
    except FileNotFoundError:
        print("This system does not appear to be a Raspberry Pi.")
        return False

    if not check_raspi_gpio():
        return False
    if not check_gpio_group():
        return False
    if not check_gpiochip_permissions():
        return False
    if not check_rpi_gpio_installed():
        return False
    if DEBUG:
        print("\nCheck completed.")
    return True
