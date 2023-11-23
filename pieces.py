from typing import List, Tuple
from header import (
    in_range,
    human_in,
    human_out,
    combine,
    OccupiedSquares,
    Coordinates,
    STRAIGHT,
    DIAGONAL,
    KNIGHT,
)


class Piece:

    def __init__(self, white: bool):
        self._white = white
        self._has_moved = False

    @property
    def white(self) -> bool:
        return self._white

    @property
    def color(self) -> str:
        return "White" if self.white else "Black"

    @property
    def has_moved(self) -> bool:
        return self._has_moved

    def moved(self):
        """ Used to indicate the piece has been moved at least once in the game"""
        self._has_moved = True

    def valid_moves(self, file: int, rank: int, occupied_squares: OccupiedSquares) -> List[Coordinates]:
        """
        Returns a list of coordinates where the piece can move to
        (however this does not take into account checks or castling)
        """
        if not isinstance(occupied_squares, OccupiedSquares):
            raise TypeError(occupied_squares)
        raise NotImplementedError

    def _valid_moves_helper(self, file: int, rank: int, occupied_squares: OccupiedSquares,
                            adjacent: List[Tuple[int, int]]) -> List[Coordinates]:
        """ Helper method for Queen, Rook, Bishop """
        out = []
        for x, y in STRAIGHT + DIAGONAL:
            f = file
            r = rank
            while in_range(f, r):
                f += x
                r += y
                if (f, r) in occupied_squares[self.white]:
                    break
                out.append((f, r))
                if (f, r) in occupied_squares[not self.white]:
                    break
        return out

    def __eq__(self, other):
        return isinstance(self, other) and isinstance(other, self) and self.white == other.white

    def __str__(self) -> str:
        letter = self.__class__.__name__[0]
        return letter.upper() if self.white else letter.lower()

    def __repr__(self) -> str:
        return f"<{self.color} {self.__class__.__name__}>"


class King(Piece):

    def valid_moves(self, file: int, rank: int, occupied_squares: OccupiedSquares) -> List[Coordinates]:
        super().valid_moves(file, rank, occupied_squares)
        out = []
        for x, y in STRAIGHT + DIAGONAL:
            new_square = (file + x, rank + y)
            if in_range(new_square) and new_square not in occupied_squares[self.white]:
                out.append(new_square)
        return out


class Queen(Piece):

    def valid_moves(self, file: int, rank: int, occupied_squares: OccupiedSquares) -> List[Coordinates]:
        super().valid_moves(file, rank, occupied_squares)
        return self._valid_moves_helper(file, rank, occupied_squares, STRAIGHT + DIAGONAL)


class Rook(Piece):

    def valid_moves(self, file: int, rank: int, occupied_squares: OccupiedSquares) -> List[Coordinates]:
        super().valid_moves(file, rank, occupied_squares)
        return self._valid_moves_helper(file, rank, occupied_squares, STRAIGHT)


class Bishop(Piece):

    def valid_moves(self, file: int, rank: int, occupied_squares: OccupiedSquares) -> List[Coordinates]:
        super().valid_moves(file, rank, occupied_squares)
        return self._valid_moves_helper(file, rank, occupied_squares, DIAGONAL)


class Knight(Piece):

    def valid_moves(self, file: int, rank: int, occupied_squares: OccupiedSquares) -> List[Coordinates]:
        out = []
        for x, y in KNIGHT:
            new_square = (file + x, rank + y)
            if in_range(new_square) and new_square not in occupied_squares[self.white]:
                out.append(new_square)
        return out


class Pawn(Piece):

    def valid_moves(self, file: int, rank: int, occupied_squares: OccupiedSquares) -> List[Coordinates]:
        out = []
        is_home_rank = (rank == 2) if self.white else (rank == 7)
        direction = 1 if self.white else -1
        all_occupied_squares = combine(occupied_squares)

        # Moving forward 1 square:
        new_square = (file, rank + direction)
        if new_square not in all_occupied_squares:
            out.append(new_square)

            # Moving forward 2 squares:
            new_square = (file, 4 if self.white else 5)
            if is_home_rank and new_square not in all_occupied_squares:
                out.append(new_square)

        # Capture:
        for i in (1, -1):
            new_square = (file + i, rank + direction)
            if in_range(new_square) and new_square in occupied_squares[not self.white]:
                out.append(new_square)

        # En-passant:


        return out

    def __str__(self):
        return "." if self.white else ","

