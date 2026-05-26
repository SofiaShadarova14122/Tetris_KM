# Tetris_KM/games/CyberCubes/game.py
import arcade
import random
from .arena import Arena
from .player import Player
from config import Config


class CyberCubesGame:
    def __init__(self, mode='versus'):
        self.mode = mode
        self.width, self.height = 1040, 950
        self.fw, self.fh = 10 * 32, 20 * 32
        self.cx = self.width // 2

        if self.mode == 'coop':
            self.x1 = self.cx - self.fw - 40
            self.x2 = self.cx + 40
            self.shared_score = 0
        else:
            self.x1 = self.cx - self.fw - 60
            self.x2 = self.cx + 60
            self.shared_score = 0

        self.y = (950 - self.fh) // 2
        self.p1 = Player(Arena(10, 20), player_id=1)
        self.p2 = Player(Arena(10, 20), player_id=2)
        self.game_over = False
        self.paused = False
        self.show_rules = True
        self.winner_text = ""
        self.p1_garbage_pending = 0
        self.p2_garbage_pending = 0

    def update(self, dt, p1_actions, p2_actions):
        if self.paused or self.game_over or self.show_rules: return

        p1_lines_before = self.p1.lines_cleared
        p2_lines_before = self.p2.lines_cleared

        self.p1.update(dt, p1_actions)
        self.p2.update(dt, p2_actions)

        if self.mode == 'coop':
            self._clear_synced_lines()
            self.shared_score = (self.p1.lines_cleared + self.p2.lines_cleared) * 10
        else:
            self._clear_versus_lines(p1_lines_before, p2_lines_before)
            self._apply_pending_garbage()

        self.p1.arena.apply_garbage()
        self.p2.arena.apply_garbage()

        if self.p1.game_over and self.p2.game_over:
            self.game_over = True
            if self.mode == 'versus':
                if self.p1.score > self.p2.score:
                    self.winner_text = "Игрок 1 победил!"
                elif self.p2.score > self.p1.score:
                    self.winner_text = "Игрок 2 победил!"
                else:
                    self.winner_text = "Ничья!"

    def _clear_synced_lines(self):
        rows_to_clear = []
        for y in range(20):
            if all(c != 0 for c in self.p1.arena.matrix[y]) and all(c != 0 for c in self.p2.arena.matrix[y]):
                rows_to_clear.append(y)
        for y in sorted(rows_to_clear, reverse=True):
            del self.p1.arena.matrix[y];
            self.p1.arena.matrix.insert(0, [0] * 10)
            del self.p2.arena.matrix[y];
            self.p2.arena.matrix.insert(0, [0] * 10)
            self.p1.lines_cleared += 1;
            self.p2.lines_cleared += 1

    def _clear_versus_lines(self, p1_before, p2_before):
        for p in [self.p1, self.p2]:
            lines = p.arena.sweep()
            if lines > 0:
                p.lines_cleared += lines;
                p.score += lines * 10
                p.drop_interval = max(0.1, 1.0 - (p.lines_cleared // 10) * 0.05)
                if p == self.p1:
                    self.p2_garbage_pending += lines
                else:
                    self.p1_garbage_pending += lines

    def _apply_pending_garbage(self):
        if self.p1_garbage_pending > 0: self.p1.arena.add_garbage(self.p1_garbage_pending); self.p1_garbage_pending = 0
        if self.p2_garbage_pending > 0: self.p2.arena.add_garbage(self.p2_garbage_pending); self.p2_garbage_pending = 0

    def draw(self):
        arcade.set_background_color((245, 245, 250))
        self._draw_player(self.p1, self.x1, self.y)
        self._draw_player(self.p2, self.x2, self.y)

        if self.mode == 'coop':
            Config.draw_text(f"Общий счет: {self.shared_score}", self.cx, self.y + self.fh + 20, (0, 0, 0), 20,
                             anchor_x="center")
        else:
            Config.draw_text(f"Игрок 1: {self.p1.score}", self.x1 + 50, self.y + self.fh + 10, Config.P1_COLOR, 16,
                             anchor_x="center")
            Config.draw_text(f"Игрок 2: {self.p2.score}", self.x2 + 50, self.y + self.fh + 10, Config.P2_COLOR, 16,
                             anchor_x="center")
            if self.p1_garbage_pending > 0: Config.draw_text(f"⚠ +{self.p1_garbage_pending}", self.x1 + 50, self.y - 20,
                                                             (255, 100, 100), 16, anchor_x="center")
            if self.p2_garbage_pending > 0: Config.draw_text(f"⚠ +{self.p2_garbage_pending}", self.x2 + 50, self.y - 20,
                                                             (255, 100, 100), 16, anchor_x="center")

        if self.paused:
            arcade.draw_lrbt_rectangle_filled(0, self.width, 0, self.height, (0, 0, 0, 180))
            Config.draw_text("ПАУЗА", self.width // 2, self.height // 2, (255, 255, 255), 36, anchor_x="center")
            Config.draw_text("P - Продолжить | ESC - Меню", self.width // 2, self.height // 2 - 50, (200, 200, 200), 18,
                             anchor_x="center")

        if self.show_rules:
            arcade.draw_lrbt_rectangle_filled(0, self.width, 0, self.height, (241, 241, 241, 240))
            mode_name = "CO-OP" if self.mode == 'coop' else "VERSUS"
            Config.draw_text(f"ПРАВИЛА: {mode_name}", self.width // 2, self.height // 2 + 150, (40, 40, 40), 32,
                             anchor_x="center")
            rules = [
                "🎮 Управление: A/D или ←/→ - движение, W/↑ - поворот, S/↓ - ускорение",
                "🤝 CO-OP: ЛИНИИ УДАЛЯЮТСЯ ТОЛЬКО ЕСЛИ СОБРАНЫ У ОБОИХ ИГРОКОВ",
                "⚔️ VERSUS: СОБИРАЙТЕ ЛИНИИ БЫСТРЕЕ! Соперник получает мусор снизу.",
                " VERSUS: Побеждает игрок с большим счетом.",
                "", "ENTER - Начать игру | ESC - Вернуться в меню выбора"
            ]
            for i, rule in enumerate(rules):
                color = (0, 100, 0) if "ENTER" in rule or "ESC" in rule else (60, 60, 60)
                Config.draw_text(rule, self.width // 2, self.height // 2 + 100 - i * 30, color, 16, anchor_x="center")

        if self.game_over:
            arcade.draw_lrbt_rectangle_filled(0, self.width, 0, self.height, (241, 241, 241))
            Config.draw_text("GAME OVER", self.width // 2, self.height // 2 + 60, (255, 0, 0), 32, anchor_x="center")
            if self.mode == 'versus':
                Config.draw_text(self.winner_text, self.width // 2, self.height // 2, (0, 0, 0), 24, anchor_x="center")
            else:
                Config.draw_text(f"Итоговый счет: {self.shared_score}", self.width // 2, self.height // 2, (0, 0, 0),
                                 24, anchor_x="center")
            Config.draw_text("Нажмите ESC для выхода в меню", self.width // 2, self.height // 2 - 50, (100, 100, 100),
                             18, anchor_x="center")

    def _draw_player(self, player, x, y):
        CELL = 32
        bg_color = (245, 245, 245)
        arcade.draw_lrbt_rectangle_filled(x - 5, x + 10 * CELL + 5, y - 5, y + 20 * CELL + 5, bg_color)
        arcade.draw_lrbt_rectangle_outline(x, x + 10 * CELL, y, y + 20 * CELL, player.border_color, 4)
        for r in range(21): arcade.draw_line(x, y + r * CELL, x + 10 * CELL, y + r * CELL, (230, 230, 230), 1)
        for c in range(11): arcade.draw_line(x + c * CELL, y, x + c * CELL, y + 20 * CELL, (230, 230, 230), 1)
        for r in range(20):
            for c in range(10):
                if player.arena.matrix[r][c]:
                    col = Config.GENERAL_COLORS[player.arena.matrix[r][c]]
                    arcade.draw_lrbt_rectangle_filled(x + c * CELL + 1, x + (c + 1) * CELL - 1, y + (19 - r) * CELL + 1,
                                                      y + (20 - r) * CELL - 1, col)
        if player.matrix and not player.game_over:
            for r, row in enumerate(player.matrix):
                for c, v in enumerate(row):
                    if v:
                        px, py = player.pos['x'] + c, player.pos['y'] + r
                        if 0 <= px < 10 and 0 <= py < 20:
                            col = Config.GENERAL_COLORS[v]
                            arcade.draw_lrbt_rectangle_filled(x + px * CELL + 1, x + (px + 1) * CELL - 1,
                                                              y + (19 - py) * CELL + 1, y + (20 - py) * CELL - 1, col)
        if player.player_id == 1:
            prev_x = x - 110
        else:
            prev_x = x + 10 * CELL + 15
        prev_y = y + 20 * CELL - 80
        color = Config.P1_COLOR if player.player_id == 1 else Config.P2_COLOR
        arcade.draw_lrbt_rectangle_outline(prev_x - 5, prev_x + 85, prev_y - 5, prev_y + 65, color, 2)
        Config.draw_text("Next:", prev_x + 40, prev_y + 70, color, 12, anchor_x="center")
        if player.next_piece:
            for r, row in enumerate(player.next_piece):
                for c, v in enumerate(row):
                    if v: arcade.draw_lrbt_rectangle_filled(prev_x + c * 15 + 5, prev_x + (c + 1) * 15 - 5 + 5,
                                                            prev_y + 45 - r * 15, prev_y + 60 - r * 15,
                                                            Config.GENERAL_COLORS[v])

    def toggle_pause(self):
        if not self.show_rules and not self.game_over: self.paused = not self.paused

    def start_game(self):
        self.show_rules = False