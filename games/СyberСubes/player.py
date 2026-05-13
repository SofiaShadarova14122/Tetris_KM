# Tetris_KM/games/CyberCubes/player.py
from .pieces import get_random_piece


class Player:
    def __init__(self, arena):
        self.arena = arena
        self.DROP_SLOW = 1.0
        self.DROP_FAST = 0.05
        self.normal_drop_interval = self.DROP_SLOW
        self.drop_interval = self.normal_drop_interval
        self.drop_counter = 0.0
        self.pos = {'x': 0, 'y': 0}
        self.matrix = None
        self.score = 0
        self.lines_cleared = 0
        self.game_over = False
        self.next_piece = get_random_piece()
        self.rotate_lock = False
        self.keys_pressed = {'left': False, 'right': False, 'down': False, 'rotate': False}

        # ✅ Таймеры для плавного горизонтального движения
        self.move_timer_l = 0.0
        self.move_timer_r = 0.0
        self.reset()

    def reset(self):
        self.matrix = self.next_piece
        self.next_piece = get_random_piece()
        self.pos['y'] = 0
        self.pos['x'] = (self.arena.width // 2) - (len(self.matrix[0]) // 2)
        if self.arena.collide(self):
            self.game_over = True

    def move(self, dx):
        if self.game_over: return
        self.pos['x'] += dx
        if self.arena.collide(self):
            self.pos['x'] -= dx

    def rotate(self, direction):
        if self.game_over: return
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
        n = len(self.matrix);
        m = len(self.matrix[0])
        transposed = [[self.matrix[j][i] for j in range(n)] for i in range(m)]
        self.matrix = [row[::-1] for row in transposed] if direction > 0 else transposed[::-1]

    def update(self, delta_time):
        if self.game_over: return

        # ✅ Движение влево: мгновенный сдвиг + задержка 0.15с + плавный автоповтор 0.08с
        if self.keys_pressed.get('left'):
            if self.move_timer_l <= 0:
                self.move(-1)
                self.move_timer_l = 0.15
            self.move_timer_l -= delta_time
            if self.move_timer_l <= 0:
                self.move_timer_l = 0.08
        else:
            self.move_timer_l = 0

        # ✅ Движение вправо: аналогично
        if self.keys_pressed.get('right'):
            if self.move_timer_r <= 0:
                self.move(1)
                self.move_timer_r = 0.15
            self.move_timer_r -= delta_time
            if self.move_timer_r <= 0:
                self.move_timer_r = 0.08
        else:
            self.move_timer_r = 0

        # Гравитация / падение
        spd = self.DROP_FAST if self.keys_pressed.get('down') else self.drop_interval
        self.drop_counter += delta_time
        if self.drop_counter >= spd:
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
            # ✅ Ускорение работает НЕЗАВИСИМО для каждого игрока, т.к. self.lines_cleared хранится внутри экземпляра Player
            level = self.lines_cleared // 50
            speeds = [1.0, 0.8, 0.6, 0.4, 0.3, 0.2, 0.15]
            self.normal_drop_interval = speeds[min(level, len(speeds) - 1)]
            if self.drop_interval != self.DROP_FAST:
                self.drop_interval = self.normal_drop_interval
        self.reset()

    def drop(self):
        if self.game_over: return
        while True:
            self.pos['y'] += 1
            if self.arena.collide(self):
                self.pos['y'] -= 1
                break
        self._lock_piece()