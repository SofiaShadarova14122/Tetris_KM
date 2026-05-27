# Tetris_KM/main.py
import arcade, os, importlib
from ui.serial_menu import SerialMenu
from config import Config
from cyber_bear_comms.client import CyberBearClient


class MainMenu(arcade.Window):
    def __init__(self, bear_client=None, show_menu=False):
        super().__init__(800, 600, "КиберМедведи")
        arcade.set_background_color((241, 241, 241))
        self.bear = bear_client
        self.exit = False
        self.show_menu = show_menu or (bear_client is not None)
        self.input = SerialMenu(800, 600)
        self.state = "input"
        self.games = []

        gp = os.path.join(os.path.dirname(__file__), "games")
        if os.path.exists(gp):
            for f in os.listdir(gp):
                p = os.path.join(gp, f)
                if os.path.isdir(p) and os.path.exists(os.path.join(p, "main.py")):
                    self.games.append(f)

        # Кнопки: {'x':left, 'y':bottom, 'w':width, 'h':height}
        self.btns = {
            'versus': {'x': 250, 'y': 300, 'w': 300, 'h': 50},
            'coop': {'x': 250, 'y': 230, 'w': 300, 'h': 50},
            'fishing': {'x': 250, 'y': 160, 'w': 300, 'h': 50},
            'pingpong': {'x': 250, 'y': 90, 'w': 300, 'h': 50}
        }

    def on_update(self, dt):
        if self.state == "input" and not self.show_menu: self.input.update(dt)

    def on_draw(self):
        self.clear()
        if self.state == "input" and not self.show_menu:
            self.input.draw()
        else:
            Config.draw_text("Выберите игру:", 400, 500, (40, 40, 40), 24)
            if self.bear:
                s = self.bear.get_status()
                Config.draw_text(f"{'✅' if s.get('bear1') else '❌'} Мишка 1", 400, 460,
                                 Config.P1_COLOR if s.get('bear1') else (150, 150, 150), 16)
                Config.draw_text(f"{'✅' if s.get('bear2') else '❌'} Мишка 2", 400, 430,
                                 Config.P2_COLOR if s.get('bear2') else (150, 150, 150), 16)
            else:
                Config.draw_text("🎮 Игра на клавиатуре", 400, 450, (100, 100, 100), 16)

            # Отрисовка кнопок с явными координатами
            for name, (label, color) in [
                ('versus', ("CyberCubes: Versus", (255, 100, 100))),
                ('coop', ("CyberCubes: Co-op", (100, 200, 100))),
                ('fishing', ("Рыбалка", (100, 180, 255))),
                ('pingpong', ("Ping-Pong", (150, 150, 150)))
            ]:
                b = self.btns[name]
                arcade.draw_lrbt_rectangle_filled(b['x'], b['x'] + b['w'], b['y'], b['y'] + b['h'], color)
                Config.draw_text(label, 400, b['y'] + 25, (255, 255, 255), 18)

    def on_text(self, t):
        if self.state == "input" and not self.show_menu: self.input.on_text(t)

    def on_key_press(self, k, m):
        if self.state == "input" and not self.show_menu:
            r = self.input.on_key(k, m)
            if r == "connect": self.connect()
        elif k == arcade.key.ESCAPE:
            self.state = "input";
            self.show_menu = False

    def on_mouse_press(self, x, y, b, m):
        if self.state == "input" and not self.show_menu:
            r = self.input.on_mouse(x, y)
            if r == "connect":
                self.connect()
            elif r == "skip":
                self.skip()
        elif self.state == "menu" or self.show_menu:
            for name in ['versus', 'coop', 'fishing', 'pingpong']:
                bt = self.btns[name]
                if bt['x'] <= x <= bt['x'] + bt['w'] and bt['y'] <= y <= bt['y'] + bt['h']:
                    self.launch(name)
                    return

    def connect(self):
        s1, s2 = self.input.s1.strip(), self.input.s2.strip()
        serials = [s for s in [s1, s2] if s]
        self.bear = CyberBearClient(serials or None)
        self.bear.start()
        self.state = "menu";
        self.show_menu = True

    def skip(self):
        self.bear = None
        self.state = "menu";
        self.show_menu = True

    def launch(self, mode):
        try:
            # ✅ ТОЧНОЕ сопоставление имени папки
            target = None
            mode_l = mode.lower()
            for g in self.games:
                gl = g.lower()
                if mode_l == 'fishing' and 'fishing' in gl:
                    target = g; break
                elif mode_l == 'pingpong' and 'ping' in gl:
                    target = g; break
                elif mode_l in ['versus', 'coop'] and any(k in gl for k in ['cyber', 'cubes', 'tetris']):
                    target = g; break

            if not target:
                print(f"❌ Не найдена игра для '{mode}'. Доступно: {self.games}")
                return

            # Очистка перед запуском
            if self.bear: self.bear.clear_queue()

            mod = importlib.import_module(f"games.{target}.main")
            self.close()  # Закрываем меню, но НЕ останавливаем BLE
            mod.main(self.bear, mode=mode)  # Запускаем игру

        except Exception as e:
            print(f"❌ Ошибка запуска {mode}: {e}")
            import traceback;
            traceback.print_exc()

    def on_close(self):
        if self.bear and not getattr(self, '_launching', False):
            self.bear.stop()
        self.exit = True
        super().on_close()


def main():
    client = None
    while True:
        app = MainMenu(client, show_menu=(client is not None))
        arcade.run()
        if app.exit: break
        client = app.bear  # Сохраняем клиента для следующей игры


if __name__ == "__main__":
    main()