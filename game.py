import pygame, sys, main
from typing import Dict, List, Optional, Tuple
from random import randint

pygame.init()

PIECE_DIMENSION, SQUARE_DIMENSION = 300, 350
LIGHT_SQUARE, DARK_SQUARE = "icons/light_square.png", "icons/dark_square.png"


def make_image(icon_file: str, width: int, height: int) -> pygame.surface:
    """
    A helper function for loading <icon_file> as a pygame image
    and scaling it to have dimensions <width> and <height>
    """
    pic = pygame.image.load(icon_file)
    return pygame.transform.scale(pic, (width, height))


class ChessGame:
    """The UI for a chess game."""
    square_size: int
    _board: main.Board
    _screen: pygame.Surface
    _light_square: pygame.Surface
    _dark_square: pygame.Surface
    _icon_map: Dict[Tuple[main.Piece, bool], str]
    _grid: Dict[Tuple[int, int], pygame.Rect]

    def __init__(self, square_size: int):
        self._board = main.Board()
        self.square_size = square_size

        self.grid = dict()

        # Initialize a window of these pixel dimensions for display
        self._screen = pygame.display.set_mode((8 * self.square_size, 8 * self.square_size))

        # a function defined for convenience that we use to set up the
        # _icon_map below.
        def image_loader(x: str) -> pygame.surface:
            return make_image(x, self.square_size, self.square_size)

        self._light_square = image_loader(LIGHT_SQUARE)
        self._dark_square = image_loader(DARK_SQUARE)

        self._icon_map = {
            (main.King, True): image_loader('icons/white_king.png'),
            (main.Queen, True): image_loader('icons/white_queen.png'),
            (main.Rook, True): image_loader('icons/white_rook.png'),
            (main.Bishop, True): image_loader('icons/white_bishop.png'),
            (main.Knight, True): image_loader('icons/white_knight.png'),
            (main.Pawn, True): image_loader('icons/white_pawn.png'),
            (main.King, False): image_loader('icons/black_king.png'),
            (main.Queen, False): image_loader('icons/black_queen.png'),
            (main.Rook, False): image_loader('icons/black_rook.png'),
            (main.Bishop, False): image_loader('icons/black_bishop.png'),
            (main.Knight, False): image_loader('icons/black_knight.png'),
            (main.Pawn, False): image_loader('icons/black_pawn.png'),
        }

    def draw(self) -> None:
        """
        Draw the given board state using pygame and also print it to the
        terminal in a text representation.
        """
        for x in range(8):
            for y in range(8):
                rectangle = pygame.Rect(x * self.square_size,
                                        y * self.square_size,
                                        self.square_size, self.square_size)
                self.grid[(x + 1, y + 1)] = rectangle
                if (x + y) % 2 == 0:
                    self._screen.blit(self._light_square, (x * self.square_size,
                                                              y * self.square_size))
                else:
                    self._screen.blit(self._dark_square, (x * self.square_size,
                                                              y * self.square_size))
                if self._board.occupant(x + 1, y*(-1) + 8) is not None:
                    c = type(self._board.occupant(x + 1, y*(-1) + 8)), self._board.occupant(x + 1, y*(-1) + 8).white
                    self._screen.blit(self._icon_map[c], rectangle)

        # Update the screen.

        pygame.display.flip()


def program(square_size: int, player_color: bool = None) -> None:
    """If player_color is not None, it is assumed cpu is the other player."""
    c = ChessGame(square_size)
    c.draw()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for square in c.grid:
                    if c.grid[square].collidepoint(event.pos):
                        pass
    pygame.quit()


if __name__ == '__main__':
    program(100, bool(randint(0, 1)))
