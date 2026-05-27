# Tetris_KM/games/PingPong/game.py
import arcade
import math
import random
from config import Config


class Paddle:
    def __init__(self, x, y, width, height, color, speed):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.speed = speed
        self.score = 0

    def draw(self):
        arcade.draw_lrbt_rectangle_filled(
            self.x - self.width / 2, self.x + self.width / 2,
            self.y - self.height / 2, self.y + self.height / 2,
            self.color
        )

    def move(self, direction, dt):
        if direction != 0:
            self.x += direction * self.speed * dt
            half_w = self.width / 2
            field_width = 1040
            if self.x - half_w < 0: self.x = half_w
            if self.x + half_w > field_width: self.x = field_width - half_w


class Ball:
    def __init__(self):
        self.x = 520
        self.y = 475
        self.radius = 12
        self.base_speed = 260  # ✅ Меньше начальная скорость
        self.speed = self.base_speed
        self.dx = 0
        self.dy = 0
        self.active = False

    def draw(self):
        # ✅ Полностью белый шарик, без теней
        arcade.draw_circle_filled(self.x, self.y, self.radius, (255, 255, 255))

    def reset(self, direction):
        self.speed = self.base_speed  # ✅ Сброс скорости при новом раунде
        angle_deg = random.randint(65, 115)
        angle_rad = math.radians(angle_deg)
        self.dx = math.cos(angle_rad) * self.speed
        self.dy = math.sin(angle_rad) * self.speed * direction
        self.active = False

    def start(self):
        self.active = True

    def update(self, dt, p1, p2, field_height):
        if not self.active:
            return None

        self.x += self.dx * dt
        self.y += self.dy * dt

        if self.x - self.radius < 0:
            self.x = self.radius
            self.dx = -self.dx
        elif self.x + self.radius > 1040:
            self.x = 1040 - self.radius
            self.dx = -self.dx

        if self.dy > 0:
            if p1.y - p1.height / 2 <= self.y + self.radius <= p1.y + p1.height / 2:
                if p1.x - p1.width / 2 <= self.x <= p1.x + p1.width / 2:
                    self.y = p1.y - p1.height / 2 - self.radius
                    self._bounce(p1)
                    return None

        if self.dy < 0:
            if p2.y - p2.height / 2 <= self.y - self.radius <= p2.y + p2.height / 2:
                if p2.x - p2.width / 2 <= self.x <= p2.x + p2.width / 2:
                    self.y = p2.y + p2.height / 2 + self.radius
                    self._bounce(p2)
                    return None

        if self.y > field_height + 50: return "p1_missed"
        if self.y < -50: return "p2_missed"
        return None

    def _bounce(self, paddle):
        self.dy = -self.dy
        hit_offset = (self.x - paddle.x) / (paddle.width / 2)
        hit_offset = max(-1, min(1, hit_offset))
        self.dx += hit_offset * 180

        # ✅ Плавное ускорение (+4% за отскок, макс 650)
        self.speed = min(self.speed * 1.04, 650)

        length = math.sqrt(self.dx ** 2 + self.dy ** 2)
        if length > 0:
            self.dx = (self.dx / length) * self.speed
            self.dy = (self.dy / length) * self.speed


class PingPongGame:
    def __init__(self, total_rounds=5):
        self.width = 1040
        self.height = 950
        self.total_rounds = total_rounds

        self.p1 = Paddle(520, 850, 120, 20, (255, 100, 100), 500)
        self.p2 = Paddle(520, 150, 120, 20, (100, 150, 255), 500)

        self.ball = Ball()
        self.paused = False
        self.show_rules = True
        self.game_over = False
        self.winner = ""
        self.awaiting_start = True
        self.rounds_played = 0

    def update(self, dt, p1_actions, p2_actions):
        if self.paused or self.game_over or self.show_rules:
            return

        self.p1.move((1 if p1_actions.get('right') else 0) - (1 if p1_actions.get('left') else 0), dt)
        self.p2.move((1 if p2_actions.get('right') else 0) - (1 if p2_actions.get('left') else 0), dt)

        if not self.ball.active:
            if self.ball.dy > 0:
                self.ball.x = self.p2.x
                self.ball.y = self.p2.y + self.p2.height / 2 + self.ball.radius + 2
            else:
                self.ball.x = self.p1.x
                self.ball.y = self.p1.y - self.p1.height / 2 - self.ball.radius - 2

        if self.awaiting_start and not self.ball.active:
            if p1_actions.get('up') or p2_actions.get('up'):
                self.ball.start()
                self.awaiting_start = False

        if self.ball.active:
            result = self.ball.update(dt, self.p1, self.p2, self.height)
            if result == "p1_missed":
                self.p2.score += 1
                self._check_win()
                if not self.game_over:
                    self.ball.reset(direction=-1)
                    self.awaiting_start = True
                    self.rounds_played += 1
            elif result == "p2_missed":
                self.p1.score += 1
                self._check_win()
                if not self.game_over:
                    self.ball.reset(direction=1)
                    self.awaiting_start = True
                    self.rounds_played += 1

    def _check_win(self):
        if self.rounds_played >= self.total_rounds:
            self.game_over = True
            if self.p1.score > self.p2.score:
                self.winner = "Игрок 1 (🔴)!"
            elif self.p2.score > self.p1.score:
                self.winner = "Игрок 2 (🔵)!"
            else:
                self.winner = "Ничья!"

    def draw(self):
        arcade.set_background_color((210, 210, 215))

        try:
            arcade.draw_text(f"{self.p1.score}", 480, 490, (180, 80, 80), 40, anchor_x="right")
            arcade.draw_text(":", 520, 490, (140, 140, 140), 40, anchor_x="center")
            arcade.draw_text(f"{self.p2.score}", 560, 490, (80, 120, 180), 40, anchor_x="left")
        except:
            pass

        self.p1.draw()
        self.p2.draw()
        self.ball.draw()

        if self.awaiting_start and not self.game_over and not self.show_rules:
            try:
                arcade.draw_text("Нажмите ВВЕРХ для подачи", 520, 400, (100, 100, 100), 18, anchor_x="center")
            except:
                pass

        if self.paused:
            arcade.draw_lrbt_rectangle_filled(0, self.width, 0, self.height, (0, 0, 0, 150))
            try:
                arcade.draw_text("ПАУЗА", self.width // 2, self.height // 2, (255, 255, 255), 36, anchor_x="center")
            except:
                pass

        if self.show_rules:
            arcade.draw_lrbt_rectangle_filled(0, self.width, 0, self.height, (241, 241, 241, 240))
            try:
                arcade.draw_text("ПРАВИЛА: PING-PONG", self.width // 2, self.height // 2 + 150, (40, 40, 40), 32,
                                 anchor_x="center")
                rules = [
                    " Игрок 1: A/D |  Игрок 2: ←/→",
                    "⚾ Мяч двигается с ракеткой до запуска",
                    "⬆️ Нажмите ВВЕРХ для подачи",
                    " Угол зависит от точки удара",
                    f" {self.total_rounds} раундов. Больше очков = победа!",
                    "", "ENTER - Старт | ESC - Меню"
                ]
                for i, r in enumerate(rules):
                    c = (0, 100, 0) if "ENTER" in r or "ESC" in r else (60, 60, 60)
                    arcade.draw_text(r, self.width // 2, self.height // 2 + 100 - i * 30, c, 16, anchor_x="center")
            except:
                pass

        if self.game_over:
            arcade.draw_lrbt_rectangle_filled(0, self.width, 0, self.height, (240, 240, 240, 230))
            try:
                arcade.draw_text("ИГРА ОКОНЧЕНА", self.width // 2, self.height // 2 + 60, (50, 50, 50), 40,
                                 anchor_x="center")
                wc = (255, 100, 100) if "1" in self.winner else (100, 150, 255)
                arcade.draw_text(self.winner, self.width // 2, self.height // 2, wc, 32, anchor_x="center")
                arcade.draw_text(f"{self.p1.score} : {self.p2.score}", self.width // 2, self.height // 2 - 50,
                                 (80, 80, 80), 24, anchor_x="center")
            except:
                pass

    def toggle_pause(self):
        if not self.show_rules and not self.game_over: self.paused = not self.paused

    def start_game(self):
        self.show_rules = False
        self.p1.score = 0;
        self.p2.score = 0
        self.p1.x = 520;
        self.p2.x = 520
        self.rounds_played = 0
        self.ball.reset(direction=1)
        self.awaiting_start = True