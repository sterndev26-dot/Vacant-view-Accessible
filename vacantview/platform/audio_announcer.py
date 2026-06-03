import subprocess
import threading
import time
import os
import re

from vacantview.core.state import state
import vacantview.config.config as cfg

_lock = threading.Lock()
_last_trigger = 0.0
_current_processes = []
_pir = None


def _detect_devices():
    """Detect ALL audio output devices currently connected."""
    try:
        result = subprocess.run(['aplay', '-l'], capture_output=True, text=True, timeout=5)
        found = []
        for line in result.stdout.split('\n'):
            m = re.search(r'card (\d+):', line)
            if m:
                device = f'plughw:{m.group(1)},0'
                if device not in found:
                    found.append(device)
        return found if found else ['default']
    except Exception:
        return ['default']


def _get_devices():
    """
    Return the list of devices to play on.
    If AUDIO_DEVICE is explicitly configured, use that.
    Otherwise re-detect all connected devices every time so
    hot-plugged speakers are always picked up.
    """
    configured = cfg.AUDIO_DEVICE.strip()
    if configured and configured != 'default':
        return [d.strip() for d in configured.split(',') if d.strip()]
    return _detect_devices()


def _is_accessible_vacant():
    mode = state.current_mode
    if mode in ('men', 'men_accessible'):
        if state.clean_mode_button_1:
            return None
        acc = state.OccupiedCounter_string_MEN_acc
    elif mode in ('women', 'women_accessible'):
        if state.clean_mode_button_2:
            return None
        acc = state.OccupiedCounter_string_WOMEN_acc
    else:
        return None
    if not acc:
        return None
    return any(v == '0' for v in acc.values())


def _set_headphone_mute(muted):
    """Mute/unmute the Pi's analog output to eliminate idle white noise."""
    vol = "0%" if muted else "100%"
    subprocess.run(
        ['amixer', '-c', 'Headphones', 'set', 'Headphone', vol],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )


def _play_audio(filepath):
    global _current_processes
    if not filepath or not os.path.exists(filepath):
        return
    for p in _current_processes:
        if p.poll() is None:
            p.terminate()
    _current_processes = []
    devices = _get_devices()
    print(f"[AUDIO] Playing {os.path.basename(filepath)} on {devices}")
    _set_headphone_mute(False)
    for device in devices:
        p = subprocess.Popen(
            ['aplay', '-D', device, filepath],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        _current_processes.append(p)

    def _mute_when_done():
        for p in _current_processes:
            p.wait()
        _set_headphone_mute(True)

    threading.Thread(target=_mute_when_done, daemon=True).start()


def _play_audio_sync(filepath):
    global _current_processes
    if not filepath or not os.path.exists(filepath):
        return
    for p in _current_processes:
        if p.poll() is None:
            p.terminate()
    _current_processes = []
    devices = _get_devices()
    print(f"[AUDIO] Playing {os.path.basename(filepath)} on {devices}")
    _set_headphone_mute(False)
    procs = []
    for device in devices:
        p = subprocess.Popen(
            ['aplay', '-D', device, filepath],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        procs.append(p)
    _current_processes = procs
    for p in procs:
        p.wait()
    _set_headphone_mute(True)


def _play_both():
    if not state.clean_mode_button_1:
        men_acc = state.OccupiedCounter_string_MEN_acc
        if men_acc:
            men_vacant = any(v == '0' for v in men_acc.values())
            _play_audio_sync(cfg.AUDIO_MEN_VACANT if men_vacant else cfg.AUDIO_MEN_OCCUPIED)
    if not state.clean_mode_button_2:
        women_acc = state.OccupiedCounter_string_WOMEN_acc
        if women_acc:
            women_vacant = any(v == '0' for v in women_acc.values())
            _play_audio_sync(cfg.AUDIO_WOMEN_VACANT if women_vacant else cfg.AUDIO_WOMEN_OCCUPIED)


def _on_motion():
    global _last_trigger
    with _lock:
        now = time.monotonic()
        if now - _last_trigger < cfg.AUDIO_COOLDOWN:
            return
        _last_trigger = now
        mode = state.current_mode
        if mode == 'both_accessible':
            if not (state.clean_mode_button_1 and state.clean_mode_button_2):
                _play_both()
        else:
            vacant = _is_accessible_vacant()
            if vacant is None:
                return
            _play_audio(cfg.AUDIO_VACANT if vacant else cfg.AUDIO_OCCUPIED)


def start():
    global _pir
    if not cfg.PIR_PIN:
        return

    devices = _get_devices()
    print(f"[AUDIO] Using devices: {devices}")

    for label, path in [
        ("AUDIO_VACANT", cfg.AUDIO_VACANT),
        ("AUDIO_OCCUPIED", cfg.AUDIO_OCCUPIED),
        ("AUDIO_MEN_VACANT", cfg.AUDIO_MEN_VACANT),
        ("AUDIO_MEN_OCCUPIED", cfg.AUDIO_MEN_OCCUPIED),
        ("AUDIO_WOMEN_VACANT", cfg.AUDIO_WOMEN_VACANT),
        ("AUDIO_WOMEN_OCCUPIED", cfg.AUDIO_WOMEN_OCCUPIED),
    ]:
        if not path or not os.path.exists(path):
            print(f"[AUDIO] Warning: {label} not found at '{path}'")

    try:
        from gpiozero import Button
        _pir = Button(cfg.PIR_PIN, pull_up=True)
        _pir.when_pressed = _on_motion
        print(f"[AUDIO] PIR sensor ready on GPIO {cfg.PIR_PIN}")
    except Exception as e:
        print(f"[AUDIO] PIR init failed: {e}")
