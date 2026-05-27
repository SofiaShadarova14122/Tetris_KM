# Tetris_KM/games/CyberCubes/arena.py
class Arena:
    def __init__(self, w=10, h=20):
        self.w, self.h = w, h
        self.m = [[0]*w for _ in range(h)]
        self.garbage = 0

    def collide(self, p):
        for y,row in enumerate(p.matrix):
            for x,v in enumerate(row):
                if v:
                    tx, ty = p.pos['x']+x, p.pos['y']+y
                    if tx<0 or tx>=self.w or ty>=self.h or (ty>=0 and self.m[ty][tx]): return True
        return False

    def merge(self, p):
        for y,row in enumerate(p.matrix):
            for x,v in enumerate(row):
                if v:
                    ty, tx = p.pos['y']+y, p.pos['x']+x
                    if 0<=ty<self.h and 0<=tx<self.w: self.m[ty][tx] = v

    def sweep(self):
        s = 0
        y = self.h - 1
        while y >= 0:
            if all(self.m[y]):
                del self.m[y]
                self.m.insert(0, [0]*self.w)
                s += 1
            else: y -= 1
        return s

    def add_garbage(self, n): self.garbage += n

    def apply_garbage(self):
        if self.garbage > 0:
            for _ in range(min(self.garbage, self.h)):
                import random
                line = [1]*self.w
                line[random.randint(0,self.w-1)] = 0
                del self.m[0]
                self.m.append(line)
            self.garbage = 0