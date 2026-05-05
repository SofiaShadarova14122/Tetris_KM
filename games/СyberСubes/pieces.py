# pieces.py
import random

def create_piece(piece_type):
    if piece_type == 'T':
        return [[0,0,0],[1,1,1],[0,1,0]]
    elif piece_type == 'O':
        return [[2,2],[2,2]]
    elif piece_type == 'L':
        return [[0,3,0],[0,3,0],[0,3,3]]
    elif piece_type == 'J':
        return [[0,4,0],[0,4,0],[4,4,0]]
    elif piece_type == 'I':
        return [[0,5,0,0],[0,5,0,0],[0,5,0,0],[0,5,0,0]]
    elif piece_type == 'S':
        return [[0,6,6],[6,6,0],[0,0,0]]
    elif piece_type == 'Z':
        return [[7,7,0],[0,7,7],[0,0,0]]
    else:
        return [[1]]

def get_random_piece():
    pieces = 'ILJOTSZ'
    return create_piece(random.choice(pieces))