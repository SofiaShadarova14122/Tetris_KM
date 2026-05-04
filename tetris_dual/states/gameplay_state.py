# tetris_dual/states/gameplay_state.py
import arcade
import os
from .base_state import GameState
from ..game.tetris_board import TetrisBoard
from ..ui.rendering import draw_board, draw_next_piece_preview, draw_scores, draw_controls
from ..config import BOARD_WIDTH, BOARD_HEIGHT, CELL_SIZE  # ← ДОБАВЛЕН ИМПОРТ


class GameplayState(GameState):
    def __init__(self):
        self.board1 = TetrisBoard()
        self.board2 = TetrisBoard()
        self.fall_timer1 = 0
        self.fall_timer2 = 0
        self.game_over = False
        self.winner = None
        self.music_player = None

        # Звуки (опционально)
        sound_dir = os.path.join("assets", "sounds")
        self.rotate_sound = self._load_sound(sound_dir, "rotate.wav")
        self.drop_sound = self._load_sound(sound_dir, "drop.wav")

        # Музыка (опционально)
        music_path = os.path.join("assets", "music", "tetris_theme.mp3")
        if os.path.exists(music_path):
            try:
                self.music = arcade.Sound(music_path, streaming=True)
                self.music_player = self.music.play(volume=0.3, loop=True)
            except Exception as e:
                print(f"[Музыка] Ошибка: {e}")

    def _load_sound(self, dir_path, filename):
        path = os.path.join(dir_path, filename)
        if os.path.exists(path):
            return arcade.load_sound(path)
        return None

    def on_update(self, delta_time):
        if self.game_over:
            return self

        if not self.board1.game_over:
            self.fall_timer1 += delta_time
            if self.fall_timer1 >= self.board1.get_fall_delay():
                self.fall_timer1 = 0
                self.board1.move(0, 1)

        if not self.board2.game_over:
            self.fall_timer2 += delta_time
            if self.fall_timer2 >= self.board2.get_fall_delay():
                self.fall_timer2 = 0
                self.board2.move(0, 1)

        if self.board1.game_over and self.board2.game_over:
            self._determine_winner()
            self.game_over = True
            if self.music_player:
                self.music_player.pause()
            from .game_over_state import GameOverState
            return GameOverState(self.winner, self.board1.score, self.board2.score)

        return self

    def _determine_winner(self):
        if self.board1.score > self.board2.score:
            self.winner = 1
        elif self.board2.score > self.board1.score:
            self.winner = 2
        else:
            self.winner = 0

    def on_draw(self, window):
        window.clear()
        board_w = BOARD_WIDTH * CELL_SIZE
        board_h = BOARD_HEIGHT * CELL_SIZE

        # Левое поле (Игрок 1)
        x1 = 50
        y1 = (window.height - board_h) // 2
        draw_board(self.board1, x1, y1)
        draw_next_piece_preview(self.board1, x1, y1 - 100)

        # Правое поле (Игрок 2)
        x2 = window.width - 50 - board_w
        y2 = (window.height - board_h) // 2
        draw_board(self.board2, x2, y2)
        draw_next_piece_preview(self.board2, x2, y2 - 100)

        draw_scores(self.board1.score, self.board2.score, window.height)
        draw_controls(window.width, window.height)

    def on_key_press(self, key, modifiers):
        if self.game_over:
            return self

        # Игрок 1
        if key == arcade.key.A:
            self.board1.move(-1, 0)
        elif key == arcade.key.D:
            self.board1.move(1, 0)
        elif key == arcade.key.W:
            self.board1.rotate()
            if self.rotate_sound:
                arcade.play_sound(self.rotate_sound)
        elif key == arcade.key.S:
            self.board1.drop()
            if self.drop_sound:
                arcade.play_sound(self.drop_sound)

        # Игрок 2
        if key == arcade.key.LEFT:
            self.board2.move(-1, 0)
        elif key == arcade.key.RIGHT:
            self.board2.move(1, 0)
        elif key == arcade.key.UP:
            self.board2.rotate()
            if self.rotate_sound:
                arcade.play_sound(self.rotate_sound)
        elif key == arcade.key.DOWN:
            self.board2.drop()
            if self.drop_sound:
                arcade.play_sound(self.drop_sound)

        return self