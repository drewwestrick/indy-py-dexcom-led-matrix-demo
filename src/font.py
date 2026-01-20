"""
Custom font definitions for glucose display
Format: Each character is defined as a list of blocks (x, y, width, height)
"""

# 6x10 pixel font - optimized block format
CUSTOM_FONT = {
    '1': [
    (2, 0, 2, 10),  # Block 1
    (0, 2, 2, 2),  # Block 2
    (0, 8, 2, 2),  # Block 3
    (4, 8, 2, 2),  # Block 4
    ],
}

# Arrow definitions (can use same format)
CUSTOM_ARROWS = {
    'double_up': [],
    'single_up': [],
    'forty_five_up': [],
    'flat': [],
    'forty_five_down': [],
    'single_down': [],
    'double_down': [],
}

# Helper function to draw a character from block list
def draw_char_blocks(graphics, blocks, x_offset, y_offset, color):
    """
    Draw a character defined by blocks at the given offset
    
    Args:
        graphics: PicoGraphics instance
        blocks: List of (x, y, width, height) tuples
        x_offset: X position to draw at
        y_offset: Y position to draw at
        color: Pen color to use
    """
    graphics.set_pen(color)
    for x, y, w, h in blocks:
        for dy in range(h):
            for dx in range(w):
                graphics.pixel(x_offset + x + dx, y_offset + y + dy)

# Helper function to draw from bitmap
def draw_char_bitmap(graphics, bitmap, x_offset, y_offset, color):
    """
    Draw a character defined by 2D bitmap at the given offset
    
    Args:
        graphics: PicoGraphics instance
        bitmap: 2D array where 1 = pixel on, 0 = pixel off
        x_offset: X position to draw at
        y_offset: Y position to draw at
        color: Pen color to use
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
