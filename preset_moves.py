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
