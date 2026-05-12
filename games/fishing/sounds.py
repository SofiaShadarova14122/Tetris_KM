# Tetris_KM/games/fishing/sounds.py
import arcade
import os

class SoundManager:
    def __init__(self):
        self.music = None
        self.catch_sound = None
        self.miss_sound = None
        self._load_sounds()

    def _load_sounds(self):
        base = "games/fishing/assets/sounds"
        music_path = os.path.join(base, "bg_music.mp3")
        catch_path = os.path.join(base, "catch.wav")
        miss_path = os.path.join(base, "miss.wav")

        if os.path.exists(music_path):
            try:
                self.music = arcade.Sound(music_path, streaming=True)
            except Exception as e:
                print(f"Музыка не загружена: {e}")
        if os.path.exists(catch_path):
            try:
                self.catch_sound = arcade.load_sound(catch_path)
            except Exception as e:
                print(f"Звук поимки не загружен: {e}")
        if os.path.exists(miss_path):
            try:
                self.miss_sound = arcade.load_sound(miss_path)
            except Exception as e:
                print(f"Звук пропуска не загружен: {e}")

    def play_music(self):
        if self.music:
            self.music.play(volume=0.5, loop=True)

    def play_catch(self):
        if self.catch_sound:
            arcade.play_sound(self.catch_sound, volume=0.6)

    def play_miss(self):
        if self.miss_sound:
            arcade.play_sound(self.miss_sound, volume=0.4)