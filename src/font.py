"""
Custom font definitions for glucose display
Defines pixel art fonts and arrow symbols using optimized block format

Block format: Each character is a list of (x, y, width, height) tuples representing
rectangular blocks. This is more memory-efficient than storing individual pixels
and faster to render on MicroPython.

Font Design:
- Digits (0-9): 6x10 pixels, blocky LED-style design
- Space: Empty (for padding)
- Arrows: 10px wide, variable height (10-21px for double arrows)
  - double_up/down: 17x10 (tallest)
  - single_up/down: 10x10
  - forty_five_up/down: 10x10
  - flat: 10x10

Use font_editor.py in host/ to create or modify characters.
"""

# 6x10 pixel blocky font - optimized block format
# Each digit designed for LED matrix aesthetic
CUSTOM_FONT = {
    ' ': [],  # Space character (empty, reserves width for padding)
    '0': [
    (0, 0, 6, 2),  # Block 1
    (0, 2, 2, 8),  # Block 2
    (4, 2, 2, 8),  # Block 3
    (2, 8, 2, 2),  # Block 4
    ],
    '1': [
    (2, 0, 2, 10), # Block 1
    (0, 2, 2, 2),  # Block 2
    (0, 8, 2, 2),  # Block 3
    (4, 8, 2, 2),  # Block 4
    ],
    '2': [
    (0, 0, 6, 2),  # Block 1
    (4, 2, 2, 4),  # Block 2
    (0, 4, 4, 2),  # Block 3
    (0, 6, 2, 4),  # Block 4
    (2, 8, 4, 2),  # Block 5
    ],
    '3': [
    (0, 0, 6, 2),  # Block 1
    (4, 2, 2, 8),  # Block 2
    (0, 4, 4, 2),  # Block 3
    (0, 8, 4, 2),  # Block 4
    ],
    '4': [
    (0, 0, 2, 6),  # Block 1
    (4, 0, 2, 10), # Block 2
    (2, 4, 2, 2),  # Block 3
    ],
    '5': [
    (0, 0, 6, 2),  # Block 1
    (0, 2, 2, 4),  # Block 2
    (2, 4, 4, 2),  # Block 3
    (4, 6, 2, 4),  # Block 4
    (0, 8, 4, 2),  # Block 5
    ],
    '6': [
    (0, 0, 6, 2),  # Block 1
    (0, 2, 1, 8),  # Block 2
    (1, 4, 5, 2),  # Block 3
    (5, 6, 1, 4),  # Block 4
    (1, 8, 4, 2),  # Block 5
    ],
    '7': [
    (0, 0, 6, 2),  # Block 1
    (4, 2, 2, 8),  # Block 2
    ],
    '8': [
    (0, 0, 6, 2),  # Block 1
    (0, 2, 2, 8),  # Block 2
    (4, 2, 2, 8),  # Block 3
    (2, 4, 2, 2),  # Block 4
    (2, 8, 2, 2),  # Block 5
    ],
    '9': [
    (0, 0, 6, 2),  # Block 1
    (0, 2, 2, 4),  # Block 2
    (4, 2, 2, 8),  # Block 3
    (2, 4, 2, 2),  # Block 4
    ],
    'double_up': [
    (3, 0, 2, 10),  # Block 1
    (12, 0, 2, 10), # Block 2
    (2, 1, 1, 3),   # Block 3
    (5, 1, 1, 3),   # Block 4
    (11, 1, 1, 3),  # Block 5
    (14, 1, 1, 3),  # Block 6
    (1, 2, 1, 3),   # Block 7
    (6, 2, 1, 3),   # Block 8
    (10, 2, 1, 3),  # Block 9
    (15, 2, 1, 3),  # Block 10
    (0, 3, 1, 2),   # Block 11
    (7, 3, 1, 2),   # Block 12
    (9, 3, 1, 2),   # Block 13
    (16, 3, 1, 2),  # Block 14
    ],
    'single_up': [
    (4, 0, 2, 10), # Block 1
    (3, 1, 1, 3),  # Block 2
    (6, 1, 1, 3),  # Block 3
    (2, 2, 1, 3),  # Block 4
    (7, 2, 1, 3),  # Block 5
    (1, 3, 1, 2),  # Block 6
    (8, 3, 1, 2),  # Block 7
    ],
    'forty_five_up': [
    (2, 0, 8, 2),  # Block 1
    (6, 2, 4, 2),  # Block 2
    (4, 4, 2, 2),  # Block 3
    (8, 4, 2, 4),  # Block 4
    (2, 6, 2, 2),  # Block 5
    (0, 8, 2, 2),  # Block 6
    ],
    'flat': [
    (5, 1, 2, 2),  # Block 1
    (7, 2, 1, 6),  # Block 2
    (6, 3, 1, 6),  # Block 3
    (8, 3, 1, 4),  # Block 4
    (0, 4, 6, 2),  # Block 5
    (9, 4, 1, 2),  # Block 6
    (5, 7, 1, 2),  # Block 7
    ],
    'forty_five_down': [
    (0, 0, 2, 2),  # Block 1
    (2, 2, 2, 2),  # Block 2
    (8, 2, 2, 8),  # Block 3
    (4, 4, 2, 2),  # Block 4
    (6, 6, 2, 4),  # Block 5
    (2, 8, 4, 2),  # Block 6
    ],
    'single_down': [
    (4, 0, 2, 10),  # Block 1
    (1, 5, 2, 2),  # Block 2
    (7, 5, 2, 2),  # Block 3
    (3, 6, 1, 3),  # Block 4
    (6, 6, 1, 3),  # Block 5
    (2, 7, 1, 1),  # Block 6
    (7, 7, 1, 1),  # Block 7
    ],
    'double_down': [
    (3, 0, 2, 10),  # Block 1
    (12, 0, 2, 10), # Block 2
    (0, 5, 2, 2),   # Block 3
    (6, 5, 2, 2),   # Block 4
    (9, 5, 2, 2),   # Block 5
    (15, 5, 2, 2),  # Block 6
    (2, 6, 1, 3),   # Block 7
    (5, 6, 1, 3),   # Block 8
    (11, 6, 1, 3),  # Block 9
    (14, 6, 1, 3),  # Block 10
    (1, 7, 1, 1),   # Block 11
    (6, 7, 1, 1),   # Block 12
    (10, 7, 1, 1),  # Block 13
    (15, 7, 1, 1),  # Block 14
    ],
}

# Deprecated: Arrow definitions moved to CUSTOM_FONT above
# This dict is kept for backwards compatibility but is not used
CUSTOM_ARROWS = {
    'double_up': [],
    'single_up': [],
    'forty_five_up': [],
    'flat': [],
    'forty_five_down': [],
    'single_down': [],
    'double_down': [],
}

# Helper functions for rendering characters
# These support multiple input formats for flexibility

def draw_char_blocks(graphics, blocks, x_offset, y_offset, color):
    """
    Draw a character from optimized block format (RECOMMENDED)
    
    Most memory-efficient format. Each block is a rectangle (x, y, width, height).
    Example: [(0, 0, 6, 2), (0, 2, 2, 8)] represents two rectangles.
    
    Args:
        graphics: PicoGraphics instance
        blocks: List of (x, y, width, height) tuples defining rectangles
        x_offset: X position to draw at (pixels from left)
        y_offset: Y position to draw at (pixels from top)
        color: Pen color (created with graphics.create_pen())
    """
    graphics.set_pen(color)
    for x, y, w, h in blocks:
        for dy in range(h):
            for dx in range(w):
                graphics.pixel(x_offset + x + dx, y_offset + y + dy)

def draw_char_bitmap(graphics, bitmap, x_offset, y_offset, color):
    """
    Draw a character from 2D bitmap array (ALTERNATIVE FORMAT)
    
    Bitmap format is a 2D array where 1 = pixel on, 0 = pixel off.
    Example: [[1,1,0], [1,0,1], [0,1,1]] for a 3x3 character.
    Less efficient than blocks but easier to visualize.
    
    Args:
        graphics: PicoGraphics instance
        bitmap: 2D array where 1 = pixel on, 0 = pixel off
        x_offset: X position to draw at
        y_offset: Y position to draw at
        color: Pen color (created with graphics.create_pen())
    """
    graphics.set_pen(color)
    for y, row in enumerate(bitmap):
        for x, pixel in enumerate(row):
            if pixel:
                graphics.pixel(x_offset + x, y_offset + y)

# Helper function to draw from coordinates
def draw_char_coords(graphics, coords, x_offset, y_offset, color):
    """
    Draw a character defined by coordinate list at the given offset
    
    Args:
        graphics: PicoGraphics instance
        coords: List of (x, y) tuples
        x_offset: X position to draw at
        y_offset: Y position to draw at
        color: Pen color to use
    """
    graphics.set_pen(color)
    for x, y in coords:
        graphics.pixel(x_offset + x, y_offset + y)
