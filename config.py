# Tetris_KM/config.py
import os
import arcade


class Config:
    # Шрифты (Roboto или системный аналог)
    FONT_NAME = "Roboto-Regular.ttf"  # Убедись, что файл есть в папке assets/fonts/
    FONT_PATH = os.path.join("assets", "fonts", FONT_NAME)

    # Если файла нет, arcade попытается найти системный, но лучше положить файл рядом с main.py
    # Для надежности используем дефолт, если файла нет:
    try:
        arcade.load_font(FONT_PATH)
        FONT_FAMILY = "Roboto"
    except:
        FONT_FAMILY = "Arial"

    # Цвета игроков
    P1_COLOR = (0, 150, 255)  # Синий
    P1_BG_COLOR = (200, 230, 255)  # Светло-синий фон
    P1_STRIP_COLOR = (0, 100, 200)  # Полоска под медведем

    P2_COLOR = (255, 50, 50)  # Красный
    P2_BG_COLOR = (255, 200, 200)  # Светло-красный фон
    P2_STRIP_COLOR = (200, 50, 50)  # Полоска под медведем

    GENERAL_COLORS = [
        (0, 0, 0),
        (255, 100, 100), (100, 200, 255), (100, 255, 150),
        (200, 100, 255), (255, 200, 100), (255, 150, 100), (150, 150, 255)
    ]

    @staticmethod
    def draw_text(text, x, y, color, size=16, anchor_x="left", anchor_y="bottom"):
        try:
            arcade.draw_text(text, x, y, color, font_size=size, font_name=Config.FONT_FAMILY,
                             anchor_x=anchor_x, anchor_y=anchor_y)
        except Exception:
            arcade.draw_text(text, x, y, color, font_size=size, anchor_x=anchor_x, anchor_y=anchor_y)