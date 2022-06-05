from main import *  # This also imports everything from main


def points(b: Board, color: bool = None) -> int:
    """Calculates & returns total material points of a given player."""
    if color is None:
        color = b.turn
    points_map = {
        King:   0,
        Queen:  9,
        Rook:   5,
        Bishop: 3,
        Knight: 3,
        Pawn:   1,
    }
    out = 0
    for piece in b.pieces(color):
        out += points_map[type(piece)]
    return out


def points_diff(b: Board) -> int:
    return points(b, not b.turn) - points(b, b.turn)


def _alg001(b: Board) -> Tuple[Piece, Tuple[int, int]]:
    # ALGORITHM 001: POINT DIFFERENTIAL:

    potential = dict()  # Key: point value. Value: (piece, move: tuple)

    for piece in b.pieces(b.turn):
        print(piece)
        for move in piece.available_moves():
            print(f"    {move}")
            copy = BoardCopy(b)
            copy.move(piece, move)
            if copy.is_checkmate():
                return piece, move
            potential[points_diff(copy)] = (piece, move)

    print(potential)
    return potential[max(potential)]


def bot(b: Board) -> None:
    """This is the function where the bot makes the move. Nothing is returned; rather, the board is taken as
    an argument and the bot makes its move on that board."""

    b.move(_alg001(b)[0], _alg001(b)[1])


