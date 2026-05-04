# tetris_dual/game/tetris_board.py
from .tetromino import Tetromino
from ..config import BOARD_WIDTH, BOARD_HEIGHT


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
        # Создаём следующую фигуру, если её нет
        if self.next_piece is None:
            self.next_piece = Tetromino()

        # Текущая фигура = следующая
        self.current_piece = self.next_piece
        self.next_piece = Tetromino()

        # Фигура появляется НАД полем (y = -высота_фигуры)
        self.current_piece.x = BOARD_WIDTH // 2 - len(self.current_piece.shape[0]) // 2
        self.current_piece.y = -len(self.current_piece.shape)  # за пределами сверху

        # Проверяем: можно ли хотя бы частично войти?
        if not self._can_enter_field():
            self.game_over = True

    def _can_enter_field(self):
        """Проверяет, может ли фигура хотя бы частично войти в поле."""
        for px, py in self.current_piece.get_positions():
            nx, ny = px + self.current_piece.x, py + self.current_piece.y
            if nx < 0 or nx >= BOARD_WIDTH:
                continue
            if ny >= BOARD_HEIGHT:
                continue
            if ny >= 0 and self.grid[ny][nx] is not None:
                return False
        return True

    def _is_valid_position(self, piece=None, x=None, y=None):
        if piece is None:
            piece = self.current_piece
        if x is None:
            x = piece.x
        if y is None:
            y = piece.y

        for px, py in piece.get_positions():
            nx, ny = px + x, py + y
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
            if dy > 0:  # падение вниз невозможно → фиксируем
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
        for x, y in self.current_piece.get_positions():
            if y < 0:
                # Фигура зашла за верх → игра окончена
                self.game_over = True
                return
            if 0 <= y < BOARD_HEIGHT and 0 <= x < BOARD_WIDTH:
                self.grid[y][x] = self.current_piece.shape_type
        self._clear_lines()
        self._spawn_new_piece()

    def _clear_lines(self):
        lines_to_clear = []
        for y in range(BOARD_HEIGHT):
            if all(cell is not None for cell in self.grid[y]):
                lines_to_clear.append(y)

        for y in sorted(lines_to_clear):
            del self.grid[y]
            self.grid.insert(0, [None for _ in range(BOARD_WIDTH)])

        points = {1: 100, 2: 300, 3: 500, 4: 800}
        self.score += points.get(len(lines_to_clear), 0)

    def get_fall_delay(self):
        from ..config import INITIAL_FALL_DELAY, MIN_FALL_DELAY, FALL_ACCELERATION_BASE
        return max(MIN_FALL_DELAY, INITIAL_FALL_DELAY - self.score * FALL_ACCELERATION_BASE)