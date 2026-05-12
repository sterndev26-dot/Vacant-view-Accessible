import os
import subprocess
import shutil
import getpass
from pathlib import Path
from datetime import datetime


def run_cmd(cmd):
    print(f"Running: {cmd}")
    subprocess.run(cmd, shell=True, check=True)


def get_real_user_home():
    user = os.getenv("SUDO_USER") or getpass.getuser()
    return Path(f"/home/{user}")


def disable_console_blanking():
    cmdline_path = "/boot/firmware/cmdline.txt"
    if not os.path.exists(cmdline_path):
        print(f"{cmdline_path} not found, skipping.")
        return
    with open(cmdline_path, "r") as f:
        content = f.read().strip()
    if "consoleblank=0" not in content:
        content += " consoleblank=0"
        subprocess.run(["sudo", "tee", cmdline_path], input=content + "\n", text=True, check=True)
        print("Console blanking disabled.")
    else:
        print("Console blanking already disabled.")


def disable_sleep_lxde(user_home=None):
    if user_home is None:
        user_home = get_real_user_home()

    autostart_dir = Path(user_home) / ".config" / "lxsession" / "LXDE-pi"
    autostart_file = autostart_dir / "autostart"

    disable_cmds = [
        "@xset s off",
        "@xset -dpms",
        "@xset s noblank",
        "@unclutter -idle 10 -root",
        "@bash -c 'pkill light-locker; true'",
    ]

    os.makedirs(autostart_dir, exist_ok=True)

    if autostart_file.exists():
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        shutil.copy2(autostart_file, f"{autostart_file}.backup.{timestamp}")
        existing_lines = autostart_file.read_text().splitlines()
    else:
        existing_lines = []

    updated = False
    for cmd in disable_cmds:
        if cmd not in existing_lines:
            existing_lines.append(cmd)
            updated = True

    if updated:
        autostart_file.write_text("\n".join(existing_lines) + "\n")
        print(f"Sleep/lock mode disabled for {user_home}.")
    else:
        print("Sleep mode already disabled. No changes made.")


def detect_display_manager():
    for dm in ["lightdm", "gdm3", "sddm"]:
        result = subprocess.run(
            ["systemctl", "is-active", dm],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        if result.stdout.strip() == "active":
            return dm
    return None


def backup_file(file_path):
    if os.path.exists(file_path):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        shutil.copy2(file_path, f"{file_path}.backup.{timestamp}")
        print(f"Backup created: {file_path}.backup.{timestamp}")


def detect_x11_session():
    session_dir = "/usr/share/xsessions"
    preferred = ["LXDE-pi-x", "lxde-pi-x", "LXDE", "lxde", "openbox"]
    if not os.path.exists(session_dir):
        return "LXDE-pi-x"
    available = [f.replace(".desktop", "") for f in os.listdir(session_dir) if f.endswith(".desktop")]
    for s in preferred:
        if s in available:
            return s
    return available[0] if available else "LXDE-pi-x"


def is_x11_session_active(dm, session_name):
    if dm == "lightdm":
        conf_file = "/etc/lightdm/lightdm.conf"
        if not os.path.exists(conf_file):
            return False
        with open(conf_file, "r") as f:
            return any(line.strip() == f"user-session={session_name}" for line in f)
    elif dm == "gdm3":
        conf_file = "/etc/gdm3/custom.conf"
        if not os.path.exists(conf_file):
            return False
        with open(conf_file, "r") as f:
            return any(line.strip() == "WaylandEnable=false" for line in f)
    elif dm == "sddm":
        conf_file = "/etc/sddm.conf"
        if not os.path.exists(conf_file):
            return False
        with open(conf_file, "r") as f:
            return any(line.strip() == f"Session={session_name}.desktop" for line in f)
    return False


def switch_to_x11(dm):
    session_name = detect_x11_session()
    print(f"Using X11 session: {session_name}")

    if is_x11_session_active(dm, session_name):
        print(f"{session_name} already active, no changes needed.")
        return

    if dm == "lightdm":
        conf_file = "/etc/lightdm/lightdm.conf"
        if not os.path.exists(conf_file):
            lines = []
        else:
            backup_file(conf_file)
            with open(conf_file, "r") as f:
                lines = f.readlines()

        found_session = found_autologin = False
        for i, line in enumerate(lines):
            if line.strip().startswith("user-session"):
                lines[i] = f"user-session={session_name}\n"
                found_session = True
            elif line.strip().startswith("autologin-session"):
                lines[i] = f"autologin-session={session_name}\n"
                found_autologin = True
        if not found_session:
            lines.append(f"user-session={session_name}\n")
        if not found_autologin:
            lines.append(f"autologin-session={session_name}\n")

        subprocess.run(["sudo", "tee", conf_file], input="".join(lines), text=True, check=True)
        print(f"lightdm configured for {session_name}.")

    elif dm == "gdm3":
        conf_file = "/etc/gdm3/custom.conf"
        if not os.path.exists(conf_file):
            print(f"{conf_file} not found.")
            return
        backup_file(conf_file)
        with open(conf_file, "r") as f:
            lines = f.readlines()
        found = False
        for i, line in enumerate(lines):
            if line.strip().startswith("WaylandEnable"):
                lines[i] = "WaylandEnable=false\n"
                found = True
                break
        if not found:
            lines.append("WaylandEnable=false\n")
        subprocess.run(["sudo", "tee", conf_file], input="".join(lines), text=True, check=True)

    elif dm == "sddm":
        conf_file = "/etc/sddm.conf"
        if not os.path.exists(conf_file):
            print(f"{conf_file} not found.")
            return
        backup_file(conf_file)
        with open(conf_file, "r") as f:
            lines = f.readlines()
        found = False
        for i, line in enumerate(lines):
            if line.strip().startswith("Session"):
                lines[i] = f"Session={session_name}.desktop\n"
                found = True
                break
        if not found:
            lines.append(f"Session={session_name}.desktop\n")
        subprocess.run(["sudo", "tee", conf_file], input="".join(lines), text=True, check=True)

    else:
        print("Display manager not supported.")


def install_x11_lightdm():
    print("Installing X11, lightdm, and unclutter...")
    run_cmd("sudo apt update")
    run_cmd("sudo apt install -y xserver-xorg lightdm unclutter")


def set_default_display_manager(dm):
    print(f"Setting {dm} as default display manager...")
    if dm == "lightdm":
        subprocess.run("sudo systemctl disable gdm3", shell=True)
        run_cmd("sudo systemctl enable lightdm")
    elif dm == "gdm3":
        subprocess.run("sudo systemctl disable lightdm", shell=True)
        run_cmd("sudo systemctl enable gdm3")
    elif dm == "sddm":
        subprocess.run("sudo systemctl disable lightdm", shell=True)
        subprocess.run("sudo systemctl disable gdm3", shell=True)
        run_cmd("sudo systemctl enable sddm")
    else:
        print(f"Unknown display manager: {dm}")
        return
    run_cmd("sudo systemctl set-default graphical.target")


def main_switch_to_x11(user_home=None):
    if user_home is None:
        user_home = get_real_user_home()

    install_x11_lightdm()

    dm = detect_display_manager()
    if dm is None:
        print("Could not detect display manager. Defaulting to lightdm.")
        dm = "lightdm"

    print(f"Detected display manager: {dm}")

    switch_to_x11(dm)
    set_default_display_manager("lightdm")
    disable_console_blanking()
    disable_sleep_lxde(user_home)
