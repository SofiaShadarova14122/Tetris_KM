# Tetris_KM/input_manager.py
import arcade


class InputManager:
    def __init__(self):
        self.keyboard = set()
        self.bear = {1: set(), 2: set()}

    def clear(self):
        self.keyboard.clear()
        self.bear[1].clear()
        self.bear[2].clear()

    def update(self, keys: set):
        self.keyboard = keys.copy()

    def handle_bear(self, player: int, action: str):
        """Преобразует сигнал мишки в виртуальные клавиши"""
        self.bear[player].clear()
        if action is None:
            return

        map_keys = {
            1: {'left': arcade.key.A, 'right': arcade.key.D, 'down': arcade.key.S, 'up': arcade.key.W},
            2: {'left': arcade.key.LEFT, 'right': arcade.key.RIGHT, 'down': arcade.key.DOWN, 'up': arcade.key.UP}
        }
        km = map_keys.get(player, {})

        # Убираем конфликты
        if 'left' in action: self.bear[player].discard(km.get('right'))
        if 'right' in action: self.bear[player].discard(km.get('left'))
        if 'down' in action: self.bear[player].discard(km.get('up'))

        # Добавляем активные
        if 'left' in action and 'left' in km: self.bear[player].add(km['left'])
        if 'right' in action and 'right' in km: self.bear[player].add(km['right'])
        if 'down' in action and 'down' in km: self.bear[player].add(km['down'])
        if action in ['up', 'up_left', 'up_right'] and 'up' in km:
            self.bear[player].add(km['up'])

    def get_p1(self):
        m = self.keyboard | self.bear[1]
        return {
            'left': arcade.key.A in m, 'right': arcade.key.D in m,
            'up': arcade.key.W in m, 'rotate': arcade.key.W in m, 'down': arcade.key.S in m
        }

    def get_p2(self):
        m = self.keyboard | self.bear[2]
        return {
            'left': arcade.key.LEFT in m, 'right': arcade.key.RIGHT in m,
            'up': arcade.key.UP in m, 'rotate': arcade.key.UP in m, 'down': arcade.key.DOWN in m
        }