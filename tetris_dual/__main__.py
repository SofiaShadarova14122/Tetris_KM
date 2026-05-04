import arcade
from .states.menu_state import MenuState

class TetrisGame(arcade.Window):
    def __init__(self):
        from .config import SCREEN_WIDTH, SCREEN_HEIGHT, TITLE
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, TITLE)
        arcade.set_background_color((20, 20, 30))
        self.current_state = MenuState()

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

def main():
    game = TetrisGame()
    arcade.run()

if __name__ == "__main__":
    main()