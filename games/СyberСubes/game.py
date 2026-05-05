# game.py
import arcade
import os
from .arena import Arena
from .player import Player

class TetrisGame:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.cell_size = 32
        self.arena_width = 10
        self.arena_height = 20
        self.width = self.arena_width * self.cell_size
        self.height = self.arena_height * self.cell_size

        self.arena = Arena(self.arena_width, self.arena_height)
        self.player = Player(self.arena)

        self.colors = [
            (0, 0, 0),
            (255, 100, 100),
            (100, 200, 255),
            (100, 255, 150),
            (200, 100, 255),
            (255, 200, 100),
            (255, 150, 100),
            (150, 150, 255),
        ]

        self.sounds = {}
        sound_files = {
            'drop': 'assets/sounds/drop.wav',
            'rotate': 'assets/sounds/rotate.wav',
            'line_clear': 'assets/sounds/line_clear.wav'
        }
        for name, path in sound_files.items():
            if os.path.exists(path):
                try:
                    self.sounds[name] = arcade.load_sound(path)
                except:
                    pass

    def play_sound(self, name):
        if name in self.sounds:
            arcade.play_sound(self.sounds[name])

    def draw(self):
        arcade.draw_lrbt_rectangle_filled(
            self.x - 5, self.x + self.width + 5,
            self.y - 5, self.y + self.height + 5,
            (255, 255, 255)
        )
        arcade.draw_lrbt_rectangle_outline(
            self.x, self.x + self.width,
            self.y, self.y + self.height,
            (100, 100, 100), 2
        )
        for i in range(self.arena_width + 1):
            arcade.draw_line(self.x + i * self.cell_size, self.y,
                             self.x + i * self.cell_size, self.y + self.height,
                             (220, 220, 220), 1)
        for i in range(self.arena_height + 1):
            arcade.draw_line(self.x, self.y + i * self.cell_size,
                             self.x + self.width, self.y + i * self.cell_size,
                             (220, 220, 220), 1)

        for y in range(self.arena_height):
            for x in range(self.arena_width):
                val = self.arena.matrix[y][x]
                if val != 0:
                    color = self.colors[val]
                    arcade.draw_lrbt_rectangle_filled(
                        self.x + x * self.cell_size + 1,
                        self.x + (x + 1) * self.cell_size - 1,
                        self.y + (self.arena_height - 1 - y) * self.cell_size + 1,
                        self.y + (self.arena_height - y) * self.cell_size - 1,
                        color
                    )

        if self.player.matrix and not self.player.game_over:
            for y, row in enumerate(self.player.matrix):
                for x, val in enumerate(row):
                    if val != 0:
                        px = self.player.pos['x'] + x
                        py = self.player.pos['y'] + y
                        if 0 <= px < self.arena_width and 0 <= py < self.arena_height:
                            color = self.colors[val]
                            arcade.draw_lrbt_rectangle_filled(
                                self.x + px * self.cell_size + 1,
                                self.x + (px + 1) * self.cell_size - 1,
                                self.y + (self.arena_height - 1 - py) * self.cell_size + 1,
                                self.y + (self.arena_height - py) * self.cell_size - 1,
                                color
                            )

    def draw_preview(self, x, y):
        """Стандартное превью (для левого игрока)."""
        arcade.draw_text("Следующая:", x, y + 70, (40, 40, 40), 14)
        next_piece = self.player.next_piece
        preview_y = y
        for y_off, row in enumerate(next_piece):
            for x_off, val in enumerate(row):
                if val != 0:
                    color = self.colors[val]
                    arcade.draw_lrbt_rectangle_filled(
                        x + x_off * 20 + 1,
                        x + (x_off + 1) * 20 - 1,
                        preview_y + (len(next_piece) - 1 - y_off) * 20 + 1,
                        preview_y + (len(next_piece) - y_off) * 20 - 1,
                        color
                    )

    def draw_preview_with_offset(self, x, y, text_offset=0):
        """Превью с отдельным сдвигом текста (для правого игрока)."""
        arcade.draw_text("Следующая:", x + text_offset, y + 70, (40, 40, 40), 14)
        next_piece = self.player.next_piece
        preview_y = y  # ← фигура остаётся на месте!
        for y_off, row in enumerate(next_piece):
            for x_off, val in enumerate(row):
                if val != 0:
                    color = self.colors[val]
                    arcade.draw_lrbt_rectangle_filled(
                        x + x_off * 20 + 1,
                        x + (x_off + 1) * 20 - 1,
                        preview_y + (len(next_piece) - 1 - y_off) * 20 + 1,
                        preview_y + (len(next_piece) - y_off) * 20 - 1,
                        color
                    )

    def update(self, delta_time):
        self.player.update(delta_time)

    def get_score(self):
        return self.player.score

    def is_game_over(self):
        return self.player.game_over

    def handle_input(self, action, is_key_down=True):
        if self.player.game_over:
            return
        if action == 'left':
            self.player.move(-1)
        elif action == 'right':
            self.player.move(1)
        elif action == 'rotate':
            self.player.rotate(1)
            self.play_sound('rotate')
        elif action == 'drop':
            if is_key_down:
                self.player.drop_interval = self.player.DROP_FAST
            else:
                self.player.drop_interval = self.player.normal_drop_interval