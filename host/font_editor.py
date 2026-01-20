#!/usr/bin/env python3
"""
Font Editor - Paint custom characters on a variable-width grid and export to font.py format
"""

import pygame
import sys
import os

# Add src directory to path to import font
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
try:
    from font import CUSTOM_FONT
except ImportError:
    CUSTOM_FONT = {}

# Default grid dimensions
DEFAULT_GRID_WIDTH = 6
DEFAULT_GRID_HEIGHT = 10
PIXEL_SIZE = 40
BORDER_SIZE = 1

# Window dimensions (will be adjusted based on grid size)
CONTROL_PANEL_WIDTH = 400
BOTTOM_MARGIN = 100

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
GRAY = (50, 50, 50)
DARK_GRAY = (30, 30, 30)
LIGHT_GRAY = (100, 100, 100)
YELLOW = (255, 255, 0)

class FontEditor:
    def __init__(self):
        pygame.init()
        
        # Grid dimensions (variable)
        self.grid_width = DEFAULT_GRID_WIDTH
        self.grid_height = DEFAULT_GRID_HEIGHT
        
        # Calculate window size
        self.update_window_size()
        
        # Grid state - 2D array of booleans
        self.grid = [[False for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        
        # Current character being edited
        self.current_char = '0'
        
        # Available characters from font.py
        self.available_chars = sorted(CUSTOM_FONT.keys()) if CUSTOM_FONT else []
        
        # Dropdown state
        self.show_dropdown = False
        self.dropdown_scroll = 0
        self.dropdown_selected = 0
        
        # Font for text
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # Drawing state
        self.is_drawing = False
        self.draw_mode = True  # True = paint, False = erase
    
    def update_window_size(self):
        """Update window size based on current grid dimensions"""
        window_width = self.grid_width * PIXEL_SIZE + CONTROL_PANEL_WIDTH
        # Ensure minimum height for all controls (650px minimum)
        window_height = max(self.grid_height * PIXEL_SIZE + BOTTOM_MARGIN, 650)
        self.screen = pygame.display.set_mode((window_width, window_height))
        pygame.display.set_caption(f"Font Editor - {self.grid_width}x{self.grid_height} Grid")
    
    def resize_grid(self, new_width, new_height):
        """Resize the grid, preserving existing content where possible"""
        new_grid = [[False for _ in range(new_width)] for _ in range(new_height)]
        
        # Copy existing grid content
        for y in range(min(self.grid_height, new_height)):
            for x in range(min(self.grid_width, new_width)):
                new_grid[y][x] = self.grid[y][x]
        
        self.grid_width = new_width
        self.grid_height = new_height
        self.grid = new_grid
        self.update_window_size()
        
    def get_pixel_at_mouse(self, pos):
        """Convert mouse position to grid coordinates"""
        x, y = pos
        if x < 0 or x >= self.grid_width * PIXEL_SIZE or y < 0 or y >= self.grid_height * PIXEL_SIZE:
            return None
        grid_x = x // PIXEL_SIZE
        grid_y = y // PIXEL_SIZE
        return (grid_x, grid_y)
    
    def toggle_pixel(self, grid_x, grid_y, value=None):
        """Toggle or set a pixel in the grid"""
        if 0 <= grid_x < self.grid_width and 0 <= grid_y < self.grid_height:
            if value is None:
                self.grid[grid_y][grid_x] = not self.grid[grid_y][grid_x]
            else:
                self.grid[grid_y][grid_x] = value
    
    def clear_grid(self):
        """Clear all pixels"""
        self.grid = [[False for _ in range(self.grid_width)] for _ in range(self.grid_height)]
    
    def load_character(self, char_key):
        """Load a character from CUSTOM_FONT into the grid"""
        if char_key not in CUSTOM_FONT:
            print(f"Character '{char_key}' not found in font.py")
            return
        
        blocks = CUSTOM_FONT[char_key]
        if not blocks:
            print(f"Character '{char_key}' has no blocks defined")
            self.clear_grid()
            return
        
        # Calculate required grid size from blocks
        max_x = max(x + w for x, y, w, h in blocks) if blocks else 6
        max_y = max(y + h for x, y, w, h in blocks) if blocks else 10
        
        # Resize grid if needed
        if max_x > self.grid_width or max_y > self.grid_height:
            new_width = max(max_x, self.grid_width)
            new_height = max(max_y, self.grid_height)
            self.resize_grid(new_width, new_height)
        
        # Clear and load blocks into grid
        self.clear_grid()
        for x, y, w, h in blocks:
            for dy in range(h):
                for dx in range(w):
                    if y + dy < self.grid_height and x + dx < self.grid_width:
                        self.grid[y + dy][x + dx] = True
        
        self.current_char = char_key
        print(f"Loaded character '{char_key}' ({max_x}x{max_y})")
    
    def export_as_blocks(self):
        """Export grid as list of (x, y, width, height) blocks - optimized"""
        blocks = []
        visited = [[False for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                if self.grid[y][x] and not visited[y][x]:
                    # Find the largest rectangle starting at this pixel
                    width = 1
                    height = 1
                    
                    # Extend width
                    while x + width < self.grid_width and self.grid[y][x + width] and not visited[y][x + width]:
                        width += 1
                    
                    # Extend height (check if entire row can be extended)
                    can_extend = True
                    while can_extend and y + height < self.grid_height:
                        for check_x in range(x, x + width):
                            if not self.grid[y + height][check_x] or visited[y + height][check_x]:
                                can_extend = False
                                break
                        if can_extend:
                            height += 1
                    
                    # Mark all pixels in this block as visited
                    for mark_y in range(y, y + height):
                        for mark_x in range(x, x + width):
                            visited[mark_y][mark_x] = True
                    
                    blocks.append((x, y, width, height))
        
        return blocks
    
    def export_as_bitmap(self):
        """Export grid as 2D bitmap array"""
        return [[1 if self.grid[y][x] else 0 for x in range(self.grid_width)] for y in range(self.grid_height)]
    
    def export_as_coordinates(self):
        """Export as list of (x, y) coordinates"""
        coords = []
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                if self.grid[y][x]:
                    coords.append((x, y))
        return coords
    
    def print_exports(self):
        """Print all export formats to console"""
        print("\n" + "="*60)
        print(f"CHARACTER: '{self.current_char}'")
        print("="*60)
        
        # Format 1: Optimized blocks (same as pixel_designer.py)
        blocks = self.export_as_blocks()
        print("\n--- FORMAT 1: OPTIMIZED BLOCKS (recommended) ---")
        print(f"'{self.current_char}': [")
        for i, (x, y, w, h) in enumerate(blocks):
            comment = f"  # Block {i+1}"
            print(f"    ({x}, {y}, {w}, {h}),{comment}")
        print("],")
        
        # Format 2: Bitmap array
        bitmap = self.export_as_bitmap()
        print("\n--- FORMAT 2: BITMAP ARRAY ---")
        print(f"'{self.current_char}': [")
        for row in bitmap:
            print(f"    {row},")
        print("],")
        
        # Format 3: Coordinate list
        coords = self.export_as_coordinates()
        print("\n--- FORMAT 3: COORDINATE LIST ---")
        print(f"'{self.current_char}': [")
        for i in range(0, len(coords), 5):  # 5 coords per line
            chunk = coords[i:i+5]
            print(f"    {', '.join(str(c) for c in chunk)},")
        print("],")
        
        print("\n" + "="*60)
        print("Copy the format you prefer to font.py")
        print("="*60 + "\n")
    
    def draw_grid(self):
        """Draw the pixel grid"""
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                rect = pygame.Rect(
                    x * PIXEL_SIZE,
                    y * PIXEL_SIZE,
                    PIXEL_SIZE,
                    PIXEL_SIZE
                )
                
                # Draw pixel
                color = GREEN if self.grid[y][x] else DARK_GRAY
                pygame.draw.rect(self.screen, color, rect)
                
                # Draw border
                pygame.draw.rect(self.screen, GRAY, rect, BORDER_SIZE)
    
    def draw_controls(self):
        """Draw control panel"""
        panel_x = self.grid_width * PIXEL_SIZE + 20
        y_offset = 20
        
        # Title
        title = self.font.render("Font Editor", True, WHITE)
        self.screen.blit(title, (panel_x, y_offset))
        y_offset += 40
        
        # Grid size display
        size_text = self.font.render(f"Grid: {self.grid_width}x{self.grid_height}", True, YELLOW)
        self.screen.blit(size_text, (panel_x, y_offset))
        y_offset += 30
        
        # Current character
        char_text = self.font.render(f"Character: '{self.current_char}'", True, WHITE)
        self.screen.blit(char_text, (panel_x, y_offset))
        y_offset += 30
        
        # Load character dropdown
        if self.available_chars:
            load_btn_text = self.small_font.render("L: Load from font.py", True, YELLOW)
            self.screen.blit(load_btn_text, (panel_x, y_offset))
            y_offset += 25
            
            if self.show_dropdown:
                # Draw dropdown list (show up to 10 items)
                dropdown_height = min(10, len(self.available_chars))
                for i in range(dropdown_height):
                    idx = self.dropdown_scroll + i
                    if idx >= len(self.available_chars):
                        break
                    
                    char = self.available_chars[idx]
                    bg_color = LIGHT_GRAY if idx == self.dropdown_selected else DARK_GRAY
                    text_color = BLACK if idx == self.dropdown_selected else WHITE
                    
                    rect = pygame.Rect(panel_x, y_offset + i * 20, 200, 18)
                    pygame.draw.rect(self.screen, bg_color, rect)
                    pygame.draw.rect(self.screen, GRAY, rect, 1)
                    
                    item_text = self.small_font.render(char, True, text_color)
                    self.screen.blit(item_text, (panel_x + 5, y_offset + i * 20))
                
                y_offset += dropdown_height * 20 + 10
        
        y_offset += 15
        
        # Instructions
        instructions = [
            "CONTROLS:",
            "Click: Paint pixel",
            "Right-click: Erase pixel",
            "Drag: Paint/erase multiple",
            "",
            "C: Clear grid",
            "E: Export to console",
            "L: Toggle load dropdown",
            "UP/DOWN: Navigate dropdown",
            "ENTER: Load selected",
            "",
            "W/S: Width +/- 1",
            "H/J: Height +/- 1",
            "R: Reset to 6x10",
            "",
            "0-9: Set character 0-9",
            "A-Z: Set character A-Z",
            "",
            "ESC/Q: Quit",
        ]
        
        for instruction in instructions:
            text = self.small_font.render(instruction, True, LIGHT_GRAY if instruction else WHITE)
            self.screen.blit(text, (panel_x, y_offset))
            y_offset += 22
    
    def handle_events(self):
        """Handle user input"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    return False
                
                elif event.key == pygame.K_c:
                    self.clear_grid()
                
                elif event.key == pygame.K_e:
                    self.print_exports()
                
                elif event.key == pygame.K_l:
                    self.show_dropdown = not self.show_dropdown
                    if self.show_dropdown and self.available_chars:
                        # Try to select current character if in list
                        if self.current_char in self.available_chars:
                            self.dropdown_selected = self.available_chars.index(self.current_char)
                        else:
                            self.dropdown_selected = 0
                        self.dropdown_scroll = max(0, self.dropdown_selected - 5)
                
                elif event.key == pygame.K_UP and self.show_dropdown:
                    if self.dropdown_selected > 0:
                        self.dropdown_selected -= 1
                        if self.dropdown_selected < self.dropdown_scroll:
                            self.dropdown_scroll = self.dropdown_selected
                
                elif event.key == pygame.K_DOWN and self.show_dropdown:
                    if self.dropdown_selected < len(self.available_chars) - 1:
                        self.dropdown_selected += 1
                        if self.dropdown_selected >= self.dropdown_scroll + 10:
                            self.dropdown_scroll = self.dropdown_selected - 9
                
                elif event.key == pygame.K_RETURN and self.show_dropdown:
                    if 0 <= self.dropdown_selected < len(self.available_chars):
                        char_to_load = self.available_chars[self.dropdown_selected]
                        self.load_character(char_to_load)
                        self.show_dropdown = False
                
                # Grid size controls
                elif event.key == pygame.K_w:
                    self.resize_grid(min(self.grid_width + 1, 25), self.grid_height)
                
                elif event.key == pygame.K_s:
                    self.resize_grid(max(self.grid_width - 1, 1), self.grid_height)
                
                elif event.key == pygame.K_h:
                    self.resize_grid(self.grid_width, min(self.grid_height + 1, 10))
                
                elif event.key == pygame.K_j:
                    self.resize_grid(self.grid_width, max(self.grid_height - 1, 1))
                
                elif event.key == pygame.K_r:
                    self.resize_grid(DEFAULT_GRID_WIDTH, DEFAULT_GRID_HEIGHT)
                
                # Number keys 0-9
                elif pygame.K_0 <= event.key <= pygame.K_9:
                    self.current_char = chr(event.key)
                
                # Letter keys A-Z
                elif pygame.K_a <= event.key <= pygame.K_z:
                    self.current_char = chr(event.key).upper()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.is_drawing = True
                    self.draw_mode = True
                    pixel = self.get_pixel_at_mouse(event.pos)
                    if pixel:
                        self.toggle_pixel(pixel[0], pixel[1], True)
                
                elif event.button == 3:  # Right click
                    self.is_drawing = True
                    self.draw_mode = False
                    pixel = self.get_pixel_at_mouse(event.pos)
                    if pixel:
                        self.toggle_pixel(pixel[0], pixel[1], False)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                self.is_drawing = False
            
            elif event.type == pygame.MOUSEMOTION:
                if self.is_drawing:
                    pixel = self.get_pixel_at_mouse(event.pos)
                    if pixel:
                        self.toggle_pixel(pixel[0], pixel[1], self.draw_mode)
        
        return True
    
    def run(self):
        """Main loop"""
        clock = pygame.time.Clock()
        running = True
        
        print("\n" + "="*60)
        print("Font Editor Started!")
        print("="*60)
        print("Design your characters on the 6x10 grid")
        print("Press 'E' to export when done")
        print("Press '0-9' or 'A-Z' to set the current character")
        print("="*60 + "\n")
        
        while running:
            running = self.handle_events()
            
            # Draw
            self.screen.fill(BLACK)
            self.draw_grid()
            self.draw_controls()
            
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()

def main():
    editor = FontEditor()
    editor.run()

if __name__ == "__main__":
    main()
