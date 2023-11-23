from typing import Optional, List, Tuple, Dict
from pieces import Piece
from header import in_range, OccupiedSquares, Coordinates


class Board:
    _board_has_changed: bool
    """
    Has a dictionary mapping board coordinates (file, rank) to a Piece object or None.
    Pieces in the Board object do not move. A new Board objected is created upon each move.
    """

    def __init__(self):
        self._grid: Dict[Coordinates, Optional[Piece]] = {}
        self._turn: bool = True
        # Make the grid:
        for file in range(1, 9):
            for rank in range(1, 9):
                self._grid[(file, rank)] = None
        self._update_pieces_lists()

    def get_piece(self, file, rank) -> Optional[Piece]:
        if not in_range(file) or not in_range(rank):
            raise ValueError(file if not in_range(file) else rank)
        return self._grid[(file, rank)]

    def add_piece(self, piece, file, rank):
        if not in_range(file, rank):
            raise ValueError(f"({file}, {rank}) is invalid")
        if self._grid[(file, rank)] is not None:
            raise ValueError(f"({file}, {rank}) is already occupied")
        self._grid[(file, rank)] = piece
        self._board_has_changed = True

    def _update_pieces_lists(self):
        self._pieces = {True: [], False: []}
        for square in self._grid:
            if self._grid[square] is not None:
                self._pieces[self._grid[square].white].append(square)
        self._board_has_changed = False

    @property
    def occupied_squares(self) -> OccupiedSquares:
        """ Returns a dict mapping True & False (representing white/black) to
        a list of coordinates containing a piece of that color. """
        if self._board_has_changed:
            self._update_pieces_lists()
        return self._pieces

    @property
    def is_playable(self) -> bool:
        raise NotImplementedError  # todo

    @property
    def turn(self) -> bool:
        """ Returns True if it's white to play, otherwise False"""
        return self._turn

    def __eq__(self, other) -> bool:
        for square in self._grid:
            if self.get_piece(*square) != other.get_piece(*square):
                return False
        return True
