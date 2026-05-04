import arcade
import os
from .states.menu_pause_settings import MenuState
from .config import SCREEN_WIDTH, SCREEN_HEIGHT, TITLE, MUSIC_VOLUME, MUSIC_PATH

class TetrisGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, TITLE)
        arcade.set_background_color((20,20,30))
        self.music = None
        if os.path.exists(MUSIC_PATH):
            self.music = arcade.Sound(MUSIC_PATH, streaming=True)
            self.music.play(volume=MUSIC_VOLUME, loop=True)
        else:
            print(f"Файл {MUSIC_PATH} не найден")
        self.current_state = MenuState(self.music)

    def on_draw(self):
        self.current_state.on_draw(self)

    def on_update(self, delta_time):
        new_state = self.current_state.on_update(delta_time)
        if new_state:
            self.current_state = new_state

    def on_key_press(self, key, modifiers):
        new_state = self.current_state.on_key_press(key, modifiers)
        if new_state:
            self.current_state = new_state

    def on_mouse_press(self, x, y, button, modifiers):
        new_state = self.current_state.on_mouse_press(x, y, button, modifiers)
        if new_state:
            self.current_state = new_state

    def on_mouse_release(self, x, y, button, modifiers):
        if hasattr(self.current_state, 'on_mouse_release'):
            new_state = self.current_state.on_mouse_release(x, y, button, modifiers)
            if new_state:
                self.current_state = new_state

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if hasattr(self.current_state, 'on_mouse_drag'):
            new_state = self.current_state.on_mouse_drag(x, y, dx, dy, buttons, modifiers)
            if new_state:
                self.current_state = new_state

def main():
    game = TetrisGame()
    arcade.run()

if __name__ == "__main__":
    main()