import arcade
from .base_state import GameState
from ..ui.rendering import draw_game_over

class GameOverState(GameState):
    def __init__(self, winner, score1, score2):
        self.winner = winner
        self.score1 = score1
        self.score2 = score2

    def on_draw(self, window):
        window.clear()
        draw_game_over(self.winner, self.score1, self.score2, window.width, window.height)

    def on_key_press(self, key, modifiers):
        from .menu_pause_settings import MenuState
        window = arcade.get_window()
        music = getattr(window, 'music_controller', None)
        return MenuState(music)