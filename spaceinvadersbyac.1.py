#!/usr/bin/env python3
"""
ultra_invaders.py — ULTRA!INVADERS 0.1
=======================================
A self-contained Space Invaders recreation. FILES=OFF.

* No ROMs, images, fonts, or sound files.
* Graphics drawn with primitive shapes.
* Audio synthesized in memory.
* Full game: menu, help, about, pause, game over, win.
* 10 arcade-style levels + endless mode.
* Destructible barriers, UFO bonus, lives, high score, respawn.
* 60 FPS target.

Controls:
    Left / Right / A / D : Move cannon
    Space                : Fire
    P / Escape           : Pause
    Enter                : Select / start / continue
    M                    : Toggle sound
    Q                    : Main menu while paused
"""

from __future__ import annotations

import math
import random
import sys

try:
    import pygame as pg
except ImportError:
    print("Install pygame-ce first:  python -m pip install pygame-ce", file=sys.stderr)
    sys.exit(1)

# ─── Constants ────────────────────────────────────────────────────────────
APP_TITLE = "ULTRA!INVADERS 0.1"
FILES_OFF = True
FPS = 60
WIDTH, HEIGHT = 640, 720
PLAYFIELD_TOP = 80
PLAYFIELD_BOTTOM = 640

BLACK = (0, 0, 0)
WHITE = (240, 240, 240)
GREEN = (80, 240, 120)
RED = (240, 80, 80)
YELLOW = (240, 220, 80)
CYAN = (80, 220, 240)
PURPLE = (200, 120, 240)
GREY = (120, 120, 140)
DARK = (16, 16, 24)
ORANGE = (240, 160, 60)

INVADER_COLORS = (GREEN, CYAN, YELLOW, PURPLE, RED)

MAX_LEVEL = 10

# ─── Embedded 5x7 font ────────────────────────────────────────────────────
GLYPHS = {
    "A": "01110/10001/10001/11111/10001/10001/10001",
    "B": "11110/10001/10001/11110/10001/10001/11110",
    "C": "01111/10000/10000/10000/10000/10000/01111",
    "D": "11110/10001/10001/10001/10001/10001/11110",
    "E": "11111/10000/10000/11110/10000/10000/11111",
    "F": "11111/10000/10000/11110/10000/10000/10000",
    "G": "01111/10000/10000/10111/10001/10001/01111",
    "H": "10001/10001/10001/11111/10001/10001/10001",
    "I": "11111/00100/00100/00100/00100/00100/11111",
    "J": "00111/00010/00010/00010/10010/10010/01100",
    "K": "10001/10010/10100/11000/10100/10010/10001",
    "L": "10000/10000/10000/10000/10000/10000/11111",
    "M": "10001/11011/10101/10101/10001/10001/10001",
    "N": "10001/11001/10101/10011/10001/10001/10001",
    "O": "01110/10001/10001/10001/10001/10001/01110",
    "P": "11110/10001/10001/11110/10000/10000/10000",
    "Q": "01110/10001/10001/10001/10101/10010/01101",
    "R": "11110/10001/10001/11110/10100/10010/10001",
    "S": "01111/10000/10000/01110/00001/00001/11110",
    "T": "11111/00100/00100/00100/00100/00100/00100",
    "U": "10001/10001/10001/10001/10001/10001/01110",
    "V": "10001/10001/10001/10001/10001/01010/00100",
    "W": "10001/10001/10001/10101/10101/11011/10001",
    "X": "10001/10001/01010/00100/01010/10001/10001",
    "Y": "10001/10001/01010/00100/00100/00100/00100",
    "Z": "11111/00001/00010/00100/01000/10000/11111",
    "0": "01110/10001/10011/10101/11001/10001/01110",
    "1": "00100/01100/00100/00100/00100/00100/01110",
    "2": "01110/10001/00001/00010/00100/01000/11111",
    "3": "11110/00001/00001/01110/00001/00001/11110",
    "4": "00010/00110/01010/10010/11111/00010/00010",
    "5": "11111/10000/10000/11110/00001/00001/11110",
    "6": "01110/10000/10000/11110/10001/10001/01110",
    "7": "11111/00001/00010/00100/01000/01000/01000",
    "8": "01110/10001/10001/01110/10001/10001/01110",
    "9": "01110/10001/10001/01111/00001/00001/01110",
    "!": "00100/00100/00100/00100/00100/00000/00100",
    "?": "01110/10001/00001/00010/00100/00000/00100",
    ".": "00000/00000/00000/00000/00000/00110/00110",
    ",": "00000/00000/00000/00000/00110/00110/00000",
    "-": "00000/00000/00000/11111/00000/00000/00000",
    "_": "00000/00000/00000/00000/00000/00000/11111",
    ":": "00000/00110/00110/00000/00110/00110/00000",
    "/": "00001/00010/00010/00100/01000/01000/10000",
    "+": "00000/00100/00100/11111/00100/00100/00000",
    "=": "00000/00000/11111/00000/11111/00000/00000",
    "(": "00010/00100/01000/01000/01000/00100/00010",
    ")": "01000/00100/00010/00010/00010/00100/01000",
    "*": "00000/10101/01110/11111/01110/10101/00000",
    " ": "00000/00000/00000/00000/00000/00000/00000",
}


def text_surface(value: str, color=WHITE, scale=1) -> pg.Surface:
    value = value.upper()
    w = max(1, len(value) * 6 - 1) * scale
    h = 7 * scale
    surf = pg.Surface((w, h), pg.SRCALPHA)
    for i, ch in enumerate(value):
        rows = GLYPHS.get(ch, GLYPHS["?"]).split("/")
        for y, row in enumerate(rows):
            for x, bit in enumerate(row):
                if bit == "1":
                    pg.draw.rect(surf, color,
                                 ((i * 6 + x) * scale, y * scale, scale, scale))
    return surf


def draw_text(surf, value, x, y, color=WHITE, scale=1, center=False):
    label = text_surface(str(value), color, scale)
    if center:
        x = x - label.get_width() // 2
    surf.blit(label, (round(x), round(y)))


# ─── Audio (synthesized in memory) ────────────────────────────────────────
class Audio:
    RATE = 22050

    def __init__(self):
        self.available = False
        self.muted = False
        self.sounds: dict[str, pg.mixer.Sound] = {}
        try:
            pg.mixer.pre_init(self.RATE, -16, 1, 256)
            pg.mixer.init(self.RATE, -16, 1, 256)
            self.available = True
            self._build()
        except Exception:
            self.available = False

    def _synth(self, duration, freq_fn, volume=0.2, square=True):
        n = max(1, int(self.RATE * duration))
        buf = bytearray()
        phase = 0.0
        for i in range(n):
            t = i / self.RATE
            f = freq_fn(t)
            phase = (phase + max(0.0, f) / self.RATE) % 1.0
            wave = 1.0 if phase < 0.5 else -1.0 if square else 1.0 - 4.0 * abs(phase - 0.5)
            env = min(1.0, i / 60, (n - 1 - i) / 120)
            sample = int(wave * env * volume * 32767)
            buf += sample.to_bytes(2, "little", signed=True)
        return pg.mixer.Sound(buffer=bytes(buf))

    def _build(self):
        self.sounds["shoot"] = self._synth(0.12, lambda t: 900 - 4000 * t, 0.18)
        self.sounds["invader_die"] = self._synth(0.18, lambda t: 400 + 1200 * t, 0.22)
        self.sounds["player_die"] = self._synth(0.55, lambda t: max(60, 500 - 900 * t), 0.25)
        self.sounds["step"] = self._synth(0.06, lambda t: 120, 0.12)
        self.sounds["ufo"] = self._synth(0.25, lambda t: 1400 + 200 * math.sin(t * 60), 0.14)
        self.sounds["menu"] = self._synth(0.07, lambda t: 660, 0.14)
        self.sounds["select"] = self._synth(0.12, lambda t: 880 + 200 * t, 0.18)
        self.sounds["levelup"] = self._synth(0.30, lambda t: 660 + 800 * t, 0.20)
        self.sounds["extra_life"] = self._synth(0.45, lambda t: 520 + 1200 * t, 0.22)

    def play(self, name):
        if self.available and not self.muted and name in self.sounds:
            self.sounds[name].play()

    def toggle(self):
        self.muted = not self.muted
        return self.muted


# ─── Entities ─────────────────────────────────────────────────────────────
class Player:
    W, H = 40, 20

    def __init__(self):
        self.x = WIDTH / 2
        self.y = PLAYFIELD_BOTTOM - 40
        self.alive = True
        self.cool = 0.0

    @property
    def rect(self):
        return pg.Rect(int(self.x - self.W / 2), int(self.y - self.H / 2), self.W, self.H)

    def update(self, dt, keys):
        speed = 260.0
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.x -= speed * dt
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.x += speed * dt
        self.x = max(self.W / 2 + 8, min(WIDTH - self.W / 2 - 8, self.x))
        self.cool = max(0.0, self.cool - dt)

    def can_fire(self):
        return self.alive and self.cool <= 0.0

    def fire(self):
        self.cool = 0.28
        return Bullet(self.x, self.y - self.H / 2 - 4, -1)

    def draw(self, surf):
        r = self.rect
        pg.draw.rect(surf, GREEN, (r.x, r.y + 8, r.w, 6))
        pg.draw.polygon(surf, GREEN, [
            (r.x + 4, r.y + 8), (r.centerx, r.y), (r.right - 4, r.y + 8),
        ])
        pg.draw.rect(surf, GREEN, (r.centerx - 2, r.y - 4, 4, 6))


class Bullet:
    W, H = 4, 12
    SPEED = 520.0

    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.dy = direction * self.SPEED
        self.alive = True

    @property
    def rect(self):
        return pg.Rect(int(self.x - self.W / 2), int(self.y - self.H / 2), self.W, self.H)

    def update(self, dt):
        self.y += self.dy * dt
        if self.y < PLAYFIELD_TOP - 20 or self.y > PLAYFIELD_BOTTOM + 40:
            self.alive = False

    def draw(self, surf, color=WHITE):
        pg.draw.rect(surf, color, self.rect)


INVADER_FRAMES = (
    (
        ("..X..X..",
         "...XX...",
         "..XXXX..",
         ".XX..XX.",
         "XXXXXXXX",
         "X.XXXX.X",
         "X.X..X.X",
         "...XX..."),
        ("..X..X..",
         "X..XX..X",
         "X.XXXX.X",
         "XXX..XXX",
         "XXXXXXXX",
         ".X.XX.X.",
         "X......X",
         ".X....X."),
    ),
    (
        ("..XXXX..",
         ".XXXXXX.",
         "XX.XX.XX",
         "XXXXXXXX",
         "X.XXXX.X",
         "X.X..X.X",
         "..X..X..",
         ".X....X."),
        ("..XXXX..",
         ".XXXXXX.",
         "XX.XX.XX",
         "XXXXXXXX",
         "..X..X..",
         ".X.XX.X.",
         "X......X",
         ".X....X."),
    ),
    (
        ("...XX...",
         "..XXXX..",
         ".XXXXXX.",
         "XX.XX.XX",
         "XXXXXXXX",
         "..X..X..",
         ".X.XX.X.",
         "X.X..X.X"),
        ("...XX...",
         "..XXXX..",
         ".XXXXXX.",
         "XX.XX.XX",
         "XXXXXXXX",
         ".X.XX.X.",
         "X.X..X.X",
         ".X....X."),
    ),
)


class Invader:
    W, H = 28, 28

    def __init__(self, x, y, tier):
        self.x = x
        self.y = y
        self.tier = tier
        self.alive = True

    @property
    def rect(self):
        return pg.Rect(int(self.x - self.W / 2), int(self.y - self.H / 2), self.W, self.H)

    @property
    def points(self):
        return (30, 20, 10)[self.tier]

    def draw(self, surf, frame):
        grid = INVADER_FRAMES[self.tier][frame]
        color = INVADER_COLORS[self.tier]
        cell = self.W / 8
        x0 = self.x - self.W / 2
        y0 = self.y - self.H / 2
        for gy, row in enumerate(grid):
            for gx, bit in enumerate(row):
                if bit == "X":
                    pg.draw.rect(surf, color,
                                 (int(x0 + gx * cell), int(y0 + gy * cell),
                                  max(1, int(cell)), max(1, int(cell))))


class UFO:
    W, H = 40, 16
    SPEED = 140.0

    def __init__(self, direction):
        self.x = -self.W if direction > 0 else WIDTH + self.W
        self.y = PLAYFIELD_TOP + 20
        self.dx = direction * self.SPEED
        self.alive = True

    @property
    def rect(self):
        return pg.Rect(int(self.x - self.W / 2), int(self.y - self.H / 2), self.W, self.H)

    def update(self, dt):
        self.x += self.dx * dt
        if self.x < -self.W - 20 or self.x > WIDTH + self.W + 20:
            self.alive = False

    def draw(self, surf):
        r = self.rect
        pg.draw.ellipse(surf, RED, (r.x, r.y, r.w, r.h))
        pg.draw.rect(surf, RED, (r.x + r.w // 2 - 3, r.y - 4, 6, 6))
        pg.draw.rect(surf, BLACK, (r.x + 6, r.y + r.h // 2 - 2, r.w - 12, 3))


class Barrier:
    COLS, ROWS = 10, 6
    CELL = 4

    def __init__(self, cx, cy):
        self.cx = cx
        self.cy = cy
        self.grid = [[True] * self.COLS for _ in range(self.ROWS)]
        for x in range(3, self.COLS - 3):
            self.grid[0][x] = False
            self.grid[1][x] = False

    def rects(self):
        x0 = self.cx - (self.COLS * self.CELL) / 2
        y0 = self.cy - (self.ROWS * self.CELL) / 2
        out = []
        for y in range(self.ROWS):
            for x in range(self.COLS):
                if self.grid[y][x]:
                    out.append(pg.Rect(int(x0 + x * self.CELL),
                                       int(y0 + y * self.CELL),
                                       self.CELL, self.CELL))
        return out

    def hit(self, rect):
        x0 = self.cx - (self.COLS * self.CELL) / 2
        y0 = self.cy - (self.ROWS * self.CELL) / 2
        for y in range(self.ROWS):
            for x in range(self.COLS):
                if not self.grid[y][x]:
                    continue
                r = pg.Rect(int(x0 + x * self.CELL), int(y0 + y * self.CELL),
                            self.CELL, self.CELL)
                if r.colliderect(rect):
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < self.COLS and 0 <= ny < self.ROWS:
                                self.grid[ny][nx] = False
                    return True
        return False

    def draw(self, surf):
        for r in self.rects():
            pg.draw.rect(surf, GREEN, r)


# ─── Level configuration (10 arcade-style + endless ramp) ─────────────────
LEVEL_CONFIG = [
    dict(rows=5, cols=10, spawn_y=PLAYFIELD_TOP + 40, drop=14, step_x=10,
         interval=0.85, fire=0.45),
    dict(rows=5, cols=10, spawn_y=PLAYFIELD_TOP + 48, drop=14, step_x=11,
         interval=0.78, fire=0.50),
    dict(rows=5, cols=10, spawn_y=PLAYFIELD_TOP + 56, drop=15, step_x=12,
         interval=0.70, fire=0.58),
    dict(rows=5, cols=11, spawn_y=PLAYFIELD_TOP + 60, drop=15, step_x=12,
         interval=0.64, fire=0.62),
    dict(rows=6, cols=10, spawn_y=PLAYFIELD_TOP + 56, drop=16, step_x=13,
         interval=0.58, fire=0.66),
    dict(rows=6, cols=11, spawn_y=PLAYFIELD_TOP + 60, drop=16, step_x=13,
         interval=0.52, fire=0.70),
    dict(rows=6, cols=11, spawn_y=PLAYFIELD_TOP + 64, drop=17, step_x=14,
         interval=0.46, fire=0.74),
    dict(rows=6, cols=12, spawn_y=PLAYFIELD_TOP + 68, drop=17, step_x=14,
         interval=0.42, fire=0.78),
    dict(rows=7, cols=11, spawn_y=PLAYFIELD_TOP + 64, drop=18, step_x=15,
         interval=0.38, fire=0.82),
    dict(rows=7, cols=12, spawn_y=PLAYFIELD_TOP + 68, drop=18, step_x=16,
         interval=0.34, fire=0.86),
]


def level_config(level: int, endless: bool = False) -> dict:
    idx = max(1, level)
    if idx <= len(LEVEL_CONFIG):
        cfg = dict(LEVEL_CONFIG[idx - 1])
        cfg["name"] = f"LEVEL {idx}"
        cfg["endless"] = False
        return cfg
    over = idx - len(LEVEL_CONFIG)
    cfg = dict(LEVEL_CONFIG[-1])
    cfg["rows"] = min(8, 7 + over // 3)
    cfg["cols"] = min(13, 12 + over // 5)
    cfg["spawn_y"] = min(PLAYFIELD_TOP + 96, PLAYFIELD_TOP + 68 + over * 2)
    cfg["drop"] = min(22, 18 + over // 4)
    cfg["step_x"] = min(20, 16 + over // 3)
    cfg["interval"] = max(0.16, 0.34 - over * 0.02)
    cfg["fire"] = min(0.95, 0.86 + over * 0.01)
    cfg["name"] = f"LEVEL {idx}*"
    cfg["endless"] = True
    return cfg


# ─── States ───────────────────────────────────────────────────────────────
MENU, PLAY, PAUSED, HELP, ABOUT, GAMEOVER, WIN, LEVEL_INTRO = range(8)


class Game:
    def __init__(self):
        self.state = MENU
        self.menu_index = 0
        self.menu_items = ["PLAY GAME", "ENDLESS MODE", "HELP", "ABOUT", "EXIT"]
        self.audio = Audio()
        self.endless = False
        self.high = 0
        self.next_extra_life = 5000
        self.intro_timer = 0.0
        self.reset()

    def reset(self):
        self.player = Player()
        self.bullets: list[Bullet] = []
        self.enemy_bullets: list[Bullet] = []
        self.invaders: list[Invader] = []
        self.barriers = []
        self.ufo: UFO | None = None
        self.ufo_timer = random.uniform(12.0, 20.0)
        self.score = 0
        self.lives = 3
        self.level = 1
        self.invader_dir = 1
        self.invader_step = 0.0
        self.invader_frame = 0
        self.player_respawn = 0.0
        self.next_extra_life = 5000
        self.cfg = level_config(1, self.endless)
        self._build_barriers()
        self._spawn_wave()
        self.intro_timer = 0.0

    def _build_barriers(self):
        self.barriers = [
            Barrier(WIDTH * 0.2, PLAYFIELD_BOTTOM - 110),
            Barrier(WIDTH * 0.5, PLAYFIELD_BOTTOM - 110),
            Barrier(WIDTH * 0.8, PLAYFIELD_BOTTOM - 110),
        ]

    def _spawn_wave(self):
        self.invaders.clear()
        cfg = self.cfg
        rows = cfg["rows"]
        cols = cfg["cols"]
        spacing_x = 40 if cols >= 11 else 42
        spacing_y = 32 if rows >= 6 else 34
        total_w = (cols - 1) * spacing_x
        start_x = (WIDTH - total_w) / 2
        start_y = cfg["spawn_y"]
        for r in range(rows):
            tier = min(2, r * 3 // max(1, rows))
            for c in range(cols):
                self.invaders.append(
                    Invader(start_x + c * spacing_x, start_y + r * spacing_y, tier)
                )
        self.invader_dir = 1
        self.invader_step = 0.0

    def _alive_invaders(self):
        return [i for i in self.invaders if i.alive]

    def _add_score(self, points: int):
        self.score += points
        self.high = max(self.high, self.score)
        while self.score >= self.next_extra_life:
            self.lives += 1
            self.audio.play("extra_life")
            self.next_extra_life += 5000

    def _next_level(self):
        self.level += 1
        if not self.endless and self.level > MAX_LEVEL:
            self.state = WIN
            return
        self.cfg = level_config(self.level, self.endless)
        self.bullets.clear()
        self.enemy_bullets.clear()
        self._build_barriers()
        self._spawn_wave()
        self.audio.play("levelup")
        self.state = LEVEL_INTRO
        self.intro_timer = 1.6

    # ── events ────────────────────────────────────────────────────────────
    def handle_event(self, event):
        if event.type == pg.KEYDOWN:
            if self.state == MENU:
                self._menu_key(event.key)
            elif self.state == PLAY:
                self._play_key(event.key)
            elif self.state == PAUSED:
                self._paused_key(event.key)
            elif self.state == LEVEL_INTRO:
                if event.key in (pg.K_RETURN, pg.K_SPACE, pg.K_ESCAPE):
                    self.intro_timer = 0.0
            elif self.state in (HELP, ABOUT, GAMEOVER, WIN):
                if event.key in (pg.K_ESCAPE, pg.K_RETURN, pg.K_SPACE):
                    self.audio.play("menu")
                    self.state = MENU

    def _menu_key(self, key):
        if key in (pg.K_UP, pg.K_w):
            self.menu_index = (self.menu_index - 1) % len(self.menu_items)
            self.audio.play("menu")
        elif key in (pg.K_DOWN, pg.K_s):
            self.menu_index = (self.menu_index + 1) % len(self.menu_items)
            self.audio.play("menu")
        elif key in (pg.K_RETURN, pg.K_SPACE):
            self._activate_menu()
        elif key == pg.K_ESCAPE:
            pg.event.post(pg.event.Event(pg.QUIT))

    def _activate_menu(self):
        label = self.menu_items[self.menu_index]
        self.audio.play("select")
        if label == "PLAY GAME":
            self.endless = False
            self.reset()
            self.state = PLAY
        elif label == "ENDLESS MODE":
            self.endless = True
            self.reset()
            self.state = PLAY
        elif label == "HELP":
            self.state = HELP
        elif label == "ABOUT":
            self.state = ABOUT
        else:
            pg.event.post(pg.event.Event(pg.QUIT))

    def _play_key(self, key):
        if key == pg.K_SPACE and self.player.can_fire():
            self.bullets.append(self.player.fire())
            self.audio.play("shoot")
        elif key in (pg.K_p, pg.K_ESCAPE):
            self.audio.play("menu")
            self.state = PAUSED
        elif key == pg.K_m:
            self.audio.toggle()

    def _paused_key(self, key):
        if key in (pg.K_p, pg.K_ESCAPE, pg.K_RETURN):
            self.audio.play("menu")
            self.state = PLAY
        elif key == pg.K_q:
            self.audio.play("menu")
            self.state = MENU
        elif key == pg.K_m:
            self.audio.toggle()

    # ── update ────────────────────────────────────────────────────────────
    def update(self, dt):
        if self.state == LEVEL_INTRO:
            self.intro_timer -= dt
            if self.intro_timer <= 0.0:
                self.state = PLAY
            return

        if self.state != PLAY:
            return

        keys = pg.key.get_pressed()

        if self.player_respawn > 0.0:
            self.player_respawn -= dt
            if self.player_respawn <= 0.0:
                self.player.alive = True
            return

        self.player.update(dt, keys)

        if keys[pg.K_SPACE] and self.player.can_fire():
            self.bullets.append(self.player.fire())
            self.audio.play("shoot")

        for b in self.bullets:
            b.update(dt)
        for b in self.enemy_bullets:
            b.update(dt)

        self.bullets = [b for b in self.bullets if b.alive]
        self.enemy_bullets = [b for b in self.enemy_bullets if b.alive]

        if self.ufo:
            self.ufo.update(dt)
            if not self.ufo.alive:
                self.ufo = None
        else:
            self.ufo_timer -= dt
            if self.ufo_timer <= 0.0:
                direction = random.choice((-1, 1))
                self.ufo = UFO(direction)
                self.audio.play("ufo")
                self.ufo_timer = random.uniform(14.0, 22.0)

        self._update_invaders(dt)
        self._collisions()
        self._check_end()

    def _update_invaders(self, dt):
        alive = self._alive_invaders()
        if not alive:
            return
        cfg = self.cfg
        self.invader_step += dt
        if self.invader_step < cfg["interval"]:
            return
        self.invader_step = 0.0
        self.invader_frame ^= 1
        self.audio.play("step")

        step_x = cfg["step_x"]
        edge = False
        for inv in alive:
            nx = inv.x + self.invader_dir * step_x
            if nx < inv.W / 2 + 8 or nx > WIDTH - inv.W / 2 - 8:
                edge = True
                break
        if edge:
            self.invader_dir *= -1
            for inv in alive:
                inv.y += cfg["drop"]
        else:
            for inv in alive:
                inv.x += self.invader_dir * step_x

        if alive and random.random() < cfg["fire"]:
            shooter = random.choice(alive)
            self.enemy_bullets.append(
                Bullet(shooter.x, shooter.y + shooter.H / 2 + 4, 1)
            )

    def _collisions(self):
        for b in list(self.bullets):
            if not b.alive:
                continue
            br = b.rect
            hit = False
            for inv in self._alive_invaders():
                if inv.rect.colliderect(br):
                    inv.alive = False
                    self._add_score(inv.points)
                    b.alive = False
                    self.audio.play("invader_die")
                    hit = True
                    break
            if hit:
                continue
            if self.ufo and self.ufo.rect.colliderect(br):
                self._add_score(100)
                b.alive = False
                self.ufo.alive = False
                self.audio.play("invader_die")
                continue
            for bar in self.barriers:
                if bar.hit(br):
                    b.alive = False
                    break

        for b in list(self.enemy_bullets):
            if not b.alive:
                continue
            br = b.rect
            for bar in self.barriers:
                if bar.hit(br):
                    b.alive = False
                    break
            if not b.alive:
                continue
            if self.player.alive and self.player.rect.colliderect(br):
                b.alive = False
                self.player.alive = False
                self.lives -= 1
                self.audio.play("player_die")
                if self.lives > 0:
                    self.player_respawn = 1.2

        for inv in self._alive_invaders():
            if inv.y + inv.H / 2 >= PLAYFIELD_BOTTOM - 20:
                self.state = GAMEOVER
                return

    def _check_end(self):
        if not self._alive_invaders():
            self._next_level()
        elif self.lives <= 0:
            self.state = GAMEOVER

    # ── draw ──────────────────────────────────────────────────────────────
    def draw(self, surf):
        surf.fill(BLACK)
        self._draw_stars(surf)

        if self.state == MENU:
            self._draw_menu(surf)
            return

        self._draw_playfield_border(surf)
        self._draw_hud(surf)

        if self.state in (PLAY, PAUSED, LEVEL_INTRO):
            for bar in self.barriers:
                bar.draw(surf)
            if self.player.alive:
                self.player.draw(surf)
            for b in self.bullets:
                b.draw(surf, WHITE)
            for b in self.enemy_bullets:
                b.draw(surf, RED)
            for inv in self._alive_invaders():
                inv.draw(surf, self.invader_frame)
            if self.ufo:
                self.ufo.draw(surf)

        if self.state == LEVEL_INTRO:
            self._draw_center_panel(surf, self.cfg.get("name", "LEVEL"), [
                "GET READY",
            ])
        elif self.state == PAUSED:
            self._draw_center_panel(surf, "PAUSED", [
                "ENTER / P RESUME",
                "Q MAIN MENU",
                "M SOUND",
            ])
        elif self.state == GAMEOVER:
            self._draw_center_panel(surf, "GAME OVER", [
                f"SCORE {self.score}",
                f"HIGH  {self.high}",
                f"REACHED LEVEL {self.level}",
                "",
                "ENTER MENU",
            ])
        elif self.state == WIN:
            self._draw_center_panel(surf, "YOU WIN", [
                f"SCORE {self.score}",
                f"HIGH  {self.high}",
                "",
                "ALL 10 LEVELS CLEARED",
                "",
                "ENTER MENU",
            ])
        elif self.state == HELP:
            self._draw_help(surf)
        elif self.state == ABOUT:
            self._draw_about(surf)

    def _draw_stars(self, surf):
        rng = random.Random(1337)
        for _ in range(90):
            x = rng.randrange(WIDTH)
            y = rng.randrange(HEIGHT)
            c = 200 if rng.random() > 0.7 else 110
            surf.set_at((x, y), (c, c, c))

    def _draw_playfield_border(self, surf):
        pg.draw.rect(surf, GREY,
                     (4, PLAYFIELD_TOP - 4, WIDTH - 8,
                      PLAYFIELD_BOTTOM - PLAYFIELD_TOP + 8), 1)

    def _draw_hud(self, surf):
        draw_text(surf, "SCORE", 12, 12, CYAN, 2)
        draw_text(surf, f"{self.score:06d}", 12, 30, WHITE, 2)
        draw_text(surf, "HIGH", WIDTH // 2 - 30, 12, CYAN, 2)
        draw_text(surf, f"{self.high:06d}", WIDTH // 2 - 30, 30, WHITE, 2)

        if self.endless:
            label = f"LEVEL {self.level}*"
        else:
            label = f"LEVEL {self.level}/{MAX_LEVEL}"
        draw_text(surf, label, WIDTH - 140, 12, CYAN, 2)

        for i in range(self.lives - 1):
            x = WIDTH - 140 + i * 24
            y = 34
            pg.draw.rect(surf, GREEN, (x, y + 6, 18, 4))
            pg.draw.polygon(surf, GREEN, [(x + 2, y + 6), (x + 9, y), (x + 16, y + 6)])

        if self.audio.muted:
            draw_text(surf, "SOUND OFF", WIDTH - 120, HEIGHT - 20, GREY, 1)

    def _draw_menu(self, surf):
        draw_text(surf, "ULTRA!INVADERS", WIDTH // 2, 100, GREEN, 4, center=True)
        draw_text(surf, "0.1", WIDTH // 2, 160, CYAN, 2, center=True)
        draw_text(surf, "FILES=OFF", WIDTH // 2, 190, GREY, 1, center=True)

        y0 = 270
        for i, label in enumerate(self.menu_items):
            color = YELLOW if i == self.menu_index else WHITE
            prefix = "> " if i == self.menu_index else "  "
            draw_text(surf, prefix + label, WIDTH // 2, y0 + i * 34, color, 2, center=True)

        draw_text(surf, "10 LEVELS  ·  ENDLESS MODE  ·  ALL FILES=OFF",
                  WIDTH // 2, HEIGHT - 110, CYAN, 1, center=True)
        draw_text(surf, "ARROWS SELECT   ENTER CONFIRM",
                  WIDTH // 2, HEIGHT - 80, CYAN, 1, center=True)
        draw_text(surf, "LEFT/RIGHT MOVE   SPACE FIRE   P PAUSE   M SOUND",
                  WIDTH // 2, HEIGHT - 60, GREY, 1, center=True)
        draw_text(surf, "(C) 1999-2026 AC CO", WIDTH // 2, HEIGHT - 30, GREY, 1, center=True)

    def _draw_help(self, surf):
        draw_text(surf, "HELP", WIDTH // 2, 40, YELLOW, 3, center=True)
        lines = [
            "MOVE       LEFT / RIGHT  OR  A / D",
            "FIRE       SPACE",
            "PAUSE      P  OR  ESC",
            "SOUND      M",
            "MENU       Q  (WHILE PAUSED)",
            "",
            "SHOOT ALL INVADERS TO CLEAR A WAVE.",
            "10 LEVELS IN NORMAL MODE.",
            "ENDLESS MODE KEEPS GOING (LEVEL 11+).",
            "DO NOT LET THEM REACH THE BOTTOM.",
            "BARRIERS ABSORB SHOTS. USE THEM.",
            "UFO GIVES 100 PTS. EXTRA LIFE EVERY 5000.",
            "",
            "ENTER OR ESC TO RETURN",
        ]
        y = 110
        for line in lines:
            draw_text(surf, line, WIDTH // 2, y, WHITE, 1, center=True)
            y += 22

    def _draw_about(self, surf):
        draw_text(surf, "ABOUT", WIDTH // 2, 40, YELLOW, 3, center=True)
        lines = [
            "ULTRA!INVADERS 0.1",
            "",
            "A SELF-CONTAINED SPACE INVADERS RECREATION.",
            "FILES=OFF - NO ROMS, IMAGES, FONTS, OR SOUND FILES.",
            "GRAPHICS DRAWN WITH PRIMITIVES.",
            "AUDIO SYNTHESIZED IN MEMORY.",
            "",
            "10 ARCADE-STYLE LEVELS + ENDLESS MODE.",
            "DESTRUCTIBLE BARRIERS. UFO BONUS. EXTRA LIVES.",
            "GAMEPLAY IS A RECREATION, NOT A ROM EMULATION.",
            "",
            "CONTROLS: ARROWS / A D / SPACE / P / M / Q",
            "",
            "(C) 1999-2026 AC CO",
            "",
            "ENTER OR ESC TO RETURN",
        ]
        y = 100
        for line in lines:
            draw_text(surf, line, WIDTH // 2, y, WHITE, 1, center=True)
            y += 22

    def _draw_center_panel(self, surf, title, lines):
        box = pg.Rect(WIDTH // 2 - 200, HEIGHT // 2 - 110, 400, 220)
        pg.draw.rect(surf, DARK, box)
        pg.draw.rect(surf, CYAN, box, 2)
        draw_text(surf, title, box.centerx, box.y + 16, YELLOW, 3, center=True)
        y = box.y + 70
        for line in lines:
            draw_text(surf, line, box.centerx, y, WHITE, 1, center=True)
            y += 22


def main():
    pg.init()
    pg.display.set_caption(APP_TITLE)
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    clock = pg.time.Clock()
    game = Game()

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        dt = min(dt, 0.05)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            else:
                game.handle_event(event)
        game.update(dt)
        game.draw(screen)
        pg.display.flip()

    pg.quit()


if __name__ == "__main__":
    main()