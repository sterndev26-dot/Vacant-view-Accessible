import arabic_reshaper
from bidi.algorithm import get_display

def reshape_rtl_text(text):
    # Use arabic_reshaper to reshape Arabic (or similar) text for correct display
    reshaped_text = arabic_reshaper.reshape(text)
    # Use get_display to reorder characters properly for right-to-left rendering
    return get_display(reshaped_text)

def is_rtl_char(char):
    # Check if a single character is in the Unicode range commonly used for RTL scripts
    # '\u0590' to '\u08FF' covers Hebrew, Arabic, and related blocks
    return '\u0590' <= char <= '\u08FF'

def is_rtl_text(text):
    # Check if any character in the text belongs to the RTL character range
    # If yes, treat the entire string as RTL
    return any(is_rtl_char(c) for c in text)

def prepare_text_for_widget(text: str) -> str:
  
    if not text:
        return text
    if is_rtl_text(text):
        reshaped = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped)
        return bidi_text
    else:
        return text
     
    
    
def update_canvas_texts(canvas):
    
    tags_to_update = [
        'h1', 'h2_v', 'h2_o', 'h2_v2', 'h2_o2', 'h2_v_add', 'h2_o_add',
        'h2_v2_add', 'h2_o2_add', 'TOTAL_1', 'TOTAL_2', 'TOTAL_3', 'TOTAL_4',
        'cleaning_message_1', 'cleaning_message_2', 'custom_title_text',
        'cleaning_message_1_add', 'cleaning_message_2_add', 'h2_v2_add'
    ]

   
    for tag in tags_to_update:
      
        items = canvas.find_withtag(tag)
        for item in items:
           
            if canvas.type(item) == "text":
                
                current_text = canvas.itemcget(item, 'text')
                print(f"Checking tag: {tag} - Current text: {current_text}")

           
                if current_text == "TOTAL":
                    new_text = prepare_text_for_widget(_("TOTAL"))
                elif current_text == "VACANT":
                    new_text = prepare_text_for_widget(_("VACANT"))
                elif current_text == "OCCUPIED":
                    new_text = prepare_text_for_widget(_("OCCUPIED"))
                elif current_text == "WC IS BEING CLEANED, PLEASE USE WC IN FLOOR #1":
                    new_text = prepare_text_for_widget(_("WC IS BEING CLEANED, PLEASE USE WC IN FLOOR #1"))
                elif current_text == "WC IS BEING CLEANED, PLEASE USE WC IN FLOOR #2":
                    new_text = prepare_text_for_widget(_("WC IS BEING CLEANED, PLEASE USE WC IN FLOOR #2"))
                elif current_text == "CUSTOM TEXT":
                    new_text = prepare_text_for_widget(_("CUSTOM TEXT"))
                elif current_text == "WASHROOM OCCUPANCY":
                    new_text = prepare_text_for_widget(_("WASHROOM OCCUPANCY"))
                elif current_text == "MEN":
                    new_text = prepare_text_for_widget(_("MEN"))
                elif current_text == "WOMEN":
                    new_text = prepare_text_for_widget(_("WOMEN"))
                else:
                    
                    new_text = current_text

               
                canvas.itemconfig(item, text=new_text)
                print(f"Updated text for tag {tag}: {new_text}")