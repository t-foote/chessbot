from abstractboard import AbstractBoard
from abc import ABC, abstractmethod
from header import in_range, Coordinates, human_out, color_str
from typing import Optional, List
from copy import copy


class AbstractPiece(ABC):
    """ """
    STRAIGHT = [(1, 0), (0, 1), (-1, 0), (0, -1)]
    DIAGONAL = [(1, -1), (-1, 1), (1, 1), (-1, -1)]
    KNIGHT = [(1, 2), (1, -2), (-1, 2), (-1, -2), (2, 1), (2, -1), (-2, 1), (-2, -1)]

    def __init__(self, board: AbstractBoard, file: int, rank: int, color: bool):
        self._board = board
        self.file = file
        self.rank = rank
        self._color = bool(color)
        self.pieces_can_capture: list = []

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__) and
            isinstance(self, other.__class__) and
            self.file == other.file and
            self.rank == other.rank and
            self.color == other.color
        )

    def __repr__(self):
        return f"<{color_str(self.color, caps=False)} {self.__class__.__name__} at {human_out((self.file, self.rank))}>"

    @abstractmethod
    def __str__(self):
        """ Should return a 1 character symbolization of the piece's type and color. """
        raise NotImplementedError

    @property
    def file(self) -> int:
        return self._file

    @property
    def rank(self) -> int:
        return self._rank

    @file.setter
    def file(self, new: int):
        self._check_file_rank(new)
        self._file = new

    @rank.setter
    def rank(self, new: int):
        self._check_file_rank(new)
        self._rank = new

    @staticmethod
    def _check_file_rank(new: int):
        if not in_range(new):
            raise ValueError(new)

    @property
    def board(self) -> AbstractBoard:
        return self._board

    @property
    def color(self) -> bool:
        return self._color

    @abstractmethod
    def get_valid_moves(self) -> List[Coordinates]:
        """
        Returns a list of valid moves, which means a square the piece can legally
        move to disregarding checks.
        Get valid moves should also populate `pieces_can_capture` accordingly.
        """
        raise NotImplementedError

    def can_capture(self) -> List["AbstractPiece"]:
        """ Returns a list of pieces this piece can capture """
        self.pieces_can_capture = []
        self.get_valid_moves()
        return self.pieces_can_capture

    def get_legal_moves(self) -> List[Coordinates]:
        """ Returns a subset of get_valid_moves, but only moves that are legal (not in check) """
        out = []
        for square in self.get_valid_moves():
            new_board = copy(self.board)
            new_board.move_piece(self.file, self.rank, *square)
            if not new_board.is_in_check():
                out.append(square)
        return out


MaybePiece = Optional[AbstractPiece]

