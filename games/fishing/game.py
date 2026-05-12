# Tetris_KM/games/fishing/game.py
import arcade
import random
import os

MAX_LIVES = 10
TEXTURE_SIZE = 80


def load_texture_safe(path):
    if os.path.exists(path):
        try:
            return arcade.load_texture(path)
        except:
            pass
    return None


def draw_entity(texture, x, y, w, h, flip_h=False):
    if texture is None: return
    sprite = arcade.Sprite()
    sprite.texture = texture
    sprite.center_x, sprite.center_y = x, y
    sprite.width, sprite.height = w, h
    if flip_h:
        sprite.flip_horizontally = True
    arcade.draw_sprite(sprite)


class Bear:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.width, self.height = 80, 70
        self.facing, self.target_facing = "idle", "idle"
        self.is_reaching, self.score, self.lives = False, 0, MAX_LIVES
        self.game_over, self.rotation_progress = False, 0.0
        self.rotation_speed = 0.15
        self.active_actions = {'left': False, 'right': False, 'up': False, 'down': False}
        base = "games/fishing/assets/images"
        self.textures = {k: load_texture_safe(os.path.join(base, f"bear_{k}.png"))
                         for k in ["idle", "left", "right", "up", "up_left", "up_right"]}

    def set_action(self, action, state):
        if action in self.active_actions: self.active_actions[action] = state

    def update_state(self):
        if self.game_over: return
        self.is_reaching = self.active_actions['up']
        if self.active_actions['up']:
            self.target_facing = "up_left" if self.active_actions['left'] else "up_right" if self.active_actions[
                'right'] else "up"
        else:
            self.target_facing = "left" if self.active_actions['left'] else "right" if self.active_actions[
                'right'] else "idle"

        if self.facing != self.target_facing:
            self.rotation_progress += self.rotation_speed
            if self.rotation_progress >= 1.0: self.facing = self.target_facing; self.rotation_progress = 0.0
        else:
            self.rotation_progress = 0.0

    def draw(self):
        tex = self.textures.get(self.facing)
        if tex:
            draw_entity(tex, self.x, self.y, TEXTURE_SIZE, TEXTURE_SIZE)
        else:
            arcade.draw_lrbt_rectangle_filled(self.x - self.width // 2, self.x + self.width // 2,
                                              self.y - self.height // 2, self.y + self.height // 2, (180, 120, 80))
            eye_x = self.x + (20 if "right" in self.facing else -20 if "left" in self.facing else 0)
            arcade.draw_circle_filled(eye_x, self.y + 15, 6, (0, 0, 0))

    def get_loss_zone(self):
        return self.x - self.width // 2 - 20, self.x + self.width // 2 + 20

    def draw_health(self, x, y):
        for i in range(self.lives): arcade.draw_circle_filled(x + i * 25, y, 8, (255, 215, 0))


class Fish:
    def __init__(self, stream_id, start_x, start_y, end_x, end_y, speed=100, fish_type=1, flip_h=False):
        self.stream_id, self.start_x, self.start_y, self.end_x, self.end_y = stream_id, start_x, start_y, end_x, end_y
        self.progress, self.speed, self.fish_type, self.flip_h = 0.0, speed, fish_type, flip_h
        self.caught, self.sinking, self.sink_speed = False, False, 150

    def update(self, dt, field_bottom):
        if self.sinking:
            self.end_y += self.sink_speed * dt
            return self.end_y > field_bottom
        self.progress += dt * self.speed / 1000
        if self.progress >= 1.0: self.progress = 1.0
        return False

    def get_position(self):
        if self.sinking: return self.end_x, self.end_y
        return self.start_x + (self.end_x - self.start_x) * self.progress, self.start_y + (
                    self.end_y - self.start_y) * self.progress

    def dist_to_zone(self, l, r):
        x, _ = self.get_position()
        return min(abs(x - l), abs(x - r))

    def in_zone(self, l, r):
        x, _ = self.get_position()
        return l <= x <= r

    def draw(self, game):
        x, y = self.get_position()
        tex = game.fish_textures.get(self.fish_type)
        if tex:
            draw_entity(tex, x, y, 40, 25, self.flip_h)
        else:
            arcade.draw_circle_filled(x, y, 12, (255, 100, 100))


class FishingGame:
    def __init__(self):
        self.W, self.H = 1200, 950
        self.FW, self.FH = 480, 600
        # Новые размеры по вашему запросу
        self.lx, self.rx, self.fy = 80, 80 + self.FW + 80, 200
        self.bear1 = Bear(self.lx + self.FW // 2, self.fy + 100)
        self.bear2 = Bear(self.rx + self.FW // 2, self.fy + 100)
        top_y, bottom_y = self.fy + self.FH - 50, self.fy + 50
        self.streams_left = [(self.lx, top_y, self.bear1.x, self.bear1.y + 20),
                             (self.lx + self.FW, top_y, self.bear1.x, self.bear1.y + 20),
                             (self.lx, bottom_y, self.bear1.x, self.bear1.y - 20),
                             (self.lx + self.FW, bottom_y, self.bear1.x, self.bear1.y - 20)]
        self.streams_right = [(self.rx, top_y, self.bear2.x, self.bear2.y + 20),
                              (self.rx + self.FW, top_y, self.bear2.x, self.bear2.y + 20),
                              (self.rx, bottom_y, self.bear2.x, self.bear2.y - 20),
                              (self.rx + self.FW, bottom_y, self.bear2.x, self.bear2.y - 20)]
        self.fishes, self.spawn_timer, self.spawn_interval = [], 0.0, 2.0
        self.paused, self.show_game_over = False, False
        self.bg = load_texture_safe("games/fishing/assets/images/field_background.png")
        self.fish_textures = {}
        for i in range(1, 10):
            tex = load_texture_safe(f"games/fishing/assets/images/fish_{i}.png")
            if tex: self.fish_textures[i] = tex

    def apply_controller_actions(self, actions):
        for b in [self.bear1, self.bear2]:
            for k in b.active_actions: b.active_actions[k] = False
        for p, act in actions:
            if p == 1:
                self.bear1.set_action(act, True)
            elif p == 2:
                self.bear2.set_action(act, True)

    def apply_keyboard_actions(self, actions):
        for p, act in actions:
            if p == 1:
                self.bear1.set_action(act, True)
            elif p == 2:
                self.bear2.set_action(act, True)

    def update(self, dt):
        if self.paused or self.show_game_over: return
        self.bear1.update_state();
        self.bear2.update_state()
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval and len(self.fishes) < 6:
            self.spawn_timer = 0
            is_left = random.choice([True, False])
            sid = random.randint(0, 3)
            s = self.streams_left[sid] if is_left else self.streams_right[sid]
            bear = self.bear1 if is_left else self.bear2
            speed = min(300, 100 + bear.score * 5)
            fish_type = random.choice(list(self.fish_textures.keys())) if self.fish_textures else 1
            # Исправленная инверсия: слева (is_left=True) - не зеркалим, справа - зеркалим
            self.fishes.append(Fish(sid if is_left else sid + 4, *s, speed, fish_type, flip_h=not is_left))
            if (self.bear1.score + self.bear2.score) > 0 and (self.bear1.score + self.bear2.score) % 5 == 0:
                self.spawn_interval = max(0.5, self.spawn_interval * 0.9)

        for fish in self.fishes[:]:
            bear = self.bear1 if fish.stream_id < 4 else self.bear2
            lz, rz = bear.get_loss_zone()
            if not fish.sinking:
                if 1 <= fish.dist_to_zone(lz, rz) <= 30:
                    upper = fish.stream_id in (0, 1, 4, 5)
                    catch = (bear.is_reaching and ((fish.stream_id in (0, 4) and bear.active_actions['left']) or (
                                fish.stream_id in (1, 5) and bear.active_actions['right']))) if upper else \
                        ((fish.stream_id in (2, 6) and bear.active_actions['left']) or (
                                    fish.stream_id in (3, 7) and bear.active_actions['right']))
                    if catch: fish.caught = True; bear.score += 1; self.fishes.remove(fish); continue
                if fish.in_zone(lz, rz): fish.sinking = True
            if fish.update(dt, self.fy + self.FH):
                self.fishes.remove(fish)
                if not fish.caught:
                    bear.lives -= 1
                    if bear.lives <= 0: bear.game_over = True
                    if self.bear1.game_over and self.bear2.game_over: self.show_game_over = True

    def draw(self):
        arcade.set_background_color((220, 240, 255))
        if self.bg:
            draw_entity(self.bg, self.lx + self.FW // 2, self.fy + self.FH // 2, self.FW, self.FH)
            draw_entity(self.bg, self.rx + self.FW // 2, self.fy + self.FH // 2, self.FW, self.FH)
        else:
            arcade.draw_lrbt_rectangle_filled(self.lx, self.lx + self.FW, self.fy, self.fy + self.FH, (217, 217, 217))
            arcade.draw_lrbt_rectangle_filled(self.rx, self.rx + self.FW, self.fy, self.fy + self.FH, (217, 217, 217))
        self.bear1.draw();
        self.bear2.draw()
        for f in self.fishes: f.draw(self)
        hy, sy = self.fy - 40, self.fy + self.FH + 20
        self.bear1.draw_health(self.lx + 20, hy);
        self.bear2.draw_health(self.rx + 20, hy)
        arcade.draw_text(f"Счёт: {self.bear1.score}", self.lx + 20, sy, (0, 0, 0), 14)
        arcade.draw_text(f"Счёт: {self.bear2.score}", self.rx + 20, sy, (0, 0, 0), 14)
        if self.paused:
            arcade.draw_lrbt_rectangle_filled(0, self.W, 0, self.H, (0, 0, 0, 180))
            arcade.draw_text("ПАУЗА", self.W // 2, self.H // 2, (255, 255, 255), 32, anchor_x="center")
            arcade.draw_text("Нажмите ESC/M для выхода в меню", self.W // 2, self.H // 2 - 50, (200, 200, 200), 18,
                             anchor_x="center")
        if self.show_game_over:
            arcade.draw_lrbt_rectangle_filled(0, self.W, 0, self.H, (241, 241, 241))
            arcade.draw_text("ИГРА ОКОНЧЕНА", self.W // 2, self.H // 2 + 60, (40, 40, 40), 32, anchor_x="center")
            w = "Игрок 1 победил!" if self.bear1.score > self.bear2.score else "Игрок 2 победил!" if self.bear2.score > self.bear1.score else "Ничья!"
            arcade.draw_text(w, self.W // 2, self.H // 2, (60, 60, 60), 24, anchor_x="center")
            arcade.draw_text(f"1: {self.bear1.score} | 2: {self.bear2.score}", self.W // 2, self.H // 2 - 40,
                             (40, 40, 40), 18, anchor_x="center")
            arcade.draw_text("Нажмите ESC", self.W // 2, self.H // 2 - 80, (100, 100, 100), 16, anchor_x="center")

    def toggle_pause(self):
        self.paused = not self.paused