from main import *

import pygame
pygame.init()


icons = {
    'wK': 'icons/white_king.png',
    'wQ': 'icons/white_queen.png',
    'wR': 'icons/white_rook.png',
    'wB': 'icons/white_bishop.png',
    'wN': 'icons/white_knight.png',
    'w': 'icons/white_pawn.png',
    'bK': 'icons/black_king.png',
    'bQ': 'icons/black_queen.png',
    'bR': 'icons/black_rook.png',
    'bB': 'icons/black_bishop.png',
    'bN': 'icons/black_knight.png',
    'b': 'icons/black_pawn.png',
}

icons = {
    10: 'icons/white_king.png',
    9: 'icons/white_queen.png',
    5: 'icons/white_rook.png',
    4: 'icons/white_bishop.png',
    3: 'icons/white_knight.png',
    1: 'icons/white_pawn.png',
    -10: 'icons/black_king.png',
    -9: 'icons/black_queen.png',
    -5: 'icons/black_rook.png',
    -4: 'icons/black_bishop.png',
    -3: 'icons/black_knight.png',
    -1: 'icons/black_pawn.png',
}


PIECE_DIMENSION, SQUARE_DIMENSION = 300, 350
LIGHT_SQUARE, DARK_SQUARE = (240, 240, 200), (202, 193, 53)


def image(file_name: str, width: int, height: int = None) -> pygame.surface:
    if height is None:
        height = width
    return pygame.transform.scale(pygame.image.load(file_name), (width, height))


class ChessGame:
    pass
