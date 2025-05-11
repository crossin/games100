# 获取教程、习题、案例，共同学习、讨论、打卡
# 请关注：Crossin的编程教室
# 学习交流或对代码有疑问请加交流群：
#【微信】sunset24678（添加时备注：python）
#【QQ】725903636（最新群号见 https://python666.cn/c/9）

import pygame
import sys
import random
import math
import numpy as np
import os
import threading
import time
import traceback

try:
    import pyaudio
    import audioop
    AUDIO_AVAILABLE = True
    print("成功导入音频模块")
except Exception as e:
    print(f"无法初始化音频系统: {e}")
    AUDIO_AVAILABLE = False

# 初始化 Pygame
pygame.init()

# 音频输入参数
if AUDIO_AVAILABLE:
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    THRESHOLD = 3000

class AudioInput:
    def __init__(self):
        self.audio = None
        self.stream = None
        self.is_running = False
        self.current_volume = 0
        if AUDIO_AVAILABLE:
            self.setup_stream()

    def setup_stream(self):
        try:
            self.audio = pyaudio.PyAudio()
            self.stream = self.audio.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK
            )
            self.is_running = True
            threading.Thread(target=self.audio_loop, daemon=True).start()
            print("音频输入初始化成功")
        except Exception as e:
            print(f"音频输入初始化失败: {e}")
            print(traceback.format_exc())
            self.is_running = False
            if self.audio:
                self.audio.terminate()

    def audio_loop(self):
        while self.is_running:
            try:
                if self.stream and not self.stream.is_stopped():
                    data = self.stream.read(CHUNK, exception_on_overflow=False)
                    self.current_volume = audioop.rms(data, 2)
            except Exception as e:
                print(f"音频读取错误: {e}")
                time.sleep(0.1)

    def get_is_loud(self):
        """返回当前音量是否超过阈值"""
        if not self.is_running:
            return False
        return self.current_volume > THRESHOLD

    def cleanup(self):
        print("正在清理音频资源...")
        self.is_running = False
        if self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except Exception as e:
                print(f"关闭音频流时出错: {e}")
        if self.audio:
            try:
                self.audio.terminate()
            except Exception as e:
                print(f"终止音频系统时出错: {e}")

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

# 游戏状态
PLAYING = 'playing'
GAME_OVER = 'game_over'

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
        self.vy += 0.1
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

def get_system_chinese_font():
    """获取系统支持的中文字体"""
    system_fonts = [
        "PingFang SC",
        "STHeiti",
        "Heiti SC",
        "Hiragino Sans GB",
        "Microsoft YaHei",
        "WenQuanYi Micro Hei"
    ]
    for font in system_fonts:
        try:
            test_font = pygame.font.SysFont(font, 24)
            if test_font.render('测试', True, (0, 0, 0)).get_rect().width > 0:
                return font
        except:
            continue
    return None

# 加载音效
eat_sounds = []
for i in range(1, 6):
    sound_path = f'eat{i}.wav'
    if os.path.exists(sound_path):
        try:
            sound = pygame.mixer.Sound(sound_path)
            sound.set_volume(0.3)
            eat_sounds.append(sound)
        except:
            print(f"无法加载音效文件: {sound_path}")

def play_random_eat_sound():
    """随机播放一个吃食物的音效"""
    if eat_sounds:
        random.choice(eat_sounds).play()

def main():
    try:
        print("游戏启动...")
        clock = pygame.time.Clock()
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('贪吃蛇 - 声控冲刺模式')

        # 初始化音频输入
        print("初始化音频输入...")
        audio_input = AudioInput()

        # 获取中文字体
        print("加载字体...")
        chinese_font_name = get_system_chinese_font()
        if chinese_font_name:
            chinese_font = pygame.font.SysFont(chinese_font_name, 36)
            chinese_font_small = pygame.font.SysFont(chinese_font_name, 24)
        else:
            print("未找到支持中文的字体，将使用默认字体")
            chinese_font = pygame.font.Font(None, 36)
            chinese_font_small = pygame.font.Font(None, 24)

        print("初始化游戏对象...")
        snake = Snake()
        food = Food()
        particle_system = ParticleSystem()
        game_speed = NORMAL_SPEED
        game_state = PLAYING

        print("进入游戏主循环...")
        try:
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        raise SystemExit
                    elif event.type == pygame.KEYDOWN:
                        if game_state == GAME_OVER:
                            game_state = PLAYING
                            snake.reset()
                            food.randomize_position()
                            continue

                        if game_state == PLAYING:
                            if event.key == pygame.K_UP and snake.direction != DOWN:
                                snake.direction = UP
                            elif event.key == pygame.K_DOWN and snake.direction != UP:
                                snake.direction = DOWN
                            elif event.key == pygame.K_LEFT and snake.direction != RIGHT:
                                snake.direction = LEFT
                            elif event.key == pygame.K_RIGHT and snake.direction != LEFT:
                                snake.direction = RIGHT
                            elif event.key == pygame.K_SPACE and not audio_input.is_running:
                                snake.is_sprinting = True
                    elif event.type == pygame.KEYUP:
                        if event.key == pygame.K_SPACE and not audio_input.is_running:
                            snake.is_sprinting = False

                if game_state == PLAYING:
                    if audio_input.is_running:
                        snake.is_sprinting = audio_input.get_is_loud()
                    game_speed = SPRINT_SPEED if snake.is_sprinting else NORMAL_SPEED

                    if not snake.update():
                        game_state = GAME_OVER
                        snake.high_score = max(snake.score, snake.high_score)
                        continue

                    if snake.get_head_position() == food.position:
                        if snake.is_sprinting:
                            particle_system.emit(food.position[0], food.position[1],
                                               (RED[0], RED[1], RED[2], 255))
                            play_random_eat_sound()

                            snake.length += 1
                            snake.score += 1
                            food.randomize_position()
                        else:
                            game_state = GAME_OVER
                            snake.high_score = max(snake.score, snake.high_score)
                            continue

                head_x, head_y = snake.get_head_position()
                particle_system.update()

                # 绘制
                screen.fill(BLACK)
                draw_grid(screen, head_x, head_y)
                snake.render(screen, head_x, head_y)
                food.render(screen, head_x, head_y)
                particle_system.render(screen, head_x, head_y)

                if game_state == PLAYING:
                    score_text = chinese_font.render(f'分数: {snake.score}', True, WHITE)
                    screen.blit(score_text, (10, 10))

                    sprint_text = chinese_font.render(
                        '冲刺模式：开启' if snake.is_sprinting else '冲刺模式：关闭',
                        True, YELLOW if snake.is_sprinting else WHITE)
                    screen.blit(sprint_text, (10, 50))

                    if audio_input.is_running:
                        tip_text = chinese_font_small.render(
                            '发出声音进入冲刺模式，只有在冲刺模式下才能吃到食物！',
                            True, WHITE)
                    else:
                        tip_text = chinese_font_small.render(
                            '按住空格键进入冲刺模式，只有在冲刺模式下才能吃到食物！',
                            True, WHITE)
                    screen.blit(tip_text, (10, WINDOW_HEIGHT - 30))

                    if audio_input.is_running:
                        volume = audio_input.current_volume
                        max_width = 200
                        volume_width = min(max_width, volume / THRESHOLD * max_width)
                        pygame.draw.rect(screen, GRAY, (10, 90, max_width, 20))
                        pygame.draw.rect(screen, GREEN if volume > THRESHOLD else WHITE,
                                       (10, 90, volume_width, 20))
                        pygame.draw.line(screen, RED, (10 + max_width * 0.8, 90),
                                       (10 + max_width * 0.8, 110), 2)

                else:  # 游戏结束状态
                    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
                    overlay.fill(BLACK)
                    overlay.set_alpha(128)
                    screen.blit(overlay, (0, 0))

                    game_over_text = chinese_font.render('游戏结束', True, WHITE)
                    score_text = chinese_font.render(f'最终分数: {snake.score}', True, WHITE)
                    high_score_text = chinese_font.render(f'最高分数: {snake.high_score}', True, WHITE)
                    continue_text = chinese_font_small.render('按任意键继续', True, WHITE)

                    text_y = WINDOW_HEIGHT // 2 - 100
                    for text in [game_over_text, score_text, high_score_text, continue_text]:
                        text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, text_y))
                        screen.blit(text, text_rect)
                        text_y += 50

                pygame.display.update()
                clock.tick(game_speed)

        finally:
            print("清理游戏资源...")
            audio_input.cleanup()
            pygame.quit()

    except Exception as e:
        print(f"游戏运行出错: {e}")
        print(traceback.format_exc())
        pygame.quit()
        sys.exit(1)

if __name__ == '__main__':
    main()
