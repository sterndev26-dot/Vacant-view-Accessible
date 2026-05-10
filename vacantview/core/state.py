from tkinter import *
from collections import defaultdict
from threading import Lock
from dotenv import load_dotenv
from PIL import Image
#from vacantview.ui.image_loader import load_background_image
from vacantview.config.config import APP_LANG

import tkinter as tk
import tkinter.font
import os

load_dotenv('.env')

class GlobalState:
    
    def __init__(self):
        
        self.GLOBAL_ORIENTATION = "horizontal"
        
        self.res_refresh = [0,0]
        
        self.fullscreen_signal = False
        self.logo_rel_pos = {}
        
        self.bg_canvas_prev_size  = (0,0)
        
        self.current_res_size = (0,0)
        
        self.button_states = {
                    'button_1': {'active': False, 'permanent': False, 'timer': None},
                    'button_2': {'active': False, 'permanent': False, 'timer': None}
                }

        
        self.current_translation = None
        
        self.current_lang = APP_LANG
        
        self.c_block = False
        
        self.tk_icons = {}
         
        self.icon_rect : Any
        
        self.cleaning_active = False
        
        self.permanent_mode = False
        
        self.cleaning_timer = None
        
        self.cleaning_timer_2 = None
        
        self.button_press_time = 0
        
        self.win = Tk()
        
        self.button_1 : Any
        self.button_2 : Any
        
        self.a_progress_on = True
        
        self.is_accessible= tuple()
        
        self.GRID_SIZE = 10
        
        self.no_uart = False
        
        self.fullscreen_mode = False
        self.current_mode = 'custom'
        
        self.refresh_ui_flag = False
        self.flag_start_mode = False
        self.indicator_type = 'circle'
        
        self.config_cleaning_mode = False
        
        self.custom_title = False
        
       
        
        self.image_path_folder : Any
        
        self.fill_h1 = "white"
        self.fill_h2_v = "white"
        self.fill_h2_o = "white"
        self.fill_h2_v2 = "white"
        self.fill_h2_o2 = "white"
        self.fill_v_line = "white"
        
        self.bg_fill_tag : Any 
        self.bg_color = '#00436e'
        self.bg_set_img = False
        
        self.font_h1 = ("Arial", 16, "bold")
        self.font_h2_v = ("Arial", 12)
        self.font_h2_o = ("Arial", 12)
        self.font_h2_v2 = ("Arial", 12)
        self.font_h2_o2 = ("Arial", 12) 
        self.font_v_line = 2
        
        self.line_vertical_pos = True
        
        self.drag_data_rings={
                                "item_tag": None,
                                "start_x": 0,
                                "start_y": 0
                             }

        self.drag_and_drop = False
        
        self.outring_fill = '#417293'
        self.outer3_fill =  '#004974'
        
        self.h : Any
        
        self.open_window = []
        
        self.DEBUG = os.getenv("DEBUG").lower() in ("true",1)
        
        self.admin_button : Any
        
        self.myFont : Any
        self.myFontNumbers : Any
        
        self.label : Any
        self.copy_of_image : Any
        
        self.disp_Cubiculs_MEN_only : Any
        self.disp_Cubiculs_WOMEN_only : Any
        self.disp_Cubiculs_MEN : Any
        self.disp_Cubiculs_WOMEN : Any
        
        self.disp_men_total : Any
        self.disp_woman_total : Any
        
        self.graph_w_GREEN : Any
        self.graph_w_RED : Any
        self.graph_M_GREEN : Any
        self.graph_M_RED : Any
        
        self.string_TotalSpace = tk.StringVar()
        self.string_TotalSpace_WOMEN = tk.StringVar()
        self.addresses_string = []
        self.addresses_string_WOMEN = []
        self.BackGrounds = ["MEN", "WOMEN" , "BOTH", "NONE", "MEN_ACCESSIBLE", "WOMEN_ACCESSIBLE", "BOTH_ACCESSIBLE"]
        self.string_genderSelect = tk.StringVar()
        self.OccupiedCounter_string = defaultdict(lambda: '0')
        self.OccupiedCounter_string_WOMEN = defaultdict(lambda: '0')
        self.OccupiedCounter_string_MEN_acc = defaultdict(lambda: '0')
        self.OccupiedCounter_string_WOMEN_acc = defaultdict(lambda: '0')
        self.int_COUNT = 0
        self.int_cansize = 0
        self.clean_mode_button_1 = False
        self.clean_mode_button_2 = False
        self.button_label = None
        self.widget_lock = Lock()
        
        self.flag_sensor_thread = False
        self.flag_monitor_thread = False
        
        ''' SHOW ELEMENTS '''
        
        self.s_element_dict = {
            'both': ['Cubiculs_MEN', 'Cubiculs_WOMEN'],
            'both_accessible': [
                'Cubiculs_MEN', 'Cubiculs_WOMEN',
                'accessible_vacant_indicator_men',
                'accessible_vacant_indicator_women',
                'accessible_occup_indicator_women', 
                'accessible_occup_indicator_men'
            ],
            'men': [
                'Cubiculs_MEN', 'Cubiculs_WOMEN',
                'accessible_vacant_indicator_men',
                'accessible_occup_indicator_men'
            ],
            'men_accessible': [
                'Cubiculs_MEN',
                'accessible_vacant_indicator_men',
                'accessible_occup_indicator_men'
            ],
            'women': ['Cubiculs_WOMEN'],
            'women_accessible': [
                'Cubiculs_WOMEN',
                'accessible_vacant_indicator_women',
                'accessible_occup_indicator_women'
            ],
            'custom': [
                'Cubiculs_MEN', 'Cubiculs_WOMEN',
                'accessible_vacant_indicator_men',
                'accessible_vacant_indicator_women',
                'accessible_occup_indicator_women',
                'accessible_occup_indicator_men']}
        
        
        ''' HIDDEN ELEMENTS '''
        
        self.hidden_tags = []
        self.filtered_tags = []
        
        ''' Background '''
        
        self.bg_fill_tag : Any 
        self.bg_color = '#00436e'
        self.bg_set_img = False
        self.background_filepath = ''
        
        ''' LOGO '''
        self.logo_positions = {
            'x' : 20,
            'y' : 20,
            }
        
        self.logo_original_img : Any
        self.logo_image_id : Any
        self.logo_photo : Any
        self.logo_scale = 1.0
        self.logo_file_path = ''
        
        self.new_font = ['Arial',25,'bold']#f"Arial 25 bold"
        self.new_font_CUBICLES : Any
        self.new_font_CUBICLES_BOTH : Any
        self.new_font_clean : Any
        
        self.image : Any #Image.open(load_background_image('BACKGROUND.jpg'))
        
        self.status_windows = {'Master' : 'normal',
                               'Guest': 'splash',
                               'User' : 'splash' }
        
        self.after_id : Any
        
        self.GREEN_OUTLINE = '#8ec685'
        self.GREEN_FILL = '#40af49'
        self.RED_OUTLINE = '#d95842'
        self.RED_FILL = '#d1242a'
        
        self.total = 0
        self.free = 0
        self.Occupied = 0
        
        self.text_color = {'graph_M_GREEN' : 'white',
                           'graph_M_RED' : 'white',
                           'graph_w_GREEN' : 'white',
                           'graph_w_RED' : 'white'}

        self.colors22 = {
            "GREEN": ('#8ec685', '#40af49'),
            "RED": ('#d95842', '#d1242a')
            }
        
        self.colors = {
            "graph_M_GREEN": {"outline": "#80FF80", "fill": "#80FF80"},
            "graph_M_RED": {"outline": "#FF8080", "fill": "#FF8080"},
            "graph_w_GREEN": {"outline": "#80FF80", "fill": "#80FF80"},
            "graph_w_RED": {"outline": "#FF8080", "fill": "#FF8080"}}
    
        self.positions = {
            "graph_w_GREEN": {"WOMEN": (0.25, 0.45), "BOTH": (0.645, 0.5)},
            "graph_w_RED": {"WOMEN": (0.7555, 0.45), "BOTH": (0.83, 0.5)},
            "graph_M_GREEN": {"MEN": (0.25, 0.45), "BOTH": (0.17, 0.5)},
            "graph_M_RED": {"MEN": (0.7555, 0.45), "BOTH": (0.355, 0.5)}
            }
        
        self.ring_color_table = {
            "graph_M_GREEN": {"outline": "#80FF80", "fill": "#80FF80"},
            "graph_M_RED": {"outline": "#FF8080", "fill": "#FF8080"},
            "graph_w_GREEN": {"outline": "#80FF80", "fill": "#80FF80"},
            "graph_w_RED": {"outline": "#FF8080", "fill": "#FF8080"}}
        
        self.ring_color_add_table = {
            "graph_M_GREEN": {"outline": "#00FF00", "fill": "#00FF00"},
            "graph_M_RED": {"outline": "#FF0000", "fill": "#FF0000"},
            "graph_w_GREEN": {"outline": "#00FF00", "fill": "#00FF00"},
            "graph_w_RED": {"outline": "#FF0000", "fill": "#FF0000"}}
        
        self.outring_fill_old = '#417293'
        
        self.outring_fill = {
            "graph_M_GREEN": '#417293',
            "graph_M_RED": '#417293',
            "graph_w_GREEN": '#417293',
            "graph_w_RED": '#417293'}
        
        self.outer3_fill = {
            "graph_M_GREEN": '#004974',
            "graph_M_RED": '#004974',
            "graph_w_GREEN": '#004974',
            "graph_w_RED": '#004974'}
        
        self.graph_elements = {
            "graph_M_GREEN": {
                "items": [],              
                "scale_params": None,     
                "accumulated_scale": 1.0,
            },
            "graph_M_RED": {
                "items": [],
                "scale_params": None,
                "accumulated_scale": 1.0,
            },
            "graph_w_GREEN": {
                "items": [],
                "scale_params": None,
                "accumulated_scale": 1.0,
            },
            "graph_w_RED": {
                "items": [],
                "scale_params": None,
                "accumulated_scale": 1.0,
            },
        }
            
        self.COLOR_CATEGORIES_RINGS = {
                                        "Primary": [
                                            "#FF0000",  # Red
                                            "#00FF00",  # Green
                                            "#0000FF",  # Blue
                                            "#FFFF00",  # Yellow
                                            "#FFA500",  # Orange
                                            "#800080",  # Purple
                                            "#00FFFF",  # Cyan (Aqua)
                                            "#FFC0CB",  # Pink
                                            "#A52A2A",  # Brown
                                            "#000000",  # Black
                                            "#FFFFFF"   # White
                                        ],
                                        "Available": [
                                            "#00FF00", "#32CD32", "#7FFF00", "#ADFF2F", "#98FB98",
                                            "#00FA9A", "#3CB371", "#2E8B57", "#228B22", "#66CDAA",
                                            "#8FBC8F", "#9ACD32", "#6B8E23", "#00FF7F", "#7CFC00"
                                        ],

                                        "Occupied": [
                                            "#FF0000", "#DC143C", "#B22222", "#8B0000", "#FF4500",
                                            "#FF6347", "#CD5C5C", "#E34234", "#D1001C", "#C41E3A",
                                            "#FF2400", "#FA8072", "#F08080", "#B22222", "#A52A2A"
                                        ],

                                        "Caution": [
                                            "#FFFF00", "#FFD700", "#FFA500", "#FF8C00", "#F4A460",
                                            "#DAA520", "#FFE135", "#E1AD01", "#FFC300", "#E97451",
                                            "#FFB347", "#FFDB58", "#F5DEB3", "#FFCC00", "#FFDAB9"
                                        ],

                                        "Neutral": [
                                            "#FFFFFF", "#F0F0F0", "#C0C0C0", "#808080", "#A9A9A9",
                                            "#696969", "#000000", "#D3D3D3", "#BEBEBE", "#E5E4E2",
                                            "#DCDCDC", "#B0C4DE", "#778899", "#708090", "#ECECEC"
                                        ],

                                        "Special": [
                                            "#0000FF", "#1E90FF", "#4169E1", "#4682B4", "#6495ED",
                                            "#8A2BE2", "#4B0082", "#800080", "#9932CC", "#BA55D3",
                                            "#00CED1", "#20B2AA", "#5F9EA0", "#40E0D0", "#00FFFF"
                                        ]
                                        
                                    }
        
        
        self.ser1 = None
        self.ser2 = None
        
class GlobalAuthentications:
    
    def __init__(self):
        
        self.current_user = 'Guest'
        
g_auth = GlobalAuthentications()
state = GlobalState()
