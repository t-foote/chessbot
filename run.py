from main import *
from preset_moves import *


def is_valid_notation(s: str) -> bool:
    """Returns True iff s is valid chess board notation"""
    return (len(s) == 2) and (s[0] in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']) and \
        s[1].isnumeric() and (int(s[1]) in range(1, 9))


INVALID_INPUT = "INVALID INPUT"
INVALID_SQUARE = "INVALID SQUARE"
INVALID_MOVE = "INVALID MOVE"
MOVES_AVAILABLE = "Moves available:"

b = Board()
# INSERT PRESET MOVE FUNCTIONS HERE:
en_passant_preset(b)


while True:
    print(b)
    old = input('Enter square of piece to move: ')
    if old == 'quit' or old == 'exit':
        break
    elif not is_valid_notation(old):
        print(INVALID_INPUT)
    elif b.occupant(human_in(old)[0], human_in(old)[1]) is None or \
            b.occupant(human_in(old)[0], human_in(old)[1]).white != b.turn:
        print(INVALID_SQUARE)
    else:
        out = ''
        for i in b.occupant(human_in(old)[0], human_in(old)[1]).available_moves():
            out = out + human_out(i) + ', '
        print(MOVES_AVAILABLE, out)
        new = input('Enter square to move piece to: ')
        if not is_valid_notation(new):
            print(INVALID_INPUT)
        elif not b.move(old, new):
            print(INVALID_MOVE)
