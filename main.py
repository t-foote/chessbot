from typing import Dict, Tuple, List, Optional

"""
_valid_moves vs. available_moves:
    - available_moves takes into account check. 
"""


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
    is_castle_move: bool
    promote_to: Optional[object]

    def __init__(self, old_file: int, old_rank: int, new_file: int, new_rank: int, piece: Piece, promote_to: object = None):
        self.old_file = old_file
        self.old_rank = old_rank
        self.new_file = new_file
        self.new_rank = new_rank
        self.piece = piece
        self.can_move = (new_file, new_rank) in piece.available_moves()
        self.is_empty_move, self.is_castle_move = False, False
        if isinstance(piece, Pawn) and old_rank == piece.white*5+2:
            self.promote_to = promote_to

    def can_en_passant(self) -> Optional[int]:
        if self.is_empty_move or self.is_castle_move:
            return None
        if self.piece.white:
            if isinstance(self.piece, Pawn) and self.old_rank == 2 and self.new_rank == 4:
                return self.new_file
        else:
            if isinstance(self.piece, Pawn) and self.old_rank == 7 and self.new_rank == 5:
                return self.new_file
        return None
    
    def __eq__(self, other) -> bool:
        if isinstance(self, EmptyMove) and isinstance(other, EmptyMove):
            return True
        if isinstance(self, EmptyMove) or isinstance(other, EmptyMove):
            return False
        if isinstance(self, CastleMove) and isinstance(other, CastleMove):
            return self.color == other.color and self.kingside == other.kingside
        if isinstance(self, CastleMove) or isinstance(other, CastleMove):
            return False
        return (self.old_file == other.old_file and
                self.old_rank == other.old_rank and
                self.new_file == other.new_file and
                self.new_rank == other.new_rank and
                self.piece is other.piece)


class ForcedMove(Move):
    """Forced move, for the Piece.available_moves method."""
    old_file: int
    old_rank: int
    new_file: int
    new_rank: int
    piece: Piece
    can_move: bool
    is_empty_move: bool
    is_castle_move: bool

    def __init__(self, old_file_rank: Tuple[int, int], new_file_rank: Tuple[int, int], piece: Piece):
        self.old_file = old_file_rank[0]
        self.old_rank = old_file_rank[1]
        self.new_file = new_file_rank[0]
        self.new_rank = new_file_rank[1]
        self.piece = piece
        self.can_move = True  # Forced
        self.is_empty_move, self.is_castle_move = False, False


class EmptyMove(Move):
    """
    The 0th move in the move log.
    """
    is_empty_move: bool
    is_castle_move: bool

    def __init__(self):
        self.is_empty_move, self.is_castle_move = True, False


class CastleMove(Move):
    """For castling"""
    is_empty_move: bool
    is_castle_move: bool
    color: bool
    kingside: bool

    def __init__(self, color: bool, kingside: bool):
        self.is_empty_move, self.is_castle_move = True, False
        self.color, self.kingside = color, kingside


class Piece:
    """
    A chess piece.
    Files 'a' through 'h' are indicated by 1 through 8 respectively.
    """
    file: int
    rank: int
    white: bool
    board: Board
    type: object

    def __init__(self, file: int, rank: int, white: bool, board: Board):
        self.file = file
        self.rank = rank
        self.white = white
        self.board = board
        self.type = type(self)

    def _valid_moves(self) -> List[Tuple[int, int]]:
        """
        Returns list of valid moves for that piece.
        """
        raise NotImplementedError

    def available_moves(self) -> List[Tuple[int, int]]:
        # TODO special case for pawn promotion. (New method in Pawn class.)
        """
        Returns list of available moves for that piece (like dots in lichess).
        """
        if not self.board.is_in_check():
            return self._valid_moves()
        else:
            out = []
            for move in self._valid_moves():
                if not self._will_be_in_check(move):
                    out.append(move)
            return out

    def _will_be_in_check(self, new_file_rank: Tuple[int, int]) -> bool:
        file, rank = new_file_rank
        c = BoardCopy(self.board)
        c.remove_occupant(file, rank)  # Removes any occupant of the new square
        c.remove_occupant(self.file, self.rank)  # Removes self from old square
        if type(self) == King:
            c.add_piece(King(file, rank, self.white, c))  # Adds copy to new square
        elif type(self) == Queen:
            c.add_piece(Queen(file, rank, self.white, c))  # Adds copy to new square
        elif type(self) == Bishop:
            c.add_piece(Bishop(file, rank, self.white, c))  # Adds copy to new square
        elif type(self) == Knight:
            c.add_piece(Knight(file, rank, self.white, c))  # Adds copy to new square
        elif type(self) == Rook:
            c.add_piece(Rook(file, rank, self.white, c))  # Adds copy to new square
        elif type(self) == Pawn:
            # TODO May have to change this for pawn promotion
            c.add_piece(Pawn(file, rank, self.white, c))  # Adds copy to new square
        return c.is_in_check()

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
        m = Move(self.file, self.rank, file, rank, self)
        if m.can_move or override:
            self.board.remove_occupant(file, rank)
            self.file = file
            self.rank = rank
            self.board.moved(m)
            return True
        return False

    def _is_same_color(self, file, rank) -> bool:
        """
        Returns True iff occupant of file, rank is the same color as self.
        """
        return self.board.occupant(file, rank).white == self.white

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
        if file not in range(1, 9):
            file = self.file
        if rank not in range(1, 9):
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
        if (self.board.retrieve(-1).can_en_passant() == self.file + 1) and (self.rank == self.white + 4):
            out.append((self.file + 1, self.rank + (int(self.white) * 2 - 1)))
        elif (self.board.retrieve(-1).can_en_passant() == self.file - 1) and (self.rank == self.white + 4):
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
        # en-passant:
        elif ((file, rank) in self._valid_moves()) and (self.file != file) and (self.board.occupant(file, rank) is None):
            if Piece.move(self, file, rank):
                self.board.remove_occupant(file, self.white + 4)
                return True
            return False
        # standard pawn move:
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
        Does not take into account castling and checks.
        """
        out = []
        for i in [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
            if self.moveable((self.file + i[0], self.rank + i[1])):
                out.append((self.file + i[0], self.rank + i[1]))
        return out

    # def available_moves(self) -> List[Tuple[int, int]]:
    #     """
    #     Returns list of available moves (like dots in lichess), including castling.
    #     """
    #     out = []
    #     for move in self._valid_moves():
    #         if not self.attackers(move[0], move[1]):
    #             out.append(move)
    #     out += [(7, self.rank)] * self.castle(True, False)
    #     out += [(3, self.rank)] * self.castle(False, False)
    #     return out

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
                if (not self._is_in_check()) and (not self.board.is_in_check((self.rank, 6))) and \
                        (not self.board.is_in_check((self.rank, 7))):
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

    def _is_in_check(self) -> bool:
        """Returns True iff self is in check, using the Board.is_in_check method."""
        return self.board.is_in_check


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
    _move_log: List[Move]
    is_playable: bool

    def __init__(self, ready_to_play: bool = True):
        self._pieces = []
        self._move_log = [EmptyMove()]
        self.is_playable = ready_to_play
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
        return out + "White to play." * self.turn + "Black to play." * (not self.turn) + " CHECK." * (
                self.is_in_check())

    def check_ready(self) -> bool:
        """Checks if the board is ready to play (has 1 king of each color) and updates & returns self.is_playable"""
        white_king, black_king = 0, 0
        for p in self._pieces:
            if isinstance(p, King) and p.white:
                white_king += 1
            elif isinstance(p, King) and not p.white:
                black_king += 1
        self.is_playable = (white_king, black_king == 1, 1)
        return self.is_playable

    def moved(self, m: Move) -> None:
        self.turn = not self.turn
        self._move_log.append(m)

    def occupant(self, file: int, rank: int) -> Optional[Piece]:
        """
        Returns piece occupying a square, or None if square is empty or not on board.
        """
        if in_range((file, rank)):
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

    def remove_occupant(self, file: int, rank: int) -> bool:
        """
        Removes occupant of specified square if occupied.
        Returns True iff a piece was removed.
        """
        for i in range(len(self._pieces)):
            if self._pieces[i].file == file and self._pieces[i].rank == rank:
                del self._pieces[i]
                return True
        return False

    def retrieve(self, i: int) -> Move:
        """Returns the i-th index of the move log, or empty move if IndexError."""
        try:
            return self._move_log[i]
        except IndexError:
            return self._move_log[0]

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

    def internal_move(self, old_file_rank: Tuple[int, int], new_file_rank: Tuple[int, int], promote_to: Piece = None) -> bool:
        """Returns True iff move is successful"""
        old_file, old_rank = old_file_rank
        new_file, new_rank = new_file_rank
        for piece in self._pieces:
            if piece.file == old_file and piece.rank == old_rank:
                if piece.white != self.turn:
                    return False
                if isinstance(piece, Pawn) and (int(piece.white) * 5 + 2):
                    return piece.move(new_file, new_rank, promote_to)
                return piece.move(new_file, new_rank)
        return False

    def move(self, old: str, new: str) -> bool:
        return self.internal_move(human_in(old), human_in(new))

    def _return_king(self, color: bool) -> King:
        """Returns the King of specified color"""
        for p in self._pieces:
            if (type(p) == King) and (p.white == color):
                return p

    def is_in_check(self, file_rank: Tuple[int, int] = None) -> bool:
        """Returns True iff King is in check, or hypothetical square file_rank (assuming same color king)."""
        king = self._return_king(self.turn)
        if file_rank is None:
            file, rank = king.file, king.rank
        else:
            file, rank = file_rank
        # Knight check:
        for i in [(1, 2), (1, -2), (-1, 2), (-1, -2), (2, 1), (2, -1), (-2, 1), (-2, -1)]:
            if in_range((file + i[0], rank + i[1])) and (
                    self.occupant(file + i[0], rank + i[1]) is not None) and (
                    self.occupant(file + i[0], rank + i[1]).white != self.turn):
                return True
        # Rook / Queen check:
        for i in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
            f = file
            r = rank
            while in_range((f + i[0], r + i[1])) and self.occupant(f + i[0], r + i[1]) is None:
                f += i[0]
                r += i[1]
            if (isinstance(self.occupant(f + i[0], r + i[1]), Rook) or
                isinstance(self.occupant(f + i[0], r + i[1]), Queen)) and \
                    self.occupant(f + i[0], r + i[1]).white != self.turn:
                return True
        # Bishop / Queen check:
        for i in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
            f = file
            r = rank
            while in_range((f + i[0], r + i[1])) and self.occupant(f + i[0], r + i[1]) is None:
                f += i[0]
                r += i[1]
            if (isinstance(self.occupant(f + i[0], r + i[1]), Bishop) or
                isinstance(self.occupant(f + i[0], r + i[1]), Queen)) and \
                    self.occupant(f + i[0], r + i[1]).white != self.turn:
                return True
        # Pawn check:
        for i in (1, -1):
            if in_range((file + i, rank + (self.turn * 2 -1))) and \
                    isinstance(self.occupant(file + i, rank + (self.turn * 2 -1)), Pawn) and \
                    self.occupant(file + i, rank + (self.turn * 2 - 1)).white != self.turn:
                return True
        return False

    def add_piece(self, piece) -> bool:
        """Returns True if piece was added successfully; False if square was already occupied."""
        if self.occupant(piece.file, piece.rank) is not None:
            return False
        else:
            self._pieces.append(piece)
            return True


class BoardCopy(Board):
    """
    Same as a Board, but is initialized by taking a board and copying its attributes.
    No Move log.
    """
    _pieces: List[Piece]
    turn: bool
    is_playable: bool

    def __init__(self, b: Board):
        self._pieces = []
        for piece in b._pieces:
            self._pieces.append(type(piece)(piece.file, piece.rank, piece.white, self))
        self.is_playable = b.is_playable
        self.turn = b.turn
