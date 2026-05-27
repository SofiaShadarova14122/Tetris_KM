# Tetris_KM/games/Fishing/main.py
import arcade
from input_manager import InputManager
from .game import FishingGame

class FishingWindow(arcade.Window):
    def __init__(self, bear_client):
        super().__init__(1200, 950, "Рыбалка")
        self.center_window()
        self.bear_client = bear_client
        self.kb = InputManager()
        self.kb.clear()
        if self.bear_client: self.bear_client.clear_queue()
        self.game = FishingGame()
        self.pressed_keys = set()

    def on_update(self, dt):
        if not self.game.game_over:
            self.kb.update(self.pressed_keys)
            if self.bear_client:
                for p, act in self.bear_client.get_actions():
                    self.kb.handle_bear_input(p, act)
            self.game.update(dt, self.kb.get_player1_input(), self.kb.get_player2_input())

    def on_draw(self):
        self.clear()
        self.game.draw()

    def on_key_press(self, key, mods):
        self.pressed_keys.add(key)
        if key == arcade.key.P:
            self.game.toggle_pause()
        elif key == arcade.key.ENTER and self.game.show_rules:
            self.game.start_game()
        # ✅ ESC/M всегда возвращает в главное меню (из правил, паузы или game over)
        elif key in (arcade.key.ESCAPE, arcade.key.M):
            arcade.close_window()

    def on_key_release(self, key, mods):
        if key in self.pressed_keys:
            self.pressed_keys.remove(key)

def main(bear_client=None, mode=None):
    app = FishingWindow(bear_client)
    arcade.run()