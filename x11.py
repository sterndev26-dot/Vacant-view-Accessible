import os
import subprocess
import sys
import shutil
from datetime import datetime


def run_cmd(cmd):
    print(f"Running: {cmd}")
    subprocess.run(cmd, shell=True, check=True)


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


def disable_sleep_lxde():
    """Disable screen blanking, screensaver, DPMS, and hide idle cursor."""
    autostart_dir = os.path.expanduser("~/.config/lxsession/LXDE-pi")
    autostart_file = os.path.join(autostart_dir, "autostart")

    disable_cmds = [
        "@xset s off",
        "@xset -dpms",
        "@xset s noblank",
        "@unclutter -idle 10 -root",
    ]

    os.makedirs(autostart_dir, exist_ok=True)

    if os.path.exists(autostart_file):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        backup_path = f"{autostart_file}.backup.{timestamp}"
        shutil.copy2(autostart_file, backup_path)
        print(f"Backup created: {backup_path}")

        with open(autostart_file, "r") as f:
            existing_lines = f.read().splitlines()
    else:
        existing_lines = []

    updated = False
    for cmd in disable_cmds:
        if cmd not in existing_lines:
            existing_lines.append(cmd)
            updated = True

    if updated:
        with open(autostart_file, "w") as f:
            f.write("\n".join(existing_lines) + "\n")
        print("Sleep mode disabled for LXDE-pi-x session. Changes will apply after next login.")
    else:
        print("Sleep mode already disabled. No changes made.")


def detect_display_manager():
    dm_candidates = ["lightdm", "gdm3", "sddm"]
    for dm in dm_candidates:
        status = subprocess.run(
            ["systemctl", "is-active", dm],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        if status.stdout.strip() == "active":
            return dm
    return None


def backup_file(file_path):
    if os.path.exists(file_path):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        backup_path = f"{file_path}.backup.{timestamp}"
        shutil.copy2(file_path, backup_path)
        print(f"Backup created: {backup_path}")


def is_x11_session_active(dm, session_name):
    if dm == "lightdm":
        conf_file = "/etc/lightdm/lightdm.conf"
        if not os.path.exists(conf_file):
            return False
        with open(conf_file, "r") as f:
            for line in f:
                if line.strip() == f"user-session={session_name}":
                    return True
        return False

    elif dm == "gdm3":
        conf_file = "/etc/gdm3/custom.conf"
        if not os.path.exists(conf_file):
            return False
        with open(conf_file, "r") as f:
            for line in f:
                if line.strip() == "WaylandEnable=false":
                    return True
        return False

    elif dm == "sddm":
        conf_file = "/etc/sddm.conf"
        if not os.path.exists(conf_file):
            return False
        with open(conf_file, "r") as f:
            for line in f:
                if line.strip() == f"Session={session_name}.desktop":
                    return True
        return False

    return False


def switch_to_x11(dm):
    session_name = "LXDE-pi-x"

    if is_x11_session_active(dm, session_name):
        print(f"{session_name} session already active for {dm}, no changes needed.")
        return

    if dm == "lightdm":
        conf_file = "/etc/lightdm/lightdm.conf"
        if not os.path.exists(conf_file):
            print(f"{conf_file} not found, creating a new one.")
            lines = []
        else:
            backup_file(conf_file)
            with open(conf_file, "r") as f:
                lines = f.readlines()

        found_session = False
        found_autologin = False
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

        content = "".join(lines)
        subprocess.run(
            ["sudo", "tee", conf_file],
            input=content,
            text=True,
            check=True
        )
        print(f"{dm} configuration updated. Changes will apply after reboot.")

    elif dm == "gdm3":
        conf_file = "/etc/gdm3/custom.conf"
        if not os.path.exists(conf_file):
            print(f"{conf_file} not found. GDM3 not configured.")
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

        content = "".join(lines)
        subprocess.run(
            ["sudo", "tee", conf_file],
            input=content,
            text=True,
            check=True
        )
        print(f"{dm} configuration updated. Changes will apply after reboot.")

    elif dm == "sddm":
        conf_file = "/etc/sddm.conf"
        if not os.path.exists(conf_file):
            print(f"{conf_file} not found. SDDM not configured.")
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

        content = "".join(lines)
        subprocess.run(
            ["sudo", "tee", conf_file],
            input=content,
            text=True,
            check=True
        )
        print(f"{dm} configuration updated. Changes will apply after reboot.")

    else:
        print("Display manager not found or not automatically supported.")


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
        print(f"Unknown display manager: {dm}, cannot set default.")
        return
    run_cmd("sudo systemctl set-default graphical.target")


def main_switch_to_x11():
    install_x11_lightdm()

    dm = detect_display_manager()
    if dm is None:
        print("Could not detect display manager. Defaulting to lightdm.")
        dm = "lightdm"

    print(f"Detected display manager: {dm}")

    switch_to_x11(dm)

    set_default_display_manager("lightdm")

    disable_console_blanking()
    disable_sleep_lxde()


