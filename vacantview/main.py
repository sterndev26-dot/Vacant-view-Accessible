from vacantview.ui.gui_app import start_app
from vacantview.data import database
from vacantview.core.state import state

from vacantview.tests import test_ports
from vacantview.tests import check_gpio_status
from vacantview.ui.context_menu.functions.language_manager import set_language 

import lgpio
import os



def run_app():
    
    #try:
    #test_ports.available_ports() and
    if check_gpio_status.full_rpi_check():
        
        database.init_db()

        from vacantview.platform import audio_announcer
        audio_announcer.start()

        start_app()
        
    else:
        print("\n\n[ ERROR ] Ports are not configured, please run the setup.py file located in the root of the application using the command:\n\nsudo python3 setup.py\n\nand follow the instructions.")
        
    #finally:
        
       # lgpio.gpiochip_close(state.h)
    
    
    

    
    