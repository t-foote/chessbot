from board import Board
from typing import List
from header import WHITE, BLACK
from enum import Enum, auto
from pieces import (
    King,
    Queen,
    Rook,
    Bishop,
    Knight,
    Pawn,
)


class GameState(Enum):

    IN_PROGRESS = auto()
    CHECKMATE_WHITE = auto()
    CHECKMATE_BLACK = auto()
    STALEMATE = auto()
    REPETITION = auto()
    INSUFFICIENT = auto()
    FIFTY_MOVE_RULE = auto()

    @property
    def is_draw(self) -> bool:
        return self in [
            self.STALEMATE,
            self.REPETITION,
            self.INSUFFICIENT,
            self.FIFTY_MOVE_RULE,
        ]

    @property
    def is_checkmate(self) -> bool:
        return self in [
            self.CHECKMATE_WHITE,
            self.CHECKMATE_BLACK,
        ]

    @property
    def in_progress(self) -> bool:
        return self is self.IN_PROGRESS

    @property
    def is_over(self) -> bool:
        return not self.in_progress

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<{self.__class__.__name__}: {str(self)}>"


class Game:
    """ A game being played """

    def __init__(self):
        board = Board()
        board.populate()
        self.boards: List[Board] = [board]
        self.state: GameState = GameState.IN_PROGRESS
        self.twice_repeated_boards: List[Board] = []
        self.fifty_move_rule_count = 0

    def __str__(self):
        return str(self.current_board)

    def __repr__(self):
        return f"<{self.__class__.__name__}>"

    @property
    def state(self) -> GameState:
        return self._state

    @state.setter
    def state(self, new_state: GameState):
        if not isinstance(new_state, GameState):
            raise TypeError(new_state)
        self._state = new_state

    @property
    def current_board(self) -> Board:
        return self.boards[-1]

    @property
    def turn(self) -> bool:
        return self.current_board.turn

    def is_in_check_or_stale_mate(self) -> bool:
        """
        Returns True iff the Game is in checkmate or stalemate.
        Does not change the Game State.
        """
        board = self.current_board
        for piece in board.pieces:
            if piece.color != self.turn:
                # Skip opponent's pieces
                continue
            if piece.get_legal_moves():
                # If at least 1 piece still has legal moves available
                return False
        return True

    def is_insufficient_material(self) -> bool:
        """
        Returns True iff the Game has insufficient material to proceed.
        Does not change the Game State.
        """
        pieces = self.current_board.pieces
        if len(pieces) == 2:
            # Just 2 Kings left
            return True
        if len(pieces) > 3:
            return False
        for piece in pieces:
            if isinstance(piece, (Rook, Queen, Pawn)):
                return False
        return True

    def move(self, old_file: int, old_rank: int, new_file: int, new_rank: int) -> None:
        """ Make a move and check game states. Assumes the move is legal. """
        if self.state.is_over:
            return
        piece_moved = self.current_board[old_file:old_rank]
        self.boards.append(self.current_board.get_new_board_after_move(
            old_file=old_file,
            old_rank=old_rank,
            new_file=new_file,
            new_rank=new_rank,
        ))
        # CHECK GAME STATES:
        current_board = self.current_board
        # Checkmate or Stalemate
        if self.is_in_check_or_stale_mate():
            # Checkmate:
            if current_board.is_in_check():
                if current_board.turn == WHITE:
                    self.state = GameState.CHECKMATE_BLACK
                if current_board.turn == BLACK:
                    self.state = GameState.CHECKMATE_WHITE
            # Stalemate:
            else:
                self.state = GameState.STALEMATE
            return
        # Insufficient Material:
        if self.is_insufficient_material():
            self.state = GameState.INSUFFICIENT
            return
        # Repetition:
        for board in self.twice_repeated_boards:
            if board == current_board:
                self.state = GameState.REPETITION
                return
        for i in range(len(self.boards) - 1, 0, -1):
            board = self.boards[i-1]
            if board == current_board:
                self.twice_repeated_boards.append(board)
                break
        # Fifty-move rule:
        if isinstance(piece_moved, Pawn) or len(current_board.pieces) != len(self.boards[-2].pieces):
            self.fifty_move_rule_count = 0
        else:
            self.fifty_move_rule_count += 1
        if self.fifty_move_rule_count >= 50:
            self.state = GameState.FIFTY_MOVE_RULE
            return

        # todo pawn promotion


if __name__ == "__main__":
    g = Game()
    print(g)
