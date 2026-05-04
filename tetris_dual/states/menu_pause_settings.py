import arcade
from .base_state import GameState
from ..ui.theme import TEXT_COLOR
from ..sounds import is_sounds_enabled, set_sounds_enabled

# ------------------------------------------------------------
class MusicController:
    """Простой контроллер громкости для музыки."""
    def __init__(self, sound):
        self.sound = sound
        self._volume = 0.7
    @property
    def volume(self):
        return self._volume
    @volume.setter
    def volume(self, value):
        self._volume = max(0.0, min(1.0, value))
        if self.sound:
            self.sound.volume = self._volume
# ------------------------------------------------------------

class MenuState(GameState):
    def __init__(self, music_player):
        self.music_player = music_player

    def on_draw(self, window):
        window.clear()
        arcade.draw_text("ПАРНЫЙ ТЕТРИС", window.width//2, window.height//2+50,
                         TEXT_COLOR, 36, anchor_x="center")
        arcade.draw_text("ПРОБЕЛ - начать игру", window.width//2, window.height//2-50,
                         TEXT_COLOR, 20, anchor_x="center")
        arcade.draw_text("S - настройки", window.width//2, window.height//2-100,
                         (200,200,200), 16, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            from .gameplay_state import GameplayState
            return GameplayState(self.music_player)
        elif key == arcade.key.S:
            return SettingsState(self.music_player, return_state=self)
        return self

# ------------------------------------------------------------
class PauseState(GameState):
    def __init__(self, gameplay_state, music_player):
        self.gameplay_state = gameplay_state
        self.music_player = music_player

    def on_draw(self, window):
        self.gameplay_state.on_draw(window)
        arcade.draw_lrbt_rectangle_filled(0, window.width, 0, window.height,
                                          (0,0,0,180))
        arcade.draw_text("ПАУЗА", window.width//2, window.height//2+60,
                         TEXT_COLOR, 48, anchor_x="center")
        arcade.draw_text("ПРОБЕЛ или P - продолжить", window.width//2, window.height//2,
                         TEXT_COLOR, 24, anchor_x="center")
        arcade.draw_text("ESC - выход в меню", window.width//2, window.height//2-40,
                         TEXT_COLOR, 20, anchor_x="center")
        arcade.draw_text("S - настройки", window.width//2, window.height//2-80,
                         TEXT_COLOR, 18, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key in (arcade.key.SPACE, arcade.key.P):
            return self.gameplay_state
        elif key == arcade.key.ESCAPE:
            return MenuState(self.music_player)
        elif key == arcade.key.S:
            return SettingsState(self.music_player, return_state=self)
        return self

    def on_update(self, delta_time):
        return self

# ------------------------------------------------------------
class SettingsState(GameState):
    def __init__(self, music_player, return_state):
        self.music_player = music_player
        self.return_state = return_state
        self.music_volume = music_player.volume if music_player else 0.7
        self.sounds_enabled = is_sounds_enabled()
        self.dragging = False

    def on_draw(self, window):
        arcade.draw_lrbt_rectangle_filled(0, window.width, 0, window.height,
                                          (40,40,50,255))
        arcade.draw_text("НАСТРОЙКИ", window.width//2, window.height//2+150,
                         TEXT_COLOR, 32, anchor_x="center")

        # Ползунок громкости
        arcade.draw_text("Громкость музыки", window.width//2-150, window.height//2+40,
                         TEXT_COLOR, 18)
        slider_left = window.width//2 - 100
        slider_right = window.width//2 + 100
        slider_y = window.height//2
        arcade.draw_lrbt_rectangle_filled(slider_left, slider_right,
                                          slider_y-10, slider_y+10,
                                          (100,100,100))
        handle_x = slider_left + self.music_volume * 200
        arcade.draw_lrbt_rectangle_filled(handle_x-5, handle_x+5,
                                          slider_y-15, slider_y+15,
                                          (200,200,255))

        # Переключатель звуков
        arcade.draw_text("Звуки", window.width//2-150, window.height//2-40,
                         TEXT_COLOR, 18)
        toggle_x = window.width//2 - 50
        toggle_y = window.height//2 - 40
        if self.sounds_enabled:
            arcade.draw_text("ВКЛ", toggle_x, toggle_y, (100,255,100), 20, anchor_x="center")
            arcade.draw_lrbt_rectangle_filled(toggle_x+25, toggle_x+55,
                                              toggle_y-10, toggle_y+10,
                                              (100,255,100))
        else:
            arcade.draw_text("ВЫКЛ", toggle_x, toggle_y, (255,100,100), 20, anchor_x="center")
            arcade.draw_lrbt_rectangle_filled(toggle_x+25, toggle_x+55,
                                              toggle_y-10, toggle_y+10,
                                              (100,100,100))

        arcade.draw_text("ESC - назад", window.width//2, 50,
                         TEXT_COLOR, 16, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            if self.music_player:
                self.music_player.volume = self.music_volume
            set_sounds_enabled(self.sounds_enabled)
            return self.return_state
        return self

    def on_mouse_press(self, x, y, button, modifiers):
        window = arcade.get_window()
        slider_left = window.width//2 - 100
        slider_right = window.width//2 + 100
        slider_y = window.height//2
        if slider_left <= x <= slider_right and slider_y-10 <= y <= slider_y+10:
            self.dragging = True
            self._set_volume_from_x(x)
        toggle_x = window.width//2 - 50
        toggle_y = window.height//2 - 40
        if toggle_x-30 <= x <= toggle_x+30 and toggle_y-15 <= y <= toggle_y+15:
            self.sounds_enabled = not self.sounds_enabled
        return self

    def on_mouse_release(self, x, y, button, modifiers):
        self.dragging = False
        return self

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.dragging:
            self._set_volume_from_x(x)
        return self

    def _set_volume_from_x(self, x):
        window = arcade.get_window()
        slider_left = window.width//2 - 100
        slider_right = window.width//2 + 100
        self.music_volume = min(1.0, max(0.0, (x - slider_left) / 200))
        if self.music_player:
            self.music_player.volume = self.music_volume