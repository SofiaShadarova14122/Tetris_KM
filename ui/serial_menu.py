# Tetris_KM/ui/serial_menu.py
import arcade
from config import Config


class SerialMenu:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.s1, self.s2 = "", ""
        self.active = 1
        self.cursor = True;
        self.t = 0  # self.t — это таймер курсора, не путать с параметром text
        self.btn = {'x': 300, 'y': 180, 'w': 200, 'h': 50}
        self.skip = {'x': 300, 'y': 120, 'w': 200, 'h': 40}

    def update(self, dt):
        self.t += dt
        if self.t >= 0.5: self.cursor = not self.cursor; self.t = 0

    def draw(self):
        arcade.draw_lrbt_rectangle_filled(0, self.w, 0, self.h, (240, 240, 250))
        Config.draw_text("Введите серии КиберМишек", self.w // 2, 480, (40, 40, 40), 24, anchor_x="center")

        # Поле ввода Игрока 1 (Синяя рамка)
        c1 = Config.P1_COLOR if self.active == 1 else (150, 150, 150)
        arcade.draw_lrbt_rectangle_filled(250, 550, 350, 390, (255, 255, 255))
        arcade.draw_lrbt_rectangle_outline(250, 550, 350, 390, c1, 3)
        txt1 = (self.s1 if self.s1 else "Игрок 1") + ("|" if self.active == 1 and self.cursor else "")
        Config.draw_text(f"Игрок 1: {txt1}", 260, 370, (0, 0, 0), 16, anchor_y="center")

        # Поле ввода Игрока 2 (Красная рамка)
        c2 = Config.P2_COLOR if self.active == 2 else (150, 150, 150)
        arcade.draw_lrbt_rectangle_filled(250, 550, 280, 320, (255, 255, 255))
        arcade.draw_lrbt_rectangle_outline(250, 550, 280, 320, c2, 3)
        txt2 = (self.s2 if self.s2 else "Игрок 2") + ("|" if self.active == 2 and self.cursor else "")
        Config.draw_text(f"Игрок 2: {txt2}", 260, 300, (0, 0, 0), 16, anchor_y="center")

        # Кнопка "Подключить"
        btn_l = self.btn['x']
        btn_r = self.btn['x'] + self.btn['w']
        btn_b = self.btn['y']
        btn_t = self.btn['y'] + self.btn['h']
        arcade.draw_lrbt_rectangle_filled(btn_l, btn_r, btn_b, btn_t, (100, 200, 100))
        Config.draw_text("Подключить", 400, 205, (255, 255, 255), 18, anchor_x="center", anchor_y="center")

        # Кнопка "Пропустить"
        skip_l = self.skip['x']
        skip_r = self.skip['x'] + self.skip['w']
        skip_b = self.skip['y']
        skip_t = self.skip['y'] + self.skip['h']
        arcade.draw_lrbt_rectangle_filled(skip_l, skip_r, skip_b, skip_t, (150, 150, 200))
        Config.draw_text("Пропустить", 400, 140, (255, 255, 255), 16, anchor_x="center", anchor_y="center")

    # ✅ ИСПРАВЛЕНО: параметр называется text, а не t
    def on_text(self, text):
        if self.active == 1:
            self.s1 += text  # ✅ Используем text вместо t
        else:
            self.s2 += text  # ✅ Используем text вместо t

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
        if 250 <= x <= 550 and 350 <= y <= 390:
            self.active = 1
            return None
        elif 250 <= x <= 550 and 280 <= y <= 320:
            self.active = 2
            return None
        if self.btn['x'] <= x <= self.btn['x'] + self.btn['w'] and self.btn['y'] <= y <= self.btn['y'] + self.btn['h']:
            return "connect"
        if self.skip['x'] <= x <= self.skip['x'] + self.skip['w'] and self.skip['y'] <= y <= self.skip['y'] + self.skip[
            'h']:
            return "skip"
        return None