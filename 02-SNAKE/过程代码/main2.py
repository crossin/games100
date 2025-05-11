import pygame
import sys
import random
import math

# 初始化 Pygame
pygame.init()

# 游戏参数设置
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GRID_SIZE = 20  # 减小格子尺寸
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (40, 40, 40)
DARK_GREEN = (0, 200, 0)  # 蛇头颜色
LIGHT_RED = (255, 150, 150)  # 食物指示器颜色

# 方向定义
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

class Snake:
    def __init__(self):
        self.length = 1
        self.positions = [(0, 0)]  # 蛇头初始位置在(0,0)
        self.direction = RIGHT
        self.color = GREEN
        self.head_color = DARK_GREEN  # 蛇头特殊颜色
        self.score = 0

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

    def render(self, surface, offset_x, offset_y):
        screen_center_x = WINDOW_WIDTH // 2
        screen_center_y = WINDOW_HEIGHT // 2

        for i, p in enumerate(self.positions):
            # 计算相对于屏幕中心的位置
            screen_x = screen_center_x + (p[0] - offset_x) * GRID_SIZE
            screen_y = screen_center_y + (p[1] - offset_y) * GRID_SIZE

            # 只渲染在屏幕范围内的部分
            if -GRID_SIZE <= screen_x <= WINDOW_WIDTH and -GRID_SIZE <= screen_y <= WINDOW_HEIGHT:
                color = self.head_color if i == 0 else self.color
                pygame.draw.rect(surface, color,
                               (screen_x, screen_y, GRID_SIZE, GRID_SIZE))
                # 为蛇身添加边框，提高视觉效果
                pygame.draw.rect(surface, BLACK,
                               (screen_x, screen_y, GRID_SIZE, GRID_SIZE), 1)

class Food:
    def __init__(self):
        self.position = (0, 0)
        self.color = RED
        self.randomize_position()

    def randomize_position(self):
        # 在蛇头周围的一定范围内随机生成食物
        head_x, head_y = (0, 0)  # 初始蛇头位置
        range_size = 10  # 缩小生成范围，确保食物在视野内
        self.position = (
            random.randint(head_x - range_size, head_x + range_size),
            random.randint(head_y - range_size, head_y + range_size)
        )

    def render(self, surface, offset_x, offset_y):
        screen_center_x = WINDOW_WIDTH // 2
        screen_center_y = WINDOW_HEIGHT // 2

        # 计算食物在屏幕上的位置
        screen_x = screen_center_x + (self.position[0] - offset_x) * GRID_SIZE
        screen_y = screen_center_y + (self.position[1] - offset_y) * GRID_SIZE

        # 检查食物是否在可视范围内
        in_view = (-GRID_SIZE <= screen_x <= WINDOW_WIDTH and
                  -GRID_SIZE <= screen_y <= WINDOW_HEIGHT)

        if in_view:
            # 绘制食物主体
            pygame.draw.rect(surface, self.color,
                           (screen_x, screen_y, GRID_SIZE, GRID_SIZE))
            # 添加边框
            pygame.draw.rect(surface, BLACK,
                           (screen_x, screen_y, GRID_SIZE, GRID_SIZE), 1)
        else:
            # 如果食物在视野外，绘制指向食物的指示器
            dx = self.position[0] - offset_x
            dy = self.position[1] - offset_y
            angle = math.atan2(dy, dx)

            # 计算指示器位置（在屏幕边缘）
            margin = 40  # 距离边缘的距离
            indicator_x = screen_center_x + math.cos(angle) * (WINDOW_WIDTH/2 - margin)
            indicator_y = screen_center_y + math.sin(angle) * (WINDOW_HEIGHT/2 - margin)

            # 绘制指示器
            pygame.draw.circle(surface, LIGHT_RED, (int(indicator_x), int(indicator_y)), 8)
            pygame.draw.circle(surface, RED, (int(indicator_x), int(indicator_y)), 8, 2)

            # 显示距离
            distance = math.sqrt(dx*dx + dy*dy)
            font = pygame.font.Font(None, 24)
            distance_text = font.render(f'{int(distance)}', True, WHITE)
            text_rect = distance_text.get_rect(center=(int(indicator_x), int(indicator_y) - 15))
            surface.blit(distance_text, text_rect)

def draw_grid(surface, offset_x, offset_y):
    screen_center_x = WINDOW_WIDTH // 2
    screen_center_y = WINDOW_HEIGHT // 2

    # 计算可见网格的范围
    start_x = -int(WINDOW_WIDTH / (2 * GRID_SIZE)) - 1
    end_x = int(WINDOW_WIDTH / (2 * GRID_SIZE)) + 1
    start_y = -int(WINDOW_HEIGHT / (2 * GRID_SIZE)) - 1
    end_y = int(WINDOW_HEIGHT / (2 * GRID_SIZE)) + 1

    # 绘制垂直线
    for x in range(start_x, end_x + 1):
        screen_x = screen_center_x + (x - offset_x % 1) * GRID_SIZE
        pygame.draw.line(surface, GRAY,
                        (screen_x, 0),
                        (screen_x, WINDOW_HEIGHT))

    # 绘制水平线
    for y in range(start_y, end_y + 1):
        screen_y = screen_center_y + (y - offset_y % 1) * GRID_SIZE
        pygame.draw.line(surface, GRAY,
                        (0, screen_y),
                        (WINDOW_WIDTH, screen_y))

def main():
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('贪吃蛇 - 跟随视角')

    snake = Snake()
    food = Food()

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

        # 更新蛇的位置
        if not snake.update():
            snake.reset()
            food.randomize_position()

        # 检查是否吃到食物
        if snake.get_head_position() == food.position:
            snake.length += 1
            snake.score += 1
            food.randomize_position()

        # 获取蛇头位置作为偏移量
        head_x, head_y = snake.get_head_position()

        # 绘制
        screen.fill(BLACK)
        draw_grid(screen, head_x, head_y)  # 绘制网格
        snake.render(screen, head_x, head_y)
        food.render(screen, head_x, head_y)

        # 显示分数
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'分数: {snake.score}', True, WHITE)
        screen.blit(score_text, (10, 10))

        pygame.display.update()
        clock.tick(10)  # 控制游戏速度

if __name__ == '__main__':
    main()
