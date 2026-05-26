# Tetris_KM/games/CyberCubes/arena.py
class Arena:
    def __init__(self, width=10, height=20):
        self.width = width
        self.height = height
        self.matrix = [[0 for _ in range(width)] for _ in range(height)]
        self.garbage_queue = 0  # Очередь мусорных линий

    def clear(self):
        self.matrix = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.garbage_queue = 0

    def collide(self, player):
        matrix = player.matrix
        pos = player.pos
        for y, row in enumerate(matrix):
            for x, value in enumerate(row):
                if value != 0:
                    target_y = y + pos['y']
                    target_x = x + pos['x']
                    if target_x < 0 or target_x >= self.width: return True
                    if target_y >= self.height or (target_y >= 0 and self.matrix[target_y][target_x] != 0): return True
        return False

    def merge(self, player):
        matrix = player.matrix
        pos = player.pos
        for y, row in enumerate(matrix):
            for x, value in enumerate(row):
                if value != 0:
                    target_y = y + pos['y']
                    target_x = x + pos['x']
                    if 0 <= target_y < self.height and 0 <= target_x < self.width:
                        self.matrix[target_y][target_x] = value

    def sweep(self):
        """Возвращает количество очищенных линий"""
        score = 0
        y = self.height - 1
        while y >= 0:
            if all(cell != 0 for cell in self.matrix[y]):
                del self.matrix[y]
                self.matrix.insert(0, [0 for _ in range(self.width)])
                score += 1
            else:
                y -= 1
        return score

    def add_garbage(self, lines):
        """Добавляет мусорные линии снизу"""
        self.garbage_queue += lines

    def apply_garbage(self):
        """Применяет очередь мусора, поднимая матрицу"""
        if self.garbage_queue > 0:
            lines_to_add = min(self.garbage_queue, self.height)

            # Удаляем верхние строки
            del self.matrix[:lines_to_add]

            # Добавляем мусор снизу (с дыркой в случайном месте)
            import random
            for _ in range(lines_to_add):
                garbage_line = [1] * self.width
                hole = random.randint(0, self.width - 1)
                garbage_line[hole] = 0
                self.matrix.append(garbage_line)

            self.garbage_queue -= lines_to_add