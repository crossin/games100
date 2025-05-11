import pygame

# 检查必要的库
AUDIO_AVAILABLE = False
try:
    import pyaudio
    AUDIO_CHUNK = 1024
    AUDIO_FORMAT = pyaudio.paInt16
    AUDIO_CHANNELS = 1
    AUDIO_RATE = 44100
    AUDIO_THRESHOLD = 2000  # 调整为 audioop 适用的阈值
    AUDIO_MAX_VOLUME = 5000  # 音量显示的最大值
    AUDIO_AVAILABLE = True
    print("音频系统初始化成功")
except ImportError as e:
    print(f"音频系统初始化失败: {e}")
    print("将使用空格键控制模式")

# 窗口设置
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
