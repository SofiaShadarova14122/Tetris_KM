# Tetris_KM/input_manager.py
import arcade

class InputManager:
    def __init__(self):
        self.keyboard_keys = set()
        self.bear_state = {1: {}, 2: {}}  # Хранит текущее состояние кнопок мишек

    def update(self, physical_key_states: set):
        self.keyboard_keys = physical_key_states.copy()

    def get_player1_input(self):
        merged = self.keyboard_keys.copy()
        merged.update(self.bear_state[1].values())
        return {
            'left': arcade.key.A in merged,
            'right': arcade.key.D in merged,
            'up': arcade.key.W in merged,
            'down': arcade.key.S in merged
        }

    def get_player2_input(self):
        merged = self.keyboard_keys.copy()
        merged.update(self.bear_state[2].values())
        return {
            'left': arcade.key.LEFT in merged,
            'right': arcade.key.RIGHT in merged,
            'up': arcade.key.UP in merged,
            'down': arcade.key.DOWN in merged
        }

    def handle_bear_input(self, player_num, action):
        """Обновляет состояние кнопок для конкретного мишки"""
        keys_map = {
            'left':   arcade.key.A if player_num == 1 else arcade.key.LEFT,
            'right':  arcade.key.D if player_num == 1 else arcade.key.RIGHT,
            'down':   arcade.key.S if player_num == 1 else arcade.key.DOWN,
            'up':     arcade.key.W if player_num == 1 else arcade.key.UP,
        }

        if action is None:
            # Отпускание всех кнопок для этого игрока
            self.bear_state[player_num].clear()
        else:
            # Сбрасываем конфликтующие направления
            if 'left' in action: self.bear_state[player_num].pop('right', None)
            if 'right' in action: self.bear_state[player_num].pop('left', None)
            if 'down' in action: self.bear_state[player_num].pop('up', None)

            # Добавляем активные
            if 'left' in action: self.bear_state[player_num]['left'] = keys_map['left']
            if 'right' in action: self.bear_state[player_num]['right'] = keys_map['right']
            if 'down' in action: self.bear_state[player_num]['down'] = keys_map['down']
            if action in ['up', 'up_left', 'up_right']:
                self.bear_state[player_num]['up'] = keys_map['up']
            elif 'up' in self.bear_state[player_num]:
                del self.bear_state[player_num]['up']