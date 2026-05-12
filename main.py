# Tetris_KM/main.py
import arcade
import os
import importlib

class TextInput:
    def __init__(self, x, y, width, height, placeholder=""):
        self.x, self.y, self.width, self.height = x, y, width, height
        self.text, self.placeholder = "", placeholder
        self.active, self.cursor_visible, self.cursor_timer = False, True, 0.0

    def draw(self):
        color = (0, 100, 200) if self.active else (150, 150, 150)
        arcade.draw_lrbt_rectangle_filled(self.x, self.x+self.width, self.y, self.y+self.height, (255,255,255))
        arcade.draw_lrbt_rectangle_outline(self.x, self.x+self.width, self.y, self.y+self.height, color, 3)
        display = self.text if self.text else self.placeholder
        if self.active and self.cursor_visible: display += "|"
        arcade.draw_text(display, self.x+10, self.y+self.height//2, (0,0,0), 16, anchor_y="center")

    def update(self, dt):
        self.cursor_timer += dt
        if self.cursor_timer >= 0.5: self.cursor_visible = not self.cursor_visible; self.cursor_timer = 0.0
    def add_text(self, text):
        if self.active: self.text += text
    def backspace(self):
        if self.active: self.text = self.text[:-1]

class MainMenu(arcade.Window):
    def __init__(self, bear_client=None, show_game_menu=False):
        super().__init__(800, 600, "КиберМедведи: Меню")
        arcade.set_background_color((241, 241, 241))
        self.bear_client = bear_client
        self.exit_program = False
        self.show_game_menu = show_game_menu  # Сразу показать меню выбора игры
        self.input1 = TextInput(250, 350, 300, 40, "Серия мишки 1")
        self.input2 = TextInput(250, 280, 300, 40, "Серия мишки 2")
        self.start_btn = {'x': 300, 'y': 180, 'w': 200, 'h': 50}
        self.state, self.selected_game = "input", None
        self.game_folders = []
        games_path = os.path.join(os.path.dirname(__file__), "games")
        if os.path.exists(games_path):
            for item in os.listdir(games_path):
                full = os.path.join(games_path, item)
                if os.path.isdir(full) and os.path.exists(os.path.join(full, "main.py")):
                    self.game_folders.append(item)

    def on_update(self, dt):
        if self.state == "input" and not self.show_game_menu:
            self.input1.update(dt); self.input2.update(dt)

    def on_draw(self):
        self.clear()
        if self.state == "input" and not self.show_game_menu:
            arcade.draw_text("Введите серии КиберМишек", 400, 480, (40,40,40), 24, anchor_x="center")
            arcade.draw_text("Игрок 1:", 240, 370, (0,0,0), 16, anchor_x="right", anchor_y="center")
            arcade.draw_text("Игрок 2:", 240, 300, (0,0,0), 16, anchor_x="right", anchor_y="center")
            self.input1.draw(); self.input2.draw()
            arcade.draw_lrbt_rectangle_filled(self.start_btn['x'], self.start_btn['x']+self.start_btn['w'],
                                              self.start_btn['y'], self.start_btn['y']+self.start_btn['h'], (100,200,100))
            arcade.draw_text("Подключить", 400, 205, (255,255,255), 18, anchor_x="center", anchor_y="center")
        else:
            # Меню выбора игры (показываем сразу если show_game_menu=True)
            status = self.bear_client.get_status() if self.bear_client else {'bear1':False, 'bear2':False}
            arcade.draw_text("Выберите игру:", 400, 500, (40,40,40), 24, anchor_x="center")
            s1, s2 = "Мишка 1 найден ✅" if status.get('bear1') else "Мишка 1 не найден ❌", "Мишка 2 найден ✅" if status.get('bear2') else "Мишка 2 не найден ❌"
            c1, c2 = (0,120,0) if status.get('bear1') else (180,0,0), (0,120,0) if status.get('bear2') else (180,0,0)
            arcade.draw_text(s1, 400, 460, c1, 16, anchor_x="center")
            arcade.draw_text(s2, 400, 430, c2, 16, anchor_x="center")
            y = 380
            for name in self.game_folders:
                color = (100,200,255) if self.selected_game == name else (200,200,255)
                arcade.draw_lrbt_rectangle_filled(250, 550, y, y+40, color)
                arcade.draw_text(name.replace("_"," ").title(), 400, y+20, (30,30,30), 16, anchor_x="center", anchor_y="center")
                y -= 50

    def on_text(self, text):
        if self.state == "input" and not self.show_game_menu:
            if self.input1.active: self.input1.add_text(text)
            elif self.input2.active: self.input2.add_text(text)

    def on_key_press(self, key, mods):
        if self.state == "input" and not self.show_game_menu:
            if key == arcade.key.TAB: self.input1.active = not self.input1.active; self.input2.active = not self.input2.active
            elif key == arcade.key.BACKSPACE: self.input1.backspace() if self.input1.active else self.input2.backspace()
            elif key == arcade.key.ENTER: self.connect_and_go_menu()
        elif self.state == "menu" or self.show_game_menu:
            if key == arcade.key.ENTER and self.selected_game:
                self.launch_game()

    def on_mouse_press(self, x, y, btn, mods):
        if self.state == "input" and not self.show_game_menu:
            self.input1.active = self.input1.x <= x <= self.input1.x+self.input1.width and self.input1.y <= y <= self.input1.y+self.input1.height
            self.input2.active = not self.input1.active and self.input2.x <= x <= self.input2.x+self.input2.width and self.input2.y <= y <= self.input2.y+self.input2.height
            if self.start_btn['x'] <= x <= self.start_btn['x']+self.start_btn['w'] and self.start_btn['y'] <= y <= self.start_btn['y']+self.start_btn['h']:
                self.connect_and_go_menu()
        elif self.state == "menu" or self.show_game_menu:
            y_pos = 380
            for name in self.game_folders:
                if 250 <= x <= 550 and y_pos <= y <= y_pos+40:
                    self.selected_game = name
                    self.launch_game()
                    return
                y_pos -= 50

    def connect_and_go_menu(self):
        from cyber_bear_comms import CyberBearClient
        s1, s2 = self.input1.text.strip(), self.input2.text.strip()
        if not s1 or not s2: return
        if self.bear_client and self.bear_client.serials == [s1, s2]:
            self.state = "menu"; self.show_game_menu = True; return
        self.bear_client = CyberBearClient(serials=[s1, s2], max_bears=2)
        self.bear_client.start()
        self.state = "menu"
        self.show_game_menu = True

    def launch_game(self):
        if not self.selected_game: return
        try:
            mod = importlib.import_module(f"games.{self.selected_game}.main")
            self.close()
            mod.main(self.bear_client)
        except Exception as e:
            print(f"❌ Ошибка запуска: {e}")

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