import arcade
from .base_state import GameState
from ..game.tetris_board import TetrisBoard
from ..ui.rendering import draw_board, draw_next_piece_preview, draw_scores_under_boards, draw_controls_bottom
from ..config import BOARD_WIDTH, BOARD_HEIGHT, CELL_SIZE

class GameplayState(GameState):
    def __init__(self, music_player=None):
        self.board1 = TetrisBoard()
        self.board2 = TetrisBoard()
        self.fall_timer1 = 0
        self.fall_timer2 = 0
        self.game_over = False
        self.winner = None
        self.music_player = music_player  # объект музыки (для настроек)

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

        x_left = 50
        y_board = (window.height - board_h) // 2
        draw_board(self.board1, x_left, y_board)

        x_right = window.width - 50 - board_w
        draw_board(self.board2, x_right, y_board)

        preview_y = y_board + board_h + 25
        draw_next_piece_preview(self.board1, x_left + board_w // 2, preview_y, dim=True)
        draw_next_piece_preview(self.board2, x_right + board_w // 2, preview_y, dim=True)

        draw_scores_under_boards(self.board1.score, self.board2.score,
                                 x_left + board_w // 2, y_board - 20,
                                 x_right + board_w // 2, y_board - 20)

        draw_controls_bottom(window.width, window.height)

        if self.board1.game_over:
            arcade.draw_text("GAME OVER", x_left + board_w // 2, y_board + board_h + 60,
                             (255, 100, 100), 16, anchor_x="center")
        if self.board2.game_over:
            arcade.draw_text("GAME OVER", x_right + board_w // 2, y_board + board_h + 60,
                             (255, 100, 100), 16, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if self.game_over:
            return self

        # Пауза по Пробелу или ESC
        if key in (arcade.key.SPACE, arcade.key.ESCAPE):
            from .pause_state import PauseState
            return PauseState(self, self.music_player)

        # Игрок 1
        if key == arcade.key.A:
            self.board1.move(-1, 0)
        elif key == arcade.key.D:
            self.board1.move(1, 0)
        elif key == arcade.key.W:
            self.board1.rotate()
        elif key == arcade.key.S:
            self.board1.drop()

        # Игрок 2
        if key == arcade.key.LEFT:
            self.board2.move(-1, 0)
        elif key == arcade.key.RIGHT:
            self.board2.move(1, 0)
        elif key == arcade.key.UP:
            self.board2.rotate()
        elif key == arcade.key.DOWN:
            self.board2.drop()

        return self