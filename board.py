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
from typing import Optional, Type, List
from header import WHITE, BLACK, in_range
from copy import copy


class Board(AbstractBoard):

    def __getitem__(self, item) -> Optional[AbstractPiece]:
        return super().__getitem__(item)

    def __eq__(self, other):
        """
        This dunder method is to enforce repetition rules such as threefold repetition.
        In chess, a move is considered a repetition of a previous move if both of the following conditions are True:
            1. All pieces of the same kind and color are on identical squares
            2. All possible moves are the same
        """
        if not isinstance(other, AbstractBoard):
            raise TypeError(other)
        for file in range(1, 9):
            for rank in range(1, 9):
                x = self[file:rank]
                y = other[file:rank]
                if x != y:
                    # If condition 1 is False
                    return False
                if x is not None and set(x.get_legal_moves()) != set(y.get_legal_moves()):
                    # If condition 2 is False
                    return False
        return True

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

    def move_piece(self, old_file: int, old_rank: int, new_file: int, new_rank: int) -> bool:
        if not in_range((old_file, old_rank)):
            raise ValueError((old_file, old_rank))
        if not in_range((new_file, new_rank)):
            raise ValueError((new_file, new_rank))
        old_piece = self[old_file:old_rank]
        if old_piece is None:
            return False
        new_square = self[new_file:new_rank]
        if new_square is not None and new_square.color == old_piece.color:
            return False
        self.rm_piece(new_file, new_rank)
        old_piece.file = new_file
        old_piece.rank = new_rank
        self.grid[old_file][old_rank] = None
        self.grid[new_file][new_rank] = old_piece
        return True

    @property
    def pieces(self) -> List[AbstractPiece]:
        return super().pieces

    def __copy__(self):
        out = self.__class__(turn=self.turn)
        for piece in self.pieces:
            out.add_piece(
                piece_type=piece.__class__,
                file=piece.file,
                rank=piece.rank,
                color=piece.color,
            )
        return out

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

    def get_new_board_after_move(self, old_file: int, old_rank: int, new_file: int, new_rank: int) -> "Board":
        out = copy(self)
        old_piece: MaybePiece = out[old_file:old_rank]
        if old_piece is None or old_piece.color != self.turn:
            raise ValueError(f"can't move from {(old_file, old_rank)}")
        if (new_file, new_rank) not in old_piece.get_legal_moves():
            raise ValueError(f"illegal move to {(new_file, new_rank)}")
        if not out.move_piece(old_file, old_rank, new_file, new_rank):
            raise RuntimeError(f"move failed")
        out.turn = not out.turn
        return out


if __name__ == "__main__":
    b = Board()
    b.populate()
    print(b)
    b.move_piece(5,2,5,4)
    print(b)
