from typing import Dict, Tuple, List, Optional, Union


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
    # promote_to: Optional[object]

    def __init__(self, old_file: int, old_rank: int, new_file: int, new_rank: int, piece: Piece, promote_to: object = None):
        self.old_file = old_file
        self.old_rank = old_rank
        self.new_file = new_file
        self.new_rank = new_rank
        self.piece = piece
        self.can_move = (new_file, new_rank) in piece.available_moves()
        self.is_empty_move, self.is_castle_move = False, False
        # if isinstance(piece, Pawn) and old_rank == piece.white*5+2:
        #     self.promote_to = promote_to

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

    def __str__(self) -> str:
        return f"{'White' if self.white else 'Black'} {self.__class__.__name__.lower()} " \
               f"at {human_out((self.file, self.rank))}"

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
        if self.board.turn != self.white:
            return []  # TODO This might mess some stuff up idk
        out = []
        for move in self._valid_moves():
            if not self._will_be_in_check(move):
                out.append(move)
        return out
        # return [not self._will_be_in_check(move) for move in self._valid_moves()]

    def _will_be_in_check(self, new_file_rank: Tuple[int, int]) -> bool:
        """Determines if the board will be in check if a given piece moves to the inputted square."""
        file, rank = new_file_rank
        c = BoardCopy(self.board)
        c.remove_occupant(file, rank)  # Removes any occupant of the new square
        c.remove_occupant(self.file, self.rank)  # Removes self from old square
        c.add_piece(type(self)(file, rank, self.white, c))
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
            self.board.moves_made += int(self.white)
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

    def in_range(self) -> bool:
        return in_range((self.file, self.rank))

    def center_bonus(self) -> float:
        if type(self) == King:
            if (2 <= self.file <= 7) and (2 <= self.rank <= 7):
                return -0.2
            else:
                return 0
        if self.board.moves_made <= 10:
            if (4 <= self.file <= 5) and (4 <= self.rank <= 5):
                return 0.2
            if (3 <= self.file <= 6) and (3 <= self.rank <= 6):
                return 0.1
        return 0

    def __str__(self) -> str:
        # TODO Implement
        pass


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
        if self.board.occupant(self.file, self.rank + (int(self.white) * 2 - 1)) is None and \
                in_range((self.file, self.rank + (int(self.white) * 2 - 1))):
            out.append((self.file, self.rank + (int(self.white) * 2 - 1)))
            # Moving forward 2 squares:
            if (self.white and self.rank == 2) or (not self.white and self.rank == 7):
                if self.board.occupant(self.file, int(self.white)*(-1) + 5) is None:
                    out.append((self.file, int(self.white)*(-1) + 5))
        # Capture:
        for i in (1, -1):
            if (in_range((self.file + i, self.rank + (self.white * 2 - 1))) and
                    (self.board.occupant(self.file + i, self.rank + (self.white * 2 - 1)) is not None) and
                    (self.board.occupant(self.file + i, self.rank + (self.white * 2 - 1)).white != self.white) and
                    in_range((self.file + i, self.rank + (self.white * 2 - 1)))):
                out.append((self.file + i, self.rank + (self.white * 2 - 1)))
        # En-passant:
        if (self.board.retrieve(-1).can_en_passant() == self.file + 1) and (self.rank == self.white + 4):
            out.append((self.file + 1, self.rank + (int(self.white) * 2 - 1)))
        elif (self.board.retrieve(-1).can_en_passant() == self.file - 1) and (self.rank == self.white + 4):
            out.append((self.file - 1, self.rank + (int(self.white) * 2 - 1)))
        return out

    def move(self, file: int, rank: int) -> bool:
        """
        Attempts to move pawn. Returns True iff successfully moved.

        Pre-conditions:
        if (self.white and self.rank == 7) or (not self.white and self.rank == 2), promote_to is not None
        """
        # TODO Re-implement promotion stuff:
        if (self.white and self.rank == 7) or (not self.white and self.rank == 2):
            # Promotion:
            if Piece.move(self, file, rank):
                self.board.add_piece(Queen(self.file, self.rank, self.white, self.board), True)
                self.board.remove_occupant(self.file, self.rank)
                self.board.moves_made += int(self.white)
        # TODO: Look up how to use input() for both run.py and game.py
        # For now, all promotions are to a Queen.
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
            self.board.moves_made += int(self.white)
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

    def available_moves(self) -> List[Tuple[int, int]]:
        """Adds castling"""
        return Piece.available_moves(self) + self.can_castle()

    def can_castle(self) -> List[Tuple[int, int]]:
        if self.has_moved or self.board.is_in_check():
            return []
        out = []
        ks_rook, qs_rook = self.board.occupant(8, self.rank), self.board.occupant(1, self.rank)
        if type(ks_rook) == Rook and not ks_rook.has_moved \
                and not self._will_be_in_check((6, self.rank)) \
                and not self._will_be_in_check((7, self.rank)) \
                and self.board.occupant(6, self.rank) is None \
                and self.board.occupant(7, self.rank) is None:
            out.append((7, self.rank))
        if type(qs_rook) == Rook and not qs_rook.has_moved \
                and not self._will_be_in_check((4, self.rank)) \
                and not self._will_be_in_check((3, self.rank)) \
                and self.board.occupant(4, self.rank) is None \
                and self.board.occupant(3, self.rank) is None:
            out.append((3, self.rank))
        return out

    def move(self, file: int, rank: int, override: bool = False) -> bool:
        """
        Attempts to move king. Returns True iff piece is successfully moved.
        Updates self.has_moved

        Pre-conditions:
        - file in range(1, 9) and rank in range(1, 9)
        """
        old_file = self.file
        if Piece.move(self, file, rank, override):
            if old_file - file == 2:
                self.board.remove_occupant(1, self.rank)
                self.board.add_piece(Rook(4, self.rank, self.white, self.board))
                self.board.occupant(4, self.rank).has_moved = True
            elif old_file - file == -2:
                self.board.remove_occupant(8, self.rank)
                self.board.add_piece(Rook(6, self.rank, self.white, self.board))
                self.board.occupant(6, self.rank).has_moved = True
            self.has_moved = True
            self.board.moves_made += int(self.white)
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
    _pieces: List[Piece]   # A list of all pieces currently on the Board (order doesn't matter).
    turn: bool             # Whose turn it is (white or black).
    _move_log: List[Move]  # A list of all moves.
    is_playable: bool      # Does the board have exactly 1 King of each color?
    requesting: bool       # The board is requesting an input from the client for pawn promotion.
    promote_to: Piece      # A container for which piece to promote pawn to. Default is Queen.
    moves_made: int        # Keeps track of how many moves (by white) have been made in the game.

    def __init__(self, ready_to_play: bool = True):
        self._pieces = []
        self._move_log = [EmptyMove()]
        self.is_playable = ready_to_play
        self.requesting = False
        self.promote_to = Queen
        self.moves_made = 0
        if ready_to_play:
            # Initialize kings:
            for r in [1, 8]:
                self._pieces.append(King(5, r, r == 1, self))
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
                    out += 'Q'*int(p.white) + 'q'*int(not p.white)
                elif isinstance(p, Pawn):
                    out += '.'*int(p.white) + ','*int(not p.white)
                elif isinstance(p, King):
                    out += 'K'*int(p.white) + 'k'*int(not p.white)
                elif isinstance(p, Rook):
                    out += 'R'*int(p.white) + 'r'*int(not p.white)
                elif isinstance(p, Bishop):
                    out += 'B'*int(p.white) + 'b'*int(not p.white)
                elif isinstance(p, Knight):
                    out += 'N'*int(p.white) + 'n'*int(not p.white)
                else:
                    out += ' '
                out += ' '
            out = out[:-1] + '\n'
        if not self.check_if_playable():
            return out + "BOARD NOT PLAYABLE."
        if self.is_checkmate():
            return out + f"CHECKMATE! {'BLACK'*self.turn + 'WHITE'*(not self.turn)} WINS!"
        if self.is_stalemate():
            return out + "DRAW BY STALEMATE."
        if self.is_repetition():
            return out + "DRAW BY 3-FOLD REPETITION."
        if self.is_insufficient():
            return out + "DRAW BY INSUFFICIENT MATERIAL."
        return out + "White to play." * self.turn + "Black to play." * (not self.turn) + " CHECK." * (
                self.is_in_check())

    def is_checkmate(self) -> bool:
        """Returns True iff checkmate."""
        if not self.is_in_check():
            return False
        for p in self.turn_pieces():
            if p.available_moves():
                return False
        if type(self) is Board:
            print(f"CHECKMATE {'BLACK' if self.turn else 'WHITE'}")  # todo remove?
        return True

    def is_stalemate(self) -> bool:
        """Returns True iff stalemate."""
        if self.is_in_check():
            return False
        for p in self.turn_pieces():
            if p.available_moves():
                return False
        if type(self) == Board:
            print("STALEMATE") # todo remove?
        return True

    def is_repetition(self) -> bool:
        """Returns True iff threefold repetition."""
        # TODO Implement this.
        pass

    def is_insufficient(self) -> bool:
        """Returns True iff draw by insufficient material."""
        if len(self._pieces) >= 5:
            return False
        # 2 Kings:
        if len(self._pieces) == 2:
            return True
        # 2 Kings + a Bishop or Knight:
        if len(self._pieces) == 3:
            for p in self._pieces:
                if isinstance(p, Knight) or isinstance(p, Bishop):
                    return True
        # 2 Bishops of different colors on the same colored square:
        if len(self._pieces) == 4:
            bishops = []
            for p in self._pieces:
                if isinstance(p, Bishop):
                    bishops.append(p)
                elif (not isinstance(p, King)) or (not isinstance(p, Bishop)):
                    return False
            if bishops[0].white != bishops[1].white and \
                    (bishops[0].file + bishops[0].rank) % 2 == (bishops[1].file + bishops[1].rank) % 2:
                return True
        return False

    def game_is_over(self) -> bool:
        # todo figure these out:
        if self.is_insufficient():
            print("DRAW BY INSUFFICIENT MATERIAL")
        elif self.is_stalemate():
            print("DRAW BY STALEMATE")
        elif self.is_repetition():
            print("DRAW BY REPETITION")
        else:
            return False
        return True

    def check_if_playable(self) -> bool:
        """Checks if the board is ready to play (has 1 king of each color) and updates & returns self.is_playable"""
        white_king, black_king = 0, 0
        for p in self._pieces:
            if isinstance(p, King) and p.white:
                white_king += 1
            elif isinstance(p, King) and not p.white:
                black_king += 1
        self.is_playable = white_king == 1 and black_king == 1
        return self.is_playable

    def moved(self, m: Move) -> None:
        self.turn = not self.turn
        self._move_log.append(m)

    def occupant(self, file: int, rank: int = None) -> Optional[Piece]:
        """
        Returns piece occupying a square, or None if square is empty or not on board.
        """
        if rank is None:
            if type(file) != tuple:
                raise Exception("Invalid argument type.")
        elif not (type(file) == int and type(rank) == int):
            raise Exception("Invalid argument type.")

        if rank is None:
            file, rank = file[0], file[1]
        if in_range((file, rank)):
            for piece in self._pieces:
                if piece.file == file and piece.rank == rank:
                    return piece
        return None

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

    def remove(self, piece: Piece) -> bool:
        """
        Removes the piece specified.
        Returns True iff a piece was removed.
        """
        for p in self._pieces:
            if p is piece:
                del p
                return True
        return False

    def retrieve(self, i: int) -> Move:
        """Returns the i-th index of the move log, or empty move if IndexError."""
        try:
            return self._move_log[i]
        except IndexError:
            return self._move_log[0]

    def pieces(self, color: bool = None) -> List[Piece]:
        if color is None:
            return self._pieces
        elif color:
            return self.white_pieces()
        else:
            return self.black_pieces()

    def white_pieces(self) -> List[Piece]:
        out = []
        for piece in self._pieces:
            if piece.white:
                out.append(piece)
        return out

    def black_pieces(self) -> List[Piece]:
        out = []
        for piece in self._pieces:
            if not piece.white:
                out.append(piece)
        return out

    def turn_pieces(self) -> List[Piece]:
        """Returns black_pieces or white_pieces depending on whose turn it is."""
        if self.turn:
            return self.white_pieces()
        else:
            return self.black_pieces()

    def opponent_pieces(self) -> List[Piece]:
        """Returns black_pieces or white_pieces depending on whose turn it isn't."""
        if not self.turn:
            return self.white_pieces()
        else:
            return self.black_pieces()

    def points(self, color: bool = None) -> int:
        """Calculates & returns total material points of a given player."""
        if color is None:
            color = self.turn
        out = 0
        for piece in self.pieces(color):
            out += POINTS[type(piece)] + piece.center_bonus()
        return out

    def value(self, color: bool = None) -> int:
        if self.is_checkmate():
            return float("inf") * (self.turn * 2 - 1)
        if color is not None:
            return self.points(color) - self.points(not color)
        return self.points() - self.points(not self.turn)

    def move(self, old: Union[Piece, str, Tuple[int, int]], new: Union[str, Tuple[int, int]]) -> bool:
        """Returns True iff move is successful. Same as Board.move except takes human chess coordinates.

        Pre-conditions:
        - old is either:
            - Type: Piece: a piece on the board
            - Type: str: chess-board notation; or
            - Type: Tuple[int, int]: coordinates; or
        - new is either:
            - Type: str: chess-board notation; or
            - Type: Tuple[int, int]: coordinates; or
        """
        if isinstance(old, Piece):
            old = (old.file, old.rank)
        elif type(old) is str:
            old = human_in(old)
        if type(new) is str:
            new = human_in(new)

        old_file, old_rank = old
        new_file, new_rank = new
        for piece in self._pieces:
            if piece.file == old_file and piece.rank == old_rank:
                if piece.white != self.turn:
                    return False
                if piece.move(new_file, new_rank):
                    self.moves_made += int(self.turn)
                    return True
        return False

    def return_king(self, color: bool = None) -> King:
        """Returns the King of specified color"""
        if color is None:
            color = self.turn
        for p in self._pieces:
            if (type(p) == King) and (p.white == color):
                return p

    def is_in_check(self, file_rank: Tuple[int, int] = None, color: bool = None) -> bool:
        """Returns True iff King is in check, or hypothetical square file_rank (assuming same color king)."""
        if color is None:
            color = self.turn
        king = self.return_king(color)
        if file_rank is None:
            file, rank = king.file, king.rank
        else:
            file, rank = file_rank
        # Knight check:
        for i in [(1, 2), (1, -2), (-1, 2), (-1, -2), (2, 1), (2, -1), (-2, 1), (-2, -1)]:
            if in_range((file + i[0], rank + i[1])) and (
                    self.occupant(file + i[0], rank + i[1]) is not None) and (
                    self.occupant(file + i[0], rank + i[1]).white != color) and (
                    isinstance(self.occupant(file + i[0], rank + i[1]), Knight)):
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
                    self.occupant(f + i[0], r + i[1]).white != color:
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
                    self.occupant(f + i[0], r + i[1]).white != color:
                return True
        # Pawn check:
        for i in (1, -1):
            if in_range((file + i, rank + (color * 2 -1))) and \
                    isinstance(self.occupant(file + i, rank + (color * 2 -1)), Pawn) and \
                    self.occupant(file + i, rank + (color * 2 - 1)).white != color:
                return True
        # King check:
        for i in [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
            if isinstance(self.occupant(file + i[0], rank + i[1]), King):
                return True
        # No checks found:
        return False

    def add_piece(self, piece, force: bool = False) -> bool:
        """Returns True if piece was added successfully; False if square was already occupied."""
        if not (self.occupant(piece.file, piece.rank) is None or force):
            return False
        else:
            self._pieces.append(piece)
            return True

    def __eq__(self, other) -> bool:
        if self.turn != other.turn:
            return False
        for f in range(1, 9):
            for r in range(1, 9):
                if type(self.occupant(f, r)) is not type(other.occupant(f, r)):
                    return False
                if self.occupant(f, r) is not None and other.occupant(f, r) is not None and \
                        self.occupant(f, r).white != other.occupant(f, r).white:
                    return False
        return True


class BoardCopy(Board):
    """
    Same as a Board, but is initialized by taking a board and copying its attributes.
    """
    _pieces: List[Piece]
    turn: bool
    is_playable: bool
    _move_log: List[Move]
    moves_made: int

    def __init__(self, b: Board):
        self._pieces = []
        self._move_log = [EmptyMove()]  # TODO: May need to change this.
        for piece in b._pieces:
            self._pieces.append(type(piece)(piece.file, piece.rank, piece.white, self))
        self.is_playable = b.is_playable
        self.turn = b.turn
        self.moves_made = b.moves_made


PIECES = {
    King:   'K',
    Queen:  'Q',
    Rook:   'R',
    Bishop: 'B',
    Knight: 'N',
    Pawn:   'P',
}
POINTS = {
    King:   10,
    Queen:  9,
    Rook:   5,
    Bishop: 3,
    Knight: 3,
    Pawn:   1,
}

if __name__ == '__main__':
    b = Board()
    from preset_moves import castle
    castle(b)
    print(b)