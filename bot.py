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


class PotentialMove:
    piece: Piece
    move: Tuple[int, int]
    point_diff: int

    def __init__(self, piece, move, point_diff=None):
        self.piece = piece
        self.move = move
        self.point_diff = point_diff

    def __lt__(self, other) -> bool:
        """Compares point differentials"""
        return self.point_diff < other.point_diff


def _alg001(b: Board) -> PotentialMove:
    # ALGORITHM 001: POINT DIFFERENTIAL:

    potentials = []  # Value: point value. Key: (piece, move: tuple)

    for piece in b.pieces(b.turn):
        print(piece)
        for move in piece.available_moves():
            print(f"    {move}")
            copy = BoardCopy(b)
            copy.move(piece, move)
            if copy.is_checkmate():
                return PotentialMove(piece, move)
            potentials.append(PotentialMove(piece, move, points_diff(copy)))

    print(potentials)
    return max(potentials)


def bot(b: Board) -> None:
    """This is the function where the bot makes the move. Nothing is returned; rather, the board is taken as
    an argument and the bot makes its move on that board."""

    b.move(_alg001(b).move[0], _alg001(b).move[1])


