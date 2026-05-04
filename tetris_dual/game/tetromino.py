import random

class Tetromino:
    SHAPES = {
        'I': [[1,1,1,1]],
        'O': [[1,1],[1,1]],
        'T': [[0,1,0],[1,1,1]],
        'S': [[0,1,1],[1,1,0]],
        'Z': [[1,1,0],[0,1,1]],
        'J': [[1,0,0],[1,1,1]],
        'L': [[0,0,1],[1,1,1]]
    }
    def __init__(self, shape_type=None):
        if shape_type is None:
            shape_type = random.choice(list(self.SHAPES.keys()))
        self.shape_type = shape_type
        self.shape = self.SHAPES[shape_type]
        self.x = 0
        self.y = 0

    def rotate(self):
        rows = len(self.shape)
        cols = len(self.shape[0])
        return [[self.shape[rows-1-j][i] for j in range(rows)] for i in range(cols)]

    def get_positions(self):
        positions = []
        for y, row in enumerate(self.shape):
            for x, cell in enumerate(row):
                if cell:
                    positions.append((self.x + x, self.y + y))
        return positions