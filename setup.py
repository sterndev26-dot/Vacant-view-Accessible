import os
import shutil
import subprocess
import sys
from pathlib import Path
import getpass

from x11 import main_switch_to_x11, disable_sleep_lxde


# Get the username who invoked sudo or fallback to the current user
USER_NAME = os.getenv("SUDO_USER") or getpass.getuser()
# Define home directory path for that user
USER_HOME = Path(f"/home/{USER_NAME}")
# Path to user's .bashrc (not used currently, but defined)
USER_BASHRC_PATH = USER_HOME / ".bashrc"

# Path to Raspberry Pi config.txt file (system config)
CONFIG_PATH = "/boot/firmware/config.txt"
# Backup path for the original config file
BACKUP_PATH = "/boot/firmware/config_backup_uart.txt"
# Virtual environment directory path (relative to script location)
VENV_PATH = Path("./venv")
# Python requirements file with dependencies
REQUIREMENTS_FILE = "requirements.txt"
# Wrapper shell script file name
WRAPPER_PATH = "wrapper.sh"
# Name of the main Python script to run inside the wrapper
RUN_SCRIPT_NAME = "run.py"

# List of device tree overlays and settings to add to config.txt
OVERLAYS = [
    "enable_uart=1",
    "dtoverlay=uart3,txd_pin=4,rxd_pin=5",
    "dtoverlay=uart4,txd_pin=8,rxd_pin=9",
    "dtoverlay=uart5,txd_pin=12,rxd_pin=13",
    "dtoverlay=disable-bt"  # disable Bluetooth to free UART
]

# Modifications to existing config.txt parameters (key=old, value=new)
MODIFICATIONS = {
    "dtparam=audio=on": "dtparam=audio=off",
    "camera_auto_detect=1": "camera_auto_detect=0",
}

# Paths used for bashrc and absolute wrapper script
BASHRC_PATH = Path.home() / ".bashrc"
WRAPPER_ABS_PATH = str(Path.cwd() / WRAPPER_PATH)


def get_autostart_dir(user_home):
    """
    Returns the autostart directory path inside a user's config folder.
    This directory can be used for .desktop files to autostart applications.
    """
    return user_home / ".config" / "autostart"


def get_users():
    """
    Get a list of tuples (username, home_path) for relevant users:
    - The sudo user who ran the script (or current user)
    - The root user
    Only if their home directories exist.
    """
    users = []
    user_name = os.getenv("SUDO_USER") or getpass.getuser()
    user_home = Path(f"/home/{user_name}")
    if user_home.exists():
        users.append((user_name, user_home))

    root_home = Path("/root")
    if root_home.exists():
        users.append(("root", root_home))

    return users


def add_wrapper_to_autostart_profile():
    """
    Add a line to users' .profile files that starts the wrapper.sh script in the background.
    This ensures the Python script will launch on user login (both terminal and GUI).
    Avoids duplicates and checks if .profile exists.
    """
    wrapper_abs_path = Path.cwd() / WRAPPER_PATH
    wrapper_abs_path_str = str(wrapper_abs_path)
    # Оборачиваем путь в кавычки
    start_line = f'"{wrapper_abs_path_str}" &  # wrapper-demo autostart\n'

    for user_name, user_home in get_users():
        profile_path = user_home / ".profile"
        if not profile_path.exists():
            print(f".profile not found for user {user_name} at {profile_path} — skipping")
            continue

        with open(profile_path, "r") as f:
            content = f.readlines()

        # Skip if autostart line already present
        if any(wrapper_abs_path_str in line for line in content):
            print(f"wrapper.sh autostart line already exists in {profile_path} for user {user_name} — skipping")
            continue

        try:
            with open(profile_path, "a") as f:
                f.write("\n# Added by UART setup script\n")
                f.write(start_line)
            print(f"Added wrapper.sh autostart line to {profile_path} for user {user_name}")
        except Exception as e:
            print(f"Failed to add autostart line to {profile_path} for user {user_name}: {e}")



def remove_wrapper_from_autostart_profile():
    """
    Remove the wrapper.sh autostart line from all relevant users' .profile files,
    if it exists. This disables automatic startup of the wrapper script.
    """
    wrapper_abs_path = str(Path.cwd() / WRAPPER_PATH)

    for user_name, user_home in get_users():
        profile_path = user_home / ".profile"
        if not profile_path.exists():
            print(f".profile not found for user {user_name} at {profile_path} — skipping")
            continue

        try:
            with open(profile_path, "r") as f:
                lines = f.readlines()

            new_lines = []
            removed = False
            for line in lines:
                # Remove only the exact line added by this script
                if wrapper_abs_path in line and "# wrapper-demo autostart" in line:
                    removed = True
                    continue
                new_lines.append(line)

            if removed:
                with open(profile_path, "w") as f:
                    f.writelines(new_lines)
                print(f"Removed wrapper.sh autostart line from {profile_path} for user {user_name}")
            else:
                print(f"No wrapper.sh autostart line found in {profile_path} for user {user_name}")
        except Exception as e:
            print(f"Failed to remove autostart line from {profile_path} for user {user_name}: {e}")


def create_wrapper_script():
    """
    Create the wrapper.sh script that:
    - Checks that the virtual environment and run.py exist
    - Changes directory to the script's directory
    - Opens a terminal emulator
    - Activates the virtual environment
    - Runs the main Python script
    - Keeps the terminal open after the script ends
    """
    wrapper_content = f"""#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"

if [ ! -f "${{SCRIPT_DIR}}/{VENV_PATH}/bin/activate" ]; then
    echo "Virtual environment not found at ${{SCRIPT_DIR}}/{VENV_PATH}/bin/activate"
    exit 1
fi

if [ ! -f "${{SCRIPT_DIR}}/{RUN_SCRIPT_NAME}" ]; then
    echo "{RUN_SCRIPT_NAME} not found in ${{SCRIPT_DIR}}"
    exit 1
fi

cd "${{SCRIPT_DIR}}"

x-terminal-emulator -e bash -c '
    echo "Activating virtual environment...";
    source {VENV_PATH}/bin/activate;
    echo "Running {RUN_SCRIPT_NAME}...";
    python {RUN_SCRIPT_NAME};
    echo "";
    echo "Done. Staying in virtual environment.";
    exec bash
    '
"""
    try:
        with open(WRAPPER_PATH, "w") as f:
            f.write(wrapper_content)
        os.chmod(WRAPPER_PATH, 0o755)  # Make script executable
        print(f"Created and made '{WRAPPER_PATH}' executable.")
    except Exception as e:
        print(f"Failed to create '{WRAPPER_PATH}': {e}")


def make_wrapper_executable():
    """
    Ensure wrapper.sh is executable.
    """
    if os.path.exists(WRAPPER_PATH):
        os.chmod(WRAPPER_PATH, 0o755)
        print(f"Made '{WRAPPER_PATH}' executable (chmod +x).")
    else:
        print(f"Wrapper script '{WRAPPER_PATH}' not found — skipping chmod.")


def create_venv_and_install_deps():
    """
    Install system dependencies required for PyQt6 graphical support,
    create a Python virtual environment if it does not exist,
    then install Python packages from requirements.txt and PyQt6.
    """
    print("Installing system dependencies required for Qt and XCB plugins...")
    subprocess.run([
        "sudo", "apt", "update"
    ], check=True)
    subprocess.run([
        "sudo", "apt", "install", "-y",
        "libxcb-cursor0", "libxcb-xinerama0", "libxcb-xfixes0", "libxcb-icccm4",
        "libxcb-image0", "libxcb-keysyms1", "libxcb-render-util0", "libxcb-render0",
        "libxcb-shape0", "libxcb-shm0", "libxcb-sync1", "libxcb-xkb1", "libxkbcommon-x11-0",
        "libx11-xcb1", "libxrender1", "libxext6", "libxi6", "libgl1",
        "qt5-qmake", "qtbase5-dev", "alsa-utils",
        "python3-dev", "liblgpio-dev", "swig"
    ], check=True)

    print("Creating virtual environment and installing Python dependencies...")
    if not VENV_PATH.exists():
        subprocess.run([sys.executable, "-m", "venv", str(VENV_PATH)], check=True)
        print(f"Virtual environment created at {VENV_PATH}")
    else:
        print(f"Virtual environment already exists at {VENV_PATH}")

    if not os.path.exists(REQUIREMENTS_FILE):
        print(f"{REQUIREMENTS_FILE} not found. Skipping dependency installation.")
        return

    venv_pip = str(VENV_PATH / "bin" / "pip")

    subprocess.run([venv_pip, "install", "--upgrade", "pip", "setuptools", "wheel"], check=True)
    subprocess.run([venv_pip, "install", "--only-binary=:all:", "PyQt6"], check=True)
    subprocess.run([venv_pip, "install", "-r", REQUIREMENTS_FILE, "--no-deps"], check=True)
    print(f"Dependencies installed from {REQUIREMENTS_FILE} and required packages.")


def backup_config():
    """
    Backup the existing config.txt to a backup file.
    """
    if os.path.exists(CONFIG_PATH):
        shutil.copy(CONFIG_PATH, BACKUP_PATH)
        print(f"Backup created at {BACKUP_PATH}")
    else:
        print("Config file not found for backup.")


def restore_config():
    """
    Restore the config.txt from the backup if it exists.
    """
    if os.path.exists(BACKUP_PATH):
        shutil.copy(BACKUP_PATH, CONFIG_PATH)
        print(f"Restored original config from {BACKUP_PATH}")
        print("Please reboot the system to apply restored settings.")
    else:
        print("No backup file found to restore.")


def modify_config_file():
    """
    Modify config.txt by:
    - Replacing specific lines according to MODIFICATIONS dict
    - Adding overlays from OVERLAYS list if not present
    Returns True if file modified, False otherwise.
    """
    if not os.path.exists(CONFIG_PATH):
        print(f"Error: {CONFIG_PATH} not found.")
        return False

    with open(CONFIG_PATH, "r") as f:
        lines = f.read().splitlines()

    new_lines = []
    existing = set(lines)
    for line in lines:
        modified = False
        for old, new in MODIFICATIONS.items():
            if line.strip().startswith(old):
                new_lines.append(new)  # replace line
                modified = True
                break
        if not modified:
            new_lines.append(line)

    # Add overlays if missing
    for overlay in OVERLAYS:
        if overlay not in existing and overlay not in new_lines:
            new_lines.append(overlay)

    with open(CONFIG_PATH, "w") as f:
        f.write("\n".join(new_lines) + "\n")

    print(f"{CONFIG_PATH} successfully modified.")
    return True


def enable_serial_port_interface():
    """
    Enable UART serial port and disable serial console via raspi-config CLI.
    """
    try:
        subprocess.run(
            ["raspi-config", "nonint", "do_serial", "2"],
            check=True
        )
        print("Serial port enabled and serial console disabled.")
    except subprocess.CalledProcessError:
        print("Failed to set serial port interface via raspi-config.")


def prompt_reboot():
    """
    Ask the user if they want to reboot immediately.
    If yes, reboot the system, else remind to reboot later.
    """
    choice = input("Reboot now? (y/N): ").strip().lower()
    if choice == "y":
        print("Rebooting system...")
        subprocess.run(["reboot"])
    else:
        print("Please remember to reboot manually later.")


def main():
    # Check for root privileges
    if os.geteuid() != 0:
        print("Please run this script with sudo.")
        return

    print("UART Setup Script")

    # User menu for action selection
    action = input(
        "Select action:\n"
        "  1) Apply full UART setup (with venv, dependencies, add wrapper.sh to autostart)\n"
        "  2) Restore original config\n"
        "  3) Only create venv and install dependencies\n"
        "  4) Add wrapper.sh to autostart only\n"
        "  5) Remove wrapper.sh from autostart\n"
        "Choice [1/2/3/4/5]: "
    ).strip()

    if action == "2":
        restore_config()
        return
    elif action == "3":
        create_venv_and_install_deps()
        create_wrapper_script()
        return
    elif action == "4":
        create_wrapper_script()
        make_wrapper_executable()
        add_wrapper_to_autostart_profile()
        return
    elif action == "5":
        remove_wrapper_from_autostart_profile()
        return
    elif action != "1":
        print(" Invalid choice. Exiting.")
        return

    # Full setup flow:
    create_venv_and_install_deps()
    create_wrapper_script()
    backup_config()
    print("Modifying UART and system configuration...")
    modified = modify_config_file()

    print("Enabling serial interface...")
    enable_serial_port_interface()
    make_wrapper_executable()
    add_wrapper_to_autostart_profile()
    #main_switch_to_x11()
    #disable_sleep_lxde()
    if modified:
        prompt_reboot()
    else:
        print("No changes were necessary.")


if __name__ == "__main__":
    main()
