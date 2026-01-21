# themes/theme.py

import customtkinter as ctk

# ============================================
# COLOR PALETTE - White & Purple Theme
# ============================================

class Colors:
    """
    ORA Jewelry Store Color Scheme
    Primary: Purple | Background: White
    """
    # Primary Colors
    PRIMARY = "#8B5CF6"          # Purple
    PRIMARY_DARK = "#7C3AED"     # Darker Purple (hover)
    PRIMARY_LIGHT = "#A78BFA"    # Light Purple
    
    # Background Colors
    BG_WHITE = "#FFFFFF"         # Pure White
    BG_LIGHT = "#F9FAFB"         # Off-White
    BG_GRAY = "#F3F4F6"          # Light Gray
    
    # Text Colors
    TEXT_PRIMARY = "#111827"     # Dark Gray (main text)
    TEXT_SECONDARY = "#6B7280"   # Medium Gray (secondary text)
    TEXT_WHITE = "#FFFFFF"       # White text
    
    # Status Colors
    SUCCESS = "#10B981"          # Green
    WARNING = "#F59E0B"          # Orange
    ERROR = "#EF4444"            # Red
    INFO = "#3B82F6"             # Blue
    
    # Border Colors
    BORDER_LIGHT = "#E5E7EB"     # Light border
    BORDER_DARK = "#D1D5DB"      # Darker border

# ============================================
# FONTS
# ============================================

class Fonts:
    """
    Font configurations for the application
    """
    # Font Families
    FAMILY = "Segoe UI"          # Default Windows font
    FAMILY_BOLD = "Segoe UI Bold"
    
    # Font Sizes
    TITLE = 24                   # Page titles
    HEADING = 18                 # Section headings
    SUBHEADING = 16              # Subheadings
    NORMAL = 14                  # Regular text
    SMALL = 12                   # Small text
    TINY = 10                    # Very small text

# ============================================
# SPACING & DIMENSIONS
# ============================================

class Layout:
    """
    Layout constants for consistent spacing
    """
    # Padding
    PADDING_SMALL = 10
    PADDING_MEDIUM = 20
    PADDING_LARGE = 30
    
    # Margins
    MARGIN_SMALL = 5
    MARGIN_MEDIUM = 10
    MARGIN_LARGE = 20
    
    # Border Radius
    RADIUS_SMALL = 8
    RADIUS_MEDIUM = 12
    RADIUS_LARGE = 16
    
    # Component Sizes
    BUTTON_HEIGHT = 40
    INPUT_HEIGHT = 40
    CARD_WIDTH = 250
    CARD_HEIGHT = 300
    
    # Window Sizes
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 700
    MIN_WIDTH = 800
    MIN_HEIGHT = 600

# ============================================
# THEME SETUP FUNCTION
# ============================================

def setup_theme():
    """
    Initialize CustomTkinter with ORA Jewelry theme
    """
    # Set appearance mode (light/dark)
    ctk.set_appearance_mode("light")  # Force light mode for white background
    
    # Set default color theme
    ctk.set_default_color_theme("blue")  # Base theme (we'll override with custom colors)
    
    print("✅ Theme configured: White & Purple")

# ============================================
# REUSABLE STYLE FUNCTIONS
# ============================================

def get_button_style(variant="primary"):
    """
    Get button styling based on variant
    
    Variants:
    - primary: Purple button (main actions)
    - secondary: Gray button (secondary actions)
    - success: Green button (confirmations)
    - danger: Red button (deletions)
    """
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
    """
    Get input field styling
    """
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
    """
    Get card/frame styling for product cards
    """
    return {
        "fg_color": Colors.BG_WHITE,
        "corner_radius": Layout.RADIUS_MEDIUM,
        "border_width": 1,
        "border_color": Colors.BORDER_LIGHT
    }

def get_label_style(variant="normal"):
    """
    Get label styling based on variant
    
    Variants:
    - title: Large title text
    - heading: Section heading
    - normal: Regular text
    - small: Small text
    """
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

# ============================================
# WINDOW CONFIGURATION
# ============================================

def configure_window(window, title="ORA Jewelry Store"):
    """
    Configure main window properties
    """
    window.title(title)
    window.geometry(f"{Layout.WINDOW_WIDTH}x{Layout.WINDOW_HEIGHT}")
    window.minsize(Layout.MIN_WIDTH, Layout.MIN_HEIGHT)
    
    # Center window on screen
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - Layout.WINDOW_WIDTH) // 2
    y = (screen_height - Layout.WINDOW_HEIGHT) // 2
    window.geometry(f"{Layout.WINDOW_WIDTH}x{Layout.WINDOW_HEIGHT}+{x}+{y}")
    
    # Set background color
    window.configure(fg_color=Colors.BG_LIGHT)