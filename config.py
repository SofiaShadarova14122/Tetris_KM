# Tetris_KM/config.py
import arcade


class Config:
    # Цвета
    P1_COLOR = (255, 100, 100)  # Красный
    P2_COLOR = (100, 150, 255)  # Синий
    P1_BG = (255, 240, 240)
    P2_BG = (240, 245, 255)

    # Шрифт
    FONT = "Arial"

    @staticmethod
    def draw_text(text, x, y, color, size=16, anchor_x="center", anchor_y="center"):
        try:
            arcade.draw_text(text, x, y, color, font_size=size,
                             font_name=Config.FONT, anchor_x=anchor_x, anchor_y=anchor_y)
        except:
            arcade.draw_text(text, x, y, color, font_size=size,
                             anchor_x=anchor_x, anchor_y=anchor_y)