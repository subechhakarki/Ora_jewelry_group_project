# test_theme.py

import customtkinter as ctk
from themes.theme import (
    setup_theme, 
    configure_window, 
    get_button_style, 
    get_input_style,
    get_label_style,
    Colors,
    Layout
)

def test_theme():
    """
    Test the theme configuration with sample UI elements
    """
    # Setup theme
    setup_theme()
    
    # Create main window
    root = ctk.CTk()
    configure_window(root, "ORA Jewelry - Theme Test")
    
    # Create main frame
    main_frame = ctk.CTkFrame(root, fg_color=Colors.BG_WHITE, corner_radius=0)
    main_frame.pack(fill="both", expand=True, padx=Layout.PADDING_LARGE, pady=Layout.PADDING_LARGE)
    
    # Title
    title = ctk.CTkLabel(main_frame, text="🎨 ORA Jewelry Theme Test", **get_label_style("title"))
    title.pack(pady=(Layout.PADDING_LARGE, Layout.PADDING_MEDIUM))
    
    # Heading
    heading = ctk.CTkLabel(main_frame, text="Button Variants", **get_label_style("heading"))
    heading.pack(pady=Layout.PADDING_SMALL)
    
    # Button frame
    button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    button_frame.pack(pady=Layout.PADDING_MEDIUM)
    
    # Primary Button
    btn_primary = ctk.CTkButton(button_frame, text="Primary Button", **get_button_style("primary"))
    btn_primary.pack(side="left", padx=Layout.PADDING_SMALL)
    
    # Secondary Button
    btn_secondary = ctk.CTkButton(button_frame, text="Secondary Button", **get_button_style("secondary"))
    btn_secondary.pack(side="left", padx=Layout.PADDING_SMALL)
    
    # Success Button
    btn_success = ctk.CTkButton(button_frame, text="Success Button", **get_button_style("success"))
    btn_success.pack(side="left", padx=Layout.PADDING_SMALL)
    
    # Danger Button
    btn_danger = ctk.CTkButton(button_frame, text="Danger Button", **get_button_style("danger"))
    btn_danger.pack(side="left", padx=Layout.PADDING_SMALL)
    
    # Input heading
    input_heading = ctk.CTkLabel(main_frame, text="Input Fields", **get_label_style("heading"))
    input_heading.pack(pady=(Layout.PADDING_LARGE, Layout.PADDING_SMALL))
    
    # Input fields
    entry1 = ctk.CTkEntry(main_frame, placeholder_text="Email", width=300, **get_input_style())
    entry1.pack(pady=Layout.PADDING_SMALL)
    
    entry2 = ctk.CTkEntry(main_frame, placeholder_text="Password", show="*", width=300, **get_input_style())
    entry2.pack(pady=Layout.PADDING_SMALL)
    
    # Status message
    status = ctk.CTkLabel(main_frame, text="✅ Theme loaded successfully!", **get_label_style("small"))
    status.pack(pady=Layout.PADDING_LARGE)
    
    root.mainloop()

if __name__ == "__main__":
    test_theme()