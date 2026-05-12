# Tetris_KM/games/fishing/main.py
import arcade
from .game import FishingGame

class FishingWindow(arcade.Window):
    def __init__(self, bear_client):
        super().__init__(1200, 850, "Fishing")
        self.center_window()
        self.bear_client, self.game, self.pressed_keys = bear_client, FishingGame(), set()

    def on_update(self, dt):
        if not self.game.show_game_over:
            if self.bear_client: self.game.apply_controller_actions(self.bear_client.get_actions())
            self.game.apply_keyboard_actions(self._get_kb_actions())
            self.game.update(dt)

    def _get_kb_actions(self):
        acts = []
        for k, p, a in [(arcade.key.W,1,'up'),(arcade.key.A,1,'left'),(arcade.key.S,1,'down'),(arcade.key.D,1,'right'),
                        (arcade.key.UP,2,'up'),(arcade.key.LEFT,2,'left'),(arcade.key.DOWN,2,'down'),(arcade.key.RIGHT,2,'right')]:
            if k in self.pressed_keys: acts.append((p,a))
        return acts

    def on_draw(self): self.clear(); self.game.draw()
    def on_key_press(self, key, mods):
        self.pressed_keys.add(key)
        if key == arcade.key.P: self.game.toggle_pause()
        elif key in (arcade.key.ESCAPE, arcade.key.M): arcade.close_window()
    def on_key_release(self, key, mods):
        if key in self.pressed_keys: self.pressed_keys.remove(key)

def main(bear_client=None):
    app = FishingWindow(bear_client); arcade.run()