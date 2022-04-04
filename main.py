from typing import Dict, Tuple, List, Optional

"""
_valid_moves vs. available_moves:
same for all pieces except king, in which _valid_moves doesn't consider checks & castling options. 
"""

RUN = True


def human_in(s: str) -> Tuple[int, int]:
    letters = {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6, 'g': 7, 'h': 8}
    return letters[s[0].lower()], int(s[1])


def human_out(file_rank: Tuple[int, int]) -> str:
    file, rank = file_rank[0], file_rank[1]
    numbers = {1: 'a', 2: 'b', 3: 'c', 4: 'd', 5: 'e', 6: 'f', 7: 'g', 8: 'h'}
    return numbers[file] + str(rank)


def in_range(file_rank: Tuple[int, int]) -> bool:
    return file_rank[0] in range(1, 9) and file_rank[1] in range(1, 9)


class Board:
    def occupant(self, file, rank):
        raise NotImplementedError


class Piece:
    pass


class Move:
    """
    old move; new move. Piece.
    """
    old_file: int
    old_rank: int
    new_file: int
    new_rank: int
    piece: Piece
    can_move: bool
    is_empty_move: bool

    def __init__(self, old_file: int, old_rank: int, new_file: int, new_rank: int, piece: Piece):
        self.old_file = old_file
        self.old_rank = old_rank
        self.new_file = new_file
        self.new_rank = new_rank
        self.piece = piece
        self.can_move = (new_file, new_rank) in piece.available_moves()
        self.is_empty_move = False

    def can_en_passant(self) -> Optional[int]:
        if self.is_empty_move:
            return None
        if self.piece.white:
            if isinstance(self.piece, Pawn) and self.old_rank == 2 and self.new_rank == 4:
                return self.new_file
        else:
            if isinstance(self.piece, Pawn) and self.old_rank == 7 and self.new_rank == 5:
                return self.new_file
        return None
    
    def __eq__(self, other) -> bool:
        return (self.old_file == other.old_file and
                self.old_rank == other.old_rank and
                self.new_file == other.new_file and
                self.new_rank == other.new_rank and
                self.piece is other.piece)


class EmptyMove(Move):
    """
    The 0th move in the move log.
    """
    is_empty_move: bool

    def __init__(self):
        self.is_empty_move = True


class Piece:
    """
    A chess piece.
    Files 'a' through 'h' are indicated by 1 through 8 respectively.
    """
    file: int
    rank: int
    white: bool
    board: Board

    def __init__(self, file: int, rank: int, white: bool, board: Board):
        self.file = file
        self.rank = rank
        self.white = white
        self.board = board

    def _valid_moves(self) -> List[Tuple[int, int]]:
        """
        Returns list of valid moves for that piece.
        """
        raise NotImplementedError

    def available_moves(self) -> List[Tuple[int, int]]:
        """
        Returns list of available moves for that piece (like dots in lichess).
        """
        return self._valid_moves()

    def moveable(self, file_rank: Tuple[int, int]) -> bool:
        """
        Returns True iff occupant of specified square is not the same color as self, or empty.
        Returns False if (file, rank) isn't in range.
        """
        file, rank = file_rank[0], file_rank[1]
        if not in_range((file, rank)):
            return False
        if self.board.occupant(file, rank) is None:
            return True
        return self.board.occupant(file, rank).white != self.white

    def move(self, file: int, rank: int, override: bool = False) -> bool:
        """
        Attempts to move piece. Returns True iff piece is successfully moved.
        If override argument is given and True, move will be executed regardless of validity.
        """
        # old_square = (self.file, self.rank)
        # if ((file, rank) in self.available_moves()) or override:
        #     self.board.remove_occupant(file, rank)
        #     self.file = file
        #     self.rank = rank
        #     self.board.moved()
        #     return True
        # return False
        m = Move(self.file, self.rank, file, rank, self)
        if m.can_move or override:
            self.board.remove_occupant(file, rank)
            self.file = file
            self.rank = rank
            self.board.moved(m)
            return True
        return False

    def _get_opposing_pieces(self) -> List[Piece]:
        """
        Exactly what the name suggests.
        """
        if self.white:
            return self.board.black_pieces()
        else:
            return self.board.white_pieces()

    def attackers(self, file: int = 0, rank: int = 0) -> List[Piece]:
        """
        Returns the opponent's pieces that can capture that piece.
        """
        out = []
        if file < 1:
            file = self.file
        if rank < 1:
            rank = self.rank
        for piece in self._get_opposing_pieces():
            if (file, rank) in piece.available_moves():
                out.append(piece)
        return out


class Pawn(Piece):
    """
    A pawn.
    """
    file: int
    rank: int
    white: bool
    board: Board

    def _valid_moves(self) -> List[Tuple[int, int]]:
        out = []
        # Moving forward 1 square:
        if self.board.occupant(self.file, self.rank + (int(self.white) * 2 - 1)) is None:
            out.append((self.file, self.rank + (int(self.white) * 2 - 1)))
            # Moving forward 2 squares:
            if (self.white and self.rank == 2) or (not self.white and self.rank == 7):
                if self.board.occupant(self.file, int(self.white)*(-1) + 5) is None:
                    out.append((self.file, int(self.white)*(-1) + 5))
        # Capture:
        for i in (1, -1):
            if (in_range((self.file + i, self.rank + (self.white * 2 - 1))) and
                    (self.board.occupant(self.file + i, self.rank + (self.white * 2 - 1)) is not None) and
                    (self.board.occupant(self.file + i, self.rank + (self.white * 2 - 1)).white != self.white)):
                out.append((self.file + i, self.rank + (self.white * 2 - 1)))
        # En-passant:
        if (self.board.last_move().can_en_passant() == self.file + 1) and (self.rank == int(self.white)*(-1) + 5):
            out.append((self.file + 1, self.rank + (int(self.white) * 2 - 1)))
        elif (self.board.last_move().can_en_passant() == self.file - 1) and (self.rank == int(self.white)*(-1) + 5):
            out.append((self.file - 1, self.rank + (int(self.white) * 2 - 1)))
        return out

    def move(self, file: int, rank: int, promote_to: Piece = None) -> bool:
        """
        Attempts to move pawn. Returns True iff successfully moved.

        Pre-conditions:
        if (self.white and self.rank == 7) or (not self.white and self.rank == 2), promote_to is not None
        """
        if (self.white and self.rank == 7) or (not self.white and self.rank == 2):
            # Promotion:
            if Piece.move(self, file, rank):
                self.board.promote(file, self.white, promote_to)
                return True
            return False
        # elif abs(rank - self.rank) == 2:
        #     # Moves by 2 squares (makes itself en-passant capture eligible):
        #     if Piece.move(self, file, rank):
        #         self.board.en_passant(file)
        #         return True
        #     return False
        elif ((file, rank) in self._valid_moves()) and (self.file != file) and (self.board.occupant(file, rank) is None):
            if Piece.move(self, file, rank):
                self.board.remove_occupant(file, self.rank)
                return True
            return False
        else:
            return Piece.move(self, file, rank)


class Knight(Piece):
    """
    A knight.
    """
    file: int
    rank: int
    white: bool
    board: Board

    def _valid_moves(self) -> List[Tuple[int, int]]:
        out = []
        for i in [(1, 2), (1, -2), (-1, 2), (-1, -2), (2, 1), (2, -1), (-2, 1), (-2, -1)]:
            if self.moveable((self.file + i[0], self.rank + i[1])):
                out.append((self.file + i[0], self.rank + i[1]))
        return out


class Bishop(Piece):
    """
    A bishop.
    """
    file: int
    rank: int
    white: bool
    board: Board

    def _valid_moves(self) -> List[Tuple[int, int]]:
        out = []
        for i in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
            f = self.file
            r = self.rank
            while in_range((f + i[0], r + i[1])) and self.board.occupant(f + i[0], r + i[1]) is None:
                f += i[0]
                r += i[1]
                out.append((f, r))
            if self.board.occupant(f + i[0], r + i[1]) is not None and \
                    self.board.occupant(f + i[0], r + i[1]).white != self.white:
                out.append((f + i[0], r + i[1]))
        return out


class Rook(Piece):
    """
    A rook.
    """
    file: int
    rank: int
    white: bool
    board: Board
    has_moved: bool

    def __init__(self, file: int, rank: int, white: bool, board: Board):
        Piece.__init__(self, file, rank, white, board)
        self.has_moved = False

    def _valid_moves(self) -> List[Tuple[int, int]]:
        out = []
        for i in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
            f = self.file
            r = self.rank
            while in_range((f + i[0], r + i[1])) and self.board.occupant(f + i[0], r + i[1]) is None:
                f += i[0]
                r += i[1]
                out.append((f, r))
            if self.board.occupant(f + i[0], r + i[1]) is not None and \
                    self.board.occupant(f + i[0], r + i[1]).white != self.white:
                out.append((f + i[0], r + i[1]))
        return out

    def move(self, file: int, rank: int, override: bool = False) -> bool:
        if Piece.move(self, file, rank, override):
            self.has_moved = True
            return True
        return False


class Queen(Piece):
    """
    A queen.
    """
    file: int
    rank: int
    white: bool
    board: Board

    # def __init__(self, file: int, rank: int, white: bool, board: Board):
    #     Piece.__init__(self, file, rank, white, board)

    def _valid_moves(self) -> List[Tuple[int, int]]:
        out = []
        for i in [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
            f = self.file
            r = self.rank
            while in_range((f + i[0], r + i[1])) and self.board.occupant(f + i[0], r + i[1]) is None:
                f += i[0]
                r += i[1]
                out.append((f, r))
            if self.board.occupant(f + i[0], r + i[1]) is not None and \
                    self.board.occupant(f + i[0], r + i[1]).white != self.white:
                out.append((f + i[0], r + i[1]))
        return out


class King(Piece):
    """
    A king.
    """
    file: int
    rank: int
    white: bool
    board: Board
    has_moved: bool

    def __init__(self, file: int, rank: int, white: bool, board: Board):
        Piece.__init__(self, file, rank, white, board)
        self.has_moved = False

    def _valid_moves(self) -> List[Tuple[int, int]]:
        """
        Does not include castling or in-check positions.
        """
        out = []
        for i in [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
            if not (((self.board.occupant(self.file + i[0], self.rank + i[1]) is not None) and (
                    self.board.occupant(self.file + i[0], self.rank + i[1]).white == self.white)) or (
                    self.file + i[0] not in range(1, 9)) or (self.rank + i[1] not in range(1, 9))):
                out.append((self.file + i[0], self.rank + i[1]))
        return out

    def available_moves(self) -> List[Tuple[int, int]]:
        """
        Returns list of available moves (like dots in lichess), including castling.
        """
        out = []
        for move in self._valid_moves():
            if not self.attackers(move[0], move[1]):
                out.append(move)
        out += [(7, self.rank)] * self.castle(True, False)
        out += [(3, self.rank)] * self.castle(False, False)
        return out

    def castle(self, king_side: bool, proceed: bool = True) -> bool:
        """
        Attempts to castle. Returns True iff successfully castled.
        If proceed == False, move will not be executed but bool will still be returned.
        """
        if self.has_moved:
            return False
        if king_side:
            if isinstance(self.board.occupant(8, 7 * int(not self.white) + 1), Rook) and (
                    not self.board.occupant(8, 7 * int(not self.white) + 1).has_moved):
                if (not self.attackers()) and (not self.attackers(6)) and (not self.attackers(7)):
                    if proceed:
                        # Moving the king:
                        self.move(7, self.rank, True)
                        # Moving the rook:
                        self.board.occupant(8, self.rank).move(6, self.rank, True)
                        self.board.moved()
                    return True
                return False
            return False
        else:
            if isinstance(self.board.occupant(1, 7 * int(not self.white) + 1), Rook) and (
                    not self.board.occupant(1, 7 * int(not self.white) + 1).has_moved):
                if (not self.attackers()) and (not self.attackers(4)) and (not self.attackers(3)):
                    if proceed:
                        # Moving the king:
                        self.move(3, self.rank, True)
                        # Moving the rook:
                        self.board.occupant(1, self.rank).move(4, self.rank, True)
                        self.board.moved()
                    return True
                return False
            return False

    def move(self, file: int, rank: int, override: bool = False) -> bool:
        """
        Attempts to move king. Returns True iff piece is successfully moved.
        Updates self.has_moved

        Pre-conditions:
        - file in range(1, 9) and rank in range(1, 9)
        """
        if (not self.attackers(file, rank)) and Piece.move(self, file, rank, override):
            self.has_moved = True
            return True
        return False


class Board:
    """
    A chess board in which a game is taking place.
    Initializes as a set board ready for play.
    turn == True indicates white's turn to play.
    turn == False indicates black's turn to play.
    _en_passant is the file where the pawn can be captured
    """
    _pieces: List[Piece]
    turn: bool
    _checkmate: bool
    _draw: bool
    # _en_passant: Optional[int]
    _move_log: List[Move]

    def __init__(self, ready_to_play: bool = True):
        self._pieces = []
        self._move_log = [EmptyMove()]
        if ready_to_play:
            # Initialize rooks:
            for f in [1, 8]:
                for r in [1, 8]:
                    self._pieces.append(Rook(f, r, r == 1, self))
            # Initialize knights:
            for f in [2, 7]:
                for r in [1, 8]:
                    self._pieces.append(Knight(f, r, r == 1, self))
            # Initialize bishops:
            for f in [3, 6]:
                for r in [1, 8]:
                    self._pieces.append(Bishop(f, r, r == 1, self))
            # Initialize queens:
            for r in [1, 8]:
                self._pieces.append(Queen(4, r, r == 1, self))
            # Initialize kings:
            for r in [1, 8]:
                self._pieces.append(King(5, r, r == 1, self))
            # Initialize pawns:
            for f in range(1, 9):
                for r in [2, 7]:
                    self._pieces.append(Pawn(f, r, r == 2, self))
        # Initialize booleans and en-passant:
        self.turn = True
        self._checkmate = False
        self._draw = False
        # self._en_passant = None
        
    def __str__(self) -> str:
        out = ""
        for rank in range(8, 0, -1):
            for file in range(1, 9):
                p = self.occupant(file, rank)
                if isinstance(p, Queen):
                    out = out + 'Q'*int(p.white) + 'q'*int(not p.white)
                elif isinstance(p, Pawn):
                    out = out + '.'*int(p.white) + ','*int(not p.white)
                elif isinstance(p, King):
                    out = out + 'K'*int(p.white) + 'k'*int(not p.white)
                elif isinstance(p, Rook):
                    out = out + 'R'*int(p.white) + 'r'*int(not p.white)
                elif isinstance(p, Bishop):
                    out = out + 'B'*int(p.white) + 'b'*int(not p.white)
                elif isinstance(p, Knight):
                    out = out + 'N'*int(p.white) + 'n'*int(not p.white)
                else:
                    out += ' '
                out += ' '
            out = out[:-1] + '\n'
        if self.turn:
            return out + "White to play."
        else:
            return out + "Black to play."

    def moved(self, m: Move) -> None:
        self.turn = not self.turn
        self._move_log.append(m)
        # self._en_passant = None

    # def add_move(self, old_move: Tuple[int, int], new_move: Tuple[int, int]):
    #     self._move_log.append((old_move, new_move))

    def en_passant(self, file: int) -> None:
        """Makes a file eligible for en-passant capture"""
        self._en_passant = file

    # def can_en_passant(self, file: int) -> bool:
    #     """Returns True iff en-passant eligible on specified file"""
    #     pass

    def occupant(self, file: int, rank: int) -> Optional[Piece]:
        """
        Returns piece occupying a square, or None if square is empty.

        Pre-conditions:
        - square is on the board
        """
        for piece in self._pieces:
            if piece.file == file and piece.rank == rank:
                return piece
        return None

    def promote(self, file: int, white: bool, piece: Piece = Queen):
        """Takes a pawn already on the last rank and replaces it with the specified piece,
        or queen if not specified"""
        self.remove_occupant(file, int(white)*7+1)
        if piece == Queen:
            self._pieces.append(Queen(file, int(white) * 7 + 1, white, self))
        elif piece == Knight:
            self._pieces.append(Knight(file, int(white) * 7 + 1, white, self))
        elif piece == Rook:
            self._pieces.append(Rook(file, int(white) * 7 + 1, white, self))
        else:
            self._pieces.append(Bishop(file, int(white) * 7 + 1, white, self))

    def remove_occupant(self, file: int, rank: int) -> None:
        """
        Removes occupant of specified square if occupied.
        """
        for piece in self._pieces:
            if piece.file == file and piece.rank == rank:
                del piece
                return None

    def last_move(self) -> Move:
        return self._move_log[-1]

    def all_pieces(self):
        return self._pieces

    def white_pieces(self):
        out = []
        for piece in self._pieces:
            if piece.white:
                out.append(piece)
        return out

    def black_pieces(self):
        out = []
        for piece in self._pieces:
            if not piece.white:
                out.append(piece)
        return out

    def _move(self, old_file: int, old_rank: int, new_file: int, new_rank: int, promote_to: Piece = None) -> bool:
        """Returns True iff move is successful"""
        for piece in self._pieces:
            if piece.file == old_file and piece.rank == old_rank:
                if piece.white != self.turn:
                    return False
                if isinstance(piece, Pawn) and (int(piece.white) * 5 + 2):
                    return piece.move(new_file, new_rank, promote_to)
                return piece.move(new_file, new_rank)
        return False

    def move(self, old: str, new: str) -> bool:
        return self._move(human_in(old)[0], human_in(old)[1],
                          human_in(new)[0], human_in(new)[1])


if __name__ == '__main__' and RUN:
    b = Board()
    while True:
        print(b)
        old = input('Enter square of piece to move: ')
        if b.occupant(human_in(old)[0], human_in(old)[1]) is None or \
                b.occupant(human_in(old)[0], human_in(old)[1]).white != b.turn:
            print('INVALID INPUT')
        else:
            out = ''
            for i in b.occupant(human_in(old)[0], human_in(old)[1]).available_moves():
                out = out + human_out(i) + ', '
            print(out)
            new = input('Enter square to move piece to: ')
            if not b.move(old, new):
                print('INVALID MOVE')
