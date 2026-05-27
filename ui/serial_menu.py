# Tetris_KM/ui/serial_menu.py
import arcade
from config import Config


class SerialMenu:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.s1 = self.s2 = ""
        self.active = 1
        self.cursor = True
        self.t = 0
        self.btn = {'x': 250, 'y': 180, 'w': 300, 'h': 50}
        self.skip = {'x': 250, 'y': 120, 'w': 300, 'h': 40}

    def update(self, dt):
        self.t += dt
        if self.t >= 0.5: self.cursor = not self.cursor; self.t = 0

    def draw(self):
        arcade.draw_lrbt_rectangle_filled(0, self.w, 0, self.h, (240, 240, 250))
        Config.draw_text("Введите серии КиберМишек", self.w // 2, 480, (40, 40, 40), 24)

        # P1
        c = Config.P1_COLOR if self.active == 1 else (150, 150, 150)
        arcade.draw_lrbt_rectangle_filled(250, 550, 350, 390, (255, 255, 255))
        arcade.draw_lrbt_rectangle_outline(250, 550, 350, 390, c, 3)
        txt = (self.s1 or "Игрок 1") + ("|" if self.active == 1 and self.cursor else "")
        Config.draw_text(f"Игрок 1: {txt}", 260, 370, (0, 0, 0), 16, anchor_x="left", anchor_y="center")

        # P2
        c = Config.P2_COLOR if self.active == 2 else (150, 150, 150)
        arcade.draw_lrbt_rectangle_filled(250, 550, 280, 320, (255, 255, 255))
        arcade.draw_lrbt_rectangle_outline(250, 550, 280, 320, c, 3)
        txt = (self.s2 or "Игрок 2") + ("|" if self.active == 2 and self.cursor else "")
        Config.draw_text(f"Игрок 2: {txt}", 260, 300, (0, 0, 0), 16, anchor_x="left", anchor_y="center")

        # Buttons
        b = self.btn
        arcade.draw_lrbt_rectangle_filled(b['x'], b['x'] + b['w'], b['y'], b['y'] + b['h'], (100, 200, 100))
        Config.draw_text("Подключить", 400, 205, (255, 255, 255), 18)
        b = self.skip
        arcade.draw_lrbt_rectangle_filled(b['x'], b['x'] + b['w'], b['y'], b['y'] + b['h'], (150, 150, 200))
        Config.draw_text("Пропустить", 400, 140, (255, 255, 255), 16)

    def on_text(self, t):
        if self.active == 1:
            self.s1 += t
        else:
            self.s2 += t

    def on_key(self, k, _):
        if k == arcade.key.TAB:
            self.active = 2 if self.active == 1 else 1
        elif k == arcade.key.BACKSPACE:
            if self.active == 1:
                self.s1 = self.s1[:-1]
            else:
                self.s2 = self.s2[:-1]
        elif k == arcade.key.ENTER:
            return "connect"
        return None

    def on_mouse(self, x, y):
        if 250 <= x <= 550 and 350 <= y <= 390: self.active = 1; return None
        if 250 <= x <= 550 and 280 <= y <= 320: self.active = 2; return None
        b = self.btn
        if b['x'] <= x <= b['x'] + b['w'] and b['y'] <= y <= b['y'] + b['h']: return "connect"
        b = self.skip
        if b['x'] <= x <= b['x'] + b['w'] and b['y'] <= y <= b['y'] + b['h']: return "skip"
        return None