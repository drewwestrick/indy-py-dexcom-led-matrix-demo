"""
Display rendering for Galactic Unicorn
Handles all graphics rendering logic for glucose display with custom fonts
"""

# Import custom font system
try:
    from font import CUSTOM_FONT, draw_char_blocks
except ImportError:
    CUSTOM_FONT = {}
    draw_char_blocks = None

# Display configuration
DISPLAY_X = 6                   # X offset (pixels from left edge, for centering)
DISPLAY_Y = 0                   # Y offset (pixels from top edge)
CUSTOM_FONT_CHAR_WIDTH = 6      # Width of each digit in custom font
CUSTOM_FONT_SPACING = 0         # Additional spacing between font characters

# Fallback for built-in font
DISPLAY_SCALE = 2
DISPLAY_SCALE_ARROW = 1

# Colors (RGB tuples)
COLOR_WHITE = (255, 255, 255)
COLOR_RED = (255, 0, 0)
COLOR_YELLOW = (255, 200, 0)
COLOR_GREEN = (0, 255, 0)

# Glucose thresholds (mg/dL)
GLUCOSE_LOW = 70
GLUCOSE_HIGH = 180

class Display:
    """
    Display manager for glucose readings with custom pixel art fonts
    
    Renders 3-digit glucose values with color coding and custom trend arrows
    on a 53x11 LED matrix. Supports custom block-based fonts defined in font.py.
    """
    
    def __init__(self, galactic_unicorn, picographics, digit_spacing=1):
        """
        Initialize display
        
        Args:
            galactic_unicorn: GalacticUnicorn instance
            picographics: PicoGraphics instance
            digit_spacing: Pixel gap between digits (default: 1)
        """
        self.gu = galactic_unicorn
        self.graphics = picographics
        self.digit_spacing = digit_spacing
    
    def get_glucose_color(self, glucose_value):
        """
        Determine display color based on glucose value
        
        Args:
            glucose_value: Glucose in mg/dL (or None)
            
        Returns:
            RGB tuple: RED (<70), YELLOW (>180), GREEN (70-180), or WHITE (None)
        """
        if glucose_value is None:
            return COLOR_WHITE
        elif glucose_value < GLUCOSE_LOW:
            return COLOR_RED
        elif glucose_value > GLUCOSE_HIGH:
            return COLOR_YELLOW
        else:
            return COLOR_GREEN
    
    def get_trend_arrow(self, glucose_trend):
        """
        Convert Dexcom trend string to custom arrow symbol key
        
        Args:
            glucose_trend: Dexcom trend string (e.g., "DoubleUp", "Flat")
            
        Returns:
            str: Symbol key for CUSTOM_FONT (e.g., "double_up", "flat")
        """
        if not glucose_trend:
            return "flat"
        
        trend_map = {
            "DoubleUp": "double_up",          # ⇈ >2 mg/dL/min
            "SingleUp": "single_up",          # ↑ 1-2 mg/dL/min
            "FortyFiveUp": "forty_five_up",   # ↗ 0.5-1 mg/dL/min
            "Flat": "flat",                   # → ±0.5 mg/dL/min
            "FortyFiveDown": "forty_five_down",   # ↘ 0.5-1 mg/dL/min
            "SingleDown": "single_down",      # ↓ 1-2 mg/dL/min
            "DoubleDown": "double_down",      # ⇊ <-2 mg/dL/min
            "NotComputable": "flat",          # Unknown - show flat
            "RateOutOfRange": "flat"          # Unknown - show flat
        }
        
        return trend_map.get(glucose_trend, "flat")
    
    def draw_custom_text(self, text, x, y, color):
        """
        Draw text using custom block-based font
        
        Args:
            text: String to render (e.g., " 85")
            x: Starting X coordinate
            y: Starting Y coordinate
            color: RGB tuple for text color
            
        Returns:
            int: X coordinate after last character (for positioning next element)
        """
        if not CUSTOM_FONT or not draw_char_blocks:
            # Fallback to built-in font if custom font unavailable
            self.graphics.set_pen(self.graphics.create_pen(*color))
            self.graphics.text(text, x, y, scale=DISPLAY_SCALE)
            return x + len(text) * 12
        
        current_x = x
        for char in text:
            if char in CUSTOM_FONT:
                pen = self.graphics.create_pen(*color)
                draw_char_blocks(self.graphics, CUSTOM_FONT[char], current_x, y, pen)
                current_x += CUSTOM_FONT_CHAR_WIDTH + self.digit_spacing
            else:
                # Skip unknown characters but reserve space
                current_x += CUSTOM_FONT_CHAR_WIDTH + self.digit_spacing
        
        return current_x
    
    def draw_glucose(self, glucose_value, glucose_trend):
        """
        Render complete glucose display: value + trend arrow
        
        Displays a right-aligned 3-digit glucose value in color-coded custom font,
        followed by a custom pixel art trend arrow. Layout:
        - Position: 6px offset from left (DISPLAY_X) for centering on 53x11 matrix
        - Format: "###" (3 digits, space-padded) + 2px gap + arrow symbol
        - Colors: Red (<70), Green (70-180), Yellow (>180 mg/dL)
        
        Args:
            glucose_value: Glucose reading in mg/dL (or None if unavailable)
            glucose_trend: Dexcom trend string (e.g., "DoubleUp", "Flat")
        """
        # Clear display with black background
        self.graphics.set_pen(0)
        self.graphics.clear()
        
        if glucose_value is not None:
            glucose_color = self.get_glucose_color(glucose_value)
            
            # Right-align glucose value in 3-digit space
            # Examples: "120" → "120", "85" → " 85", "9" → "  9"
            glucose_str = str(glucose_value)
            while len(glucose_str) < 3:
                glucose_str = ' ' + glucose_str
            
            if CUSTOM_FONT and draw_char_blocks:
                # Render custom font digits
                end_x = self.draw_custom_text(glucose_str, DISPLAY_X, DISPLAY_Y, glucose_color)
                
                # Render custom arrow symbol
                arrow_key = self.get_trend_arrow(glucose_trend)
                if arrow_key in CUSTOM_FONT:
                    arrow_x = end_x + 2  # 2px gap between glucose and arrow
                    arrow_y = DISPLAY_Y
                    pen = self.graphics.create_pen(*glucose_color)
                    draw_char_blocks(self.graphics, CUSTOM_FONT[arrow_key], arrow_x, arrow_y, pen)
            else:
                # Fallback to built-in font (if custom font fails to load)
                self.graphics.set_pen(self.graphics.create_pen(*glucose_color))
                self.graphics.text(glucose_str, DISPLAY_X, DISPLAY_Y, scale=DISPLAY_SCALE)
        else:
            # No data available - show placeholder
            self.graphics.set_pen(self.graphics.create_pen(*COLOR_WHITE))
            self.graphics.text("---", 10, 0, scale=DISPLAY_SCALE)
        
        # Push frame to LED matrix
        self.gu.update(self.graphics)
