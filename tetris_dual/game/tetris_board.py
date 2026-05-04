import random
from .tetromino import Tetromino
from ..config import BOARD_WIDTH, BOARD_HEIGHT, INITIAL_FALL_DELAY, MIN_FALL_DELAY, FALL_ACCELERATION_BASE

class TetrisBoard:
    def __init__(self):
        self.reset()

    def reset(self):
        self.grid = [[None for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
        self.current_piece = None
        self.next_piece = None
        self.game_over = False
        self.score = 0
        self._spawn_new_piece()

    def _spawn_new_piece(self):
        if self.next_piece is None:
            self.next_piece = Tetromino()
        self.current_piece = self.next_piece
        self.next_piece = Tetromino()

        self.current_piece.x = BOARD_WIDTH // 2 - len(self.current_piece.shape[0]) // 2
        self.current_piece.y = -len(self.current_piece.shape)

        if self._collides_with_grid():
            self.game_over = True

    def _collides_with_grid(self, piece=None, offset_x=0, offset_y=0):
        if piece is None:
            piece = self.current_piece
        for px, py in piece.get_positions():
            nx = px + piece.x + offset_x
            ny = py + piece.y + offset_y
            if ny >= 0 and 0 <= nx < BOARD_WIDTH and ny < BOARD_HEIGHT:
                if self.grid[ny][nx] is not None:
                    return True
        return False

    def _is_valid_position(self, piece=None, x=None, y=None):
        if piece is None:
            piece = self.current_piece
        if x is None:
            x = piece.x
        if y is None:
            y = piece.y

        for px, py in piece.get_positions():
            nx = px + x
            ny = py + y
            if ny >= 0:
                if nx < 0 or nx >= BOARD_WIDTH or ny >= BOARD_HEIGHT:
                    return False
            if ny >= 0 and self.grid[ny][nx] is not None:
                return False
        return True

    def move(self, dx, dy):
        if self.game_over:
            return False

        new_x = self.current_piece.x + dx
        new_y = self.current_piece.y + dy

        if self._is_valid_position(x=new_x, y=new_y):
            self.current_piece.x = new_x
            self.current_piece.y = new_y
            return True
        else:
            if dy > 0:
                self._lock_piece()
            return False

    def rotate(self):
        if self.game_over:
            return
        original = self.current_piece.shape
        self.current_piece.shape = self.current_piece.rotate()
        if not self._is_valid_position():
            self.current_piece.shape = original

    def drop(self):
        if self.game_over:
            return
        while self.move(0, 1):
            self.score += 1

    def _lock_piece(self):
        any_cell_inside = False
        for x, y in self.current_piece.get_positions():
            board_x = self.current_piece.x + x
            board_y = self.current_piece.y + y
            if 0 <= board_y < BOARD_HEIGHT and 0 <= board_x < BOARD_WIDTH:
                any_cell_inside = True
                self.grid[board_y][board_x] = self.current_piece.shape_type
        if not any_cell_inside:
            self.game_over = True
            return

        self._clear_lines()
        self._spawn_new_piece()

    def _clear_lines(self):
        lines_to_clear = [y for y in range(BOARD_HEIGHT) if all(self.grid[y][col] is not None for col in range(BOARD_WIDTH))]
        for y in sorted(lines_to_clear, reverse=True):
            del self.grid[y]
            self.grid.insert(0, [None for _ in range(BOARD_WIDTH)])

        points = {1: 100, 2: 300, 3: 500, 4: 800}
        self.score += points.get(len(lines_to_clear), 0)

    def get_fall_delay(self):
        delay = INITIAL_FALL_DELAY - self.score * FALL_ACCELERATION_BASE
        return max(MIN_FALL_DELAY, delay)