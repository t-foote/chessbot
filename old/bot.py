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

    def __init__(self, piece, new, point_diff=None):
        self.piece = piece
        self.new = new
        self.point_diff = point_diff

    def __lt__(self, other) -> bool:
        """Compares point differentials"""
        return self.point_diff < other.point_diff

    def old(self) -> Tuple[int, int]:
        return self.piece.file, self.piece.rank


def _alg001(b: Board) -> PotentialMove:
    # ALGORITHM 001: POINT DIFFERENTIAL:

    potentials = []

    for piece in b.pieces(b.turn):
        # print(piece)
        for move in piece.available_moves():
            # print(f"    {move}")
            copy = BoardCopy(b)
            copy.move(piece, move)
            if copy.is_checkmate():
                return PotentialMove(piece, move)
            potentials.append(PotentialMove(piece, move, points_diff(copy)))

    # print(potentials)
    return max(potentials)


def _2move(b: Board) -> PotentialMove:
    pass


def bot(b: Board) -> None:
    """This is the function where the bot makes the move. Nothing is returned; rather, the board is taken as
    an argument and the bot makes its move on that board."""

    b.move(_alg001(b).old(), _alg001(b).new)

