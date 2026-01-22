import customtkinter as ctk


# COLOR CHOICE - White & Purple




class Colors:
    PRIMARY = "#8B5CF6"          #
    PRIMARY_DARK = "#7C3AED"    
    PRIMARY_LIGHT = "#A78BFA"    
   
    BG_WHITE = "#FFFFFF"        
    BG_LIGHT = "#F9FAFB"        
    BG_GRAY = "#F3F4F6"          
   
    TEXT_PRIMARY = "#111827"    
    TEXT_SECONDARY = "#6B7280"  
    TEXT_WHITE = "#FFFFFF"      
   
    SUCCESS = "#10B981"        
    WARNING = "#F59E0B"          
    ERROR = "#EF4444"            
    INFO = "#3B82F6"            
   
    BORDER_LIGHT = "#E5E7EB"    
    BORDER_DARK = "#D1D5DB"      






class Fonts:


    FAMILY = "Segoe UI"          
    FAMILY_BOLD = "Segoe UI Bold"


    TITLE = 24                  
    HEADING = 18                
    SUBHEADING = 16            
    NORMAL = 14                  
    SMALL = 12                  
    TINY = 10                    






class Layout:




    PADDING_SMALL = 10
    PADDING_MEDIUM = 20
    PADDING_LARGE = 30
   
    MARGIN_SMALL = 5
    MARGIN_MEDIUM = 10
    MARGIN_LARGE = 20
   
    RADIUS_SMALL = 8
    RADIUS_MEDIUM = 12
    RADIUS_LARGE = 16
   
    BUTTON_HEIGHT = 40
    INPUT_HEIGHT = 40
    CARD_WIDTH = 250
    CARD_HEIGHT = 300
   
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 700
    MIN_WIDTH = 800
    MIN_HEIGHT = 600




def setup_theme():
   
    ctk.set_appearance_mode("light")
   
    ctk.set_default_color_theme("blue")
    print("✅ Theme configured: White & Purple")




def get_button_style(variant="primary"):


    styles = {
        "primary": {
            "fg_color": Colors.PRIMARY,
            "hover_color": Colors.PRIMARY_DARK,
            "text_color": Colors.TEXT_WHITE,
            "corner_radius": Layout.RADIUS_MEDIUM,
            "height": Layout.BUTTON_HEIGHT,
            "font": (Fonts.FAMILY, Fonts.NORMAL, "bold")
        },
        "secondary": {
            "fg_color": Colors.BG_GRAY,
            "hover_color": Colors.BORDER_DARK,
            "text_color": Colors.TEXT_PRIMARY,
            "corner_radius": Layout.RADIUS_MEDIUM,
            "height": Layout.BUTTON_HEIGHT,
            "font": (Fonts.FAMILY, Fonts.NORMAL)
        },
        "success": {
            "fg_color": Colors.SUCCESS,
            "hover_color": "#059669",
            "text_color": Colors.TEXT_WHITE,
            "corner_radius": Layout.RADIUS_MEDIUM,
            "height": Layout.BUTTON_HEIGHT,
            "font": (Fonts.FAMILY, Fonts.NORMAL, "bold")
        },
        "danger": {
            "fg_color": Colors.ERROR,
            "hover_color": "#DC2626",
            "text_color": Colors.TEXT_WHITE,
            "corner_radius": Layout.RADIUS_MEDIUM,
            "height": Layout.BUTTON_HEIGHT,
            "font": (Fonts.FAMILY, Fonts.NORMAL, "bold")
        }
    }
    return styles.get(variant, styles["primary"])


def get_input_style():


    return {
        "fg_color": Colors.BG_WHITE,
        "border_color": Colors.BORDER_LIGHT,
        "border_width": 2,
        "corner_radius": Layout.RADIUS_SMALL,
        "height": Layout.INPUT_HEIGHT,
        "font": (Fonts.FAMILY, Fonts.NORMAL),
        "text_color": Colors.TEXT_PRIMARY
    }


def get_card_style():


    return {
        "fg_color": Colors.BG_WHITE,
        "corner_radius": Layout.RADIUS_MEDIUM,
        "border_width": 1,
        "border_color": Colors.BORDER_LIGHT
    }


def get_label_style(variant="normal"):


    styles = {
        "title": {
            "text_color": Colors.TEXT_PRIMARY,
            "font": (Fonts.FAMILY_BOLD, Fonts.TITLE, "bold")
        },
        "heading": {
            "text_color": Colors.TEXT_PRIMARY,
            "font": (Fonts.FAMILY_BOLD, Fonts.HEADING, "bold")
        },
        "normal": {
            "text_color": Colors.TEXT_PRIMARY,
            "font": (Fonts.FAMILY, Fonts.NORMAL)
        },
        "small": {
            "text_color": Colors.TEXT_SECONDARY,
            "font": (Fonts.FAMILY, Fonts.SMALL)
        }
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
   
    window.configure(fg_color=Colors.BG_LIGHT)
