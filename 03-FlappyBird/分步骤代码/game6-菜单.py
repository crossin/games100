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

# 管道类
class Pipe:
    def __init__(self):
        self.x = SCREEN_WIDTH
        self.height = random.randint(150, 400)
        self.passed = False
        self.top_rect = PIPE_IMG.get_rect(bottomleft=(self.x, self.height - PIPE_GAP))
        self.bottom_rect = PIPE_IMG.get_rect(topleft=(self.x, self.height))
    
    def update(self):
        self.x -= PIPE_SPEED
        self.top_rect.x = self.bottom_rect.x = self.x
    
    def draw(self, screen):
        screen.blit(PIPE_IMG, self.top_rect)
        flipped_pipe = pygame.transform.flip(PIPE_IMG, False, True)
        screen.blit(flipped_pipe, self.bottom_rect)

# 地面类
class Base:
    def __init__(self):
        self.x = 0
        self.y = SCREEN_HEIGHT - 100
        self.image = BASE_IMG
        self.width = self.image.get_width()
    
    def update(self):
        self.x -= PIPE_SPEED
        if self.x <= -self.width:
            self.x += self.width
    
    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))
        screen.blit(self.image, (self.x + self.width, self.y))

# 主游戏循环
bird = Bird()
pipes = []
base = Base()
score = 0
font = pygame.font.SysFont("arial", 20)
pipe_timer = 0
running = True
game_state = "start"
start_text = font.render("Press SPACE to Start", True, WHITE)
game_over_text = font.render("Game Over!", True, WHITE)

while running:
    # 事件处理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if game_state == "start" and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            game_state = "playing"
        if game_state == "game_over" and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            bird = Bird()
            pipes = []
            score = 0
            game_state = "playing"
        if game_state == "playing":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bird.jump()
            if event.type == pygame.MOUSEBUTTONDOWN:
                bird.jump()    

    if game_state == "start":
        screen.blit(BG_IMG, (0, 0))
        screen.blit(start_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 100))
    elif game_state == "playing":
        # 更新
        bird.update()
        base.update()

        # 生成管道
        pipe_timer += 1
        if pipe_timer > 90:  # 每 1.5 秒生成一对管道
            pipes.append(Pipe())
            pipe_timer = 0
        
        # 更新管道
        for pipe in pipes[:]:
            pipe.update()
            if pipe.x < -pipe.top_rect.width:
                pipes.remove(pipe)
            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                score += 1

        # 碰撞检测
        for pipe in pipes:
            if bird.rect.colliderect(pipe.top_rect) or bird.rect.colliderect(pipe.bottom_rect):
                game_state = "game_over"
        if bird.y <= 0 or bird.y >= SCREEN_HEIGHT - 100:
            game_state = "game_over"

        # 绘制
        screen.blit(BG_IMG, (0, 0))
        for pipe in pipes:
            pipe.draw(screen)
        base.draw(screen)
        bird.draw(screen)

        # 显示得分
        score_text = font.render(str(score), True, WHITE)
        screen.blit(score_text, (SCREEN_WIDTH // 2, 50))

    elif game_state == "game_over":
        screen.blit(BG_IMG, (0, 0))
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT // 2 - 150))
        final_score = font.render(f"Score: {score}", True, WHITE)
        screen.blit(final_score, (SCREEN_WIDTH // 2 - 40, SCREEN_HEIGHT // 2 - 100))
        screen.blit(start_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()






