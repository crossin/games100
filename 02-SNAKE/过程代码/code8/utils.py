import os
import pygame
import random
from config import *

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

def draw_grid(surface, offset_x, offset_y):
    """绘制网格背景"""
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

class SoundManager:
    def __init__(self):
        self.eat_sounds = []
        self._load_sounds()

    def _load_sounds(self):
        """加载所有音效文件"""
        for i in range(1, 6):
            sound_path = f'eat{i}.wav'
            if os.path.exists(sound_path):
                try:
                    sound = pygame.mixer.Sound(sound_path)
                    sound.set_volume(0.3)
                    self.eat_sounds.append(sound)
                except:
                    print(f"无法加载音效文件: {sound_path}")

    def play_random_eat_sound(self):
        """随机播放一个吃食物的音效"""
        if self.eat_sounds:
            random.choice(self.eat_sounds).play()
