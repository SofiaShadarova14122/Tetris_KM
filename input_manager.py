# Tetris_KM/input_manager.py
import arcade


class InputManager:
    """Единый менеджер управления. Разделяет клавиатуру и мишек для избежания конфликтов."""

    def __init__(self):
        self.keyboard_keys = set()
        self.bear_keys = {1: set(), 2: set()}
        self.merged_keys = set()

    def update(self, physical_key_states: set):
        """Вызывается каждый кадр. Объединяет физическую клавиатуру и сигналы мишек."""
        self.keyboard_keys = physical_key_states.copy()
        self.merged_keys = self.keyboard_keys.copy()
        for p_keys in self.bear_keys.values():
            self.merged_keys.update(p_keys)

    def get_player1_input(self):
        return {
            'left': arcade.key.A in self.merged_keys,
            'right': arcade.key.D in self.merged_keys,
            'up': arcade.key.W in self.merged_keys,
            'down': arcade.key.S in self.merged_keys
        }

    def get_player2_input(self):
        return {
            'left': arcade.key.LEFT in self.merged_keys,
            'right': arcade.key.RIGHT in self.merged_keys,
            'up': arcade.key.UP in self.merged_keys,
            'down': arcade.key.DOWN in self.merged_keys
        }

    def handle_bear_input(self, player_num, action):
        """Обрабатывает сырые сигналы от мишек и переводит их в виртуальные клавиши."""
        self.bear_keys[player_num].clear()
        if action is None:
            return  # Отпускание кнопки

        keys_map = {
            'left': arcade.key.A if player_num == 1 else arcade.key.LEFT,
            'right': arcade.key.D if player_num == 1 else arcade.key.RIGHT,
            'down': arcade.key.S if player_num == 1 else arcade.key.DOWN,
            'up': arcade.key.W if player_num == 1 else arcade.key.UP,
        }

        # Убираем конфликтующие направления
        if 'left' in action: self.bear_keys[player_num].discard(keys_map['right'])
        if 'right' in action: self.bear_keys[player_num].discard(keys_map['left'])
        if 'down' in action: self.bear_keys[player_num].discard(keys_map['up'])

        # Добавляем активные
        if 'left' in action: self.bear_keys[player_num].add(keys_map['left'])
        if 'right' in action: self.bear_keys[player_num].add(keys_map['right'])
        if 'down' in action: self.bear_keys[player_num].add(keys_map['down'])

        if action in ['up', 'up_left', 'up_right']:
            self.bear_keys[player_num].add(keys_map['up'])