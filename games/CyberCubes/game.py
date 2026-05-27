# Tetris_KM/games/CyberCubes/game.py
import arcade, random
from .arena import Arena
from .player import Player
from config import Config


class CyberCubesGame:
    def __init__(self, mode='versus'):
        self.mode = mode
        self.W, self.H = 1040, 950
        self.FW, self.FH = 320, 640  # 10x20 клеток по 32px
        self.CX = self.W // 2
        self.Y = (950 - self.FH) // 2

        if mode == 'coop':
            self.X1, self.X2 = self.CX - self.FW - 40, self.CX + 40
        else:
            self.X1, self.X2 = self.CX - self.FW - 60, self.CX + 60

        self.p1 = Player(Arena(10, 20), 1)
        self.p2 = Player(Arena(10, 20), 2)
        self.game_over = False
        self.paused = False
        self.show_rules = True
        self.winner = ""

    def update(self, dt, a1, a2):
        if self.paused or self.game_over or self.show_rules: return
        self.p1.update(dt, a1)
        self.p2.update(dt, a2)

        if self.mode == 'coop':
            # Синхронная очистка линий
            for y in range(20):
                if all(self.p1.arena.m[y][x] and self.p2.arena.m[y][x] for x in range(10)):
                    del self.p1.arena.m[y];
                    self.p1.arena.m.insert(0, [0] * 10)
                    del self.p2.arena.m[y];
                    self.p2.arena.m.insert(0, [0] * 10)
                    self.p1.score += 10;
                    self.p2.score += 10
        else:
            # Versus: мусор
            for p, opp in [(self.p1, self.p2), (self.p2, self.p1)]:
                lines = p.arena.sweep()
                if lines:
                    p.score += lines * 10
                    opp.arena.add_garbage(lines)
            self.p1.arena.apply_garbage()
            self.p2.arena.apply_garbage()

        if self.p1.game_over and self.p2.game_over:
            self.game_over = True
            self.winner = "Ничья!" if self.p1.score == self.p2.score else f"{'Игрок 1' if self.p1.score > self.p2.score else 'Игрок 2'} победил!"

    def draw(self):
        arcade.set_background_color((245, 245, 250))
        self._draw(self.p1, self.X1, self.Y)
        self._draw(self.p2, self.X2, self.Y)

        if self.mode == 'coop':
            Config.draw_text(f"Общий: {self.p1.score + self.p2.score}", self.CX, self.Y + self.FH + 20, (0, 0, 0), 20)
        else:
            Config.draw_text(f"P1: {self.p1.score}", self.X1 + 50, self.Y + self.FH + 10, Config.P1_COLOR, 16)
            Config.draw_text(f"P2: {self.p2.score}", self.X2 + 50, self.Y + self.FH + 10, Config.P2_COLOR, 16)

        if self.paused:
            arcade.draw_lrbt_rectangle_filled(0, self.W, 0, self.H, (0, 0, 0, 180))
            Config.draw_text("ПАУЗА", self.W // 2, self.H // 2, (255, 255, 255), 36)

        if self.show_rules:
            arcade.draw_lrbt_rectangle_filled(0, self.W, 0, self.H, (241, 241, 241, 240))
            Config.draw_text(f"ПРАВИЛА: {self.mode.upper()}", self.W // 2, self.H // 2 + 150, (40, 40, 40), 32)
            rules = ["A/D или ←/→ - движение", "W/↑ - поворот", "S/↓ - ускорение"]
            if self.mode == 'coop':
                rules.append("Линии удаляются, если собраны у обоих")
            else:
                rules.append("За линию соперник получает мусор")
            rules += ["", "ENTER - старт", "ESC - меню"]
            for i, r in enumerate(rules):
                c = (0, 100, 0) if "ENTER" in r or "ESC" in r else (60, 60, 60)
                Config.draw_text(r, self.W // 2, self.H // 2 + 100 - i * 30, c, 16)

        if self.game_over:
            arcade.draw_lrbt_rectangle_filled(0, self.W, 0, self.H, (241, 241, 241))
            Config.draw_text("GAME OVER", self.W // 2, self.H // 2 + 60, (255, 0, 0), 32)
            Config.draw_text(self.winner, self.W // 2, self.H // 2, (0, 0, 0), 24)

    def _draw(self, p, x, y):
        CELL = 32
        bg = Config.P1_BG if p.id == 1 else Config.P2_BG
        arcade.draw_lrbt_rectangle_filled(x - 5, x + 10 * CELL + 5, y - 5, y + 20 * CELL + 5, bg)
        arcade.draw_lrbt_rectangle_outline(x, x + 10 * CELL, y, y + 20 * CELL, p.color, 4)
        for r in range(21): arcade.draw_line(x, y + r * CELL, x + 10 * CELL, y + r * CELL, (230, 230, 230), 1)
        for c in range(11): arcade.draw_line(x + c * CELL, y, x + c * CELL, y + 20 * CELL, (230, 230, 230), 1)
        for r in range(20):
            for c in range(10):
                if p.arena.m[r][c]:
                    col = \
                    [(0, 0, 0), (255, 100, 100), (100, 200, 255), (100, 255, 150), (200, 100, 255), (255, 200, 100),
                     (255, 150, 100), (150, 150, 255)][p.arena.m[r][c]]
                    arcade.draw_lrbt_rectangle_filled(x + c * CELL + 1, x + (c + 1) * CELL - 1, y + (19 - r) * CELL + 1,
                                                      y + (20 - r) * CELL - 1, col)
        if p.matrix and not p.game_over:
            for r, row in enumerate(p.matrix):
                for c, v in enumerate(row):
                    if v:
                        px, py = p.pos['x'] + c, p.pos['y'] + r
                        if 0 <= px < 10 and 0 <= py < 20:
                            col = [(0, 0, 0), (255, 100, 100), (100, 200, 255), (100, 255, 150), (200, 100, 255),
                                   (255, 200, 100), (255, 150, 100), (150, 150, 255)][v]
                            arcade.draw_lrbt_rectangle_filled(x + px * CELL + 1, x + (px + 1) * CELL - 1,
                                                              y + (19 - py) * CELL + 1, y + (20 - py) * CELL - 1, col)
        # Next piece
        px = x - 110 if p.id == 1 else x + 10 * CELL + 15
        py = y + 20 * CELL - 80
        arcade.draw_lrbt_rectangle_outline(px - 5, px + 85, py - 5, py + 65, p.color, 2)
        Config.draw_text("Next:", px + 40, py + 70, p.color, 12)
        if p.next:
            for r, row in enumerate(p.next):
                for c, v in enumerate(row):
                    if v:
                        col = \
                        [(0, 0, 0), (255, 100, 100), (100, 200, 255), (100, 255, 150), (200, 100, 255), (255, 200, 100),
                         (255, 150, 100), (150, 150, 255)][v]
                        arcade.draw_lrbt_rectangle_filled(px + c * 15 + 5, px + (c + 1) * 15 - 5 + 5, py + 45 - r * 15,
                                                          py + 60 - r * 15, col)

    def toggle_pause(self):
        if not self.show_rules and not self.game_over: self.paused = not self.paused

    def start(self):
        self.show_rules = False