# Tetris_KM/games/CyberCubes/game.py
import arcade
import random
from .arena import Arena
from .player import Player

COLORS = [(0, 0, 0), (255, 100, 100), (100, 200, 255), (100, 255, 150), (200, 100, 255), (255, 200, 100),
          (255, 150, 100), (150, 150, 255)]


class CyberCubesGame:
    def __init__(self):
        self.cx, self.fw, self.fh = 1040 // 2, 10 * 32, 20 * 32
        self.x1, self.x2 = self.cx - self.fw - 60, self.cx + 60
        self.y = (950 - self.fh) // 2
        self.p1 = Player(Arena(10, 20))
        self.p2 = Player(Arena(10, 20))
        self.game_over, self.paused = False, False

    def apply_controller_actions(self, actions):
        """Обработка ввода от мишек"""
        for p, act in actions:
            player = self.p1 if p == 1 else self.p2
            if act in ['left', 'right', 'down']:
                if act == 'left':
                    player.move(-1)
                elif act == 'right':
                    player.move(1)
                elif act == 'down':
                    player.drop_interval = player.DROP_FAST
            # Для мишек вращение тоже делаем однократным
            if act in ['up', 'up_left', 'up_right'] and not player.rotate_lock:
                player.rotate(1)
                player.rotate_lock = True

    def apply_keyboard_actions(self, actions):
        """Обработка движения с клавиатуры (без вращения)"""
        for g in [self.p1, self.p2]:
            g.keys_pressed = {'left': False, 'right': False, 'down': False}

        for p, act in actions:
            player = self.p1 if p == 1 else self.p2
            if act in player.keys_pressed:
                player.keys_pressed[act] = True

    def update(self, dt):
        if self.paused or self.game_over: return
        self.p1.update(dt);
        self.p2.update(dt)
        if self.p1.game_over and self.p2.game_over: self.game_over = True

    def draw(self):
        arcade.set_background_color((245, 245, 250))
        self._draw_player(self.p1, self.x1, self.y)
        self._draw_player(self.p2, self.x2, self.y)
        try:
            arcade.draw_text(f"Игрок 1: {self.p1.score}", self.x1 + self.fw // 2, self.y + self.fh + 10, (40, 40, 40),
                             16, anchor_x="center")
        except:
            pass
        try:
            arcade.draw_text(f"Игрок 2: {self.p2.score}", self.x2 + self.fw // 2, self.y + self.fh + 10, (40, 40, 40),
                             16, anchor_x="center")
        except:
            pass
        if self.paused:
            arcade.draw_lrbt_rectangle_filled(0, 1040, 0, 950, (0, 0, 0, 180))
            try:
                arcade.draw_text("ПАУЗА", 520, 475, (255, 255, 255), 36, anchor_x="center")
            except:
                pass
            try:
                arcade.draw_text("Нажмите ESC/M для выхода в меню", 520, 425, (200, 200, 200), 18, anchor_x="center")
            except:
                pass
        if self.game_over:
            arcade.draw_lrbt_rectangle_filled(0, 1040, 0, 950, (241, 241, 241))
            try:
                arcade.draw_text("ИГРА ОКОНЧЕНА", 520, 535, (40, 40, 40), 32, anchor_x="center")
            except:
                pass
            w = "Игрок 1 победил!" if self.p1.score > self.p2.score else "Игрок 2 победил!" if self.p2.score > self.p1.score else "Ничья!"
            try:
                arcade.draw_text(w, 520, 475, (60, 60, 60), 24, anchor_x="center")
            except:
                pass
            try:
                arcade.draw_text(f"1: {self.p1.score} | 2: {self.p2.score}", 520, 435, (40, 40, 40), 18,
                                 anchor_x="center")
            except:
                pass
            try:
                arcade.draw_text("Нажмите ESC", 520, 375, (100, 100, 100), 16, anchor_x="center")
            except:
                pass

    def _draw_player(self, player, x, y):
        CELL = 32
        arcade.draw_lrbt_rectangle_filled(x - 5, x + 10 * CELL + 5, y - 5, y + 20 * CELL + 5, (255, 255, 255))
        arcade.draw_lrbt_rectangle_outline(x, x + 10 * CELL, y, y + 20 * CELL, (100, 100, 100), 2)
        for r in range(21): arcade.draw_line(x, y + r * CELL, x + 10 * CELL, y + r * CELL, (230, 230, 230), 1)
        for c in range(11): arcade.draw_line(x + c * CELL, y, x + c * CELL, y + 20 * CELL, (230, 230, 230), 1)
        for r in range(20):
            for c in range(10):
                if player.arena.matrix[r][c]:
                    col = COLORS[player.arena.matrix[r][c]]
                    arcade.draw_lrbt_rectangle_filled(x + c * CELL + 1, x + (c + 1) * CELL - 1,
                                                      y + (19 - r) * CELL + 1, y + (20 - r) * CELL - 1, col)
        if player.matrix and not player.game_over:
            for r, row in enumerate(player.matrix):
                for c, v in enumerate(row):
                    if v:
                        px, py = player.pos['x'] + c, player.pos['y'] + r
                        if 0 <= px < 10 and 0 <= py < 20:
                            col = COLORS[v]
                            arcade.draw_lrbt_rectangle_filled(x + px * CELL + 1, x + (px + 1) * CELL - 1,
                                                              y + (19 - py) * CELL + 1, y + (20 - py) * CELL - 1, col)
        try:
            arcade.draw_text("След:", x + 10 * CELL + 15, y + 20 * CELL - 40, (40, 40, 40), 12)
        except:
            pass
        if player.next_piece:
            for r, row in enumerate(player.next_piece):
                for c, v in enumerate(row):
                    if v:
                        arcade.draw_lrbt_rectangle_filled(x + 10 * CELL + 20 + c * 15, x + 10 * CELL + 35 + c * 15,
                                                          y + 20 * CELL - 30 - r * 15, y + 20 * CELL - 15 - r * 15,
                                                          COLORS[v])

    def toggle_pause(self):
        self.paused = not self.paused