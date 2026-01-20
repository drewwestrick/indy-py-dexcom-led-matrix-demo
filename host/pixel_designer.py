"""
Pixel Designer - Design custom numbers and arrows for LED display
Simulates 53x11 LED matrix with custom pixel art
"""

import pygame
import sys

# Display dimensions
WIDTH = 53
HEIGHT = 11
PIXEL_SIZE = 20  # Larger pixels for easier design
WINDOW_WIDTH = WIDTH * PIXEL_SIZE
WINDOW_HEIGHT = HEIGHT * PIXEL_SIZE

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GRAY = (50, 50, 50)
GRID_COLOR = (30, 30, 30)

# Minecraft-style blocky number designs (each number as list of (x, y, width, height) blocks)
# Format: list of rectangles [(x, y, w, h), ...]
# Based on classic Minecraft font with thick borders and clean segments
BLOCKY_NUMBERS = {
    '0': [
        (0, 0, 5, 2),   # Top bar
        (0, 2, 2, 7),   # Left side
        (3, 2, 2, 7),   # Right side
        (0, 9, 5, 2),   # Bottom bar
    ],
    '1': [
        (1, 0, 2, 2),   # Top center/cap
        (1, 2, 2, 9),   # Vertical center line
    ],
    '2': [
        (0, 0, 5, 2),   # Top bar
        (3, 2, 2, 3),   # Upper right
        (0, 5, 5, 2),   # Middle bar
        (0, 7, 2, 2),   # Lower left
        (0, 9, 5, 2),   # Bottom bar
    ],
    '3': [
        (0, 0, 5, 2),   # Top bar
        (3, 2, 2, 3),   # Upper right
        (0, 5, 5, 2),   # Middle bar
        (3, 7, 2, 2),   # Lower right
        (0, 9, 5, 2),   # Bottom bar
    ],
    '4': [
        (0, 0, 2, 5),   # Upper left vertical
        (3, 0, 2, 11),  # Right vertical full height
        (0, 5, 5, 2),   # Middle bar
    ],
    '5': [
        (0, 0, 5, 2),   # Top bar
        (0, 2, 2, 3),   # Upper left
        (0, 5, 5, 2),   # Middle bar
        (3, 7, 2, 2),   # Lower right
        (0, 9, 5, 2),   # Bottom bar
    ],
    '6': [
        (0, 0, 5, 2),   # Top bar
        (0, 2, 2, 7),   # Left side full
        (0, 5, 5, 2),   # Middle bar
        (3, 7, 2, 2),   # Lower right
        (0, 9, 5, 2),   # Bottom bar
    ],
    '7': [
        (0, 0, 5, 2),   # Top bar
        (3, 2, 2, 9),   # Right side
    ],
    '8': [
        (0, 0, 5, 2),   # Top bar
        (0, 2, 2, 3),   # Upper left
        (3, 2, 2, 3),   # Upper right
        (0, 5, 5, 2),   # Middle bar
        (0, 7, 2, 2),   # Lower left
        (3, 7, 2, 2),   # Lower right
        (0, 9, 5, 2),   # Bottom bar
    ],
    '9': [
        (0, 0, 5, 2),   # Top bar
        (0, 2, 2, 3),   # Upper left
        (3, 2, 2, 7),   # Right side full
        (0, 5, 5, 2),   # Middle bar
        (0, 9, 5, 2),   # Bottom bar
    ],
}

# Arrow designs as pixel patterns
ARROWS = {
    'double_up': [
        # First arrow (left)
        (0, 7, 1, 1),    # Tip
        (0, 8, 3, 1),    # Row 2
        (0, 9, 5, 1),    # Row 3
        (1, 10, 3, 1),   # Base
        (2, 0, 1, 10),   # Shaft
        # Second arrow (right)
        (4, 7, 1, 1),    # Tip
        (4, 8, 3, 1),    # Row 2
        (4, 9, 5, 1),    # Row 3
        (5, 10, 3, 1),   # Base
        (6, 0, 1, 10),   # Shaft
    ],
    'single_up': [
        (2, 7, 2, 1),    # Tip
        (1, 8, 4, 1),    # Row 2
        (0, 9, 6, 1),    # Row 3
        (1, 10, 4, 1),   # Base
        (2, 0, 2, 10),   # Shaft
    ],
    'forty_five_up': [
        (5, 8, 2, 3),    # Top right
        (4, 7, 2, 2),    # 
        (3, 5, 2, 3),    # Middle
        (2, 4, 2, 2),    #
        (1, 2, 2, 3),    #
        (0, 0, 2, 3),    # Bottom left
    ],
    'flat': [
        (0, 4, 8, 3),    # Horizontal bar
    ],
    'forty_five_down': [
        (0, 8, 2, 3),    # Top left
        (1, 7, 2, 2),    #
        (2, 5, 2, 3),    # Middle
        (3, 4, 2, 2),    #
        (4, 2, 2, 3),    #
        (5, 0, 2, 3),    # Bottom right
    ],
    'single_down': [
        (2, 0, 2, 10),   # Shaft
        (1, 10, 4, 1),   # Top
        (0, 9, 6, 1),    # Row 2
        (1, 8, 4, 1),    # Row 3
        (2, 7, 2, 1),    # Tip
    ],
    'double_down': [
        # First arrow (left)
        (2, 0, 1, 10),   # Shaft
        (1, 10, 3, 1),   # Top
        (0, 9, 5, 1),    # Row 2
        (0, 8, 3, 1),    # Row 3
        (0, 7, 1, 1),    # Tip
        # Second arrow (right)
        (6, 0, 1, 10),   # Shaft
        (5, 10, 3, 1),   # Top
        (4, 9, 5, 1),    # Row 2
        (4, 8, 3, 1),    # Row 3
        (4, 7, 1, 1),    # Tip
    ],
}


class PixelDesigner:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH + 300, WINDOW_HEIGHT))
        pygame.display.set_caption("Pixel Designer - LED Display Simulator")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        
        # Current display state
        self.glucose = 265
        self.trend = 'forty_five_down'
        self.delta = -15  # Change in glucose
        
    def draw_grid(self):
        """Draw grid lines"""
        for x in range(0, WINDOW_WIDTH, PIXEL_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (x, 0), (x, WINDOW_HEIGHT), 1)
        for y in range(0, WINDOW_HEIGHT, PIXEL_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (0, y), (WINDOW_WIDTH, y), 1)
    
    def draw_blocks(self, blocks, x_offset, y_offset, color):
        """Draw a list of blocks at offset position"""
        for block in blocks:
            bx, by, bw, bh = block
            pygame.draw.rect(
                self.screen,
                color,
                (
                    (x_offset + bx) * PIXEL_SIZE,
                    (y_offset + by) * PIXEL_SIZE,
                    bw * PIXEL_SIZE,
                    bh * PIXEL_SIZE
                )
            )
    
    def draw_number(self, digit, x_offset, y_offset, color):
        """Draw a single digit"""
        if digit in BLOCKY_NUMBERS:
            self.draw_blocks(BLOCKY_NUMBERS[digit], x_offset, y_offset, color)
    
    def draw_arrow(self, arrow_type, x_offset, y_offset, color):
        """Draw an arrow"""
        if arrow_type in ARROWS:
            self.draw_blocks(ARROWS[arrow_type], x_offset, y_offset, color)
    
    def draw_display(self):
        """Draw the complete display"""
        # Clear display area
        pygame.draw.rect(self.screen, BLACK, (0, 0, WINDOW_WIDTH, WINDOW_HEIGHT))
        
        # Determine color based on glucose value
        if self.glucose < 70:
            color = RED
        elif self.glucose > 180:
            color = YELLOW
        else:
            color = GREEN
        
        # Draw glucose number (3 digits max)
        glucose_str = str(self.glucose)
        x_pos = 0
        for digit in glucose_str:
            self.draw_number(digit, x_pos, 0, color)
            x_pos += 6  # Each number is 5 wide + 1 gap
        
        # Draw arrow
        x_pos += 2  # Gap before arrow
        self.draw_arrow(self.trend, x_pos, 0, color)
        
        # Draw delta (change in glucose)
        x_pos += 10  # Gap after arrow
        delta_str = f"{self.delta:+d}"  # Format with + or - sign
        for char in delta_str:
            if char in BLOCKY_NUMBERS:
                self.draw_number(char, x_pos, 0, color)
                x_pos += 6
            elif char == '+':
                # Draw plus sign
                pygame.draw.rect(self.screen, color, (x_pos * PIXEL_SIZE, 4 * PIXEL_SIZE, 3 * PIXEL_SIZE, 3 * PIXEL_SIZE))
                x_pos += 4
            elif char == '-':
                # Draw minus sign
                pygame.draw.rect(self.screen, color, (x_pos * PIXEL_SIZE, 5 * PIXEL_SIZE, 3 * PIXEL_SIZE, 1 * PIXEL_SIZE))
                x_pos += 4
        
        # Draw grid
        self.draw_grid()
    
    def draw_controls(self):
        """Draw control panel"""
        x = WINDOW_WIDTH + 10
        y = 10
        
        texts = [
            f"Glucose: {self.glucose}",
            f"Trend: {self.trend}",
            f"Delta: {self.delta:+d}",
            "",
            "Controls:",
            "UP/DOWN: Glucose ±10",
            "LEFT/RIGHT: Glucose ±1",
            "",
            "Arrows:",
            "1: ↑↑ Double Up",
            "2: ↑ Single Up",
            "3: ↗ Forty-Five Up",
            "4: → Flat",
            "5: ↘ Forty-Five Down",
            "6: ↓ Single Down",
            "7: ↓↓ Double Down",
            "",
            "D: Change delta",
            "Q: Quit",
        ]
        
        for text in texts:
            surface = self.font.render(text, True, WHITE)
            self.screen.blit(surface, (x, y))
            y += 30
    
    def cycle_trend(self):
        """Cycle through trend types"""
        trends = list(ARROWS.keys())
        current_idx = trends.index(self.trend)
        self.trend = trends[(current_idx + 1) % len(trends)]
    
    def run(self):
        """Main loop"""
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        running = False
                    elif event.key == pygame.K_UP:
                        self.glucose = min(400, self.glucose + 10)
                    elif event.key == pygame.K_DOWN:
                        self.glucose = max(50, self.glucose - 10)
                    elif event.key == pygame.K_RIGHT:
                        self.glucose = min(400, self.glucose + 1)
                    elif event.key == pygame.K_LEFT:
                        self.glucose = max(50, self.glucose - 1)
                    elif event.key == pygame.K_1:
                        self.trend = 'double_up'
                    elif event.key == pygame.K_2:
                        self.trend = 'single_up'
                    elif event.key == pygame.K_3:
                        self.trend = 'forty_five_up'
                    elif event.key == pygame.K_4:
                        self.trend = 'flat'
                    elif event.key == pygame.K_5:
                        self.trend = 'forty_five_down'
                    elif event.key == pygame.K_6:
                        self.trend = 'single_down'
                    elif event.key == pygame.K_7:
                        self.trend = 'double_down'
                    elif event.key == pygame.K_t:
                        self.cycle_trend()
                    elif event.key == pygame.K_d:
                        # Cycle delta values
                        deltas = [-30, -15, -5, 0, 5, 15, 30]
                        current_idx = deltas.index(self.delta) if self.delta in deltas else 0
                        self.delta = deltas[(current_idx + 1) % len(deltas)]
            
            # Draw everything
            self.screen.fill(BLACK)
            self.draw_display()
            self.draw_controls()
            
            pygame.display.flip()
            self.clock.tick(30)
        
        pygame.quit()


if __name__ == "__main__":
    designer = PixelDesigner()
    designer.run()
