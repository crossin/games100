import pygame
import random

# 初始化 Pygame
pygame.init()

# 游戏窗口设置
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock()
FPS = 60

# 颜色
WHITE = (255, 255, 255)

# 加载资源（替换为你的图片路径）
try:
    BIRD_IMG = pygame.image.load("assets/bird.png").convert_alpha()
    PIPE_IMG = pygame.image.load("assets/pipe.png").convert_alpha()
    BG_IMG = pygame.image.load("assets/background.png").convert()
    BASE_IMG = pygame.image.load("assets/base.png").convert_alpha()
except FileNotFoundError:
    print("资源文件未找到，请确保 assets 文件夹中有 bird.png, pipe.png, background.png, base.png")
    pygame.quit()
    exit()

# 游戏变量
GRAVITY = 0.5
JUMP_HEIGHT = -10
PIPE_GAP = 150
PIPE_SPEED = 3

# 小鸟类
class Bird:
    def __init__(self):
        self.x = 100
        self.y = SCREEN_HEIGHT // 2
        self.velocity = 0
        self.image = BIRD_IMG
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
    
    def jump(self):
        self.velocity = JUMP_HEIGHT
    
    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity
        self.rect.y = self.y
    
    def draw(self, screen):
        screen.blit(self.image, self.rect)

# 主游戏循环
bird = Bird()
running = True

while running:
    # 事件处理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bird.jump()
        if event.type == pygame.MOUSEBUTTONDOWN:
            bird.jump()    

    # 更新
    bird.update()

    # 绘制
    screen.blit(BG_IMG, (0, 0))
    bird.draw(screen)
    
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()







