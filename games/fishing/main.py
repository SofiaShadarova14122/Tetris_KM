# Tetris_KM/games/fishing/main.py
import arcade
from input_manager import InputManager
from .game import FishingGame

class FishingWindow(arcade.Window):
    def __init__(self, bear_client):
        super().__init__(1200, 950, "Рыбалка")
        self.center_window()
        self.bear_client = bear_client
        self.kb = InputManager()
        self.game = FishingGame()
        self.pressed_keys = set()

    def on_update(self, dt):
        if not self.game.game_over:
            self.kb.update(self.pressed_keys)
            if self.bear_client:
                for p, act in self.bear_client.get_actions():
                    self.kb.handle_bear_input(p, act)
            # Передаем объединенные действия в игру
            self.game.update(dt, self.kb.get_player1_input(), self.kb.get_player2_input())

    def on_draw(self):
        self.clear()
        self.game.draw()

    def on_key_press(self, key, mods):
        self.pressed_keys.add(key)
        if key == arcade.key.P: self.game.toggle_pause()
        elif key in (arcade.key.ESCAPE, arcade.key.M): arcade.close_window()

    def on_key_release(self, key, mods):
        if key in self.pressed_keys: self.pressed_keys.remove(key)

# ✅ mode=None добавлен для совместимости
def main(bear_client=None, mode=None):
    app = FishingWindow(bear_client)
    arcade.run()