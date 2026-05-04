import arcade
from .base_state import GameState

class MenuState(GameState):
    def on_draw(self, window):
        window.clear()
        arcade.draw_text("ПАРНЫЙ ТЕТРИС", window.width // 2, window.height // 2 + 50,
                         (240, 240, 240), 32, anchor_x="center")
        arcade.draw_text("Нажмите ПРОБЕЛ для начала", window.width // 2, window.height // 2 - 50,
                         (240, 240, 240), 20, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            from .gameplay_state import GameplayState
            return GameplayState()
        return self

    def on_mouse_press(self, x, y, button, modifiers):
        from .gameplay_state import GameplayState
        return GameplayState()