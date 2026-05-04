# tetris_dual/states/settings_state.py
import arcade
from .base_state import GameState


class SettingsState(GameState):
    def __init__(self, music_player):
        self.music_player = music_player
        self.volume = 0.4
        if music_player:
            self.volume = music_player.volume

    def on_draw(self, window):
        window.clear()
        arcade.draw_text("НАСТРОЙКИ", window.width // 2, window.height // 2 + 100,
                         (240, 240, 240), 32, anchor_x="center")

        # Ползунок громкости
        arcade.draw_text("Громкость музыки:", window.width // 2 - 150, window.height // 2,
                         (240, 240, 240), 20)

        # Фон ползунка
        arcade.draw_lrbt_rectangle_filled(
            window.width // 2 - 100, window.width // 2 + 100,
            window.height // 2 - 10, window.height // 2 + 10,
            (100, 100, 100)
        )
        # Ползунок
        pos_x = window.width // 2 - 100 + self.volume * 200
        arcade.draw_lrbt_rectangle_filled(
            pos_x - 5, pos_x + 5,
            window.height // 2 - 15, window.height // 2 + 15,
            (200, 200, 255)
        )

        arcade.draw_text("Нажмите ESC для возврата в игру", window.width // 2, 50,
                         (240, 240, 240), 16, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            from .gameplay_state import GameplayState
            new_state = GameplayState()
            # Сохраняем громкость
            if self.music_player and new_state.music_player:
                new_state.music_player.volume = self.volume
            return new_state
        return self

    def on_mouse_press(self, x, y, button, modifiers):
        # Простой клик для изменения громкости (упрощённо)
        if 300 < x < 500 and 470 < y < 490:  # область ползунка
            self.volume = min(1.0, max(0.0, (x - 300) / 200))
            if self.music_player:
                self.music_player.volume = self.volume
        return self