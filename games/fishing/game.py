# Tetris_KM/games/Fishing/game.py
import arcade
import random
import os
from config import Config


def load_texture_safe(path):
    if os.path.exists(path):
        try:
            tex = arcade.load_texture(path)
            return tex
        except:
            pass
    return None


def load_animation_frames(base_path, prefix, count=6):
    frames = []
    for i in range(count):
        path = os.path.join(base_path, f"{prefix}_{i}.png")
        tex = load_texture_safe(path)
        if tex is None: return None
        frames.append(tex)
    return frames


class Bear:
    def __init__(self, x, y, player_id):
        self.x, self.y = x, y
        self.player_id = player_id
        self.width, self.height = 80, 70
        self.speed = 150
        self.stun_timer = 0.0
        self.facing = "idle"
        self.color = Config.P1_COLOR if player_id == 1 else Config.P2_COLOR
        self.health = 10
        self.max_health = 10

        self.walk_frames_left = None
        self.walk_frames_right = None
        self.anim_timer = 0.0
        self.anim_frame = 0
        self.is_moving = False

        base = "games/Fishing/assets/images"
        self.walk_frames_left = load_animation_frames(base, "bear_walk_left", 6)
        self.walk_frames_right = load_animation_frames(base, "bear_walk_right", 6)

        self.static_textures = {}
        for state in ["idle", "left", "right", "up", "up_left", "up_right", "stunned"]:
            t = load_texture_safe(os.path.join(base, f"bear_{state}.png"))
            if t: self.static_textures[state] = t

    def update(self, dt, actions, field_left, field_right):
        if self.stun_timer > 0:
            self.stun_timer -= dt
            self.facing = "stunned"
            self.is_moving = False
            return

        was_moving = self.is_moving
        self.is_moving = actions.get('left') or actions.get('right')

        if actions.get('left'):
            self.x -= self.speed * dt
            self.facing = "left"
        elif actions.get('right'):
            self.x += self.speed * dt
            self.facing = "right"
        else:
            self.facing = "idle"

        self.x = max(field_left + self.width // 2, min(field_right - self.width // 2, self.x))

        if self.is_moving:
            self.anim_timer += dt
            if self.anim_timer >= 0.1:
                self.anim_timer = 0
                self.anim_frame = (self.anim_frame + 1) % 6
        elif was_moving != self.is_moving:
            self.anim_frame = 0

    def draw(self):
        strip_color = Config.P1_STRIP_COLOR if self.player_id == 1 else Config.P2_STRIP_COLOR
        arcade.draw_lrbt_rectangle_filled(self.x - 40, self.x + 40, self.y - 45, self.y - 35, strip_color)

        tex = None
        if self.is_moving and self.facing in ['left', 'right']:
            if self.facing == 'left' and self.walk_frames_left:
                tex = self.walk_frames_left[self.anim_frame]
            elif self.facing == 'right' and self.walk_frames_right:
                tex = self.walk_frames_right[self.anim_frame]

        if tex is None:
            tex = self.static_textures.get(self.facing)

        if tex:
            sprite = arcade.Sprite()
            sprite.texture = tex
            sprite.center_x, sprite.center_y = self.x, self.y
            sprite.width, sprite.height = self.width, self.height
            arcade.draw_sprite(sprite)
        else:
            if self.facing == "stunned":
                arcade.draw_circle_filled(self.x, self.y, 35, (200, 200, 200))
                Config.draw_text("💥", self.x, self.y, (0, 0, 0), 20, anchor_x="center", anchor_y="center")
            else:
                arcade.draw_lrbt_rectangle_filled(self.x - 30, self.x + 30, self.y - 30, self.y + 30, self.color)

        bar_width = 60
        bar_height = 8
        health_ratio = self.health / self.max_health
        arcade.draw_lrbt_rectangle_filled(self.x - bar_width // 2, self.x + bar_width // 2,
                                          self.y + 45, self.y + 45 + bar_height, (100, 100, 100))
        arcade.draw_lrbt_rectangle_filled(self.x - bar_width // 2, self.x - bar_width // 2 + (bar_width * health_ratio),
                                          self.y + 45, self.y + 45 + bar_height,
                                          (0, 255, 0) if health_ratio > 0.3 else (255, 0, 0))


class Fish:
    def __init__(self, x, y, speed, stream_id, is_fugu=False, is_golden=False):
        self.x, self.y = x, y
        self.speed = speed
        self.stream_id = stream_id
        self.is_fugu = is_fugu
        self.is_golden = is_golden
        self.active = True

        base = "games/Fishing/assets/images"
        if is_golden:
            self.tex = load_texture_safe(os.path.join(base, "fish_golden.png"))
        elif is_fugu:
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
            color = (255, 215, 0) if self.is_golden else (255, 100, 100) if self.is_fugu else (100, 200, 255)
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
        self.combo = 0
        self.consecutive_catches = 0
        self.multiplier = 1
        self.golden_fish_timer = 0
        self.game_time = 0
        self.paused = False
        self.show_rules = True
        self.game_over = False
        self.winner = None

        self.bg_tex = load_texture_safe("games/Fishing/assets/images/field_shared.png")
        self.catch_effect_timer = 0.0
        self.catch_effect_pos = (0, 0)

    def update(self, dt, p1_actions, p2_actions):
        if self.paused or self.game_over or self.show_rules: return

        self.game_time += dt
        self.golden_fish_timer += dt

        if self.golden_fish_timer >= 30 and not any(f.is_golden for f in self.fishes):
            self.golden_fish_timer = 0
            x = random.randint(self.field_x + 100, self.field_x + self.field_w - 100)
            self.fishes.append(Fish(x, self.field_y_top, 200, random.randint(0, 3), is_golden=True))

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
            is_fugu = random.random() < 0.1
            self.fishes.append(Fish(x, y, speed, stream, is_fugu=is_fugu))

        for fish in self.fishes[:]:
            status = fish.update(dt, self.yellow_zone_y)

            if status == "lost":
                self.fishes.remove(fish)
                player_idx = 0 if fish.stream_id < 2 else 1
                self.bears[player_idx].health -= 1
                self.combo = 0
                self.multiplier = 1
                if self.bears[player_idx].health <= 0:
                    self.game_over = True
                    self.winner = 2 if player_idx == 0 else 1
                continue

            for bear_idx, bear in enumerate(self.bears):
                if bear.stun_timer > 0: continue
                dx = fish.x - bear.x
                dy = fish.y - bear.y
                dist = (dx ** 2 + dy ** 2) ** 0.5

                if dist < 50:
                    if fish.is_golden:
                        self.score += 100 * self.multiplier
                        self.catch_effect_timer = 0.5
                        self.catch_effect_pos = (fish.x, fish.y)
                    elif fish.is_fugu:
                        self.score -= 10
                        self.combo = 0
                        self.multiplier = 1
                    else:
                        points = 10 * self.multiplier
                        self.score += points
                        self.consecutive_catches += 1
                        if self.consecutive_catches >= 3: self.multiplier = 2
                        self.catch_effect_timer = 0.5
                        self.catch_effect_pos = (fish.x, fish.y)
                    self.fishes.remove(fish)
                    break

        if self.catch_effect_timer > 0:
            self.catch_effect_timer -= dt

    def draw(self):
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

        # ✅ ЖЕЛТАЯ ЗОНА ПОЛНОСТЬЮ СКРЫТА (удалена отрисовка)

        for f in self.fishes: f.draw()
        for b in self.bears: b.draw()

        Config.draw_text(f"СЧЕТ: {self.score}", self.W - 150, self.H - 50, (0, 100, 0), 28, anchor_x="right")
        if self.multiplier > 1:
            Config.draw_text(f"x{self.multiplier} COMBO!", self.W // 2, self.H - 50, (255, 215, 0), 24,
                             anchor_x="center")

        time_to_golden = 30 - self.golden_fish_timer
        Config.draw_text(f"🐟 {int(time_to_golden)}с", self.W // 2, self.H - 80, (255, 215, 0), 18, anchor_x="center")

        if self.catch_effect_timer > 0:
            alpha = int(255 * (self.catch_effect_timer / 0.5))
            x, y = self.catch_effect_pos
            arcade.draw_circle_filled(x, y, 30, (255, 215, 0, alpha))
            Config.draw_text("+10", x, y, (255, 215, 0), 20, anchor_x="center", anchor_y="center")

        if self.paused:
            arcade.draw_lrbt_rectangle_filled(0, self.W, 0, self.H, (0, 0, 0, 180))
            Config.draw_text("ПАУЗА", self.W // 2, self.H // 2, (255, 255, 255), 36, anchor_x="center")
            Config.draw_text("P - Продолжить | ESC - Меню", self.W // 2, self.H // 2 - 50, (200, 200, 200), 18,
                             anchor_x="center")

        if self.show_rules:
            arcade.draw_lrbt_rectangle_filled(0, self.W, 0, self.H, (241, 241, 241, 240))
            Config.draw_text("ПРАВИЛА ИГРЫ", self.W // 2, self.H // 2 + 150, (40, 40, 40), 32, anchor_x="center")
            rules = [
                "🎣 Двигайтесь влево/вправо: A/D или ←/→",
                "🤝 РЫБА ЛОВИТСЯ АВТОМАТИЧЕСКИ при касании!",
                "💚 У каждого игрока своя база здоровья",
                "⚠️ Не дайте рыбе упасть ниже медведей!",
                "💥 Фугу: -10 очков", "🏆 3 рыбы подряд = x2 множитель",
                "⭐ Золотая рыба каждые 30с (+100)", "🤝 Если игрок оглушен - ловите за двоих!",
                "", "Побеждает тот, кто дольше продержится!", "",
                "ENTER - Начать игру | ESC - В меню выбора"
            ]
            for i, rule in enumerate(rules):
                color = (0, 100, 0) if "ENTER" in rule or "ESC" in rule else (60, 60, 60)
                Config.draw_text(rule, self.W // 2, self.H // 2 + 100 - i * 30, color, 16, anchor_x="center")

        if self.game_over:
            arcade.draw_lrbt_rectangle_filled(0, self.W, 0, self.H, (241, 241, 241, 230))
            Config.draw_text("ИГРА ОКОНЧЕНА", self.W // 2, self.H // 2 + 60, (255, 0, 0), 40, anchor_x="center")
            winner_text = f"🏆 Игрок {self.winner} победил!" if self.winner else "Ничья!"
            Config.draw_text(winner_text, self.W // 2, self.H // 2, (0, 100, 0), 28, anchor_x="center")
            Config.draw_text(f"Финальный счет: {self.score}", self.W // 2, self.H // 2 - 50, (0, 0, 0), 24,
                             anchor_x="center")
            Config.draw_text("Нажмите ESC для выхода в меню", self.W // 2, self.H // 2 - 100, (100, 100, 100), 18,
                             anchor_x="center")

    def toggle_pause(self):
        if not self.show_rules and not self.game_over: self.paused = not self.paused

    def start_game(self):
        self.show_rules = False