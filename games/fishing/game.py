# Tetris_KM/games/Fishing/game.py
import arcade
import random
import os
from config import Config


def load_texture_safe(path):
    if os.path.exists(path):
        try:
            return arcade.load_texture(path)
        except:
            pass
    return None


class Bear:
    def __init__(self, x, y, player_id):
        self.x, self.y = x, y
        self.player_id = player_id
        self.width, self.height = 80, 70
        self.speed = 150
        self.stun_timer = 0.0
        self.facing = "idle"
        self.color = Config.P1_COLOR if player_id == 1 else Config.P2_COLOR

        base = "games/Fishing/assets/images"
        self.textures = {}
        for state in ["idle", "left", "right", "up", "up_left", "up_right", "stunned"]:
            t = load_texture_safe(os.path.join(base, f"bear_{state}.png"))
            if t: self.textures[state] = t

    def update(self, dt, actions, field_left, field_right):
        if self.stun_timer > 0:
            self.stun_timer -= dt
            self.facing = "stunned"
            return

        # Исправленная логика поворота
        if actions.get('up'):
            if actions.get('left'):
                self.facing = "up_left"
            elif actions.get('right'):
                self.facing = "up_right"
            else:
                self.facing = "up"
        elif actions.get('left'):
            self.facing = "left"
        elif actions.get('right'):
            self.facing = "right"
        else:
            self.facing = "idle"

        # Движение
        if actions.get('left'):
            self.x -= self.speed * dt
        elif actions.get('right'):
            self.x += self.speed * dt

        self.x = max(field_left + self.width // 2, min(field_right - self.width // 2, self.x))

    def draw(self):
        # Полоска под медведем
        strip_color = Config.P1_STRIP_COLOR if self.player_id == 1 else Config.P2_STRIP_COLOR
        arcade.draw_lrbt_rectangle_filled(self.x - 40, self.x + 40, self.y - 45, self.y - 35, strip_color)

        tex = self.textures.get(self.facing)
        if tex:
            sprite = arcade.Sprite()
            sprite.texture = tex
            sprite.center_x, sprite.center_y = self.x, self.y
            sprite.width, sprite.height = self.width, self.height
            arcade.draw_sprite(sprite)
        else:
            # Если текстуры нет, рисуем круг
            if self.facing == "stunned":
                arcade.draw_circle_filled(self.x, self.y, 35, (200, 200, 200))
                Config.draw_text("💥", self.x, self.y, (0, 0, 0), 20, anchor_x="center", anchor_y="center")
            else:
                arcade.draw_lrbt_rectangle_filled(self.x - 30, self.x + 30, self.y - 30, self.y + 30, self.color)

        # Индикатор оглушения (таймер)
        if self.stun_timer > 0:
            remaining = self.stun_timer / 3.0
            arcade.draw_lrbt_rectangle_filled(self.x - 40, self.x - 40 + (80 * remaining),
                                              self.y - 50, self.y - 45, (255, 100, 100))


class Fish:
    def __init__(self, x, y, speed, stream_id, is_fugu=False):
        self.x, self.y = x, y
        self.speed = speed
        self.stream_id = stream_id
        self.is_fugu = is_fugu
        self.active = True

        base = "games/Fishing/assets/images"
        if is_fugu:
            self.tex = load_texture_safe(os.path.join(base, "fish_fugu.png"))
        else:
            idx = random.randint(1, 3)
            self.tex = load_texture_safe(os.path.join(base, f"fish_{idx}.png"))

    def update(self, dt, yellow_zone_y):
        self.y -= self.speed * dt
        if self.y <= yellow_zone_y:
            self.active = False
            return "lost"
        return None

    def draw(self):
        if self.tex:
            sprite = arcade.Sprite()
            sprite.texture = self.tex
            sprite.center_x, sprite.center_y = self.x, self.y
            sprite.width, sprite.height = 40, 25
            arcade.draw_sprite(sprite)
        else:
            color = (255, 255, 0) if self.is_fugu else (100, 200, 255)
            arcade.draw_circle_filled(self.x, self.y, 15, color)


class FishingGame:
    def __init__(self):
        self.W, self.H = 1200, 950
        self.field_w = 1000
        self.field_x = (self.W - self.field_w) // 2
        self.field_y_top = 900
        self.field_y_bottom = 100
        self.yellow_zone_y = 250

        self.bears = [
            Bear(self.field_x + 250, self.yellow_zone_y + 80, 1),
            Bear(self.field_x + self.field_w - 250, self.yellow_zone_y + 80, 2)
        ]

        self.fishes = []
        self.spawn_timer = 0
        self.score = 0
        self.lives = 20
        self.paused = False
        self.game_over = False

        self.bg_tex = load_texture_safe("games/Fishing/assets/images/field_shared.png")

        # ✅ ИСПРАВЛЕНО: Простой таймер для эффекта поимки (без arcade.get_time)
        self.catch_effect_timer = 0.0
        self.catch_effect_pos = (0, 0)

    def update(self, dt, p1_actions, p2_actions):
        if self.paused or self.game_over: return

        self.bears[0].update(dt, p1_actions, self.field_x, self.field_x + self.field_w)
        self.bears[1].update(dt, p2_actions, self.field_x, self.field_x + self.field_w)

        self.spawn_timer += dt
        if self.spawn_timer > 1.2:
            self.spawn_timer = 0
            stream = random.randint(0, 3)
            if stream == 0:
                x = self.field_x + 150
            elif stream == 1:
                x = self.field_x + 400
            elif stream == 2:
                x = self.field_x + 600
            else:
                x = self.field_x + 850

            y = self.field_y_top
            speed = random.randint(80, 140)
            is_fugu = random.random() < 0.12
            self.fishes.append(Fish(x, y, speed, stream, is_fugu))

        for fish in self.fishes[:]:
            status = fish.update(dt, self.yellow_zone_y)
            if status == "lost":
                self.fishes.remove(fish)
                self.lives -= 1
                if self.lives <= 0: self.game_over = True
                continue

            for bear in self.bears:
                if bear.stun_timer > 0: continue
                dx = fish.x - bear.x
                dy = fish.y - bear.y
                dist = (dx ** 2 + dy ** 2) ** 0.5

                if dist < 60 and bear.facing == "up":
                    if fish.is_fugu:
                        bear.stun_timer = 3.0
                    else:
                        self.score += 10
                        # ✅ ИСПРАВЛЕНО: Просто запускаем таймер и запоминаем позицию
                        self.catch_effect_timer = 0.5
                        self.catch_effect_pos = (fish.x, fish.y)
                    self.fishes.remove(fish)
                    break

        # Обновляем таймер эффекта
        if self.catch_effect_timer > 0:
            self.catch_effect_timer -= dt

    def draw(self):
        # Увеличенный фон
        if self.bg_tex:
            sprite = arcade.Sprite()
            sprite.texture = self.bg_tex
            sprite.center_x, sprite.center_y = self.W // 2, self.H // 2
            sprite.width = 1000
            sprite.height = 750
            arcade.draw_sprite(sprite)
        else:
            arcade.set_background_color((200, 230, 255))
            arcade.draw_lrbt_rectangle_filled(self.field_x, self.field_x + self.field_w,
                                              self.field_y_bottom, self.field_y_top, (220, 240, 255))

        for f in self.fishes: f.draw()
        for b in self.bears: b.draw()

        # Улучшенный UI
        Config.draw_text(f"СЧЕТ: {self.score}", self.W - 150, self.H - 50, (0, 100, 0), 28, anchor_x="right")

        # Жизни в виде сердечек
        hearts_x = 20
        hearts_y = self.H - 50
        for i in range(self.lives):
            arcade.draw_circle_filled(hearts_x + i * 30, hearts_y, 10, (255, 100, 100))
            arcade.draw_circle_filled(hearts_x + i * 30 - 8, hearts_y + 5, 8, (255, 100, 100))
            arcade.draw_circle_filled(hearts_x + i * 30 + 8, hearts_y + 5, 8, (255, 100, 100))
            arcade.draw_polygon_filled([(hearts_x + i * 30, hearts_y + 25),
                                        (hearts_x + i * 30 - 12, hearts_y + 10),
                                        (hearts_x + i * 30 + 12, hearts_y + 10)], (255, 100, 100))

        # ✅ ИСПРАВЛЕНО: Эффект пойманной рыбы через простой таймер
        if self.catch_effect_timer > 0:
            alpha = int(255 * (self.catch_effect_timer / 0.5))
            x, y = self.catch_effect_pos
            arcade.draw_circle_filled(x, y, 30, (255, 215, 0, alpha))
            Config.draw_text("+10", x, y, (255, 215, 0), 20, anchor_x="center", anchor_y="center")

        if self.game_over:
            arcade.draw_lrbt_rectangle_filled(0, self.W, 0, self.H, (241, 241, 241, 230))
            Config.draw_text("GAME OVER", self.W // 2, self.H // 2 + 60, (255, 0, 0), 40, anchor_x="center")
            Config.draw_text(f"Итоговый счет: {self.score}", self.W // 2, self.H // 2, (0, 0, 0), 28, anchor_x="center")

            if self.score >= 500:
                rank = "🏆 МАСТЕР РЫБАЛКИ!"
            elif self.score >= 300:
                rank = "⭐ ОТЛИЧНЫЙ РЕЗУЛЬТАТ!"
            elif self.score >= 100:
                rank = "👍 ХОРОШАЯ ИГРА!"
            else:
                rank = "🎣 ПОПРОБУЙ ЕЩЕ РАЗ!"
            Config.draw_text(rank, self.W // 2, self.H // 2 - 50, (100, 100, 100), 20, anchor_x="center")

    def toggle_pause(self):
        self.paused = not self.paused