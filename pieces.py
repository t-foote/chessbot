from abstractpiece import (
    AbstractPiece,
    Coordinates,
    ABC,
    abstractmethod,
    MaybePiece
)
from header import (
    in_range,
)
from typing import Optional, List


class AbstractQRB(AbstractPiece, ABC):
    """
    An intermediary abstract class between AbstractPiece and the Queen, Rook, and Bishop
    subclasses; given the overlap between the get_valid_moves() methods of those 3 pieces.
    """

    def __str__(self):
        out = self.__class__.__name__[0]
        return out.upper() if self.color else out.lower()

    @abstractmethod
    def _steps(self) -> List[Coordinates]:
        raise NotImplementedError

    def get_valid_moves(self) -> List[Coordinates]:
        out = []
        for step in self._steps():
            x, y = step
            f = self.file
            r = self.rank
            while in_range((f+x, r+y)):
                f += x
                r += y
                maybe_piece: MaybePiece = self.board[f:r]
                if maybe_piece is not None and maybe_piece.color == self.color:
                    break
                out.append((f, r))
                if maybe_piece is not None:
                    self.pieces_can_capture.append((f, r))
                    break
        return out


class King(AbstractPiece):

    def __str__(self):
        return 'K' if self.color else 'k'

    def get_valid_moves(self) -> List[Coordinates]:
        out = []
        for x, y in self.STRAIGHT + self.DIAGONAL:
            f = self.file + x
            r = self.rank + y
            if not in_range((f, r)):
                continue
            maybe_piece: MaybePiece = self.board[f:r]
            if maybe_piece is not None:
                if maybe_piece.color == self.color:
                    continue
                if maybe_piece.color != self.color:
                    self.pieces_can_capture.append((f, r))
            out.append((f, r))
        # todo castling
        return out


class Queen(AbstractQRB):

    def _steps(self) -> List[Coordinates]:
        return self.STRAIGHT + self.DIAGONAL


class Rook(AbstractQRB):

    def _steps(self) -> List[Coordinates]:
        return self.STRAIGHT


class Bishop(AbstractQRB):

    def _steps(self) -> List[Coordinates]:
        return self.DIAGONAL


class Knight(AbstractPiece):

    def __str__(self):
        return 'N' if self.color else 'n'

    def get_valid_moves(self) -> List[Coordinates]:
        out = []
        for x, y in self.KNIGHT:
            f = self.file + x
            r = self.rank + y
            if not in_range((f, r)):
                continue
            new_square: MaybePiece = self.board[f:r]
            if new_square is None or new_square.color != self.color:
                out.append(new_square)
                if new_square is not None:
                    self.pieces_can_capture.append((f, r))
        return out


class Pawn(AbstractPiece):

    def __str__(self):
        return '.' if self.color else ','

    def get_valid_moves(self) -> List[Coordinates]:
        out = []

        is_home_rank = (self.rank == 2) if self.color else (self.rank == 7)
        direction = 1 if self.color else -1

        # todo consider pawn promotion

        # Moving forward 1 square:
        new_square: MaybePiece = self.board[self.file: self.rank + direction]
        if new_square is None:
            out.append(new_square)

            # Moving forward 2 squares:
            new_square: MaybePiece = self.board[self.file: 4 if self.color else 5]
            if is_home_rank and new_square is None:
                out.append(new_square)

        # Capture:
        for i in (1, -1):
            f = self.file + i
            r = self.rank + direction
            if not in_range((f, r)):
                continue
            new_square: MaybePiece = self.board[f:r]
            if new_square is not None and new_square.color != self.color:
                self.pieces_can_capture.append((f, r))
                out.append(new_square)

        # En-passant:
            # todo

        return out

