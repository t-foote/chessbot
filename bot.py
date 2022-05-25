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
    return points(b, b.turn) - points(b, not b.turn)


def _alg001(b: Board) -> Tuple[Piece, Tuple[int, int]]:
    # ALGORITHM 001: POINT DIFFERENTIAL:

    best_piece = None
    best_spread = -float("inf")  # The highest difference b/w player & opponent's points
    best_move = (0, 0)

    for piece in b.pieces(b.turn):
        for move in piece.available_moves():
            copy = BoardCopy(b)
            copy.move(piece, move)
            if copy.is_checkmate():
                return piece, move
            if points_diff(copy) > best_spread:
                best_piece = piece
                best_move = move
                best_spread = points_diff(copy)

    return best_piece, best_move


def bot(b: Board) -> None:
    """This is the function where the bot makes the move. Nothing is returned; rather, the board is taken as
    an argument and the bot makes its move on that board."""

    b.move(_alg001(b)[0], _alg001(b)[1])


