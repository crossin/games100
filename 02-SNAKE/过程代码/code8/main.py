import pygame
import sys
import traceback
from config import *
from audio import AudioInput
from game_objects import Snake, Food
from particles import ParticleSystem
from utils import get_system_chinese_font, draw_grid, SoundManager

def draw_volume_meter(surface, volume, font, x=10, y=90):
    """绘制音量计"""
    max_width = 200
    height = 20
    # 计算音量条宽度
    volume_width = min(max_width, volume / AUDIO_MAX_VOLUME * max_width)

    # 绘制背景
    pygame.draw.rect(surface, GRAY, (x, y, max_width, height))

    # 绘制音量条
    if volume > AUDIO_THRESHOLD:
        color = GREEN
    else:
        color = WHITE
    pygame.draw.rect(surface, color, (x, y, volume_width, height))

    # 绘制阈值线
    threshold_x = x + (AUDIO_THRESHOLD / AUDIO_MAX_VOLUME * max_width)
    pygame.draw.line(surface, RED, (threshold_x, y), (threshold_x, y + height), 2)

    # 显示当前音量值
    try:
        volume_text = font.render(f'音量: {int(volume)}', True, WHITE)
    except:
        volume_text = font.render(f'音量: 0', True, WHITE)
    surface.blit(volume_text, (x + max_width + 10, y))

def main():
    try:
        print("游戏启动...")
        pygame.init()
        clock = pygame.time.Clock()
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('贪吃蛇 - 声控冲刺模式')

        # 初始化音频输入
        print("初始化音频输入...")
        audio_input = AudioInput()

        # 初始化音效管理器
        sound_manager = SoundManager()

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
                            sound_manager.play_random_eat_sound()

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
                        # 绘制音量计
                        draw_volume_meter(screen, audio_input.current_volume, chinese_font_small)
                    else:
                        tip_text = chinese_font_small.render(
                            '按住空格键进入冲刺模式，只有在冲刺模式下才能吃到食物！',
                            True, WHITE)
                    screen.blit(tip_text, (10, WINDOW_HEIGHT - 30))

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
