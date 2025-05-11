import random
import math
import pygame
from config import *

class Snake:
    def __init__(self):
        self.reset()

    def get_head_position(self):
        return self.positions[0]

    def update(self):
        cur = self.get_head_position()
        x, y = self.direction
        new = (cur[0] + x, cur[1] + y)
        if new in self.positions[3:]:
            return False
        self.positions.insert(0, new)
        if len(self.positions) > self.length:
            self.positions.pop()
        return True

    def reset(self):
        self.length = 1
        self.positions = [(0, 0)]
        self.direction = RIGHT
        self.color = GREEN
        self.head_color = DARK_GREEN
        self.score = 0
        self.is_sprinting = False
        self.high_score = getattr(self, 'high_score', 0)

    def render(self, surface, offset_x, offset_y):
        screen_center_x = WINDOW_WIDTH // 2
        screen_center_y = WINDOW_HEIGHT // 2

        for i, p in enumerate(self.positions):
            screen_x = screen_center_x + (p[0] - offset_x) * GRID_SIZE
            screen_y = screen_center_y + (p[1] - offset_y) * GRID_SIZE

            if -GRID_SIZE <= screen_x <= WINDOW_WIDTH and -GRID_SIZE <= screen_y <= WINDOW_HEIGHT:
                if i == 0:
                    color = YELLOW if self.is_sprinting else self.head_color
                else:
                    color = YELLOW if self.is_sprinting else self.color

                pygame.draw.rect(surface, color,
                               (screen_x, screen_y, GRID_SIZE, GRID_SIZE))
                pygame.draw.rect(surface, BLACK,
                               (screen_x, screen_y, GRID_SIZE, GRID_SIZE), 1)

                if self.is_sprinting and i == 0:
                    glow_size = GRID_SIZE + 4
                    glow_rect = pygame.Rect(screen_x - 2, screen_y - 2, glow_size, glow_size)
                    pygame.draw.rect(surface, YELLOW, glow_rect, 2)

class Food:
    def __init__(self):
        self.position = (0, 0)
        self.color = RED
        self.randomize_position()

    def randomize_position(self):
        head_x, head_y = (0, 0)
        range_size = 10
        self.position = (
            random.randint(head_x - range_size, head_x + range_size),
            random.randint(head_y - range_size, head_y + range_size)
        )

    def render(self, surface, offset_x, offset_y):
        screen_center_x = WINDOW_WIDTH // 2
        screen_center_y = WINDOW_HEIGHT // 2

        screen_x = screen_center_x + (self.position[0] - offset_x) * GRID_SIZE
        screen_y = screen_center_y + (self.position[1] - offset_y) * GRID_SIZE

        in_view = (-GRID_SIZE <= screen_x <= WINDOW_WIDTH and
                  -GRID_SIZE <= screen_y <= WINDOW_HEIGHT)

        if in_view:
            pygame.draw.rect(surface, self.color,
                           (screen_x, screen_y, GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, BLACK,
                           (screen_x, screen_y, GRID_SIZE, GRID_SIZE), 1)
        else:
            dx = self.position[0] - offset_x
            dy = self.position[1] - offset_y
            angle = math.atan2(dy, dx)

            margin = 40
            indicator_x = screen_center_x + math.cos(angle) * (WINDOW_WIDTH/2 - margin)
            indicator_y = screen_center_y + math.sin(angle) * (WINDOW_HEIGHT/2 - margin)

            pygame.draw.circle(surface, LIGHT_RED, (int(indicator_x), int(indicator_y)), 8)
            pygame.draw.circle(surface, RED, (int(indicator_x), int(indicator_y)), 8, 2)

            distance = math.sqrt(dx*dx + dy*dy)
            font = pygame.font.Font(None, 24)
            distance_text = font.render(f'{int(distance)}', True, WHITE)
            text_rect = distance_text.get_rect(center=(int(indicator_x), int(indicator_y) - 15))
            surface.blit(distance_text, text_rect)
