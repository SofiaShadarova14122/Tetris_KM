# arena.py
class Arena:
    def __init__(self, width=12, height=20):
        self.width = width
        self.height = height
        self.matrix = [[0 for _ in range(width)] for _ in range(height)]

    def clear(self):
        self.matrix = [[0 for _ in range(self.width)] for _ in range(self.height)]

    def collide(self, player):
        matrix = player.matrix
        pos = player.pos
        for y, row in enumerate(matrix):
            for x, value in enumerate(row):
                if value != 0:
                    target_y = y + pos['y']
                    target_x = x + pos['x']
                    # Выход за боковые границы
                    if target_x < 0 or target_x >= self.width:
                        return True
                    # Выход за НИЖНЮЮ границу или пересечение с занятой клеткой
                    if target_y >= self.height or (target_y >= 0 and self.matrix[target_y][target_x] != 0):
                        return True
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
        score = 0
        y = self.height - 1
        while y >= 0:
            if all(cell != 0 for cell in self.matrix[y]):
                del self.matrix[y]
                self.matrix.insert(0, [0 for _ in range(self.width)])
                score += 10
            else:
                y -= 1
        return score