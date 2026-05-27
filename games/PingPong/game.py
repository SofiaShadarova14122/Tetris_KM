# Tetris_KM/games/PingPong/game.py
import arcade, math, random
from config import Config


class Paddle:
    def __init__(self, x, y, w, h, color, speed):
        self.x, self.y = x, y
        self.w, self.h = w, h
        self.color = color
        self.speed = speed

    def draw(self):
        arcade.draw_lrbt_rectangle_filled(self.x - self.w / 2, self.x + self.w / 2, self.y - self.h / 2,
                                          self.y + self.h / 2, self.color)

    def move(self, d, dt):
        if d: self.x += d * self.speed * dt
        self.x = max(self.w / 2, min(1040 - self.w / 2, self.x))


class Ball:
    def __init__(self):
        self.x, self.y = 520, 475
        self.r = 12
        self.base_spd = 260
        self.spd = self.base_spd
        self.dx = self.dy = 0
        self.active = False

    def draw(self):
        arcade.draw_circle_filled(self.x, self.y, self.r, (255, 255, 255))

    def reset(self, px, py, ph, dir):
        self.x = px
        self.y = py + (ph / 2 + self.r + 2) * dir  # +1 = up (P1), -1 = down (P2)
        self.spd = self.base_spd * 0.6
        ang = math.radians(random.randint(65, 115))
        self.dx = math.cos(ang) * self.spd
        self.dy = math.sin(ang) * self.spd * dir
        self.active = False

    def start(self):
        self.active = True

    def update(self, dt, p1, p2, H):
        if not self.active: return None
        self.x += self.dx * dt
        self.y += self.dy * dt

        # Walls
        if self.x - self.r < 0:
            self.x = self.r; self.dx = -self.dx
        elif self.x + self.r > 1040:
            self.x = 1040 - self.r; self.dx = -self.dx

        # Paddles
        if self.dy > 0:  # Going up
            if p1.y - p1.h / 2 <= self.y + self.r <= p1.y + p1.h / 2:
                if p1.x - p1.w / 2 <= self.x <= p1.x + p1.w / 2:
                    self.y = p1.y - p1.h / 2 - self.r
                    self._bounce(p1)
                    return None
        if self.dy < 0:  # Going down
            if p2.y - p2.h / 2 <= self.y - self.r <= p2.y + p2.h / 2:
                if p2.x - p2.w / 2 <= self.x <= p2.x + p2.w / 2:
                    self.y = p2.y + p2.h / 2 + self.r
                    self._bounce(p2)
                    return None

        # Missed
        if self.y > H + 50: return "p1_miss"
        if self.y < -50: return "p2_miss"
        return None

    def _bounce(self, pad):
        self.dy = -self.dy
        off = max(-1, min(1, (self.x - pad.x) / (pad.w / 2)))
        self.dx += off * 180
        self.spd = min(self.spd * 1.04, 650)
        l = math.sqrt(self.dx ** 2 + self.dy ** 2)
        if l: self.dx, self.dy = (self.dx / l) * self.spd, (self.dy / l) * self.spd


class PingPongGame:
    def __init__(self):
        self.W, self.H = 1040, 950
        self.p1 = Paddle(520, 850, 120, 20, Config.P1_COLOR, 500)
        self.p2 = Paddle(520, 150, 120, 20, Config.P2_COLOR, 500)
        self.ball = Ball()
        self.paused = False
        self.show_rules = True
        self.game_over = False
        self.winner = ""
        self.awaiting = True
        self.rounds = 0
        self.max_rounds = 5

    def update(self, dt, a1, a2):
        if self.paused or self.game_over or self.show_rules: return

        d1 = (1 if a1['right'] else 0) - (1 if a1['left'] else 0)
        d2 = (1 if a2['right'] else 0) - (1 if a2['left'] else 0)
        self.p1.move(d1, dt)
        self.p2.move(d2, dt)

        # Sync ball to paddle before launch
        if not self.ball.active:
            if self.ball.dy > 0:  # P2 serves down
                self.ball.x = self.p2.x
                self.ball.y = self.p2.y + self.p2.h / 2 + self.ball.r + 2
            else:  # P1 serves up
                self.ball.x = self.p1.x
                self.ball.y = self.p1.y - self.p1.h / 2 - self.ball.r - 2

        # Launch
        if self.awaiting and not self.ball.active:
            if a1['up'] or a2['up']:
                self.ball.start()
                self.awaiting = False

        if self.ball.active:
            res = self.ball.update(dt, self.p1, self.p2, self.H)
            if res == "p1_miss":
                self.p2.score = getattr(self.p2, 'score', 0) + 1
                self.rounds += 1
                self._check_win()
                if not self.game_over:
                    self.ball.reset(self.p2.x, self.p2.y, self.p2.h, -1)
                    self.awaiting = True
            elif res == "p2_miss":
                self.p1.score = getattr(self.p1, 'score', 0) + 1
                self.rounds += 1
                self._check_win()
                if not self.game_over:
                    self.ball.reset(self.p1.x, self.p1.y, self.p1.h, 1)
                    self.awaiting = True

    def _check_win(self):
        if self.rounds >= self.max_rounds:
            self.game_over = True
            s1, s2 = getattr(self.p1, 'score', 0), getattr(self.p2, 'score', 0)
            if s1 > s2:
                self.winner = "Игрок 1 (🔴)!"
            elif s2 > s1:
                self.winner = "Игрок 2 (🔵)!"
            else:
                self.winner = "Ничья!"

    def draw(self):
        arcade.set_background_color((210, 210, 215))

        # Score (semi-transparent, behind)
        arcade.draw_lrbt_rectangle_filled(480, 560, 470, 510, (255, 255, 255, 180))
        arcade.draw_text(f"{getattr(self.p1, 'score', 0)}", 510, 490, (180, 80, 80), 40, anchor_x="right")
        arcade.draw_text(":", 520, 490, (140, 140, 140), 40, anchor_x="center")
        arcade.draw_text(f"{getattr(self.p2, 'score', 0)}", 530, 490, (80, 120, 180), 40, anchor_x="left")

        self.p1.draw()
        self.p2.draw()
        self.ball.draw()

        if self.awaiting and not self.game_over and not self.show_rules:
            Config.draw_text("Нажмите ВВЕРХ для подачи", 520, 400, (100, 100, 100), 18)

        if self.paused:
            arcade.draw_lrbt_rectangle_filled(0, self.W, 0, self.H, (0, 0, 0, 180))
            Config.draw_text("ПАУЗА", self.W // 2, self.H // 2, (255, 255, 255), 36)

        if self.show_rules:
            arcade.draw_lrbt_rectangle_filled(0, self.W, 0, self.H, (241, 241, 241, 240))
            Config.draw_text("ПРАВИЛА: PING-PONG", self.W // 2, self.H // 2 + 150, (40, 40, 40), 32)
            rules = ["🔴 Игрок 1: A/D | 🔵 Игрок 2: ←/→",
                     "⚾ Мяч двигается с ракеткой до запуска",
                     "⬆️ Нажмите ВВЕРХ для подачи",
                     "💥 Угол зависит от точки удара",
                     "⚡ Мяч ускоряется с каждым ударом",
                     "5 раундов. Больше очков = победа!",
                     "", "ENTER - старт", "ESC - меню"]
            for i, r in enumerate(rules):
                c = (0, 100, 0) if "ENTER" in r or "ESC" in r else (60, 60, 60)
                Config.draw_text(r, self.W // 2, self.H // 2 + 100 - i * 30, c, 16)

        if self.game_over:
            arcade.draw_lrbt_rectangle_filled(0, self.W, 0, self.H, (240, 240, 240, 230))
            Config.draw_text("ИГРА ОКОНЧЕНА", self.W // 2, self.H // 2 + 60, (50, 50, 50), 40)
            wc = Config.P1_COLOR if "1" in self.winner else Config.P2_COLOR
            Config.draw_text(self.winner, self.W // 2, self.H // 2, wc, 32)
            Config.draw_text(f"{getattr(self.p1, 'score', 0)} : {getattr(self.p2, 'score', 0)}", self.W // 2,
                             self.H // 2 - 50, (80, 80, 80), 24)

    def toggle_pause(self):
        if not self.show_rules and not self.game_over: self.paused = not self.paused

    def start(self):
        self.show_rules = False
        self.p1.score = self.p2.score = 0
        self.p1.x = self.p2.x = 520
        self.rounds = 0
        self.ball.reset(self.p1.x, self.p1.y, self.p1.h, 1)
        self.awaiting = True