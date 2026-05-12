# Tetris_KM/input_manager.py
import arcade

class InputManager:
    """Единый менеджер управления для всех игр"""
    def __init__(self):
        self.pressed_keys = set()

    def update(self, key_states: set):
        self.pressed_keys = key_states

    def get_player1_input(self):
        return {
            'left': arcade.key.A in self.pressed_keys,
            'right': arcade.key.D in self.pressed_keys,
            'up': arcade.key.W in self.pressed_keys,
        }

    def get_player2_input(self):
        return {
            'left': arcade.key.LEFT in self.pressed_keys,
            'right': arcade.key.RIGHT in self.pressed_keys,
            'up': arcade.key.UP in self.pressed_keys,
        }