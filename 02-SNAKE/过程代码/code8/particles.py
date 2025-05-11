import random
import math
import pygame
from config import *

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(2, 5)
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 6)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = 1.0
        self.decay_rate = random.uniform(0.02, 0.05)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1  # 重力效果
        self.life -= self.decay_rate
        return self.life > 0

    def render(self, surface, offset_x, offset_y):
        screen_center_x = WINDOW_WIDTH // 2
        screen_center_y = WINDOW_HEIGHT // 2

        screen_x = int(screen_center_x + (self.x - offset_x) * GRID_SIZE)
        screen_y = int(screen_center_y + (self.y - offset_y) * GRID_SIZE)

        alpha = int(255 * self.life)
        color = (*self.color[:3], alpha)

        s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, color, (self.size, self.size), self.size)
        surface.blit(s, (screen_x - self.size, screen_y - self.size))

class ParticleSystem:
    def __init__(self):
        self.particles = []

    def emit(self, x, y, color, count=20):
        for _ in range(count):
            self.particles.append(Particle(x, y, color))

    def update(self):
        self.particles = [p for p in self.particles if p.update()]

    def render(self, surface, offset_x, offset_y):
        for particle in self.particles:
            particle.render(surface, offset_x, offset_y)
