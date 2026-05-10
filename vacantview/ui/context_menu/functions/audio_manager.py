import os
from tkinter import filedialog
from dotenv import set_key
import vacantview.config.config as cfg


def select_audio_vacant():
    filepath = filedialog.askopenfilename(
        title="Select audio for VACANT accessible stall",
        filetypes=[("WAV files", "*.wav"), ("All files", "*.*")]
    )
    if filepath:
        set_key(cfg.env_path, "AUDIO_VACANT", filepath)
        cfg.AUDIO_VACANT = filepath


def select_audio_occupied():
    filepath = filedialog.askopenfilename(
        title="Select audio for OCCUPIED accessible stall",
        filetypes=[("WAV files", "*.wav"), ("All files", "*.*")]
    )
    if filepath:
        set_key(cfg.env_path, "AUDIO_OCCUPIED", filepath)
        cfg.AUDIO_OCCUPIED = filepath
