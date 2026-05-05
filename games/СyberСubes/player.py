# Tetris_KM/games/СyberСubes/player.py
from .pieces import get_random_piece

class Player:
    def __init__(self, arena):
        self.arena = arena
        self.DROP_FAST = 0.05          # ← ВОССТАНОВЛЕНО
        self.normal_drop_interval = 1.0  # ← ВОССТАНОВЛЕНО
        self.drop_interval = self.normal_drop_interval
        self.drop_counter = 0.0
        self.pos = {'x': 0, 'y': 0}
        self.matrix = None
        self.score = 0
        self.lines_cleared = 0
        self.game_over = False
        self.next_piece = get_random_piece()
        self.reset()

    def reset(self):
        self.matrix = self.next_piece
        self.next_piece = get_random_piece()
        self.pos['y'] = 0
        self.pos['x'] = (self.arena.width // 2) - (len(self.matrix[0]) // 2)
        if self.arena.collide(self):
            self.game_over = True

    def move(self, dx):
        if self.game_over:
            return
        self.pos['x'] += dx
        if self.arena.collide(self):
            self.pos['x'] -= dx

    def rotate(self, direction):
        if self.game_over:
            return
        original = [row[:] for row in self.matrix]
        self._rotate_matrix(direction)
        if self.arena.collide(self):
            original_x = self.pos['x']
            offset = 1
            while self.arena.collide(self):
                self.pos['x'] += offset
                offset = -(offset + (1 if offset > 0 else -1))
                if abs(offset) > len(self.matrix[0]):
                    self.matrix = original
                    self.pos['x'] = original_x
                    break

    def _rotate_matrix(self, direction):
        n = len(self.matrix)
        m = len(self.matrix[0])
        transposed = [[self.matrix[j][i] for j in range(n)] for i in range(m)]
        if direction > 0:
            self.matrix = [row[::-1] for row in transposed]
        else:
            self.matrix = transposed[::-1]

    def update(self, delta_time):
        if self.game_over:
            return
        self.drop_counter += delta_time
        if self.drop_counter >= self.drop_interval:
            self.drop_counter = 0
            self._try_move_down()

    def _try_move_down(self):
        self.pos['y'] += 1
        if self.arena.collide(self):
            self.pos['y'] -= 1
            self._lock_piece()

    def _lock_piece(self):
        self.arena.merge(self)
        lines = self.arena.sweep()
        if lines > 0:
            self.lines_cleared += lines
            self.score += lines * 10

            # === КЛАССИЧЕСКАЯ СКОРОСТЬ (Game Boy) ===
            level = self.lines_cleared // 10

            if level < 8:
                frames = 48 - level * 5
            elif level == 8:
                frames = 11
            elif level == 9:
                frames = 10
            elif level == 10:
                frames = 9
            elif level == 11:
                frames = 8
            elif level == 12:
                frames = 7
            elif level == 13:
                frames = 6
            elif level == 14:
                frames = 5
            elif level >= 15 and level < 20:
                frames = 4
            else:  # level >= 20
                frames = 3

            self.normal_drop_interval = frames / 60.0  # ← ОБНОВЛЯЕМ НОРМАЛЬНУЮ СКОРОСТЬ
            if self.drop_interval != self.DROP_FAST:
                self.drop_interval = self.normal_drop_interval

        self.reset()

    def drop(self):
        if self.game_over:
            return
        while True:
            self.pos['y'] += 1
            if self.arena.collide(self):
                self.pos['y'] -= 1
                break
        self._lock_piece()