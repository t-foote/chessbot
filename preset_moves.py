from main import Board


def en_passant_preset(b: Board) -> None:
    b.move('a2', 'a4')
    b.move('h7', 'h5')
    b.move('a4', 'a5')
    b.move('b7', 'b5')

