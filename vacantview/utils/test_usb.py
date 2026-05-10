import os
import getpass

def check_usb():
    usb_drives = []
    assets_found = []

    media_path = "/media"
    if os.path.exists(media_path):
        for user in os.listdir(media_path):
            user_path = os.path.join(media_path, user)
            if os.path.isdir(user_path):
                for device in os.listdir(user_path):
                    full_path = os.path.join(user_path, device)
                    if os.path.ismount(full_path):
                        usb_drives.append(full_path)
                        assets_path = os.path.join(full_path, "images")
                        if os.path.isdir(assets_path):
                            assets_found.append(assets_path)

    if usb_drives:
        if assets_found:
            return assets_path
        else:
            return False
    else:
        return False
    
    


def detect_usb():
    user = getpass.getuser()
    possible_mount_dirs = [
        f"/media/{user}",
        f"/run/media/{user}"
    ]

    usb_mounts = []
    for mount_dir in possible_mount_dirs:
        if os.path.isdir(mount_dir):
            for device in os.listdir(mount_dir):
                full_path = os.path.join(mount_dir, device)
                if os.path.ismount(full_path):
                    usb_mounts.append(full_path)
    
    return usb_mounts

