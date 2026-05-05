# TETRIS_KM/main.py
import arcade
import os
import importlib

GAME_FOLDER = "games"


class MainMenu(arcade.Window):
    def __init__(self):
        super().__init__(800, 600, "КиберМедведи: Выбор игры")
        arcade.set_background_color((241, 241, 241))

        # Сканируем папку games/
        self.game_folders = []
        if os.path.exists(GAME_FOLDER):
            for item in os.listdir(GAME_FOLDER):
                full_path = os.path.join(GAME_FOLDER, item)
                if os.path.isdir(full_path) and os.path.isfile(os.path.join(full_path, "main.py")):
                    self.game_folders.append(item)

        # Создаём кнопки
        total = len(self.game_folders)
        start_y = 400
        step = 70
        self.buttons = []
        for i, folder_name in enumerate(self.game_folders):
            y_pos = start_y - i * step
            display_name = folder_name.replace("_", " ").title()
            self.buttons.append({
                "label": display_name,
                "game": folder_name,
                "x": 400,
                "y": y_pos,
                "width": 300,  # фиксированная ширина кнопки
                "height": 50  # высота кнопки
            })

        if not self.buttons:
            self.buttons.append({
                "label": "Нет доступных игр",
                "game": None,
                "x": 400,
                "y": 300,
                "width": 300,
                "height": 50
            })

    def draw_tetris_piece(self, x, y, size=10):
        """Мини-фигурка Тетриса (размер 10x10), выровненная по правому краю кнопки."""
        color = (100, 200, 255)  # голубой
        offsets = [(0, 1), (-1, 0), (0, 0), (1, 0)]  # форма T
        for dx, dy in offsets:
            arcade.draw_lrbt_rectangle_filled(
                x + dx * size,
                x + (dx + 1) * size,
                y + dy * size,
                y + (dy + 1) * size,
                color
            )

    def on_draw(self):
        self.clear()
        arcade.draw_text("Выберите игру:", 400, 480, (40, 40, 40), 28, anchor_x="center")

        for btn in self.buttons:
            # Координаты кнопки
            left = btn["x"] - btn["width"] // 2
            right = btn["x"] + btn["width"] // 2
            bottom = btn["y"] - btn["height"] // 2
            top = btn["y"] + btn["height"] // 2

            # Фон кнопки
            arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, (200, 200, 255))

            # Текст по центру
            arcade.draw_text(
                btn["label"],
                btn["x"], btn["y"],
                (30, 30, 30),
                18,
                anchor_x="center",
                anchor_y="center"
            )

            # Мини-фигурка (если игра существует)
            if btn["game"]:
                # Отступ 10px от правого края, по вертикали — центр кнопки
                piece_x = right - 10 - 2 * 10  # 2*size = ширина фигурки
                piece_y = btn["y"] - 10  # центрируем по высоте (size=10 → высота=20)
                self.draw_tetris_piece(piece_x, piece_y, size=10)

    def on_mouse_press(self, x, y, button, modifiers):
        for btn in self.buttons:
            if btn["game"] is None:
                continue
            left = btn["x"] - btn["width"] // 2
            right = btn["x"] + btn["width"] // 2
            bottom = btn["y"] - btn["height"] // 2
            top = btn["y"] + btn["height"] // 2
            if left <= x <= right and bottom <= y <= top:
                self.launch_game(btn["game"])
                break

    def launch_game(self, game_name):
        try:
            game_module = importlib.import_module(f"games.{game_name}.main")
            self.close()
            game_module.main()
        except Exception as e:
            print(f"Ошибка запуска {game_name}: {e}")


def main():
    app = MainMenu()
    arcade.run()


if __name__ == "__main__":
    main()