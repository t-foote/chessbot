from typing import Optional, List, Tuple, Dict, Any


Coordinates = Tuple[int, int]
OccupiedSquares = Dict[bool, List[Coordinates]]

STRAIGHT = [(1, 0), (0, 1), (-1, 0), (0, -1)]
DIAGONAL = [(1, 1), (-1, -1), (1, -1), (-1, 1)]
KNIGHT = [(1, 2), (1, -2), (-1, 2), (-1, -2), (2, 1), (2, -1), (-2, 1), (-2, -1)]


def human_in(s: str) -> Tuple[int, int]:
    letters = {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6, 'g': 7, 'h': 8}
    return letters[s[0].lower()], int(s[1])


def human_out(file_rank: Tuple[int, int]) -> str:
    file, rank = file_rank[0], file_rank[1]
    numbers = {1: 'a', 2: 'b', 3: 'c', 4: 'd', 5: 'e', 6: 'f', 7: 'g', 8: 'h'}
    return numbers[file] + str(rank)


def in_range(file_rank: Tuple[int, int]) -> bool:
    return file_rank[0] in range(1, 9) and file_rank[1] in range(1, 9)


def combine(d: Dict[Any, List[Any]]) -> List[Any]:
    out = []
    for key in d:
        out += d[key]
    return out
