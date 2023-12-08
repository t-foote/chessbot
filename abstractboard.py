from abc import ABC, abstractmethod
from typing import Dict, Union, Tuple, Any
from header import WHITE, BLACK, color_str, human_in


class AbstractBoard(ABC):

    def __init__(self, turn: bool = WHITE):
        """ Instantiates empty board """
        self.grid: Dict[int, Dict[int, Any]] = {file: None for file in range(1, 9)}
        for file in self.grid:
            self.grid[file] = {rank: None for rank in range(1, 9)}
        self.turn = turn

    def __repr__(self):
        return f"<{self.__class__.__name__}: {color_str(self.turn)} TO PLAY>"

    def __str__(self):
        """ A string representation of the board, for debugging purposes """
        out = ""
        for rank in range(8, 0, -1):
            for file in range(1, 9):
                p = self[file:rank]
                out += " " if p is None else str(self[file:rank]) + " "
            out = out[:-1] + "\n"
        out += color_str(self.turn) + " TO PLAY"
        return out

    def __getitem__(self, file_rank: Union[Tuple[int, int], slice]):
        """
        Returns the item (piece or None) in the given coordinates (file, rank).
        The coordinates (file, rank) can be given in 1 of 2 ways:
        - self[file:rank]
        - self[(file, rank)]
        """
        if isinstance(file_rank, tuple) and len(file_rank) == 2:
            file, rank = file_rank
            return self.grid[file][rank]
        if not isinstance(file_rank, slice):
            raise TypeError(file_rank)
        if file_rank.step is not None:
            raise ValueError(f"unexpected index: {file_rank.step}")
        if file_rank.stop is None:
            raise ValueError(f"missing rank value")
        return self.grid[file_rank.start][file_rank.stop]

    def get_from_human_in(self, square: str):
        return self[human_in(square)]

    @property
    def pieces(self) -> list:
        """ A list of pieces on the board """
        out = []
        for file in self.grid:
            for rank in self.grid[file]:
                item = self.grid[file][rank]
                if item is not None:
                    out.append(item)
        return out

    @abstractmethod
    def populate(self) -> bool:
        """
        Populate a new board with pieces.
        Returns False iff the board is not empty to begin with.
        """
        raise NotImplementedError

    @abstractmethod
    def is_playable(self) -> bool:
        """
        Returns True iff:
        - There is exactly 1 King of each color on the board
        """
        raise NotImplementedError

    @abstractmethod
    def add_piece(self, piece_type, file: int, rank: int, white: bool) -> bool:
        """ Adds a piece to the board. Returns True iff piece was successfully added. """
        raise NotImplementedError

    @abstractmethod
    def is_in_check(self) -> bool:
        """ Returns True if the player whose turn it is is in check. """
        raise NotImplementedError

