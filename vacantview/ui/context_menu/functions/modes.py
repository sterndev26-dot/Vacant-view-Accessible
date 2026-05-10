from .branding_images import upload_background_image,set_canvas_background_color
from vacantview.core.state import state
from vacantview.config.config import DEBUG,IMG_DIR

import os

def men_mode(accessiable=False):
    hidden_elements=(
        'graph_w_GREEN',
        'graph_w_RED',
        'h1',
        'h2_v',
        'h2_o',
        'h2_v2',
        'h2_o2',
        'v_line',
        'figure_women',
        'figure_men',
        'accessible_panel_men',
        'accessible_panel_women',
        'accessible_vacant_indicator_men',
        'accessible_vacant_indicator_women',
        'accessible_occup_indicator_men',
        'accessible_occup_indicator_women',
        'logo'
        )
    if accessiable:
        values_to_remove = ('accessible_panel_men','accessible_vacant_indicator_men','accessible_occup_indicator_men')
        state.hidden_tags = (x for x in state.hidden_tags if x not in values_to_remove)
        new_hidden_elements = tuple(x for x in hidden_elements if x not in values_to_remove)
        [state.bg_canvas.itemconfigure(tag, state='hidden') for tag in new_hidden_elements]
        
        show_men_elements=(
            'accessible_panel_men',
            'accessible_vacant_indicator_men',
            'accessible_occup_indicator_men',
            'Cubiculs_MEN',
            'graph_M_GREEN',
            'graph_M_RED',
            )
        [state.bg_canvas.itemconfigure(tag, state='normal') for tag in show_men_elements]
        state.current_mode = 'men_accessible'
    else:
        [state.bg_canvas.itemconfigure(tag, state='hidden') for tag in hidden_elements]
        
        show_men_elements=(
            'graph_M_GREEN',
            'graph_M_RED',
            'Cubiculs_MEN',
            )
        [state.bg_canvas.itemconfigure(tag, state='normal') for tag in show_men_elements]
        state.current_mode = 'men'
    #upload_background_image(os.path.join('vacantview', IMG_DIR,'MEN.jpg'))

def women_mode(accessiable=False):
    hidden_elements=(
        'graph_M_GREEN',
        'graph_M_RED',
        'h1',
        'h2_v',
        'h2_o',
        'h2_v2',
        'h2_o2',
        'v_line',
        'figure_women',
        'figure_men',
        'accessible_panel_men',
        'accessible_panel_women',
        'accessible_vacant_indicator_men',
        'accessible_vacant_indicator_women',
        'accessible_occup_indicator_men',
        'accessible_occup_indicator_women',
        'logo'
        )
        
    if accessiable:
        values_to_remove = ('accessible_panel_women','accessible_vacant_indicator_women','accessible_occup_indicator_women')
        state.hidden_tags = (x for x in state.hidden_tags if x not in values_to_remove)
        new_hidden_elements = tuple(x for x in hidden_elements if x not in values_to_remove)
        [state.bg_canvas.itemconfigure(tag, state='hidden') for tag in new_hidden_elements]
        
        show_men_elements=(
            'accessible_panel_women',
            'accessible_vacant_indicator_women',
            'accessible_occup_indicator_women',
            'Cubiculs_WOMEN',
            'graph_w_GREEN',
            'graph_w_RED',
            )
        [state.bg_canvas.itemconfigure(tag, state='normal') for tag in show_men_elements]

        state.current_mode = 'women_accessible'
    else:
        [state.bg_canvas.itemconfigure(tag, state='hidden') for tag in hidden_elements]
    
        show_men_elements=(
            'Cubiculs_WOMEN',
            'graph_w_GREEN',
            'graph_w_RED',
            )
        [state.bg_canvas.itemconfigure(tag, state='normal') for tag in show_men_elements]
    
        state.current_mode = 'women'
    #upload_background_image(os.path.join('vacantview', IMG_DIR,'WOMEN.jpg'))
   

def both_mode(accessiable=False):
    hidden_elements=(
        'h1',
        'h2_v',
        'h2_o',
        'h2_v2',
        'h2_o2',
        'v_line',
        'figure_women',
        'figure_men',
        'accessible_panel_men',
        'accessible_panel_women',
        'accessible_vacant_indicator_men',
        'accessible_vacant_indicator_women',
        'accessible_occup_indicator_men',
        'accessible_occup_indicator_women',
        'logo'
        )
        
    if accessiable:
        values_to_remove = ('accessible_panel_men','accessible_vacant_indicator_men','accessible_occup_indicator_men','accessible_panel_women','accessible_vacant_indicator_women','accessible_occup_indicator_women')
        state.hidden_tags = (x for x in state.hidden_tags if x not in values_to_remove)
        new_hidden_elements = tuple(x for x in hidden_elements if x not in values_to_remove)
        [state.bg_canvas.itemconfigure(tag, state='hidden') for tag in new_hidden_elements]
        show_elements=(
        'accessible_panel_men',
        'accessible_vacant_indicator_men',
        'accessible_occup_indicator_men',
        'accessible_panel_women',
        'accessible_vacant_indicator_women',
        'accessible_occup_indicator_women',
        'Cubiculs_WOMEN',
        'Cubiculs_MEN',
        'graph_w_GREEN',
        'graph_w_RED',
        'graph_M_GREEN',
        'graph_M_RED',
        
        )
        [state.bg_canvas.itemconfigure(tag, state='normal') for tag in show_elements]
        state.current_mode = 'both_accessible'
    else:
        [state.bg_canvas.itemconfigure(tag, state='hidden') for tag in hidden_elements]
    
        show_elements=(
            'Cubiculs_WOMEN',
            'Cubiculs_MEN',
            'graph_w_GREEN',
            'graph_w_RED',
            'graph_M_GREEN',
            'graph_M_RED',
            
            )
        [state.bg_canvas.itemconfigure(tag, state='normal') for tag in show_elements]
    
        state.current_mode = 'both'
    #upload_background_image(os.path.join('vacantview', IMG_DIR,'BOTH.jpg'))
    

def custom_mode(context=False):
    if context:
        hidden_elements=(
            'graph_M_GREEN',
            'graph_M_RED',
            'graph_w_GREEN',
            'graph_w_RED',
            'h1',
            'h2_v',
            'h2_o',
            'h2_v2',
            'h2_o2',
            'v_line',
            'figure_women',
            'figure_men',
            'accessible_panel_men',
            'accessible_panel_women',
            'accessible_vacant_indicator_men',
            'accessible_vacant_indicator_women',
            'accessible_occup_indicator_men',
            'accessible_occup_indicator_women',
            )

        [state.bg_canvas.itemconfigure(tag, state='normal') for tag in hidden_elements]
        
    else:
        [state.bg_canvas.itemconfigure(tag, state='hidden') for tag in state.hidden_tags]
    state.current_mode = 'custom'
    set_canvas_background_color('background', "#00436e")