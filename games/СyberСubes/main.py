# Tetris_KM/games/CyberCubes/main.py
import arcade
from input_manager import InputManager
from .game import CyberCubesGame


class CubesWindow(arcade.Window):
    def __init__(self, bear_client):
        super().__init__(1040, 950, "Мишуткины Кубики")
        self.center_window()
        self.bear_client = bear_client
        self.kb = InputManager()
        self.game = CyberCubesGame()
        self.pressed_keys = set()

    def on_update(self, dt):
        if not self.game.game_over:
            self.kb.update(self.pressed_keys)
            if self.bear_client: self.game.apply_controller_actions(self.bear_client.get_actions())
            self.game.apply_keyboard_actions(self._get_kb_actions())
            self.game.update(dt)

    def _get_kb_actions(self):
        acts = []
        # ⛔ Вращение ('rotate') убрано из опроса, чтобы не крутилось при удержании
        for k, p, a in [(arcade.key.A, 1, 'left'), (arcade.key.S, 1, 'down'), (arcade.key.D, 1, 'right'),
                        (arcade.key.LEFT, 2, 'left'), (arcade.key.DOWN, 2, 'down'), (arcade.key.RIGHT, 2, 'right')]:
            if k in self.pressed_keys: acts.append((p, a))
        return acts

    def on_draw(self):
        self.clear(); self.game.draw()

    def on_key_press(self, key, mods):
        self.pressed_keys.add(key)
        if key == arcade.key.P:
            self.game.toggle_pause()
        elif key in (arcade.key.ESCAPE, arcade.key.M):
            arcade.close_window()

        # ✅ ВРАЩЕНИЕ: обрабатываем только в момент нажатия (один раз)
        elif key in (arcade.key.W, arcade.key.UP):
            player = self.game.p1 if key == arcade.key.W else self.game.p2
            if not player.game_over and not player.rotate_lock:
                player.rotate(1)
                player.rotate_lock = True  # Блокируем повторное вращение

    def on_key_release(self, key, mods):
        if key in self.pressed_keys: self.pressed_keys.remove(key)
        # ✅ Снимаем блокировку только после полного отпускания кнопки
        if key in (arcade.key.W, arcade.key.UP):
            player = self.game.p1 if key == arcade.key.W else self.game.p2
            player.rotate_lock = False


def main(bear_client=None):
    """Функция запуска игры"""
    app = CubesWindow(bear_client)
    arcade.run()