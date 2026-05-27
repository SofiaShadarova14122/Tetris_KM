# Tetris_KM/input_manager.py
import arcade

class InputManager:
    def __init__(self):
        self.keyboard_keys = set()
        self.bear_keys = {1: set(), 2: set()}

    def clear(self):
        self.keyboard_keys.clear()
        self.bear_keys[1].clear()
        self.bear_keys[2].clear()

    def update(self, physical_keys: set):
        self.keyboard_keys = physical_keys.copy()

    def handle_bear_input(self, player_num: int, action: str):
        self.bear_keys[player_num].clear()
        if action is None: return

        p1_map = {'left': arcade.key.A, 'right': arcade.key.D, 'down': arcade.key.S, 'up': arcade.key.W}
        p2_map = {'left': arcade.key.LEFT, 'right': arcade.key.RIGHT, 'down': arcade.key.DOWN, 'up': arcade.key.UP}
        key_map = p1_map if player_num == 1 else p2_map

        if 'left' in action: self.bear_keys[player_num].discard(key_map['right'])
        if 'right' in action: self.bear_keys[player_num].discard(key_map['left'])
        if 'down' in action: self.bear_keys[player_num].discard(key_map['up'])

        if 'left' in action: self.bear_keys[player_num].add(key_map['left'])
        if 'right' in action: self.bear_keys[player_num].add(key_map['right'])
        if 'down' in action: self.bear_keys[player_num].add(key_map['down'])
        if action in ['up', 'up_left', 'up_right']:
            self.bear_keys[player_num].add(key_map['up'])

    def get_player1_input(self):
        merged = self.keyboard_keys.union(self.bear_keys[1])
        return {
            'left': arcade.key.A in merged,
            'right': arcade.key.D in merged,
            'up': arcade.key.W in merged,
            'rotate': arcade.key.W in merged,  # Для Тетриса
            'down': arcade.key.S in merged
        }

    def get_player2_input(self):
        merged = self.keyboard_keys.union(self.bear_keys[2])
        return {
            'left': arcade.key.LEFT in merged,
            'right': arcade.key.RIGHT in merged,
            'up': arcade.key.UP in merged,
            'rotate': arcade.key.UP in merged,  # Для Тетриса
            'down': arcade.key.DOWN in merged
        }