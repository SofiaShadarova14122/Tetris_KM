# Tetris_KM/games/CyberCubes/pieces.py
import random

def get_piece():
    t = random.choice(['I','O','T','S','Z','J','L'])
    if t=='I': return [[0,0,0,0],[1,1,1,1],[0,0,0,0],[0,0,0,0]]
    if t=='O': return [[2,2],[2,2]]
    if t=='T': return [[0,3,0],[3,3,3],[0,0,0]]
    if t=='S': return [[0,4,4],[4,4,0],[0,0,0]]
    if t=='Z': return [[5,5,0],[0,5,5],[0,0,0]]
    if t=='J': return [[6,0,0],[6,6,6],[0,0,0]]
    if t=='L': return [[0,0,7],[7,7,7],[0,0,0]]
    return [[1]]