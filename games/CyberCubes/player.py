# Tetris_KM/games/CyberCubes/player.py
from .pieces import get_piece
from config import Config


class Player:
    def __init__(self, arena, id):
        self.arena = arena
        self.id = id
        self.color = Config.P1_COLOR if id == 1 else Config.P2_COLOR
        self.base_speed = 1.0
        self.speed = self.base_speed
        self.drop_t = 0.0
        self.pos = {'x': 0, 'y': 0}
        self.matrix = None
        self.score = 0
        self.game_over = False
        self.next = get_piece()
        self.lock = False
        self.move_t = {'l': 0, 'r': 0}
        self.das = 0.18
        self.rep = 0.08
        self.reset()

    def reset(self):
        self.matrix = self.next
        self.next = get_piece()
        self.pos['y'] = 0
        self.pos['x'] = (10 - len(self.matrix[0])) // 2
        if self.arena.collide(self): self.game_over = True

    def move(self, dx):
        if self.game_over: return
        self.pos['x'] += dx
        if self.arena.collide(self): self.pos['x'] -= dx

    def rotate(self, d):
        if self.game_over: return
        orig = [r[:] for r in self.matrix]
        self._rot(d)
        if self.arena.collide(self):
            ox = self.pos['x']
            off = 1
            while self.arena.collide(self):
                self.pos['x'] += off
                off = -(off + (1 if off > 0 else -1))
                if abs(off) > len(self.matrix[0]):
                    self.matrix = orig
                    self.pos['x'] = ox
                    break

    def _rot(self, d):
        n, m = len(self.matrix), len(self.matrix[0])
        t = [[self.matrix[j][i] for j in range(n)] for i in range(m)]
        self.matrix = [r[::-1] for r in t] if d > 0 else t[::-1]

    def update(self, dt, a):
        if self.game_over: return

        # Движение влево
        if a['left']:
            if self.move_t['l'] <= 0:
                self.move(-1)
                self.move_t['l'] = self.das
            self.move_t['l'] -= dt
            if self.move_t['l'] <= -self.rep:
                self.move(-1)
                self.move_t['l'] = 0
        else:
            self.move_t['l'] = 0

        # Движение вправо
        if a['right']:
            if self.move_t['r'] <= 0:
                self.move(1)
                self.move_t['r'] = self.das
            self.move_t['r'] -= dt
            if self.move_t['r'] <= -self.rep:
                self.move(1)
                self.move_t['r'] = 0
        else:
            self.move_t['r'] = 0

        # Поворот
        if a['rotate'] and not self.lock:
            self.rotate(1)
            self.lock = True
        elif not a['rotate']:
            self.lock = False

        # Падение
        spd = 0.05 if a['down'] else self.speed
        self.drop_t += dt
        if self.drop_t >= spd:
            self.drop_t = 0
            self._fall()

    def _fall(self):
        self.pos['y'] += 1
        if self.arena.collide(self):
            self.pos['y'] -= 1
            self._lock()

    def _lock(self):
        self.arena.merge(self)
        lines = self.arena.sweep()
        if lines:
            self.score += lines * 10
            self.speed = max(0.1, 1.0 - (self.score // 100) * 0.05)
        self.reset()