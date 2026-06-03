import os
import shutil
import subprocess
import sys
from pathlib import Path
import getpass
import pwd

from x11 import main_switch_to_x11, disable_sleep_lxde

# Always resolve paths relative to this script's location, not cwd
SCRIPT_DIR = Path(__file__).resolve().parent

# Get the username who invoked sudo or fallback to the current user
USER_NAME = os.getenv("SUDO_USER") or getpass.getuser()
# Define home directory path for that user
USER_HOME = Path(f"/home/{USER_NAME}")

# Path to Raspberry Pi config.txt file (system config)
CONFIG_PATH = "/boot/firmware/config.txt"
# Backup path for the original config file
BACKUP_PATH = "/boot/firmware/config_backup_uart.txt"
# Virtual environment directory path
VENV_PATH = SCRIPT_DIR / "venv"
# Python requirements file with dependencies
REQUIREMENTS_FILE = SCRIPT_DIR / "requirements.txt"
# Wrapper shell script
WRAPPER_PATH = SCRIPT_DIR / "wrapper.sh"
# Name of the main Python script to run inside the wrapper
RUN_SCRIPT_NAME = "run.py"

# List of device tree overlays and settings to add to config.txt
OVERLAYS = [
    "enable_uart=1",
    "dtoverlay=uart3,txd_pin=4,rxd_pin=5",
    "dtoverlay=uart4,txd_pin=8,rxd_pin=9",
    "dtoverlay=uart5,txd_pin=12,rxd_pin=13",
    "dtoverlay=disable-bt",
    "dtoverlay=hifiberry-dac"
]

# Modifications to existing config.txt parameters (key=old, value=new)
MODIFICATIONS = {
    "dtparam=audio=on": "dtparam=audio=off",
    "camera_auto_detect=1": "camera_auto_detect=0",
}

# Overlays to remove from config.txt if present
OVERLAYS_REMOVE = []


def _chown_to_user(path):
    """Change file ownership to the real (non-root) user."""
    try:
        pw = pwd.getpwnam(USER_NAME)
        os.chown(path, pw.pw_uid, pw.pw_gid)
    except Exception as e:
        print(f"Warning: could not chown {path} to {USER_NAME}: {e}")


def get_users():
    users = []
    user_home = USER_HOME
    if user_home.exists():
        users.append((USER_NAME, user_home))
    root_home = Path("/root")
    if root_home.exists():
        users.append(("root", root_home))
    return users


def add_wrapper_to_autostart():
    """
    Create an XDG autostart .desktop file so the wrapper starts on GUI login.
    This works reliably with LightDM autologin on Raspberry Pi OS.
    Also adds a fallback line to .profile for console-only sessions.
    """
    wrapper_str = str(WRAPPER_PATH)

    for user_name, user_home in get_users():
        if user_name == "root":
            continue

        # XDG autostart (works for all desktop managers)
        autostart_dir = user_home / ".config" / "autostart"
        autostart_dir.mkdir(parents=True, exist_ok=True)
        desktop_file = autostart_dir / "vacantview.desktop"
        desktop_content = (
            "[Desktop Entry]\n"
            "Type=Application\n"
            "Name=VacantView\n"
            f"Exec={wrapper_str}\n"
            "Hidden=false\n"
            "NoDisplay=false\n"
            "X-GNOME-Autostart-enabled=true\n"
        )
        desktop_file.write_text(desktop_content)
        _chown_to_user(desktop_file)
        _chown_to_user(autostart_dir)
        print(f"Created autostart desktop entry: {desktop_file}")

        # Remove any old .profile fallback line that causes double-start
        profile_path = user_home / ".profile"
        if profile_path.exists():
            lines = profile_path.read_text().splitlines(keepends=True)
            new_lines = [l for l in lines if wrapper_str not in l and "VacantView autostart" not in l]
            if len(new_lines) != len(lines):
                profile_path.write_text("".join(new_lines))
                print(f"Removed old .profile autostart line from {profile_path}")


def remove_wrapper_from_autostart():
    """Remove both the .desktop autostart entry and the .profile fallback line."""
    wrapper_str = str(WRAPPER_PATH)

    for user_name, user_home in get_users():
        desktop_file = user_home / ".config" / "autostart" / "vacantview.desktop"
        if desktop_file.exists():
            desktop_file.unlink()
            print(f"Removed {desktop_file}")
        else:
            print(f"No desktop autostart file at {desktop_file}")

        profile_path = user_home / ".profile"
        if profile_path.exists():
            lines = profile_path.read_text().splitlines(keepends=True)
            new_lines = [l for l in lines if wrapper_str not in l and "VacantView autostart" not in l]
            if len(new_lines) != len(lines):
                profile_path.write_text("".join(new_lines))
                print(f"Removed wrapper from {profile_path}")


def create_wrapper_script():
    """
    Create wrapper.sh that kills any existing instance, waits for display,
    then runs the app silently (no terminal window). Output goes to log file.
    """
    venv_activate = str(VENV_PATH / "bin" / "activate")
    run_script = str(SCRIPT_DIR / RUN_SCRIPT_NAME)
    log_file = str(SCRIPT_DIR / "vacantview.log")

    wrapper_content = f"""#!/bin/bash

SCRIPT_DIR="{SCRIPT_DIR}"
LOG="{log_file}"
LOCKFILE="/tmp/vacantview_wrapper.lock"

exec 9>"$LOCKFILE"
if ! flock -n 9; then
    exit 0
fi

# Kill any existing instance to release GPIO
pkill -f "${{SCRIPT_DIR}}/{RUN_SCRIPT_NAME}" 2>/dev/null || true
pkill lgd 2>/dev/null || true
sleep 1

export DISPLAY="${{DISPLAY:-:0}}"

for i in $(seq 1 30); do
    xdpyinfo -display "$DISPLAY" >/dev/null 2>&1 && break
    sleep 1
done

if ! xdpyinfo -display "$DISPLAY" >/dev/null 2>&1; then
    echo "$(date): Display $DISPLAY not available after 30s, aborting." >> "$LOG"
    exit 1
fi

# Disable screen sleep
xset s off 2>/dev/null || true
xset -dpms 2>/dev/null || true
xset s noblank 2>/dev/null || true

pcmanfm --desktop 2>/dev/null &

cd "${{SCRIPT_DIR}}"
source "{venv_activate}"
echo "$(date): Starting VacantView" >> "$LOG"
python "{run_script}" >> "$LOG" 2>&1
echo "$(date): VacantView exited" >> "$LOG"
"""
    WRAPPER_PATH.write_text(wrapper_content)
    WRAPPER_PATH.chmod(0o755)
    print(f"Created wrapper script: {WRAPPER_PATH}")


def make_wrapper_executable():
    if WRAPPER_PATH.exists():
        WRAPPER_PATH.chmod(0o755)
        print(f"Made '{WRAPPER_PATH}' executable.")
    else:
        print(f"Wrapper script '{WRAPPER_PATH}' not found — skipping chmod.")


def create_venv_and_install_deps():
    print("Installing system dependencies...")
    subprocess.run(["apt", "update"], check=True)
    subprocess.run([
        "apt", "install", "-y",
        # X11 / XCB
        "libxcb-cursor0", "libxcb-xinerama0", "libxcb-xfixes0", "libxcb-icccm4",
        "libxcb-image0", "libxcb-keysyms1", "libxcb-render-util0", "libxcb-render0",
        "libxcb-shape0", "libxcb-shm0", "libxcb-sync1", "libxcb-xkb1", "libxkbcommon-x11-0",
        "libx11-xcb1", "libxrender1", "libxext6", "libxi6", "libgl1",
        "qt5-qmake", "qtbase5-dev",
        # Audio
        "alsa-utils",
        # GPIO / Python
        "python3-dev", "liblgpio-dev", "swig",
        # Display utilities
        "x11-utils",    # provides xdpyinfo
        "unclutter",    # hides cursor
    ], check=True)

    print("Creating virtual environment and installing Python dependencies...")
    if not VENV_PATH.exists():
        subprocess.run([sys.executable, "-m", "venv", str(VENV_PATH)], check=True)
        print(f"Virtual environment created at {VENV_PATH}")
    else:
        print(f"Virtual environment already exists at {VENV_PATH}")

    if not REQUIREMENTS_FILE.exists():
        print(f"{REQUIREMENTS_FILE} not found. Skipping dependency installation.")
        return

    venv_pip = str(VENV_PATH / "bin" / "pip")
    subprocess.run([venv_pip, "install", "--upgrade", "pip", "setuptools", "wheel"], check=True)
    subprocess.run([venv_pip, "install", "--only-binary=:all:", "PyQt6"], check=True)
    subprocess.run([venv_pip, "install", "-r", str(REQUIREMENTS_FILE), "--no-deps"], check=True)
    print("Dependencies installed.")


def backup_config():
    if os.path.exists(CONFIG_PATH):
        shutil.copy(CONFIG_PATH, BACKUP_PATH)
        print(f"Backup created at {BACKUP_PATH}")
    else:
        print("Config file not found for backup.")


def restore_config():
    if os.path.exists(BACKUP_PATH):
        shutil.copy(BACKUP_PATH, CONFIG_PATH)
        print(f"Restored original config from {BACKUP_PATH}")
        print("Please reboot the system to apply restored settings.")
    else:
        print("No backup file found to restore.")


def modify_config_file():
    if not os.path.exists(CONFIG_PATH):
        print(f"Error: {CONFIG_PATH} not found.")
        return False

    with open(CONFIG_PATH, "r") as f:
        lines = f.read().splitlines()

    new_lines = []
    existing = set(lines)
    for line in lines:
        # Skip overlays that should be removed
        if any(line.strip() == r or line.strip().startswith(r) for r in OVERLAYS_REMOVE):
            continue
        modified = False
        for old, new in MODIFICATIONS.items():
            if line.strip().startswith(old):
                new_lines.append(new)
                modified = True
                break
        if not modified:
            new_lines.append(line)

    for overlay in OVERLAYS:
        if overlay not in existing and overlay not in new_lines:
            new_lines.append(overlay)

    with open(CONFIG_PATH, "w") as f:
        f.write("\n".join(new_lines) + "\n")

    print(f"{CONFIG_PATH} successfully modified.")
    return True


def enable_serial_port_interface():
    try:
        subprocess.run(
            ["raspi-config", "nonint", "do_serial", "2"],
            check=True
        )
        print("Serial port enabled and serial console disabled.")
    except subprocess.CalledProcessError:
        print("Failed to set serial port interface via raspi-config.")


def enable_ssh():
    print("Enabling SSH server...")
    subprocess.run(["systemctl", "enable", "ssh"], check=False)
    subprocess.run(["systemctl", "start", "ssh"], check=False)
    print("SSH enabled.")


def prompt_reboot():
    choice = input("Reboot now? (y/N): ").strip().lower()
    if choice == "y":
        print("Rebooting system...")
        subprocess.run(["reboot"])
    else:
        print("Please remember to reboot manually later.")


def main():
    if os.geteuid() != 0:
        print("Please run this script with sudo.")
        return

    print("UART Setup Script")

    action = input(
        "Select action:\n"
        "  1) Apply full UART setup (with venv, dependencies, add wrapper to autostart)\n"
        "  2) Restore original config\n"
        "  3) Only create venv and install dependencies\n"
        "  4) Add wrapper to autostart only\n"
        "  5) Remove wrapper from autostart\n"
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
        add_wrapper_to_autostart()
        return
    elif action == "5":
        remove_wrapper_from_autostart()
        return
    elif action != "1":
        print("Invalid choice. Exiting.")
        return

    # Full setup flow
    create_venv_and_install_deps()
    create_wrapper_script()
    backup_config()
    print("Modifying UART and system configuration...")
    modified = modify_config_file()
    print("Enabling serial interface...")
    enable_serial_port_interface()
    enable_ssh()
    make_wrapper_executable()
    add_wrapper_to_autostart()
    main_switch_to_x11(USER_HOME)
    if modified:
        prompt_reboot()
    else:
        print("No changes were necessary.")


if __name__ == "__main__":
    main()
