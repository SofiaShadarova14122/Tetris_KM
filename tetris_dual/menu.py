# menu.py
import arcade

class MenuState:
    def __init__(self, window_width, window_height):
        self.window_width = window_width
        self.window_height = window_height
        self.start_button = {
            'x': window_width // 2 - 100,
            'y': window_height // 2 - 30,
            'width': 200,
            'height': 60
        }

    def on_draw(self):
        arcade.draw_lrbt_rectangle_filled(0, self.window_width, 0, self.window_height, (241, 241, 241))
        arcade.draw_text("ПАРНЫЙ ТЕТРИС", self.window_width // 2, self.window_height // 2 + 80,
                         (40, 40, 40), 32, anchor_x="center")
        arcade.draw_lrbt_rectangle_filled(
            self.start_button['x'],
            self.start_button['x'] + self.start_button['width'],
            self.start_button['y'],
            self.start_button['y'] + self.start_button['height'],
            (200, 200, 255)
        )
        arcade.draw_text("Начать игру", self.window_width // 2, self.window_height // 2,
                         (30, 30, 30), 20, anchor_x="center")

    def on_mouse_press(self, x, y):
        btn = self.start_button
        if btn['x'] <= x <= btn['x'] + btn['width'] and btn['y'] <= y <= btn['y'] + btn['height']:
            return True
        return False