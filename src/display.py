"""
Display rendering for Galactic Unicorn
Handles all graphics and rendering logic
"""

# Import custom font
try:
    from font import CUSTOM_FONT, draw_char_blocks
except ImportError:
    CUSTOM_FONT = {}
    draw_char_blocks = None

# Display configuration
DISPLAY_X = 6
DISPLAY_Y = 0
CUSTOM_FONT_CHAR_WIDTH = 6
CUSTOM_FONT_SPACING = 0

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
    """Display manager for glucose readings"""
    
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
        """Determine glucose color based on value"""
        if glucose_value is None:
            return COLOR_WHITE
        elif glucose_value < GLUCOSE_LOW:
            return COLOR_RED
        elif glucose_value > GLUCOSE_HIGH:
            return COLOR_YELLOW
        else:
            return COLOR_GREEN
    
    def get_trend_arrow(self, glucose_trend):
        """Convert Dexcom trend to custom arrow symbol key"""
        if not glucose_trend:
            return "flat"
        
        trend_map = {
            "DoubleUp": "double_up",
            "SingleUp": "single_up",
            "FortyFiveUp": "forty_five_up",
            "Flat": "flat",
            "FortyFiveDown": "forty_five_down",
            "SingleDown": "single_down",
            "DoubleDown": "double_down",
            "NotComputable": "flat",
            "RateOutOfRange": "flat"
        }
        
        return trend_map.get(glucose_trend, "flat")
    
    def draw_custom_text(self, text, x, y, color):
        """Draw text using custom font blocks"""
        if not CUSTOM_FONT or not draw_char_blocks:
            # Fallback to built-in font
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
                current_x += CUSTOM_FONT_CHAR_WIDTH + self.digit_spacing
        
        return current_x
    
    def draw_glucose(self, glucose_value, glucose_trend):
        """
        Draw glucose data on the display
        
        Args:
            glucose_value: Glucose value in mg/dL
            glucose_trend: Dexcom trend string
        """
        self.graphics.set_pen(0)  # Black background
        self.graphics.clear()
        
        if glucose_value is not None:
            glucose_color = self.get_glucose_color(glucose_value)
            # Right-align glucose value in 3-digit space (always reserve space for hundreds digit)
            glucose_str = str(glucose_value)
            while len(glucose_str) < 3:
                glucose_str = ' ' + glucose_str
            
            if CUSTOM_FONT and draw_char_blocks:
                # Use custom font for digits
                end_x = self.draw_custom_text(glucose_str, DISPLAY_X, DISPLAY_Y, glucose_color)
                
                # Draw trend arrow symbol
                arrow_key = self.get_trend_arrow(glucose_trend)
                if arrow_key in CUSTOM_FONT:
                    # Add small gap before arrow
                    arrow_x = end_x + 2
                    arrow_y = DISPLAY_Y
                    pen = self.graphics.create_pen(*glucose_color)
                    draw_char_blocks(self.graphics, CUSTOM_FONT[arrow_key], arrow_x, arrow_y, pen)
            else:
                # Fallback to built-in font
                self.graphics.set_pen(self.graphics.create_pen(*glucose_color))
                self.graphics.text(glucose_str, DISPLAY_X, DISPLAY_Y, scale=DISPLAY_SCALE)
        else:
            # No data yet
            self.graphics.set_pen(self.graphics.create_pen(*COLOR_WHITE))
            self.graphics.text("---", 10, 0, scale=DISPLAY_SCALE)
        
        self.gu.update(self.graphics)
