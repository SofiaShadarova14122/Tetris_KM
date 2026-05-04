# tetris_dual/main.py
import arcade
import os
from .menu import MenuState
from .game import TetrisGame

class GameOverState:
    def __init__(self, score1, score2):
        self.score1 = score1
        self.score2 = score2

    def on_draw(self, width, height):
        arcade.draw_lrbt_rectangle_filled(0, width, 0, height, (241, 241, 241))
        arcade.draw_text("ИГРА ОКОНЧЕНА", width // 2, height // 2 + 60,
                         (40, 40, 40), 32, anchor_x="center")
        if self.score1 > self.score2:
            winner = "Игрок 1 победил!"
        elif self.score2 > self.score1:
            winner = "Игрок 2 победил!"
        else:
            winner = "Ничья!"
        arcade.draw_text(winner, width // 2, height // 2,
                         (60, 60, 60), 24, anchor_x="center")
        arcade.draw_text(f"Игрок 1: {self.score1}", width // 2, height // 2 - 40,
                         (40, 40, 40), 18, anchor_x="center")
        arcade.draw_text(f"Игрок 2: {self.score2}", width // 2, height // 2 - 70,
                         (40, 40, 40), 18, anchor_x="center")
        arcade.draw_text("Нажмите любую клавишу для возврата в меню", width // 2, height // 2 - 120,
                         (100, 100, 100), 16, anchor_x="center")

    def on_key_press(self):
        return "menu"


class TetrisApp(arcade.Window):
    def __init__(self):
        width, height = 960, 760
        super().__init__(width, height, "Парный Тетрис с КиберМишками")
        self.center_window()
        arcade.set_background_color((241, 241, 241))

        self.state = "menu"  # "menu", "game", "game_over"
        self.menu = MenuState(self.width, self.height)
        self.game_over_screen = None

        # Позиции полей
        field_width = 10 * 32
        field_height = 20 * 32
        center_x = self.width // 2
        self.x1 = center_x - field_width - 60
        self.x2 = center_x + 60
        self.y = (self.height - field_height) // 2

        self.game1 = None
        self.game2 = None
        self.paused = False
        self.key_states = {'p1_drop': False, 'p2_drop': False}

        # Музыка
        self.music = None
        music_path = "assets/music/tetris_theme.mp3"
        if os.path.exists(music_path):
            try:
                self.music = arcade.Sound(music_path, streaming=True)
                self.music.play(volume=0.5, loop=True)
            except Exception as e:
                print(f"Не удалось загрузить музыку: {e}")

    def center_window(self):
        screen_width, screen_height = arcade.get_display_size()
        window_x = (screen_width - self.width) // 2
        window_y = (screen_height - self.height) // 2
        self.set_location(window_x, window_y)

    def start_game(self):
        self.game1 = TetrisGame(self.x1, self.y)
        self.game2 = TetrisGame(self.x2, self.y)
        self.state = "game"
        self.paused = False

    def on_draw(self):
        self.clear()
        if self.state == "menu":
            self.menu.on_draw()
        elif self.state == "game":
            self.game1.draw()
            self.game2.draw()
            self.game1.draw_preview(self.x1 - 120, self.y + 50)
            self.game2.draw_preview(self.x2 + self.game2.width + 20, self.y + 50)
            # Счёт НАД полями
            arcade.draw_text(
                f"Игрок 1: {self.game1.get_score()}",
                self.x1 + self.game1.width // 2, self.y + self.game1.height + 10,
                (40, 40, 40), 16, anchor_x="center"
            )
            arcade.draw_text(
                f"Игрок 2: {self.game2.get_score()}",
                self.x2 + self.game2.width // 2, self.y + self.game2.height + 10,
                (40, 40, 40), 16, anchor_x="center"
            )
            if self.paused:
                arcade.draw_lrbt_rectangle_filled(0, self.width, 0, self.height, (0, 0, 0, 180))
                arcade.draw_text("ПАУЗА", self.width // 2, self.height // 2,
                                 (255, 255, 255), 36, anchor_x="center")
                arcade.draw_text("Нажмите P для продолжения", self.width // 2, self.height // 2 - 50,
                                 (200, 200, 200), 18, anchor_x="center")
        elif self.state == "game_over":
            self.game_over_screen.on_draw(self.width, self.height)

    def on_update(self, delta_time):
        if self.state == "game":
            self.game1.update(delta_time)
            self.game2.update(delta_time)
            if self.game1.is_game_over() and self.game2.is_game_over():
                self.game_over_screen = GameOverState(
                    self.game1.get_score(),
                    self.game2.get_score()
                )
                self.state = "game_over"

    def on_mouse_press(self, x, y, button, modifiers):
        if self.state == "menu":
            if self.menu.on_mouse_press(x, y):
                self.start_game()

    def on_key_press(self, key, modifiers):
        if self.state == "game_over":
            self.state = "menu"
            return

        if self.state != "game":
            return

        if key == arcade.key.P:
            self.paused = not self.paused
            return

        if self.paused:
            return

        # Игрок 1: стрелки
        if key == arcade.key.LEFT:
            self.game1.handle_input('left')
        elif key == arcade.key.RIGHT:
            self.game1.handle_input('right')
        elif key == arcade.key.UP:
            self.game1.handle_input('rotate')
        elif key == arcade.key.DOWN:
            self.key_states['p1_drop'] = True
            self.game1.handle_input('drop', is_key_down=True)

        # Игрок 2: WASD
        if key == arcade.key.A:
            self.game2.handle_input('left')
        elif key == arcade.key.D:
            self.game2.handle_input('right')
        elif key == arcade.key.W:
            self.game2.handle_input('rotate')
        elif key == arcade.key.S:
            self.key_states['p2_drop'] = True
            self.game2.handle_input('drop', is_key_down=True)

    def on_key_release(self, key, modifiers):
        if key == arcade.key.DOWN:
            self.key_states['p1_drop'] = False
            self.game1.handle_input('drop', is_key_down=False)
        elif key == arcade.key.S:
            self.key_states['p2_drop'] = False
            self.game2.handle_input('drop', is_key_down=False)


def main():
    app = TetrisApp()
    arcade.run()


if __name__ == "__main__":
    main()