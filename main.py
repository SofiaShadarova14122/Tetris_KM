# Tetris_KM/main.py
import arcade
import os
import importlib
from ui.serial_menu import SerialMenu
from config import Config
from cyber_bear_comms.client import CyberBearClient


class MainMenu(arcade.Window):
    def __init__(self, bear_client=None, show_game_menu=False):
        super().__init__(800, 600, "КиберМедведи")
        arcade.set_background_color((241, 241, 241))
        self.bear_client = bear_client
        self.exit_program = False
        self.show_game_menu = show_game_menu or (bear_client is not None)
        self.input_menu = SerialMenu(800, 600)
        self.state = "input"
        self.game_folders = []

        # Сканируем игры
        games_path = os.path.join(os.path.dirname(__file__), "games")
        if os.path.exists(games_path):
            for item in os.listdir(games_path):
                full = os.path.join(games_path, item)
                if os.path.isdir(full) and os.path.exists(os.path.join(full, "main.py")):
                    self.game_folders.append(item)

        # Кнопки выбора режима
        self.btn_versus = {'x': 250, 'y': 300, 'w': 300, 'h': 50}
        self.btn_coop = {'x': 250, 'y': 230, 'w': 300, 'h': 50}
        self.btn_fishing = {'x': 250, 'y': 160, 'w': 300, 'h': 50}
        self.btn_pingpong = {'x': 250, 'y': 90, 'w': 300, 'h': 50}  # ✅ Новая кнопка

    def on_update(self, dt):
        if self.state == "input" and not self.show_game_menu:
            self.input_menu.update(dt)

    def on_draw(self):
        self.clear()
        if self.state == "input" and not self.show_game_menu:
            self.input_menu.draw()
        else:
            Config.draw_text("Выберите игру:", 400, 500, (40, 40, 40), 24, anchor_x="center")

            if self.bear_client:
                status = self.bear_client.get_status()
                c1 = Config.P1_COLOR if status.get('bear1') else (150, 150, 150)
                c2 = Config.P2_COLOR if status.get('bear2') else (150, 150, 150)
                Config.draw_text(f"{'✅' if status.get('bear1') else '❌'} Мишка 1", 400, 460, c1, 16, anchor_x="center")
                Config.draw_text(f"{'✅' if status.get('bear2') else ''} Мишка 2", 400, 430, c2, 16, anchor_x="center")
            else:
                Config.draw_text("🎮 Игра на клавиатуре", 400, 450, (100, 100, 100), 16, anchor_x="center")

            # Кнопка CyberCubes Versus
            arcade.draw_lrbt_rectangle_filled(
                self.btn_versus['x'], self.btn_versus['x'] + self.btn_versus['w'],
                self.btn_versus['y'], self.btn_versus['y'] + self.btn_versus['h'],
                (255, 100, 100)
            )
            Config.draw_text("CyberCubes: Versus", 400, 325, (255, 255, 255), 18, anchor_x="center", anchor_y="center")
            Config.draw_text("(С мусорными линиями)", 400, 305, (200, 200, 200), 12, anchor_x="center",
                             anchor_y="center")

            # Кнопка CyberCubes Co-op
            arcade.draw_lrbt_rectangle_filled(
                self.btn_coop['x'], self.btn_coop['x'] + self.btn_coop['w'],
                self.btn_coop['y'], self.btn_coop['y'] + self.btn_coop['h'],
                (100, 200, 100)
            )
            Config.draw_text("CyberCubes: Co-op", 400, 255, (255, 255, 255), 18, anchor_x="center", anchor_y="center")
            Config.draw_text("(Общий счет, синхронно)", 400, 235, (200, 200, 200), 12, anchor_x="center",
                             anchor_y="center")

            # Кнопка Fishing
            arcade.draw_lrbt_rectangle_filled(
                self.btn_fishing['x'], self.btn_fishing['x'] + self.btn_fishing['w'],
                self.btn_fishing['y'], self.btn_fishing['y'] + self.btn_fishing['h'],
                (100, 180, 255)
            )
            Config.draw_text("Рыбалка (Общее поле)", 400, 185, (255, 255, 255), 18, anchor_x="center",
                             anchor_y="center")

            # ✅ Кнопка PingPong
            arcade.draw_lrbt_rectangle_filled(
                self.btn_pingpong['x'], self.btn_pingpong['x'] + self.btn_pingpong['w'],
                self.btn_pingpong['y'], self.btn_pingpong['y'] + self.btn_pingpong['h'],
                (150, 150, 150)
            )
            Config.draw_text("Ping-Pong", 400, 115, (255, 255, 255), 18, anchor_x="center", anchor_y="center")

    def on_text(self, text):
        if self.state == "input" and not self.show_game_menu:
            self.input_menu.on_text(text)

    def on_key_press(self, key, mods):
        if self.state == "input" and not self.show_game_menu:
            res = self.input_menu.on_key(key, mods)
            if res == "connect": self.connect_and_go_menu()
        elif key == arcade.key.ESCAPE:
            self.state = "input"
            self.show_game_menu = False

    def on_mouse_press(self, x, y, btn, mods):
        if self.state == "input" and not self.show_game_menu:
            res = self.input_menu.on_mouse(x, y)
            if res == "connect":
                self.connect_and_go_menu()
            elif res == "skip":
                self.skip_and_go_menu()
        elif self.state == "menu" or self.show_game_menu:
            if self._hit_button(self.btn_versus, x, y):
                self.launch_game(mode='versus')
            elif self._hit_button(self.btn_coop, x, y):
                self.launch_game(mode='coop')
            elif self._hit_button(self.btn_fishing, x, y):
                self.launch_game(mode='fishing')
            elif self._hit_button(self.btn_pingpong, x, y):  # ✅ Обработка клика
                self.launch_game(mode='pingpong')

    def _hit_button(self, btn, x, y):
        return (btn['x'] <= x <= btn['x'] + btn['w'] and
                btn['y'] <= y <= btn['y'] + btn['h'])

    def connect_and_go_menu(self):
        s1, s2 = self.input_menu.s1.strip(), self.input_menu.s2.strip()
        serials = [s for s in [s1, s2] if s]
        self.bear_client = CyberBearClient(serials if serials else None)
        self.bear_client.start()
        self.state = "menu"
        self.show_game_menu = True

    def skip_and_go_menu(self):
        self.bear_client = None
        self.state = "menu"
        self.show_game_menu = True

    def launch_game(self, mode='versus'):
        try:
            target_folder = None
            for folder in self.game_folders:
                # Нормализуем имя: убираем кириллицу, меняем регистр
                norm = folder.lower().replace('с', 'c').replace('у', 'y').replace('е', 'e').replace('р', 'p').replace(
                    'о', 'o').replace('а', 'a')

                if mode == 'fishing':
                    if 'fishing' in norm:
                        target_folder = folder
                        break
                elif mode == 'pingpong':  # ✅ Поиск папки PingPong
                    if 'pingpong' in norm or 'ping' in norm:
                        target_folder = folder
                        break
                else:  # versus или coop
                    if any(k in norm for k in ['cyber', 'cubes', 'tetris']):
                        target_folder = folder
                        break

            if not target_folder:
                print(f"❌ Не найдена папка для '{mode}'. Доступные: {self.game_folders}")
                return

            print(f"✅ Запускаем: games.{target_folder}.main")
            mod = importlib.import_module(f"games.{target_folder}.main")

            self.close()
            # Безопасный вызов: проверяем, принимает ли функция mode
            import inspect
            sig = inspect.signature(mod.main)
            if 'mode' in sig.parameters:
                mod.main(self.bear_client, mode=mode)
            else:
                mod.main(self.bear_client)

        except Exception as e:
            print(f"❌ Ошибка запуска: {e}")
            import traceback
            traceback.print_exc()

    def on_close(self):
        if self.bear_client: self.bear_client.stop()
        self.exit_program = True
        super().on_close()


def main():
    client = None
    while True:
        app = MainMenu(client, show_game_menu=(client is not None))
        arcade.run()
        if app.exit_program: break
        client = app.bear_client


if __name__ == "__main__":
    main()