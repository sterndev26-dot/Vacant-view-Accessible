1. Main Title (title_editor.py)

edit_main_title_text(new_text)
Changes the main title text on the screen.

change_main_title_color(color)
Sets the title text color.

change_main_title_font(font_name)
Applies the selected font to the title.

change_main_title_font_size(size)
Changes the title font size.

2. Status Color Scheme (status_color_scheme.py)

set_available_color(color)
Sets the "Available" status color (default: green).

set_occupied_color(color)
Sets the "Occupied" status color (default: red).

3. Numerical Status Indicators (status_indicators.py)

move_indicator(x, y)
Moves the indicator on the screen (drag-and-drop).

set_indicator_font(font_name)
Changes the font of the numeric indicator.

set_indicator_font_size(size)
Changes the font size of the indicator.

set_indicator_shape(shape)
Sets the shape: 'circle', 'square', 'rounded'.

set_number_color(color)
Changes the number color inside the indicator.

set_background_color(color)
Changes the background color of the indicator.

4. Indicator Border Colors (occupancy_border_colors.py)

toggle_dynamic_border(enabled: bool)
Enables or disables dynamic border coloring.

set_border_color_thresholds(ranges: list)
Configures color thresholds based on occupancy level.

5. Images and Logos (branding_images.py)

select_logo(type)
Sets the logo: 'stern' (default) or 'user'.

upload_background_image(path)
Uploads a custom background image.

set_default_background(gender: str)
Sets the default background image: 'MEN', 'WOMEN', 'BOTH'.

6. Cleaning Mode Message (cleaning_mode.py)

set_cleaning_text(message)
Changes the cleaning mode message text.

set_cleaning_text_color(color)
Sets the text color.

set_cleaning_font(font_name)
Applies a font to the message.

set_cleaning_font_size(size)
Sets the font size.

7. Language Support (language_support.py)

set_interface_language(lang_code)
Sets the interface language (supports both LTR and RTL).

add_secondary_title(text, position, color, font, size)
Adds a secondary title under the main one.

8. Layout Management (layout_management.py)

enable_element_drag(element_type)
Enables drag-and-drop for a specific element type: 'title', 'logo', 'status', 'cleaning'.

9. Communication Blocking (Admin) (communication_blocking.py)

toggle_communication(module: str, enabled: bool)
Enables or disables a module: 'bluetooth', 'wifi', 'gps', 'other'.
Requires admin password input.

10. Export/Import Design (design_import_export.py)

export_layout(path)
Saves the current layout and settings to a file.

import_layout(path)
Loads a previously saved design and configuration.

