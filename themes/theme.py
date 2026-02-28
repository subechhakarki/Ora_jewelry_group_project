import customtkinter as ctk
 
class Colors:
    PRIMARY = "#3B1D6F"        
    PRIMARY_DARK = "#2A124F"  
    PRIMARY_LIGHT = "#E9D5FF"    


    GOLD = "#D6B15A"
    GOLD_DARK = "#B9923D"
    GOLD_SOFT = "#F5E6B8"


    BG_WHITE = "#FFFFFF"
    BG_IVORY = "#FCFAF7"
    BG_LIGHT = "#F7F5F2"
    BG_GRAY = "#F2F1EF"


    TEXT_PRIMARY = "#141414"
    TEXT_SECONDARY = "#6B6B6B"
    TEXT_MUTED = "#8A8A8A"
    TEXT_WHITE = "#FFFFFF"


    SUCCESS = "#14B8A6"
    WARNING = "#F59E0B"
    ERROR = "#EF4444"
    INFO = "#3B82F6"




    BORDER_LIGHT = "#E7E3DA"
    BORDER_DARK = "#D3CBBF"




class Fonts:
    FAMILY = "Segoe UI"
    FAMILY_BOLD = "Segoe UI Semibold"


    TITLE = 26
    HEADING = 18
    SUBHEADING = 16
    NORMAL = 14
    SMALL = 12
    TINY = 10




class Layout:
    PADDING_SMALL = 10
    PADDING_MEDIUM = 20
    PADDING_LARGE = 30


    MARGIN_SMALL = 6
    MARGIN_MEDIUM = 12
    MARGIN_LARGE = 22


    RADIUS_SMALL = 10
    RADIUS_MEDIUM = 14
    RADIUS_LARGE = 18


    BUTTON_HEIGHT = 42
    INPUT_HEIGHT = 42


    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 700
    MIN_WIDTH = 800
    MIN_HEIGHT = 600




def setup_theme():
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    print("Theme configured: Luxury Ivory / Royal Purple / Gold")




def get_button_style(variant="primary"):
    styles = {
        "primary": {
            "fg_color": Colors.PRIMARY,
            "hover_color": Colors.PRIMARY_DARK,
            "text_color": Colors.TEXT_WHITE,
            "corner_radius": Layout.RADIUS_MEDIUM,
            "height": Layout.BUTTON_HEIGHT,
            "font": (Fonts.FAMILY_BOLD, Fonts.NORMAL),
        },


        "gold": {
            "fg_color": Colors.GOLD,
            "hover_color": Colors.GOLD_DARK,
            "text_color": Colors.TEXT_PRIMARY,
            "corner_radius": Layout.RADIUS_MEDIUM,
            "height": Layout.BUTTON_HEIGHT,
            "font": (Fonts.FAMILY_BOLD, Fonts.NORMAL),
        },


        "secondary": {
            "fg_color": Colors.BG_WHITE,
            "hover_color": Colors.BG_GRAY,
            "text_color": Colors.TEXT_PRIMARY,
            "border_color": Colors.BORDER_DARK,
            "border_width": 1,
            "corner_radius": Layout.RADIUS_MEDIUM,
            "height": Layout.BUTTON_HEIGHT,
            "font": (Fonts.FAMILY, Fonts.NORMAL),
        },


        "success": {
            "fg_color": Colors.SUCCESS,
            "hover_color": "#0F9488",
            "text_color": Colors.TEXT_WHITE,
            "corner_radius": Layout.RADIUS_MEDIUM,
            "height": Layout.BUTTON_HEIGHT,
            "font": (Fonts.FAMILY_BOLD, Fonts.NORMAL),
        },


        "danger": {
            "fg_color": Colors.ERROR,
            "hover_color": "#DC2626",
            "text_color": Colors.TEXT_WHITE,
            "corner_radius": Layout.RADIUS_MEDIUM,
            "height": Layout.BUTTON_HEIGHT,
            "font": (Fonts.FAMILY_BOLD, Fonts.NORMAL),
        },
    }
    return styles.get(variant, styles["primary"])




def get_input_style():
    return {
        "fg_color": Colors.BG_WHITE,
        "border_color": Colors.BORDER_LIGHT,
        "border_width": 1,
        "corner_radius": Layout.RADIUS_SMALL,
        "height": Layout.INPUT_HEIGHT,
        "font": (Fonts.FAMILY, Fonts.NORMAL),
        "text_color": Colors.TEXT_PRIMARY,
        "placeholder_text_color": Colors.TEXT_MUTED,
    }




def get_card_style():
    return {
        "fg_color": Colors.BG_WHITE,
        "corner_radius": Layout.RADIUS_LARGE,
        "border_width": 1,
        "border_color": Colors.BORDER_LIGHT,
    }




def get_label_style(variant="normal"):
    styles = {
        "title": {
            "text_color": Colors.TEXT_PRIMARY,
            "font": (Fonts.FAMILY_BOLD, Fonts.TITLE),
        },
        "heading": {
            "text_color": Colors.TEXT_PRIMARY,
            "font": (Fonts.FAMILY_BOLD, Fonts.HEADING),
        },
        "subheading": {
            "text_color": Colors.TEXT_PRIMARY,
            "font": (Fonts.FAMILY_BOLD, Fonts.SUBHEADING),
        },
        "normal": {
            "text_color": Colors.TEXT_PRIMARY,
            "font": (Fonts.FAMILY, Fonts.NORMAL),
        },
        "small": {
            "text_color": Colors.TEXT_SECONDARY,
            "font": (Fonts.FAMILY, Fonts.SMALL),
        },
        "accent": {
            "text_color": Colors.GOLD_DARK,
            "font": (Fonts.FAMILY_BOLD, Fonts.SMALL),
        },
    }
    return styles.get(variant, styles["normal"])




def configure_window(window, title="ORA Jewelry Store"):
    window.title(title)
    window.geometry(f"{Layout.WINDOW_WIDTH}x{Layout.WINDOW_HEIGHT}")
    window.minsize(Layout.MIN_WIDTH, Layout.MIN_HEIGHT)


    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - Layout.WINDOW_WIDTH) // 2
    y = (screen_height - Layout.WINDOW_HEIGHT) // 2
    window.geometry(f"{Layout.WINDOW_WIDTH}x{Layout.WINDOW_HEIGHT}+{x}+{y}")


    window.configure(fg_color=Colors.BG_IVORY)





