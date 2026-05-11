import subprocess
import threading
import time
import os

from vacantview.core.state import state
import vacantview.config.config as cfg

_lock = threading.Lock()
_last_trigger = 0.0
_current_processes = []
_pir = None


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
    elif mode == 'both_accessible':
        if state.clean_mode_button_1 and state.clean_mode_button_2:
            return None
        men = {} if state.clean_mode_button_1 else dict(state.OccupiedCounter_string_MEN_acc)
        women = {} if state.clean_mode_button_2 else dict(state.OccupiedCounter_string_WOMEN_acc)
        acc = {**men, **women}
    else:
        return None
    if not acc:
        return None
    return any(v == '0' for v in acc.values())


def _play_audio(filepath):
    global _current_processes
    if not filepath or not os.path.exists(filepath):
        return
    for p in _current_processes:
        if p.poll() is None:
            p.terminate()
    _current_processes = []
    devices = [d.strip() for d in cfg.AUDIO_DEVICE.split(',') if d.strip()]
    for device in devices:
        p = subprocess.Popen(
            ['aplay', '-D', device, filepath],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        _current_processes.append(p)


def _on_motion():
    global _last_trigger
    with _lock:
        now = time.monotonic()
        if now - _last_trigger < cfg.AUDIO_COOLDOWN:
            return
        _last_trigger = now
        vacant = _is_accessible_vacant()
        if vacant is None:
            return
        _play_audio(cfg.AUDIO_VACANT if vacant else cfg.AUDIO_OCCUPIED)


def start():
    global _pir
    if not cfg.PIR_PIN:
        return
    for label, path in [("AUDIO_VACANT", cfg.AUDIO_VACANT), ("AUDIO_OCCUPIED", cfg.AUDIO_OCCUPIED)]:
        if not path or not os.path.exists(path):
            print(f"[AUDIO] Warning: {label} not found at '{path}'")
    try:
        from gpiozero import MotionSensor
        _pir = MotionSensor(cfg.PIR_PIN, pull_up=True)
        _pir.when_motion = _on_motion
        print(f"[AUDIO] PIR sensor ready on GPIO {cfg.PIR_PIN}")
    except Exception as e:
        print(f"[AUDIO] PIR init failed: {e}")
