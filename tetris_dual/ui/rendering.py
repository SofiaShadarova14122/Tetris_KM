# tetris_dual/ui/rendering.py
import arcade
from ..config import BOARD_WIDTH, BOARD_HEIGHT, CELL_SIZE  # ← добавлен импорт
from .theme import TEXT_COLOR, SHAPE_COLORS, GRID_LINE_COLOR


def draw_board(board, x, y):
    # Сетка
    for row in range(BOARD_HEIGHT + 1):
        arcade.draw_line(x, y + row * CELL_SIZE,
                         x + BOARD_WIDTH * CELL_SIZE, y + row * CELL_SIZE,
                         GRID_LINE_COLOR, 1)
    for col in range(BOARD_WIDTH + 1):
        arcade.draw_line(x + col * CELL_SIZE, y,
                         x + col * CELL_SIZE, y + BOARD_HEIGHT * CELL_SIZE,
                         GRID_LINE_COLOR, 1)

    # Заполненные клетки
    for row_idx in range(BOARD_HEIGHT):
        for col_idx in range(BOARD_WIDTH):
            cell = board.grid[row_idx][col_idx]
            if cell is not None:
                color = SHAPE_COLORS.get(cell, (200, 200, 200))
                left = x + col_idx * CELL_SIZE + 1
                right = left + CELL_SIZE - 2
                bottom = y + (BOARD_HEIGHT - 1 - row_idx) * CELL_SIZE + 1
                top = bottom + CELL_SIZE - 2
                arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, color)

    # Текущая фигура
    if not board.game_over:
        for px, py in board.current_piece.get_positions():
            if 0 <= px < BOARD_WIDTH and 0 <= py < BOARD_HEIGHT:
                color = SHAPE_COLORS.get(board.current_piece.shape_type, (200, 200, 200))
                left = x + px * CELL_SIZE + 1
                right = left + CELL_SIZE - 2
                bottom = y + (BOARD_HEIGHT - 1 - py) * CELL_SIZE + 1
                top = bottom + CELL_SIZE - 2
                arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, color)


def draw_next_piece_preview(board, x, y):
    """Отрисовка следующей фигуры (превью)."""
    if board.next_piece is None:
        return
    arcade.draw_text("Следующая:", x, y + 80, TEXT_COLOR, 16)
    preview_y = y
    shape = board.next_piece.shape
    for row_idx, row in enumerate(shape):
        for col_idx, cell in enumerate(row):
            if cell:
                color = SHAPE_COLORS.get(board.next_piece.shape_type, (200, 200, 200))
                left = x + col_idx * (CELL_SIZE // 2) + 1
                right = left + (CELL_SIZE // 2) - 2
                bottom = preview_y + (len(shape) - 1 - row_idx) * (CELL_SIZE // 2) + 1
                top = bottom + (CELL_SIZE // 2) - 2
                arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, color)


def draw_scores(score1, score2, screen_height):
    arcade.draw_text(f"Игрок 1: {score1}", 50, screen_height - 50, TEXT_COLOR, 20)
    arcade.draw_text(f"Игрок 2: {score2}", 50, screen_height - 80, TEXT_COLOR, 20)


def draw_controls(screen_width, screen_height):
    arcade.draw_text("Управление:", screen_width - 250, screen_height - 30, TEXT_COLOR, 16)
    arcade.draw_text("Игрок 1: A/D — влево/вправо, W — поворот, S — ускорение", screen_width - 250, screen_height - 60, TEXT_COLOR, 14)
    arcade.draw_text("Игрок 2: ←/→ — влево/вправо, ↑ — поворот, ↓ — ускорение", screen_width - 250, screen_height - 80, TEXT_COLOR, 14)


def draw_game_over(winner, score1, score2, screen_width, screen_height):
    arcade.draw_text("ИГРА ОКОНЧЕНА", screen_width // 2, screen_height // 2 + 50,
                     TEXT_COLOR, 36, anchor_x="center")
    winner_text = "Игрок 1 победил!" if winner == 1 else "Игрок 2 победил!" if winner == 2 else "Ничья!"
    arcade.draw_text(winner_text, screen_width // 2, screen_height // 2,
                     TEXT_COLOR, 28, anchor_x="center")
    arcade.draw_text(f"Счёт: {score1} – {score2}", screen_width // 2, screen_height // 2 - 40,
                     TEXT_COLOR, 24, anchor_x="center")
    arcade.draw_text("Нажмите любую кнопку для возврата в меню", screen_width // 2, screen_height // 2 - 80,
                     TEXT_COLOR, 20, anchor_x="center")