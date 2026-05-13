# Tetris_KM/input_manager.py
import arcade

class InputManager:
    """Единый менеджер управления для всех игр"""
    def __init__(self):
        self.pressed_keys = set()
        self.rotate_used_p1 = False
        self.rotate_used_p2 = False

    def update(self, key_states: set):
        self.pressed_keys = key_states
        if arcade.key.W not in self.pressed_keys:
            self.rotate_used_p1 = False
        if arcade.key.UP not in self.pressed_keys:
            self.rotate_used_p2 = False

    def get_player1_input(self):
        return {
            'left': arcade.key.A in self.pressed_keys,
            'right': arcade.key.D in self.pressed_keys,
            'up': arcade.key.W in self.pressed_keys,
            'rotate': arcade.key.W in self.pressed_keys and not self.rotate_used_p1,
            'down': arcade.key.S in self.pressed_keys
        }

    def get_player2_input(self):
        return {
            'left': arcade.key.LEFT in self.pressed_keys,
            'right': arcade.key.RIGHT in self.pressed_keys,
            'up': arcade.key.UP in self.pressed_keys,
            'rotate': arcade.key.UP in self.pressed_keys and not self.rotate_used_p2,
            'down': arcade.key.DOWN in self.pressed_keys
        }

    def mark_rotate_used(self, player):
        if player == 1:
            self.rotate_used_p1 = True
        else:
            self.rotate_used_p2 = True