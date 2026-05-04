"""
Модель игрового поля для одного игрока.
Реализует правила тетриса: спавн, движение, вращение, фиксация, очистка линий.
"""
import random
from .tetromino import Tetromino
from ..config import BOARD_WIDTH, BOARD_HEIGHT, INITIAL_FALL_DELAY, MIN_FALL_DELAY, FALL_ACCELERATION_BASE
from ..sounds import play_drop, play_rotate, play_line_clear

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

    # ---------- Спавн ----------
    def _spawn_new_piece(self):
        if self.next_piece is None:
            self.next_piece = Tetromino()
        self.current_piece = self.next_piece
        self.next_piece = Tetromino()

        # Фигура появляется ЦЕНТРИРОВАННО НАД ПОЛЕМ
        self.current_piece.x = BOARD_WIDTH // 2 - len(self.current_piece.shape[0]) // 2
        self.current_piece.y = -len(self.current_piece.shape)  # полностью над полем

        # Проверяем: может ли фигура хотя бы частично войти в поле?
        if not self._can_enter_field():
            self.game_over = True

    def _can_enter_field(self):
        """Проверяет, может ли фигура войти в поле (даже частично)."""
        for px, py in self.current_piece.get_positions():
            nx = self.current_piece.x + px
            ny = self.current_piece.y + py
            # Клетки вне поля по X — недопустимы даже над полем
            if nx < 0 or nx >= BOARD_WIDTH:
                return False
            # Клетки внутри поля по Y — проверяем на занятость
            if 0 <= ny < BOARD_HEIGHT:
                if self.grid[ny][nx] is not None:
                    return False
        return True

    # ---------- Проверка позиции ----------
    def _is_valid_position(self, piece=None, x=None, y=None):
        """Проверяет, допустима ли позиция фигуры."""
        if piece is None:
            piece = self.current_piece
        if x is None:
            x = piece.x
        if y is None:
            y = piece.y

        for px, py in piece.get_positions():
            nx = x + px
            ny = y + py

            # Выход за боковые границы — всегда запрещён
            if nx < 0 or nx >= BOARD_WIDTH:
                return False

            # Выход за нижнюю границу — запрещён
            if ny >= BOARD_HEIGHT:
                return False

            # Клетки внутри поля не должны пересекаться с занятыми
            if ny >= 0 and self.grid[ny][nx] is not None:
                return False

        return True

    # ---------- Движение ----------
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
            # Если движение ВНИЗ невозможно — фиксируем фигуру
            if dy > 0:
                self._lock_piece()
            return False

    def rotate(self):
        if self.game_over:
            return
        original_shape = self.current_piece.shape
        self.current_piece.shape = self.current_piece.rotate()
        if not self._is_valid_position():
            self.current_piece.shape = original_shape
        else:
            play_rotate()

    def drop(self):
        if self.game_over:
            return
        while self.move(0, 1):
            self.score += 1  # бонус за ускоренное падение
        play_drop()

    # ---------- Фиксация фигуры ----------
    def _lock_piece(self):
        """Фиксирует текущую фигуру в сетке."""
        any_in_field = False
        for px, py in self.current_piece.get_positions():
            nx = self.current_piece.x + px
            ny = self.current_piece.y + py

            # Игнорируем клетки, которые остались над полем
            if ny < 0:
                continue

            # Все клетки внутри поля — фиксируем
            if 0 <= ny < BOARD_HEIGHT and 0 <= nx < BOARD_WIDTH:
                any_in_field = True
                self.grid[ny][nx] = self.current_piece.shape_type

        # Если фигура вообще не вошла в поле — игра окончена
        if not any_in_field:
            self.game_over = True
            return

        # Начисляем базовые очки за фиксацию
        self.score += 4

        # Очищаем линии
        lines_cleared = self._clear_lines()
        if lines_cleared > 0:
            # Классическая система очков
            points = {1: 100, 2: 300, 3: 500, 4: 800}
            self.score += points.get(lines_cleared, 0)
            play_line_clear()

        # Спавним следующую фигуру
        self._spawn_new_piece()

    def _clear_lines(self):
        """Удаляет заполненные строки и возвращает их количество."""
        lines_to_clear = []
        for y in range(BOARD_HEIGHT):
            if all(cell is not None for cell in self.grid[y]):
                lines_to_clear.append(y)

        # Удаляем строки снизу вверх
        for y in sorted(lines_to_clear, reverse=True):
            del self.grid[y]
            # Вставляем новую пустую строку сверху
            self.grid.insert(0, [None for _ in range(BOARD_WIDTH)])

        return len(lines_to_clear)

    def get_fall_delay(self):
        delay = INITIAL_FALL_DELAY - self.score * FALL_ACCELERATION_BASE
        return max(MIN_FALL_DELAY, delay)