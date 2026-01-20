#!/usr/bin/env python3
"""
Font Editor - Paint custom characters on a 6x10 grid and export to font.py format
"""

import pygame
import sys

# Grid dimensions
GRID_WIDTH = 6
GRID_HEIGHT = 10
PIXEL_SIZE = 40
BORDER_SIZE = 1

# Window dimensions
WINDOW_WIDTH = GRID_WIDTH * PIXEL_SIZE + 400  # Extra space for controls
WINDOW_HEIGHT = GRID_HEIGHT * PIXEL_SIZE + 100

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
GRAY = (50, 50, 50)
DARK_GRAY = (30, 30, 30)
LIGHT_GRAY = (100, 100, 100)

class FontEditor:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Font Editor - 6x10 Grid")
        
        # Grid state - 2D array of booleans
        self.grid = [[False for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        
        # Current character being edited
        self.current_char = '0'
        
        # Font for text
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # Drawing state
        self.is_drawing = False
        self.draw_mode = True  # True = paint, False = erase
        
    def get_pixel_at_mouse(self, pos):
        """Convert mouse position to grid coordinates"""
        x, y = pos
        if x < 0 or x >= GRID_WIDTH * PIXEL_SIZE or y < 0 or y >= GRID_HEIGHT * PIXEL_SIZE:
            return None
        grid_x = x // PIXEL_SIZE
        grid_y = y // PIXEL_SIZE
        return (grid_x, grid_y)
    
    def toggle_pixel(self, grid_x, grid_y, value=None):
        """Toggle or set a pixel in the grid"""
        if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
            if value is None:
                self.grid[grid_y][grid_x] = not self.grid[grid_y][grid_x]
            else:
                self.grid[grid_y][grid_x] = value
    
    def clear_grid(self):
        """Clear all pixels"""
        self.grid = [[False for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    
    def export_as_blocks(self):
        """Export grid as list of (x, y, width, height) blocks - optimized"""
        blocks = []
        visited = [[False for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y][x] and not visited[y][x]:
                    # Find the largest rectangle starting at this pixel
                    width = 1
                    height = 1
                    
                    # Extend width
                    while x + width < GRID_WIDTH and self.grid[y][x + width] and not visited[y][x + width]:
                        width += 1
                    
                    # Extend height (check if entire row can be extended)
                    can_extend = True
                    while can_extend and y + height < GRID_HEIGHT:
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
        return [[1 if self.grid[y][x] else 0 for x in range(GRID_WIDTH)] for y in range(GRID_HEIGHT)]
    
    def export_as_coordinates(self):
        """Export as list of (x, y) coordinates"""
        coords = []
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
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
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
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
        panel_x = GRID_WIDTH * PIXEL_SIZE + 20
        y_offset = 20
        
        # Title
        title = self.font.render("Font Editor", True, WHITE)
        self.screen.blit(title, (panel_x, y_offset))
        y_offset += 40
        
        # Current character
        char_text = self.font.render(f"Character: '{self.current_char}'", True, WHITE)
        self.screen.blit(char_text, (panel_x, y_offset))
        y_offset += 40
        
        # Instructions
        instructions = [
            "CONTROLS:",
            "Click: Paint pixel",
            "Right-click: Erase pixel",
            "Drag: Paint/erase multiple",
            "",
            "C: Clear grid",
            "E: Export to console",
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
