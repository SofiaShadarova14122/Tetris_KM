# Tetris_KM/games/Fishing/game.py
import arcade, random, os
from config import Config


def load_tex(p):
    if os.path.exists(p):
        try:
            return arcade.load_texture(p)
        except:
            pass
    return None


class Bear:
    def __init__(self, x, y, id):
        self.x, self.y = x, y
        self.id = id
        self.w, self.h = 80, 70
        self.speed = 150
        self.stun = 0.0
        self.facing = "idle"
        self.color = Config.P1_COLOR if id == 1 else Config.P2_COLOR
        self.health = 10
        self.tex = {}
        base = "games/Fishing/assets/images"
        for s in ["idle", "left", "right", "up", "stunned"]:
            t = load_tex(os.path.join(base, f"bear_{s}.png"))
            if t: self.tex[s] = t

    def update(self, dt, a, l, r):
        if self.stun > 0:
            self.stun -= dt
            self.facing = "stunned"
            return
        if a['left']:
            self.x -= self.speed * dt; self.facing = "left"
        elif a['right']:
            self.x += self.speed * dt; self.facing = "right"
        else:
            self.facing = "idle"
        if a['up']: self.facing = "up"
        self.x = max(l + self.w // 2, min(r - self.w // 2, self.x))

    def draw(self):
        c = Config.P1_COLOR if self.id == 1 else Config.P2_COLOR
        arcade.draw_lrbt_rectangle_filled(self.x - 40, self.x + 40, self.y - 45, self.y - 35, c)
        t = self.tex.get(self.facing)
        if t:
            s = arcade.Sprite();
            s.texture = t;
            s.center_x, s.center_y = self.x, self.y
            s.width, s.height = self.w, self.h;
            arcade.draw_sprite(s)
        else:
            arcade.draw_lrbt_rectangle_filled(self.x - 30, self.x + 30, self.y - 30, self.y + 30, self.color)
        # Health bar
        hw, hh = 60, 8
        arcade.draw_lrbt_rectangle_filled(self.x - hw // 2, self.x + hw // 2, self.y + 45, self.y + 45 + hh,
                                          (100, 100, 100))
        arcade.draw_lrbt_rectangle_filled(self.x - hw // 2, self.x - hw // 2 + hw * (self.health / 10), self.y + 45,
                                          self.y + 45 + hh, (0, 255, 0) if self.health > 3 else (255, 0, 0))


class Fish:
    def __init__(self, x, y, speed, sid, fugu=False, gold=False):
        self.x, self.y = x, y
        self.speed = speed
        self.sid = sid
        self.fugu = fugu
        self.gold = gold
        self.active = True
        base = "games/Fishing/assets/images"
        if gold:
            self.tex = load_tex(os.path.join(base, "fish_gold.png"))
        elif fugu:
            self.tex = load_tex(os.path.join(base, "fish_fugu.png"))
        else:
            self.tex = load_tex(os.path.join(base, f"fish_{random.randint(1, 3)}.png"))

    def update(self, dt, yz):
        self.y -= self.speed * dt
        if self.y <= yz:
            self.active = False
            return "lost"
        return None

    def draw(self):
        if self.tex:
            s = arcade.Sprite();
            s.texture = self.tex;
            s.center_x, s.center_y = self.x, self.y
            s.width, s.height = 40, 25;
            arcade.draw_sprite(s)
        else:
            c = (255, 215, 0) if self.gold else (255, 100, 100) if self.fugu else (100, 200, 255)
            arcade.draw_circle_filled(self.x, self.y, 15, c)


class FishingGame:
    def __init__(self):
        self.W, self.H = 1200, 950
        self.FW = 1000
        self.FX = (self.W - self.FW) // 2
        self.FY_TOP = 900
        self.FY_BOT = 100
        self.YZ = 250  # Yellow zone

        self.bears = [Bear(self.FX + 250, self.YZ + 80, 1), Bear(self.FX + self.FW - 250, self.YZ + 80, 2)]
        self.fish = []
        self.spawn_t = 0
        self.score = 0
        self.rounds = 0
        self.max_rounds = 5
        self.paused = False
        self.show_rules = True
        self.game_over = False
        self.winner = ""
        self.bg = load_tex("games/Fishing/assets/images/field.png")

    def update(self, dt, a1, a2):
        if self.paused or self.game_over or self.show_rules: return

        self.bears[0].update(dt, a1, self.FX, self.FX + self.FW)
        self.bears[1].update(dt, a2, self.FX, self.FX + self.FW)

        self.spawn_t += dt
        if self.spawn_t > 1.2:
            self.spawn_t = 0
            sid = random.randint(0, 3)
            xs = [self.FX + 150, self.FX + 400, self.FX + 600, self.FX + 850][sid]
            self.fish.append(Fish(xs, self.FY_TOP, random.randint(80, 140), sid,
                                  random.random() < 0.1, random.random() < 0.05))

        for f in self.fish[:]:
            st = f.update(dt, self.YZ)
            if st == "lost":
                self.fish.remove(f)
                idx = 0 if f.sid < 2 else 1
                self.bears[idx].health -= 1
                if self.bears[idx].health <= 0:
                    self.rounds += 1
                    self._check_win()
                continue

            for i, b in enumerate(self.bears):
                if b.stun > 0: continue
                dx, dy = f.x - b.x, f.y - b.y
                if (dx * dx + dy * dy) ** 0.5 < 50:  # Catch radius
                    if f.gold:
                        self.score += 100
                    elif f.fugu:
                        self.score = max(0, self.score - 10); b.stun = 3.0
                    else:
                        self.score += 10
                    self.fish.remove(f)
                    break

    def _check_win(self):
        if self.rounds >= self.max_rounds:
            self.game_over = True
            h1, h2 = self.bears[0].health, self.bears[1].health
            if h1 > h2:
                self.winner = "Игрок 1 (🔴)!"
            elif h2 > h1:
                self.winner = "Игрок 2 (🔵)!"
            else:
                self.winner = "Ничья!"

    def draw(self):
        if self.bg:
            s = arcade.Sprite();
            s.texture = self.bg;
            s.center_x, s.center_y = self.W // 2, self.H // 2
            s.width, s.height = 1000, 750;
            arcade.draw_sprite(s)
        else:
            arcade.set_background_color((210, 210, 215))
            arcade.draw_lrbt_rectangle_filled(self.FX, self.FX + self.FW, self.FY_BOT, self.FY_TOP, (220, 240, 255))

        # Score (semi-transparent, behind sprites)
        arcade.draw_lrbt_rectangle_filled(400, 640, 450, 530, (255, 255, 255, 180))
        arcade.draw_lrbt_rectangle_outline(400, 640, 450, 530, (150, 150, 150), 2)
        arcade.draw_text(f"{self.bears[0].health} : {self.bears[1].health}", 520, 490, (50, 50, 50), 36,
                         anchor_x="center")

        for f in self.fish: f.draw()
        for b in self.bears: b.draw()

        if self.paused:
            arcade.draw_lrbt_rectangle_filled(0, self.W, 0, self.H, (0, 0, 0, 180))
            Config.draw_text("ПАУЗА", self.W // 2, self.H // 2, (255, 255, 255), 36)

        if self.show_rules:
            arcade.draw_lrbt_rectangle_filled(0, self.W, 0, self.H, (241, 241, 241, 240))
            Config.draw_text("ПРАВИЛА: РЫБАЛКА", self.W // 2, self.H // 2 + 150, (40, 40, 40), 32)
            rules = ["A/D или ←/→ - движение", "Рыба ловится автоматически при касании",
                     "💥 Фугу: -10 очков, ⭐ Золотая: +100", "5 раундов. Больше здоровья = победа!",
                     "", "ENTER - старт", "ESC - меню"]
            for i, r in enumerate(rules):
                c = (0, 100, 0) if "ENTER" in r or "ESC" in r else (60, 60, 60)
                Config.draw_text(r, self.W // 2, self.H // 2 + 100 - i * 30, c, 16)

        if self.game_over:
            arcade.draw_lrbt_rectangle_filled(0, self.W, 0, self.H, (240, 240, 240, 230))
            Config.draw_text("ИГРА ОКОНЧЕНА", self.W // 2, self.H // 2 + 60, (50, 50, 50), 40)
            Config.draw_text(self.winner, self.W // 2, self.H // 2,
                             Config.P1_COLOR if "1" in self.winner else Config.P2_COLOR, 32)
            Config.draw_text(f"Счёт: {self.score}", self.W // 2, self.H // 2 - 50, (80, 80, 80), 24)

    def toggle_pause(self):
        if not self.show_rules and not self.game_over: self.paused = not self.paused

    def start(self):
        self.show_rules = False