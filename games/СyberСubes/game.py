# Tetris_KM/games/CyberCubes/game.py
import arcade
import random

COLORS = [(0, 0, 0), (255, 100, 100), (100, 200, 255), (100, 255, 150), (200, 100, 255), (255, 200, 100),
          (255, 150, 100), (150, 150, 255)]
SHAPES = [[[0, 0, 0], [1, 1, 1], [0, 1, 0]], [[1, 1], [1, 1]], [[0, 1, 0], [0, 1, 0], [0, 1, 1]],
          [[0, 1, 0], [0, 1, 0], [1, 1, 0]], [[0, 1, 0, 0], [0, 1, 0, 0], [0, 1, 0, 0], [0, 1, 0, 0]],
          [[0, 1, 1], [1, 1, 0], [0, 0, 0]], [[1, 1, 0], [0, 1, 1], [0, 0, 0]]]


class TetrisGrid:
    def __init__(self, x, y):
        self.x, self.y, self.W, self.H, self.CELL = x, y, 10, 20, 32
        self.grid = [[0] * self.W for _ in range(self.H)]
        self.score, self.lines, self.game_over = 0, 0, False
        self.drop_interval, self.drop_timer = 0.8, 0.0
        self.move_timer_l, self.move_timer_r = 0.0, 0.0
        self.keys = {'left': False, 'right': False, 'down': False}
        self.piece, self.piece_color, self.px, self.py = None, 1, 0, 0
        self.next_piece, self.next_color = random.choice(SHAPES), random.randint(1, 7)
        self.spawn_piece()
        self.was_rotate_pressed = False

    def spawn_piece(self):
        self.piece, self.piece_color = self.next_piece, self.next_color
        self.next_piece, self.next_color = random.choice(SHAPES), random.randint(1, 7)
        self.px, self.py = self.W // 2 - len(self.piece[0]) // 2, 0
        if self.collides(0, 0): self.game_over = True

    def collides(self, dx, dy):
        for r, row in enumerate(self.piece):
            for c, v in enumerate(row):
                if v:
                    nx, ny = self.px + c + dx, self.py + r + dy
                    if nx < 0 or nx >= self.W or ny >= self.H: return True
                    if ny >= 0 and self.grid[ny][nx]: return True
        return False

    def rotate(self):
        if self.game_over: return
        old = [r[:] for r in self.piece]
        self.piece = [list(x) for x in zip(*self.piece[::-1])]
        if self.collides(0, 0): self.piece = old

    def move(self, dx):
        if self.game_over: return
        if not self.collides(dx, 0): self.px += dx

    def update(self, dt):
        if self.game_over: return
        if self.keys['left']:
            self.move_timer_l += dt
            if self.move_timer_l > 0.15: self.move(-1); self.move_timer_l = 0.06
        if self.keys['right']:
            self.move_timer_r += dt
            if self.move_timer_r > 0.15: self.move(1); self.move_timer_r = 0.06

        interval = 0.05 if self.keys['down'] else self.drop_interval
        self.drop_timer += dt
        if self.drop_timer >= interval:
            self.drop_timer = 0
            if not self.collides(0, 1):
                self.py += 1
            else:
                self.lock()
                self.clear_lines()
                self.spawn_piece()
                self.drop_interval = max(0.05, 0.8 - (self.lines // 10) * 0.07)

    def lock(self):
        for r, row in enumerate(self.piece):
            for c, v in enumerate(row):
                if v:
                    ny, nx = self.py + r, self.px + c
                    if 0 <= ny < self.H and 0 <= nx < self.W: self.grid[ny][nx] = self.piece_color
        cleared = 0
        self.grid = [row for row in self.grid if any(v == 0 for v in row)]
        cleared = self.H - len(self.grid)
        self.grid = [[0] * self.W for _ in range(cleared)] + self.grid
        self.lines += cleared
        self.score += cleared * 10

    def clear_lines(self):
        pass

    def draw(self):
        arcade.draw_lrbt_rectangle_filled(self.x - 5, self.x + self.W * self.CELL + 5, self.y - 5,
                                          self.y + self.H * self.CELL + 5, (250, 250, 250))
        arcade.draw_lrbt_rectangle_outline(self.x, self.x + self.W * self.CELL, self.y, self.y + self.H * self.CELL,
                                           (100, 100, 100), 2)
        for r in range(self.H + 1): arcade.draw_line(self.x, self.y + r * self.CELL, self.x + self.W * self.CELL,
                                                     self.y + r * self.CELL, (230, 230, 230), 1)
        for c in range(self.W + 1): arcade.draw_line(self.x + c * self.CELL, self.y, self.x + c * self.CELL,
                                                     self.y + self.H * self.CELL, (230, 230, 230), 1)

        for r in range(self.H):
            for c in range(self.W):
                if self.grid[r][c]:
                    col = COLORS[self.grid[r][c]]
                    arcade.draw_lrbt_rectangle_filled(self.x + c * self.CELL + 1, self.x + (c + 1) * self.CELL - 1,
                                                      self.y + (self.H - 1 - r) * self.CELL + 1,
                                                      self.y + (self.H - r) * self.CELL - 1, col)
        if self.piece and not self.game_over:
            for r, row in enumerate(self.piece):
                for c, v in enumerate(row):
                    if v:
                        px, py = self.px + c, self.py + r
                        if 0 <= px < self.W and 0 <= py < self.H:
                            col = COLORS[self.piece_color]
                            arcade.draw_lrbt_rectangle_filled(self.x + px * self.CELL + 1,
                                                              self.x + (px + 1) * self.CELL - 1,
                                                              self.y + (self.H - 1 - py) * self.CELL + 1,
                                                              self.y + (self.H - py) * self.CELL - 1, col)

        arcade.draw_text("След:", self.x + self.W * self.CELL + 15, self.y + self.H * self.CELL - 40, (40, 40, 40), 12)
        for r, row in enumerate(self.next_piece):
            for c, v in enumerate(row):
                if v: arcade.draw_lrbt_rectangle_filled(self.x + self.W * self.CELL + 20 + c * 15,
                                                        self.x + self.W * self.CELL + 35 + c * 15,
                                                        self.y + self.H * self.CELL - 30 - r * 15,
                                                        self.y + self.H * self.CELL - 15 - r * 15,
                                                        COLORS[self.next_color])


class CyberCubesGame:
    def __init__(self):
        self.cx, self.fw, self.fh = 1040 // 2, 10 * 32, 20 * 32
        self.x1, self.x2 = self.cx - self.fw - 60, self.cx + 60
        self.y = (950 - self.fh) // 2
        self.p1, self.p2 = TetrisGrid(self.x1, self.y), TetrisGrid(self.x2, self.y)
        self.game_over, self.paused = False, False

    def apply_controller_actions(self, actions):
        # НЕ сбрасываем действия! Мишка сам отправляет 0 при отпускании
        for p, act in actions:
            grid = self.p1 if p == 1 else self.p2
            if act is None:
                # Сброс всех действий (пришел байт 0)
                grid.keys = {'left': False, 'right': False, 'down': False}
                grid.was_rotate_pressed = False
            elif act == 'rotate':
                if not grid.was_rotate_pressed:
                    grid.rotate()
                    grid.was_rotate_pressed = True
            elif act == 'left':
                grid.keys['left'] = True
            elif act == 'right':
                grid.keys['right'] = True
            elif act == 'down':
                grid.keys['down'] = True
            # up_left и up_right игнорируем в тетрисе

    def apply_keyboard_actions(self, actions):
        for g in [self.p1, self.p2]:
            g.keys = {'left': False, 'right': False, 'down': False}
            g.was_rotate_pressed = False

        for p, act in actions:
            grid = self.p1 if p == 1 else self.p2
            if act == 'rotate':
                if not grid.was_rotate_pressed:
                    grid.rotate()
                    grid.was_rotate_pressed = True
            elif act in grid.keys:
                grid.keys[act] = True

    def update(self, dt):
        if self.paused or self.game_over: return
        self.p1.update(dt);
        self.p2.update(dt)
        if self.p1.game_over and self.p2.game_over: self.game_over = True

    def draw(self):
        arcade.set_background_color((245, 245, 250))
        self.p1.draw();
        self.p2.draw()
        arcade.draw_text(f"Игрок 1: {self.p1.score}", self.x1 + self.fw // 2, self.y + self.fh + 10, (40, 40, 40), 16,
                         anchor_x="center")
        arcade.draw_text(f"Игрок 2: {self.p2.score}", self.x2 + self.fw // 2, self.y + self.fh + 10, (40, 40, 40), 16,
                         anchor_x="center")
        if self.paused:
            arcade.draw_lrbt_rectangle_filled(0, 1040, 0, 950, (0, 0, 0, 180))
            arcade.draw_text("ПАУЗА", 520, 475, (255, 255, 255), 36, anchor_x="center")
            arcade.draw_text("Нажмите ESC/M для выхода в меню", 520, 425, (200, 200, 200), 18, anchor_x="center")
        if self.game_over:
            arcade.draw_lrbt_rectangle_filled(0, 1040, 0, 950, (241, 241, 241))
            arcade.draw_text("ИГРА ОКОНЧЕНА", 520, 535, (40, 40, 40), 32, anchor_x="center")
            w = "Игрок 1 победил!" if self.p1.score > self.p2.score else "Игрок 2 победил!" if self.p2.score > self.p1.score else "Ничья!"
            arcade.draw_text(w, 520, 475, (60, 60, 60), 24, anchor_x="center")
            arcade.draw_text(f"1: {self.p1.score} | 2: {self.p2.score}", 520, 435, (40, 40, 40), 18, anchor_x="center")
            arcade.draw_text("Нажмите ESC", 520, 375, (100, 100, 100), 16, anchor_x="center")

    def toggle_pause(self):
        self.paused = not self.paused