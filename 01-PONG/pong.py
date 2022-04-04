import pgzrun
import pygame
import random
import math
import os

WIDTH = 800                                 # 屏幕宽度
HEIGHT = 600                                # 屏幕高度
PAD_SPEED = 1000                            # 挡板移动速度
BALL_SPEED = 800                            # 小球速度        
BALL_RADIUS = 6                             # 小球半径

pad_1 = Rect((20, 20), (10, 100))
pad_2 = Rect((WIDTH-20, 20), (10, 100))
scores = [0, 0]

class Ball():                               # 小球类
    def __init__(self):
        self.reset()

    def reset(self):                        # 重置小球
        self.pos = [WIDTH/2, HEIGHT/2]
        sy = BALL_SPEED * 0.9 * (1 - random.random() * 2)
        sx = (BALL_SPEED ** 2 - sy ** 2) ** 0.5 * random.choice([-1,1])
        self.speed = [sx, sy]        

    def update(self, dt):                   # 更新小球位置
        for i in range(2):
            self.pos[i] += self.speed[i] * dt
        if self.pos[1] < 0 or self.pos[1] > HEIGHT:
            self.speed[1] *= -1

        if self.pos[0] < 0:
            self.dead(1)
        if self.pos[0] > WIDTH:
            self.dead(0)

    def dead(self, side):                   # 小球出界
        scores[side] += 1
        self.reset()

ball = Ball()                               # 创建小球

def draw():                                 # 游戏绘制函数
    screen.clear()
    screen.draw.filled_rect(pad_1, 'white')
    screen.draw.filled_rect(pad_2, 'white')
    screen.draw.filled_circle(ball.pos, BALL_RADIUS, 'white')
    screen.draw.text(":", midtop=(WIDTH/2, 20), fontname="zhaozi", fontsize=64)
    screen.draw.text(f"{scores[0]}", topright=(WIDTH/2 - 40, 20), fontname="zhaozi", fontsize=64)
    screen.draw.text(f"{scores[1]}", topleft=(WIDTH/2 + 40, 20), fontname="zhaozi", fontsize=64)


def listen_key(dt):                         # 键盘响应
    if keyboard.w:
        pad_1.y -= PAD_SPEED * dt
        if pad_1.top < 0:
            pad_1.top = 0
    elif keyboard.s:
        pad_1.y += PAD_SPEED * dt
        if pad_1.bottom > HEIGHT:
            pad_1.bottom = HEIGHT

    if keyboard.up:
        pad_2.y -= PAD_SPEED * dt
        if pad_2.top < 0:
            pad_2.top = 0
    elif keyboard.down:
        pad_2.y += PAD_SPEED * dt
        if pad_2.bottom > HEIGHT:
            pad_2.bottom = HEIGHT


def auto_move_pad(dt):                      # 挡板自动追踪
    if ball.pos[0] > WIDTH / 2 and ball.speed[0] > 0:
        if pad_2.y + pad_2.height * 0.25 > ball.pos[1]:
            pad_2.y -= PAD_SPEED * dt
            if pad_2.top < 0:
                pad_2.top = 0
        elif pad_2.y + pad_2.height * 0.75 < ball.pos[1]:
            pad_2.y += PAD_SPEED * dt
            if pad_2.bottom > HEIGHT:
                pad_2.bottom = HEIGHT

def update(dt):                             # 游戏更新函数
    # 更新小球
    ball.update(dt)
    # 键盘响应
    listen_key(dt)
    # 单人模式AI
    auto_move_pad(dt)
    # 碰撞检测
    if (pad_1.collidepoint(ball.pos) and ball.speed[0] < 0) or (
        pad_2.collidepoint(ball.pos) and ball.speed[0] > 0):
        ball.speed[0] *= -1

pgzrun.go()
