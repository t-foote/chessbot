from abstractboard import AbstractBoard
from pieces import (
    AbstractPiece,
    MaybePiece,
    King,
    Queen,
    Rook,
    Bishop,
    Knight,
    Pawn
)
from typing import Optional, Type
from header import WHITE, BLACK


class Board(AbstractBoard):

    def __getitem__(self, item) -> Optional[AbstractPiece]:
        return super().__getitem__(item)

    def add_piece(self, piece_type: Type[AbstractPiece], file: int, rank: int, color: bool) -> bool:
        if self[file:rank] is not None:
            return False
        self.grid[file][rank] = piece_type(
            board=self,
            file=file,
            rank=rank,
            color=color,
        )
        return True

    def is_playable(self) -> bool:
        # Making sure there's exactly 1 King of each color on the board:
        kings = {
            WHITE: False,
            BLACK: False,
        }
        for piece in self.pieces:
            if isinstance(piece, King):
                if kings[piece.color]:
                    return False
                kings[piece.color] = True
        if False in kings.values():
            return False
        # Other ...
        return True

    def populate(self) -> bool:
        if self.pieces:
            return False
        for rank in (1, 8):
            # Initialize Kings:
            self.add_piece(King, file=5, rank=rank, color=(rank == 1))
            # Initialize Queens:
            self.add_piece(Queen, file=4, rank=rank, color=(rank == 1))
            # Initialize Rooks:
            for file in (1, 8):
                self.add_piece(Rook, file=file, rank=rank, color=(rank == 1))
            # Initialize Knights:
            for file in (2, 7):
                self.add_piece(Knight, file=file, rank=rank, color=(rank == 1))
            # Initialize Bishops:
            for file in (3, 6):
                self.add_piece(Bishop, file=file, rank=rank, color=(rank == 1))
        # Initialize Pawns:
        for file in range(1, 9):
            for rank in (2, 7):
                self.add_piece(Pawn, file=file, rank=rank, color=(rank == 2))
        self.turn = WHITE
        return True

    def is_in_check(self) -> bool:
        for piece in self.pieces:
            piece: AbstractPiece
            if piece.color != self.turn and self in piece.can_capture():
                return True
        return False
