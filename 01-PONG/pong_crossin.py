import pgzrun
import pygame
import random
import math
import os

WIDTH = 800
HEIGHT = 600
PAD_SPEED = 1000
BALL_SPEED = 400
BALL_RADIUS = 6
ITEM_SPEED = 100
ITEM_PROB = 0.5
SINGLE_MODE = True

pad_1 = Rect((20, 20), (10, 100))
pad_2 = Rect((WIDTH-20, 20), (10, 100))
pad_1_trail = []
pad_2_trail = []
scores = [0, 0]
global_vals = {
    'cool_down': 0,
    'time_speedup': 0,
    'time_invisible': 0,
    'time_gravity': 0,
    'interval': 5,
    'flash': False,
}

notes = []
for j in '56':
    for i in 'CDEFGAB':
        notes.append(tone.create(i+j, 0.01))


class Particle():
    def __init__(self, pos, r):
        self.pos = pos
        self.r = r

    def end(self):
        particles.remove(self)

particles = []


def pong(pos, key, on_pad=False):
    key = min(key, len(notes))
    notes[key-1].play()
    if on_pad:
        global_vals['flash'] = True

    for i in range(10):
        theta = random.random() * math.pi * 2
        r = 10 + random.random() * 20
        dest = (pos[0]+math.cos(theta)*r, pos[1]+math.sin(theta)*r)
        p = Particle(pos[:], 1)
        particles.append(p)
        animate(p, duration=0.5, pos=dest, on_finished=p.end, tween='decelerate')


class Ball():
    def __init__(self):
        self.pos = [WIDTH/4+random.random()*WIDTH/2, random.random()*HEIGHT]
        self.r = 0
        self.trail = []
        self.times = 0
        # self.speed = [0, 0]
        # self.in_gravity = False

    def start(self):
        # self.pos = [WIDTH/2, HEIGHT/2]
        sy = BALL_SPEED * 0.9 * (1 - random.random() * 2)
        sx = (BALL_SPEED ** 2 - sy ** 2) ** 0.5 * random.choice([-1,1])
        self.speed = [sx, sy]
        self.in_gravity = False
        self.r = BALL_RADIUS

    def set(self, pos, speed):
        self.pos = pos
        self.speed = speed       
        self.in_gravity = False
        self.r = BALL_RADIUS

    def update(self, dt):
        if self.r < BALL_RADIUS:
            self.r += BALL_RADIUS * dt
            theta = random.random() * math.pi * 2
            if self.r < BALL_RADIUS / 2:
                p = Particle((self.pos[0]+math.cos(theta)*40, self.pos[1]+math.sin(theta)*40), 1)
                particles.append(p)
                animate(p, duration=0.5, pos=self.pos, on_finished=p.end, tween='accelerate')
            if self.r >= BALL_RADIUS:
                self.start()
                balls_ready.remove(self)
                balls.append(self)
            return

        old_pos = self.pos[:]
        if global_vals['time_gravity'] > 0:
            self.in_gravity = True
            if global_vals['gravity_side'] > 0:
                g = 500
            else:
                g = -500
            self.speed[0] += g * dt
        elif self.in_gravity:
            ratio = BALL_SPEED / ((self.speed[0]**2 + self.speed[1]**2) ** 0.5)
            self.speed[0] *= ratio
            self.speed[1] *= ratio
            self.in_gravity = False
        factor = 1.5 if global_vals['time_speedup'] > 0 else 1
        for i in range(2):
            self.pos[i] += self.speed[i] * dt * factor
        if (self.pos[1] < 0 and self.speed[1] < 0) or (self.pos[1] > HEIGHT and self.speed[1] > 0):
            self.speed[1] *= -1
            pong(self.pos, self.times)
        self.trail.append(old_pos)
        if len(self.trail) > 9:
            self.trail.pop(0)
        return old_pos

    def is_out(self):
        return self.pos[0] < -20 or self.pos[0] > WIDTH + 20

    def score(self):
        side = 0 if self.speed[0] > 0 else 1
        scores[side] += 1

    def split(self):
        sy1 = min(self.speed[1] + BALL_SPEED * 0.1, BALL_SPEED * 0.9)
        sy2 = max(self.speed[1] - BALL_SPEED * 0.1, -BALL_SPEED * 0.9)
        sign = 1 if self.speed[0] > 0 else -1
        sx1 = (BALL_SPEED ** 2 - sy1 ** 2) ** 0.5 * sign
        sx2 = (BALL_SPEED ** 2 - sy2 ** 2) ** 0.5 * sign
        self.set(self.pos[:], [sx1, sy1])
        ball_new = Ball()
        ball_new.set(self.pos[:], [sx2, sy2])
        return ball_new

balls = []
balls_ready = []


class Item():
    texts = ('裂', '速', '隐', '坠')
    colors = ('blue', 'red', 'purple', 'orange')

    def __init__(self, pos):
        direct = 1 if pos[0] < WIDTH / 2 else -1
        # self.rect = Rect((pos[0]-10+10*direct, pos[1]-10), (20, 20))
        self.pos = [pos[0]+10*direct, pos[1]]
        self.speed = [ITEM_SPEED * direct, 0]
        self.angle = 0
        self.kind = random.randint(0, 3)
        self.text = self.texts[self.kind]
        self.color = self.colors[self.kind]
        # self.rect.angle = 45

    def update(self, dt):
        self.pos[0] += self.speed[0] * dt
        self.angle += 180 * dt

    def is_out(self):
        return self.pos[0] < -20 or self.pos[0] > WIDTH + 20

    def do_effect(self):
        sounds.item.play()
        if self.kind == 0:      # 分裂
            balls_to_add = []
            for ball in balls:
                b = ball.split()
                balls_to_add.append(b)
            balls.extend(balls_to_add)
        elif self.kind == 1:    # 加速
            global_vals['time_speedup'] = 5
        elif self.kind == 2:    # 隐形
            global_vals['time_invisible'] = 5
            global_vals['invisible_side'] = 1 if self.speed[0] < 0 else -1
        elif self.kind == 3:    # 重力
            global_vals['time_gravity'] = 5
            global_vals['gravity_side'] = 1 if self.speed[0] < 0 else -1

items = []


def draw():
    screen.clear()
    if global_vals['flash']:
        screen.fill('grey33')
        global_vals['flash'] = False

    screen.draw.filled_rect(pad_1, 'white')
    screen.draw.filled_rect(Rect((pad_1.left-2, pad_1.top), (4, pad_1.height)), 'blue')
    screen.draw.filled_rect(pad_2, 'white')
    screen.draw.filled_rect(Rect((pad_2.right-2, pad_2.top), (4, pad_2.height)), 'red')

    surface_a = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    alpha = 10
    for t in pad_1_trail:
        alpha *= 1.4
        pygame.draw.rect(surface_a, (255, 255, 255, alpha), pygame.Rect(20, t, 10, 100))
    alpha = 10
    for t in pad_2_trail:
        alpha *= 1.4
        pygame.draw.rect(surface_a, (255, 255, 255, alpha), pygame.Rect(WIDTH-20, t, 10, 100))

    for ball in balls:
        if global_vals['time_invisible'] > 0:
            if (global_vals['invisible_side'] > 0 and ball.speed[0] > 0 and WIDTH/2 < ball.pos[0] < WIDTH*4/5) or (
                global_vals['invisible_side'] < 0 and ball.speed[0] < 0 and WIDTH/5 < ball.pos[0] < WIDTH/2):
                continue
        screen.draw.filled_circle(ball.pos, BALL_RADIUS, 'white')
        alpha = 10
        for t in ball.trail:
            alpha *= 1.4
            pygame.draw.circle(surface_a, (255, 255, 255, alpha), t, BALL_RADIUS)
    for ball in balls_ready:
        screen.draw.filled_circle(ball.pos, ball.r, 'white')
    screen.draw.text(":", midtop=(WIDTH/2, 20), fontname="zhaozi", fontsize=64)
    screen.draw.text(f"{scores[0]}", topright=(WIDTH/2 - 40, 20), fontname="zhaozi", fontsize=64)
    screen.draw.text(f"{scores[1]}", topleft=(WIDTH/2 + 40, 20), fontname="zhaozi", fontsize=64)
    for i in items:
        screen.draw.text(i.text, i.pos, fontname="zhaozi", anchor=(0.5, 0.5), angle=i.angle, owidth=1, ocolor=i.color)

    for p in particles:
        pygame.draw.circle(surface_a, (255, 255, 255, 200), p.pos, p.r)

    screen.blit(surface_a, (0, 0))

    # power time
    if global_vals['time_speedup'] > 0:
        l = global_vals['time_speedup'] * 100
        x = (WIDTH - l) / 2
        screen.draw.filled_rect(Rect((x, HEIGHT - 40), (l, 4)), 'red')
        screen.draw.rect(Rect((x, HEIGHT - 40), (l, 4)), 'white')
    if global_vals['time_invisible'] > 0:
        l = global_vals['time_invisible'] * 100
        x = (WIDTH - l) / 2
        screen.draw.filled_rect(Rect((x, HEIGHT - 30), (l, 4)), 'purple')
        screen.draw.rect(Rect((x, HEIGHT - 30), (l, 4)), 'white')
    if global_vals['time_gravity'] > 0:
        l = global_vals['time_gravity'] * 100
        x = (WIDTH - l) / 2
        screen.draw.filled_rect(Rect((x, HEIGHT - 20), (l, 4)), 'orange')
        screen.draw.rect(Rect((x, HEIGHT - 20), (l, 4)), 'white')


def move_mouse(dt):
    mouse_y = pygame.mouse.get_pos()[1]
    if pad_1.center[1] > mouse_y:
        pad_1.y -= dt * MOVE_SPEED
        if pad_1.top < 0:
            pad_1.top = 0
        if pad_1.center[1] < mouse_y:
            pad_1.y = mouse_y - pad_1.height / 2
    elif pad_1.center[1] < mouse_y:
        pad_1.y += dt * PAD_SPEED
        if pad_1.bottom > HEIGHT:
            pad_1.bottom = HEIGHT
        if pad_1.center[1] > mouse_y:
            pad_1.y = mouse_y - pad_1.height / 2


def listen_key(dt):
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


def auto_move_pad(dt):
    target = None
    min_t = 9999
    start = WIDTH / 2
    if global_vals['time_invisible'] > 0 and global_vals['invisible_side'] > 0:
        start = WIDTH * 4 / 5
    for ball in balls + items:
        if start < ball.pos[0] < pad_2.x and ball.speed[0] > 0:
            t = (pad_2.x - ball.pos[0]) / ball.speed[0]
            if t < min_t:
                target = ball.pos[1]
                min_t = t

    if target:
        if pad_2.y + pad_2.height * 0.25 > target:
            pad_2.y -= PAD_SPEED * dt
            if pad_2.top < 0:
                pad_2.top = 0
        elif pad_2.y + pad_2.height * 0.75 < target:
            pad_2.y += PAD_SPEED * dt
            if pad_2.bottom > HEIGHT:
                pad_2.bottom = HEIGHT


def intersect(p1, p2, b1, b2):
    # 判断 b1b2 是否与 p1p2 相交
    k = (b2[1] - b1[1]) / (b2[0] - b1[0])
    y = k * (p1[0] - b1[0]) + b1[1]
    return p1[1] <= y <= p2[1]
    

def update(dt):
    items_to_del = []
    for i in items:
        i.update(dt)
        if (i.speed[0] < 0 and pad_1.collidepoint(i.pos)) or (
            i.speed[0] > 0 and pad_2.collidepoint(i.pos)):
            i.do_effect()
            items_to_del.append(i)
        if i.is_out():
            items_to_del.append(i)
    for i in items_to_del:
        items.remove(i)

    balls_to_del = []
    p1_1 = pad_1.topright
    p1_2 = pad_1.bottomright
    p2_1 = pad_2.topleft
    p2_2 = pad_2.bottomleft
    for ball in balls:
        old_pos = ball.update(dt)        
        if (ball.speed[0] < 0 and ball.pos[0] <= p1_1[0] < old_pos[0] and intersect(p1_1, p1_2, old_pos, ball.pos)) or (
            ball.speed[0] > 0 and ball.pos[0] >= p2_1[0] > old_pos[0] and intersect(p2_1, p2_2, old_pos, ball.pos)):
            px = p1_1[0] if ball.speed[0] < 0 else p2_1[0]
            ball.set([px - (ball.pos[0] - px), ball.pos[1]], [-ball.speed[0], ball.speed[1]])
            ball.times += 1
            pong([px, ball.pos[1]], ball.times, True)
            if random.random() > ITEM_PROB:
                items.append(Item(ball.pos))
        if ball.is_out():
            balls_to_del.append(ball)
    for ball in balls_to_del:
        ball.score()
        balls.remove(ball)

    for ball in balls_ready:
        ball.update(dt)

    pad_1_trail.append(pad_1.y)
    if len(pad_1_trail) > 9:
        pad_1_trail.pop(0)
    pad_2_trail.append(pad_2.y)
    if len(pad_2_trail) > 9:
        pad_2_trail.pop(0)

    listen_key(dt)

    # single mode
    if SINGLE_MODE:
        auto_move_pad(dt)

    global_vals['cool_down'] += dt
    if global_vals['cool_down'] > global_vals['interval'] or len(balls) + len(balls_ready) == 0:
        if global_vals['interval'] > 1:
            global_vals['interval'] *= 0.9
        balls_ready.append(Ball())
        sounds.ready.play()
        global_vals['cool_down'] = 0

    if global_vals['time_speedup'] > 0:
        global_vals['time_speedup'] -= dt
    if global_vals['time_invisible'] > 0:
        global_vals['time_invisible'] -= dt
    if global_vals['time_gravity'] > 0:
        global_vals['time_gravity'] -= dt


music.play('bgm')

pgzrun.go()
