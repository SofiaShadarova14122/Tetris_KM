# Tetris_KM/games/CyberCubes/main.py
import arcade
from input_manager import InputManager
from .game import CyberCubesGame

class CubesWindow(arcade.Window):
    def __init__(self, bear, mode='versus'):
        super().__init__(1040, 950, f"CyberCubes: {mode.upper()}")
        self.center_window()
        self.bear = bear
        self.kb = InputManager()
        self.kb.clear()
        if self.bear: self.bear.clear_queue()
        self.game = CyberCubesGame(mode=mode)
        self.keys = set()

    def on_update(self, dt):
        if self.game.game_over: return
        self.kb.update(self.keys)
        if self.bear:
            for p,a in self.bear.get_actions(): self.kb.handle_bear(p,a)
        self.game.update(dt, self.kb.get_p1(), self.kb.get_p2())

    def on_draw(self): self.clear(); self.game.draw()

    def on_key_press(self, k, m):
        self.keys.add(k)
        if k==arcade.key.P: self.game.toggle_pause()
        elif k==arcade.key.ENTER and self.game.show_rules: self.game.start()
        elif k in (arcade.key.ESCAPE, arcade.key.M): arcade.close_window()

    def on_key_release(self, k, m):
        if k in self.keys: self.keys.remove(k)

def main(bear=None, mode='versus'):
    app = CubesWindow(bear, mode=mode)
    arcade.run()