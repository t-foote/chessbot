from main import *


def en_passant_preset(b: Board) -> None:
    b.move('a2', 'a4')
    b.move('h7', 'h5')
    b.move('a4', 'a5')
    b.move('b7', 'b5')


def check_check_preset(b: Board) -> None:
    b.move('e2', 'e4')
    b.move('e7', 'e5')
    b.move('d1', 'h5')
    b.move('d7', 'd5')
    b.move('h5', 'f7')


def debug_001(b: Board) -> None:
    b.move('b2', 'b3')
    b.move('e7', 'e5')
    b.move('c1', 'b2')
    b.move('d7', 'd5')
    b.move('b2', 'e5')
    b.move('a2', 'a3')
    b.move('e5', 'g7')
    b.move('c7', 'c6')
