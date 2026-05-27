# Tetris_KM/games/fishing/game.py
import arcade
import random
import os
from config import Config


def load_tex(path):
    """Безопасная загрузка текстуры"""
    if os.path.exists(path):
        try:
            return arcade.load_texture(path)
        except:
            pass
    return None


class Bear:
    """Медведь-игрок"""

    def __init__(self, x, y, player_id):
        self.x, self.y = x, y
        self.player_id = player_id
        self.w, self.h = 80, 70
        self.speed = 150
        self.stun = 0.0
        self.facing = "idle"
        self.health = 10
        self.max_health = 10

        self.color = Config.P1_COLOR if player_id == 1 else Config.P2_COLOR
        self.suffix = "red" if player_id == 1 else "blue"

        base = "games/Fishing/assets/images"
        self.tex = {}
        for state in ["idle", "left", "right", "up", "stunned"]:
            path = os.path.join(base, f"bear_{state}_{self.suffix}.png")
            t = load_tex(path)
            if t:
                self.tex[state] = t

    def update(self, dt, actions, field_left, field_right):
        """Обновление позиции и состояния"""
        if self.stun > 0:
            self.stun -= dt
            self.facing = "stunned"
            return

        if actions.get('left'):
            self.x -= self.speed * dt
            self.facing = "left"
        elif actions.get('right'):
            self.x += self.speed * dt
            self.facing = "right"
        else:
            self.facing = "idle"

        if actions.get('up'):
            self.facing = "up"

        self.x = max(field_left + self.w // 2, min(field_right - self.w // 2, self.x))

    def draw(self):
        """Отрисовка медведя"""
        tex = self.tex.get(self.facing)
        if tex:
            sprite = arcade.Sprite()
            sprite.texture = tex
            sprite.center_x, sprite.center_y = self.x, self.y
            sprite.width, sprite.height = self.w, self.h
            arcade.draw_sprite(sprite)
        else:
            arcade.draw_circle_filled(self.x, self.y, 30, (240, 240, 240))
            arcade.draw_circle_outline(self.x, self.y, 32, self.color, 3)

        # Индикатор оглушения
        if self.stun > 0:
            remaining = self.stun / 3.0
            arcade.draw_lrbt_rectangle_filled(
                self.x - 40, self.x - 40 + (80 * remaining),
                self.y - 50, self.y - 45,
                (255, 100, 100)
            )

        # Полоска здоровья над медведем
        bar_w, bar_h = 60, 8
        arcade.draw_lrbt_rectangle_filled(
            self.x - bar_w // 2, self.x + bar_w // 2,
            self.y + 45, self.y + 45 + bar_h,
            (100, 100, 100)
        )
        health_ratio = max(0, self.health / self.max_health)
        health_color = (0, 255, 0) if health_ratio > 0.3 else (255, 100, 100)
        arcade.draw_lrbt_rectangle_filled(
            self.x - bar_w // 2,
            self.x - bar_w // 2 + max(0, bar_w * health_ratio),
            self.y + 45, self.y + 45 + bar_h,
            health_color
        )


class Fish:
    """Рыбка с флагом пересечения зоны потери"""

    def __init__(self, x, y, speed, stream_id, fugu=False, gold=False):
        self.x, self.y = x, y
        self.speed = speed  # Скорость фиксируется при создании
        self.stream_id = stream_id
        self.fugu = fugu
        self.gold = gold
        self.active = True
        self.crossed_loss_zone = False  # Флаг: пересекла ли границу потери

        base = "games/Fishing/assets/images"
        if gold:
            self.tex = load_tex(os.path.join(base, "fish_gold.png"))
        elif fugu:
            self.tex = load_tex(os.path.join(base, "fish_fugu.png"))
        else:
            idx = random.randint(1, 7)
            self.tex = load_tex(os.path.join(base, f"fish_{idx}.png"))

    def update(self, dt, yellow_zone_y, bottom_y):
        """Обновление позиции"""
        self.y -= self.speed * dt

        # Уменьшение здоровья при первом пересечении границы потери
        if not self.crossed_loss_zone and self.y <= yellow_zone_y:
            self.crossed_loss_zone = True
            return "crossed_loss"

        # Удаление рыбы при достижении нижней границы поля
        if self.y <= bottom_y:
            self.active = False
            return "removed"

        return None

    def draw(self):
        """Отрисовка рыбки"""
        if self.tex:
            sprite = arcade.Sprite()
            sprite.texture = self.tex
            sprite.center_x, sprite.center_y = self.x, self.y
            sprite.width, sprite.height = 40, 25
            arcade.draw_sprite(sprite)
        else:
            if self.gold:
                color = (255, 215, 0)
            elif self.fugu:
                color = (255, 100, 100)
            else:
                color = (100, 200, 255)
            arcade.draw_circle_filled(self.x, self.y, 15, color)


class FishingGame:
    """Основной класс игры"""

    def __init__(self):
        # РАЗМЕРЫ ОКНА
        self.W, self.H = 1200, 950

        # ИГРОВОЕ ПОЛЕ
        self.FIELD_W = 900
        self.FIELD_H = 670
        self.FIELD_X = (self.W - self.FIELD_W) // 2
        self.FIELD_Y = 125

        # Границы поля
        self.FX = self.FIELD_X
        self.FY_TOP = self.FIELD_Y + self.FIELD_H
        self.FY_BOT = self.FIELD_Y + 50
        self.YZ = self.FIELD_Y + 200

        # Медведи
        self.bears = [
            Bear(self.FX + 250, self.YZ + 20, 1),
            Bear(self.FX + self.FIELD_W - 250, self.YZ + 20, 2)
        ]

        self.fish = []
        self.spawn_t = 0
        self.spawn_interval = 0.7  # ✅ ЧАЩЕ СПАВН (было 0.9)
        self.score = 0
        self.base_fish_speed = 60
        self.next_speed_score = 80
        self.paused = False
        self.show_rules = True
        self.game_over = False
        self.winner = ""

        self.bg = load_tex("games/Fishing/assets/images/field_light.png")
        self.last_spawn_y = {}

    def update(self, dt, a1, a2):
        """Основной цикл обновления"""
        if self.paused or self.game_over or self.show_rules:
            return

        # ✅ Ускорение строго по очкам (только вперёд)
        if self.score >= self.next_speed_score:
            self.base_fish_speed += 10
            self.next_speed_score += 80
            print(f" Speed UP! Base: {self.base_fish_speed}, Next at: {self.next_speed_score}")

        self.bears[0].update(dt, a1, self.FX, self.FX + self.FIELD_W)
        self.bears[1].update(dt, a2, self.FX, self.FX + self.FIELD_W)

        # Спавн рыб
        self.spawn_t += dt
        if self.spawn_t >= self.spawn_interval:
            self.spawn_t = 0
            sid = random.randint(0, 3)

            # ✅ МЯГЧЕ ПРОВЕРКА: рыбы могут спавниться ближе друг к другу
            last_y = self.last_spawn_y.get(sid, 0)
            if last_y > self.FY_TOP - 80:
                return

            xs = [self.FX + 150, self.FX + 400, self.FX + 600, self.FX + 850][sid]
            is_fugu = random.random() < 0.10
            is_gold = not is_fugu and random.random() < 0.05

            # ✅ УБРАН ОТРИЦАТЕЛЬНЫЙ РАЗБРОС: новые рыбы всегда >= base_fish_speed
            speed = self.base_fish_speed + random.randint(0, 8)

            new_fish = Fish(xs, self.FY_TOP, speed, sid, is_fugu, is_gold)
            self.fish.append(new_fish)
            self.last_spawn_y[sid] = self.FY_TOP

        # Обновление рыб
        for f in self.fish[:]:
            status = f.update(dt, self.YZ, self.FY_BOT)

            if status == "crossed_loss":
                if f.stream_id < 2:
                    self.bears[0].health = max(0, self.bears[0].health - 1)
                else:
                    self.bears[1].health = max(0, self.bears[1].health - 1)
                continue

            if status == "removed":
                self.fish.remove(f)
                continue

            # Проверка поимки
            for b in self.bears:
                if b.stun > 0:
                    continue
                dx, dy = f.x - b.x, f.y - b.y
                dist = (dx * dx + dy * dy) ** 0.5
                if dist < 50:
                    if f.gold:
                        self.score += 100
                        for bear in self.bears:
                            if bear.health < bear.max_health:
                                bear.health += 1
                    elif f.fugu:
                        self.score = max(0, self.score - 10)
                        b.stun = 3.0
                    else:
                        self.score += 10
                    self.fish.remove(f)
                    self.last_spawn_y[f.stream_id] = f.y
                    break

        # Проверка окончания игры
        if self.bears[0].health <= 0 and self.bears[1].health <= 0:
            self.game_over = True
            if self.bears[0].health > self.bears[1].health:
                self.winner = "Игрок 1 (🔴)!"
            elif self.bears[1].health > self.bears[0].health:
                self.winner = "Игрок 2 (🔵)!"
            else:
                self.winner = "Ничья!"

    def draw(self):
        """Отрисовка игры"""
        arcade.set_background_color((240, 245, 250))

        if self.bg:
            sprite = arcade.Sprite()
            sprite.texture = self.bg
            sprite.center_x = self.FIELD_X + self.FIELD_W // 2
            sprite.center_y = self.FIELD_Y + self.FIELD_H // 2
            sprite.width = self.FIELD_W
            sprite.height = self.FIELD_H
            arcade.draw_sprite(sprite)
        else:
            arcade.draw_lrbt_rectangle_filled(
                self.FX, self.FX + self.FIELD_W,
                self.FIELD_Y, self.FY_TOP,
                (220, 240, 255)
            )

        for f in self.fish:
            f.draw()
        for b in self.bears:
            b.draw()

        # UI ПОД ИГРОВЫМ ПОЛЕМ
        ui_y = self.FIELD_Y + self.FIELD_H + 10

        Config.draw_text("🔴 Игрок 1", 105, ui_y + 50, Config.P1_COLOR, 18)
        Config.draw_text(f"❤️ {self.bears[0].health}", 105, ui_y + 25, (0, 150, 0), 20)
        Config.draw_text(f"💥 {int(self.bears[0].stun)}с", 105, ui_y + 5, (150, 150, 150), 12)

        Config.draw_text("🔵 Игрок 2", 1095, ui_y + 50, Config.P2_COLOR, 18)
        Config.draw_text(f"❤️ {self.bears[1].health}", 1095, ui_y + 25, (0, 150, 0), 20)
        Config.draw_text(f"💥 {int(self.bears[1].stun)}с", 1095, ui_y + 5, (150, 150, 150), 12)

        points_to_speed = max(0, self.next_speed_score - self.score)
        Config.draw_text(f"🎣 Счёт: {self.score}", 600, ui_y + 50, (50, 50, 50), 22)
        Config.draw_text(f" {points_to_speed} очков до ускорения", 600, ui_y + 25, (100, 100, 100), 16)

        if self.paused:
            arcade.draw_lrbt_rectangle_filled(0, self.W, 0, self.H, (0, 0, 0, 150))
            Config.draw_text("ПАУЗА", self.W // 2, self.H // 2, (255, 255, 255), 36)

        if self.show_rules:
            arcade.draw_lrbt_rectangle_filled(0, self.W, 0, self.H, (255, 255, 255, 240))
            Config.draw_text("ПРАВИЛА: РЫБАЛКА", self.W // 2, self.H // 2 + 150, (40, 40, 40), 32)
            rules = [
                "🔴 Игрок 1: A/D | 🔵 Игрок 2: ←/→",
                "🎣 Ловля автоматически при касании",
                "💥 Фугу: -10 очков, ⭐ Золотая: +100",
                " Скорость растёт каждые 80 очков",
                "",
                "ENTER - Старт | ESC - Меню"
            ]
            for i, r in enumerate(rules):
                c = (0, 100, 0) if "ENTER" in r or "ESC" in r else (60, 60, 60)
                Config.draw_text(r, self.W // 2, self.H // 2 + 100 - i * 30, c, 16)

        if self.game_over:
            arcade.draw_lrbt_rectangle_filled(0, self.W, 0, self.H, (255, 255, 255, 230))
            Config.draw_text("ИГРА ОКОНЧЕНА", self.W // 2, self.H // 2 + 60, (50, 50, 50), 40)
            wc = Config.P1_COLOR if "1" in self.winner else Config.P2_COLOR
            Config.draw_text(self.winner, self.W // 2, self.H // 2, wc, 32)
            Config.draw_text(f"Счёт: {self.score}", self.W // 2, self.H // 2 - 50, (80, 80, 80), 24)

    def toggle_pause(self):
        if not self.show_rules and not self.game_over:
            self.paused = not self.paused

    def start(self):
        self.show_rules = False
        self.base_fish_speed = 60
        self.next_speed_score = 80
        self.score = 0
        self.bears[0].health = 10
        self.bears[1].health = 10
        self.fish.clear()
        self.last_spawn_y.clear()