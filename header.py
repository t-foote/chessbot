from typing import Dict, Tuple, List, Optional, Union

WHITE = True
BLACK = False

Coordinates = Tuple[int, int]


def color_str(color: bool, caps: bool = True) -> str:
    out = 'WHITE' if color else 'BLACK'
    return out.upper() if caps else out.capitalize()


def human_in(s: str) -> Tuple[int, int]:
    letters = {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6, 'g': 7, 'h': 8}
    return letters[s[0].lower()], int(s[1])


def human_out(file_rank: Tuple[int, int]) -> str:
    file, rank = file_rank[0], file_rank[1]
    numbers = {1: 'a', 2: 'b', 3: 'c', 4: 'd', 5: 'e', 6: 'f', 7: 'g', 8: 'h'}
    return numbers[file] + str(rank)


def in_range(file_rank: Union[int, Tuple[int, int]]) -> bool:
    if isinstance(file_rank, int):
        return file_rank in range(1, 9)
    if isinstance(file_rank, tuple):
        return file_rank[0] in range(1, 9) and file_rank[1] in range(1, 9)
    raise TypeError(file_rank)