import pygame as pg
import sys
from main import *
from typing import *
from minimax import *


pg.init()

PIECE_DIMENSION, SQUARE_DIMENSION = 300, 350
LIGHT_SQUARE, DARK_SQUARE = "icons/light_square.png", "icons/dark_square.png"
CAPTURE, MOVE_TO, CHECK = "icons/capture.png", "icons/move_to.png", "icons/check.png"


def make_image(icon_file: str, width: int, height: int) -> pg.surface:
    """
    A helper function for loading <icon_file> as a pg image
    and scaling it to have dimensions <width> and <height>
    """
    pic = pg.image.load(icon_file)
    return pg.transform.scale(pic, (width, height))


class ChessGame:
    """The UI for a chess game."""
    square_size:    int
    board:          Board
    _icon_map:      Dict[Tuple[Piece, bool], str]
    grid:           Dict[Tuple[int, int], pg.Rect]
    piece_clicked:  Optional[Tuple[int, int]]
    # Icons:
    _screen:        pg.Surface
    _light_square:  pg.Surface
    _dark_square:   pg.Surface
    _capture:       pg.Surface
    _move_to:       pg.Surface
    _check:         pg.Surface

    def __init__(self, square_size: int, board: Board = None):
        if board is None:
            self.board = Board()
        else:
            self.board = board
        self.square_size = square_size
        self.piece_clicked = None
        self.grid = dict()

        self._screen = pg.display.set_mode((8 * self.square_size, 8 * self.square_size))

        # a function defined for convenience that we use to set up the
        # _icon_map below.
        def load_image(x: str) -> pg.surface:
            return make_image(x, self.square_size, self.square_size)

        self._light_square, self._dark_square = load_image(LIGHT_SQUARE), load_image(DARK_SQUARE)
        self._capture, self._move_to, self._check = load_image(CAPTURE), load_image(MOVE_TO), load_image(CHECK)

        self._icon_map = {
            (King,   True):  load_image('icons/white_king.png'),
            (Queen,  True):  load_image('icons/white_queen.png'),
            (Rook,   True):  load_image('icons/white_rook.png'),
            (Bishop, True):  load_image('icons/white_bishop.png'),
            (Knight, True):  load_image('icons/white_knight.png'),
            (Pawn,   True):  load_image('icons/white_pawn.png'),
            (King,   False): load_image('icons/black_king.png'),
            (Queen,  False): load_image('icons/black_queen.png'),
            (Rook,   False): load_image('icons/black_rook.png'),
            (Bishop, False): load_image('icons/black_bishop.png'),
            (Knight, False): load_image('icons/black_knight.png'),
            (Pawn,   False): load_image('icons/black_pawn.png'),
        }

    def occupant(self, file_rank: Tuple[int, int]) -> Optional[Piece]:
        return self.board.occupant(file_rank)

    def draw(self, side_up: bool) -> None:
        """
        Draw the given board state using pg.

        side_up == True means white is playing / on the bottom.
        side_up == False means black is playing / on the bottom.
        """
        for x in range(8):
            for y in range(8):
                rectangle = pg.Rect(x * self.square_size,
                                        y * self.square_size,
                                        self.square_size, self.square_size)
                if side_up:
                    self.grid[(x + 1, y*(-1) + 8)] = rectangle
                    if (x + y) % 2 == 0:
                        self._screen.blit(self._light_square, (x * self.square_size, y * self.square_size))
                    else:
                        self._screen.blit(self._dark_square, (x * self.square_size, y * self.square_size))
                    if self.board.occupant(x + 1, y*(-1) + 8) is not None:
                        c = type(self.board.occupant(x + 1, y*(-1) + 8)), self.board.occupant(x + 1, y*(-1) + 8).white
                        self._screen.blit(self._icon_map[c], rectangle)

                else:
                    self.grid[(x*(-1) + 8, y + 1)] = rectangle
                    if (x + y) % 2 == 1:
                        self._screen.blit(self._light_square, (x * self.square_size, y * self.square_size))
                    else:
                        self._screen.blit(self._dark_square, (x * self.square_size, y * self.square_size))
                    if self.board.occupant(x*(-1) + 8, y + 1) is not None:
                        c = type(self.board.occupant(x*(-1) + 8, y + 1)), self.board.occupant(x*(-1) + 8, y + 1).white
                        self._screen.blit(self._icon_map[c], rectangle)

        if self.board.is_in_check():

            if side_up:
                y = self.board.return_king(self.board.turn).rank * (-1) + 8
                x = self.board.return_king(self.board.turn).file - 1
            else:
                x = self.board.return_king(self.board.turn).file * (-1) + 8
                y = self.board.return_king(self.board.turn).rank - 1
            self._screen.blit(self._check, (x * self.square_size, y * self.square_size))
        # Update the screen
        pg.display.flip()

    def draw_click(self, file_rank: Tuple[int, int], side_up: bool) -> None:
        """Draws the board after a piece has been clicked."""
        if self.occupant(file_rank) is None:
            return None
        for square in self.occupant(file_rank).available_moves():
            if side_up:
                x, y = square[0] - 1, square[1]*(-1) + 8
            else:
                x, y = square[0]*(-1) + 8, square[1] - 1
            if self.board.occupant(square) is None:
                self._screen.blit(self._move_to, (x * self.square_size, y * self.square_size))
            else:
                self._screen.blit(self._capture, (x * self.square_size, y * self.square_size))
        # Update the screen
        pg.display.flip()

    def ended(self) -> bool:
        """Returns True iff the game is not over"""
        return self.board.is_checkmate() or self.board.is_stalemate() or self.board.is_insufficient()

    def end_text(self) -> str:
        if self.board.is_checkmate():
            return "CHECKMATE"
        if self.board.is_stalemate():
            return "STALEMATE"
        if self.board.is_insufficient():
            return "DRAW BY INSUFFICIENT MATERIAL"

    def run(self, user_color_or_pov: bool) -> None:
        """
        WITH BOT
        pov is the color of the pieces on the bottom of the screen.
        """
        pov = user_color_or_pov  # Just to keep things clean
        self.draw(pov)
        if not pov:
            GameState(self.board, 2).make_best_move()
            self.draw(pov)
        running = True
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False

                # If event type is a click:
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
    
                    # Helper function that assigns a coordinate value to c.piece_clicked:
                    def assign_piece_clicked(c: ChessGame) -> None:
                        for square in c.grid:
                            if c.grid[square].collidepoint(event.pos):
                                if c.occupant(square) is not None and c.occupant(square).available_moves():
                                    c.piece_clicked = square
                                    c.draw(pov)
                                    c.draw_click(square, pov)
                                else:
                                    c.draw(pov)

                    if self.piece_clicked is None:
                        assign_piece_clicked(self)
                    else:
                        for square in self.grid:
                            if self.grid[square].collidepoint(event.pos):
                                if self.occupant(self.piece_clicked) is not None and \
                                        square in self.occupant(self.piece_clicked).available_moves():
                                    self.board.move(self.piece_clicked, square)
                                    self.draw(pov)
                                    # BOT moves here:
                                    if not self.ended():
                                        GameState(self.board, 2).make_best_move()
                                        self.draw(pov)
                                else:
                                    assign_piece_clicked(self)
        if not running:
            pg.quit()
            sys.exit()

    def play(self, user_color_or_pov: bool) -> None:
        """
        WITHOUT BOT
        pov is the color of the pieces on the bottom of the screen.
        """
        pov = user_color_or_pov  # Just to keep things clean
        self.draw(pov)
        running = True
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False

                # If event type is a click:
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:

                    # Helper function that assigns a coordinate value to c.piece_clicked:
                    def assign_piece_clicked(c: ChessGame) -> None:
                        for square in c.grid:
                            if c.grid[square].collidepoint(event.pos):
                                if c.occupant(square) is not None and c.occupant(square).available_moves():
                                    c.piece_clicked = square
                                    c.draw(pov)
                                    c.draw_click(square, pov)
                                else:
                                    c.draw(pov)

                    if self.piece_clicked is None:
                        assign_piece_clicked(self)
                    else:
                        for square in self.grid:
                            if self.grid[square].collidepoint(event.pos):
                                if self.occupant(self.piece_clicked) is not None and \
                                        square in self.occupant(self.piece_clicked).available_moves():
                                    self.board.move(self.piece_clicked, square)
                                    self.draw(pov)
                                else:
                                    assign_piece_clicked(self)
        if not running:
            pg.quit()
            sys.exit()


if __name__ == '__main__':
    b = Board()
    ChessGame(75, b).run(True)
