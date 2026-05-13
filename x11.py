import os
import subprocess
import shutil
import getpass
import pwd
from pathlib import Path
from datetime import datetime


def run_cmd(cmd):
    print(f"Running: {cmd}")
    subprocess.run(cmd, shell=True, check=True)


def get_real_user():
    return os.getenv("SUDO_USER") or getpass.getuser()


def get_real_user_home():
    user = get_real_user()
    return Path(f"/home/{user}")


def _chown_to_user(path, username):
    try:
        pw = pwd.getpwnam(username)
        os.chown(path, pw.pw_uid, pw.pw_gid)
    except Exception as e:
        print(f"Warning: could not chown {path} to {username}: {e}")


def disable_console_blanking():
    cmdline_path = "/boot/firmware/cmdline.txt"
    if not os.path.exists(cmdline_path):
        print(f"{cmdline_path} not found, skipping.")
        return
    with open(cmdline_path, "r") as f:
        content = f.read().strip()
    modified = False
    # Disable screen blanking
    if "consoleblank=0" not in content:
        content += " consoleblank=0"
        modified = True
    # Remove splash/plymouth to stop boot flicker
    for token in ("splash", "plymouth.ignore-serial-consoles", "quiet"):
        if token in content:
            content = content.replace(token, "").strip()
            # Clean up double spaces
            while "  " in content:
                content = content.replace("  ", " ")
            modified = True
    if modified:
        subprocess.run(["sudo", "tee", cmdline_path], input=content + "\n", text=True, check=True)
        print("Console blanking disabled and splash screen removed.")
    else:
        print("Console blanking already disabled.")


def disable_sleep_lxde(user_home=None):
    if user_home is None:
        user_home = get_real_user_home()

    username = get_real_user()
    autostart_dir = Path(user_home) / ".config" / "lxsession" / "LXDE-pi"
    autostart_file = autostart_dir / "autostart"

    disable_cmds = [
        "@xset s off",
        "@xset -dpms",
        "@xset s noblank",
        "@unclutter -idle 10 -root",
        "@bash -c 'pkill light-locker; true'",
    ]

    autostart_dir.mkdir(parents=True, exist_ok=True)
    _chown_to_user(autostart_dir, username)

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
        _chown_to_user(autostart_file, username)
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


def _read_ini(path):
    """Read an INI file into a list of (section, lines) tuples preserving order."""
    sections = []
    current_section = None
    current_lines = []
    if not os.path.exists(path):
        return sections
    with open(path, "r") as f:
        for line in f:
            stripped = line.strip()
            if stripped.startswith("[") and stripped.endswith("]"):
                if current_section is not None or current_lines:
                    sections.append((current_section, current_lines))
                current_section = stripped[1:-1]
                current_lines = []
            else:
                current_lines.append(line)
    sections.append((current_section, current_lines))
    return sections


def _write_ini(sections):
    """Render an INI section list back to a string."""
    out = []
    for section, lines in sections:
        if section is not None:
            out.append(f"[{section}]\n")
        out.extend(lines)
    return "".join(out)


def _set_ini_key(sections, section_name, key, value):
    """Set key=value inside the named section, creating the section if needed."""
    full_value = f"{key}={value}\n"
    for i, (sec, lines) in enumerate(sections):
        if sec == section_name:
            for j, line in enumerate(lines):
                if line.strip().startswith(key):
                    lines[j] = full_value
                    return sections
            lines.append(full_value)
            return sections
    # Section not found — create it
    sections.append((section_name, [full_value]))
    return sections


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


def switch_to_x11(dm, username=None):
    session_name = detect_x11_session()
    if username is None:
        username = get_real_user()
    print(f"Using X11 session: {session_name}, autologin user: {username}")

    if is_x11_session_active(dm, session_name):
        print(f"{session_name} already active, no changes needed.")
        return

    if dm == "lightdm":
        conf_file = "/etc/lightdm/lightdm.conf"
        backup_file(conf_file)
        sections = _read_ini(conf_file)
        sections = _set_ini_key(sections, "Seat:*", "user-session", session_name)
        sections = _set_ini_key(sections, "Seat:*", "autologin-session", session_name)
        sections = _set_ini_key(sections, "Seat:*", "autologin-user", username)
        sections = _set_ini_key(sections, "Seat:*", "autologin-user-timeout", "0")
        content = _write_ini(sections)
        subprocess.run(["sudo", "tee", conf_file], input=content, text=True, check=True)
        print(f"lightdm configured for {session_name}, autologin: {username}.")

    elif dm == "gdm3":
        conf_file = "/etc/gdm3/custom.conf"
        if not os.path.exists(conf_file):
            print(f"{conf_file} not found.")
            return
        backup_file(conf_file)
        sections = _read_ini(conf_file)
        sections = _set_ini_key(sections, "daemon", "WaylandEnable", "false")
        content = _write_ini(sections)
        subprocess.run(["sudo", "tee", conf_file], input=content, text=True, check=True)

    elif dm == "sddm":
        conf_file = "/etc/sddm.conf"
        if not os.path.exists(conf_file):
            print(f"{conf_file} not found.")
            return
        backup_file(conf_file)
        sections = _read_ini(conf_file)
        sections = _set_ini_key(sections, "Autologin", "Session", f"{session_name}.desktop")
        content = _write_ini(sections)
        subprocess.run(["sudo", "tee", conf_file], input=content, text=True, check=True)

    else:
        print("Display manager not supported.")


def disable_dpms_in_lightdm():
    """Disable DPMS/blanking at the X server level via lightdm.conf [Seat:*]."""
    conf_file = "/etc/lightdm/lightdm.conf"
    backup_file(conf_file)
    sections = _read_ini(conf_file)
    sections = _set_ini_key(sections, "Seat:*", "xserver-command", "X -s 0 -dpms")
    content = _write_ini(sections)
    subprocess.run(["sudo", "tee", conf_file], input=content, text=True, check=True)
    print("X server DPMS disabled in lightdm.conf [Seat:*].")


def install_x11_lightdm():
    print("Installing X11, lightdm, unclutter and desktop UI...")
    run_cmd("apt update")
    run_cmd("apt install -y xserver-xorg lightdm unclutter x11-utils")
    subprocess.run(
        'apt install -y -o Dpkg::Options::="--force-overwrite" raspberrypi-ui-mods',
        shell=True, check=False
    )
    subprocess.run("apt install -f -y", shell=True, check=False)


def set_default_display_manager(dm):
    print(f"Setting {dm} as default display manager...")
    if dm == "lightdm":
        subprocess.run("systemctl disable gdm3 2>/dev/null || true", shell=True)
        subprocess.run("systemctl disable sddm 2>/dev/null || true", shell=True)
        run_cmd("systemctl enable lightdm")
    elif dm == "gdm3":
        subprocess.run("systemctl disable lightdm 2>/dev/null || true", shell=True)
        run_cmd("systemctl enable gdm3")
    elif dm == "sddm":
        subprocess.run("systemctl disable lightdm 2>/dev/null || true", shell=True)
        subprocess.run("systemctl disable gdm3 2>/dev/null || true", shell=True)
        run_cmd("systemctl enable sddm")
    else:
        print(f"Unknown display manager: {dm}")
        return
    run_cmd("systemctl set-default graphical.target")


def main_switch_to_x11(user_home=None):
    if user_home is None:
        user_home = get_real_user_home()

    install_x11_lightdm()

    dm = detect_display_manager()
    if dm is None:
        print("Could not detect display manager. Defaulting to lightdm.")
        dm = "lightdm"

    print(f"Detected display manager: {dm}")

    username = get_real_user()
    switch_to_x11(dm, username)
    set_default_display_manager("lightdm")
    disable_console_blanking()
    disable_dpms_in_lightdm()
    disable_sleep_lxde(user_home)
