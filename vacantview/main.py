import atexit
import lgpio
import os

from vacantview.data import database
from vacantview.core.state import state
from vacantview.tests import check_gpio_status


def run_app():
    if not check_gpio_status.full_rpi_check():
        print(
            "\n\n[ ERROR ] Ports are not configured, please run the setup.py file "
            "located in the root of the application using the command:\n\n"
            "sudo python3 setup.py\n\nand follow the instructions."
        )
        return

    database.init_db()

    from vacantview.platform import audio_announcer
    audio_announcer.start()

    atexit.register(_cleanup)

    from vacantview.ui.gui_app import start_app
    start_app()


def _cleanup():
    try:
        if hasattr(state, 'h') and state.h is not None:
            lgpio.gpiochip_close(state.h)
            state.h = None
    except Exception:
        pass
