import pygame
import sys
import random
import math
import numpy as np

# 初始化 Pygame
pygame.init()

# 游戏参数设置
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (40, 40, 40)
DARK_GREEN = (0, 200, 0)
LIGHT_RED = (255, 150, 150)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

# 方向定义
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# 游戏速度设置
NORMAL_SPEED = 10
SPRINT_SPEED = 20

try:
    # 初始化音频系统
    pygame.mixer.init(44100, -16, 2, 512)
    # 创建简单的音效（方波）
    sample_rate = 44100
    duration = 0.1  # 秒
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    tone = np.sign(np.sin(2 * np.pi * 440 * t))  # 440 Hz
    tone = np.int16(tone * 32767)
    eat_sound = pygame.mixer.Sound(tone.tobytes())
    eat_sound.set_volume(0.3)
except Exception as e:
    print(f"音效初始化失败: {e}")
    # 创建一个空的音效对象
    eat_sound = type('DummySound', (), {'play': lambda: None})()

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

class Snake:
    def __init__(self):
        self.length = 1
        self.positions = [(0, 0)]
        self.direction = RIGHT
        self.color = GREEN
        self.head_color = DARK_GREEN
        self.score = 0
        self.is_sprinting = False

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
        self.score = 0
        self.is_sprinting = False

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

def draw_grid(surface, offset_x, offset_y):
    screen_center_x = WINDOW_WIDTH // 2
    screen_center_y = WINDOW_HEIGHT // 2

    start_x = -int(WINDOW_WIDTH / (2 * GRID_SIZE)) - 1
    end_x = int(WINDOW_WIDTH / (2 * GRID_SIZE)) + 1
    start_y = -int(WINDOW_HEIGHT / (2 * GRID_SIZE)) - 1
    end_y = int(WINDOW_HEIGHT / (2 * GRID_SIZE)) + 1

    for x in range(start_x, end_x + 1):
        screen_x = screen_center_x + (x - offset_x % 1) * GRID_SIZE
        pygame.draw.line(surface, GRAY,
                        (screen_x, 0),
                        (screen_x, WINDOW_HEIGHT))

    for y in range(start_y, end_y + 1):
        screen_y = screen_center_y + (y - offset_y % 1) * GRID_SIZE
        pygame.draw.line(surface, GRAY,
                        (0, screen_y),
                        (WINDOW_WIDTH, screen_y))

def main():
    try:
        clock = pygame.time.Clock()
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('贪吃蛇 - 冲刺模式')

        snake = Snake()
        food = Food()
        particle_system = ParticleSystem()
        game_speed = NORMAL_SPEED

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP and snake.direction != DOWN:
                        snake.direction = UP
                    elif event.key == pygame.K_DOWN and snake.direction != UP:
                        snake.direction = DOWN
                    elif event.key == pygame.K_LEFT and snake.direction != RIGHT:
                        snake.direction = LEFT
                    elif event.key == pygame.K_RIGHT and snake.direction != LEFT:
                        snake.direction = RIGHT

            keys = pygame.key.get_pressed()
            snake.is_sprinting = keys[pygame.K_SPACE]
            game_speed = SPRINT_SPEED if snake.is_sprinting else NORMAL_SPEED

            if not snake.update():
                snake.reset()
                food.randomize_position()
                continue

            if snake.get_head_position() == food.position:
                if snake.is_sprinting:
                    # 在食物位置创建粒子效果
                    particle_system.emit(food.position[0], food.position[1],
                                       (RED[0], RED[1], RED[2], 255))
                    # 播放音效
                    eat_sound.play()

                    snake.length += 1
                    snake.score += 1
                    food.randomize_position()
                else:
                    snake.reset()
                    food.randomize_position()
                    continue

            head_x, head_y = snake.get_head_position()

            # 更新粒子系统
            particle_system.update()

            # 绘制
            screen.fill(BLACK)
            draw_grid(screen, head_x, head_y)
            snake.render(screen, head_x, head_y)
            food.render(screen, head_x, head_y)
            particle_system.render(screen, head_x, head_y)

            font = pygame.font.Font(None, 36)
            score_text = font.render(f'分数: {snake.score}', True, WHITE)
            screen.blit(score_text, (10, 10))

            sprint_text = font.render('冲刺模式：开启' if snake.is_sprinting else '冲刺模式：关闭',
                                    True, YELLOW if snake.is_sprinting else WHITE)
            screen.blit(sprint_text, (10, 50))

            tip_font = pygame.font.Font(None, 24)
            tip_text = tip_font.render('按住空格键进入冲刺模式，只有在冲刺模式下才能吃到食物！',
                                     True, WHITE)
            screen.blit(tip_text, (10, WINDOW_HEIGHT - 30))

            pygame.display.update()
            clock.tick(game_speed)
    except Exception as e:
        print(f"游戏运行出错: {e}")
        pygame.quit()
        sys.exit(1)

if __name__ == '__main__':
    main()
